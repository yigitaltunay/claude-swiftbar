#!/usr/bin/env python3
# <swiftbar.title>Claude Usage</swiftbar.title>
# <swiftbar.version>7.5</swiftbar.version>
# <swiftbar.author>Yiğit Altunay</swiftbar.author>
# <swiftbar.refreshTime>5</swiftbar.refreshTime>

import json
import os
import sys

import requests
from datetime import datetime, timezone


def _config_root_dirs():
    """Search order for .env / secrets.json — later dirs win on duplicate keys."""
    seen = set()
    out = []

    def append_dir(path):
        if not path:
            return
        root = os.path.realpath(path)
        if root not in seen:
            seen.add(root)
            out.append(root)

    append_dir(os.path.dirname(os.path.realpath(__file__)))
    append_dir(os.path.dirname(os.path.abspath(__file__)))

    plugins_root = os.environ.get("SWIFTBAR_PLUGINS_PATH", "").strip()
    if plugins_root:
        append_dir(plugins_root)

    plugin_file = os.environ.get("SWIFTBAR_PLUGIN_PATH", "").strip()
    if plugin_file:
        append_dir(os.path.dirname(os.path.abspath(plugin_file)))

    return out


def _parse_env_file(path):
    out = {}
    try:
        with open(path, encoding="utf-8-sig") as f:
            for raw in f:
                line = raw.strip().replace("\r", "")
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:].strip()
                if "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip().replace("\r", "")
                if not key:
                    continue
                val = val.strip().replace("\r", "")
                if val and val[0] in "\"'" and len(val) >= 2 and val[-1] == val[0]:
                    val = val[1:-1]
                elif " #" in val:
                    val = val.split(" #", 1)[0].strip()
                if val:
                    out[key] = val
    except OSError:
        pass
    return out


def _parse_secrets_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    out = {}
    for k, v in data.items():
        if not isinstance(k, str):
            continue
        s = str(v).strip() if v is not None else ""
        if s:
            out[k] = s
    return out


def _hydrate_os_env():
    merged = {}
    roots = _config_root_dirs()
    for root in roots:
        merged.update(_parse_env_file(os.path.join(root, ".env")))
    for root in roots:
        merged.update(_parse_secrets_json(os.path.join(root, "secrets.json")))
    for k, v in merged.items():
        os.environ[k] = v
    if os.environ.get("CLAUDE_USAGE_DEBUG"):
        print("claude_usage dirs: " + " | ".join(roots), file=sys.stderr)
        print("claude_usage keys from files: " + ",".join(sorted(merged.keys())), file=sys.stderr)


_hydrate_os_env()

# ┌─────────────────────────────────────────────────────────────────────┐
# │                         CONFIGURATION                                │
# ├─────────────────────────────────────────────────────────────────────┤
SESSION_KEY = os.environ.get("CLAUDE_SESSION_KEY", "").strip()
ORG_ID = os.environ.get("CLAUDE_ORG_ID", "").strip()
WARNING_THRESHOLD = int(os.environ.get("CLAUDE_WARNING_THRESHOLD", "50"))
CRITICAL_THRESHOLD = int(os.environ.get("CLAUDE_CRITICAL_THRESHOLD", "85"))
BAR_WIDTH = int(os.environ.get("CLAUDE_BAR_WIDTH", "20"))
MENUBAR_FONT = os.environ.get("CLAUDE_MENUBAR_FONT", "Menlo-Bold")
MENUBAR_SIZE = int(os.environ.get("CLAUDE_MENUBAR_SIZE", "12"))
# └─────────────────────────────────────────────────────────────────────┘

DEVELOPER = "yigitaltunay"
GITHUB = "https://github.com/yigitaltunay/claude-meter"

C_GREEN = "#32D74B"
C_AMBER = "#FFD60A"
C_RED = "#FF453A"
C_PURPLE = "#BF5AF2"
C_BLUE = "#0A84FF"
C_GRAY = "#8E8E93"


def tier(val):
    if val < WARNING_THRESHOLD:
        return "green"
    if val < CRITICAL_THRESHOLD:
        return "amber"
    return "red"


def color(val):
    t = tier(val)
    return C_GREEN if t == "green" else C_AMBER if t == "amber" else C_RED


def badge(val):
    t = tier(val)
    return "● LOW" if t == "green" else "● MED" if t == "amber" else "● HIGH"


def bar(pct, width=BAR_WIDTH):
    n = round(pct / 100 * width)
    return "█" * n + "▒" * (width - n)


def pct_label(val):
    return f"{int(val):>3}%"


def format_reset_time(iso_str, mode="relative"):
    if not iso_str:
        return ""
    try:
        reset_dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = reset_dt - now

        if mode == "relative":
            hours, remainder = divmod(int(diff.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            if hours > 0:
                return f"Resets in {hours} hr {minutes} min"
            return f"Resets in {max(0, minutes)} min"
        return f"Resets {reset_dt.strftime('%a %-I:%M %p')}"
    except (ValueError, TypeError, OSError):
        return ""


def get_claude_usage():
    if not SESSION_KEY or not ORG_ID:
        print("✦ Claude ⚙ | color=" + C_AMBER)
        print("---")
        print("Missing CLAUDE_SESSION_KEY or CLAUDE_ORG_ID | font=Menlo size=11")
        print(".env next to script (SwiftBar sets SWIFTBAR_PLUGIN_PATH) | font=Menlo size=10 color=" + C_GRAY)
        return

    url = f"https://claude.ai/api/organizations/{ORG_ID}/usage"
    headers = {
        "Cookie": f"sessionKey={SESSION_KEY}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "anthropic-version": "2023-06-01",
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code == 200:
            data = res.json()
            s_data = data.get("five_hour", {})
            w_data = data.get("seven_day", {})

            s, w = s_data.get("utilization", 0.0), w_data.get("utilization", 0.0)
            sc, wc = color(s), color(w)

            s_reset = format_reset_time(s_data.get("resets_at"), "relative")
            w_reset = format_reset_time(w_data.get("resets_at"), "absolute")

            print(f"Claude {pct_label(s)}| font={MENUBAR_FONT} size={MENUBAR_SIZE} color={sc}")
            print("---")

            print(f"  SESSION (5H)                    {badge(s)} | font=Menlo-Bold size=11 color={sc}")
            print(f"  {bar(s)}  {pct_label(s)} | font=Monaco size=11 color={sc}")
            if s_reset:
                print(f"  {s_reset} | font=Menlo size=10 color={C_GRAY}")
            print("---")

            print(f"  WEEKLY  (7D)                    {badge(w)} | font=Menlo-Bold size=11 color={wc}")
            print(f"  {bar(w)}  {pct_label(w)} | font=Monaco size=11 color={wc}")
            if w_reset:
                print(f"  {w_reset} | font=Menlo size=10 color={C_GRAY}")
            print("---")

            if s < WARNING_THRESHOLD and w < WARNING_THRESHOLD:
                st, stc = "  ✔  All systems go", C_GREEN
            elif s >= CRITICAL_THRESHOLD or w >= CRITICAL_THRESHOLD:
                st, stc = "  ✖  Usage critical — slow down", C_RED
            else:
                st, stc = "  ◉  Moderate — keep an eye", C_AMBER
            print(f"{st} | font=Menlo-Bold size=11 color={stc}")
            print("---")

            print(f"  ↗  Open Dashboard | href=https://claude.ai/settings/usage font=Menlo-Bold size=11 color={C_BLUE}")
            print(f"  ↺  Refresh | refresh=true font=Menlo size=11 color={C_GRAY}")
            print("---")
            print(f"  crafted by {DEVELOPER} | href={GITHUB} font=Menlo size=10 color={C_PURPLE}")

        else:
            print(f"✦ Claude  ✖ | color={C_RED}")
            print(f"--- \n API Error {res.status_code}")

    except requests.RequestException:
        print(f"✦ Claude  ⚡ | color={C_AMBER}")
        print("--- \n Network Error")


if __name__ == "__main__":
    get_claude_usage()
    sys.stdout.flush()

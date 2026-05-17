<h1 align="center">Claude Meter</h1>

<p align="center">
  <i>A macOS menu bar plugin that shows your <b>Claude Pro</b> usage — both the rolling <b>5-hour</b> and <b>7-day</b> windows — at a glance.</i>
</p>

<p align="center">
  <img width="306" height="451" alt="image" src="https://github.com/user-attachments/assets/7aa8d7d9-e726-4a3a-8d49-db7bf9f0e2dd" />
  <img width="306" height="451" alt="image" src="https://github.com/user-attachments/assets/4b263c3d-a3c2-4824-bb6c-1ac1ea20d1c8" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS-lightgrey.svg" alt="macOS">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python 3.8+">
  <a href="https://github.com/swiftbar/SwiftBar"><img src="https://img.shields.io/badge/built%20for-SwiftBar-orange.svg" alt="SwiftBar"></a>
  <a href="https://claude.ai"><img src="https://img.shields.io/badge/for-Claude%20Pro-8A63D2.svg" alt="Claude Pro"></a>
</p>

---

## Features

- **At-a-glance percentage** in the menu bar (`Claude 12%`) — no clicks needed
- **Two windows in one view** — 5-hour session and 7-day weekly, each with its own dithered progress bar and `LOW` / `MED` / `HIGH` indicator
- **Color-coded thresholds** so you know when to slow down (green → yellow → red)
- **Quick actions** in the dropdown: open the Claude dashboard, force-refresh
- **Minimal dependencies** — only `requests`; reads `.env` via stdlib
- Configurable refresh interval, bar width, font, and thresholds via `.env`

## Requirements

- macOS
- [SwiftBar](https://github.com/swiftbar/SwiftBar)
- Python 3.8+
- `requests` (`pip install -r requirements.txt`)

---

## Installation

### 1. Install SwiftBar

**Homebrew**

```bash
brew install --cask swiftbar && open -a SwiftBar
```

Or download the `.dmg` from [SwiftBar releases](https://github.com/swiftbar/SwiftBar/releases) and drag it to Applications.

On first launch, pick a **plugin folder** (or later: SwiftBar menu → **Open Plugin Folder…**). The default is:

```
~/Library/Application Support/SwiftBar/Plugins/
```

To print the current path:

```bash
echo "$HOME/Library/Application Support/SwiftBar/Plugins"
```

If you changed it inside SwiftBar:

```bash
defaults read com.ameba.SwiftBar PluginDirectory
```

### 2. Install Claude Meter

```bash
git clone https://github.com/yigitaltunay/claude-meter.git
cd claude-meter
python3 -m pip install -r requirements.txt
chmod +x install-plugin.sh
./install-plugin.sh
```

The installer copies `claude_usage.5m.py` into the Plugins folder and makes it executable. If a `.env` already exists in Plugins, it is left alone; if it is missing, the installer copies `./.env` from the repo when present, otherwise falls back to `.env.example`. Use `SYNC_ENV=1 ./install-plugin.sh` to overwrite the Plugins `.env` from the repo.

> **Heads-up:** if you had `claude_usage.py` or `claude_pro_dashboard.py` in Plugins from an earlier version, delete them.

---

## Configuration

Edit `.env` in your Plugins folder (next to the installed script):

| Variable | Required | Purpose |
|----------|:---:|---------|
| `CLAUDE_SESSION_KEY` | yes | Cookie `sessionKey` from your logged-in claude.ai session |
| `CLAUDE_ORG_ID` | yes | UUID from `/api/organizations/<id>/usage` |
| `CLAUDE_WARNING_THRESHOLD` | no | Percent at which the bar turns yellow |
| `CLAUDE_CRITICAL_THRESHOLD` | no | Percent at which the bar turns red |
| `CLAUDE_BAR_WIDTH` | no | Width of the progress bar in characters |
| `CLAUDE_MENUBAR_FONT` | no | Custom font for the menu bar text |
| `CLAUDE_MENUBAR_SIZE` | no | Font size for the menu bar text |

**Refresh interval** is controlled by the filename: `5m` = 5 minutes. To change it, rename the file (for example `claude_usage.2m.py`) and re-run `./install-plugin.sh`.

### How to get `CLAUDE_SESSION_KEY` and `CLAUDE_ORG_ID`

Both values come from a real request that claude.ai makes in your logged-in browser. Easiest way to capture them in one shot:

1. Open [claude.ai](https://claude.ai) in your browser, logged in.
2. Open **DevTools** (⌥⌘I on macOS / F12 elsewhere) and go to the **Network** tab. Leave it open.
3. In the Claude UI, find the **"Last updated: just now"** label (usage panel) and click the **↻ refresh button** next to it. This fires a fresh request to `/api/organizations/<org-id>/usage`.
4. In the Network tab, click that `usage` request.
   - **`CLAUDE_ORG_ID`** → the UUID in the request URL: `/api/organizations/`**`<this-part>`**`/usage`
   - **`CLAUDE_SESSION_KEY`** → in the request's **Headers** section, find **`Cookie:`** and copy the value of the `sessionKey=...` entry (stop at the next `;`). It starts with `sk-ant-sid01-...`
5. Paste both into your `.env`:

   ```env
   CLAUDE_SESSION_KEY=sk-ant-sid01-...
   CLAUDE_ORG_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

> **Alternative for the session key:** DevTools → **Application** → **Cookies** → `https://claude.ai` → copy the `sessionKey` value.

> **Security:** treat `sessionKey` like a password — it grants full access to your Claude account. Never commit it or share it. It rotates when you log out, so logging out everywhere invalidates it.

---

## Updating

From your local clone:

```bash
cd claude-meter
git pull
python3 -m pip install -r requirements.txt
```

Then:

- **If you used `./install-plugin.sh`:** run it again to refresh `claude_usage.5m.py`. Your Plugins `.env` is left alone unless you pass `SYNC_ENV=1`.
- **If you symlinked Plugins → this repo's script:** `git pull` is enough; wait for the next refresh or hit **↺ Refresh** in the menu.

`SYNC_ENV=1` only affects `.env` in the Plugins folder and does nothing if the repo has no `.env`.

---

## Troubleshooting

<details>
<summary><b>The <code>.env</code> looks filled but I still see ⚙</b></summary>

<br>

SwiftBar may be running a copy of the script. This plugin reads `.env` via stdlib (no `python-dotenv`) and includes the folder from `SWIFTBAR_PLUGIN_PATH` (the real plugin path) in its search.

Re-run `./install-plugin.sh` to copy the latest script. From the Plugins folder, run:

```bash
CLAUDE_USAGE_DEBUG=1 ./claude_usage.5m.py
```

It prints which directories were read on stderr.

</details>

<details>
<summary><b>Works in Terminal but not in SwiftBar</b></summary>

<br>

Wrong Python interpreter. Set the script's shebang to the full path from `which python3`, then install deps with that Python:

```bash
/path/to/that-python -m pip install -r requirements.txt
```

Make sure the file is executable: `chmod +x claude_usage.5m.py`.

</details>

<details>
<summary><b>Network / API errors</b></summary>

<br>

Run `./claude_usage.5m.py` directly from the Plugins folder to see the actual output. Most often the fix is a stale `CLAUDE_SESSION_KEY`, a wrong `CLAUDE_ORG_ID`, or a connectivity issue.

</details>

---

## Security

Do **not** commit `.env` or `secrets.json`. Do **not** share `sessionKey` — it is equivalent to your Claude account password.

## Contributing

Issues and PRs are welcome. For non-trivial changes, open an issue first to discuss what you'd like to change.

## Acknowledgements

Built on top of [SwiftBar](https://github.com/swiftbar/SwiftBar). Not affiliated with or endorsed by Anthropic.

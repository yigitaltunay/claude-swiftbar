# Claude Usage (SwiftBar)

macOS menu bar plugin for **[Claude](https://claude.ai) Pro** usage (5-hour and 7-day windows). Built for [SwiftBar](https://github.com/swiftbar/SwiftBar).  
**Repo:** [github.com/yigitaltunay/claude-swiftbar](https://github.com/yigitaltunay/claude-swiftbar)

**Needs:** macOS, SwiftBar, Python 3, and `requests` (`pip install -r requirements.txt`). Configure secrets in **`.env`** and/or **`secrets.json`** next to the installed script (never commit real values).

---

## 1. Install SwiftBar

**Homebrew**

```bash
brew install --cask swiftbar && open -a SwiftBar
```

**Or** install from the [SwiftBar releases](https://github.com/swiftbar/SwiftBar/releases) `.dmg` and drag the app to Applications.

On first launch, pick a **plugin folder** (or later: SwiftBar menu → **Open Plugin Folder…**). The usual default location is:

`~/Library/Application Support/SwiftBar/Plugins/`

To **print that path** in Terminal (paste the line, press Enter — you are not editing a file; it only shows where to copy the script):

```bash
echo "$HOME/Library/Application Support/SwiftBar/Plugins"
```

If you changed the folder in SwiftBar, read the path SwiftBar saved:

```bash
defaults read com.ameba.SwiftBar PluginDirectory
```

---

## 2. Install this plugin

Clone the repo and install Python deps (from the repo folder):

```bash
git clone https://github.com/yigitaltunay/claude-swiftbar.git
cd claude-swiftbar
python3 -m pip install -r requirements.txt
```

**Install into SwiftBar’s plugin folder** (uses `defaults read com.ameba.SwiftBar PluginDirectory` when set, otherwise `~/Library/Application Support/SwiftBar/Plugins/`):

```bash
chmod +x install-plugin.sh
./install-plugin.sh
```

The script copies `claude_usage.5m.py` and makes it executable. **`.env` in Plugins:** if that file is missing, the installer copies **`./.env` from the repo** when it exists; otherwise it copies `.env.example`. If Plugins already has a `.env`, it is left alone — use **`SYNC_ENV=1 ./install-plugin.sh`** to overwrite it from the repo’s `.env`. Remove any old `claude_usage.py` or `claude_pro_dashboard.py` from the Plugins folder if you still have them.

| Variable | Purpose |
|----------|---------|
| `CLAUDE_SESSION_KEY` | Cookie `sessionKey` while logged in at claude.ai |
| `CLAUDE_ORG_ID` | UUID from `/api/organizations/<id>/usage` in DevTools → Network |

Optional tuning (env): `CLAUDE_WARNING_THRESHOLD`, `CLAUDE_CRITICAL_THRESHOLD`, `CLAUDE_BAR_WIDTH`, `CLAUDE_MENUBAR_FONT`, `CLAUDE_MENUBAR_SIZE` — see `claude_usage.py` for defaults.

Refresh interval: controlled by the filename (`5m` = 5 minutes). To change it, rename the file (e.g. `claude_usage.2m.py` for 2 minutes) and re-run `./install-plugin.sh`.

---

## 3. Update when this repo changes

From your **local clone** of [claude-swiftbar](https://github.com/yigitaltunay/claude-swiftbar):

```bash
cd claude-swiftbar          # or wherever you cloned it
git pull
python3 -m pip install -r requirements.txt
```

Then:

- **You used `./install-plugin.sh` in section 2:** run `./install-plugin.sh` again to refresh `claude_usage.5m.py`. Existing Plugins `.env` is unchanged unless you run **`SYNC_ENV=1 ./install-plugin.sh`** (then it copies from the repo’s `.env` if that file exists).

- **You symlinked** Plugins → this repo’s `claude_usage.5m.py`: `git pull` is enough; wait for SwiftBar’s next refresh or use **↺ Refresh** in the menu.

`SYNC_ENV=1` only affects `.env` in the Plugins folder; it does nothing if the repo has no `.env`.

---

## If something breaks

- **`.env` looks filled but you still see ⚙** — SwiftBar may run a copy of the script; this plugin no longer uses `python-dotenv` and reads `.env` via stdlib, including the folder from **`SWIFTBAR_PLUGIN_PATH`** (the real plugin path). Re-run `./install-plugin.sh` to copy the latest script. From Terminal in Plugins: `CLAUDE_USAGE_DEBUG=1 ./claude_usage.5m.py` prints which directories were read on stderr.
- **Works in Terminal, not in SwiftBar** — Wrong Python: set the first line of the script to the full path from `which python3`, then `that-python -m pip install -r requirements.txt`. Ensure the file is executable (`chmod +x`).
- **Network / API errors** — Run `./claude_usage.py` from the Plugins folder to see behavior; fix key, org id, or connectivity.

Do **not** commit `.env`, `secrets.json`, or share `sessionKey`.

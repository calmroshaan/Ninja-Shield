# FB Profile Manager

A free, open-source browser profile manager that generates unique browser fingerprints for each profile. Built with Python + Playwright + PyQt6 GUI.

> Manage multiple browser profiles on the same PC — each with a completely isolated identity: unique canvas fingerprint, WebGL, timezone, language, screen resolution, and cookie storage.

---

## Features

- Unique browser fingerprint per profile (canvas, WebGL, audio, navigator)
- Free-text VPN city input — type any city, timezone auto-detected via API
- 100% isolated cookie & localStorage per profile
- Pre-launch VPN reminder so you never forget which city to connect
- Proxy support per profile (http / socks5)
- Professional PyQt6 GUI — tabbed interface, search, one-click actions
- Completely free — only needs Python + Playwright + PyQt6

---

## What Gets Spoofed Per Profile

| Signal | Spoofed |
|---|---|
| User Agent | Yes |
| Screen Resolution | Yes |
| Timezone | Yes — auto-matched to VPN city |
| Language | Yes — auto-matched to VPN city |
| Platform (Win/Mac/Linux) | Yes |
| CPU Core Count | Yes |
| RAM Amount | Yes |
| WebGL Vendor & Renderer | Yes |
| Canvas Fingerprint | Yes — unique pixel noise |
| Audio Fingerprint | Yes — unique buffer noise |
| Battery API | Yes |
| Network Connection API | Yes |
| WebRTC IP Leak | Yes — blocked |
| Cookies & Storage | Yes — 100% isolated |
| webdriver detection flag | Yes — removed |

---

## Requirements

- Windows 10/11
- Python 3.9+ from https://python.org (check "Add Python to PATH" during install)
- That's it — everything else installs automatically via START.bat

---

## Installation & Run

### Option A — Double click (easiest)
1. Download or clone this repo
2. Double-click **`START.bat`**
3. First run installs all dependencies automatically, then launches the GUI

### Option B — Manual
```bash
pip install -r requirements.txt
playwright install chromium
python gui.py
```

---

## Quick Start

1. Click **+ New Profile** — enter a name and VPN city (e.g. `Dubai, UAE`)
2. Click **Lookup** — timezone is auto-detected
3. Click **Create Profile**
4. Select the profile → click **Launch**
5. Connect your VPN to the assigned city when prompted
6. Browser opens with a unique fingerprint

---

## Project Structure

```
fb-profile-manager/
|- main.py                  <- CLI entry point (legacy)
|- gui.py                   <- PyQt6 GUI (main app)
|- fingerprint_engine.py    <- Fingerprint generator + timezone API
|- browser_launcher.py      <- Playwright browser launcher with stealth JS
|- START.bat                <- Windows one-click launcher
|- FIX_DEPENDENCIES.bat     <- Run this if START.bat has dependency issues
|- requirements.txt
|- profiles/                <- Created on first run (gitignored)
    |- fb_01.json           <- Per-profile fingerprint config
    |- browser_data_fb_01/  <- Isolated browser storage
```

---

## Notes

- `profiles/` folder is gitignored — your profile data stays private
- Each profile's fingerprint is deterministic (same name = same fingerprint every run)
- Browser window is fixed at 1280x800 — the spoofed screen size reported to websites is separate and unique per profile
- Timezone lookup uses OpenStreetMap (geocoding) + TimeZoneDB API — requires internet

---

## License

MIT — free to use, modify, and share.

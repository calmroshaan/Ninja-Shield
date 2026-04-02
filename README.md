# 🛡️ Ninja Shield — Camoufox Edition (v4.1.1)

A premium, commercial-grade browser profile manager designed to bypass advanced anti-bot systems. Built with Python, PyQt6, and powered by the **Camoufox** native fingerprinting engine.

> Manage multiple isolated browser profiles on a single machine. Unlike traditional Chromium anti-detects that rely on easily detected JavaScript injections, Ninja Shield uses Camoufox to alter fingerprints at the core binary level.

---

## ✨ Key Features

- **Binary-Level Stealth:** Powered by Camoufox (a privacy-hardened Firefox engine) to completely bypass advanced JS-based detection methods.
- **Smart Resolution Calibration:** Mathematically simulates real Windows taskbars and Firefox UI dimensions to ensure your viewport footprint is 100% congruent with real human hardware.
- **Native Proxy Integration:** Direct HTTP/SOCKS5 proxy support per profile.
- **Location Spoofing:** Free-text city input automatically detects and applies the correct global timezone and language locales (`Sec-CH-UA-Platform`).
- **Complete Isolation:** 100% separate cache, cookies, indexedDB, and local storage for every single profile.
- **Commercial GUI:** A sleek, dark-mode PyQt6 interface with one-click profile generation, cache clearing, and live resolution editing.

---

## 🧬 What Gets Spoofed Per Profile?

| Signal | Protection Method |
|---|---|
| User Agent / Client Hints | Native OS & Browser Spoofing |
| Screen Resolution | Standardized Hardware Pools (e.g., 1080p, 4K, Mac 1440) |
| Available Desktop Space | Smart Taskbar & UI Subtraction Math |
| Timezone | Auto-matched via Geocoding API |
| Language & Locale | Dynamically matched or safely defaulted |
| WebGL / Canvas / Audio | Native Binary Spoofing (No JS injection flags) |
| WebRTC | IP Leaks Blocked / Proxied |
| Headless Detection | Erased (Fakes standard graphical environment) |

---

## 🚀 Installation & Setup

Ninja Shield is designed to be lightweight. The heavy Camoufox engine (~500MB) will automatically download itself directly from the official repository during your first launch.

### Option A: Compiled Release (Easiest)
1. Download the latest `NinjaShield.exe` from the Releases tab.
2. Run the executable.
3. The setup wizard will automatically fetch the Camoufox engine and launch the UI.

### Option B: Developer Setup (Source Code)
Requires Windows 10/11 and Python 3.9+
```bash
# 1. Clone the repository
git clone [https://github.com/yourusername/ninja-shield.git](https://github.com/yourusername/ninja-shield.git)
cd ninja-shield

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Application
python gui.py
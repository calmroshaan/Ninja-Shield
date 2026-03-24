"""
Browser Launcher v4 - Camoufox Edition
Replaced Playwright/patchright with Camoufox (Firefox-based, binary-level fingerprinting).
Camoufox handles canvas, WebGL, fonts, audio, navigator, screen, and timezone spoofing
at the binary/patch level — no JS timing gaps, no injection race conditions.

What changed from v3:
  - Engine: patchright (Chromium) → Camoufox (Firefox)
  - Fingerprint spoofing: JS injection → binary-level (Camoufox native)
  - Stealth JS: REMOVED for Camoufox-handled properties; WebRTC JS block KEPT as extra layer
  - Profile isolation: user_data_dir still used (Camoufox supports it via `profile` param)
  - All function signatures identical — gui.py needs zero changes
"""

import sys
import io
try:
    if sys.stdout and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

import asyncio
import os
import json
from pathlib import Path
from fingerprint_engine import load_fingerprint


def build_webrtc_protection_script(fp: dict) -> str:
    """
    Minimal JS injection — only WebRTC leak protection.
    Everything else (canvas, WebGL, audio, navigator, screen, fonts) is
    handled natively by Camoufox at binary level. No need to inject those.
    """
    return """
(function() {
'use strict';

// -- WebRTC IP Leak Protection -------------------------------------------
// Camoufox does not patch WebRTC policy at binary level, so we keep this
// as a JS layer to block real local IP exposure through ICE candidates.
if (typeof RTCPeerConnection !== 'undefined') {
    const _OrigRTC = RTCPeerConnection;
    window.RTCPeerConnection = function(config, constraints) {
        if (config && config.iceServers) {
            config.iceTransportPolicy = 'relay';
        }
        const pc = new _OrigRTC(config || {}, constraints);

        const _origCreateOffer = pc.createOffer.bind(pc);
        pc.createOffer = async function(...args) {
            const offer = await _origCreateOffer(...args);
            offer.sdp = offer.sdp.replace(/a=candidate:.*host.*\\r\\n/g, '');
            offer.sdp = offer.sdp.replace(/c=IN IP4 (192\\.168|10\\.|172\\.(1[6-9]|2[0-9]|3[01]))\\..*\\r\\n/g, '');
            return offer;
        };

        const _origAddIce = pc.addIceCandidate.bind(pc);
        pc.addIceCandidate = function(candidate) {
            if (candidate && candidate.candidate &&
                (candidate.candidate.includes(' host ') ||
                 candidate.candidate.match(/192\\.168|10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\./))) {
                return Promise.resolve();
            }
            return _origAddIce(candidate);
        };
        return pc;
    };
    window.RTCPeerConnection.prototype = _OrigRTC.prototype;
}
['webkitRTCPeerConnection', 'mozRTCPeerConnection'].forEach(name => {
    if (window[name]) window[name] = window.RTCPeerConnection;
});

})();
"""


async def launch_browser(profile_name: str,
                          url: str = "about:blank",
                          profiles_dir: str = "profiles",
                          headless: bool = False):
    from camoufox.async_api import AsyncCamoufox

    fp            = load_fingerprint(profile_name, profiles_dir)
    import screeninfo
    try:
        monitor = screeninfo.get_monitors()[0]
        win_width  = monitor.width
        win_height = monitor.height
    except Exception:
        win_width  = 1366
        win_height = 768
    webrtc_js     = build_webrtc_protection_script(fp)
    user_data_dir = os.path.join(profiles_dir, f"browser_data_{profile_name}")
    Path(user_data_dir).mkdir(exist_ok=True)

    # -- Proxy config -------------------------------------------------------
    proxy_config = None
    proxy = fp.get("proxy")
    if proxy and proxy.get("host"):
        proxy_url = f"{proxy.get('protocol', 'http')}://"
        if proxy.get("username"):
            proxy_url += f"{proxy['username']}:{proxy.get('password', '')}@"
        proxy_url += f"{proxy['host']}:{proxy['port']}"
        proxy_config = proxy_url

    print(f"\n[{profile_name}] -- Launching ------------------------------")
    print(f"  Engine:   Camoufox (Firefox, binary-level fingerprinting)")
    print(f"  OS:       {fp.get('os_name', '?')}  |  Platform: {fp.get('platform', 'Win32')}")
    print(f"  Screen:   {fp['screen_width']}x{fp['screen_height']}")
    print(f"  Timezone: {fp['timezone']}  |  Lang: {fp['languages'][0]}")
    if proxy_config:
        print(f"  Proxy:    {proxy.get('protocol','http')}://{proxy['host']}:{proxy['port']}")
    else:
        print(f"  Proxy:    None (VPN mode or local)")
    print(f"  WebRTC:   Protected - local IP leak blocked (JS layer)")

    # -- Build Camoufox fingerprint config ----------------------------------
    # Camoufox accepts these natively and applies them at binary/patch level.
    # No JS injection needed for these fields.
    # -- Build Camoufox launch kwargs ---------------------------------------
    # Camoufox handles fingerprinting natively via top-level params.
    # The config={} dict is only for low-level Camoufox property overrides
    # using its internal property names (from properties.json).
    # Everything else is passed as direct keyword arguments to AsyncCamoufox.

    # Find Camoufox executable path explicitly
    try:
        from camoufox.pkgman import INSTALL_DIR
        camoufox_exec = os.path.join(str(INSTALL_DIR), "camoufox.exe")
        if not os.path.exists(camoufox_exec):
            camoufox_exec = None
    except Exception:
        camoufox_exec = None

    launch_kwargs = dict(
        headless=headless,
        persistent_context=True,
        user_data_dir=user_data_dir,
        os="windows",
        locale=fp["languages"][0],
        fonts=fp.get("fonts", ["Arial", "Verdana"]),
        block_webrtc=False,
        window=(win_width, win_height - 80),
        config={"timezone": fp["timezone"]},
        firefox_user_prefs={
            "browser.tabs.selectOwnerOnClose": True,
            "ui.key.menuAccessKeyFocuses": False,
            "browser.tabs.closeWindowWithLastTab": False,
            "browser.toolbars.bookmarks.visibility": "always",
            "browser.navigation.requireUserInteraction": False,
            "fission.bfcacheInParent": True,
            "browser.sessionhistory.max_entries": 50,
            "browser.sessionhistory.max_total_viewers": 4,
        },
        i_know_what_im_doing=True,
    )

    if camoufox_exec:
        launch_kwargs["executable_path"] = camoufox_exec

    if proxy_config:
        launch_kwargs["proxy"] = proxy_config

    async with AsyncCamoufox(**launch_kwargs) as browser:
        # Get or open a page
        page = browser.pages[0] if browser.pages else await browser.new_page()

        # Inject WebRTC protection on every page (only JS layer we keep)
        await browser.add_init_script(webrtc_js)
        await page.add_init_script(webrtc_js)

        # Inject WebRTC protection into new pages opened during session
        async def inject_on_new_page(new_page):
            try:
                await new_page.add_init_script(webrtc_js)
            except Exception:
                pass

        browser.on("page", inject_on_new_page)

        # Inject into web workers
        async def inject_worker(worker):
            try:
                await worker.evaluate(webrtc_js)
            except Exception:
                pass

        page.on("worker", inject_worker)

        try:
            await page.goto(url, wait_until="commit", timeout=30000)
        except Exception:
            pass  # Page may redirect — that is fine, browser stays open

        print(f"\n[{profile_name}]  Browser ready!")
        print(f"  Close the browser window to exit.\n")

        # Keep-alive loop — signals GUI when browser closes
        disconnected = asyncio.Event()
        browser.on("disconnected", lambda: disconnected.set())
        try:
            await asyncio.wait_for(disconnected.wait(), timeout=3600)
        except (asyncio.TimeoutError, KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            try:
                await browser.close()
            except Exception:
                pass  # Browser already closed — that is fine
            print(f"[{profile_name}] Browser closed.")


def launch_profile(profile_name: str,
                   url: str = "about:newtab",
                   profiles_dir: str = "profiles"):
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(launch_browser(profile_name, url, profiles_dir))


if __name__ == "__main__":
    import sys
    profile = sys.argv[1] if len(sys.argv) > 1 else "profile_1"
    profiles_dir = sys.argv[2] if len(sys.argv) > 2 else "profiles"
    launch_profile(profile, profiles_dir=profiles_dir)

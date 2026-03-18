"""
Browser Launcher v3 - Maximum GoLogin-level stealth
New in v3:
  - WebRTC IP leak protection (blocks real IP exposure)
  - Battery API spoofing
  - Network Connection API spoofing
  - Real plugin objects (not just count)
  - devicePixelRatio spoofing
  - Permissions API spoofing (no automation flags)
  - Media devices spoofing (fake camera/mic list)
  - Speech synthesis voices spoofing
  - ClientRects noise (font fingerprint defense)
  - navigator.vendor / vendorSub / productSub
  - window.outerWidth / outerHeight
  - Proxy support per profile
  - chrome.app / chrome.runtime realistic object
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

WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 800


def build_stealth_script(fp: dict) -> str:
    langs        = json.dumps(fp["languages"])
    fonts        = json.dumps(fp.get("fonts", ["Arial", "Verdana"]))
    plugins      = json.dumps(fp.get("plugins", []))
    dpr          = fp.get("device_pixel_ratio", 1.0)
    battery_lvl  = fp.get("battery_level", 1.0)
    battery_chg  = str(fp.get("battery_charging", True)).lower()
    conn_type    = fp.get("connection_type", "wifi")
    conn_down    = fp.get("connection_downlink", 10)
    conn_rtt     = fp.get("connection_rtt", 50)
    vendor_sub   = fp.get("vendor_sub", "")
    product_sub  = fp.get("product_sub", "20030107")
    chrome_ver   = fp.get("chrome_version", "146")
    wgl_vendor   = fp.get("webgl_vendor", "Google Inc. (Intel)")
    wgl_renderer = fp.get("webgl_renderer", "ANGLE (Intel)")
    wgl_shading  = fp.get("webgl_shading_lang", "WebGL GLSL ES 1.0")
    wgl_max_tex  = fp.get("webgl_max_texture", 16384)

    return f"""
// ========================================================================
//  STEALTH INJECTION v3 - Maximum fingerprint protection
// ========================================================================

(function() {{
'use strict';

// -- Utility: safe property override --------------------------------------
function def(obj, prop, value) {{
    try {{
        Object.defineProperty(obj, prop, {{
            get: typeof value === 'function' ? value : () => value,
            configurable: true,
            enumerable: true,
        }});
    }} catch(e) {{}}
}}

// -- 1. NAVIGATOR ---------------------------------------------------------
def(navigator, 'userAgent',          '{fp["user_agent"]}');
def(navigator, 'platform',           '{fp["platform"]}');
def(navigator, 'hardwareConcurrency', {fp["hardware_concurrency"]});
def(navigator, 'deviceMemory',        {fp.get("device_memory", 8)});
def(navigator, 'languages',           {langs});
def(navigator, 'language',           '{fp["languages"][0]}');
def(navigator, 'cookieEnabled',       true);
def(navigator, 'doNotTrack',          {json.dumps(fp.get("do_not_track"))});
def(navigator, 'maxTouchPoints',      {fp.get("touch_points", 0)});
def(navigator, 'pdfViewerEnabled',    {str(fp.get("pdf_viewer_enabled", True)).lower()});
def(navigator, 'vendor',             'Google Inc.');
def(navigator, 'vendorSub',          '{vendor_sub}');
def(navigator, 'productSub',         '{product_sub}');
def(navigator, 'product',            'Gecko');
def(navigator, 'appCodeName',        'Mozilla');
def(navigator, 'appName',            'Netscape');
def(navigator, 'appVersion',         '{fp["user_agent"].replace("Mozilla/", "")}');
def(navigator, 'webdriver',           undefined);

// -- 2. SCREEN ------------------------------------------------------------
def(screen, 'width',       {fp["screen_width"]});
def(screen, 'height',      {fp["screen_height"]});
def(screen, 'availWidth',  {fp["screen_width"]});
def(screen, 'availHeight', {fp["screen_height"] - 40});
def(screen, 'availLeft',   0);
def(screen, 'availTop',    0);
def(screen, 'colorDepth',  {fp["color_depth"]});
def(screen, 'pixelDepth',  {fp["color_depth"]});
def(screen, 'orientation', {{ type: 'landscape-primary', angle: 0 }});

// -- 3. WINDOW ------------------------------------------------------------
def(window, 'devicePixelRatio', {dpr});
def(window, 'outerWidth',       {fp["screen_width"]});
def(window, 'outerHeight',      {fp["screen_height"]});
def(window, 'innerWidth',       {WINDOW_WIDTH});
def(window, 'innerHeight',      {WINDOW_HEIGHT});

// -- 4. WEBGL - full parameter spoofing -----------------------------------
function patchWebGL(ctx) {{
    if (!ctx) return;
    const orig = ctx.getParameter.bind(ctx);
    ctx.getParameter = function(p) {{
        if (p === 37445) return '{wgl_vendor}';
        if (p === 37446) return '{wgl_renderer}';
        if (p === 35724) return '{wgl_shading}';
        if (p === 34076) return {wgl_max_tex};
        if (p === 3379)  return {wgl_max_tex};
        if (p === 34024) return {wgl_max_tex};
        if (p === 36349) return 1024;
        if (p === 34921) return 16;
        if (p === 35661) return 16;
        if (p === 35660) return 8;
        return orig(p);
    }};
    const origExt = ctx.getExtension.bind(ctx);
    ctx.getExtension = function(name) {{
        if (name === 'WEBGL_debug_renderer_info') {{
            return {{
                UNMASKED_VENDOR_WEBGL: 37445,
                UNMASKED_RENDERER_WEBGL: 37446
            }};
        }}
        return origExt(name);
    }};
}}

const origGetContext = HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext = function(type, attrs) {{
    const ctx = origGetContext.call(this, type, attrs);
    if (type === 'webgl' || type === 'experimental-webgl' || type === 'webgl2') {{
        patchWebGL(ctx);
    }}
    return ctx;
}};

// Also patch directly
try {{ patchWebGL(document.createElement('canvas').getContext('webgl')); }} catch(e) {{}}
try {{ patchWebGL(document.createElement('canvas').getContext('webgl2')); }} catch(e) {{}}

// -- 5. CANVAS NOISE ------------------------------------------------------
const _cseed = {fp["canvas_noise_seed"]};
function _crng(s) {{
    let v = s;
    return () => {{ v = (v * 9301 + 49297) % 233280; return v / 233280; }};
}}
const _crand = _crng(_cseed);

const _origToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function(type, quality) {{
    const ctx = this.getContext('2d');
    if (ctx && this.width > 0 && this.height > 0) {{
        const img = ctx.getImageData(0, 0, this.width, this.height);
        for (let i = 0; i < img.data.length; i += 99) {{
            img.data[i] = img.data[i] ^ (Math.floor(_crand() * 3));
        }}
        ctx.putImageData(img, 0, 0);
    }}
    return _origToDataURL.call(this, type, quality);
}};

const _origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
CanvasRenderingContext2D.prototype.getImageData = function(sx, sy, sw, sh) {{
    const img = _origGetImageData.call(this, sx, sy, sw, sh);
    for (let i = 0; i < img.data.length; i += 99) {{
        img.data[i] = img.data[i] ^ (Math.floor(_crand() * 3));
    }}
    return img;
}};

const _origToBlob = HTMLCanvasElement.prototype.toBlob;
HTMLCanvasElement.prototype.toBlob = function(cb, type, quality) {{
    const ctx = this.getContext('2d');
    if (ctx && this.width > 0 && this.height > 0) {{
        const img = ctx.getImageData(0, 0, this.width, this.height);
        for (let i = 0; i < img.data.length; i += 99) {{
            img.data[i] = img.data[i] ^ (Math.floor(_crand() * 3));
        }}
        ctx.putImageData(img, 0, 0);
    }}
    return _origToBlob.call(this, cb, type, quality);
}};

// -- 6. AUDIO NOISE -------------------------------------------------------
const _aseed = {fp["audio_noise_seed"]};
const _arand = _crng(_aseed);
if (typeof AudioBuffer !== 'undefined') {{
    const _origGetChannelData = AudioBuffer.prototype.getChannelData;
    AudioBuffer.prototype.getChannelData = function(ch) {{
        const data = _origGetChannelData.call(this, ch);
        for (let i = 0; i < data.length; i += 100) {{
            data[i] += (_arand() - 0.5) * 0.0001;
        }}
        return data;
    }};
}}
if (typeof AnalyserNode !== 'undefined') {{
    const _origGetFloatFreq = AnalyserNode.prototype.getFloatFrequencyData;
    AnalyserNode.prototype.getFloatFrequencyData = function(arr) {{
        _origGetFloatFreq.call(this, arr);
        for (let i = 0; i < arr.length; i++) {{ arr[i] += (_arand() - 0.5) * 0.1; }}
    }};
}}

// -- 7. CLIENT RECTS NOISE (font fingerprint defense) ---------------------
try {{
    const _rrseed = {fp.get("canvas_noise_seed", 1234) + 1};
    const _rrrand = _crng(_rrseed);
    const _noiseAmt = 0.000001;
    const _origGetBCR = Element.prototype.getBoundingClientRect;
    Element.prototype.getBoundingClientRect = function() {{
        const r = _origGetBCR.call(this);
        const n = _rrrand() * _noiseAmt;
        return new DOMRect(r.x + n, r.y + n, r.width, r.height);
    }};
}} catch(e) {{}}

// -- 8. PLUGINS (realistic) ------------------------------------------------
try {{
    const _pluginData = {plugins};
    const _fakePlugins = _pluginData.map((p, i) => {{
        const plugin = Object.create(Plugin.prototype);
        def(plugin, 'name',        p.name);
        def(plugin, 'filename',    p.filename);
        def(plugin, 'description', p.description || '');
        def(plugin, 'length',      (p.mimeTypes || []).length);
        return plugin;
    }});
    const _pluginArray = Object.create(PluginArray.prototype);
    def(_pluginArray, 'length', _fakePlugins.length);
    _fakePlugins.forEach((p, i) => {{ _pluginArray[i] = p; }});
    _pluginArray[Symbol.iterator] = function*() {{ for(let p of _fakePlugins) yield p; }};
    def(navigator, 'plugins', _pluginArray);
}} catch(e) {{}}

// -- 9. MIME TYPES ---------------------------------------------------------
try {{
    const _fakeMimes = Object.create(MimeTypeArray.prototype);
    def(_fakeMimes, 'length', 2);
    def(navigator, 'mimeTypes', _fakeMimes);
}} catch(e) {{}}

// -- 10. WEBRTC LEAK PROTECTION --------------------------------------------
// Block WebRTC from exposing real local IP - most critical for proxy/VPN use
if (typeof RTCPeerConnection !== 'undefined') {{
    const _OrigRTC = RTCPeerConnection;
    window.RTCPeerConnection = function(config, constraints) {{
        // Force ONLY relay through TURN (blocks local IP discovery)
        if (config && config.iceServers) {{
            config.iceTransportPolicy = 'relay';
        }}
        const pc = new _OrigRTC(config || {{}}, constraints);

        // Intercept SDP to strip local IP candidates
        const _origCreateOffer = pc.createOffer.bind(pc);
        pc.createOffer = async function(...args) {{
            const offer = await _origCreateOffer(...args);
            offer.sdp = offer.sdp.replace(/a=candidate:.*host.*\\r\\n/g, '');
            offer.sdp = offer.sdp.replace(/c=IN IP4 (192\\.168|10\\.|172\\.(1[6-9]|2[0-9]|3[01]))\\..*\\r\\n/g, '');
            return offer;
        }};

        const _origAddIce = pc.addIceCandidate.bind(pc);
        pc.addIceCandidate = function(candidate) {{
            // Block local network candidates
            if (candidate && candidate.candidate &&
                (candidate.candidate.includes(' host ') ||
                 candidate.candidate.match(/192\\.168|10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\./))) {{
                return Promise.resolve();
            }}
            return _origAddIce(candidate);
        }};

        return pc;
    }};
    // Copy prototype
    window.RTCPeerConnection.prototype = _OrigRTC.prototype;
}}

// Also override deprecated versions
['webkitRTCPeerConnection','mozRTCPeerConnection'].forEach(name => {{
    if (window[name]) window[name] = window.RTCPeerConnection;
}});

// -- 11. BATTERY API -------------------------------------------------------
if (navigator.getBattery) {{
    navigator.getBattery = function() {{
        return Promise.resolve({{
            charging:              {battery_chg},
            chargingTime:          {0 if battery_chg == 'true' else 'Infinity'},
            dischargingTime:       {'Infinity' if battery_chg == 'true' else 3600},
            level:                 {battery_lvl},
            addEventListener:      () => {{}},
            removeEventListener:   () => {{}},
            dispatchEvent:         () => false,
        }});
    }};
}}

// -- 12. NETWORK CONNECTION API --------------------------------------------
if ('connection' in navigator) {{
    const _fakeConn = {{
        effectiveType: '{conn_type}',
        type:          '{conn_type}',
        downlink:       {conn_down},
        rtt:            {conn_rtt},
        saveData:       false,
        addEventListener:    () => {{}},
        removeEventListener: () => {{}},
    }};
    def(navigator, 'connection',       _fakeConn);
    def(navigator, 'mozConnection',    _fakeConn);
    def(navigator, 'webkitConnection', _fakeConn);
}}

// -- 13. MEDIA DEVICES (fake camera/mic - no real device info leaked) ------
if (navigator.mediaDevices) {{
    const _origEnum = navigator.mediaDevices.enumerateDevices.bind(navigator.mediaDevices);
    navigator.mediaDevices.enumerateDevices = async function() {{
        return [
            {{ deviceId: 'default', kind: 'audioinput',  label: '', groupId: 'default' }},
            {{ deviceId: 'default', kind: 'audiooutput', label: '', groupId: 'default' }},
            {{ deviceId: 'default', kind: 'videoinput',  label: '', groupId: 'default' }},
        ];
    }};
}}

// -- 14. SPEECH SYNTHESIS (voice fingerprint) -----------------------------
if (typeof speechSynthesis !== 'undefined') {{
    const _origGetVoices = speechSynthesis.getVoices.bind(speechSynthesis);
    speechSynthesis.getVoices = function() {{
        const voices = _origGetVoices();
        // Return only generic voices, no locale-specific ones that expose real OS
        return voices.slice(0, 3);
    }};
}}

// -- 15. PERMISSIONS API (hide automation flags) ---------------------------
if (navigator.permissions) {{
    const _origQuery = navigator.permissions.query.bind(navigator.permissions);
    navigator.permissions.query = function(params) {{
        if (params.name === 'notifications') {{
            return Promise.resolve({{ state: 'prompt', onchange: null }});
        }}
        return _origQuery(params);
    }};
}}

// -- 16. CHROME OBJECT (realistic) -----------------------------------------
try {{
window.chrome = {{
    app: {{ isInstalled: false, getDetails: () => null, getIsInstalled: () => false, runningState: () => 'cannot_run' }},
    runtime: {{ id: undefined, connect: () => {{}}, sendMessage: () => {{}}, onMessage: {{ addListener: () => {{}}, removeListener: () => {{}} }} }},
    loadTimes: function() {{ return {{ requestTime: Date.now()/1000, startLoadTime: Date.now()/1000, commitLoadTime: Date.now()/1000, finishDocumentLoadTime: Date.now()/1000, finishLoadTime: Date.now()/1000, firstPaintTime: Date.now()/1000, firstPaintAfterLoadTime: 0, navigationType: 'Other', wasFetchedViaSpdy: false, wasNpnNegotiated: false, npnNegotiatedProtocol: 'unknown', wasAlternateProtocolAvailable: false, connectionInfo: 'http/1.1' }}; }},
    webstore: {{ install: () => {{}}, onInstallStageChanged: {{}}, onDownloadProgress: {{}} }},
    csi: function() {{ return {{ startE: Date.now(), onloadT: Date.now()+150, pageT: 1200, tran: 15 }}; }},
}};
}} catch(e) {{}}

// -- 17. AUTOMATION DETECTION REMOVAL -------------------------------------
try {{ delete navigator.__proto__.webdriver; }} catch(e) {{}}
try {{ delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array; }} catch(e) {{}}
try {{ delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise; }} catch(e) {{}}
try {{ delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol; }} catch(e) {{}}
try {{
    Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined, configurable: true }});
}} catch(e) {{}}

// -- 18. HISTORY (looks like real browsing) --------------------------------
try {{ history.replaceState(null, '', location.href); }} catch(e) {{}}

}})(); // end IIFE
"""


async def find_chrome_path() -> str:
    """Find real Chrome installation on Windows"""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome Beta\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome SxS\Application\chrome.exe"),
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "ms-playwright", "chromium-1208", "chrome-win64", "chrome.exe"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

async def launch_browser(profile_name: str,
                          url: str = "https://www.facebook.com",
                          profiles_dir: str = "profiles",
                          headless: bool = False):
    from playwright.async_api import async_playwright

    fp           = load_fingerprint(profile_name, profiles_dir)
    stealth_js   = build_stealth_script(fp)
    user_data_dir = os.path.join(profiles_dir, f"browser_data_{profile_name}")
    Path(user_data_dir).mkdir(exist_ok=True)

    # -- Proxy config ------------------------------------------------------
    proxy_config = None
    proxy = fp.get("proxy")
    if proxy and proxy.get("host"):
        proxy_config = {
            "server": f"{proxy.get('protocol','http')}://{proxy['host']}:{proxy['port']}",
        }
        if proxy.get("username"):
            proxy_config["username"] = proxy["username"]
            proxy_config["password"] = proxy.get("password", "")

    print(f"\n[{profile_name}] -- Launching ------------------------------")
    print(f"  UA:       {fp['user_agent'][:65]}...")
    print(f"  OS:       {fp.get('os_name','?')}  |  Platform: {fp['platform']}")
    print(f"  Screen:   {fp['screen_width']}x{fp['screen_height']}  DPR: {fp.get('device_pixel_ratio',1)}")
    print(f"  Timezone: {fp['timezone']}  |  Lang: {fp['languages'][0]}")
    print(f"  WebGL:    {fp['webgl_renderer'][:55]}...")
    print(f"  Battery:  {int(fp.get('battery_level',1)*100)}%  Charging: {fp.get('battery_charging',True)}")
    print(f"  Network:  {fp.get('connection_type','wifi')}  {fp.get('connection_downlink',10)}Mbps")
    if proxy_config:
        print(f"  Proxy:    {proxy_config['server']}")
    else:
        print(f"  Proxy:    None (VPN mode or local)")
    print(f"  WebRTC:    Protected - local IP leak blocked")

    chrome_ver = fp.get("chrome_version", "120")
    args = [
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-notifications",
        f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT + 80}",
        "--window-position=50,50",
        f"--lang={fp['languages'][0]}",
        "--disable-features=AutofillServerCommunication",
        # WebRTC IP protection
        "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
        "--webrtc-ip-handling-policy=disable_non_proxied_udp",
        # -- These 3 together hide the "controlled by automation" banner --
        "--disable-blink-features=AutomationControlled",
        "--disable-automation",
        "--hide-scrollbars",
    ]

    chrome_path = await find_chrome_path()

    if chrome_path:
        print(f"  Browser:  [OK] Real Chrome -> {chrome_path}")
    else:
        print(f"  Browser:  [WARN] Real Chrome not found - using Playwright Chromium (less stealthy)")
        print(f"  Tip: Install Google Chrome from https://chrome.google.com for best results")

    launch_kwargs = dict(
        user_data_dir=user_data_dir,
        headless=headless,
        locale=fp["languages"][0],
        timezone_id=fp["timezone"],
        user_agent=fp["user_agent"],
        viewport={"width": WINDOW_WIDTH, "height": WINDOW_HEIGHT},
        device_scale_factor=fp.get("device_pixel_ratio", 1.0),
        color_scheme="no-preference",
        ignore_https_errors=True,
        ignore_default_args=[
            "--enable-automation",
            "--enable-blink-features=IdleDetection",
        ],
        args=args,
        extra_http_headers={
            "Accept-Language": ",".join(fp["languages"]),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }
    )

    if chrome_path:
        launch_kwargs["executable_path"] = chrome_path

    if proxy_config:
        launch_kwargs["proxy"] = proxy_config

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(**launch_kwargs)

        # Inject stealth into main frame ONLY - not iframes
        # Injecting into Facebook's internal iframes caused renderer crashes
        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.add_init_script(stealth_js)

        try:
            await page.goto(url, wait_until="commit", timeout=30000)
        except Exception:
            pass  # Page may redirect - that's fine, browser stays open

        print(f"\n[{profile_name}]  Browser ready!")
        print(f"  Close the browser window to exit.\n")

        # Keep alive - handle browser dying gracefully
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
                pass  # Browser already closed - that's fine
            print(f"[{profile_name}] Browser closed.")


def launch_profile(profile_name: str,
                   url: str = "https://www.facebook.com",
                   profiles_dir: str = "profiles"):
    asyncio.run(launch_browser(profile_name, url, profiles_dir))


if __name__ == "__main__":
    import sys
    profile = sys.argv[1] if len(sys.argv) > 1 else "profile_1"
    profiles_dir = sys.argv[2] if len(sys.argv) > 2 else "profiles"
    launch_profile(profile, profiles_dir=profiles_dir)

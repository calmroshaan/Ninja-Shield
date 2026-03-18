"""
Fingerprint Engine v4 - Free-text VPN city + TimeZoneDB auto-timezone lookup
"""

import json
import random
import hashlib
import os
import urllib.request
import urllib.parse
from pathlib import Path

TIMEZONEDB_API_KEY = "YCI6EOT71S7J"

# ─── Language + Flag hints by keyword ────────────────────────────────────────
# Used to auto-assign language/flag when city is typed freely
REGION_HINTS = [
    {"keywords": ["usa", "united states", "new york", "los angeles", "chicago", "dallas", "miami", "seattle", "phoenix", "denver", "atlanta", "boston"], "languages": ["en-US", "en"], "flag": "🇺🇸"},
    {"keywords": ["uk", "united kingdom", "london", "manchester", "birmingham", "glasgow"], "languages": ["en-GB", "en"], "flag": "🇬🇧"},
    {"keywords": ["canada", "toronto", "vancouver", "montreal", "calgary"], "languages": ["en-CA", "en"], "flag": "🇨🇦"},
    {"keywords": ["australia", "sydney", "melbourne", "brisbane", "perth"], "languages": ["en-AU", "en"], "flag": "🇦🇺"},
    {"keywords": ["germany", "deutschland", "berlin", "frankfurt", "munich", "hamburg"], "languages": ["de-DE", "de", "en"], "flag": "🇩🇪"},
    {"keywords": ["france", "paris", "lyon", "marseille"], "languages": ["fr-FR", "fr", "en"], "flag": "🇫🇷"},
    {"keywords": ["netherlands", "amsterdam", "nl", "rotterdam"], "languages": ["nl-NL", "en"], "flag": "🇳🇱"},
    {"keywords": ["singapore"], "languages": ["en-SG", "en"], "flag": "🇸🇬"},
    {"keywords": ["japan", "tokyo", "osaka"], "languages": ["ja-JP", "ja", "en"], "flag": "🇯🇵"},
    {"keywords": ["india", "mumbai", "delhi", "bangalore", "hyderabad", "chennai"], "languages": ["en-IN", "en"], "flag": "🇮🇳"},
    {"keywords": ["brazil", "sao paulo", "rio", "brasil"], "languages": ["pt-BR", "pt", "en"], "flag": "🇧🇷"},
    {"keywords": ["uae", "dubai", "abu dhabi", "sharjah"], "languages": ["ar-AE", "en"], "flag": "🇦🇪"},
    {"keywords": ["pakistan", "karachi", "lahore", "islamabad", "rawalpindi", "faisalabad"], "languages": ["en-PK", "ur", "en"], "flag": "🇵🇰"},
    {"keywords": ["south africa", "johannesburg", "cape town", "durban"], "languages": ["en-ZA", "en"], "flag": "🇿🇦"},
    {"keywords": ["turkey", "istanbul", "ankara", "turkiye"], "languages": ["tr-TR", "tr", "en"], "flag": "🇹🇷"},
    {"keywords": ["saudi", "riyadh", "jeddah", "mecca"], "languages": ["ar-SA", "en"], "flag": "🇸🇦"},
    {"keywords": ["egypt", "cairo", "alexandria"], "languages": ["ar-EG", "en"], "flag": "🇪🇬"},
    {"keywords": ["italy", "rome", "milan", "italia"], "languages": ["it-IT", "it", "en"], "flag": "🇮🇹"},
    {"keywords": ["spain", "madrid", "barcelona", "espana"], "languages": ["es-ES", "es", "en"], "flag": "🇪🇸"},
    {"keywords": ["russia", "moscow", "saint petersburg"], "languages": ["ru-RU", "ru", "en"], "flag": "🇷🇺"},
    {"keywords": ["china", "beijing", "shanghai", "shenzhen"], "languages": ["zh-CN", "zh", "en"], "flag": "🇨🇳"},
    {"keywords": ["local", "no vpn", "none"], "languages": ["en-US", "en"], "flag": "🖥️"},
]

def _get_region_info(city: str) -> dict:
    """Match city string to region for language/flag assignment."""
    city_lower = city.lower()
    for region in REGION_HINTS:
        for kw in region["keywords"]:
            if kw in city_lower:
                return {"languages": region["languages"], "flag": region["flag"]}
    # Default fallback
    return {"languages": ["en-US", "en"], "flag": "🌍"}


def get_timezone_for_city(city: str) -> str:
    """
    Look up timezone for a city name using TimeZoneDB API.
    First geocodes city to lat/lng via nominatim (OpenStreetMap, free, no key),
    then queries TimeZoneDB with coordinates.
    Falls back to America/New_York if anything fails.
    """
    if not city or city.lower() in ("no vpn", "local", "none", "no vpn (local)"):
        return "America/New_York"

    try:
        # Step 1: Geocode city name → lat/lng using OpenStreetMap Nominatim (free, no key)
        geo_url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
            "q": city,
            "format": "json",
            "limit": 1
        })
        req = urllib.request.Request(geo_url, headers={"User-Agent": "NinjaShield/4.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            geo_data = json.loads(resp.read().decode())

        if not geo_data:
            return "America/New_York"

        lat = geo_data[0]["lat"]
        lng = geo_data[0]["lon"]

        # Step 2: Get timezone from TimeZoneDB using lat/lng
        tz_url = "https://api.timezonedb.com/v2.1/get-time-zone?" + urllib.parse.urlencode({
            "key": TIMEZONEDB_API_KEY,
            "format": "json",
            "by": "position",
            "lat": lat,
            "lng": lng
        })
        with urllib.request.urlopen(tz_url, timeout=8) as resp:
            tz_data = json.loads(resp.read().decode())

        if tz_data.get("status") == "OK":
            return tz_data["zoneName"]

    except Exception:
        pass

    return "America/New_York"


# ─── Data Pools ───────────────────────────────────────────────────────────────

USER_AGENTS = [
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "124"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "125"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "126"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "128"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "130"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "132"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "134"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "136"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "140"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "144"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "146"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", "os": "Mac",  "browser": "chrome",  "chrome_ver": "124"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",  "os": "Mac",  "browser": "chrome",  "chrome_ver": "130"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_0)   AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",  "os": "Mac",  "browser": "chrome",  "chrome_ver": "146"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",                                    "os": "Windows", "browser": "firefox", "chrome_ver": None},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",                                    "os": "Windows", "browser": "firefox", "chrome_ver": None},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0", "os": "Windows", "browser": "edge", "chrome_ver": "124"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0", "os": "Windows", "browser": "edge", "chrome_ver": "146"},
    {"ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",              "os": "Linux",   "browser": "chrome",  "chrome_ver": "130"},
]

OS_PLATFORM = {"Windows": "Win32", "Mac": "MacIntel", "Linux": "Linux x86_64"}

OS_SCREENS = {
    "Windows": [(1920,1080),(1920,1080),(1920,1080),(2560,1440),(1366,768),(1536,864),(1280,720),(1680,1050)],
    "Mac":     [(2560,1600),(2560,1440),(1440,900),(1680,1050),(3024,1964)],
    "Linux":   [(1920,1080),(1920,1080),(2560,1440),(1366,768),(1280,1024)],
}

HARDWARE_CONCURRENCY = [2, 4, 4, 4, 6, 8, 8, 8, 12, 16]
DEVICE_MEMORY        = [2, 4, 4, 8, 8, 8, 16]

WEBGL_PROFILES = [
    {"vendor": "Google Inc. (Intel)",  "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",        "shading": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)", "max_texture": 16384},
    {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)",         "shading": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)", "max_texture": 32768},
    {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",         "shading": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)", "max_texture": 32768},
    {"vendor": "Google Inc. (AMD)",    "renderer": "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",                  "shading": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)", "max_texture": 16384},
    {"vendor": "Google Inc. (Intel)",  "renderer": "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",     "shading": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)", "max_texture": 16384},
    {"vendor": "Apple Inc.",           "renderer": "Apple GPU",                                                                        "shading": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)", "max_texture": 16384},
]

PLUGIN_SETS = {
    "Windows": [
        [
            {"name": "PDF Viewer",               "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}, {"type": "text/pdf"}]},
            {"name": "Chrome PDF Viewer",        "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
            {"name": "Chromium PDF Viewer",      "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
            {"name": "Microsoft Edge PDF Viewer","filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
            {"name": "WebKit built-in PDF",      "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
        ],
    ],
    "Mac": [
        [
            {"name": "PDF Viewer",        "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}, {"type": "text/pdf"}]},
            {"name": "Chrome PDF Viewer", "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
        ],
    ],
    "Linux": [
        [{"name": "PDF Viewer", "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]}],
    ],
}

FONT_SETS = {
    "Windows": [
        ["Arial", "Arial Black", "Calibri", "Cambria", "Comic Sans MS", "Courier New", "Georgia",
         "Impact", "Lucida Console", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"],
        ["Arial", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Verdana"],
    ],
    "Mac": [
        ["Arial", "Helvetica", "Helvetica Neue", "Times New Roman", "Courier New", "Georgia", "Verdana", "Menlo"],
    ],
    "Linux": [
        ["Arial", "Courier New", "DejaVu Sans", "Liberation Sans", "Ubuntu", "Verdana"],
    ],
}

BATTERY_LEVELS   = [0.23, 0.45, 0.67, 0.78, 0.89, 0.92, 0.95, 1.0]
BATTERY_CHARGING = [True, True, False, False, False, True]
CONNECTION_TYPES = ["wifi", "wifi", "wifi", "ethernet", "4g"]
CONNECTION_DOWN  = [10, 50, 100, 100, 50, 25]
CONNECTION_RTT   = [50, 50, 100, 100, 150, 200]


def generate_fingerprint(profile_name: str, vpn_city: str = "No VPN (Local)", timezone: str = None) -> dict:
    seed = int(hashlib.md5(profile_name.encode()).hexdigest()[:8], 16)
    rng  = random.Random(seed)

    ua_data  = rng.choice(USER_AGENTS)
    os_name  = ua_data["os"]
    browser  = ua_data["browser"]
    screen   = rng.choice(OS_SCREENS[os_name])
    webgl    = rng.choice(WEBGL_PROFILES)
    plugins  = rng.choice(PLUGIN_SETS.get(os_name, PLUGIN_SETS["Windows"]))
    fonts    = rng.choice(FONT_SETS.get(os_name, FONT_SETS["Windows"]))

    region   = _get_region_info(vpn_city)
    languages = region["languages"]
    flag      = region["flag"]

    # Timezone: use provided, or auto-lookup, or fallback
    if timezone:
        tz = timezone
    elif vpn_city.lower() not in ("no vpn (local)", "no vpn", "local", "none", ""):
        tz = get_timezone_for_city(vpn_city)
    else:
        tz = rng.choice(["America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/London"])

    is_desktop       = rng.random() < 0.4
    battery_level    = 1.0 if is_desktop else rng.choice(BATTERY_LEVELS)
    battery_charging = True if is_desktop else rng.choice(BATTERY_CHARGING)
    conn_idx         = rng.randint(0, len(CONNECTION_TYPES) - 1)
    dpr = rng.choice([1.0, 2.0, 2.0]) if os_name == "Mac" else rng.choice([1.0, 1.0, 1.25, 1.5])

    return {
        "profile_name":         profile_name,
        "vpn_city":             vpn_city,
        "vpn_flag":             flag,
        "vpn_hint":             f"Connect VPN to {vpn_city}",
        "user_agent":           ua_data["ua"],
        "browser_type":         browser,
        "chrome_version":       ua_data.get("chrome_ver"),
        "os_name":              os_name,
        "platform":             OS_PLATFORM[os_name],
        "screen_width":         screen[0],
        "screen_height":        screen[1],
        "color_depth":          rng.choice([24, 24, 32]),
        "device_pixel_ratio":   dpr,
        "timezone":             tz,
        "languages":            languages,
        "hardware_concurrency": rng.choice(HARDWARE_CONCURRENCY),
        "device_memory":        rng.choice(DEVICE_MEMORY),
        "webgl_vendor":         webgl["vendor"],
        "webgl_renderer":       webgl["renderer"],
        "webgl_shading_lang":   webgl["shading"],
        "webgl_max_texture":    webgl["max_texture"],
        "webgl_max_viewport":   [32767, 32767],
        "canvas_noise_seed":    rng.randint(1000, 9999),
        "audio_noise_seed":     rng.randint(1000, 9999),
        "webgl_noise_seed":     rng.randint(1000, 9999),
        "plugins":              plugins,
        "fonts":                fonts,
        "do_not_track":         rng.choice([None, None, "1"]),
        "touch_points":         rng.choice([0, 0, 0, 1, 5]),
        "cookie_enabled":       True,
        "pdf_viewer_enabled":   rng.choice([True, True, False]),
        "battery_level":        battery_level,
        "battery_charging":     battery_charging,
        "connection_type":      CONNECTION_TYPES[conn_idx],
        "connection_downlink":  CONNECTION_DOWN[conn_idx],
        "connection_rtt":       CONNECTION_RTT[conn_idx],
        "vendor_sub":           "",
        "product":              "Gecko",
        "product_sub":          "20030107" if browser == "chrome" else "20100101",
        "build_id":             None if browser == "chrome" else "20230112",
    }


def save_fingerprint(fp: dict, profiles_dir: str = "profiles"):
    Path(profiles_dir).mkdir(exist_ok=True)
    path = os.path.join(profiles_dir, f"{fp['profile_name']}.json")
    with open(path, "w") as f:
        json.dump(fp, f, indent=2)
    return path


def load_fingerprint(profile_name: str, profiles_dir: str = "profiles") -> dict:
    path = os.path.join(profiles_dir, f"{profile_name}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    fp = generate_fingerprint(profile_name)
    save_fingerprint(fp, profiles_dir)
    return fp


def assign_vpn_city(profile_name: str, vpn_city: str, profiles_dir: str = "profiles"):
    fp       = load_fingerprint(profile_name, profiles_dir)
    region   = _get_region_info(vpn_city)
    timezone = get_timezone_for_city(vpn_city)
    fp["vpn_city"]  = vpn_city
    fp["vpn_flag"]  = region["flag"]
    fp["vpn_hint"]  = f"Connect VPN to {vpn_city}"
    fp["languages"] = region["languages"]
    fp["timezone"]  = timezone
    save_fingerprint(fp, profiles_dir)
    return fp


def list_profiles(profiles_dir: str = "profiles") -> list:
    Path(profiles_dir).mkdir(exist_ok=True)
    return [f.stem for f in Path(profiles_dir).glob("*.json")]


if __name__ == "__main__":
    fp = generate_fingerprint("test_01", "Dubai, UAE")
    print(json.dumps(fp, indent=2))

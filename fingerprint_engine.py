"""
Fingerprint Engine v4.1 - Camoufox (Firefox) Edition
Fixed: Swapped Chromium bundles for Firefox bundles.
Fixed: Removed hardcoded TimeZoneDB key, switched to free Open-Meteo API.
"""

import json
import random
import hashlib
import os
import urllib.request
import urllib.parse
from pathlib import Path

# ─── Language + Flag hints by keyword ────────────────────────────────────────
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
    {"keywords": ["pakistan", "karachi", "lahore", "islamabad"], "languages": ["en-PK", "ur", "en"], "flag": "🇵🇰"},
    {"keywords": ["south africa", "johannesburg", "cape town"], "languages": ["en-ZA", "en"], "flag": "🇿🇦"},
    {"keywords": ["turkey", "istanbul", "ankara"], "languages": ["tr-TR", "tr", "en"], "flag": "🇹🇷"},
    {"keywords": ["local", "no vpn", "none"], "languages": ["en-US", "en"], "flag": "🖥️"},
]

def _get_region_info(city: str) -> dict:
    city_lower = city.lower()
    for region in REGION_HINTS:
        for kw in region["keywords"]:
            if kw in city_lower:
                return {"languages": region["languages"], "flag": region["flag"]}
    return {"languages": ["en-US", "en"], "flag": "🌍"}


def get_timezone_for_city(city: str) -> str:
    """
    Look up timezone for a city name.
    Step 1: OpenStreetMap Nominatim (Free) for Lat/Lng
    Step 2: Open-Meteo (Free, NO KEY) for Timezone resolution
    """
    if not city or city.lower() in ("no vpn", "local", "none", "no vpn (local)"):
        return "America/New_York"

    try:
        # Step 1: Geocode city name → lat/lng
        geo_url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
            "q": city, "format": "json", "limit": 1
        })
        req = urllib.request.Request(geo_url, headers={"User-Agent": "NinjaShield/4.1"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            geo_data = json.loads(resp.read().decode())

        if not geo_data:
            return "America/New_York"

        lat = geo_data[0]["lat"]
        lng = geo_data[0]["lon"]

        # Step 2: Get timezone from Open-Meteo using lat/lng (No API Key needed)
        tz_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&timezone=auto"
        req = urllib.request.Request(tz_url, headers={"User-Agent": "NinjaShield/4.1"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            tz_data = json.loads(resp.read().decode())
            
        if "timezone" in tz_data:
            return tz_data["timezone"]

    except Exception as e:
        print(f"[Timezone] Lookup failed: {e}")

    return "America/New_York"


# ─── Coherent FIREFOX Device Bundles ──────────────────────────────────────────
# Replaced all Chromium/V8 traces with strict Firefox/SpiderMonkey parameters.
# Camoufox handles WebGL spoofing natively, so we only pass structural OS data.

# Expanded pool of 20 statistically common Windows hardware configurations
DEVICE_BUNDLES = [
    # 1080p Standard Laptops/Desktops (Most Common - ~60% of users)
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1920, "height": 1080}, "cpu": 8, "ram": 8},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1920, "height": 1080}, "cpu": 8, "ram": 16},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1920, "height": 1080}, "cpu": 4, "ram": 8},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1920, "height": 1080}, "cpu": 12, "ram": 16},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1920, "height": 1080}, "cpu": 16, "ram": 32},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1920, "height": 1080}, "cpu": 6, "ram": 8},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1920, "height": 1080}, "cpu": 8, "ram": 12},

    # 1366x768 Budget/Older Laptops (~15% of users)
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1366, "height": 768}, "cpu": 4, "ram": 8},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1366, "height": 768}, "cpu": 4, "ram": 4},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1366, "height": 768}, "cpu": 8, "ram": 8},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1366, "height": 768}, "cpu": 2, "ram": 4},

    # 1440p (2K) Gaming/Creator Monitors (~10% of users)
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 2560, "height": 1440}, "cpu": 16, "ram": 32},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 2560, "height": 1440}, "cpu": 12, "ram": 16},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 2560, "height": 1440}, "cpu": 8, "ram": 16},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 2560, "height": 1440}, "cpu": 24, "ram": 32},

    # 4K High-End Displays (~10% of users)
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 3840, "height": 2160}, "cpu": 16, "ram": 32},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 3840, "height": 2160}, "cpu": 24, "ram": 64},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 3840, "height": 2160}, "cpu": 8, "ram": 16},

    # Odd/Office resolutions (~5% of users)
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1600, "height": 900}, "cpu": 4, "ram": 8},
    {"os_name": "windows", "os_version": "10.0", "screen": {"width": 1536, "height": 864}, "cpu": 8, "ram": 8},
]
def generate_fingerprint(profile_name: str, vpn_city: str = "No VPN (Local)", timezone: str = None) -> dict:
    import secrets
    # Generate a cryptographically secure, truly random seed for every new profile
    true_random_seed = secrets.token_hex(8)
    rng  = random.Random(true_random_seed)

    bundle    = rng.choice(DEVICE_BUNDLES)
    region    = _get_region_info(vpn_city)
    languages = region["languages"]
    flag      = region["flag"]

    if timezone:
        tz = timezone
    elif vpn_city.lower() not in ("no vpn (local)", "no vpn", "local", "none", ""):
        tz = get_timezone_for_city(vpn_city)
    else:
        tz = rng.choice(["America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/London"])

    return {
        "profile_name":  profile_name,
        "vpn_city":      vpn_city,
        "vpn_flag":      flag,
        "vpn_hint":      f"Connect VPN to {vpn_city}",
        "os_name":       bundle["os"],
        "platform":      bundle["platform"],
        "user_agent":    bundle["ua"],
        "screen_width":  bundle["screen"][0],
        "screen_height": bundle["screen"][1],
        "timezone":      tz,
        "languages":     languages,
        "fonts":         bundle["fonts"],
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
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


# ─── Coherent Device Bundles ──────────────────────────────────────────────────
# Each bundle is a complete real-world device profile.
# Every value in a bundle is consistent with every other value.
# No random mixing across bundles — pick one bundle, use all its values.

DEVICE_BUNDLES = [
    # ── Windows 11 / Intel UHD 620 / 8GB / 4-core ──
    {"os": "Windows", "os_version": "11", "chrome_ver": "124",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1920, 1080), "dpr": 1.0, "cores": 4, "ram": 8,
     "webgl_vendor": "Google Inc. (Intel)", "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "ethernet", "conn_down": 100, "conn_rtt": 50,
     "fonts": ["Arial", "Arial Black", "Calibri", "Cambria", "Comic Sans MS", "Courier New", "Georgia", "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 10 / NVIDIA GTX 1060 / 16GB / 8-core ──
    {"os": "Windows", "os_version": "10", "chrome_ver": "126",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1920, 1080), "dpr": 1.0, "cores": 8, "ram": 16,
     "webgl_vendor": "Google Inc. (NVIDIA)", "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 32768, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "ethernet", "conn_down": 100, "conn_rtt": 50,
     "fonts": ["Arial", "Calibri", "Consolas", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 11 / NVIDIA RTX 3060 / 16GB / 8-core ──
    {"os": "Windows", "os_version": "11", "chrome_ver": "130",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (2560, 1440), "dpr": 1.25, "cores": 8, "ram": 16,
     "webgl_vendor": "Google Inc. (NVIDIA)", "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 32768, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "ethernet", "conn_down": 100, "conn_rtt": 50,
     "fonts": ["Arial", "Arial Black", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 10 / AMD Radeon RX 580 / 8GB / 6-core ──
    {"os": "Windows", "os_version": "10", "chrome_ver": "128",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1920, 1080), "dpr": 1.0, "cores": 6, "ram": 8,
     "webgl_vendor": "Google Inc. (AMD)", "webgl_renderer": "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "wifi", "conn_down": 50, "conn_rtt": 100,
     "fonts": ["Arial", "Calibri", "Cambria", "Comic Sans MS", "Courier New", "Georgia", "Impact", "Segoe UI", "Tahoma", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 11 / Intel Iris Xe / 16GB / 4-core (laptop) ──
    {"os": "Windows", "os_version": "11", "chrome_ver": "132",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1920, 1080), "dpr": 1.5, "cores": 4, "ram": 16,
     "webgl_vendor": "Google Inc. (Intel)", "webgl_renderer": "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": False, "battery_level": 0.67,
     "conn_type": "wifi", "conn_down": 50, "conn_rtt": 100,
     "fonts": ["Arial", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 10 / Intel UHD 630 / 8GB / 4-core (laptop) ──
    {"os": "Windows", "os_version": "10", "chrome_ver": "134",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1366, 768), "dpr": 1.0, "cores": 4, "ram": 8,
     "webgl_vendor": "Google Inc. (Intel)", "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": False, "battery_level": 0.45,
     "conn_type": "wifi", "conn_down": 25, "conn_rtt": 150,
     "fonts": ["Arial", "Calibri", "Courier New", "Georgia", "Lucida Console", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 11 / NVIDIA RTX 2070 / 32GB / 12-core ──
    {"os": "Windows", "os_version": "11", "chrome_ver": "136",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (2560, 1440), "dpr": 1.0, "cores": 12, "ram": 32,
     "webgl_vendor": "Google Inc. (NVIDIA)", "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 2070 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 32768, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "ethernet", "conn_down": 100, "conn_rtt": 50,
     "fonts": ["Arial", "Arial Black", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 10 / AMD Radeon RX 5700 / 16GB / 8-core ──
    {"os": "Windows", "os_version": "10", "chrome_ver": "140",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1920, 1080), "dpr": 1.0, "cores": 8, "ram": 16,
     "webgl_vendor": "Google Inc. (AMD)", "webgl_renderer": "ANGLE (AMD, AMD Radeon RX 5700 XT Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "ethernet", "conn_down": 100, "conn_rtt": 50,
     "fonts": ["Arial", "Calibri", "Consolas", "Courier New", "Georgia", "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 11 / Intel UHD 770 / 32GB / 16-core ──
    {"os": "Windows", "os_version": "11", "chrome_ver": "144",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (3840, 2160), "dpr": 2.0, "cores": 16, "ram": 32,
     "webgl_vendor": "Google Inc. (Intel)", "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 770 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "ethernet", "conn_down": 100, "conn_rtt": 50,
     "fonts": ["Arial", "Arial Black", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Impact", "Lucida Console", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 10 / Intel HD 4000 / 4GB / 2-core (old laptop) ──
    {"os": "Windows", "os_version": "10", "chrome_ver": "124",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1366, 768), "dpr": 1.0, "cores": 2, "ram": 4,
     "webgl_vendor": "Google Inc. (Intel)", "webgl_renderer": "ANGLE (Intel, Intel(R) HD Graphics 4000 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 8192, "color_depth": 24, "touch": 0, "battery_charging": False, "battery_level": 0.78,
     "conn_type": "wifi", "conn_down": 10, "conn_rtt": 200,
     "fonts": ["Arial", "Calibri", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 11 / NVIDIA GTX 1650 / 8GB / 4-core (budget gaming laptop) ──
    {"os": "Windows", "os_version": "11", "chrome_ver": "128",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1920, 1080), "dpr": 1.0, "cores": 4, "ram": 8,
     "webgl_vendor": "Google Inc. (NVIDIA)", "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 32768, "color_depth": 24, "touch": 0, "battery_charging": False, "battery_level": 0.89,
     "conn_type": "wifi", "conn_down": 50, "conn_rtt": 100,
     "fonts": ["Arial", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 10 / AMD Radeon Vega 8 / 8GB / 4-core (APU laptop) ──
    {"os": "Windows", "os_version": "10", "chrome_ver": "130",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1920, 1080), "dpr": 1.0, "cores": 4, "ram": 8,
     "webgl_vendor": "Google Inc. (AMD)", "webgl_renderer": "ANGLE (AMD, AMD Radeon(TM) Vega 8 Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": False, "battery_level": 0.55,
     "conn_type": "wifi", "conn_down": 25, "conn_rtt": 150,
     "fonts": ["Arial", "Calibri", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 11 / NVIDIA RTX 4070 / 32GB / 16-core ──
    {"os": "Windows", "os_version": "11", "chrome_ver": "146",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (2560, 1440), "dpr": 1.0, "cores": 16, "ram": 32,
     "webgl_vendor": "Google Inc. (NVIDIA)", "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 32768, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "ethernet", "conn_down": 100, "conn_rtt": 50,
     "fonts": ["Arial", "Arial Black", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 10 / Intel UHD 620 / 4GB / 2-core (budget laptop) ──
    {"os": "Windows", "os_version": "10", "chrome_ver": "132",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1366, 768), "dpr": 1.0, "cores": 2, "ram": 4,
     "webgl_vendor": "Google Inc. (Intel)", "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": False, "battery_level": 0.34,
     "conn_type": "wifi", "conn_down": 10, "conn_rtt": 200,
     "fonts": ["Arial", "Calibri", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 11 / AMD Radeon RX 6600 / 16GB / 8-core ──
    {"os": "Windows", "os_version": "11", "chrome_ver": "134",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1920, 1080), "dpr": 1.0, "cores": 8, "ram": 16,
     "webgl_vendor": "Google Inc. (AMD)", "webgl_renderer": "ANGLE (AMD, AMD Radeon RX 6600 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "ethernet", "conn_down": 100, "conn_rtt": 50,
     "fonts": ["Arial", "Calibri", "Consolas", "Courier New", "Georgia", "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 10 / Intel HD 520 / 8GB / 4-core (mid laptop) ──
    {"os": "Windows", "os_version": "10", "chrome_ver": "136",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1600, 900), "dpr": 1.0, "cores": 4, "ram": 8,
     "webgl_vendor": "Google Inc. (Intel)", "webgl_renderer": "ANGLE (Intel, Intel(R) HD Graphics 520 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": False, "battery_level": 0.92,
     "conn_type": "wifi", "conn_down": 50, "conn_rtt": 100,
     "fonts": ["Arial", "Calibri", "Cambria", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 11 / NVIDIA GTX 1080 / 16GB / 8-core ──
    {"os": "Windows", "os_version": "11", "chrome_ver": "140",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1920, 1080), "dpr": 1.0, "cores": 8, "ram": 16,
     "webgl_vendor": "Google Inc. (NVIDIA)", "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 32768, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "ethernet", "conn_down": 100, "conn_rtt": 50,
     "fonts": ["Arial", "Arial Black", "Calibri", "Consolas", "Courier New", "Georgia", "Impact", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 10 / AMD Radeon 530 / 4GB / 4-core (office laptop) ──
    {"os": "Windows", "os_version": "10", "chrome_ver": "144",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1366, 768), "dpr": 1.0, "cores": 4, "ram": 4,
     "webgl_vendor": "Google Inc. (AMD)", "webgl_renderer": "ANGLE (AMD, AMD Radeon 530 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": False, "battery_level": 0.23,
     "conn_type": "wifi", "conn_down": 10, "conn_rtt": 150,
     "fonts": ["Arial", "Calibri", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 11 / Intel Iris Xe Max / 16GB / 4-core (thin laptop) ──
    {"os": "Windows", "os_version": "11", "chrome_ver": "146",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (1920, 1200), "dpr": 1.5, "cores": 4, "ram": 16,
     "webgl_vendor": "Google Inc. (Intel)", "webgl_renderer": "ANGLE (Intel, Intel(R) Iris(R) Xe MAX Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 16384, "color_depth": 24, "touch": 0, "battery_charging": False, "battery_level": 0.72,
     "conn_type": "wifi", "conn_down": 50, "conn_rtt": 100,
     "fonts": ["Arial", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},

    # ── Windows 10 / NVIDIA RTX 3080 / 32GB / 16-core (high-end) ──
    {"os": "Windows", "os_version": "10", "chrome_ver": "126",
     "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
     "platform": "Win32", "screen": (3840, 2160), "dpr": 1.5, "cores": 16, "ram": 32,
     "webgl_vendor": "Google Inc. (NVIDIA)", "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)",
     "max_texture": 32768, "color_depth": 24, "touch": 0, "battery_charging": True, "battery_level": 1.0,
     "conn_type": "ethernet", "conn_down": 100, "conn_rtt": 50,
     "fonts": ["Arial", "Arial Black", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Impact", "Lucida Console", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"],
     "pdf_viewer": True, "do_not_track": None, "product_sub": "20030107"},
]

PLUGINS_WINDOWS = [
    {"name": "PDF Viewer",                "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}, {"type": "text/pdf"}]},
    {"name": "Chrome PDF Viewer",         "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
    {"name": "Chromium PDF Viewer",       "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
    {"name": "Microsoft Edge PDF Viewer", "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
    {"name": "WebKit built-in PDF",       "filename": "internal-pdf-viewer", "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
]


def generate_fingerprint(profile_name: str, vpn_city: str = "No VPN (Local)", timezone: str = None) -> dict:
    # Use profile name as seed — same name always gets same bundle
    seed = int(hashlib.md5(profile_name.encode()).hexdigest()[:8], 16)
    rng  = random.Random(seed)

    # Pick one coherent device bundle — no mixing across bundles
    bundle = rng.choice(DEVICE_BUNDLES)


    region    = _get_region_info(vpn_city)
    languages = region["languages"]
    flag      = region["flag"]

    # Timezone: use provided, or auto-lookup, or fallback
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

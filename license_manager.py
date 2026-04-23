"""
License Manager - Ninja Shield v4.2.0
Offline license validation with hardware binding.
Fixed: Removed volatile MAC address dependency. Replaced with permanent Windows MachineGuid.
"""

import hashlib
import hmac
import json
import os
import platform
import subprocess
from datetime import datetime, timedelta

# ─── SECRET — CHANGE THIS TO YOUR OWN RANDOM STRING ─────────────────────────
# This must be IDENTICAL in both license_manager.py and keygen.py
# Keep this secret — never share it
SECRET = "fbpm_9x#kL2@mQzR7!vNpW4&hYcT6^jUeA"
# ─────────────────────────────────────────────────────────────────────────────

LICENSE_FILE = os.path.join(os.path.expanduser("~"), ".fbpm_license")


def get_hardware_id() -> str:
    """Generate a unique Hardware ID using highly stable OS/Hardware anchors."""
    parts = []

    if platform.system() == "Windows":
        # 1. Windows MachineGuid (The most stable anchor, survives all network/VPN changes)
        try:
            import winreg
            registry = winreg.HKEY_LOCAL_MACHINE
            address = r"SOFTWARE\Microsoft\Cryptography"
            # Check both 64-bit and 32-bit registry views to be absolutely safe
            try:
                key = winreg.OpenKey(registry, address, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            except OSError:
                key = winreg.OpenKey(registry, address, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
            
            value, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            if value:
                parts.append(f"GUID:{value.strip()}")
        except Exception:
            pass

        # 2. Motherboard Serial Number (Physical hardware anchor)
        GARBAGE_VALUES = {
            "", "to be filled by o.e.m.", "default string", "none",
            "not applicable", "unknown", "system serial number",
            "chassis serial number", "to be filled by o.e.m",
            "00000000", "0000000000000000",
        }
        try:
            mb_result = subprocess.check_output(
                'powershell -NoProfile -Command "Get-CimInstance Win32_BaseBoard | Select-Object -First 1 -ExpandProperty SerialNumber"',
                shell=True, stderr=subprocess.DEVNULL
            ).decode(errors="ignore").strip()
            
            if mb_result and mb_result.lower() not in GARBAGE_VALUES and len(mb_result) >= 4:
                parts.append(f"MB:{mb_result}")
        except Exception:
            pass

    # Fallback if everything else fails (Fallback to hostname, NEVER network MAC)
    if not parts:
        parts.append(f"HOST:{platform.node()}")
        parts.append(f"USER:{os.environ.get('USERNAME', 'unknown')}")

    combined = "|".join(parts)
    return hashlib.sha256(combined.encode()).hexdigest()[:16].upper()


def _sign(data: str) -> str:
    """Create HMAC signature."""
    return hmac.new(
        SECRET.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()[:12].upper()


def validate_key_format(key: str) -> dict:
    """
    Validate key format and extract payload.
    Key format: FBPM-DDDD-PPPP-PPPP-SSSS
    """
    key = key.strip().upper().replace(" ", "")

    parts = key.split("-")
    if len(parts) != 5 or parts[0] != "FBPM":
        return {"valid": False, "error": "Invalid key format."}

    duration_code = parts[1]
    payload       = parts[2] + parts[3]
    signature     = parts[4]

    # Verify signature
    expected_sig = _sign(duration_code + payload)
    if not hmac.compare_digest(signature, expected_sig):
        return {"valid": False, "error": "Invalid or tampered key."}

    # Decode duration
    duration_map = {"1MO1": 30, "3MO3": 90}
    if duration_code not in duration_map:
        return {"valid": False, "error": "Unknown license duration."}
    duration_days = duration_map[duration_code]

    # Decode issue date from payload (base36)
    try:
        issue_ts  = int(payload, 36)
        issue_date = datetime.fromtimestamp(issue_ts)
    except Exception:
        return {"valid": False, "error": "Corrupted key payload."}

    return {
        "valid":         True,
        "duration_days": duration_days,
        "issue_date":    issue_date,
        "expiry_date":   issue_date + timedelta(days=duration_days),
    }


def activate_license(key: str) -> dict:
    """Activate a license key on this machine."""
    result = validate_key_format(key)
    if not result["valid"]:
        return {"success": False, "error": result["error"]}

    expiry = result["expiry_date"]
    if datetime.now() > expiry:
        return {"success": False, "error": "This key has already expired."}

    hw_id = get_hardware_id()

    license_data = {
        "duration_days": result["duration_days"],
        "expiry":        expiry.isoformat(),
        "activated_at":  datetime.now().isoformat(),
        "hw_id":         hw_id,
        "key":           key.strip().upper(),
    }

    record_str   = json.dumps(license_data, sort_keys=True)
    storage_hmac = _sign(record_str)
    license_data["_integrity"] = storage_hmac

    with open(LICENSE_FILE, "w") as f:
        json.dump(license_data, f, indent=2)

    return {
        "success":   True,
        "expiry":    expiry,
        "days_left": (expiry - datetime.now()).days,
    }


def check_license() -> dict:
    """Check if this machine has a valid active license."""
    if not os.path.exists(LICENSE_FILE):
        return {"status": "no_license", "error": "No license found."}

    try:
        with open(LICENSE_FILE) as f:
            data = json.load(f)
    except Exception:
        return {"status": "corrupt", "error": "License file is corrupted."}

    # Verify integrity
    stored_hmac = data.pop("_integrity", "")
    record_str  = json.dumps(data, sort_keys=True)
    expected    = _sign(record_str)
    data["_integrity"] = stored_hmac

    if not hmac.compare_digest(stored_hmac, expected):
        return {"status": "tampered", "error": "License file has been tampered with."}

    # Check Hardware ID
    hw_id = get_hardware_id()
    if data.get("hw_id") != hw_id:
        return {"status": "wrong_machine", "error": "This license belongs to a different machine."}

    # Check expiry
    try:
        expiry    = datetime.fromisoformat(data["expiry"])
        days_left = (expiry - datetime.now()).days
    except Exception:
        return {"status": "corrupt", "error": "License expiry data is corrupted."}

    if datetime.now() > expiry:
        return {
            "status":    "expired",
            "error":     f"Your license expired on {expiry.strftime('%B %d, %Y')}.",
            "expiry":    expiry,
            "days_left": 0,
        }

    return {
        "status":    "active",
        "expiry":    expiry,
        "days_left": days_left,
        "key":       data.get("key", ""),
    }
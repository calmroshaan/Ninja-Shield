"""
License Manager - Ninja Shield
Offline license validation with hardware binding.
Keys encode expiry duration and are bound to machine Hardware ID.
"""

import hashlib
import hmac
import json
import os
import platform
import struct
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ─── SECRET — CHANGE THIS TO YOUR OWN RANDOM STRING ─────────────────────────
# This must be IDENTICAL in both license_manager.py and keygen.py
# Keep this secret — never share it
SECRET = "fbpm_9x#kL2@mQzR7!vNpW4&hYcT6^jUeA"
# ─────────────────────────────────────────────────────────────────────────────

LICENSE_FILE = os.path.join(os.path.expanduser("~"), ".fbpm_license")


def get_hardware_id() -> str:
    """Generate a unique Hardware ID from this machine."""
    parts = []

    try:
        if platform.system() == "Windows":
            # CPU info
            result = subprocess.check_output(
                "wmic cpu get ProcessorId /value",
                shell=True, stderr=subprocess.DEVNULL
            ).decode(errors="ignore")
            for line in result.splitlines():
                if "ProcessorId=" in line:
                    parts.append(line.split("=")[1].strip())

            # Motherboard serial
            result = subprocess.check_output(
                "wmic baseboard get SerialNumber /value",
                shell=True, stderr=subprocess.DEVNULL
            ).decode(errors="ignore")
            for line in result.splitlines():
                if "SerialNumber=" in line:
                    parts.append(line.split("=")[1].strip())

            # Disk serial
            result = subprocess.check_output(
                "wmic diskdrive get SerialNumber /value",
                shell=True, stderr=subprocess.DEVNULL
            ).decode(errors="ignore")
            for line in result.splitlines():
                if "SerialNumber=" in line:
                    val = line.split("=")[1].strip()
                    if val:
                        parts.append(val)
                        break
    except Exception:
        pass

    # Fallback — always add machine node
    parts.append(str(hex(uuid_getnode())))

    combined = "|".join(p for p in parts if p)
    return hashlib.sha256(combined.encode()).hexdigest()[:16].upper()


def uuid_getnode():
    """Get MAC address as integer."""
    import uuid
    return uuid.getnode()


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
    D = duration code (1M or 3M encoded)
    P = payload (issue date)
    S = signature
    Returns dict with valid, duration_days, issue_date or error message.
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
    """
    Activate a license key on this machine.
    Saves binding to disk. Returns status dict.
    """
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
    """
    Check if this machine has a valid active license.
    Returns dict with status, days_left, expiry or error.
    """
    if not os.path.exists(LICENSE_FILE):
        return {"status": "no_license", "error": "No license found."}

    try:
        with open(LICENSE_FILE) as f:
            data = json.load(f)
    except Exception:
        return {"status": "corrupt", "error": "License file is corrupted."}

    # Verify integrity — prevent manual editing
    stored_hmac = data.pop("_integrity", "")
    record_str  = json.dumps(data, sort_keys=True)
    expected    = _sign(record_str)
    data["_integrity"] = stored_hmac

    if not hmac.compare_digest(stored_hmac, expected):
        return {"status": "tampered", "error": "License file has been tampered with."}

    # Check Hardware ID matches this machine
    hw_id = get_hardware_id()
    if data.get("hw_id") != hw_id:
        return {"status": "wrong_machine", "error": "This license is registered to a different machine."}

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
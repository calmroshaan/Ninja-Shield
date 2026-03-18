"""
Key Generator - FB Profile Manager
RUN THIS ONLY ON YOUR OWN PC. Never distribute this file.
"""

from datetime import datetime
import hashlib
import hmac

# ─── MUST MATCH SECRET IN license_manager.py EXACTLY ────────────────────────
SECRET = "fbpm_9x#kL2@mQzR7!vNpW4&hYcT6^jUeA"
# ─────────────────────────────────────────────────────────────────────────────

DURATION_MAP = {
    "1": ("1MO1", 30,  "1 Month"),
    "3": ("3MO3", 90,  "3 Months"),
}


def _sign(data: str) -> str:
    return hmac.new(
        SECRET.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()[:12].upper()


def generate_key(duration_choice: str) -> str:
    if duration_choice not in DURATION_MAP:
        raise ValueError("Invalid choice. Use '1' or '3'.")

    code, days, label = DURATION_MAP[duration_choice]

    # Encode current timestamp as base36
    now_ts  = int(datetime.now().timestamp())
    payload = ""
    n       = now_ts
    chars   = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    while n:
        payload = chars[n % 36] + payload
        n //= 36
    payload = payload.zfill(8)

    # Split payload into two 4-char groups
    p1  = payload[:4]
    p2  = payload[4:]
    sig = _sign(code + payload)

    key = f"FBPM-{code}-{p1}-{p2}-{sig}"
    return key


if __name__ == "__main__":
    print("\n╔══════════════════════════════════════╗")
    print("║   FB Profile Manager - Key Generator  ║")
    print("╚══════════════════════════════════════╝\n")
    print("Select license duration:")
    print("  [1] 1 Month")
    print("  [3] 3 Months")

    choice = input("\nEnter choice: ").strip()

    try:
        key = generate_key(choice)
        _, days, label = DURATION_MAP[choice]
        print(f"\n✓ Generated {label} License Key:")
        print(f"\n  {key}\n")
        print(f"  Send this key to your customer.")
        print(f"  It activates from the day they enter it.\n")
    except ValueError as e:
        print(f"\n[ERROR] {e}\n")
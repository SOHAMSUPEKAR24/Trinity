import hashlib
from datetime import datetime, timedelta, timezone
import os
import argparse
from dotenv import load_dotenv

# 🌍 Load environment variables from .env if available
load_dotenv()

# 🔐 Secret salt used for hashing
SECRET_SALT = os.getenv("LICENSE_SECRET", "trinity_default_salt")


def generate_license_token(user_id: str, days_valid: int = 30) -> str:
    """
    🎟️ Generate a license token using SHA-256(user_id:expiry_date:SECRET_SALT)
    """
    expiry_date = (datetime.now(timezone.utc) + timedelta(days=days_valid)).strftime("%Y-%m-%d")
    raw = f"{user_id}:{expiry_date}:{SECRET_SALT}"
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    license_token = f"{user_id}:{expiry_date}:{token_hash}"
    return license_token


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔐 Trinity License Token Generator")
    parser.add_argument("--user", type=str, required=True, help="User identifier (e.g., email, name, etc.)")
    parser.add_argument("--days", type=int, default=30, help="License validity in days (default: 30)")

    args = parser.parse_args()
    token = generate_license_token(args.user, args.days)

    print("\n✅ Generated License Token:\n")
    print(token)
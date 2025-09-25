# backend/utils/license_checker.py
import hashlib
import os
from datetime import datetime

SECRET_SALT = os.getenv("LICENSE_SECRET", "trinity_default_salt")

def is_license_valid(license_token: str) -> bool:
    """
    ✅ Basic license token verification logic.
    This assumes license tokens are SHA-256 hashes of user_id + expiry + secret salt.
    """
    try:
        # Format expected: user_id:expiry:hash
        parts = license_token.split(":")
        if len(parts) != 3:
            return False

        user_id, expiry_str, provided_hash = parts

        # ⏳ Check expiration
        expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
        if expiry < datetime.utcnow():
            return False

        # 🔐 Recompute hash and compare
        raw = f"{user_id}:{expiry_str}:{SECRET_SALT}"
        expected_hash = hashlib.sha256(raw.encode()).hexdigest()

        return expected_hash == provided_hash

    except Exception:
        return False
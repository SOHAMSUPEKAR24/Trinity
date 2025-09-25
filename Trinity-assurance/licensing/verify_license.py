# licensing/verify_license.py
import argparse
from backend.utils.license_checker import is_license_valid

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔒 License Token Verifier")
    parser.add_argument("--token", type=str, required=True, help="License token to verify")

    args = parser.parse_args()
    if is_license_valid(args.token):
        print("✅ License is valid.")
    else:
        print("❌ Invalid or expired license.")
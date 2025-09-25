# backend/routers/license.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.utils.license_checker import is_license_valid as verify_license_token

router = APIRouter()

class LicenseRequest(BaseModel):
    license_token: str

@router.post("/verify")  # ✅ Fix here
def verify_token(request: LicenseRequest):
    if not verify_license_token(request.license_token):
        raise HTTPException(status_code=401, detail="❌ Invalid or expired license token")
    return {"status": "✅ License valid"}
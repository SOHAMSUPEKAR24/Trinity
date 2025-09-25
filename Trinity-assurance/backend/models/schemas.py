from pydantic import BaseModel, Field, HttpUrl, constr
from typing import Optional, Literal
from enum import Enum

class Language(str, Enum):
    python = "python"
    java = "java"
    javascript = "javascript"
    typescript = "typescript"

class TestType(str, Enum):
    auto = "auto"
    unit = "unit"
    ui = "ui"

# 📥 Request model: AI Test Generation
class TestGenerationRequest(BaseModel):
    repo_url: HttpUrl = Field(..., description="GitHub repo URL to clone")  # Strict URL validation
    language: Language
    file_path: Optional[constr(pattern=r'^([a-zA-Z0-9_\-\/\.]*)$')] = Field(
        None, description="Optional single file path to generate test for"
    )
    folder_filter: Optional[constr(pattern=r'^([a-zA-Z0-9_\-\/\.]*)$')] = Field(
        None, description="Restrict generation to folder if provided"
    )
    dry_run: Optional[bool] = Field(default=False, description="If True, test code will not be saved")
    test_type: TestType = Field(default=TestType.auto)
    license_token: str = Field(..., description="License key/token to authenticate access")

# 📤 Response model: AI Test Generator Output
class TestGenerationResponse(BaseModel):
    status: Literal["success", "error"]
    generated_test_code: str

# 📥 Request model: Test Runner Trigger
class TestRunRequest(BaseModel):
    language: Language
    test_type: TestType = Field(default=TestType.auto)

# 📤 Response model: Test Runner Output
class TestRunResponse(BaseModel):
    status: Literal["success", "error"]
    output: str
    error: Optional[str] = None
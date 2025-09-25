from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import tests, history, download, license

app = FastAPI(title="Trinity Assurance")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later restrict to frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(tests.router, prefix="/tests", tags=["Test Generation"])
app.include_router(history.router, prefix="/history", tags=["Test History"])
app.include_router(download.router, prefix="/download", tags=["Download"])
app.include_router(license.router, prefix="/license", tags=["License"])

@app.get("/")
def root():
    return {"message": "Welcome to Trinity Assurance 🚀"}
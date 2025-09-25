## Middleware Integration Guide

- **Directory**: backend/middleware/
- **List**:
  - secret_scan.py: blocks API keys/passwords in requests
  - rate_limit.py: global per-IP and per-endpoint request limiting

- **main.py Integration**:  
  Add imports and app.add_middleware for each in the specific order:  
    CORS → RateLimiter → Secret Scanner → License Enforcement

- **Testing**:  
  - Requests with secrets → HTTP 400  
  - Bad input → HTTP 422  
  - Too many requests → HTTP 429

Ensure you have __init__.py in backend/middleware/!


✅ Generated License Token:

soham:2025-11-27:941e6762dbf68c72abeb959856236b31cb6f289e0075ce346751875f151bbdf8
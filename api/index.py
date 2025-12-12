from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from pydantic import BaseModel
import json
import string
import random
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use /tmp for serverless environment
DB_FILE = "/tmp/db.json"

def load_db():
    if os.path.exists(DB_FILE) and os.path.getsize(DB_FILE) > 0:
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

url_db = load_db()

class URLRequest(BaseModel):
    url: str

def generate_short_code(length=4):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        if code not in url_db:
            return code

# Serve the frontend
@app.get("/")
async def serve_frontend():
    html_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return JSONResponse({"status": "URL Shortener API", "total_urls": len(url_db)})

@app.post("/shorten")
async def shorten_url(request: Request):
    try:
        body = await request.json()
        long_url = body.get("url", "").strip()
        
        if not long_url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        if not long_url.startswith(('http://', 'https://')):
            long_url = 'https://' + long_url
        
        code = generate_short_code()
        url_db[code] = long_url
        save_db(url_db)
        
        # Get the base URL from request
        base_url = str(request.base_url).rstrip('/')
        short_url = f"{base_url}/{code}"
        
        return JSONResponse({
            "success": True,
            "short_url": short_url,
            "code": code,
            "original_url": long_url
        })
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/urls")
async def get_all_urls():
    current_db = load_db()
    return JSONResponse(current_db)

# Redirect route - must be last
@app.get("/{code}")
async def redirect_to_original(code: str):
    current_db = load_db()
    
    if code in current_db:
        return RedirectResponse(url=current_db[code], status_code=307)
    
    return JSONResponse(
        {"error": "Short URL not found", "code": code},
        status_code=404
    )
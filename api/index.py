from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from pydantic import BaseModel
import json
import string
import random
import os

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins (frontend on Vercel)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DATABASE FILE ----------
DB_FILE = os.path.join(os.path.dirname(__file__), "db.json")

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

class URLRequest(BaseModel):
    url: str


# ---------- HEALTH CHECK (MUST BE ABOVE /{code}) ----------
@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------- SHORTEN URL ----------
@app.post("/shorten")
async def shorten_url(request: Request):
    body = await request.json()
    long_url = body.get("url", "").strip()

    if not long_url:
        raise HTTPException(status_code=400, detail="URL is required")

    if not long_url.startswith(("http://", "https://")):
        long_url = "https://" + long_url

    db = load_db()

    # generate short code
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(5))
        if code not in db:
            break

    db[code] = long_url
    save_db(db)

    base = str(request.base_url).rstrip("/")
    short_url = f"{base}/{code}"

    return {"short_url": short_url, "code": code, "original": long_url}


# ---------- LIST ALL ----------
@app.get("/api/urls")
async def get_all():
    return load_db()


# ---------- REDIRECT SHORT URL (KEEP LAST!) ----------
@app.get("/{code}")
async def redirect(code: str):
    db = load_db()
    if code in db:
        return RedirectResponse(db[code])
    return {"error": "Short URL not found", "code": code}


# ---------- LOCAL DEVELOPMENT ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)

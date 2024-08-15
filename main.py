from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import URL, SessionLocal
import string, random
import os

app = FastAPI()

class URLRequest(BaseModel):
    long_url: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/shorten")
def shorten_url(url_request: URLRequest, db: Session = Depends(get_db)):
    short_code = generate_short_code()
    db_url = URL(long_url=url_request.long_url, short_code=short_code)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return {"short_url": f"http://127.0.0.1:8000/{short_code}"}

@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    db_url = db.query(URL).filter(URL.short_code == short_code).first()
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(db_url.long_url)

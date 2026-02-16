import os
import uvicorn
import json
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from bot_logic import get_bot_application
from database import init_db, get_page
from themes import VIBES

# Init
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set")

bot_app = get_bot_application(TOKEN)
templates = Jinja2Templates(directory="templates")

# Lifecycle to run Bot alongside FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Start Bot Polling
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling(allowed_updates=["message", "callback_query"])
    yield
    # Stop Bot
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def landing():
    return HTMLResponse("<h1>Birthday Builder Bot is Running ✅</h1><p>Send /start to the Telegram Bot to begin.</p>")

@app.get("/p/{slug}", response_class=HTMLResponse)
async def view_page(request: Request, slug: str):
    data = get_page(slug)
    if not data:
        raise HTTPException(status_code=404, detail="Page not found")
    
    theme = VIBES.get(data['theme_key'], VIBES['female_friend'])
    photo_ids = json.loads(data['photo_ids'])
    
    # Process text logic
    name = data['name']
    intro_header = f"Happy Birthday {name}"
    
    if data['age_text']:
        final_slide_title = f"Happy {data['age_text']} Birthday"
    else:
        final_slide_title = f"Happy Birthday {name}"

    return templates.TemplateResponse("birthday.html", {
        "request": request,
        "name": name,
        "dob_text": data['dob_text'],
        "colors": theme,
        "slides": theme['slides'],
        "photo_ids": photo_ids,
        "audio_id": data['audio_id'],
        "intro_header": intro_header,
        "final_slide_title": final_slide_title
    })

@app.get("/media/{file_id}")
async def proxy_media(file_id: str):
    """
    Proxies media from Telegram servers to the browser.
    This hides the Telegram URL signature and allows ephemeral handling.
    """
    try:
        # 1. Get File Path from Telegram API
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}")
            result = resp.json()
            if not result.get("ok"):
                raise HTTPException(status_code=404, detail="File info not found")
            
            file_path = result['result']['file_path']
            download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
            
            # 2. Stream the file content
            # Note: For heavy production, redirect to a cached CDN. For this scale, proxy is fine.
            req = client.build_request("GET", download_url)
            r = await client.send(req, stream=True)
            
            return StreamingResponse(
                r.aiter_bytes(), 
                media_type=r.headers.get("content-type")
            )
            
    except Exception as e:
        print(f"Media Error: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch media")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

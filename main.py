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

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set")

bot_app = get_bot_application(TOKEN)
templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Drop pending updates to clean state on restart
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.bot.delete_webhook(drop_pending_updates=True)
    await bot_app.updater.start_polling(allowed_updates=["message"])
    yield
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def landing():
    return HTMLResponse("<h1>Bot is Running ✅</h1><p>Send /start to Telegram.</p>")

@app.get("/p/{slug}", response_class=HTMLResponse)
async def view_page(request: Request, slug: str):
    data = get_page(slug)
    if not data:
        raise HTTPException(status_code=404, detail="Page not found")
    
    theme = VIBES.get(data['theme_key'], VIBES['female_friend'])
    try:
        photo_ids = json.loads(data['photo_ids'])
    except:
        photo_ids = []
    
    name = data['name']
    intro_header = f"Happy Birthday {name}"
    
    # LOGIC: Use Custom Text if it exists, otherwise default to age/name
    if data.get('custom_text'):
        final_slide_title = data['custom_text']
    elif data.get('age_text'):
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
    FIXED: Uses a generator to keep the connection open while streaming.
    This prevents the 'Internal Server Error' (500).
    """
    # 1. Get File Path
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}")
        result = resp.json()
    
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail="File info not found")
    
    file_path = result['result']['file_path']
    download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    
    # 2. Generator to stream content securely
    async def media_generator():
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", download_url) as r:
                async for chunk in r.aiter_bytes():
                    yield chunk

    return StreamingResponse(media_generator())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

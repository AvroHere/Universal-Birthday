# 🎂 Universal Birthday Bot

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A powerful, **Admin-Only Telegram Bot** that creates personalized, cinematic "birthday story" websites in seconds. 

Built with **FastAPI** and **Python-Telegram-Bot**, this project is designed for **ephemeral hosting** (like Render Free Tier) with **zero local storage requirements**—media is streamed directly from Telegram.

---

## ✨ Key Features

* 🔐 **Admin Secured:** The bot ignores everyone except YOU (the admin).
* 🎨 **Vibe System:** Select themes like *Male Friend*, *Female Friend*, or *Student* to automatically tune color palettes and copy.
* 📸 **Photo Slideshow:** Upload 10 photos via chat to create a moving background slideshow.
* 🎵 **Background Audio:** Attach any song (MP3) to play automatically on the site.
* ⚡ **Zero Storage:** No AWS S3 required. Media is proxied securely from Telegram servers.
* 📱 **Mobile First:** The generated site features scroll animations, floating hearts, and glassmorphism UI.

---

## 📂 Repository Structure

```text
Universal-Birthday/
├── main.py            # FastAPI app & Media Proxy
├── bot_logic.py       # Telegram Bot conversation engine
├── database.py        # SQLite (Metadata storage)
├── themes.py          # Theme presets (Colors & Text)
├── templates/         # HTML/Jinja2 templates
│   └── birthday.html  # The frontend design
├── requirements.txt   # Dependencies
└── README.md          # Documentation
```

# 🚀 How to Deploy on Render

This guide explains how to deploy the **Universal Birthday Bot** to [Render.com](https://render.com) for free.

## Prerequisites

1.  A [GitHub account](https://github.com/) with this repository forked or uploaded.
2.  A [Render account](https://render.com/).
3.  A Telegram Bot Token (from [@BotFather](https://t.me/BotFather)).
4.  Your Telegram User ID (from [@userinfobot](https://t.me/userinfobot)).

---

## Step 1: Create a New Web Service

1.  Log in to your **Render Dashboard**.
2.  Click **New +** and select **Web Service**.
3.  Connect your GitHub account and select your repository (`Universal-Birthday`).
4.  Give your service a name (e.g., `my-birthday-bot`).

## Step 2: Configure the Environment

Scroll down to the settings section and configure the following:

* **Region:** Choose the one closest to you (e.g., Singapore, Frankfurt).
* **Branch:** `main` (or `master`).
* **Runtime:** `Python 3`.
* **Build Command:**
    ```bash
    pip install -r requirements.txt
    ```
* **Start Command:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port $PORT
    ```
* **Instance Type:** Select **Free**.

## Step 3: Add Environment Variables

Scroll down to the **Environment Variables** section and add the following keys:

| Key | Value | Description |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | `123456:ABC-DEF...` | Your bot token from BotFather. |
| `ADMIN_UID` | `123456789` | Your personal numeric Telegram ID. |
| `RENDER_URL` | `https://your-app.onrender.com` | The URL Render assigns to you (found at the top left after creation). |
| `PYTHON_VERSION` | `3.9.0` | (Optional) Ensures compatibility. |

> **Note:** For `RENDER_URL`, you can enter `http://localhost:8000` initially, then come back and update it once Render generates your actual URL (e.g., `https://my-birthday-bot-x8z.onrender.com`).

## Step 4: Deploy

1.  Click **Create Web Service**.
2.  Render will start building your app. This takes about 1-2 minutes.
3.  Watch the logs. Once you see `Application startup complete`, your bot is live!

---

## ⚡ Important: Keep Your Bot Awake

Render's free tier "spins down" (goes to sleep) after 15 minutes of inactivity. To prevent this:

1.  Copy your new website URL (e.g., `https://my-birthday-bot.onrender.com`).
2.  Create a free account on [UptimeRobot](https://uptimerobot.com/).
3.  Add a **New Monitor**:
    * **Monitor Type:** HTTP(s)
    * **Friendly Name:** My Bot
    * **URL:** `https://my-birthday-bot.onrender.com/`
    * **Monitoring Interval:** 5 minutes
4.  This will ping your site periodically, keeping the bot active and ready to respond.

---

## 🛑 Troubleshooting

* **Bot not replying?** Check the **Logs** tab in Render. If you see errors about "Token Invalid," double-check your `TELEGRAM_BOT_TOKEN`.
* **Database Reset?** Remember that on the Free Tier, the SQLite database is deleted every time the server restarts. Generated links are temporary.

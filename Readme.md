# 🎂 Telegram Birthday Website Bot

An **Admin-Only Telegram Bot** that generates personalized, scrolling "birthday story" websites on the fly. Built with **FastAPI** and **Python-Telegram-Bot**, designed to be hosted on **Render** (Free Tier).

## ✨ Features

* **Admin Controlled:** The bot only responds to *your* Telegram ID.
* **Interactive Builder:** Collects name, age, photos, and music via Telegram chat.
* **Vibe System:** Choose themes like "Male Friend," "Female Friend," or "Student" to automatically adjust color palettes and text styles.
* **Zero Storage:** Uses Telegram's servers to host media. The web server proxies images/audio in real-time (perfect for ephemeral hosting like Render).
* **Responsive Design:** Generated sites feature a fixed photo layer, scrolling story sections, floating hearts, and background music.

## 📂 Project Structure

birthday_bot/
├── main.py            # FastAPI entry point & media proxy
├── bot_logic.py       # Telegram conversation handler
├── database.py        # SQLite handler (Ephemeral metadata)
├── themes.py          # "Vibe" configuration (Colors/Text)
├── requirements.txt   # Python dependencies
└── templates/
    └── birthday.html  # Jinja2 template (The website design)

## 🚀 Local Setup

1.  **Clone the repository**
    git clone https://github.com/yourusername/birthday-bot.git
    cd birthday-bot

2.  **Create a virtual environment**
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3.  **Install dependencies**
    pip install -r requirements.txt

4.  **Set Environment Variables**
    Create a .env file (or set them in your terminal):
    export TELEGRAM_BOT_TOKEN="your_bot_token_here"
    export ADMIN_UID="1234556769"  # Your Telegram User ID
    export RENDER_URL="http://localhost:8000"

5.  **Run the App**
    uvicorn main:app --reload

    * Open your browser to http://localhost:8000.
    * Open Telegram and message your bot /start.

## ☁️ Deployment (Render.com)

This project is optimized for **Render Web Services**.

1.  **Create a New Web Service** on Render connected to this repo.
2.  **Settings:**
    * **Runtime:** Python 3
    * **Build Command:** pip install -r requirements.txt
    * **Start Command:** uvicorn main:app --host 0.0.0.0 --port $PORT
3.  **Environment Variables:**
    Add the following in the Render Dashboard:
    * TELEGRAM_BOT_TOKEN: Your Bot Token from @BotFather.
    * ADMIN_UID: Your numeric Telegram ID (use @userinfobot to find it).
    * RENDER_URL: Your Render app URL (e.g., https://my-bot.onrender.com).
4.  **Keep it Awake:**
    * Render Free Tier spins down after 15 minutes of inactivity.
    * Use a service like **UptimeRobot** to ping https://your-app-name.onrender.com/ every 5 minutes.

## 🤖 Usage

1.  **Start the Bot:** Send /start to your bot.
2.  **Select Category:** Choose the relationship type (e.g., "Female Friend") to set the text/color theme.
3.  **Enter Details:** Provide Name and Date of Birth (DD/MM/YYYY).
4.  **Upload Media:**
    * Send **10 Photos** (you can select them all at once in your gallery).
    * Send **1 Audio File** (MP3) for background music.
5.  **Get Link:** The bot will generate a unique link (e.g., /p/x8s7df9).
6.  **Share:** Send the link to the birthday person!

## ⚠️ Important Limitations

* **Ephemeral Data:** This project uses a local SQLite database. On Render Free Tier, **the database is wiped every time the server restarts** (updates or inactivity). This means generated links are temporary (usually good for ~24 hours or as long as the server stays awake).
* **Media Hosting:** Images are proxied from Telegram. If you delete the messages in the chat, the website images will break.

## 🛠 Tech Stack

* **Backend:** FastAPI
* **Bot Framework:** Python-Telegram-Bot
* **Templating:** Jinja2
* **Frontend:** HTML5, CSS3 (Glassmorphism), Vanilla JS

## 📄 License

MIT License. Free to use and modify.

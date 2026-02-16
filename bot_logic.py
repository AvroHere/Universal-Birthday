import os
import random
import string
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ConversationHandler, ContextTypes, filters
)
from database import save_page
from themes import VIBES

# --- CONFIG ---
ADMIN_ID = int(os.getenv("ADMIN_UID", "1234556769"))
RENDER_URL = os.getenv("RENDER_URL", "http://localhost:8000") # Set this in Render Env Vars

# --- STATES ---
CATEGORY, GENDER, NAME, DATE, PHOTOS, MUSIC = range(6)

# --- UTILS ---
def generate_slug():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def get_ordinal(n):
    if 11 <= (n % 100) <= 13: suffix = 'th'
    else: suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("Sorry, this bot is private.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Male Friend 🎉", callback_data='cat_male')],
        [InlineKeyboardButton("Female Friend 💖", callback_data='cat_female')],
        [InlineKeyboardButton("University Junior 🎓", callback_data='cat_junior')],
        [InlineKeyboardButton("Student 🧑‍🎓", callback_data='cat_student')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"👋 Hello Admin! Let's build a birthday site.\n\nChoose a category:", reply_markup=reply_markup)
    return CATEGORY

async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['category'] = query.data
    
    # Even if category implies gender, we ask to confirm vibe
    keyboard = [
        [InlineKeyboardButton("Male ♂️", callback_data='male')],
        [InlineKeyboardButton("Female ♀️", callback_data='female')]
    ]
    await query.edit_message_text("Recipient Gender? (This tunes the colors/text)", reply_markup=InlineKeyboardMarkup(keyboard))
    return GENDER

async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['gender'] = query.data
    await query.edit_message_text(f"Got it. Now, what is the **Recipient's Name**?")
    return NAME

async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("Great! Enter **Birth Date**.\nFormat: `DD/MM` or `DD/MM/YYYY`\n(e.g., 15/02 or 15/02/2005)")
    return DATE

async def date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    dob_text = ""
    age_text = ""
    
    try:
        # Check DD/MM/YYYY
        date_obj = datetime.strptime(text, "%d/%m/%Y")
        dob_text = date_obj.strftime("%B %d, %Y")
        
        # Calculate Age
        today = datetime.today()
        age = today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))
        age_text = f"{get_ordinal(age)}" 
        
    except ValueError:
        try:
            # Check DD/MM
            date_obj = datetime.strptime(text, "%d/%m")
            dob_text = date_obj.strftime("%B %d")
            age_text = "" # No age known
        except ValueError:
            await update.message.reply_text("❌ Invalid format. Please use DD/MM or DD/MM/YYYY.")
            return DATE

    context.user_data['dob_text'] = dob_text
    context.user_data['age_text'] = age_text
    
    # Init photo list
    context.user_data['photos'] = []
    
    await update.message.reply_text(
        "📅 Date saved.\n\n"
        "📸 **Now send up to 10 photos.**\n"
        "You can send them as a batch. \n"
        "Type /done when you have sent enough."
    )
    return PHOTOS

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Telegram sends highest res as last item in list
    photo_file = update.message.photo[-1].file_id
    context.user_data['photos'].append(photo_file)
    
    count = len(context.user_data['photos'])
    if count == 10:
        await update.message.reply_text("✅ 10 Photos received. Now send 1 **Song/Audio** file.")
        return MUSIC
    
    return PHOTOS

async def done_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('photos'):
        await update.message.reply_text("Please send at least one photo!")
        return PHOTOS
    await update.message.reply_text(f"✅ {len(context.user_data['photos'])} photos saved. Now send 1 **Song/Audio** file.")
    return MUSIC

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio = update.message.audio or update.message.document
    if not audio:
        await update.message.reply_text("Please send a valid audio file.")
        return MUSIC
        
    context.user_data['audio'] = audio.file_id
    
    # --- GENERATION LOGIC ---
    await update.message.reply_text("⏳ Generating website...")
    
    slug = generate_slug()
    ud = context.user_data
    
    # Determine Theme Key
    cat_map = {
        'cat_male': 'male_friend',
        'cat_female': 'female_friend',
        'cat_junior': 'university_junior',
        'cat_student': 'student'
    }
    
    # Basic logic to switch preset based on selection
    base_theme = cat_map.get(ud['category'], 'female_friend')
    # If explicit gender contradicts category default (rare case), we stick to category for text, 
    # but could swap colors. For simplicity, we stick to the category map.
    
    # Fill photos to 10 if needed
    photos = ud['photos']
    while len(photos) < 10:
        photos.extend(photos[:10-len(photos)]) # Repeat photos to fill
    
    save_page(
        slug=slug,
        name=ud['name'],
        dob_text=ud['dob_text'],
        age_text=ud['age_text'],
        theme_key=base_theme,
        photo_ids=photos[:10],
        audio_id=ud['audio']
    )
    
    link = f"{RENDER_URL}/p/{slug}"
    await update.message.reply_text(f"🎉 **Done!**\n\nHere is the link:\n{link}\n\n(Send /start to create another)")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action cancelled.")
    return ConversationHandler.END

# Setup Bot
def get_bot_application(token):
    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CATEGORY: [CallbackQueryHandler(category_handler)],
            GENDER: [CallbackQueryHandler(gender_handler)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_handler)],
            PHOTOS: [
                MessageHandler(filters.PHOTO, photo_handler),
                CommandHandler('done', done_photos)
            ],
            MUSIC: [MessageHandler(filters.AUDIO | filters.Document.AUDIO, music_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    return application

import os
import random
import string
from datetime import datetime
from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    ConversationHandler, ContextTypes, filters
)
from database import save_page

# --- CONFIG ---
ADMIN_ID = int(os.getenv("ADMIN_UID", "0")) # Ensure this matches your ID
RENDER_URL = os.getenv("RENDER_URL", "http://localhost:8000")

# --- STATES ---
CATEGORY, GENDER, NAME, DATE, PHOTOS, MUSIC, CUSTOM_TEXT = range(7)

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

    # KEYBOARD: Menu Style
    keyboard = [
        ["Male Friend 🎉", "Female Friend 💖"],
        ["University Junior 🎓", "Student 🧑‍🎓"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"👋 Hello Admin! Let's build a birthday site.\n\nChoose a category:", 
        reply_markup=markup
    )
    return CATEGORY

async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Map button text to internal keys
    if "Male Friend" in text: context.user_data['category'] = 'cat_male'
    elif "Female Friend" in text: context.user_data['category'] = 'cat_female'
    elif "Junior" in text: context.user_data['category'] = 'cat_junior'
    elif "Student" in text: context.user_data['category'] = 'cat_student'
    else:
        await update.message.reply_text("⚠️ Please select an option from the menu.")
        return CATEGORY
    
    # Next Keyboard
    keyboard = [["Male ♂️", "Female ♀️"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text("Recipient Gender?", reply_markup=markup)
    return GENDER

async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Male" in text: context.user_data['gender'] = 'male'
    elif "Female" in text: context.user_data['gender'] = 'female'
    else:
        await update.message.reply_text("Please select Male or Female using the buttons.")
        return GENDER

    # Remove keyboard for text input
    await update.message.reply_text(
        "Got it. What is the **Recipient's Name**?",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("Great! Enter **Birth Date** (DD/MM/YYYY).")
    return DATE

async def date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        # Try full date first
        date_obj = datetime.strptime(text, "%d/%m/%Y")
        dob_text = date_obj.strftime("%B %d, %Y")
        
        today = datetime.today()
        age = today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))
        age_text = f"{get_ordinal(age)}"
    except ValueError:
        try:
            # Try day/month only
            date_obj = datetime.strptime(text, "%d/%m")
            dob_text = date_obj.strftime("%B %d")
            age_text = ""
        except ValueError:
            await update.message.reply_text("❌ Invalid format. Use DD/MM/YYYY (e.g. 12/05/2000)")
            return DATE

    context.user_data['dob_text'] = dob_text
    context.user_data['age_text'] = age_text
    context.user_data['photos'] = []
    
    await update.message.reply_text("📅 Date saved.\n\n📸 **Send 10 photos.**\n(Type /done if you have fewer, but 10 is best)")
    return PHOTOS

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = update.message.photo[-1].file_id
    context.user_data['photos'].append(photo_file)
    
    if len(context.user_data['photos']) >= 10:
        await update.message.reply_text("✅ 10 Photos saved.\n\n🎵 Now send an **Audio/Song** file.")
        return MUSIC
    return PHOTOS

async def done_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('photos'):
        await update.message.reply_text("Send at least one photo!")
        return PHOTOS
    await update.message.reply_text(f"✅ Photos saved.\n\n🎵 Now send an **Audio/Song** file.")
    return MUSIC

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio = update.message.audio or update.message.document
    if not audio:
        await update.message.reply_text("Please send a valid audio file.")
        return MUSIC
        
    context.user_data['audio'] = audio.file_id
    
    # NEW STEP: Ask for custom text
    await update.message.reply_text(
        "📝 **Almost done!**\n\n"
        "Enter the **Custom Text** for the final slide:\n"
        "(e.g., 'Happy Birthday Bestie!', 'Love you forever', etc.)"
    )
    return CUSTOM_TEXT

async def custom_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    custom_text = update.message.text.strip()
    
    await update.message.reply_text("⏳ Generating website...")
    
    slug = generate_slug()
    ud = context.user_data
    
    cat_map = {
        'cat_male': 'male_friend',
        'cat_female': 'female_friend',
        'cat_junior': 'university_junior',
        'cat_student': 'student'
    }
    base_theme = cat_map.get(ud.get('category'), 'female_friend')
    
    # Fill photos if < 10
    photos = ud['photos']
    if photos:
        while len(photos) < 10:
            photos.extend(photos[:10-len(photos)])
            
    save_page(
        slug=slug,
        name=ud['name'],
        dob_text=ud['dob_text'],
        age_text=ud['age_text'],
        theme_key=base_theme,
        photo_ids=photos[:10],
        audio_id=ud['audio'],
        custom_text=custom_text  # Save the new text
    )
    
    link = f"{RENDER_URL}/p/{slug}"
    await update.message.reply_text(f"🎉 **Done!**\n\nLink:\n{link}\n\n(Send /start to create another)")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def get_bot_application(token):
    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            # Use filters.TEXT instead of CallbackQueryHandler
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_handler)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_handler)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_handler)],
            PHOTOS: [
                MessageHandler(filters.PHOTO, photo_handler),
                CommandHandler('done', done_photos)
            ],
            MUSIC: [MessageHandler(filters.AUDIO | filters.Document.AUDIO, music_handler)],
            CUSTOM_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_text_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    return application

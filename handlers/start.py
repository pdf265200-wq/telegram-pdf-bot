from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import os

from config import Config
from database.db_manager import db
from keyboards.main_menu import get_main_menu
from locales import ar, en

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    args = context.args
    
    # Check for referral
    if args:
        referrer_code = args[0]
        await process_referral(user.id, referrer_code)
    
    # Get or create user
    db_user = await db.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Get user language
    lang = db_user.language if db_user else 'ar'
    messages = ar if lang == 'ar' else en
    
    # Check premium status
    is_premium = await db.check_premium_status(user.id)
    
    welcome_text = messages.WELCOME_MESSAGE.format(
        first_name=user.first_name,
        plan="Premium" if is_premium else "Free"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu(lang, is_premium),
        parse_mode=ParseMode.HTML
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    messages = ar if lang == 'ar' else en
    
    await update.message.reply_text(
        messages.HELP_MESSAGE,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu"""
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    is_premium = await db.check_premium_status(user.id)
    
    await update.message.reply_text(
        "📋 القائمة الرئيسية" if lang == 'ar' else "📋 Main Menu",
        reply_markup=get_main_menu(lang, is_premium)
    )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change user language"""
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
        ]
    ]
    
    await update.message.reply_text(
        "اختر اللغة / Choose language:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    text = update.message.text
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    messages = ar if lang == 'ar' else en
    
    # Check if user is in a conversation state
    if context.user_data.get('awaiting_password'):
        await handle_password_input(update, context)
    elif context.user_data.get('awaiting_watermark_text'):
        await handle_watermark_input(update, context)
    elif context.user_data.get('awaiting_page_numbers'):
        await handle_page_numbers_input(update, context)
    else:
        await update.message.reply_text(
            messages.USE_MENU_MESSAGE,
            reply_markup=get_main_menu(lang, await db.check_premium_status(user.id))
        )

async def process_referral(user_id: int, referral_code: str):
    """Process referral if valid"""
    async with db.async_session() as session:
        from database.models import User
        from sqlalchemy import select
        
        # Find referrer
        result = await session.execute(
            select(User).where(User.referral_code == referral_code)
        )
        referrer = result.scalar_one_or_none()
        
        if referrer and referrer.telegram_id != user_id:
            await db.add_referral(referrer.telegram_id, user_id)

async def handle_password_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle password input for PDF protection"""
    password = update.message.text
    context.user_data['password'] = password
    context.user_data['awaiting_password'] = False
    
    await update.message.reply_text("✅ تم استلام كلمة المرور" if context.user_data.get('lang') == 'ar' else "✅ Password received")

async def handle_watermark_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle watermark text input"""
    text = update.message.text
    context.user_data['watermark_text'] = text
    context.user_data['awaiting_watermark_text'] = False
    
    await update.message.reply_text("✅ تم استلام نص العلامة المائية" if context.user_data.get('lang') == 'ar' else "✅ Watermark text received")

async def handle_page_numbers_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle page numbers input"""
    text = update.message.text
    context.user_data['page_numbers'] = text
    context.user_data['awaiting_page_numbers'] = False
    
    await update.message.reply_text("✅ تم استلام أرقام الصفحات" if context.user_data.get('lang') == 'ar' else "✅ Page numbers received")

# Handler instance
start_handler = type('obj', (object,), {
    'start': start,
    'help': help,
    'menu': menu,
    'change_language': change_language,
    'handle_text': handle_text
})

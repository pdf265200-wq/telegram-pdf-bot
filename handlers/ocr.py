from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import os

from config import Config
from database.db_manager import db
from services.ocr_service import ocr_service
from utils.helpers import download_file, send_file, generate_temp_filename
from utils.validators import validate_file_size
from locales import ar, en

async def handle_ocr_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show OCR menu"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    # Check premium for OCR
    if not await db.check_premium_status(user.id):
        if lang == 'ar':
            await query.edit_message_text("⭐ OCR ميزة بريميوم. قم بالترقية للمتابعة!")
        else:
            await query.edit_message_text("⭐ OCR is a premium feature. Upgrade to continue!")
        return
    
    if lang == 'ar':
        keyboard = [
            [InlineKeyboardButton("📸 OCR من صورة", callback_data="ocr_image")],
            [InlineKeyboardButton("📄 OCR من PDF", callback_data="ocr_pdf")],
            [InlineKeyboardButton("🇸🇦 OCR عربي", callback_data="ocr_arabic")],
            [InlineKeyboardButton("🇺🇸 OCR إنجليزي", callback_data="ocr_english")],
            [InlineKeyboardButton("🔍 PDF قابل للبحث", callback_data="ocr_searchable")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📸 OCR from Image", callback_data="ocr_image")],
            [InlineKeyboardButton("📄 OCR from PDF", callback_data="ocr_pdf")],
            [InlineKeyboardButton("🇸🇦 Arabic OCR", callback_data="ocr_arabic")],
            [InlineKeyboardButton("🇺🇸 English OCR", callback_data="ocr_english")],
            [InlineKeyboardButton("🔍 Searchable PDF", callback_data="ocr_searchable")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
    
    await query.edit_message_text(
        "🔍 OCR - استخراج النصوص" if lang == 'ar' else "🔍 OCR - Text Extraction",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_ocr_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle OCR from image"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = 'ocr_image'
    context.user_data['ocr_lang'] = Config.OCR_LANGUAGES
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    messages = ar if lang == 'ar' else en
    
    await query.edit_message_text("📸 أرسل الصورة لاستخراج النص" if lang == 'ar' else "📸 Send image to extract text")

async def handle_ocr_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle OCR from PDF"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = 'ocr_pdf'
    context.user_data['ocr_lang'] = Config.OCR_LANGUAGES
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    messages = ar if lang == 'ar' else en
    
    await query.edit_message_text("📄 أرسل ملف PDF لاستخراج النص" if lang == 'ar' else "📄 Send PDF to extract text")

async def handle_ocr_arabic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Arabic OCR"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = 'ocr_image'
    context.user_data['ocr_lang'] = ['ara']
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    await query.edit_message_text("🇸🇦 أرسل صورة تحتوي على نص عربي" if lang == 'ar' else "🇸🇦 Send image with Arabic text")

async def handle_ocr_english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle English OCR"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = 'ocr_image'
    context.user_data['ocr_lang'] = ['eng']
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    await query.edit_message_text("🇺🇸 أرسل صورة تحتوي على نص إنجليزي" if lang == 'ar' else "🇺🇸 Send image with English text")

# Handler instance
ocr_handler = type('obj', (object,), {
    'handle_ocr_menu': handle_ocr_menu,
    'handle_ocr_image': handle_ocr_image,
    'handle_ocr_pdf': handle_ocr_pdf,
    'handle_ocr_arabic': handle_ocr_arabic,
    'handle_ocr_english': handle_ocr_english
})

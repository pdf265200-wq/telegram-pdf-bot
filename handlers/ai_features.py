from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import os

from config import Config
from database.db_manager import db
from services.ai_service import ai_service
from services.pdf_service import pdf_service
from utils.helpers import download_file
from utils.validators import validate_file_size

async def handle_ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show AI features menu"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    # Check premium for AI
    if not await db.check_premium_status(user.id):
        if lang == 'ar':
            await query.edit_message_text("🤖 ميزات AI للبريميوم فقط. قم بالترقية!")
        else:
            await query.edit_message_text("🤖 AI features are premium only. Upgrade now!")
        return
    
    if lang == 'ar':
        keyboard = [
            [InlineKeyboardButton("📝 تلخيص PDF", callback_data="ai_summarize")],
            [InlineKeyboardButton("🌐 ترجمة المستند", callback_data="ai_translate")],
            [InlineKeyboardButton("✍️ إعادة كتابة", callback_data="ai_rewrite")],
            [InlineKeyboardButton("📤 استخراج النص", callback_data="ai_extract")],
            [InlineKeyboardButton("❓ اسأل عن المستند", callback_data="ai_qa")],
            [InlineKeyboardButton("📊 تحليل المستند", callback_data="ai_analyze")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📝 Summarize PDF", callback_data="ai_summarize")],
            [InlineKeyboardButton("🌐 Translate Document", callback_data="ai_translate")],
            [InlineKeyboardButton("✍️ Rewrite", callback_data="ai_rewrite")],
            [InlineKeyboardButton("📤 Extract Text", callback_data="ai_extract")],
            [InlineKeyboardButton("❓ Ask About Document", callback_data="ai_qa")],
            [InlineKeyboardButton("📊 Analyze Document", callback_data="ai_analyze")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
    
    await query.edit_message_text(
        "🤖 ميزات الذكاء الاصطناعي" if lang == 'ar' else "🤖 AI Features",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PDF summarization"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = 'ai_summarize'
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    await query.edit_message_text(
        "📝 أرسل ملف PDF لتلخيصه" if lang == 'ar' else "📝 Send PDF file to summarize"
    )

async def handle_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document translation"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = 'ai_translate'
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    await query.edit_message_text(
        "🌐 أرسل ملف PDF لترجمته" if lang == 'ar' else "🌐 Send PDF file to translate"
    )

async def handle_rewrite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document rewriting"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = 'ai_rewrite'
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    await query.edit_message_text(
        "✍️ أرسل ملف PDF لإعادة كتابته" if lang == 'ar' else "✍️ Send PDF file to rewrite"
    )

async def handle_extract_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text extraction and cleanup"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = 'ai_extract'
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    await query.edit_message_text(
        "📤 أرسل ملف PDF لاستخراج النص" if lang == 'ar' else "📤 Send PDF file to extract text"
    )

async def handle_qa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PDF question-answering"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = 'ai_qa'
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    await query.edit_message_text(
        "❓ أرسل ملف PDF ثم اكتب سؤالك" if lang == 'ar' else "❓ Send PDF file then type your question"
    )

async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document analysis"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['operation'] = 'ai_analyze'
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    await query.edit_message_text(
        "📊 أرسل ملف PDF لتحليله" if lang == 'ar' else "📊 Send PDF file to analyze"
    )

# Handler instance
ai_features_handler = type('obj', (object,), {
    'handle_ai_menu': handle_ai_menu,
    'handle_summarize': handle_summarize,
    'handle_translate': handle_translate,
    'handle_rewrite': handle_rewrite,
    'handle_extract_text': handle_extract_text,
    'handle_qa': handle_qa,
    'handle_analyze': handle_analyze
})

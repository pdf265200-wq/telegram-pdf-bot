#!/usr/bin/env python3
"""Telegram PDF Bot for Railway"""

import asyncio
import logging
import sys
import os
from pathlib import Path

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import Config
from database.db_manager import db

class PDFBot:
    def __init__(self):
        self.token = Config.BOT_TOKEN
        if not self.token:
            logger.error("❌ BOT_TOKEN not set!")
            sys.exit(1)
        self.app = None
    
    async def initialize(self):
        """تهيئة البوت"""
        logger.info("🚀 Initializing bot...")
        
        # تهيئة قاعدة البيانات
        await db.init_db()
        logger.info("✅ Database initialized")
        
        # إنشاء التطبيق
        self.app = Application.builder().token(self.token).build()
        
        # استيراد handlers
        try:
            from handlers.start import start_handler
            from handlers.pdf_tools import pdf_tools_handler
            from handlers.payments import payments_handler
            from handlers.ocr import ocr_handler
            from handlers.ai_features import ai_features_handler
            from handlers.referrals import referrals_handler
            from handlers.ads import ads_handler
            from handlers.admin import admin_handler
            
            logger.info("✅ Handlers imported")
            
            # Command handlers
            self.app.add_handler(CommandHandler("start", start_handler.start))
            self.app.add_handler(CommandHandler("help", start_handler.help))
            self.app.add_handler(CommandHandler("menu", start_handler.menu))
            self.app.add_handler(CommandHandler("admin", admin_handler.admin_panel))
            
            # PDF Tools
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_pdf_menu, pattern="^pdf_tools$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_images_to_pdf, pattern="^images_to_pdf$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_merge_pdf, pattern="^merge_pdf$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_compress_pdf, pattern="^compress_pdf$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_pdf_to_word, pattern="^pdf_to_word$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_word_to_pdf, pattern="^word_to_pdf$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_rotate_pdf, pattern="^rotate_pdf$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_add_watermark, pattern="^add_watermark$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_protect_pdf, pattern="^protect_pdf$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_remove_password, pattern="^remove_password$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_extract_images, pattern="^extract_images$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_rearrange_pages, pattern="^rearrange_pages$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_delete_pages, pattern="^delete_pages$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_extract_pages, pattern="^extract_pages$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_repair_pdf, pattern="^repair_pdf$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_add_page_numbers, pattern="^add_page_numbers$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_excel_to_pdf, pattern="^excel_to_pdf$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_ppt_to_pdf, pattern="^ppt_to_pdf$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_text_to_pdf, pattern="^text_to_pdf$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_pdf_to_text, pattern="^pdf_to_text$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_pdf_to_html, pattern="^pdf_to_html$"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_quality_selection, pattern="^quality_"))
            self.app.add_handler(CallbackQueryHandler(pdf_tools_handler.handle_create_pdf, pattern="^create_pdf$"))
            
            # OCR & AI
            self.app.add_handler(CallbackQueryHandler(ocr_handler.handle_ocr_menu, pattern="^ocr_menu$"))
            self.app.add_handler(CallbackQueryHandler(ai_features_handler.handle_ai_menu, pattern="^ai_menu$"))
            
            # Payments
            self.app.add_handler(CallbackQueryHandler(payments_handler.handle_pricing, pattern="^pricing$"))
            self.app.add_handler(CallbackQueryHandler(payments_handler.handle_buy_premium, pattern="^buy_premium_"))
            
            # Referrals & Ads
            self.app.add_handler(CallbackQueryHandler(referrals_handler.handle_referrals, pattern="^referrals$"))
            self.app.add_handler(CallbackQueryHandler(ads_handler.handle_watch_ad, pattern="^watch_ad$"))
            
            # Main menu
            self.app.add_handler(CallbackQueryHandler(start_handler.menu, pattern="^main_menu$"))
            
            # File handlers
            self.app.add_handler(MessageHandler(filters.Document.ALL, pdf_tools_handler.handle_document))
            self.app.add_handler(MessageHandler(filters.PHOTO, pdf_tools_handler.handle_photo))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start_handler.handle_text))
            
            logger.info("✅ All handlers added")
            
        except Exception as e:
            logger.error(f"❌ Handler error: {e}")
            raise
        
        self.app.add_error_handler(self.error_handler)
        logger.info("✅ Bot initialized successfully")
    
    async def error_handler(self, update: Update, context):
        logger.error(f"Error: {context.error}")
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text("❌ حدث خطأ. حاول مرة أخرى.")
        except:
            pass
    
    def run(self):
        """تشغيل البوت - استخدام polling دائماً"""
        asyncio.run(self.initialize())
        logger.info("📡 Starting polling...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    bot = PDFBot()
    try:
        bot.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

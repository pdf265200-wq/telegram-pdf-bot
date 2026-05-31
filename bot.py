#!/usr/bin/env python3
"""Telegram PDF Bot for Railway"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# استيراد المكتبات
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.constants import ParseMode

from config import Config
from database.db_manager import db

# استيراد handlers بأمان
try:
    from handlers.start import start_handler
    from handlers.pdf_tools import pdf_tools_handler
    from handlers.payments import payments_handler
    logger.info("✅ All handlers loaded")
except ImportError as e:
    logger.error(f"❌ Handler import error: {e}")
    sys.exit(1)

class PDFBot:
    def __init__(self):
        self.token = Config.BOT_TOKEN
        self.app = None
    
    async def initialize(self):
        """تهيئة البوت وقاعدة البيانات"""
        logger.info("🚀 Initializing bot...")
        
        # تهيئة قاعدة البيانات
        await db.init_db()
        logger.info("✅ Database initialized")
        
        # إنشاء التطبيق
        self.app = Application.builder().token(self.token).build()
        
        # إضافة handlers الأساسية
        self.app.add_handler(CommandHandler("start", start_handler.start))
        self.app.add_handler(CommandHandler("help", start_handler.help))
        self.app.add_handler(CommandHandler("menu", start_handler.menu))
        
        # PDF handlers
        self.app.add_handler(CallbackQueryHandler(
            pdf_tools_handler.handle_pdf_menu, pattern="^pdf_tools$"
        ))
        self.app.add_handler(CallbackQueryHandler(
            pdf_tools_handler.handle_images_to_pdf, pattern="^images_to_pdf$"
        ))
        self.app.add_handler(CallbackQueryHandler(
            pdf_tools_handler.handle_merge_pdf, pattern="^merge_pdf$"
        ))
        self.app.add_handler(CallbackQueryHandler(
            pdf_tools_handler.handle_compress_pdf, pattern="^compress_pdf$"
        ))
        self.app.add_handler(CallbackQueryHandler(
            pdf_tools_handler.handle_document, pattern="^create_pdf$"
        ))
        self.app.add_handler(CallbackQueryHandler(
            pdf_tools_handler.handle_quality_selection, pattern="^quality_"
        ))
        
        # Payment handlers
        self.app.add_handler(CallbackQueryHandler(
            payments_handler.handle_pricing, pattern="^pricing$"
        ))
        self.app.add_handler(CallbackQueryHandler(
            payments_handler.handle_buy_premium, pattern="^buy_premium_"
        ))
        
        # File handlers
        self.app.add_handler(MessageHandler(filters.Document.ALL, pdf_tools_handler.handle_document))
        self.app.add_handler(MessageHandler(filters.PHOTO, pdf_tools_handler.handle_photo))
        
        # Main menu
        self.app.add_handler(CallbackQueryHandler(
            start_handler.menu, pattern="^main_menu$"
        ))
        
        # Error handler
        self.app.add_error_handler(self.error_handler)
        
        logger.info("✅ Bot initialized")
    
    async def error_handler(self, update: Update, context):
        """معالجة الأخطاء"""
        logger.error(f"Error: {context.error}")
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text("❌ حدث خطأ. حاول مرة أخرى.")
        except:
            pass
    
    async def run(self):
        """تشغيل البوت"""
        await self.initialize()
        
        # استخدام webhook أو polling
        webhook_url = os.getenv('RAILWAY_PUBLIC_DOMAIN')
        
        if webhook_url:
            logger.info(f"🌐 Using webhook: {webhook_url}")
            await self.app.run_webhook(
                listen="0.0.0.0",
                port=int(os.getenv('PORT', 8000)),
                webhook_url=f"https://{webhook_url}/webhook"
            )
        else:
            logger.info("📡 Starting polling...")
            await self.app.run_polling(allowed_updates=Update.ALL_TYPES)

async def main():
    bot = PDFBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

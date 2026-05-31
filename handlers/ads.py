from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

from config import Config
from database.db_manager import db

async def handle_watch_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle watch ad for premium reward"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    # Check if user can watch ads (free users only)
    if await db.check_premium_status(user.id):
        if lang == 'ar':
            await query.edit_message_text("👑 أنت بالفعل مستخدم بريميوم!")
        else:
            await query.edit_message_text("👑 You are already a premium user!")
        return
    
    # Show ad content
    if lang == 'ar':
        ad_text = """
📢 <b>إعلان</b>

🎉 احصل على ساعتين من البريميوم مجاناً!

شاهد هذا الإعلان البسيط:
• افتح الرابط أدناه
• انتظر 10 ثواني
• اضغط "تم المشاهدة"

ستحصل على بضع ساعات من البريميوم مجاناً!
"""
    else:
        ad_text = """
📢 <b>Advertisement</b>

🎉 Get 2 hours of premium for free!

Watch this simple ad:
• Open the link below
• Wait 10 seconds
• Press "Watched"

You'll get some hours of premium for free!
"""
    
    keyboard = [
        [InlineKeyboardButton(
            "▶️ مشاهدة الإعلان" if lang == 'ar' else "▶️ Watch Ad",
            url="https://t.me/yourchannel"
        )],
        [InlineKeyboardButton(
            "✅ تم المشاهدة" if lang == 'ar' else "✅ Watched",
            callback_data="ad_watched"
        )],
        [InlineKeyboardButton(
            "🔙 رجوع" if lang == 'ar' else "🔙 Back",
            callback_data="main_menu"
        )]
    ]
    
    await query.edit_message_text(
        ad_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

# Handler instance
ads_handler = type('obj', (object,), {
    'handle_watch_ad': handle_watch_ad
})

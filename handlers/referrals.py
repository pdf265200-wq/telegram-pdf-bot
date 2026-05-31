from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import Config
from database.db_manager import db

async def handle_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show referral information"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    bot_username = context.bot.username
    referral_link = f"https://t.me/{bot_username}?start={db_user.referral_code}"
    
    if lang == 'ar':
        text = f"""
👥 <b>نظام الإحالات</b>

🔗 رابط الإحالة الخاص بك:
<code>{referral_link}</code>

📊 <b>إحصائياتك:</b>
• عدد المدعوين: {db_user.referral_count}
• أيام بريميوم مكتسبة: {db_user.referral_earnings}

💰 <b>المكافآت:</b>
• لكل صديق: {Config.REFERRAL_DAYS_REWARD} أيام بريميوم
• الحد الأقصى: {Config.MAX_REFERRAL_REWARDS} يوم

شارك رابطك واكسب بريميوم مجاني! 🎉
"""
    else:
        text = f"""
👥 <b>Referral System</b>

🔗 Your referral link:
<code>{referral_link}</code>

📊 <b>Your Stats:</b>
• Invited: {db_user.referral_count}
• Premium days earned: {db_user.referral_earnings}

💰 <b>Rewards:</b>
• Per friend: {Config.REFERRAL_DAYS_REWARD} premium days
• Maximum: {Config.MAX_REFERRAL_REWARDS} days

Share your link and earn free premium! 🎉
"""
    
    keyboard = [
        [InlineKeyboardButton(
            "📤 مشاركة الرابط" if lang == 'ar' else "📤 Share Link",
            switch_inline_query=referral_link
        )],
        [InlineKeyboardButton(
            "🔙 رجوع" if lang == 'ar' else "🔙 Back",
            callback_data="main_menu"
        )]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

async def handle_referral_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed referral stats"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    if lang == 'ar':
        text = f"""
📊 <b>إحصائيات الإحالات</b>

👥 المدعوين: {db_user.referral_count}
⭐ أيام البريميوم: {db_user.referral_earnings}
💎 خطة البريميوم: {db_user.plan.value}

استمر في المشاركة لكسب المزيد!
"""
    else:
        text = f"""
📊 <b>Referral Statistics</b>

👥 Invited: {db_user.referral_count}
⭐ Premium days: {db_user.referral_earnings}
💎 Premium plan: {db_user.plan.value}

Keep sharing to earn more!
"""
    
    await query.edit_message_text(text, parse_mode=ParseMode.HTML)

# Handler instance
referrals_handler = type('obj', (object,), {
    'handle_referrals': handle_referrals,
    'handle_referral_stats': handle_referral_stats
})

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import Config
from database.db_manager import db

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    user = update.effective_user
    
    if user.id not in Config.ADMIN_IDS:
        await update.message.reply_text("⛔ غير مصرح" if context else "⛔ Unauthorized")
        return
    
    stats = await db.get_statistics()
    
    text = f"""
📊 <b>لوحة التحكم</b>

👥 <b>المستخدمين:</b>
• إجمالي: {stats['total_users']}
• نشط اليوم: {stats['daily_active']}
• بريميوم: {stats['premium_users']}

📄 <b>العمليات:</b>
• إجمالي: {stats['total_operations']}

💰 <b>الإيرادات:</b>
• {stats['total_revenue']} نجمة

"""
    
    keyboard = [
        [InlineKeyboardButton("👥 إدارة المستخدمين", callback_data="admin_users")],
        [InlineKeyboardButton("📢 إرسال broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 إحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("📝 السجلات", callback_data="admin_logs")],
        [InlineKeyboardButton("🚫 حظر/إلغاء حظر", callback_data="admin_ban")]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin actions"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    if user.id not in Config.ADMIN_IDS:
        return
    
    action = query.data
    
    if action == "admin_stats":
        stats = await db.get_statistics()
        text = f"""
📊 <b>إحصائيات تفصيلية</b>

👥 المستخدمين: {stats['total_users']}
📅 نشط اليوم: {stats['daily_active']}
💎 بريميوم: {stats['premium_users']}
📄 العمليات: {stats['total_operations']}
💰 الإيرادات: {stats['total_revenue']} ⭐
"""
        await query.edit_message_text(text, parse_mode=ParseMode.HTML)
    
    elif action == "admin_broadcast":
        context.user_data['awaiting_broadcast'] = True
        await query.edit_message_text("📢 أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:")

# Handler instance
admin_handler = type('obj', (object,), {
    'admin_panel': admin_panel,
    'handle_admin': handle_admin
})

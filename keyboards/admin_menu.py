from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_admin_menu() -> InlineKeyboardMarkup:
    """Get admin panel keyboard"""
    keyboard = [
        [InlineKeyboardButton("👥 المستخدمين", callback_data="admin_users")],
        [InlineKeyboardButton("📢 إرسال broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 إحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("📝 السجلات", callback_data="admin_logs")],
        [InlineKeyboardButton("🚫 حظر/إلغاء حظر", callback_data="admin_ban")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

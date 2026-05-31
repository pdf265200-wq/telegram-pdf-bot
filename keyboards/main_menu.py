from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu(lang: str = 'ar', is_premium: bool = False) -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    
    if lang == 'ar':
        keyboard = [
            [InlineKeyboardButton("📄 أدوات PDF", callback_data="pdf_tools")],
            [
                InlineKeyboardButton("🔍 OCR", callback_data="ocr_menu"),
                InlineKeyboardButton("🤖 AI", callback_data="ai_menu")
            ],
            [InlineKeyboardButton("💎 البريميوم", callback_data="pricing")],
            [
                InlineKeyboardButton("👥 الإحالات", callback_data="referrals"),
                InlineKeyboardButton("⭐ المفضلة", callback_data="favorites")
            ],
            [InlineKeyboardButton("📢 إعلان وكسب بريميوم", callback_data="watch_ad")],
            [InlineKeyboardButton("ℹ️ مساعدة", callback_data="help")]
        ]
        
        if is_premium:
            keyboard.insert(0, [InlineKeyboardButton("👑 حساب بريميوم", callback_data="premium_status")])
    
    else:  # English
        keyboard = [
            [InlineKeyboardButton("📄 PDF Tools", callback_data="pdf_tools")],
            [
                InlineKeyboardButton("🔍 OCR", callback_data="ocr_menu"),
                InlineKeyboardButton("🤖 AI", callback_data="ai_menu")
            ],
            [InlineKeyboardButton("💎 Premium", callback_data="pricing")],
            [
                InlineKeyboardButton("👥 Referrals", callback_data="referrals"),
                InlineKeyboardButton("⭐ Favorites", callback_data="favorites")
            ],
            [InlineKeyboardButton("📢 Watch Ad & Earn", callback_data="watch_ad")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ]
        
        if is_premium:
            keyboard.insert(0, [InlineKeyboardButton("👑 Premium Account", callback_data="premium_status")])
    
    return InlineKeyboardMarkup(keyboard)

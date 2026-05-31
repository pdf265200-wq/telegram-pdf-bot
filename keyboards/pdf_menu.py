from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_pdf_menu(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Get PDF tools menu"""
    
    if lang == 'ar':
        keyboard = [
            [InlineKeyboardButton("🖼 صور إلى PDF", callback_data="images_to_pdf")],
            [InlineKeyboardButton("📑 دمج PDF", callback_data="merge_pdf"),
             InlineKeyboardButton("✂️ تقسيم PDF", callback_data="split_pdf")],
            [InlineKeyboardButton("🗜 ضغط PDF", callback_data="compress_pdf")],
            [InlineKeyboardButton("🔄 PDF إلى صور", callback_data="pdf_to_images")],
            [InlineKeyboardButton("📝 PDF إلى Word", callback_data="pdf_to_word"),
             InlineKeyboardButton("📄 Word إلى PDF", callback_data="word_to_pdf")],
            [InlineKeyboardButton("🔄 تدوير PDF", callback_data="rotate_pdf")],
            [InlineKeyboardButton("💧 علامة مائية", callback_data="add_watermark")],
            [InlineKeyboardButton("🖼 استخراج الصور", callback_data="extract_images")],
            [InlineKeyboardButton("🔒 حماية PDF", callback_data="protect_pdf"),
             InlineKeyboardButton("🔓 إزالة الحماية", callback_data="remove_password")],
            [InlineKeyboardButton("📊 ترتيب الصفحات", callback_data="rearrange_pages")],
            [InlineKeyboardButton("🗑 حذف صفحات", callback_data="delete_pages"),
             InlineKeyboardButton("📤 استخراج صفحات", callback_data="extract_pages")],
            [InlineKeyboardButton("🔧 إصلاح PDF", callback_data="repair_pdf")],
            [InlineKeyboardButton("🔢 ترقيم الصفحات", callback_data="add_page_numbers")],
            [InlineKeyboardButton("📊 Excel إلى PDF", callback_data="excel_to_pdf"),
             InlineKeyboardButton("📽 PPT إلى PDF", callback_data="ppt_to_pdf")],
            [InlineKeyboardButton("📝 نص إلى PDF", callback_data="text_to_pdf"),
             InlineKeyboardButton("📄 PDF إلى نص", callback_data="pdf_to_text")],
            [InlineKeyboardButton("🌐 PDF إلى HTML", callback_data="pdf_to_html")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🖼 Images to PDF", callback_data="images_to_pdf")],
            [InlineKeyboardButton("📑 Merge PDF", callback_data="merge_pdf"),
             InlineKeyboardButton("✂️ Split PDF", callback_data="split_pdf")],
            [InlineKeyboardButton("🗜 Compress PDF", callback_data="compress_pdf")],
            [InlineKeyboardButton("🔄 PDF to Images", callback_data="pdf_to_images")],
            [InlineKeyboardButton("📝 PDF to Word", callback_data="pdf_to_word"),
             InlineKeyboardButton("📄 Word to PDF", callback_data="word_to_pdf")],
            [InlineKeyboardButton("🔄 Rotate PDF", callback_data="rotate_pdf")],
            [InlineKeyboardButton("💧 Watermark", callback_data="add_watermark")],
            [InlineKeyboardButton("🖼 Extract Images", callback_data="extract_images")],
            [InlineKeyboardButton("🔒 Protect PDF", callback_data="protect_pdf"),
             InlineKeyboardButton("🔓 Remove Password", callback_data="remove_password")],
            [InlineKeyboardButton("📊 Rearrange Pages", callback_data="rearrange_pages")],
            [InlineKeyboardButton("🗑 Delete Pages", callback_data="delete_pages"),
             InlineKeyboardButton("📤 Extract Pages", callback_data="extract_pages")],
            [InlineKeyboardButton("🔧 Repair PDF", callback_data="repair_pdf")],
            [InlineKeyboardButton("🔢 Page Numbers", callback_data="add_page_numbers")],
            [InlineKeyboardButton("📊 Excel to PDF", callback_data="excel_to_pdf"),
             InlineKeyboardButton("📽 PPT to PDF", callback_data="ppt_to_pdf")],
            [InlineKeyboardButton("📝 Text to PDF", callback_data="text_to_pdf"),
             InlineKeyboardButton("📄 PDF to Text", callback_data="pdf_to_text")],
            [InlineKeyboardButton("🌐 PDF to HTML", callback_data="pdf_to_html")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
    
    return InlineKeyboardMarkup(keyboard)


def get_quality_menu(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Get compression quality menu"""
    if lang == 'ar':
        keyboard = [
            [InlineKeyboardButton("📉 منخفضة (حجم أصغر)", callback_data="quality_low")],
            [InlineKeyboardButton("📊 متوسطة", callback_data="quality_medium")],
            [InlineKeyboardButton("📈 عالية (جودة أفضل)", callback_data="quality_high")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="compress_pdf")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📉 Low (Smaller Size)", callback_data="quality_low")],
            [InlineKeyboardButton("📊 Medium", callback_data="quality_medium")],
            [InlineKeyboardButton("📈 High (Better Quality)", callback_data="quality_high")],
            [InlineKeyboardButton("🔙 Back", callback_data="compress_pdf")]
        ]
    
    return InlineKeyboardMarkup(keyboard)


def get_rotation_menu(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Get rotation options menu"""
    if lang == 'ar':
        keyboard = [
            [InlineKeyboardButton("↩️ 90°", callback_data="rotate_90"),
             InlineKeyboardButton("↩️ 180°", callback_data="rotate_180"),
             InlineKeyboardButton("↩️ 270°", callback_data="rotate_270")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="pdf_tools")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("↩️ 90°", callback_data="rotate_90"),
             InlineKeyboardButton("↩️ 180°", callback_data="rotate_180"),
             InlineKeyboardButton("↩️ 270°", callback_data="rotate_270")],
            [InlineKeyboardButton("🔙 Back", callback_data="pdf_tools")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

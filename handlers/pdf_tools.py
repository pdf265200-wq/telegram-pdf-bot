from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import os
import asyncio
from typing import List

from config import Config
from database.db_manager import db
from services.pdf_service import pdf_service
from utils.helpers import download_file, send_file, generate_temp_filename, clean_temp_files
from utils.validators import validate_file_size, validate_file_type
from keyboards.pdf_menu import get_pdf_menu, get_quality_menu, get_rotation_menu
from locales import ar, en

async def handle_pdf_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show PDF tools menu"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    await query.edit_message_text(
        "📄 أدوات PDF" if lang == 'ar' else "📄 PDF Tools",
        reply_markup=get_pdf_menu(lang)
    )

async def handle_images_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle images to PDF conversion"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    messages = ar if lang == 'ar' else en
    
    # Check daily limit
    if not await db.check_daily_limit(user.id):
        await query.edit_message_text(messages.DAILY_LIMIT_REACHED)
        return
    
    context.user_data['operation'] = 'images_to_pdf'
    
    await query.edit_message_text(messages.SEND_IMAGES)

async def handle_merge_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PDF merge"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    messages = ar if lang == 'ar' else en
    
    if not await db.check_daily_limit(user.id):
        await query.edit_message_text(messages.DAILY_LIMIT_REACHED)
        return
    
    context.user_data['operation'] = 'merge_pdf'
    context.user_data['pdf_files'] = []
    
    await query.edit_message_text(messages.SEND_PDFS_TO_MERGE)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads"""
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    messages = ar if lang == 'ar' else en
    operation = context.user_data.get('operation')
    
    if not operation:
        await update.message.reply_text(messages.USE_MENU_MESSAGE)
        return
    
    # Download file
    file = update.message.document
    file_path = await download_file(file, context)
    
    if not file_path:
        await update.message.reply_text(messages.DOWNLOAD_ERROR)
        return
    
    # Validate file
    if not validate_file_size(file_path, user.id):
        await update.message.reply_text(messages.FILE_TOO_LARGE)
        os.unlink(file_path)
        return
    
    # Process based on operation
    progress_msg = await update.message.reply_text(messages.PROCESSING)
    
    try:
        if operation == 'images_to_pdf':
            # Handle multiple images
            if 'image_files' not in context.user_data:
                context.user_data['image_files'] = []
            context.user_data['image_files'].append(file_path)
            
            # Check if user wants to add more
            keyboard = [
                [InlineKeyboardButton(
                    "✅ إنشاء PDF" if lang == 'ar' else "✅ Create PDF",
                    callback_data="create_pdf"
                )],
                [InlineKeyboardButton(
                    "➕ إضافة المزيد" if lang == 'ar' else "➕ Add More",
                    callback_data="add_more_images"
                )]
            ]
            await progress_msg.edit_text(
                f"📸 {len(context.user_data['image_files'])} " + 
                ("صور مضافة" if lang == 'ar' else "images added"),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        elif operation == 'merge_pdf':
            context.user_data['pdf_files'].append(file_path)
            
            if len(context.user_data['pdf_files']) >= 2:
                # Start merging
                output_path = await pdf_service.merge_pdfs(context.user_data['pdf_files'])
                await send_file(update, output_path, 'merged.pdf')
                await progress_msg.delete()
                
                # Cleanup
                clean_temp_files(context.user_data['pdf_files'])
                clean_temp_files([output_path])
                context.user_data.clear()
            else:
                await progress_msg.edit_text(messages.SEND_MORE_PDFS)
        
        elif operation == 'compress_pdf':
            quality = context.user_data.get('quality', 'medium')
            output_path = await pdf_service.compress_pdf(file_path, quality)
            await send_file(update, output_path, 'compressed.pdf')
            await progress_msg.delete()
            clean_temp_files([file_path, output_path])
        
        elif operation == 'pdf_to_word':
            output_path = await pdf_service.pdf_to_word(file_path)
            await send_file(update, output_path, 'converted.docx')
            await progress_msg.delete()
            clean_temp_files([file_path, output_path])
        
        elif operation == 'word_to_pdf':
            output_path = await pdf_service.word_to_pdf(file_path)
            await send_file(update, output_path, 'converted.pdf')
            await progress_msg.delete()
            clean_temp_files([file_path, output_path])
        
        # Add more operations here...
        
        else:
            await progress_msg.edit_text(messages.OPERATION_NOT_FOUND)
            clean_temp_files([file_path])
        
        # Log operation
        await db.add_operation(user.id, operation, file_name=file.file_name, file_size=file.file_size)
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Error: {str(e)}")
        clean_temp_files([file_path])

async def handle_compress_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show compression quality options"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    context.user_data['operation'] = 'compress_pdf'
    
    await query.edit_message_text(
        "اختر جودة الضغط:" if lang == 'ar' else "Choose compression quality:",
        reply_markup=get_quality_menu(lang)
    )

async def handle_quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quality selection for compression"""
    query = update.callback_query
    await query.answer()
    
    quality = query.data.split('_')[1]  # quality_low, quality_medium, quality_high
    context.user_data['quality'] = quality
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    messages = ar if lang == 'ar' else en
    
    await query.edit_message_text(messages.SEND_PDF_TO_COMPRESS)

async def handle_create_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create PDF from collected images"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    messages = ar if lang == 'ar' else en
    
    image_files = context.user_data.get('image_files', [])
    
    if not image_files:
        await query.edit_message_text(messages.NO_IMAGES)
        return
    
    progress_msg = await query.edit_message_text(messages.PROCESSING)
    
    try:
        output_path = await pdf_service.images_to_pdf(image_files)
        await send_file(update, output_path, 'images.pdf')
        await progress_msg.delete()
        clean_temp_files(image_files + [output_path])
        context.user_data.clear()
        
        await db.add_operation(user.id, 'images_to_pdf')
    except Exception as e:
        await progress_msg.edit_text(f"❌ Error: {str(e)}")
        clean_temp_files(image_files)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages for image to PDF"""
    user = update.effective_user
    operation = context.user_data.get('operation')
    
    if operation != 'images_to_pdf':
        return
    
    # Download photo
    file = await update.message.photo[-1].get_file()
    file_path = generate_temp_filename('.jpg')
    await file.download_to_drive(file_path)
    
    if 'image_files' not in context.user_data:
        context.user_data['image_files'] = []
    context.user_data['image_files'].append(file_path)
    
    lang = (await db.get_user(user.id)).language if await db.get_user(user.id) else 'ar'
    messages = ar if lang == 'ar' else en
    
    keyboard = [
        [InlineKeyboardButton(
            "✅ إنشاء PDF" if lang == 'ar' else "✅ Create PDF",
            callback_data="create_pdf"
        )],
        [InlineKeyboardButton(
            "➕ إضافة المزيد" if lang == 'ar' else "➕ Add More",
            callback_data="add_more_images"
        )]
    ]
    
    await update.message.reply_text(
        f"📸 {len(context.user_data['image_files'])} " + 
        ("صور مضافة" if lang == 'ar' else "images added"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Create handler instance with all methods
pdf_tools_handler = type('obj', (object,), {
    'handle_pdf_menu': handle_pdf_menu,
    'handle_images_to_pdf': handle_images_to_pdf,
    'handle_merge_pdf': handle_merge_pdf,
    'handle_document': handle_document,
    'handle_compress_pdf': handle_compress_pdf,
    'handle_quality_selection': handle_quality_selection,
    'handle_create_pdf': handle_create_pdf,
    'handle_photo': handle_photo,
    # Add all other handlers...
})

import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional, List
from telegram import Update, Bot
from telegram.ext import ContextTypes

from config import Config

def generate_temp_filename(extension: str = '') -> str:
    """Generate unique temporary filename"""
    filename = f"{uuid.uuid4().hex}{extension}"
    return os.path.join(Config.TEMP_DIR, filename)

async def download_file(file, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """Download file from Telegram"""
    try:
        file_path = generate_temp_filename(os.path.splitext(file.file_name)[1])
        telegram_file = await file.get_file()
        await telegram_file.download_to_drive(file_path)
        return file_path
    except Exception as e:
        print(f"Download error: {e}")
        return None

async def send_file(update: Update, file_path: str, filename: str = None):
    """Send file to user"""
    if not filename:
        filename = os.path.basename(file_path)
    
    try:
        if update.callback_query:
            await update.callback_query.message.reply_document(
                document=open(file_path, 'rb'),
                filename=filename
            )
        else:
            await update.message.reply_document(
                document=open(file_path, 'rb'),
                filename=filename
            )
    except Exception as e:
        print(f"Send file error: {e}")

def clean_temp_files(file_paths: List[str]):
    """Clean up temporary files"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.unlink(path)
        except Exception as e:
            print(f"Cleanup error: {e}")

async def send_progress_message(update: Update, text: str) -> callable:
    """Send progress message and return update function"""
    if update.callback_query:
        msg = await update.callback_query.edit_message_text(text)
    else:
        msg = await update.message.reply_text(text)
    
    async def update_text(new_text: str):
        await msg.edit_text(new_text)
    
    return update_text

async def delete_message_after_delay(message, delay: int = 5):
    """Delete message after delay"""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

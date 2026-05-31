import os
from typing import Optional
import magic

from config import Config
from database.db_manager import db

ALLOWED_EXTENSIONS = {
    'pdf': ['.pdf'],
    'image': ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'],
    'document': ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'],
    'all': ['.pdf', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', 
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
}

async def validate_file_size(file_path: str, user_id: int) -> bool:
    """Validate file size based on user plan"""
    file_size = os.path.getsize(file_path)
    
    is_premium = await db.check_premium_status(user_id)
    
    if is_premium:
        user = await db.get_user(user_id)
        if user.plan.value == 'lifetime' or user.plan.value == 'premium_yearly':
            return file_size <= Config.MAX_FILE_SIZE_PREMIUM_YEARLY
        else:
            return file_size <= Config.MAX_FILE_SIZE_PREMIUM_MONTHLY
    else:
        return file_size <= Config.MAX_FILE_SIZE_FREE

def validate_file_type(file_path: str, allowed_types: str = 'all') -> bool:
    """Validate file type"""
    extension = os.path.splitext(file_path)[1].lower()
    allowed = ALLOWED_EXTENSIONS.get(allowed_types, ALLOWED_EXTENSIONS['all'])
    return extension in allowed

def validate_pdf(file_path: str) -> bool:
    """Validate if file is a valid PDF"""
    try:
        mime = magic.Magic(mime=True)
        file_mime = mime.from_file(file_path)
        return file_mime == 'application/pdf'
    except:
        return False

async def validate_user_can_operate(user_id: int) -> tuple[bool, str]:
    """Check if user can perform operation"""
    # Check if banned
    user = await db.get_user(user_id)
    if user and user.is_banned:
        return False, "banned"
    
    # Check daily limit
    if not await db.check_daily_limit(user_id):
        return False, "limit_reached"
    
    return True, "ok"

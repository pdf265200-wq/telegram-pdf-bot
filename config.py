import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'PDFToolsBot')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///database/bot.db')
    
    # Redis (for Celery)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # File Storage
    TEMP_DIR = Path(os.getenv('TEMP_DIR', 'temp'))
    MAX_FILE_SIZE_FREE = 20 * 1024 * 1024  # 20 MB
    MAX_FILE_SIZE_PREMIUM_MONTHLY = 500 * 1024 * 1024  # 500 MB
    MAX_FILE_SIZE_PREMIUM_YEARLY = 1024 * 1024 * 1024  # 1 GB
    FILE_RETENTION_HOURS = 1
    
    # Rate Limiting
    RATE_LIMIT_FREE = 5  # operations per day
    RATE_LIMIT_PREMIUM = float('inf')
    
    # Payment
    TELEGRAM_STARS_ENABLED = os.getenv('TELEGRAM_STARS_ENABLED', 'true').lower() == 'true'
    PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN', '')
    
    # Premium Plans (in Telegram Stars)
    PREMIUM_MONTHLY_PRICE = 499  # Stars
    PREMIUM_YEARLY_PRICE = 4999  # Stars
    LIFETIME_PRICE = 14999  # Stars
    
    # AI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    AI_ENABLED = bool(OPENAI_API_KEY)
    
    # OCR Configuration
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
    OCR_LANGUAGES = ['ara', 'eng']
    
    # Referral System
    REFERRAL_DAYS_REWARD = 3  # days of premium per referral
    MAX_REFERRAL_REWARDS = 30  # max days from referrals
    
    # Advertisement
    ADS_ENABLED = os.getenv('ADS_ENABLED', 'true').lower() == 'true'
    ADS_REWARD_PREMIUM_HOURS = 2  # hours of premium for watching ad
    
    # Admin
    ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []
    
    # Languages
    SUPPORTED_LANGUAGES = ['ar', 'en']
    DEFAULT_LANGUAGE = 'ar'
    
    # Security
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', '')
    MALWARE_SCAN_ENABLED = os.getenv('MALWARE_SCAN_ENABLED', 'false').lower() == 'true'
    
    # Performance
    MAX_CONCURRENT_PROCESSES = int(os.getenv('MAX_CONCURRENT_PROCESSES', '4'))
    QUEUE_PRIORITY_FREE = 0
    QUEUE_PRIORITY_PREMIUM = 1
    QUEUE_PRIORITY_LIFETIME = 2

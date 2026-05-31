from sqlalchemy import (
    Column, Integer, String, BigInteger, Boolean, DateTime, 
    Float, ForeignKey, Enum, Text, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"

class SubscriptionPlan(enum.Enum):
    FREE = "free"
    PREMIUM_MONTHLY = "premium_monthly"
    PREMIUM_YEARLY = "premium_yearly"
    LIFETIME = "lifetime"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    language = Column(String(10), default='ar')
    role = Column(Enum(UserRole), default=UserRole.USER)
    plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    premium_until = Column(DateTime, nullable=True)
    daily_operations = Column(Integer, default=0)
    total_operations = Column(Integer, default=0)
    referral_code = Column(String(20), unique=True)
    referred_by = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=True)
    referral_count = Column(Integer, default=0)
    referral_earnings = Column(Integer, default=0)  # Days earned
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_activity = Column(DateTime, server_default=func.now())
    
    # Relationships
    payments = relationship("Payment", back_populates="user")
    operations = relationship("Operation", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    telegram_payment_id = Column(String(255))
    provider_payment_id = Column(String(255))
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='XTR')  # Telegram Stars
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")

class Operation(Base):
    __tablename__ = 'operations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    operation_type = Column(String(50), nullable=False)
    file_name = Column(String(255))
    file_size = Column(BigInteger)
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)  # seconds
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="operations")

class Favorite(Base):
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tool_name = Column(String(50), nullable=False)
    position = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="favorites")

class Referral(Base):
    __tablename__ = 'referrals'
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    referred_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    reward_claimed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class Advertisement(Base):
    __tablename__ = 'advertisements'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String(500))
    target_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    views_count = Column(Integer, default=0)
    clicks_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

class AdminLog(Base):
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(BigInteger, nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

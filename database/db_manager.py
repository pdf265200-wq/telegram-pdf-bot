import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import secrets
import string

from config import Config
from database.models import Base, User, Payment, Operation, Favorite, Referral, Advertisement, UserRole, SubscriptionPlan, PaymentStatus

class DatabaseManager:
    def __init__(self):
        self.engine = create_async_engine(
            Config.DATABASE_URL,
            echo=False,
            pool_size=20,
            max_overflow=10
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self):
        async with self.async_session() as session:
            yield session
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    async def create_user(self, telegram_id: int, **kwargs) -> User:
        async with self.async_session() as session:
            # Generate unique referral code
            referral_code = await self._generate_referral_code()
            
            user = User(
                telegram_id=telegram_id,
                referral_code=referral_code,
                **kwargs
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    async def get_or_create_user(self, telegram_id: int, **kwargs) -> User:
        user = await self.get_user(telegram_id)
        if not user:
            user = await self.create_user(telegram_id, **kwargs)
        return user
    
    async def update_user(self, telegram_id: int, **kwargs) -> Optional[User]:
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                await session.commit()
                await session.refresh(user)
            return user
    
    async def check_premium_status(self, telegram_id: int) -> bool:
        user = await self.get_user(telegram_id)
        if not user:
            return False
        
        if user.plan == SubscriptionPlan.LIFETIME:
            return True
        
        if user.premium_until and user.premium_until > datetime.utcnow():
            return True
        
        # Premium expired, downgrade to free
        if user.plan != SubscriptionPlan.FREE:
            await self.update_user(
                telegram_id,
                plan=SubscriptionPlan.FREE,
                premium_until=None
            )
        
        return False
    
    async def check_daily_limit(self, telegram_id: int) -> bool:
        user = await self.get_user(telegram_id)
        if not user:
            return False
        
        # Check if premium
        is_premium = await self.check_premium_status(telegram_id)
        if is_premium:
            return True
        
        # Check daily operations for free users
        today = datetime.utcnow().date()
        async with self.async_session() as session:
            result = await session.execute(
                select(func.count()).where(
                    and_(
                        Operation.user_id == user.id,
                        func.date(Operation.created_at) == today
                    )
                )
            )
            daily_count = result.scalar()
        
        return daily_count < Config.RATE_LIMIT_FREE
    
    async def add_operation(self, telegram_id: int, operation_type: str, **kwargs) -> Operation:
        user = await self.get_user(telegram_id)
        if not user:
            return None
        
        async with self.async_session() as session:
            operation = Operation(
                user_id=user.id,
                operation_type=operation_type,
                **kwargs
            )
            session.add(operation)
            
            # Update user stats
            user.total_operations += 1
            user.last_activity = datetime.utcnow()
            
            await session.commit()
            await session.refresh(operation)
            return operation
    
    async def create_payment(self, telegram_id: int, amount: float, plan: SubscriptionPlan, **kwargs) -> Payment:
        user = await self.get_user(telegram_id)
        if not user:
            return None
        
        async with self.async_session() as session:
            payment = Payment(
                user_id=user.id,
                amount=amount,
                plan=plan,
                **kwargs
            )
            session.add(payment)
            await session.commit()
            await session.refresh(payment)
            return payment
    
    async def complete_payment(self, payment_id: int) -> bool:
        async with self.async_session() as session:
            result = await session.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            payment = result.scalar_one_or_none()
            
            if not payment:
                return False
            
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.utcnow()
            
            # Update user plan
            user = payment.user
            user.plan = payment.plan
            
            if payment.plan == SubscriptionPlan.PREMIUM_MONTHLY:
                user.premium_until = datetime.utcnow() + timedelta(days=30)
            elif payment.plan == SubscriptionPlan.PREMIUM_YEARLY:
                user.premium_until = datetime.utcnow() + timedelta(days=365)
            elif payment.plan == SubscriptionPlan.LIFETIME:
                user.premium_until = None  # Never expires
            
            await session.commit()
            return True
    
    async def add_referral(self, referrer_id: int, referred_id: int) -> bool:
        async with self.async_session() as session:
            # Check if already referred
            existing = await session.execute(
                select(Referral).where(
                    and_(
                        Referral.referred_id == referred_id
                    )
                )
            )
            if existing.scalar_one_or_none():
                return False
            
            referral = Referral(
                referrer_id=referrer_id,
                referred_id=referred_id
            )
            session.add(referral)
            
            # Update referrer stats
            referrer = await self.get_user(referrer_id)
            if referrer:
                referrer.referral_count += 1
                
                # Add premium days as reward
                reward_days = min(Config.REFERRAL_DAYS_REWARD, Config.MAX_REFERRAL_REWARDS - referrer.referral_earnings)
                if reward_days > 0:
                    referrer.referral_earnings += reward_days
                    
                    if referrer.premium_until:
                        referrer.premium_until += timedelta(days=reward_days)
                    else:
                        referrer.premium_until = datetime.utcnow() + timedelta(days=reward_days)
                    
                    if referrer.plan == SubscriptionPlan.FREE:
                        referrer.plan = SubscriptionPlan.PREMIUM_MONTHLY
            
            await session.commit()
            return True
    
    async def get_statistics(self) -> Dict[str, Any]:
        async with self.async_session() as session:
            total_users = await session.scalar(select(func.count(User.id)))
            
            today = datetime.utcnow().date()
            daily_active = await session.scalar(
                select(func.count(User.id)).where(
                    func.date(User.last_activity) == today
                )
            )
            
            total_operations = await session.scalar(select(func.count(Operation.id)))
            
            total_revenue = await session.scalar(
                select(func.sum(Payment.amount)).where(
                    Payment.status == PaymentStatus.COMPLETED
                )
            ) or 0
            
            premium_users = await session.scalar(
                select(func.count(User.id)).where(
                    User.plan != SubscriptionPlan.FREE
                )
            )
            
            return {
                'total_users': total_users,
                'daily_active': daily_active,
                'total_operations': total_operations,
                'total_revenue': float(total_revenue),
                'premium_users': premium_users
            }
    
    async def _generate_referral_code(self) -> str:
        while True:
            code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
            async with self.async_session() as session:
                existing = await session.execute(
                    select(User).where(User.referral_code == code)
                )
                if not existing.scalar_one_or_none():
                    return code

# Global database instance
db = DatabaseManager()

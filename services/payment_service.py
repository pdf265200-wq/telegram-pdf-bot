from typing import Optional, Dict
from datetime import datetime, timedelta
import hashlib
import hmac

from config import Config
from database.db_manager import db
from database.models import SubscriptionPlan, PaymentStatus

class PaymentService:
    def __init__(self):
        self.provider_token = Config.PAYMENT_PROVIDER_TOKEN
    
    async def create_invoice(self, user_id: int, plan: SubscriptionPlan) -> Dict:
        """Create payment invoice"""
        prices = {
            SubscriptionPlan.PREMIUM_MONTHLY: Config.PREMIUM_MONTHLY_PRICE,
            SubscriptionPlan.PREMIUM_YEARLY: Config.PREMIUM_YEARLY_PRICE,
            SubscriptionPlan.LIFETIME: Config.LIFETIME_PRICE
        }
        
        amount = prices.get(plan, 0)
        
        return {
            'user_id': user_id,
            'amount': amount,
            'plan': plan,
            'currency': 'XTR'
        }
    
    async def verify_payment(self, payment_data: Dict) -> bool:
        """Verify payment authenticity"""
        # Verify Telegram payment data
        if Config.TELEGRAM_STARS_ENABLED:
            return True  # Telegram handles verification
        
        # Add additional verification logic here
        return True
    
    async def process_payment(self, payment_id: int) -> bool:
        """Process successful payment"""
        return await db.complete_payment(payment_id)
    
    async def refund_payment(self, payment_id: int) -> bool:
        """Process refund"""
        async with db.async_session() as session:
            from database.models import Payment, PaymentStatus as PS
            from sqlalchemy import select
            
            result = await session.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            payment = result.scalar_one_or_none()
            
            if payment and payment.status == PS.COMPLETED:
                payment.status = PS.REFUNDED
                await session.commit()
                return True
            
            return False
    
    async def get_user_subscription(self, user_id: int) -> Dict:
        """Get user subscription details"""
        user = await db.get_user(user_id)
        if not user:
            return {}
        
        return {
            'plan': user.plan.value,
            'premium_until': user.premium_until,
            'is_premium': await db.check_premium_status(user_id),
            'total_spent': await self.get_total_spent(user_id)
        }
    
    async def get_total_spent(self, user_id: int) -> float:
        """Get total amount spent by user"""
        async with db.async_session() as session:
            from database.models import Payment, PaymentStatus as PS
            from sqlalchemy import select, func
            
            result = await session.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.user_id == user_id,
                    Payment.status == PS.COMPLETED
                )
            )
            return result.scalar() or 0

# Global instance
payment_service = PaymentService()

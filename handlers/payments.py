from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import datetime, timedelta

from config import Config
from database.db_manager import db
from database.models import SubscriptionPlan, PaymentStatus

async def handle_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pricing plans"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    db_user = await db.get_user(user.id)
    lang = db_user.language if db_user else 'ar'
    
    if lang == 'ar':
        text = """
💎 <b>خطط البريميوم</b>

<b>🟡 شهري:</b>
• جميع المميزات
• حجم ملف حتى 500 ميجابايت
• معالجة سريعة
• السعر: {monthly} نجمة

<b>🟠 سنوي:</b>
• جميع المميزات
• حجم ملف حتى 1 جيجابايت
• أولوية قصوى
• السعر: {yearly} نجمة

<b>💎 مدى الحياة:</b>
• وصول دائم
• جميع المميزات المستقبلية
• السعر: {lifetime} نجمة

اختر خطتك 👇
""".format(
            monthly=Config.PREMIUM_MONTHLY_PRICE,
            yearly=Config.PREMIUM_YEARLY_PRICE,
            lifetime=Config.LIFETIME_PRICE
        )
        
        keyboard = [
            [InlineKeyboardButton(f"🟡 شهري - {Config.PREMIUM_MONTHLY_PRICE} ⭐", callback_data="buy_premium_monthly")],
            [InlineKeyboardButton(f"🟠 سنوي - {Config.PREMIUM_YEARLY_PRICE} ⭐", callback_data="buy_premium_yearly")],
            [InlineKeyboardButton(f"💎 مدى الحياة - {Config.LIFETIME_PRICE} ⭐", callback_data="buy_premium_lifetime")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
        ]
    else:
        text = """
💎 <b>Premium Plans</b>

<b>🟡 Monthly:</b>
• All features
• File size up to 500 MB
• Fast processing
• Price: {monthly} Stars

<b>🟠 Yearly:</b>
• All features
• File size up to 1 GB
• Highest priority
• Price: {yearly} Stars

<b>💎 Lifetime:</b>
• Permanent access
• All future features
• Price: {lifetime} Stars

Choose your plan 👇
""".format(
            monthly=Config.PREMIUM_MONTHLY_PRICE,
            yearly=Config.PREMIUM_YEARLY_PRICE,
            lifetime=Config.LIFETIME_PRICE
        )
        
        keyboard = [
            [InlineKeyboardButton(f"🟡 Monthly - {Config.PREMIUM_MONTHLY_PRICE} ⭐", callback_data="buy_premium_monthly")],
            [InlineKeyboardButton(f"🟠 Yearly - {Config.PREMIUM_YEARLY_PRICE} ⭐", callback_data="buy_premium_yearly")],
            [InlineKeyboardButton(f"💎 Lifetime - {Config.LIFETIME_PRICE} ⭐", callback_data="buy_premium_lifetime")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def handle_buy_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle premium purchase"""
    query = update.callback_query
    await query.answer()
    
    plan_map = {
        'buy_premium_monthly': (Config.PREMIUM_MONTHLY_PRICE, "Premium Monthly"),
        'buy_premium_yearly': (Config.PREMIUM_YEARLY_PRICE, "Premium Yearly"),
        'buy_premium_lifetime': (Config.LIFETIME_PRICE, "Lifetime Premium")
    }
    
    plan_key = query.data
    if plan_key not in plan_map:
        return
    
    amount, title = plan_map[plan_key]
    
    # Send invoice
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=title,
        description=f"Upgrade to {title} plan",
        payload=plan_key,
        provider_token=Config.PAYMENT_PROVIDER_TOKEN,
        currency="XTR",
        prices=[LabeledPrice(title, amount)],
        start_parameter="premium_upgrade"
    )

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pre-checkout"""
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payment"""
    payment = update.message.successful_payment
    user = update.effective_user
    
    # Map payment to plan
    plan_map = {
        'buy_premium_monthly': SubscriptionPlan.PREMIUM_MONTHLY,
        'buy_premium_yearly': SubscriptionPlan.PREMIUM_YEARLY,
        'buy_premium_lifetime': SubscriptionPlan.LIFETIME
    }
    
    plan = plan_map.get(payment.invoice_payload)
    if not plan:
        return
    
    # Save payment
    db_payment = await db.create_payment(
        user.id,
        payment.total_amount / 100,
        plan,
        telegram_payment_id=payment.telegram_payment_charge_id,
        provider_payment_id=payment.provider_payment_charge_id
    )
    
    if db_payment:
        await db.complete_payment(db_payment.id)
        
        lang = (await db.get_user(user.id)).language if await db.get_user(user.id) else 'ar'
        success_msg = "✅ تم تفعيل البريميوم بنجاح!" if lang == 'ar' else "✅ Premium activated successfully!"
        
        await update.message.reply_text(success_msg)

# Handler instance
payments_handler = type('obj', (object,), {
    'handle_pricing': handle_pricing,
    'handle_buy_premium': handle_buy_premium,
    'precheckout': precheckout,
    'successful_payment': successful_payment
})

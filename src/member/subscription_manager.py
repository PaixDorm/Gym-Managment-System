import os
from datetime import date, datetime
from src.models.transaction import Transaction
from src.models.subscription import Subscription, SubscriptionPlan, next_start_date, month_to_persian
from src.models.wallet import InsufficientBalanceError
from src.member.wallet_manager import (get_wallet, record_transaction, new_transaction, get_all_transactions, StorageError)

current_dir = os.path.abspath(os.path.dirname(__file__))
subscription_file_path = os.path.normpath(os.path.join(current_dir, "../../data/subscriptions.txt"))

subscription_plans = {
    1: SubscriptionPlan(months=1, price=100000),
    3: SubscriptionPlan(months=3, price=250000),
    6: SubscriptionPlan(months=6, price=450000)}

def _append_subscription(sub):
    """افزودن یک خط اشتراک به انتهای فایل با رمزگذاری utf-8"""
    if not isinstance(sub, Subscription):
        raise ValueError("ورودی باید از نوع شیء Subscription باشد.")
    try:
        directory = os.path.dirname(subscription_file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(subscription_file_path, "a", encoding="utf-8") as f:
            f.write(sub.to_line() + "\n")
    except OSError:
        raise StorageError("خطا در ذخیره‌سازی اطلاعات اشتراک روی دیسک.") from None

def _read_subscription_lines():
    """خواندن تمام خطوط فایل اشتراک‌ها؛ در صورت عدم وجود فایل، لیست خالی برمی‌گرداند"""
    if not os.path.exists(subscription_file_path):
        return []
    try:
        with open(subscription_file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        raise StorageError("خطا در خواندن فایل اشتراک‌ها از روی دیسک.") from None

def _load_subscriptions(strict=False):
    """بارگذاری تمام اشتراک‌های ذخیره‌شده با قابلیت کنترل strict"""
    lines = _read_subscription_lines()
    subscriptions = []
    for idx, line in enumerate(lines, start=1):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        try:
            sub = Subscription.from_line(line_stripped)
            subscriptions.append(sub)
        except ValueError:
            if strict:
                raise StorageError(f"خطای داده‌های ذخیره‌شده در شماره خط {idx}: فرمت خط اشتراک نامعتبر است.") from None
            continue            
    return subscriptions

def _load_paid_subscriptions():
    """
    فقط اشتراک‌های «پرداخت‌شده»: ردیفی که تراکنش subscription با همان شماره پیگیری دارد.
    تراکنش، نهایی‌کننده‌ی خرید است؛ ردیف معلق (بدون تراکنش) نادیده گرفته می‌شود.
    خواندن سخت‌گیرانه است: ردیف خراب خطا با شماره‌ی خط می‌دهد و بی‌صدا حذف نمی‌شود.
    """
    paid_codes = {tx.tracking_code for tx in get_all_transactions(strict=True)
                  if tx.transaction_type == "subscription"}
    return [sub for sub in _load_subscriptions(strict=True) if sub.tracking_code in paid_codes]
  
def _resolve_today(today):
    if today is None:
        return date.today()
    if type(today) is not date:
        raise ValueError("تاریخ امروز باید از نوع date باشد.")
    return today
 
def _clean_username(username):
    if not isinstance(username, str) or not username.strip():
        raise ValueError("نام کاربری نامعتبر است.")
    return username.strip()

def get_plans():
    """دریافت دیکشنری کاتالوگ طرح‌های اشتراک"""
    return subscription_plans

def get_plan(months):
    """دریافت طرح اشتراک بر اساس تعداد ماه با ولیدیشن دقیق نوع داده"""
    if isinstance(months, bool) or not isinstance(months, int):
        raise ValueError("تعداد ماه‌های اشتراک باید یک عدد صحیح باشد.")
    if months not in subscription_plans:
        raise ValueError(f"طرح اشتراکی برای مدت {months} ماه وجود ندارد.")
    return subscription_plans[months]

def set_plan(months, price):
    """ثبت یا ویرایش طرح اشتراک توسط مدیر (نوع و مبلغ)"""
    plan = SubscriptionPlan(months, price)   # اعتبارسنجی مدل: ValueError برای ماه یا قیمت نامعتبر
    subscription_plans[months] = plan
    return plan

def get_user_subscriptions(username):
    """دریافت اشتراک‌های پرداخت‌شده‌ی یک کاربر"""
    username = _clean_username(username)
    return [sub for sub in _load_paid_subscriptions() if sub.username == username]

def get_latest_subscription(username):
    """دریافت آخرین اشتراک کاربر بر اساس تاریخ پایان (بزرگ‌ترین end_date)"""
    user_subs = get_user_subscriptions(username)
    if not user_subs:
        return None
    return max(user_subs, key=lambda s: s.end_date)

def get_subscription_state(username, today=None):
    """وضعیت اشتراک کاربر: 'active' یا 'expired' یا 'none'"""
    today = _resolve_today(today)
    user_subs = get_user_subscriptions(username)
    if not user_subs:
        return "none"
    if any(sub.is_active(today) for sub in user_subs):
        return "active"
    return "expired"

def has_active_subscription(username, today=None):
    """آیا کاربر در این روز اشتراک فعال دارد؟ (برای ثبت‌نام کلاس)"""
    return get_subscription_state(username, today) == "active"
 
def get_current_subscription(username, today=None):
    """برای پروفایل: اشتراک فعال امروز، وگرنه آخرین اشتراک؛ بدون اشتراک: None"""
    today = _resolve_today(today)
    user_subs = get_user_subscriptions(username)
    if not user_subs:
        return None
    active = [sub for sub in user_subs if sub.is_active(today)]
    if active:
        return max(active, key=lambda s: s.end_date)
    return max(user_subs, key=lambda s: s.end_date)
 
def get_days_left(username, today=None):
    """روزهای باقی‌مانده‌ی اشتراک فعال (برای اشتراک غیرفعال: ۰)"""
    today = _resolve_today(today)
    active = [sub for sub in get_user_subscriptions(username) if sub.is_active(today)]
    if not active:
        return 0
    return max(active, key=lambda s: s.end_date).days_left(today)

def buy_subscription(username, months, today=None):
    """خرید یا تمدید اشتراک با رعایت کامل اصول ایمنی مالی و Idempotency"""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("نام کاربری نامعتبر است.")
    username = username.strip()
    if today is not None and type(today) is not date:
        raise ValueError("تاریخ امروز باید از نوع date باشد.")
    plan = get_plan(months)
    wallet = get_wallet(username)
    if not wallet.has_enough(plan.price):
        raise InsufficientBalanceError(f"موجودی کیف پول برای خرید این اشتراک کافی نیست. موجودی: {wallet.balance}, مبلغ: {plan.price}")
    latest_sub = get_latest_subscription(username)
    start_date = next_start_date(latest_sub, today)
    description = f"خرید اشتراک {plan.title}"
    if "|" in description or "\n" in description or "\r" in description:
        raise ValueError("توضیحات تراکنش شامل کاراکترهای غیرمجاز است.")
    tx = Transaction(username=username, transaction_type="subscription", amount=plan.price, description=description)
    existing_subs = _load_subscriptions(strict=False)
    existing_txs = get_all_transactions()
    matching_tx = next((t for t in existing_txs if t.tracking_code == tx.tracking_code), None)
    matching_sub = next((s for s in existing_subs if s.tracking_code == tx.tracking_code), None)
    if matching_sub:
        return matching_sub
    wallet.withdraw(plan.price)
    if not matching_tx:
        try:
            record_transaction(tx)
        except Exception:
            raise StorageError("خطا در ثبت تراکنش خرید اشتراک روی دیسک.") from None
    try:
        if not matching_sub:
            sub = Subscription(username=username, months=months, amount=plan.price, start_date=start_date, tracking_code=tx.tracking_code, payment_date=today if today is not None else date.today())
            _append_subscription(sub)
        else:
            sub = matching_sub
    except StorageError:        
        current_subs = _load_subscriptions(strict=False)
        already_saved = any(s.tracking_code == tx.tracking_code for s in current_subs)        
        if already_saved:

            pass
        else:
            raise StorageError(f"پرداخت انجام شد ولی اشتراک ثبت نشد، شماره پیگیری: {tx.tracking_code}") from None
    return sub

def get_all_subscriptions():
    """همه‌ی اشتراک‌های پرداخت‌شده (برای گزارش‌ها)"""
    return _load_paid_subscriptions()
  
def get_all_subscription_payments():
    """همه‌ی تراکنش‌های مربوط به خرید اشتراک"""
    return [tx for tx in get_all_transactions(strict=True) if tx.transaction_type == "subscription"]
 
def get_payments_report():
    """گزارش پرداخت‌های اشتراک؛ جدیدترین پرداخت اول. نام واقعی عضو را پنل مدیر از ماژول کاربران اضافه می‌کند."""
    subs = sorted(_load_paid_subscriptions(), key=lambda s: (s.payment_date, s.tracking_code), reverse=True)
    return [ {"username": s.username, "plan": month_to_persian.get(s.months, ""), "months": s.months, "amount": s.amount, "payment_date": s.payment_date, "start_date": s.start_date, "end_date": s.end_date, "tracking_code": s.tracking_code,} for s in subs]
  
def get_members_status(usernames, today=None):
    """وضعیت اشتراک هر عضو؛ فهرست نام‌ها را پنل مدیر می‌دهد (عضو بدون خرید: 'none')"""
    today = _resolve_today(today)
    if not isinstance(usernames, (list, tuple, set)):
        raise ValueError("فهرست نام‌های کاربری باید لیست باشد.")
    cleaned = [_clean_username(u) for u in usernames]
    paid = _load_paid_subscriptions()
    result = {}
    for username in cleaned:
        user_subs = [s for s in paid if s.username == username]
        if not user_subs:
            result[username] = "none"
        elif any(s.is_active(today) for s in user_subs):
            result[username] = "active"
        else:
            result[username] = "expired"
    return result
 
def get_total_revenue():
    """کل درآمد حاصل از فروش اشتراک‌ها (جمع اشتراک‌های پرداخت‌شده)"""
    return sum(sub.amount for sub in _load_paid_subscriptions())
 
def get_revenue_by_type():
    """درآمد به تفکیک نوع اشتراک: {تعداد ماه: جمع مبلغ}"""
    revenue = {}
    for sub in _load_paid_subscriptions():
        revenue[sub.months] = revenue.get(sub.months, 0) + sub.amount
    return revenue
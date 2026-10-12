import os
from datetime import date
from src.models.subscription import Subscription, SubscriptionPlan, next_start_date
from src.models.transaction import Transaction
from src.models.wallet import InsufficientBalanceError
from src.member.wallet_manager import get_wallet, record_transaction, StorageError, get_transactions

# constants and paths
current_dir = os.path.abspath(os.path.dirname(__file__))
subscription_file_path = os.path.normpath(os.path.join(current_dir, "../../data/subscriptions.txt"))

# subscription plans
subscription_plans = {
    1: SubscriptionPlan(months=1, price=100000),
    3: SubscriptionPlan(months=3, price=250000),
    6: SubscriptionPlan(months=6, price=450000)}

# Functions for saving and reading the subscriptions file
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

# Read all lines from the subscriptions file; returns an empty list if the file does not exist
def _read_subscription_lines():
    """خواندن تمام خطوط فایل اشتراک‌ها؛ در صورت عدم وجود فایل، لیست خالی برمی‌گرداند"""
    if not os.path.exists(subscription_file_path):
        return []
    try:
        with open(subscription_file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        raise StorageError("خطا در خواندن فایل اشتراک‌ها از روی دیسک.") from None

# Load all saved subscriptions with strict control capability
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

# loading Subscription Plans Catalog Dictionary
def get_plans():
    """دریافت دیکشنری کاتالوگ طرح‌های اشتراک"""
    return subscription_plans

# Retrieve subscription plan based on the number of months, with strict data type validation.
def get_plan(months):
    """دریافت طرح اشتراک بر اساس تعداد ماه با ولیدیشن دقیق نوع داده"""
    if isinstance(months, bool) or not isinstance(months, int):
        raise ValueError("تعداد ماه‌های اشتراک باید یک عدد صحیح باشد.")
    if months not in subscription_plans:
        raise ValueError(f"طرح اشتراکی برای مدت {months} ماه وجود ندارد.")
    return subscription_plans[months]

# getting the list of one user's subscriptions
def get_user_subscriptions(username):
    """دریافت لیست اشتراک‌های متعلق به یک کاربر خاص"""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("نام کاربری نامعتبر است.")
    username = username.strip()
    all_subs = _load_subscriptions(strict=False)
    return [sub for sub in all_subs if sub.username == username]

# getting the last subscription of user based on the end-date
def get_latest_subscription(username):
    """دریافت آخرین اشتراک کاربر بر اساس تاریخ پایان (بزرگ‌ترین end_date)"""
    user_subs = get_user_subscriptions(username)
    if not user_subs:
        return None
    return max(user_subs, key=lambda s: s.end_date)

# status and left-days functions
def get_subscription_status(username, today=None):
    """بررسی وضعیت اشتراک‌های کاربر (active، expired یا none)"""
    if today is not None and type(today) is not date:
        raise ValueError("تاریخ امروز باید از نوع date باشد.")
    user_subs = get_user_subscriptions(username)
    if not user_subs:
        return "none"
    if any(sub.is_active(today) for sub in user_subs):
        return "active"
    return "expired"

# calculating left days of active subscription
def get_days_left(username, today=None):
    """محاسبه تعداد روزهای باقی‌مانده از فعال‌ترین اشتراک"""
    if today is not None and type(today) is not date:
        raise ValueError("تاریخ امروز باید از نوع date باشد.")
    if get_subscription_status(username, today) != "active":
        return 0
    user_subs = get_user_subscriptions(username)
    active_subs = [sub for sub in user_subs if sub.is_active(today)]

    if not active_subs:
        return 0
    latest_active = max(active_subs, key=lambda s: s.end_date)
    return latest_active.days_left(today)

# buy_subscription
def buy_subscription(username, months, today=None):
    """خرید یا تمدید اشتراک با کسر از کیف پول و ثبت تراکنش و اشتراک"""
    # username, date, and subscription plan validation
    if not isinstance(username, str) or not username.strip():
        raise ValueError("نام کاربری نامعتبر است.")
    username = username.strip()
    if today is not None and type(today) is not date:
        raise ValueError("تاریخ امروز باید از نوع date باشد.")
    plan = get_plan(months)
    # checking user's balance
    wallet = get_wallet(username)
    if not wallet.has_enough(plan.price):
        raise InsufficientBalanceError(f"موجودی کیف پول برای خرید این اشتراک کافی نیست. موجودی: {wallet.balance}, مبلغ: {plan.price}")
    # calculating the new start date (chain renewl)
    latest_sub = get_latest_subscription(username)
    start_date = next_start_date(latest_sub, today)
    # creating the transaction object
    description = f"خرید اشتراک {plan.title}"
    if "|" in description or "\n" in description or "\r" in description:
        raise ValueError("توضیحات تراکنش شامل کاراکترهای غیرمجاز است.")
    # Deducting from the wallet balance (by reducing the `wallet` object's balance or applying a transaction via the manager)
    # Note: The balance in `wallet_manager` is calculated based on transactions; therefore, recording a 'subscription' type transaction reduces the balance. 
    # To apply the deduction, the `wallet` object must perform the withdrawal:
    wallet.withdraw(plan.price)
    tx = Transaction(
        username=username, transaction_type="subscription", amount=plan.price, description=description, date=datetime_now_if_needed(today) # اگر نیاز به تاریخ پرداخت باشد در تراکنش ثبت می‌شود
    ) if False else Transaction(username=username, transaction_type="subscription", amount=plan.price, description=description)
    # creating the subscription object with the tracking code of transaction
    if today is None:
        today_val = date.today()
    else:
        today_val = today
    sub = Subscription(username=username, months=months, amount=plan.price, start_date=start_date, tracking_code=tx.tracking_code, payment_date=today_val)
    # recording transactions and subscriptions in files
    try:
        record_transaction(tx)
    except Exception:
        # If the transaction recording fails, we refund the deducted balance (or return a storage error).
        raise StorageError("خطا در ثبت تراکنش خرید اشتراک روی دیسک.") from None
    try:
        _append_subscription(sub)
    except StorageError:
        raise StorageError(f"پرداخت انجام شد ولی اشتراک ثبت نشد، شماره پیگیری: {tx.tracking_code}") from None
    return sub

# helper for setting date for transactions if needed
def datetime_now_if_needed(today):
    pass

# manager's reports
def get_all_transactions():
    """دریافت تمام تراکنش‌های ثبت‌شده در سیستم (جهت استفاده در گزارش‌های مالی)"""
    from src.member.wallet_manager import _load_transactions
    return _load_transactions(strict=False)

# getting all transactions related to purchasing subscriptions
def get_all_subscription_payments():
    """دریافت تمام تراکنش‌های مربوط به خرید اشتراک"""
    all_txs = get_all_transactions()
    return [tx for tx in all_txs if tx.transaction_type == "subscription"]

# whole income of selling subscriptons
def get_total_revenue():
    """محاسبه کل درآمد حاصل از فروش اشتراک‌ها"""
    sub_payments = get_all_subscription_payments()
    return sum(tx.amount for tx in sub_payments)
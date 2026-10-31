import os
from datetime import date, datetime,  time
from src.models.transaction import Transaction
from src.models.subscription import Subscription, SubscriptionPlan, next_start_date, month_to_english
from src.models.wallet import InsufficientBalanceError
from src.member.wallet_manager import (get_wallet, record_transaction, new_transaction, get_all_transactions, StorageError)

current_dir = os.path.abspath(os.path.dirname(__file__))
subscription_file_path = os.path.normpath(os.path.join(current_dir, "../../data/subscriptions.txt"))

subscription_plans = {
    1: SubscriptionPlan(months=1, price=100000),
    3: SubscriptionPlan(months=3, price=250000),
    6: SubscriptionPlan(months=6, price=450000)}

def _append_subscription(sub):
    """Append a subscription record using UTF-8."""
    if not isinstance(sub, Subscription):
        raise ValueError("Input must be a Subscription instance.")
    try:
        directory = os.path.dirname(subscription_file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(subscription_file_path, "a", encoding="utf-8") as f:
            f.write(sub.to_line() + "\n")
    except OSError:
        raise StorageError("Failed to save subscription data to disk.") from None

def _read_subscription_lines():
    """Read subscription records; return an empty list if the file is missing."""
    if not os.path.exists(subscription_file_path):
        return []
    try:
        with open(subscription_file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except OSError:
        raise StorageError("Failed to read subscription data from disk.") from None

def _load_subscriptions(strict=False):
    """Load stored subscriptions, optionally rejecting malformed records."""
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
                raise StorageError(f"Invalid saved subscription data on line {idx}: invalid record format.") from None
            continue
    return subscriptions

def _load_paid_subscriptions():
    """
    Only paid subscriptions: records with a matching subscription transaction.
    The transaction finalizes the purchase; pending records are ignored.
    Strict loading raises a line-numbered error for malformed records.
    """
    paid_codes = {tx.tracking_code for tx in get_all_transactions(strict=True)
                  if tx.transaction_type == "subscription"}
    return [sub for sub in _load_subscriptions(strict=True) if sub.tracking_code in paid_codes]

def _resolve_today(today):
    if today is None:
        return date.today()
    if type(today) is not date:
        raise ValueError("Today must be a date object.")
    return today

def _clean_username(username):
    if not isinstance(username, str) or not username.strip():
        raise ValueError("Invalid username.")
    return username.strip()

def get_plans():
    """Return the subscription plan catalog."""
    return subscription_plans

def get_plan(months):
    """Get a plan by duration with strict input validation."""
    if isinstance(months, bool) or not isinstance(months, int):
        raise ValueError("Subscription duration must be an integer number of months.")
    if months not in subscription_plans:
        raise ValueError(f"No subscription plan is available for {months} months.")
    return subscription_plans[months]

def set_plan(months, price):
    """Create or update a subscription plan (duration and price)."""
    plan = SubscriptionPlan(months, price)   # Model validation raises ValueError for invalid duration or price
    subscription_plans[months] = plan
    return plan

def get_user_subscriptions(username):
    """Return paid subscriptions for a user."""
    username = _clean_username(username)
    return [sub for sub in _load_paid_subscriptions() if sub.username == username]

def get_latest_subscription(username):
    """Get the user's most recent subscription by end date."""
    user_subs = get_user_subscriptions(username)
    if not user_subs:
        return None
    return max(user_subs, key=lambda s: s.end_date)

def get_subscription_state(username, today=None):
    """Return subscription status: 'active', 'expired', or 'none'."""
    today = _resolve_today(today)
    user_subs = get_user_subscriptions(username)
    if not user_subs:
        return "none"
    if any(sub.is_active(today) for sub in user_subs):
        return "active"
    return "expired"

def has_active_subscription(username, today=None):
    """Check for an active subscription on the specified day (class enrollment)."""
    return get_subscription_state(username, today) == "active"

def get_current_subscription(username, today=None):
    """For profiles, return today's active subscription, else latest or None."""
    today = _resolve_today(today)
    user_subs = get_user_subscriptions(username)
    if not user_subs:
        return None
    active = [sub for sub in user_subs if sub.is_active(today)]
    if active:
        return max(active, key=lambda s: s.end_date)
    return max(user_subs, key=lambda s: s.end_date)

def get_days_left(username, today=None):
    """Return days left on an active subscription (zero if inactive)."""
    today = _resolve_today(today)
    active = [sub for sub in get_user_subscriptions(username) if sub.is_active(today)]
    if not active:
        return 0
    return max(active, key=lambda s: s.end_date).days_left(today)

def buy_subscription(username, months, today=None):
    """Purchase or renew a subscription with safe pending-record handling."""
    if not isinstance(username, str) or not username.strip():
        raise ValueError("Invalid username.")
    username = username.strip()
    supplied_today = today is not None
    if supplied_today and type(today) is not date:
        raise ValueError("Today must be a date object.")
    if today is None:
        today = date.today()
    when = (
        datetime.combine(today, time.min)
        if supplied_today
        else datetime.now().replace(microsecond=0))
    plan = get_plan(months)
    all_subs = _load_subscriptions(strict=True)
    all_tx = get_all_transactions()
    paid_codes = {
        tx.tracking_code
        for tx in all_tx
        if tx.transaction_type == "subscription"}
    pending = next((
            s for s in all_subs
            if s.username == username
            and s.months == months
            and s.tracking_code not in paid_codes
        ), None)
    if pending is not None:
        sub = pending
        amount = sub.amount
        tx = Transaction(
            username=username,
            transaction_type="subscription",
            amount=amount,
            description=f"Subscription purchase: {plan.title}",
            tracking_code=sub.tracking_code,
            date=(
                datetime.combine(sub.payment_date, time.min)
                if supplied_today
                else when
            ))
    else:
        amount = plan.price
        latest = get_latest_subscription(username)
        start = next_start_date(latest, today)
        used_codes = {
            s.tracking_code for s in all_subs}
        tx = None
        for _ in range(10):
            temp_tx = Transaction(
                username=username,
                transaction_type="subscription",
                amount=amount,
                description=f"Subscription purchase: {plan.title}",
                date=when)
            if temp_tx.tracking_code not in used_codes:
                tx = temp_tx
                break
        else:
            raise StorageError("Could not generate a unique tracking code.")
        sub = Subscription(
            username=username,
            months=months,
            amount=amount,
            start_date=start,
            tracking_code=tx.tracking_code,
            payment_date=today)
    wallet = get_wallet(username)
    if not wallet.has_enough(amount):
        raise InsufficientBalanceError("Insufficient wallet balance.")
    if pending is None:
        try:
            _append_subscription(sub)
        except StorageError:
            persisted = next((s for s in _load_subscriptions(strict=True) if s.tracking_code == sub.tracking_code), None)
            if persisted is None:
                raise StorageError("Subscription could not be recorded; no amount was deducted.") from None
            sub = persisted
    try:
        record_transaction(tx)
    except StorageError:
        recorded = next((t for t in get_all_transactions() if t.tracking_code == tx.tracking_code), None)
        if recorded is None:
            raise StorageError(f"Purchase is pending and no amount was deducted. Tracking code: {tx.tracking_code}") from None
        if (recorded.username != username or recorded.transaction_type != "subscription" or recorded.amount != amount):
            raise StorageError("Tracking code conflicts with an unrelated transaction.")
    recorded = next((t for t in get_all_transactions() if t.tracking_code == tx.tracking_code), None)
    if (recorded is None or recorded.username != username or recorded.transaction_type != "subscription" or recorded.amount != amount):
        raise StorageError("Payment is not confirmed; do not pay again.")
    return sub

def get_all_subscriptions():
    """Return all paid subscriptions for reports."""
    return _load_paid_subscriptions()

def get_all_subscription_payments():
    """Return all subscription purchase transactions."""
    return [tx for tx in get_all_transactions(strict=True) if tx.transaction_type == "subscription"]

def get_payments_report():
    """Report subscription payments, newest first; admin adds member names."""
    subs = sorted(_load_paid_subscriptions(), key=lambda s: (s.payment_date, s.tracking_code), reverse=True)
    return [ {"username": s.username, "plan": month_to_english.get(s.months, ""), "months": s.months, "amount": s.amount, "payment_date": s.payment_date, "start_date": s.start_date, "end_date": s.end_date, "tracking_code": s.tracking_code,} for s in subs]

def get_members_status(usernames, today=None):
    """Return member statuses from admin-provided usernames ('none' if no purchase)."""
    today = _resolve_today(today)
    if not isinstance(usernames, (list, tuple, set)):
        raise ValueError("Usernames must be provided as a list, tuple, or set.")
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
    """Return total revenue from paid subscriptions."""
    return sum(sub.amount for sub in _load_paid_subscriptions())

def get_revenue_by_type():
    """Return revenue by duration: {months: total amount}."""
    revenue = {}
    for sub in _load_paid_subscriptions():
        revenue[sub.months] = revenue.get(sub.months, 0) + sub.amount
    return revenue
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from telegram_llm_chatbot.db.database import get_session
from telegram_llm_chatbot.db.models import Payment, Subscription, SubscriptionPlan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SubscriptionPlan CRUD operations

def create_subscription_plan(
    name: str,
    price: float, currency: str,
    duration_in_days: int,
    description: Optional[str] = None
    ) -> SubscriptionPlan:
    plan = SubscriptionPlan(
        name=name, description=description,
        price=price, currency=currency,
        duration_in_days=duration_in_days
    )
    db: Session = get_session()
    db.expire_on_commit = False
    db.add(plan)
    db.commit()
    db.close()
    return plan

def get_subscription_plan(plan_id: int) -> Optional[SubscriptionPlan]:
    db: Session = get_session()
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    db.close()
    return plan

def get_subscription_plans(plan_name: Optional[str] = None) -> Optional[list[SubscriptionPlan]]:
    db: Session = get_session()
    if plan_name:
        plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == plan_name).all()
    else:
        plans = db.query(SubscriptionPlan).all()
    db.close()
    return plans

def update_subscription_plan(
    plan_id: int,
    name: Optional[str]=None,
    description: Optional[str]=None,
    price: Optional[float]=None,
    currency: Optional[str]=None,
    duration_in_days: Optional[int]=None
    ) -> Optional[SubscriptionPlan]:
    db: Session = get_session()
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if plan:
        if name is not None:
            plan.name = name
        if description is not None:
            plan.description = description
        if price is not None:
            plan.price = price
        if currency is not None:
            plan.currency = currency
        if duration_in_days is not None:
            plan.duration_in_days = duration_in_days
        db.commit()
    db.close()
    return plan

def delete_subscription_plan(plan_id: int):
    db: Session = get_session()
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if plan:
        db.delete(plan)
        db.commit()
    db.close()

# Subscription CRUD operations
def create_subscription(user_id: int, plan_id: int, status: str = "active") -> Subscription:
    plan = get_subscription_plan(plan_id)
    if not plan:
        raise ValueError("Subscription plan not found")
    subscription = Subscription(
        user_id=user_id,
        plan_id=plan_id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=plan.duration_in_days),
        status=status
    )
    db: Session = get_session()
    db.expire_on_commit = False
    db.add(subscription)
    db.commit()
    db.close()
    return subscription

def get_subscriptions_by_user_id(user_id: int) -> Optional[list[Subscription]]:
    db: Session = get_session()
    subscriptions = db.query(Subscription).filter(Subscription.user_id == user_id)
    db.close()
    return subscriptions

def update_subscription(subscription_id: int, status: Optional[str]=None, end_date: Optional[datetime]=None) -> Optional[Subscription]:
    db: Session = get_session()
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if subscription:
        if status is not None:
            subscription.status = status
        if end_date is not None:
            subscription.end_date = end_date
        db.commit()
    db.close()
    return subscription

def get_active_subscriptions_by_user_id(user_id: int) -> Optional[list[Subscription]]:
    db: Session = get_session()

    # Fetch the subscriptions
    active_subscriptions = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .filter(Subscription.status.in_(["active"]))  # Relevant statuses
        .all()
    )

    db.commit()
    db.close()
    return active_subscriptions if active_subscriptions else None

def update_subscription_statuses(user_id: int) -> None:
    current_date = datetime.now()
    db: Session = get_session()
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).all()

    for subscription in subscriptions:
        if subscription.status == "active" and subscription.end_date < current_date:
            subscription.status = "inactive"
            logger.info(f"Subscription {subscription.id} has expired")
        elif subscription.status == "inactive" and subscription.end_date > current_date:
            subscription.status = "active"
            logger.info(f"Subscription {subscription.id} has been reactivated")

    db.commit()
    db.close()

def delete_subscription(subscription_id: int):
    db: Session = get_session()
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if subscription:
        db.delete(subscription)
        db.commit()
    db.close()

# Payment CRUD operations
def create_payment(
    subscription_id: int,
    amount: float,
    currency: str,
    payment_date: datetime,
    payment_method: str
    ) -> Payment:
    payment = Payment(
        subscription_id=subscription_id,
        amount=amount,
        currency=currency,
        payment_date=payment_date,
        payment_method=payment_method
    )
    db: Session = get_session()
    db.add(payment)
    db.commit()
    db.close()
    return payment

def get_payment(payment_id: int) -> Optional[Payment]:
    db: Session = get_session()
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    db.close()
    return payment

def update_payment(payment_id: int, amount: Optional[float]=None, payment_method: Optional[str]=None) -> Optional[Payment]:
    db: Session = get_session()
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment:
        if amount is not None:
            payment.amount = amount
        if payment_method is not None:
            payment.payment_method = payment_method
        db.commit()
    db.close()
    return payment

def delete_payment(payment_id: int):
    db: Session = get_session()
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment:
        db.delete(payment)
        db.commit()
    db.close()

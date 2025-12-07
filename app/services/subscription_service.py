"""
Cleaned & fixed SubscriptionService compatible with current subscription.py models.
All invalid imports and missing models have been removed.
"""

from __future__ import annotations

import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

from decimal import Decimal
from sqlmodel import Session, select, and_, func
from fastapi import HTTPException

from app.models.organization import Organization
from app.models.subscription import (
    Subscription, SubscriptionStatus, BillingCycle,
    Invoice, InvoiceStatus, InvoiceLineItem
)
from app.models.property import Property
from app.models.booking import Booking


class SubscriptionService:
    def __init__(self, session: Session):
        self.session = session

    # -------------------------------------
    # Create Subscription
    # -------------------------------------
    def create_subscription(
        self,
        organization_id: uuid.UUID,
        plan_name: str,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        trial_days: int = 14
    ) -> Subscription:

        # check existing subscription
        existing = self.session.exec(
            select(Subscription).where(Subscription.organization_id == organization_id)
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Organization already has subscription")

        # get plan config
        plan = self.get_plan_configuration(plan_name)

        # trial period
        trial_start = datetime.utcnow()
        trial_end = trial_start + timedelta(days=trial_days)

        # billing period
        current_period_start = trial_end
        current_period_end = self.calculate_period_end(current_period_start, billing_cycle)

        subscription = Subscription(
            organization_id=organization_id,
            plan_name=plan_name,
            billing_cycle=billing_cycle,
            base_price=plan["base_price"],
            currency=plan["currency"],
            status=SubscriptionStatus.TRIALING,
            trial_start=trial_start,
            trial_end=trial_end,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
            properties_limit=plan["properties_limit"],
            users_limit=plan["users_limit"],
            bookings_limit=plan.get("bookings_limit", None)
        )

        self.session.add(subscription)
        self.session.commit()
        self.session.refresh(subscription)

        return subscription

    # -------------------------------------
    # Plan Configuration
    # -------------------------------------
    def get_plan_configuration(self, plan_name: str) -> Dict[str, Any]:

        plans = {
            "FREE": {
                "base_price": Decimal("0.00"),
                "currency": "USD",
                "properties_limit": 1,
                "users_limit": 3,
                "bookings_limit": 50
            },
            "BASIC": {
                "base_price": Decimal("29.99"),
                "currency": "USD",
                "properties_limit": 5,
                "users_limit": 10,
                "bookings_limit": 500
            },
            "PROFESSIONAL": {
                "base_price": Decimal("99.99"),
                "currency": "USD",
                "properties_limit": 25,
                "users_limit": 50,
                "bookings_limit": 2000
            },
            "ENTERPRISE": {
                "base_price": Decimal("299.99"),
                "currency": "USD",
                "properties_limit": 999,
                "users_limit": 999,
                "bookings_limit": None  # unlimited
            }
        }

        if plan_name not in plans:
            raise HTTPException(status_code=400, detail=f"Invalid plan: {plan_name}")

        return plans[plan_name]

    # -------------------------------------
    def calculate_period_end(self, start_date: datetime, billing_cycle: BillingCycle) -> datetime:

        if billing_cycle == BillingCycle.MONTHLY:
            return start_date + timedelta(days=30)
        elif billing_cycle == BillingCycle.YEARLY:
            return start_date + timedelta(days=365)
        else:
            raise ValueError("Invalid billing cycle")

    # -------------------------------------
    # Get subscription
    # -------------------------------------
    def get_organization_subscription(self, organization_id: uuid.UUID):
        return self.session.exec(
            select(Subscription).where(Subscription.organization_id == organization_id)
        ).first()

    # -------------------------------------
    # Usage Limits
    # -------------------------------------
    def check_usage_limits(self, organization_id: uuid.UUID):

        subscription = self.get_organization_subscription(organization_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # count properties
        properties_used = self.session.exec(
            select(func.count(Property.id)).where(
                Property.organization_id == organization_id,
                Property.is_active == True
            )
        ).first() or 0

        # count bookings of this billing period
        bookings_used = self.session.exec(
            select(func.count(Booking.id)).where(
                Booking.created_at >= subscription.current_period_start,
                Booking.created_at < subscription.current_period_end,
                Booking.property_id.in_(
                    select(Property.id).where(Property.organization_id == organization_id)
                ),
            )
        ).first() or 0

        return {
            "properties": {
                "used": properties_used,
                "limit": subscription.properties_limit
            },
            "users": {
                "used": 0,
                "limit": subscription.users_limit
            },
            "bookings": {
                "used": bookings_used,
                "limit": subscription.bookings_limit
            }
        }

    # -------------------------------------
    def can_create_property(self, org_id: uuid.UUID) -> bool:
        usage = self.check_usage_limits(org_id)
        return usage["properties"]["used"] < usage["properties"]["limit"]

    def can_add_user(self, org_id: uuid.UUID) -> bool:
        usage = self.check_usage_limits(org_id)
        return usage["users"]["used"] < usage["users"]["limit"]

    def can_create_booking(self, org_id: uuid.UUID) -> bool:
        usage = self.check_usage_limits(org_id)
        limit = usage["bookings"]["limit"]
        return limit is None or usage["bookings"]["used"] < limit

    # -------------------------------------
    # Invoice
    # -------------------------------------
    def generate_invoice(self, subscription_id: uuid.UUID, period_start: date, period_end: date):

        subscription = self.session.get(Subscription, subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # invoice number
        count = self.session.exec(
            select(func.count(Invoice.id)).where(Invoice.organization_id == subscription.organization_id)
        ).first() or 0

        invoice_number = f"INV-{subscription.organization_id.hex[:8]}-{count+1:04d}".upper()

        invoice = Invoice(
            organization_id=subscription.organization_id,
            subscription_id=subscription.id,
            invoice_number=invoice_number,
            status=InvoiceStatus.OPEN,
            subtotal=subscription.base_price,
            tax_amount=Decimal("0.00"),
            total_amount=subscription.base_price,
            currency=subscription.currency,
            due_date=date.today() + timedelta(days=30),
            period_start=period_start,
            period_end=period_end
        )

        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)

        # line item
        line = InvoiceLineItem(
            invoice_id=invoice.id,
            description=f"{subscription.plan_name} Plan ({period_start} → {period_end})",
            item_type="SUBSCRIPTION",
            quantity=1,
            unit_price=subscription.base_price,
            total_price=subscription.base_price
        )

        self.session.add(line)
        self.session.commit()

        return invoice

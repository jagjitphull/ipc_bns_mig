"""
Stripe Integration Service for Payment Processing
Handles subscription creation, upgrades, and webhook events
"""

import stripe
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from auth_models import User, Subscription, PaymentHistory, SubscriptionTier, SubscriptionStatus

# Initialize Stripe with API key from environment
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')

# Pricing configuration (in paise for INR)
SUBSCRIPTION_PRICES = {
    SubscriptionTier.PROFESSIONAL: {
        'amount': 299900,  # ₹2,999 in paise
        'currency': 'inr',
        'interval': 'month'
    },
    SubscriptionTier.ENTERPRISE: {
        'amount': 4999900,  # ₹49,999 in paise
        'currency': 'inr',
        'interval': 'month'
    }
}

class StripeService:
    """Service for handling Stripe payment operations"""

    @staticmethod
    def create_checkout_session(
        user: User,
        tier: SubscriptionTier,
        success_url: str,
        cancel_url: str,
        db: Session
    ) -> Optional[str]:
        """
        Create a Stripe checkout session for subscription

        Args:
            user: User subscribing
            tier: Subscription tier to purchase
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled
            db: Database session

        Returns:
            Checkout session URL or None if Stripe not configured
        """

        # Check if Stripe is configured
        if not stripe.api_key or stripe.api_key == '':
            print("WARNING: Stripe API key not configured")
            return None

        try:
            # Get pricing info
            price_info = SUBSCRIPTION_PRICES.get(tier)
            if not price_info:
                raise ValueError(f"No pricing configured for tier: {tier}")

            # Create or retrieve Stripe customer
            if not user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=user.full_name,
                    metadata={
                        'user_id': user.id,
                        'role': user.role.value
                    }
                )
                user.stripe_customer_id = customer.id
                db.commit()

            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': price_info['currency'],
                        'unit_amount': price_info['amount'],
                        'recurring': {
                            'interval': price_info['interval']
                        },
                        'product_data': {
                            'name': f'{tier.value.title()} Plan',
                            'description': f'IPC/BNS Legal Reasoning Agent - {tier.value.title()} Subscription',
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'user_id': user.id,
                    'tier': tier.value
                },
                subscription_data={
                    'metadata': {
                        'user_id': user.id,
                        'tier': tier.value
                    },
                    # Start with 14-day trial for new subscriptions
                    'trial_period_days': 14 if tier == SubscriptionTier.PROFESSIONAL else 0
                }
            )

            return session.url

        except stripe.error.StripeError as e:
            print(f"Stripe error creating checkout session: {e}")
            return None
        except Exception as e:
            print(f"Error creating checkout session: {e}")
            return None

    @staticmethod
    def handle_checkout_complete(
        session_id: str,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """
        Handle successful checkout session completion

        Args:
            session_id: Stripe checkout session ID
            db: Database session

        Returns:
            Dictionary with subscription details or None
        """

        if not stripe.api_key or stripe.api_key == '':
            return None

        try:
            # Retrieve the session
            session = stripe.checkout.Session.retrieve(
                session_id,
                expand=['subscription']
            )

            if session.payment_status != 'paid':
                return None

            # Get user and tier from metadata
            user_id = int(session.metadata.get('user_id'))
            tier = SubscriptionTier(session.metadata.get('tier'))

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            # Update subscription
            subscription = user.subscription
            if not subscription:
                subscription = Subscription(user_id=user.id)
                db.add(subscription)

            subscription.tier = tier
            subscription.status = SubscriptionStatus.TRIAL if session.subscription.trial_end else SubscriptionStatus.ACTIVE
            subscription.stripe_subscription_id = session.subscription.id
            subscription.stripe_customer_id = session.customer

            # Set billing dates
            if session.subscription.trial_end:
                subscription.trial_ends_at = datetime.fromtimestamp(session.subscription.trial_end)

            subscription.current_period_start = datetime.fromtimestamp(session.subscription.current_period_start)
            subscription.current_period_end = datetime.fromtimestamp(session.subscription.current_period_end)

            # Set limits based on tier
            StripeService._update_subscription_limits(subscription, tier)

            # Record payment
            payment = PaymentHistory(
                user_id=user.id,
                amount=session.amount_total / 100,  # Convert from paise to rupees
                currency='INR',
                status='succeeded',
                stripe_payment_intent_id=session.payment_intent,
                payment_method='card'
            )
            db.add(payment)

            db.commit()

            return {
                'success': True,
                'tier': tier.value,
                'trial_ends': subscription.trial_ends_at.isoformat() if subscription.trial_ends_at else None,
                'next_billing': subscription.current_period_end.isoformat()
            }

        except stripe.error.StripeError as e:
            print(f"Stripe error handling checkout: {e}")
            return None
        except Exception as e:
            print(f"Error handling checkout completion: {e}")
            return None

    @staticmethod
    def cancel_subscription(user: User, db: Session) -> bool:
        """
        Cancel user's Stripe subscription

        Args:
            user: User whose subscription to cancel
            db: Database session

        Returns:
            True if cancelled successfully, False otherwise
        """

        if not stripe.api_key or stripe.api_key == '':
            return False

        try:
            subscription = user.subscription
            if not subscription or not subscription.stripe_subscription_id:
                return False

            # Cancel at period end (user keeps access until then)
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )

            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()
            db.commit()

            return True

        except stripe.error.StripeError as e:
            print(f"Stripe error cancelling subscription: {e}")
            return False
        except Exception as e:
            print(f"Error cancelling subscription: {e}")
            return False

    @staticmethod
    def _update_subscription_limits(subscription: Subscription, tier: SubscriptionTier):
        """Update subscription limits based on tier"""

        if tier == SubscriptionTier.FREE:
            subscription.section_analyses_limit = 10
            subscription.memo_generation_limit = 5
            subscription.case_search_daily_limit = 3
            subscription.api_calls_daily_limit = 0

        elif tier == SubscriptionTier.PROFESSIONAL:
            subscription.section_analyses_limit = -1  # Unlimited
            subscription.memo_generation_limit = 50
            subscription.case_search_daily_limit = -1  # Unlimited
            subscription.api_calls_daily_limit = 100

        elif tier == SubscriptionTier.ENTERPRISE:
            subscription.section_analyses_limit = -1  # Unlimited
            subscription.memo_generation_limit = -1  # Unlimited
            subscription.case_search_daily_limit = -1  # Unlimited
            subscription.api_calls_daily_limit = -1  # Unlimited

        # Reset usage counters
        subscription.section_analyses_used = 0
        subscription.memo_generation_used = 0
        subscription.case_search_used = 0
        subscription.api_calls_used = 0

    @staticmethod
    def handle_webhook(payload: bytes, sig_header: str) -> Optional[Dict[str, Any]]:
        """
        Handle Stripe webhook events

        Args:
            payload: Raw request body
            sig_header: Stripe signature header

        Returns:
            Event data if processed successfully
        """

        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        if not webhook_secret:
            print("WARNING: Stripe webhook secret not configured")
            return None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )

            # Handle different event types
            if event.type == 'checkout.session.completed':
                session = event.data.object
                # Checkout completion is handled separately
                return {'event': 'checkout_completed', 'session_id': session.id}

            elif event.type == 'invoice.payment_succeeded':
                invoice = event.data.object
                return {'event': 'payment_succeeded', 'amount': invoice.amount_paid}

            elif event.type == 'invoice.payment_failed':
                invoice = event.data.object
                return {'event': 'payment_failed', 'customer': invoice.customer}

            elif event.type == 'customer.subscription.deleted':
                subscription = event.data.object
                return {'event': 'subscription_deleted', 'subscription_id': subscription.id}

            return {'event': event.type}

        except ValueError as e:
            print(f"Invalid webhook payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            print(f"Invalid webhook signature: {e}")
            return None

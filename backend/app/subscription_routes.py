"""
Subscription management and usage tracking routes
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from auth_models import (
    User, Subscription, UsageLog, SavedAnalysis,
    SubscriptionTier, SubscriptionStatus, get_subscription_limits
)
from auth_routes import get_current_user

router = APIRouter(prefix="/subscription", tags=["subscription"])


# Pydantic models
class SubscriptionInfo(BaseModel):
    tier: str
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    trial_ends_at: Optional[datetime]

    # Usage limits
    section_analyses_limit: int
    memo_generation_limit: int
    case_search_limit: int
    api_calls_limit: int

    # Current usage
    section_analyses_used: int
    memo_generation_used: int
    case_search_used: int
    api_calls_used: int

    # Remaining
    section_analyses_remaining: int
    memo_generation_remaining: int
    case_search_remaining: int
    api_calls_remaining: int

    class Config:
        from_attributes = True


class UsageStats(BaseModel):
    total_analyses: int
    total_memos: int
    total_searches: int
    total_api_calls: int
    usage_by_day: List[dict]


class UpgradeRequest(BaseModel):
    tier: SubscriptionTier
    payment_method_id: Optional[str] = None  # Stripe payment method ID


# Helper functions
def check_usage_limit(user: User, action_type: str, db: Session) -> bool:
    """
    Check if user has exceeded usage limits

    Args:
        user: User object
        action_type: 'section_analysis', 'memo_generation', 'case_search', 'api_call'
        db: Database session

    Returns:
        True if within limits, False if exceeded
    """
    subscription = user.subscription

    if not subscription:
        return False

    # Check if monthly usage needs to be reset
    if subscription.last_reset_date:
        days_since_reset = (datetime.utcnow() - subscription.last_reset_date).days
        if days_since_reset >= 30:
            # Reset monthly counters
            subscription.section_analyses_used = 0
            subscription.memo_generation_used = 0
            subscription.api_calls_used = 0
            subscription.last_reset_date = datetime.utcnow()
            db.commit()

    # Check limits
    limit_mapping = {
        'section_analysis': (subscription.section_analyses_limit, subscription.section_analyses_used),
        'memo_generation': (subscription.memo_generation_limit, subscription.memo_generation_used),
        'case_search': (subscription.case_search_limit, subscription.case_search_used),
        'api_call': (subscription.api_calls_limit, subscription.api_calls_used)
    }

    if action_type not in limit_mapping:
        return False

    limit, used = limit_mapping[action_type]

    # -1 means unlimited
    if limit == -1:
        return True

    return used < limit


def increment_usage(user: User, action_type: str, db: Session):
    """Increment usage counter for an action"""
    subscription = user.subscription

    if not subscription:
        return

    if action_type == 'section_analysis':
        subscription.section_analyses_used += 1
    elif action_type == 'memo_generation':
        subscription.memo_generation_used += 1
    elif action_type == 'case_search':
        subscription.case_search_used += 1
    elif action_type == 'api_call':
        subscription.api_calls_used += 1

    db.commit()


# Routes

@router.get("/info", response_model=SubscriptionInfo)
async def get_subscription_info(current_user: User = Depends(get_current_user)):
    """Get current subscription information"""
    subscription = current_user.subscription

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    return SubscriptionInfo(
        tier=subscription.tier.value,
        status=subscription.status.value,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        trial_ends_at=subscription.trial_ends_at,
        section_analyses_limit=subscription.section_analyses_limit,
        memo_generation_limit=subscription.memo_generation_limit,
        case_search_limit=subscription.case_search_limit,
        api_calls_limit=subscription.api_calls_limit,
        section_analyses_used=subscription.section_analyses_used,
        memo_generation_used=subscription.memo_generation_used,
        case_search_used=subscription.case_search_used,
        api_calls_used=subscription.api_calls_used,
        section_analyses_remaining=max(0, subscription.section_analyses_limit - subscription.section_analyses_used) if subscription.section_analyses_limit != -1 else -1,
        memo_generation_remaining=max(0, subscription.memo_generation_limit - subscription.memo_generation_used) if subscription.memo_generation_limit != -1 else -1,
        case_search_remaining=max(0, subscription.case_search_limit - subscription.case_search_used) if subscription.case_search_limit != -1 else -1,
        api_calls_remaining=max(0, subscription.api_calls_limit - subscription.api_calls_used) if subscription.api_calls_limit != -1 else -1
    )


@router.get("/usage", response_model=UsageStats)
async def get_usage_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get usage statistics for the last N days"""

    since_date = datetime.utcnow() - timedelta(days=days)

    # Get usage logs
    logs = db.query(UsageLog).filter(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= since_date
    ).all()

    # Count by type
    total_analyses = len([l for l in logs if l.action_type == 'section_analysis'])
    total_memos = len([l for l in logs if l.action_type == 'memo_generation'])
    total_searches = len([l for l in logs if l.action_type == 'case_search'])
    total_api_calls = len([l for l in logs if l.action_type == 'api_call'])

    # Group by day
    usage_by_day = {}
    for log in logs:
        day = log.timestamp.date().isoformat()
        if day not in usage_by_day:
            usage_by_day[day] = {
                'date': day,
                'analyses': 0,
                'memos': 0,
                'searches': 0,
                'api_calls': 0
            }

        if log.action_type == 'section_analysis':
            usage_by_day[day]['analyses'] += 1
        elif log.action_type == 'memo_generation':
            usage_by_day[day]['memos'] += 1
        elif log.action_type == 'case_search':
            usage_by_day[day]['searches'] += 1
        elif log.action_type == 'api_call':
            usage_by_day[day]['api_calls'] += 1

    return UsageStats(
        total_analyses=total_analyses,
        total_memos=total_memos,
        total_searches=total_searches,
        total_api_calls=total_api_calls,
        usage_by_day=list(usage_by_day.values())
    )


@router.post("/upgrade")
async def upgrade_subscription(
    upgrade_data: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade subscription tier with Stripe checkout"""

    from stripe_service import StripeService

    subscription = current_user.subscription

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    old_tier = subscription.tier
    new_tier = upgrade_data.tier

    if old_tier == new_tier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already on this tier"
        )

    # Check if upgrading (not downgrading)
    tier_order = {SubscriptionTier.FREE: 0, SubscriptionTier.PROFESSIONAL: 1, SubscriptionTier.ENTERPRISE: 2}
    if tier_order.get(new_tier, 0) < tier_order.get(old_tier, 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot downgrade tiers. Please cancel your current subscription first."
        )

    # Create Stripe checkout session
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    success_url = f"{frontend_url}/profile?payment=success"
    cancel_url = f"{frontend_url}/pricing?payment=cancelled"

    checkout_url = StripeService.create_checkout_session(
        user=current_user,
        tier=new_tier,
        success_url=success_url,
        cancel_url=cancel_url,
        db=db
    )

    if not checkout_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe payment service is not configured. Please contact support."
        )

    return {
        "checkout_url": checkout_url,
        "tier": new_tier.value,
        "message": "Redirecting to checkout..."
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription with Stripe (will remain active until end of billing period)"""

    from stripe_service import StripeService

    subscription = current_user.subscription

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )

    if subscription.status == SubscriptionStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription already cancelled"
        )

    # Cancel on Stripe
    success = StripeService.cancel_subscription(current_user, db)

    if not success:
        # If Stripe not configured or error, cancel locally
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        db.commit()

    return {
        "message": "Subscription cancelled. Access will continue until end of billing period.",
        "access_until": subscription.current_period_end.isoformat() if subscription.current_period_end else None
    }


@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans and pricing"""
    return {
        "plans": [
            {
                "tier": "free",
                "name": "Free",
                "price": 0,
                "currency": "INR",
                "billing": "forever",
                "features": [
                    "10 section analyses per month",
                    "5 memo generations per month",
                    "3 case searches per day",
                    "Basic case law access",
                    "Watermarked PDF exports"
                ],
                "limits": get_subscription_limits(SubscriptionTier.FREE)
            },
            {
                "tier": "professional",
                "name": "Professional",
                "price": 2999,
                "currency": "INR",
                "billing": "monthly",
                "popular": True,
                "features": [
                    "Unlimited section analyses",
                    "50 memos per month",
                    "Unlimited case searches",
                    "Advanced search filters",
                    "Save and organize research",
                    "Export without watermarks",
                    "API access (100 calls/day)",
                    "Email alerts",
                    "Priority support"
                ],
                "limits": get_subscription_limits(SubscriptionTier.PROFESSIONAL)
            },
            {
                "tier": "enterprise",
                "name": "Enterprise",
                "price": 49999,
                "currency": "INR",
                "billing": "monthly (25 users)",
                "features": [
                    "Everything in Professional",
                    "Unlimited memos",
                    "Unlimited API access",
                    "Team collaboration",
                    "Custom branding",
                    "Dedicated account manager",
                    "SLA guarantees (99.9%)",
                    "White-label option",
                    "Custom integrations",
                    "On-premise deployment"
                ],
                "limits": get_subscription_limits(SubscriptionTier.ENTERPRISE)
            }
        ]
    }

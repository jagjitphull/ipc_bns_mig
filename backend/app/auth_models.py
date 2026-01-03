"""
Authentication and User Management Models
Extends the database with user, subscription, and usage tracking tables
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum

from database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    LAWYER = "lawyer"
    RESEARCHER = "researcher"
    STUDENT = "student"
    ENTERPRISE = "enterprise"


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    SUSPENDED = "suspended"


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile information
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    bar_council_id = Column(String(100), nullable=True)
    organization = Column(String(255), nullable=True)

    # Role and status
    role = Column(SQLEnum(UserRole), default=UserRole.LAWYER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)

    # Authentication
    verification_token = Column(String(255), nullable=True)
    reset_password_token = Column(String(255), nullable=True)
    reset_password_expires = Column(DateTime, nullable=True)

    # Metadata
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    usage_logs = relationship("UsageLog", back_populates="user")
    saved_analyses = relationship("SavedAnalysis", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")


class Subscription(Base):
    """Subscription model for managing user subscriptions"""
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)

    # Subscription details
    tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.TRIAL, nullable=False)

    # Billing
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)

    # Limits (per month)
    section_analyses_limit = Column(Integer, default=10)  # Free: 10, Pro: -1 (unlimited)
    memo_generation_limit = Column(Integer, default=5)    # Free: 5, Pro: 50
    case_search_limit = Column(Integer, default=3)        # Free: 3/day, Pro: -1
    api_calls_limit = Column(Integer, default=0)          # Free: 0, Pro: 100/day

    # Usage counters (reset monthly)
    section_analyses_used = Column(Integer, default=0)
    memo_generation_used = Column(Integer, default=0)
    case_search_used = Column(Integer, default=0)
    api_calls_used = Column(Integer, default=0)

    # Billing cycle reset
    last_reset_date = Column(DateTime, default=datetime.utcnow)

    # Trial
    trial_ends_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")


class UsageLog(Base):
    """Track usage for analytics and billing"""
    __tablename__ = 'usage_logs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Usage details
    action_type = Column(String(50), nullable=False)  # 'section_analysis', 'memo_generation', 'case_search', 'api_call'
    resource_id = Column(String(100), nullable=True)  # e.g., IPC section number, case ID

    # Request details
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Response
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=True)

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_logs")


class SavedAnalysis(Base):
    """Save user's section analyses and memos for future reference"""
    __tablename__ = 'saved_analyses'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Analysis details
    title = Column(String(255), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # 'section', 'memo', 'case_search'

    # Content
    query = Column(Text, nullable=False)  # Original query/sections
    result = Column(Text, nullable=False)  # JSON of analysis result

    # Organization
    folder = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    notes = Column(Text, nullable=True)

    # Sharing
    is_public = Column(Boolean, default=False)
    share_token = Column(String(100), nullable=True, unique=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="saved_analyses")


class APIKey(Base):
    """API keys for programmatic access"""
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Key details
    key = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)  # User-defined name

    # Permissions
    scopes = Column(Text, nullable=True)  # JSON array of allowed scopes

    # Rate limiting
    rate_limit_per_day = Column(Integer, default=100)
    calls_today = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class PaymentHistory(Base):
    """Track payment transactions"""
    __tablename__ = 'payment_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")

    # Stripe/Payment gateway
    stripe_payment_id = Column(String(255), nullable=True)
    stripe_invoice_id = Column(String(255), nullable=True)

    # Status
    status = Column(String(50), nullable=False)  # 'succeeded', 'failed', 'pending', 'refunded'
    description = Column(Text, nullable=True)

    # Metadata
    payment_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


# Utility functions
def get_subscription_limits(tier: SubscriptionTier) -> dict:
    """Get limits for a subscription tier"""
    limits = {
        SubscriptionTier.FREE: {
            "section_analyses_limit": 10,
            "memo_generation_limit": 5,
            "case_search_limit": 3,  # per day
            "api_calls_limit": 0,
            "features": ["basic_search", "view_cases"]
        },
        SubscriptionTier.PROFESSIONAL: {
            "section_analyses_limit": -1,  # unlimited
            "memo_generation_limit": 50,
            "case_search_limit": -1,  # unlimited
            "api_calls_limit": 100,  # per day
            "features": ["advanced_search", "save_analyses", "export_pdf", "email_alerts", "api_access"]
        },
        SubscriptionTier.ENTERPRISE: {
            "section_analyses_limit": -1,
            "memo_generation_limit": -1,
            "case_search_limit": -1,
            "api_calls_limit": -1,
            "features": ["all_professional", "team_collaboration", "custom_branding", "priority_support", "sla"]
        }
    }
    return limits.get(tier, limits[SubscriptionTier.FREE])

"""
Authentication routes for user registration, login, and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime, timedelta

from database import get_db
from auth_models import User, Subscription, SubscriptionTier, SubscriptionStatus, UserRole, get_subscription_limits
from auth_utils import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_token, generate_verification_token,
    validate_password_strength
)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


# Pydantic models for requests/responses
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    bar_council_id: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[UserRole] = UserRole.LAWYER

    @validator('password')
    def password_strength(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    subscription_tier: str
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @validator('new_password')
    def password_strength(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


# Dependency to get current user from JWT token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials

    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


# Routes

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    verification_token = generate_verification_token()

    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        bar_council_id=user_data.bar_council_id,
        organization=user_data.organization,
        role=user_data.role,
        verification_token=verification_token,
        is_active=True,
        is_verified=False  # Will be verified via email
    )

    db.add(user)
    db.flush()  # Get user ID

    # Create subscription (14-day trial on Professional tier)
    trial_end = datetime.utcnow() + timedelta(days=14)
    limits = get_subscription_limits(SubscriptionTier.PROFESSIONAL)

    subscription = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.PROFESSIONAL,
        status=SubscriptionStatus.TRIAL,
        trial_ends_at=trial_end,
        current_period_start=datetime.utcnow(),
        current_period_end=trial_end,
        **{k: v for k, v in limits.items() if k.endswith('_limit')}
    )

    db.add(subscription)
    db.commit()
    db.refresh(user)

    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    # TODO: Send verification email (implement later)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "subscription_tier": subscription.tier.value,
            "trial_ends_at": trial_end.isoformat()
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password"""

    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support.",
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    # Get subscription info
    subscription = user.subscription

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "subscription_tier": subscription.tier.value if subscription else "free",
            "subscription_status": subscription.status.value if subscription else "active"
        }
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})

    subscription = user.subscription

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "subscription_tier": subscription.tier.value if subscription else "free"
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    subscription = current_user.subscription

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        subscription_tier=subscription.tier.value if subscription else "free",
        created_at=current_user.created_at
    )


@router.put("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""

    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (client should discard tokens)"""
    # In a production app, you might want to blacklist the token
    return {"message": "Logged out successfully"}

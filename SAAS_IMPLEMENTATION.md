# SaaS Implementation Guide - IPC/BNS Legal Reasoning Platform

## Overview
This document tracks the implementation of SaaS features for converting the IPC/BNS Legal Reasoning Agent into a subscription-based platform.

## Phase 1: Authentication & Subscription System ✅ IN PROGRESS

### Completed Features

#### 1. Database Models (`auth_models.py`)
- ✅ **User Model**: Complete user management with roles (Admin, Lawyer, Researcher, Student, Enterprise)
- ✅ **Subscription Model**: Tiered subscriptions (Free, Professional, Enterprise)
- ✅ **Usage Tracking**: UsageLog for analytics and billing
- ✅ **Saved Analyses**: Users can save and organize their research
- ✅ **API Keys**: Programmatic access for integrations
- ✅ **Payment History**: Transaction tracking

**Key Tables:**
- `users` - User accounts and profiles
- `subscriptions` - Subscription tiers and limits
- `usage_logs` - Action tracking for analytics
- `saved_analyses` - User's saved research
- `api_keys` - API authentication
- `payment_history` - Billing records

#### 2. Authentication Utilities (`auth_utils.py`)
- ✅ **Password Hashing**: Bcrypt for secure password storage
- ✅ **JWT Tokens**: Access and refresh token generation
- ✅ **Token Validation**: Decode and verify JWT tokens
- ✅ **Password Strength Validation**: Enforce strong passwords
- ✅ **API Key Generation**: Secure random keys
- ✅ **Privacy Functions**: Email/phone masking

#### 3. Authentication Routes (`auth_routes.py`)
- ✅ **POST `/auth/register`**: User registration with 14-day trial
- ✅ **POST `/auth/login`**: Email/password authentication
- ✅ **POST `/auth/refresh`**: Refresh access tokens
- ✅ **GET `/auth/me`**: Get current user info
- ✅ **PUT `/auth/change-password`**: Change password
- ✅ **POST `/auth/logout`**: Logout endpoint

#### 4. Subscription Routes (`subscription_routes.py`)
- ✅ **GET `/subscription/info`**: Get subscription details and usage
- ✅ **GET `/subscription/usage`**: Usage statistics (30-day charts)
- ✅ **POST `/subscription/upgrade`**: Upgrade subscription tier
- ✅ **POST `/subscription/cancel`**: Cancel subscription
- ✅ **GET `/subscription/plans`**: List all available plans

#### 5. Subscription Tiers

| Feature | Free | Professional | Enterprise |
|---------|------|--------------|------------|
| Section Analyses | 10/month | Unlimited | Unlimited |
| Memo Generation | 5/month | 50/month | Unlimited |
| Case Search | 3/day | Unlimited | Unlimited |
| API Access | ❌ | 100 calls/day | Unlimited |
| Save Research | ❌ | ✅ | ✅ |
| Export PDF | Watermarked | ✅ | ✅ |
| Team Features | ❌ | ❌ | ✅ |
| Custom Branding | ❌ | ❌ | ✅ |
| **Price** | Free | ₹2,999/mo | ₹49,999/mo |

---

## Phase 2: Integration (NEXT STEPS)

### To Do:

#### 1. Update `database.py`
```python
# Add auth models to Base
from auth_models import User, Subscription, UsageLog, SavedAnalysis, APIKey, PaymentHistory
```

#### 2. Update `main.py`
```python
# Import auth routes
from auth_routes import router as auth_router
from subscription_routes import router as subscription_router

# Include routers
app.include_router(auth_router)
app.include_router(subscription_router)

# Add usage tracking middleware
```

#### 3. Create Usage Tracking Middleware
```python
# File: usage_middleware.py
- Track all API calls
- Log to usage_logs table
- Check subscription limits
- Return 429 if limit exceeded
```

#### 4. Protect Existing Endpoints
Update existing routes to require authentication:
- `/analyze` → Requires auth, checks limits
- `/memo` → Requires auth, checks limits
- `/cases/search` → Requires auth, checks limits

#### 5. Update `init_db.py`
- Create new auth tables on initialization
- Optionally seed with admin user

---

## Phase 3: Document Generation (PLANNED)

### Templates to Create:
1. **Petition Template**
2. **Bail Application**
3. **Written Submission**
4. **Legal Notice**
5. **Client Advisory Letter**

### Implementation:
- Jinja2 templates
- PDF generation with ReportLab
- Docx generation with python-docx
- Email delivery integration

---

## Phase 4: Mobile API Optimization (PLANNED)

### Features:
- Pagination for all list endpoints
- Image optimization
- Response compression
- GraphQL endpoint (optional)
- WebSocket for real-time updates

---

## Phase 5: Database Expansion (PLANNED)

### Additions:
- **100+ more IPC sections** → BNS mappings
- **100+ more landmark cases**
- **CrPC → BNSS** module
- **Evidence Act → BSE** module
- **High Court judgments** (state-wise)
- **Special Acts** (POCSO, SC/ST Act, etc.)

---

## Frontend Changes Required

### New Pages:
1. **Login Page** (`/login`)
2. **Registration Page** (`/register`)
3. **User Dashboard** (`/dashboard/profile`)
4. **Subscription Management** (`/dashboard/subscription`)
5. **Usage Statistics** (`/dashboard/usage`)
6. **Saved Analyses** (`/dashboard/saved`)

### Updates to Existing Pages:
- Add authentication guards
- Show usage limits on each page
- "Upgrade to unlock" prompts for free tier
- User menu in navbar

---

## Environment Variables

Add to `.env`:
```bash
# Authentication
SECRET_KEY=your-super-secret-key-min-32-chars-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ipc_bns_legal
```

---

## API Usage Examples

### Register New User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lawyer@example.com",
    "password": "SecurePass123!",
    "full_name": "Advocate John Doe",
    "bar_council_id": "D/12345/2020",
    "role": "lawyer"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lawyer@example.com",
    "password": "SecurePass123!"
  }'
```

### Analyze Section (with auth)
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"ipc_section": "302"}'
```

### Check Subscription
```bash
curl http://localhost:8000/subscription/info \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Testing Plan

### Unit Tests
- [ ] User registration validation
- [ ] Password hashing/verification
- [ ] JWT token generation/validation
- [ ] Usage limit checking
- [ ] Subscription upgrade/downgrade

### Integration Tests
- [ ] Complete auth flow (register → login → use API)
- [ ] Usage tracking across endpoints
- [ ] Subscription limit enforcement
- [ ] Token refresh flow

### E2E Tests
- [ ] User registration through frontend
- [ ] Login and access protected pages
- [ ] Usage limit reached scenarios
- [ ] Subscription upgrade flow

---

## Deployment Checklist

- [ ] Set strong SECRET_KEY in production
- [ ] Configure Stripe webhooks
- [ ] Set up email service (SendGrid/SES)
- [ ] Configure PostgreSQL database
- [ ] Set up Redis for caching
- [ ] Enable HTTPS
- [ ] Configure CORS for production domain
- [ ] Set up monitoring (Sentry)
- [ ] Configure backups
- [ ] Load testing
- [ ] Security audit

---

## Next Immediate Steps

1. ✅ Update `database.py` to import auth models
2. ✅ Update `main.py` to include auth routes
3. ✅ Create usage tracking middleware
4. ✅ Protect existing endpoints with auth
5. ✅ Test registration and login flow
6. ✅ Build frontend login/register UI
7. ✅ Integrate Stripe for payments
8. ✅ Add email verification
9. ✅ Create user dashboard frontend

---

## Revenue Projections (Conservative)

**Year 1 Targets:**
- 10,000 free users
- 500 professional subscribers = ₹14,99,500/month
- 20 enterprise subscribers = ₹9,99,980/month
- **Total MRR: ₹24,99,480 (~₹3 Crores ARR)**

**Year 2 Targets:**
- 25,000 free users
- 2,000 professional = ₹59,98,000/month
- 50 enterprise = ₹24,99,950/month
- **Total MRR: ₹84,97,950 (~₹10 Crores ARR)**

---

## Contact & Support

For implementation questions or assistance:
- Technical Docs: `/docs` endpoint
- GitHub Issues: (your-repo)
- Email: support@iplegal.in

---

**Last Updated:** 2026-01-03
**Status:** Phase 1 - 70% Complete

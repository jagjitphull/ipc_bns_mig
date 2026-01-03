# Stripe Integration Setup Guide

This guide explains how to configure Stripe payment processing for the IPC/BNS Legal Reasoning Agent subscription system.

## Prerequisites

1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe Dashboard

## Configuration Steps

### 1. Environment Variables

Add the following environment variables to your `.env` file or deployment configuration:

```bash
# Stripe API Keys
STRIPE_SECRET_KEY=sk_test_...  # Your Stripe secret key (test or live)
STRIPE_WEBHOOK_SECRET=whsec_...  # Your webhook signing secret

# Frontend URL for redirects
FRONTEND_URL=http://localhost:3000  # Update for production
```

### 2. Stripe API Keys

#### Test Mode (Development)
1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy your **Secret key** (starts with `sk_test_`)
3. Set `STRIPE_SECRET_KEY=sk_test_...`

#### Live Mode (Production)
1. Go to https://dashboard.stripe.com/apikeys
2. Copy your **Secret key** (starts with `sk_live_`)
3. Set `STRIPE_SECRET_KEY=sk_live_...`

### 3. Webhook Setup

Webhooks allow Stripe to notify your application about subscription events.

#### Local Development (Using Stripe CLI)

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Login to Stripe CLI:
   ```bash
   stripe login
   ```
3. Forward webhooks to your local server:
   ```bash
   stripe listen --forward-to http://localhost:8000/webhooks/stripe
   ```
4. Copy the webhook signing secret from the CLI output
5. Set `STRIPE_WEBHOOK_SECRET=whsec_...`

#### Production (Dashboard)

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter your webhook URL: `https://yourdomain.com/webhooks/stripe`
4. Select events to listen for:
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.deleted`
5. Copy the **Signing secret**
6. Set `STRIPE_WEBHOOK_SECRET=whsec_...`

## Pricing Configuration

Current pricing is configured in `backend/app/stripe_service.py`:

```python
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
```

### Changing Prices

1. Update amounts in `stripe_service.py` (remember: amounts are in paise)
2. Restart your backend server
3. Test with Stripe test cards

## Testing

### Test Card Numbers

Stripe provides test cards for different scenarios:

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires Authentication**: `4000 0025 0000 3155`

Use any future expiry date, any 3-digit CVC, and any postal code.

### Test Subscription Flow

1. Register a new user or login
2. Navigate to `/pricing`
3. Click "Upgrade to Professional"
4. You'll be redirected to Stripe Checkout
5. Use test card: `4242 4242 4242 4242`
6. Complete payment
7. You'll be redirected back to `/profile?payment=success`
8. Verify subscription tier and limits are updated

## Features

### Implemented Features

✅ **Checkout Sessions**
- Create Stripe checkout for Professional and Enterprise tiers
- 14-day free trial for Professional tier
- Automatic customer creation

✅ **Subscription Management**
- Upgrade from Free → Professional → Enterprise
- Cancel subscriptions (access continues until period end)
- Automatic usage limit updates

✅ **Usage Tracking**
- Track section analyses, memos, case searches
- Enforce limits based on subscription tier
- Real-time usage indicators in UI

✅ **Webhooks** (Ready)
- Handle successful payments
- Handle failed payments
- Handle subscription cancellations

### Demo Mode

If Stripe is not configured (no API key), the system falls back to demo mode:
- Shows upgrade prompts with alert
- Allows testing without actual payment processing
- Useful for development and demos

## Security Best Practices

1. **Never commit API keys**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Use webhook secrets**
   - Verify webhook signatures
   - Prevents unauthorized access

3. **Test mode vs Live mode**
   - Always test in test mode first
   - Use separate API keys for production

4. **HTTPS in Production**
   - Webhooks require HTTPS
   - Use SSL certificates

## Troubleshooting

### "Stripe payment service is not configured"

**Cause**: `STRIPE_SECRET_KEY` environment variable not set

**Solution**:
```bash
export STRIPE_SECRET_KEY=sk_test_your_key_here
```

### Webhook signature verification failed

**Cause**: `STRIPE_WEBHOOK_SECRET` incorrect or missing

**Solution**:
1. Check webhook secret in Stripe Dashboard
2. Update environment variable
3. Restart server

### Subscription not updating after payment

**Cause**: Webhook not received or processed

**Solution**:
1. Check Stripe Dashboard → Webhooks → Events
2. Verify webhook endpoint is accessible
3. Check server logs for errors

## Going Live Checklist

- [ ] Replace test API keys with live keys
- [ ] Update `FRONTEND_URL` to production domain
- [ ] Configure production webhook endpoint
- [ ] Test complete subscription flow
- [ ] Verify webhook events are received
- [ ] Enable HTTPS on webhook endpoint
- [ ] Review Stripe Dashboard for pending actions
- [ ] Set up subscription plan prices
- [ ] Configure tax settings (if applicable)

## Support

- Stripe Documentation: https://stripe.com/docs
- Stripe Support: https://support.stripe.com
- Our Support: [your-support-email]

## Revenue Tracking

Monitor your revenue in:
- Stripe Dashboard: https://dashboard.stripe.com
- Your `/profile` endpoint for user subscription data
- Database `payment_history` table for transaction records

---

**Note**: This integration uses Stripe Checkout for a hosted payment experience. For custom payment forms, consider implementing Stripe Elements.

# Setting Up Ngrok for M-Pesa Callbacks

## The Problem
M-Pesa needs to send payment confirmations to your application via a callback URL. Since your Django app is running locally, M-Pesa can't reach it directly. Ngrok creates a secure tunnel to your local server.

## Solution 1: Fix Ngrok (Recommended)

### Step 1: Install Ngrok
```bash
# Download from https://ngrok.com/download
# Or install via package manager
brew install ngrok  # macOS
sudo snap install ngrok  # Ubuntu
```

### Step 2: Get Ngrok Auth Token
1. Sign up at https://ngrok.com/
2. Get your auth token from the dashboard
3. Configure it:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 3: Start Ngrok Tunnel
```bash
# In a new terminal, run:
ngrok http 8001

# You'll see output like:
# Forwarding: https://abc123.ngrok-free.app -> http://localhost:8001
```

### Step 4: Update Callback URL
Update your `.env` file with the new ngrok URL:
```env
MPESA_CALLBACK_URL=https://YOUR_NGROK_URL.ngrok-free.app/payments/callback/
```

### Step 5: Restart Django
```bash
python manage.py runserver 0.0.0.0:8001
```

## Solution 2: Use Manual Confirmation (Current Fallback)

If ngrok is not working, the system now supports manual payment confirmation:

1. **User completes M-Pesa payment** on their phone
2. **System waits for automatic confirmation** (30 seconds)
3. **If no confirmation**, user can click "Confirm Manually"
4. **User enters M-Pesa confirmation code** from SMS
5. **Payment is marked as successful**

## Testing the Setup

### Test Ngrok Connection
```bash
curl https://YOUR_NGROK_URL.ngrok-free.app/payments/test-callback/
```

Should return:
```json
{
  "status": "success",
  "message": "Callback URL is accessible"
}
```

### Test M-Pesa Integration
```bash
python manage.py test_mpesa --phone +254712345678 --amount 1
```

## Troubleshooting

### Ngrok Issues
- **"ERR_NGROK_3200"**: Ngrok tunnel is offline
- **"ERR_NGROK_3004"**: Free plan limitations
- **Solution**: Restart ngrok or upgrade plan

### M-Pesa Issues
- **403 Forbidden**: Callback URL not accessible
- **Invalid credentials**: Check consumer key/secret
- **Solution**: Verify ngrok is running and URL is correct

### Callback Not Working
- Check ngrok logs: `ngrok http 8001 --log=stdout`
- Check Django logs: Look for "M-Pesa callback received"
- Use manual confirmation as fallback

## Production Setup

For production, replace ngrok with:
- **Heroku**: Automatic HTTPS URLs
- **AWS/DigitalOcean**: Configure domain with SSL
- **Cloudflare**: SSL termination

Update `.env` with your production callback URL:
```env
MPESA_CALLBACK_URL=https://unsprayed-mindi-renunciable.ngrok-free.dev/payments/callback/
```
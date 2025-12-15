# Environment Setup Guide

This guide will help you configure the `.env` file with your actual credentials and settings.

## Quick Start

The `.env` file has been created with default values. You need to update it with your actual credentials before running the application.

## Required Credentials

### 1. Amazon Ads API Credentials (REQUIRED)

To use the Amazon Ads API, you need:

1. **Register for Amazon Ads API Access**
   - Visit: https://advertising.amazon.com/API/docs/en-us/get-started/overview
   - Follow the registration process
   - You'll receive: Client ID, Client Secret

2. **Generate Refresh Token**
   - Follow Amazon's OAuth flow
   - Use the authorization code to get a refresh token
   - This token is used to get access tokens automatically

3. **Update `.env` file:**
   ```bash
   AMAZON_ADS_CLIENT_ID=amzn1.application-oa2-client.xxxxxxxxxxxxx
   AMAZON_ADS_CLIENT_SECRET=your_secret_here
   AMAZON_ADS_REFRESH_TOKEN=Atzr|IwEBxxxxxxxxxxxx
   ```

### 2. AI Provider API Key (REQUIRED for AI Analysis)

Choose **ONE** AI provider:

#### Option A: OpenAI (GPT-4)

1. **Get API Key:**
   - Visit: https://platform.openai.com/api-keys
   - Create account or sign in
   - Generate a new API key

2. **Update `.env` file:**
   ```bash
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   AI_PROVIDER=openai
   AI_MODEL=gpt-4-turbo-preview
   ```

#### Option B: Anthropic Claude

1. **Get API Key:**
   - Visit: https://console.anthropic.com/
   - Create account or sign in
   - Generate a new API key

2. **Update `.env` file:**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   AI_PROVIDER=anthropic
   AI_MODEL=claude-3-opus-20240229
   ```

## Database Configuration

### Development (SQLite - Default)

No setup required! The default configuration works out of the box:

```bash
DATABASE_URL=sqlite:///amazon_ppc.db
```

The database file will be created automatically in the project root.

### Production (PostgreSQL - Recommended)

1. **Install PostgreSQL**
   ```bash
   # macOS
   brew install postgresql@16
   brew services start postgresql@16

   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Create Database**
   ```bash
   # Login to PostgreSQL
   psql -U postgres

   # Create database and user
   CREATE DATABASE amazon_ppc;
   CREATE USER ppc_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE amazon_ppc TO ppc_user;
   \q
   ```

3. **Update `.env` file:**
   ```bash
   # Standard PostgreSQL connection
   DATABASE_URL=postgresql://ppc_user:your_secure_password@localhost:5432/amazon_ppc

   # Or with async support (recommended)
   DATABASE_URL=postgresql+asyncpg://ppc_user:your_secure_password@localhost:5432/amazon_ppc
   ```

## Optional Configuration

### Optimization Parameters

Adjust based on your business goals:

```bash
# Target ACOS: 25% is a common starting point
TARGET_ACOS=0.25

# Bid limits: adjust based on your product margins
MIN_BID=0.20
MAX_BID=1.60

# Optimization mode:
# - dry-run: only show recommendations (safe for testing)
# - apply: automatically apply recommendations
# - aggressive: apply with larger bid adjustments
OPTIMIZE_DEFAULT_MODE=dry-run
```

### Advanced Optimization Thresholds

Fine-tune when keywords should be paused:

```bash
# Pause keyword after this many impressions with no sales
MIN_IMPRESSIONS_FOR_PAUSE=5000

# Pause if ACOS is 2x the target (50% if target is 25%)
HIGH_ACOS_MULTIPLIER=2.0

# Pause if CTR is below 0.2%
LOW_CTR_THRESHOLD=0.002

# Maximum bid changes per optimization
MAX_BID_INCREASE=0.20  # 20%
MAX_BID_DECREASE=0.30  # 30%

# Pause keyword if spent this much with no conversions
MIN_SPEND_FOR_PAUSE=50.0
```

### API Server Settings

```bash
# Host and port for the FastAPI server
API_HOST=0.0.0.0  # Listen on all interfaces
API_PORT=8000

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000

# Debug mode (disable in production)
DEBUG=True

# Logging level
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Amazon API Fetch Settings

```bash
# Rate limiting (requests per second)
FETCH_RATE_LIMIT_PER_SEC=5.0

# Retry configuration
FETCH_MAX_RETRIES=3
FETCH_BACKOFF_SECONDS=1.0

# Timeout for report polling (10 minutes)
FETCH_POLL_TIMEOUT_SECONDS=600.0
```

## Verification

After configuring your `.env` file, verify the setup:

1. **Check configuration:**
   ```bash
   python -m agent config
   ```

2. **Test API health:**
   ```bash
   python -m agent healthcheck
   ```

3. **Start the API server:**
   ```bash
   python -m agent api
   ```

4. **Visit the API docs:**
   Open browser to: http://localhost:8000/docs

## Security Best Practices

### 1. Never Commit `.env` File

The `.env` file is already in `.gitignore`. Verify:

```bash
git status
# .env should NOT appear in the list
```

### 2. Use Strong Credentials

- Use complex passwords for database
- Rotate API keys regularly
- Never share credentials in chat/email

### 3. Production Environment

For production deployment:

```bash
# Disable debug mode
DEBUG=False

# Use strong secret key (generate random string)
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')

# Enable HTTPS redirect
HTTPS_REDIRECT=True

# Restrict allowed hosts
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Use environment variables instead of .env file
# Set them directly in your hosting platform
```

## Troubleshooting

### Issue: "No module named 'dotenv'"

**Solution:**
```bash
pip install python-dotenv
```

### Issue: "Database connection failed"

**Solution:**
- For SQLite: Check file permissions in project directory
- For PostgreSQL: Verify service is running and credentials are correct

```bash
# Test PostgreSQL connection
psql postgresql://ppc_user:password@localhost:5432/amazon_ppc
```

### Issue: "Amazon API authentication failed"

**Solution:**
- Verify Client ID and Client Secret are correct
- Check if Refresh Token has expired
- Ensure you have proper API permissions in Amazon Ads Console

### Issue: "AI API key invalid"

**Solution:**
- Verify API key is correct (no extra spaces)
- Check if key has required permissions
- Verify billing is set up for OpenAI/Anthropic account

## Getting Help

1. Check the logs:
   ```bash
   tail -f logs/app.log
   ```

2. Enable debug logging:
   ```bash
   LOG_LEVEL=DEBUG
   ```

3. Review documentation:
   - [README.md](README.md) - General project overview
   - [project_plan.txt](project_plan.txt) - Detailed project plan
   - API Docs: http://localhost:8000/docs (when running)

## Next Steps

After configuring your environment:

1. ✅ Update `.env` with credentials
2. ✅ Verify configuration: `python -m agent config`
3. ✅ Initialize database (when migrations are ready)
4. ✅ Start API server: `python -m agent api`
5. ✅ Test data import or API fetch
6. ✅ Generate AI recommendations

---

**Last Updated:** 2025-12-15

**Note:** This file can be safely committed to version control as it contains no sensitive information.

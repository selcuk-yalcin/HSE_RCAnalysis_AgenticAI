# Environment Variables Setup Guide

This guide explains how to configure environment variables for the HSE Investigation System.

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Get your OpenAI API Key:**
   - Go to https://platform.openai.com/api-keys
   - Create a new API key
   - Copy the key (starts with `sk-`)

3. **Edit `.env` file:**
   ```bash
   nano .env
   # or
   code .env
   ```

4. **Add your API key:**
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

## Required Variables

### OpenAI Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | **YES** | - |
| `OPENAI_MODEL` | GPT model to use | No | `gpt-4o-mini` |
| `OPENAI_TEMPERATURE` | Creativity level (0-2) | No | `0.7` |

### Recommended Models

| Model | Speed | Cost | Quality | Use Case |
|-------|-------|------|---------|----------|
| `gpt-4o-mini` | ⚡⚡⚡ | 💰 | ⭐⭐⭐ | **Recommended** - Fast & cheap |
| `gpt-4o` | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐ | Best quality |
| `gpt-4-turbo` | ⚡⚡ | 💰💰💰 | ⭐⭐⭐⭐⭐ | Highest quality |
| `gpt-3.5-turbo` | ⚡⚡⚡ | 💰 | ⭐⭐ | Fastest, lowest cost |

## Optional Variables

### API Configuration

```bash
PORT=8000                                    # API port
ENVIRONMENT=development                      # development/staging/production
API_BASE_URL=http://localhost:8000          # Base URL for API
```

### Admin Panel

```bash
ADMIN_PANEL_URL=https://your-admin.vercel.app
```

### Database (Future)

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/hse_db

# SQLite (for development)
DATABASE_URL=sqlite:///./hse_database.db
```

### Logging & Monitoring

```bash
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
AGENT_TIMEOUT=30            # Seconds
MAX_RETRIES=3               # API retry attempts
```

## Testing Your Configuration

### 1. Test API Key

```bash
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('API Key:', os.getenv('OPENAI_API_KEY')[:20] + '...')
print('Model:', os.getenv('OPENAI_MODEL'))
"
```

### 2. Test Agent

```bash
python examples/test_pdf_agent.py
```

### 3. Test API Server

```bash
# Start server
python -m uvicorn api.main:app --reload

# In another terminal, test health
curl http://localhost:8000/api/v1/health
```

## Security Best Practices

### ✅ DO:
- Keep `.env` file in `.gitignore`
- Use different API keys for development/production
- Rotate API keys regularly
- Set spending limits in OpenAI dashboard
- Use environment-specific `.env` files

### ❌ DON'T:
- Commit `.env` to git
- Share API keys in chat/email
- Use production keys in development
- Hardcode API keys in source code
- Share `.env` files

## Environment-Specific Setup

### Development

```bash
# .env.development
OPENAI_API_KEY=sk-dev-key-here
OPENAI_MODEL=gpt-4o-mini
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### Production (Vercel)

Set in Vercel Dashboard → Project → Settings → Environment Variables:

```
OPENAI_API_KEY = sk-prod-key-here (Secret ✓)
OPENAI_MODEL = gpt-4o-mini
ENVIRONMENT = production
```

### VPS Deployment

```bash
# On VPS
cd /opt/HSE_AgenticAI
nano .env

# Secure the file
chmod 600 .env
chown www-data:www-data .env
```

## Troubleshooting

### "OPENAI_API_KEY not found"

```bash
# Check if .env exists
ls -la .env

# Check if loaded correctly
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### "Invalid API key"

1. Verify key in OpenAI dashboard
2. Check for extra spaces in `.env`
3. Ensure key starts with `sk-`
4. Try regenerating the key

### "Rate limit exceeded"

1. Check usage at https://platform.openai.com/usage
2. Set `OPENAI_TEMPERATURE` lower (0.3)
3. Add retry logic
4. Upgrade OpenAI plan

## Cost Management

### Estimate Costs

```python
# Approximate costs (as of 2025)
gpt-4o-mini:     $0.15  / 1M input tokens,  $0.60  / 1M output tokens
gpt-4o:          $2.50  / 1M input tokens,  $10.00 / 1M output tokens
gpt-4-turbo:     $10.00 / 1M input tokens,  $30.00 / 1M output tokens
```

### Cost Per Investigation

```
Average incident report:
- Input: ~2,000 tokens
- Output: ~1,500 tokens

Using gpt-4o-mini:
Cost = (2000 * $0.15 / 1M) + (1500 * $0.60 / 1M)
     = $0.0003 + $0.0009
     = $0.0012 per report (~$0.12 per 100 reports)
```

### Set Spending Limits

1. Go to https://platform.openai.com/account/billing/limits
2. Set monthly budget limit
3. Enable email alerts

## Example .env File

```bash
# Working example
OPENAI_API_KEY=sk-proj-abc123xyz789...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
PORT=8000
ENVIRONMENT=development
LOG_LEVEL=INFO
AGENT_TIMEOUT=30
MAX_RETRIES=3
```

## Getting Help

- OpenAI API Issues: https://help.openai.com
- Project Issues: https://github.com/selcuk-yalcin/HSE_RCAnalysis_AgenticAI/issues
- Documentation: See README.md

## Next Steps

After configuration:
1. ✅ Test with `python examples/test_pdf_agent.py`
2. ✅ Start API server: `uvicorn api.main:app --reload`
3. ✅ Connect admin panel to API
4. ✅ Deploy to VPS or Vercel

# 🚀 Deployment Guide for DaycareMoments

## Automated Deployment to Streamlit Cloud

### Prerequisites
- GitHub account with repository access
- Streamlit Cloud account (free tier works)

### Setup Steps

#### 1. Connect Repository to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your GitHub repository: `gvkmdkra/daycaremoments`
4. Set:
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: `daycaremoments` (or your custom subdomain)

#### 2. Configure Secrets

Go to App Settings → Secrets and paste:

```toml
# AI/LLM Configuration
GEMINI_API_KEY = "your_gemini_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
LLM_PROVIDER = "openai"

# Email Configuration
EMAIL_HOST_USER = "your_email@gmail.com"
EMAIL_HOST_PASSWORD = "your_app_password"

# Twilio Configuration
TWILIO_ENABLED = "true"
TWILIO_ACCOUNT_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_token"
TWILIO_PHONE_NUMBER = "+1234567890"

# Database Configuration
TURSO_DB_URL = "https://your-db.turso.io"
TURSO_DB_AUTH_TOKEN = "your_turso_auth_token"
```

#### 3. Deploy

Click "Deploy" and wait 2-3 minutes. Streamlit Cloud will:
- Pull code from GitHub
- Use Python 3.11 (from `.python-version`)
- Install dependencies from `requirements.txt`
- Start the app at `https://daycaremoments.streamlit.app`

### Automated Deployment Workflow

**Every push to `main` branch automatically deploys!**

```bash
# Make your changes
git add .
git commit -m "Your changes"
git push origin main

# Streamlit Cloud automatically detects and deploys
# Check deployment status at https://share.streamlit.io
```

### Deployment Status

Monitor deployment at:
- **App URL**: https://daycaremoments.streamlit.app
- **Dashboard**: https://share.streamlit.io → Your App → Logs

### Troubleshooting

#### Issue: App won't start after deployment
**Solution**: Check Streamlit Cloud logs for errors
- Go to https://share.streamlit.io
- Click on your app → Logs
- Look for error messages in red

#### Issue: "ModuleNotFoundError"
**Solution**: Verify `requirements.txt` includes all dependencies
```bash
# Test locally first
pip install -r requirements.txt
streamlit run app.py
```

#### Issue: "Database connection error"
**Solution**: Verify Turso credentials in Streamlit Secrets
- Check `TURSO_DB_URL` format: `https://your-db.turso.io`
- Verify `TURSO_DB_AUTH_TOKEN` is correct

#### Issue: "AI not responding"
**Solution**: Check API keys in Streamlit Secrets
- Verify `OPENAI_API_KEY` or `GEMINI_API_KEY`
- Check API quotas haven't been exceeded

### Manual Reboot

If deployment is stuck:
1. Go to https://share.streamlit.io
2. Click on your app → ⋮ (menu)
3. Click "Reboot app"

### Rollback to Previous Version

```bash
# Find commit hash
git log --oneline

# Rollback to specific commit
git reset --hard <commit-hash>
git push origin main --force

# Streamlit Cloud will redeploy that version
```

### Environment-Specific Configuration

#### Production (Streamlit Cloud)
- Uses Streamlit Secrets (configured in dashboard)
- Python 3.11 from `.python-version`
- Minimal dependencies for fast deployment

#### Local Development
- Uses `.env` file (create from `.env.example`)
- Any Python 3.11+ version
- Full development dependencies

### Deployment Checklist

Before pushing to production:

- [ ] Test locally: `streamlit run app.py`
- [ ] Verify all imports work
- [ ] Check database connections
- [ ] Test AI features
- [ ] Verify mobile responsiveness
- [ ] Review Streamlit Secrets are configured
- [ ] Commit and push to `main`
- [ ] Monitor deployment logs
- [ ] Test live site on mobile and desktop

### Performance Optimization

Current deployment time: **~2-3 minutes**

Why so fast?
- ✅ Minimal dependencies (14 packages)
- ✅ Python 3.11 (faster runtime)
- ✅ No system packages (empty `packages.txt`)
- ✅ Streamlit Cloud caching

### Monitoring

#### Check App Status
```bash
curl https://daycaremoments.streamlit.app
```

#### View Logs
Go to https://share.streamlit.io → Your App → Logs

#### Analytics
Streamlit Cloud provides basic analytics:
- Page views
- Unique visitors
- Session duration

### Security Best Practices

1. **Never commit secrets** to Git
2. **Use Streamlit Secrets** for API keys
3. **Enable GitHub secret scanning** (already enabled)
4. **Rotate API keys** regularly
5. **Monitor usage** for suspicious activity

### Cost

**Streamlit Cloud Free Tier:**
- ✅ 1 private app
- ✅ Unlimited public apps
- ✅ GitHub integration
- ✅ Automatic HTTPS
- ✅ Custom domain support

**Turso Free Tier:**
- ✅ 9 GB storage
- ✅ 1 billion row reads/month
- ✅ 25 million row writes/month

**OpenAI Free Tier:**
- ⚠️ $5 credit for new users
- ⚠️ Pay-as-you-go after

### Next Steps

1. **Custom Domain**: Configure in Streamlit Cloud settings
2. **Monitoring**: Set up Sentry for error tracking
3. **Analytics**: Integrate Google Analytics
4. **CI/CD**: Set up GitHub Actions (requires workflow scope)

---

**Deployment URL**: https://daycaremoments.streamlit.app

**Support**: If issues persist, contact support@daycaremoments.com

# 🔒 Security Best Practices

This document outlines security best practices for this project.

## ⚠️ IP Address Exposure

### Risk Level: Medium

**What's the risk?**
- Exposing your GCP VM's IP address in public repositories can:
  - Make your server a target for automated attacks
  - Reveal your infrastructure setup
  - Help attackers identify your GCP project

**Current Status:**
- ✅ `config.json` is in `.gitignore` - **safe** (not committed)
- ⚠️ `config.json.example` contains placeholder - **safe** (no real IP)
- ✅ Real IP should only be in:
  - Local `config.json` (not committed)
  - GitHub Secrets (encrypted)
  - Streamlit Cloud Secrets (encrypted)
  - Environment variables on your server

## 🛡️ Best Practices

### 1. Never Commit Real IPs or Credentials

✅ **DO:**
- Use placeholders in example files: `http://your-api-ip:8000`
- Store real values in:
  - `config.json` (gitignored)
  - GitHub Secrets
  - Streamlit Cloud Secrets
  - Environment variables

❌ **DON'T:**
- Commit real IP addresses to git
- Hardcode credentials in source code
- Share IPs in public documentation

### 2. Use Secrets Management

**For GitHub:**
- Use GitHub Secrets for CI/CD
- Never commit secrets to the repository

**For Streamlit Cloud:**
- Use Streamlit Cloud Secrets
- Access via `st.secrets` in your code

**For Local Development:**
- Use `config.json` (already in `.gitignore`)
- Or use environment variables

### 3. Secure Your GCP VM

**Firewall Rules:**
```bash
# Only allow necessary ports
# Example: Only allow port 8000 from specific IPs if possible
gcloud compute firewall-rules create allow-api \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow API access"
```

**Best Practices:**
- ✅ Use firewall rules to restrict access
- ✅ Consider using Cloud Load Balancer with HTTPS
- ✅ Use IAM roles and service accounts
- ✅ Enable Cloud Armor for DDoS protection (if needed)
- ✅ Regularly update your VM and dependencies
- ✅ Use SSH keys instead of passwords
- ✅ Disable root login
- ✅ Use fail2ban for additional protection

### 4. Use Domain Names Instead of IPs (Recommended)

**Benefits:**
- Easier to change IPs without updating code
- Can use HTTPS/SSL certificates
- More professional appearance
- Can use Cloud Load Balancer

**Options:**
1. **Cloud Load Balancer** (GCP)
   - Provides static IP
   - SSL/TLS termination
   - DDoS protection
   - Health checks

2. **Domain Name + DNS**
   - Point domain to your VM IP
   - Use Let's Encrypt for free SSL
   - Easier to remember and share

### 5. Network Security

**Current Setup:**
- Your API is accessible at `http://35.225.228.65:8000`
- This means it's publicly accessible on the internet

**Recommendations:**
- ✅ Ensure your FastAPI app has proper authentication if needed
- ✅ Use HTTPS when possible (requires SSL certificate)
- ✅ Implement rate limiting
- ✅ Add CORS restrictions if applicable
- ✅ Monitor access logs for suspicious activity

### 6. Credentials Security

**GCP Service Account Keys:**
- ✅ Never commit JSON key files
- ✅ Rotate keys regularly
- ✅ Use least privilege principle
- ✅ Consider using Workload Identity (for GKE/Cloud Run)

**API Keys/Tokens:**
- Store in secrets, not code
- Rotate regularly
- Use different keys for dev/staging/prod

## 📋 Security Checklist

Before deploying:

- [ ] No real IPs in committed files
- [ ] No credentials in committed files
- [ ] `config.json` is in `.gitignore`
- [ ] GitHub Secrets configured (if using CI/CD)
- [ ] Streamlit Cloud Secrets configured (if using Streamlit Cloud)
- [ ] GCP firewall rules configured
- [ ] VM security updates applied
- [ ] SSH keys configured (no passwords)
- [ ] API has proper error handling (no sensitive info in errors)
- [ ] Logs don't contain sensitive information

## 🚨 If You've Already Committed Sensitive Data

If you've accidentally committed an IP or credential:

1. **Remove from git history:**
   ```bash
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch path/to/file' \
     --prune-empty --tag-name-filter cat -- --all
   ```

2. **Add to .gitignore** (if not already there)

3. **Rotate credentials** (if credentials were exposed)

4. **Update secrets** in GitHub/Streamlit Cloud

5. **Force push** (coordinate with team first!)

## 🔍 Monitoring

**What to Monitor:**
- Unusual traffic patterns
- Failed authentication attempts
- High CPU/memory usage
- Unusual API requests
- Error rates

**Tools:**
- GCP Cloud Monitoring
- GCP Cloud Logging
- Application logs
- Firewall logs

## 📚 Additional Resources

- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security](https://docs.github.com/en/code-security)
- [Streamlit Security](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

---

**Remember:** Security is an ongoing process, not a one-time setup. Regularly review and update your security practices.


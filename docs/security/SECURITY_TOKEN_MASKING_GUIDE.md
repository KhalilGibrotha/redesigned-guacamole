# 🔒 Security and Token Masking Guide for CI/CD Workflows

## 🚨 Critical: Values You MUST Mask

### 🔑 Authentication Tokens
These values should **ALWAYS** be masked in logs and output:

#### GitHub Tokens
- `ghp_*` - GitHub Personal Access Tokens
- `gho_*` - GitHub OAuth tokens  
- `ghu_*` - GitHub User tokens
- `ghs_*` - GitHub Server-to-server tokens
- `github_pat_*` - GitHub Fine-grained PATs

#### Atlassian/Confluence Tokens
- `ATATT*` - Atlassian API tokens
- `ATCTT*` - Atlassian Cloud tokens
- `ATBT*` - Atlassian Bot tokens
- Base64 encoded credentials (Basic auth)

#### Generic Patterns
- `Basic <base64>` - HTTP Basic auth
- `Bearer <token>` - Bearer tokens
- `Token <value>` - Generic API tokens
- Long base64 strings (40+ chars)

### 🌐 URLs and Endpoints
- Confluence URLs (may contain sensitive info)
- Database connection strings
- API endpoints with embedded credentials

### 📧 User Information
- Email addresses
- Usernames (when used as credentials)
- Personal information

## 🛡️ Implemented Security Measures

### 1. **Global Masking Setup**
```yaml
- name: 🎭 Mask Sensitive Values
  run: |
    # Mask all secrets used in workflow
    echo "::add-mask::${{ secrets.GITHUB_TOKEN }}"
    echo "::add-mask::${{ secrets.CONFLUENCE_URL }}"
    echo "::add-mask::${{ secrets.CONFLUENCE_AUTH }}"
    
    # Mask common token patterns
    echo "::add-mask::ghp_"
    echo "::add-mask::ATATT"
    echo "::add-mask::Basic "
    echo "::add-mask::Bearer "
```

### 2. **Log Sanitization**
```yaml
- name: 🧹 Sanitize Super Linter Logs
  run: |
    # Remove token patterns from log files
    sed -i 's/ghp_[a-zA-Z0-9]\{36\}/***GITHUB_TOKEN***/g' super-linter.log
    sed -i 's/ATATT[a-zA-Z0-9+/=]\{40,\}/***ATLASSIAN_TOKEN***/g' super-linter.log
    sed -i 's/Basic [a-zA-Z0-9+/=]\{20,\}/Basic ***CREDENTIALS***/g' super-linter.log
```

### 3. **Reduced Logging Verbosity**
```yaml
env:
  LOG_LEVEL: 'WARN'  # Reduced from INFO to minimize exposure
  ACTIONS_RUNNER_DEBUG: false
  ACTIONS_STEP_DEBUG: false
```

### 4. **Conditional Artifact Upload**
- Sanitized logs: Always uploaded
- Original logs: Only for full scans (controlled access)
- Shorter retention for sensitive logs (7 vs 30 days)

## 🚫 What NOT to Do

### ❌ Never Do This:
```yaml
# DON'T: Echo secrets directly
- run: echo "Token is ${{ secrets.API_TOKEN }}"

# DON'T: Use secrets in job names or outputs  
- name: "Deploy to ${{ secrets.ENVIRONMENT_URL }}"

# DON'T: Pass secrets to external actions without verification
- uses: untrusted/action@v1
  with:
    token: ${{ secrets.GITHUB_TOKEN }}

# DON'T: Use secrets in conditional expressions that might be logged
- if: ${{ secrets.API_KEY == 'production' }}
```

### ✅ Do This Instead:
```yaml
# ✅ Use environment variables
- run: deploy.sh
  env:
    API_TOKEN: ${{ secrets.API_TOKEN }}

# ✅ Mask values before any operations
- run: |
    echo "::add-mask::${{ secrets.API_TOKEN }}"
    echo "Using token for deployment"
    
# ✅ Use outputs for non-sensitive data only
- id: check
  run: echo "status=ready" >> $GITHUB_OUTPUT
```

## 🔍 Detection and Monitoring

### Automated Secret Detection
Our workflow includes multiple layers:

1. **DevSkim Scanner** - Detects hardcoded secrets in code
2. **Custom grep patterns** - Finds common credential patterns
3. **Log sanitization** - Removes tokens from output files
4. **GitHub's built-in masking** - Automatic secret protection

### Manual Audit Checklist
Regular check these areas:

- [ ] Workflow logs for exposed tokens
- [ ] Artifact files for sensitive data
- [ ] Summary reports for credential leakage  
- [ ] Error messages for authentication details
- [ ] Debug output for environment variables

## 🚨 Emergency Response

### If Tokens Are Exposed:

1. **Immediate Actions**
   - Revoke the exposed token immediately
   - Generate new credentials
   - Update GitHub secrets

2. **Investigation**
   - Check workflow run logs
   - Review artifact downloads
   - Audit repository access logs

3. **Prevention**
   - Add new patterns to masking rules
   - Update log sanitization scripts
   - Review and improve workflows

### Confluence-Specific Tokens
If Confluence tokens are exposed:
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Delete the compromised token
3. Create a new API token
4. Update `CONFLUENCE_API_TOKEN` secret

## 🛠️ Advanced Techniques

### Dynamic Masking
For runtime-generated secrets:
```yaml
- name: Generate and mask dynamic secret
  run: |
    DYNAMIC_TOKEN=$(generate-token.sh)
    echo "::add-mask::$DYNAMIC_TOKEN"
    echo "DYNAMIC_TOKEN=$DYNAMIC_TOKEN" >> $GITHUB_ENV
```

### Conditional Masking
For development vs production:
```yaml
- name: Mask production secrets
  if: github.ref == 'refs/heads/main'
  run: |
    echo "::add-mask::${{ secrets.PROD_API_KEY }}"
    echo "::add-mask::${{ secrets.PROD_DATABASE_URL }}"
```

### File-based Sanitization
For complex log files:
```bash
# Create sanitization script
cat > sanitize_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="$1"

# Define patterns to mask
PATTERNS=(
    's/ghp_[a-zA-Z0-9]{36}/***GITHUB_TOKEN***/g'
    's/ATATT[a-zA-Z0-9+/=]{40,}/***ATLASSIAN_TOKEN***/g'
    's/Basic [a-zA-Z0-9+/=]{20,}/Basic ***CREDENTIALS***/g'
    's/Bearer [a-zA-Z0-9+/=]{20,}/Bearer ***TOKEN***/g'
    's/[a-zA-Z0-9+/=]{40,}/***POTENTIAL_SECRET***/g'
)

# Apply all patterns
for pattern in "${PATTERNS[@]}"; do
    sed -i "$pattern" "$LOG_FILE"
done
EOF

chmod +x sanitize_logs.sh
./sanitize_logs.sh super-linter.log
```

## 📊 Monitoring Dashboard

### Key Metrics to Track
- Number of masked values per run
- Log sanitization success rate
- Secret exposure incidents
- Artifact security compliance

### Alerts to Configure
- New token patterns detected
- Sanitization failures
- Unusual secret access patterns
- Failed masking operations

## 📚 Best Practices Summary

1. **🎭 Always mask first** - Add masking before any operations
2. **🔍 Sanitize logs** - Clean all output files before upload
3. **📉 Minimize verbosity** - Use WARN instead of INFO/DEBUG
4. **⏰ Limited retention** - Shorter retention for sensitive logs
5. **🔄 Regular audits** - Check for new exposure patterns
6. **🚨 Quick response** - Have incident response plan ready

## 🔗 Additional Resources

- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Masking Values in Logs](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#masking-a-value-in-log)
- [Atlassian API Token Security](https://developer.atlassian.com/cloud/confluence/rest/intro/#authentication)

---

**⚠️ Remember:** Security is not a one-time setup but an ongoing process. Regular audits and updates are essential!

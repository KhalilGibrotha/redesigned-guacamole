# GitHub Actions Setup Guide for Confluence Publishing

This guide walks you through setting up the GitHub Actions workflow to automatically publish documentation to Confluence.

## 🚀 Quick Setup

### 1. Copy the Workflow File

```bash
# Create the workflows directory
mkdir -p .github/workflows

# Copy the workflow file
cp ci-cd-templates/github-actions-confluence.yml .github/workflows/confluence-publish.yml
```

### 2. Configure GitHub Secrets

Go to your repository settings → Secrets and variables → Actions, and add these repository secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `CONFLUENCE_URL` | Your Confluence base URL | `https://company.atlassian.net/wiki` |
| `CONFLUENCE_USERNAME` | Your Confluence username/email | `user@company.com` |
| `CONFLUENCE_API_TOKEN` | Confluence API token | `ATATT3xFfGF0...` |
| `CONFLUENCE_SPACE` | Target Confluence space key | `ANSIBLE` |

### 3. Generate Confluence API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a label like "GitHub Actions"
4. Copy the token (you won't see it again!)
5. Add it as `CONFLUENCE_API_TOKEN` secret

### 4. Test the Workflow

1. Commit and push the workflow file:
   ```bash
   git add .github/workflows/confluence-publish.yml
   git commit -m "Add GitHub Actions Confluence publishing workflow"
   git push origin main
   ```

2. The workflow will trigger automatically, or you can trigger it manually:
   - Go to Actions tab in your GitHub repository
   - Select "Confluence Documentation Publisher"
   - Click "Run workflow"

## 📋 Workflow Features

### Automatic Triggers
- **Push to main**: Publishes when docs/, vars/, or playbooks/ change
- **Manual trigger**: Run on-demand with options for environment, force update, dry run
- **Pull requests**: Validates templates but doesn't publish

### Smart Change Detection
- Only processes files that have actually changed
- Supports force update for complete refresh
- Dry run mode for validation without publishing

### Security Features
- Uses GitHub secrets for credentials (never exposed in logs)
- Base64 encoding for API authentication
- Environment-specific deployments with approval gates

### Error Handling
- Validates all inputs before processing
- Continues on non-critical errors
- Provides detailed logging and summaries
- Artifact retention for debugging

## 🔧 Advanced Configuration

### Environment-Specific Deployments

You can set up different environments (dev/staging/prod) with different Confluence spaces:

1. Create environment-specific secrets:
   - `CONFLUENCE_URL_DEV`
   - `CONFLUENCE_SPACE_DEV`
   - etc.

2. Modify the workflow to use environment-specific values:
   ```yaml
   - name: Set environment variables
     run: |
       if [ "${{ github.event.inputs.environment }}" = "development" ]; then
         echo "CONFLUENCE_URL=${{ secrets.CONFLUENCE_URL_DEV }}" >> $GITHUB_ENV
         echo "CONFLUENCE_SPACE=${{ secrets.CONFLUENCE_SPACE_DEV }}" >> $GITHUB_ENV
       elif [ "${{ github.event.inputs.environment }}" = "staging" ]; then
         echo "CONFLUENCE_URL=${{ secrets.CONFLUENCE_URL_STAGING }}" >> $GITHUB_ENV
         echo "CONFLUENCE_SPACE=${{ secrets.CONFLUENCE_SPACE_STAGING }}" >> $GITHUB_ENV
       else
         echo "CONFLUENCE_URL=${{ secrets.CONFLUENCE_URL }}" >> $GITHUB_ENV
         echo "CONFLUENCE_SPACE=${{ secrets.CONFLUENCE_SPACE }}" >> $GITHUB_ENV
       fi
   ```

### Approval Gates

For production deployments, you can require manual approval:

1. Go to Settings → Environments
2. Create a "production" environment
3. Add required reviewers
4. The workflow will pause for approval before publishing

### Notifications

Add Slack/Teams/email notifications by modifying the notify job:

```yaml
- name: Send Slack notification
  if: needs.publish-confluence.result == 'success'
  uses: 8398a7/action-slack@v3
  with:
    status: success
    text: 'Confluence documentation updated successfully!'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## 🔄 Migration from Ansible

### Hybrid Approach (Recommended)

Keep both systems running in parallel:

1. **Local Development**: Continue using Ansible for testing
   ```bash
   make run-full  # Local testing with Ansible
   ```

2. **Production Publishing**: Use GitHub Actions for automatic publishing
   - Triggered by commits to main branch
   - More reliable and auditable

### Comparison: Ansible vs GitHub Actions

| Feature | Ansible | GitHub Actions |
|---------|---------|----------------|
| **Local Testing** | ✅ Easy | ❌ Requires commit |
| **Automatic Publishing** | ❌ Manual | ✅ Automatic |
| **Secret Management** | ⚠️ Local files | ✅ GitHub secrets |
| **Audit Trail** | ❌ Limited | ✅ Full history |
| **Error Handling** | ⚠️ Basic | ✅ Advanced |
| **Parallel Processing** | ❌ Sequential | ✅ Parallel jobs |
| **Infrastructure** | ⚠️ Requires Ansible | ✅ Zero maintenance |

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Failures
```
❌ CONFLUENCE_USERNAME secret is not set
```
**Solution**: Check that all required secrets are configured in repository settings.

#### 2. Template Processing Errors
```
❌ Error processing template: undefined variable
```
**Solution**: Verify that all variables used in templates are defined in the mock_vars.yml or actual vars.

#### 3. Confluence API Errors
```
❌ Failed to publish main page (HTTP 400)
```
**Solutions**:
- Check Confluence URL format (should include `/wiki`)
- Verify space key exists and you have permissions
- Ensure API token has correct permissions

#### 4. HTML Generation Issues
```
❌ Failed to generate: main.md.html
```
**Solution**: Check that pandoc is installed and markdown files are valid.

### Debug Mode

Enable debug logging by adding this to your workflow:

```yaml
- name: Debug environment
  run: |
    echo "GitHub event: ${{ github.event_name }}"
    echo "Branch: ${{ github.ref }}"
    echo "Changed files:"
    git diff --name-only HEAD~1 HEAD || echo "No changes to compare"
    echo "Secrets configured:"
    echo "- CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL != '' }}"
    echo "- CONFLUENCE_USERNAME: ${{ secrets.CONFLUENCE_USERNAME != '' }}"
    echo "- CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN != '' }}"
```

### Manual Testing

Test the workflow components locally:

```bash
# Test template processing
python3 -c "
import yaml
from jinja2 import Environment, FileSystemLoader

with open('vars/vars.yml.example', 'r') as f:
    vars = yaml.safe_load(f)

env = Environment(loader=FileSystemLoader('docs'))
template = env.get_template('main.md.j2')
print(template.render(**vars))
"

# Test HTML conversion
pandoc --from markdown --to html5 --standalone docs/main.md.j2 -o test.html

# Test Confluence API
curl -H "Authorization: Basic $(echo -n 'user:token' | base64)" \
     "https://company.atlassian.net/wiki/rest/api/content?spaceKey=TEST&limit=1"
```

## 📊 Monitoring and Metrics

### Workflow Analytics

Monitor your workflow performance:

1. Go to Actions tab → Confluence Documentation Publisher
2. View run history and success rates
3. Check average run times and identify bottlenecks

### Confluence Analytics

Track documentation usage:

1. Use Confluence analytics to see page views
2. Monitor user engagement with published content
3. Set up alerts for publishing failures

## 🎯 Next Steps

### Phase 1: Basic Implementation ✅
- [x] Set up GitHub Actions workflow
- [x] Configure secrets and permissions
- [x] Test with non-production Confluence space
- [x] Validate end-to-end flow

### Phase 2: Advanced Features (Optional)
- [ ] Add environment-specific deployments
- [ ] Implement approval gates for production
- [ ] Add Slack/Teams notifications
- [ ] Set up monitoring and alerting

### Phase 3: Full Migration (Optional)
- [ ] Deprecate Ansible publishing workflow
- [ ] Keep Ansible for local development only
- [ ] Implement advanced GitHub Actions features
- [ ] Add automated testing and validation

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/v1/)
- [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
- [Pandoc Documentation](https://pandoc.org/MANUAL.html)

---

**💡 Pro Tip**: Start with a test Confluence space to validate the workflow before pointing it at your production documentation space!

# 🌿 Branch Naming Guide

This guide explains the supported branch naming patterns that trigger our CI/CD pipeline.

## 🚀 **Supported Branch Patterns**

### 📁 **Feature Branches**
The following patterns will trigger the CI/CD pipeline for feature development:

| Pattern | Examples | Use Case |
|---------|----------|----------|
| `feature/*` | `feature/login`, `feature/user-auth` | Standard feature branches |
| `feature/**` | `feature/auth/login`, `feature/api/users` | Multi-level feature branches |
| `ft/*` | `ft/login`, `ft/user-auth` | Alternative feature prefix |
| `ft/**` | `ft/auth/login`, `ft/api/users` | Multi-level alternative features |

### 🚀 **Release Branches**
The following patterns will trigger the CI/CD pipeline for releases:

| Pattern | Examples | Use Case |
|---------|----------|----------|
| `release/*` | `release/v1.2.0`, `release/sprint-3` | Standard release branches |
| `release/**` | `release/hotfix/v1.1.1` | Multi-level release branches |
| `rel/*` | `rel/v1.2.0` | Alternative release prefix |
| `rel/**` | `rel/patch/v1.1.1` | Multi-level alternative releases |

### 🔥 **Hotfix Branches**
The following patterns will trigger the CI/CD pipeline for hotfixes:

| Pattern | Examples | Use Case |
|---------|----------|----------|
| `hotfix/*` | `hotfix/critical-bug`, `hotfix/auth-fix` | Standard hotfix branches |
| `hotfix/**` | `hotfix/security/auth-fix` | Multi-level hotfix branches |
| `hf/*` | `hf/critical-bug`, `hf/auth-bug` | Alternative hotfix prefix |
| `hf/**` | `hf/security/auth-fix` | Multi-level alternative hotfixes |

### 🏠 **Main Branches**
These branches always trigger the pipeline:
- `main` - Production branch
- `develop` - Development integration branch

## ✅ **Valid Branch Name Examples**

### With Dashes (Recommended)
```bash
# Feature branches
git checkout -b feature/user-management
git checkout -b feature/auth-system
git checkout -b ft/api-endpoints
git checkout -b ft/user-profile-update

# Release branches
git checkout -b release/v1.2.0
git checkout -b release/sprint-3-fixes
git checkout -b rel/v1.1.0

# Hotfix branches
git checkout -b hotfix/critical-security-fix
git checkout -b hotfix/login-bug-fix
git checkout -b hf/auth-token-issue
```text

### Multi-level (Advanced)
```bash
# Multi-level feature branches
git checkout -b feature/auth/login-system
git checkout -b feature/api/user-endpoints
git checkout -b ft/ui/dashboard-improvements

# Multi-level release branches
git checkout -b release/v2.0/beta-testing
git checkout -b release/hotfix/v1.1.1

# Multi-level hotfix branches
git checkout -b hotfix/security/auth-vulnerability
git checkout -b hf/performance/database-optimization
```text

## ❌ **Patterns That Won't Trigger**

These patterns will **NOT** trigger the CI/CD pipeline:

```bash
# Incorrect plurals
features/login          # Should be 'feature/login'
releases/v1.0.0         # Should be 'release/v1.0.0'
hotfixes/bug            # Should be 'hotfix/bug'

# Incorrect abbreviations
feat/login              # Should be 'feature/login' or 'ft/login'
rel-v1.0.0              # Should be 'release/v1.0.0' or 'rel/v1.0.0'
fix/bug                 # Should be 'hotfix/bug' or 'hf/bug'

# Missing slash
featurelogin            # Should be 'feature/login'
releaseV1               # Should be 'release/v1'
```text

## 🔍 **Debug Information**

When the pipeline runs, you'll see debug output in the "Quick Validation" job that shows:
- Which branch triggered the workflow
- Whether it matches any of the supported patterns
- Examples of valid branch names

## 👥 **Team Guidelines**

### For Your Dev Who Uses "ft"
✅ **These will work perfectly:**
- `ft/new-feature`
- `ft/user-dashboard`
- `ft/api/user-endpoints`

### For Standard Development
✅ **Recommended patterns:**
- `feature/descriptive-name`
- `release/version-number`
- `hotfix/issue-description`

### Best Practices
1. **Use dashes** instead of underscores: `user-management` not `user_management`
2. **Be descriptive**: `feature/user-authentication` not `feature/auth`
3. **Use lowercase**: `feature/user-management` not `feature/User-Management`
4. **Include ticket numbers** if applicable: `feature/JIRA-123-user-login`

## 🧪 **Testing Your Branch Names**

To test if your branch name will trigger the pipeline:

1. Create and push your branch:
   ```bash
   git checkout -b your-branch-name
   git push origin your-branch-name
   ```

2. Check the Actions tab in GitHub to see if the workflow triggered

3. Look at the "Debug Trigger Information" step output to confirm pattern matching

## 📞 **Need Help?**

If you're unsure about branch naming or the pipeline isn't triggering:
1. Check the debug output in the workflow logs
2. Verify your branch name matches one of the supported patterns
3. Consider using the manual trigger option in the Actions tab

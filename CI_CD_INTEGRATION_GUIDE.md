# CI/CD Integration Guide

⚠️ **WORK IN PROGRESS** ⚠️
> **Status**: These CI/CD templates are provided as examples and have not been fully tested in all environments. They should be considered work-in-progress and may require customization for your specific use case.

## Overview

This project provides **flexible CI/CD integration** that works with any major industry tool. Choose the configuration that matches your organization's CI/CD platform.

## 📁 Available Configurations

> ⚠️ **Note**: These templates are provided as starting points and require testing and customization for your environment.

The `ci-cd-templates/` directory contains ready-to-use configurations for:

### Cloud Platforms
- **GitLab CI/CD** (`gitlab-ci.yml`) - GitLab.com or self-hosted GitLab
- **GitHub Actions** (`github-actions.yml`) - GitHub.com or GitHub Enterprise
- **Azure DevOps** (`azure-pipelines.yml`) - Azure DevOps Services/Server
- **Bitbucket Pipelines** (`bitbucket-pipelines.yml`) - Atlassian Bitbucket

### Enterprise Platforms
- **Jenkins** (`Jenkinsfile`) - Jenkins CI/CD server
- **TeamCity** (`teamcity-config.txt`) - JetBrains TeamCity

## 🚀 Quick Setup

### 1. Choose Your Platform

Copy the appropriate configuration file:

```bash
# For GitLab
cp ci-cd-templates/gitlab-ci.yml .gitlab-ci.yml

# For GitHub
mkdir -p .github/workflows
cp ci-cd-templates/github-actions.yml .github/workflows/ci.yml

# For Azure DevOps
cp ci-cd-templates/azure-pipelines.yml azure-pipelines.yml

# For Bitbucket
cp ci-cd-templates/bitbucket-pipelines.yml bitbucket-pipelines.yml

# For Jenkins
cp ci-cd-templates/Jenkinsfile Jenkinsfile
```

### 2. Customize Configuration

Edit the copied file to match your environment:
- Update branch names
- Modify notification settings
- Adjust resource requirements
- Configure artifact storage

### 3. Enable in Your Platform

Follow your platform's documentation to enable CI/CD with the configuration file.

## 🔧 Pipeline Stages

All configurations include these standardized stages:

### Stage 1: **Validation** 🔍
```bash
make sanity-check      # Quick syntax and structure validation
make lint              # YAML and Ansible linting
make validate-templates # Template structure verification
```

### Stage 2: **Security** 🔒
```bash
make security-check    # Security scanning and compliance
```

### Stage 3: **Testing** 🧪
```bash
make validate          # Full validation suite
make test-render       # Template rendering tests
```

### Stage 4: **Advanced Testing** 🔬 (Optional)
```bash
molecule test          # Comprehensive functional testing
```

## 📋 Platform-Specific Notes

### GitLab CI/CD
- **Features**: Built-in Docker support, parallel jobs, security scanning
- **Best for**: GitLab users, container-based workflows
- **Requirements**: GitLab Runner with Docker executor

### GitHub Actions
- **Features**: Matrix builds, extensive marketplace, free for public repos
- **Best for**: Open source projects, GitHub-centric workflows
- **Requirements**: GitHub account, Actions enabled

### Azure DevOps
- **Features**: Enterprise integration, multi-stage pipelines, artifacts
- **Best for**: Microsoft environments, enterprise projects
- **Requirements**: Azure DevOps organization

### Jenkins
- **Features**: Extensive plugin ecosystem, self-hosted, highly customizable
- **Best for**: Enterprise environments, complex workflows
- **Requirements**: Jenkins server, appropriate plugins

### Bitbucket Pipelines
- **Features**: Integrated with Bitbucket, simple YAML configuration
- **Best for**: Atlassian tool stack, small to medium projects
- **Requirements**: Bitbucket Cloud/Server account

### TeamCity
- **Features**: Powerful build chains, detailed reporting, enterprise features
- **Best for**: Large enterprise environments, complex dependencies
- **Requirements**: TeamCity server, build agents

## 🎯 Quality Gates

### Mandatory Gates (Block Deployment)
- ❌ **Syntax errors** - Invalid YAML or Ansible syntax
- ❌ **Security violations** - Exposed secrets or insecure configurations
- ❌ **Critical lint failures** - ansible-lint production profile violations

### Warning Gates (Allow with Review)
- ⚠️ **Style violations** - Minor formatting issues
- ⚠️ **Template warnings** - Non-critical template issues
- ⚠️ **Performance concerns** - Optimization opportunities

### Optional Gates (Best Practice)
- ℹ️ **Molecule test failures** - Functional testing issues
- ℹ️ **Documentation gaps** - Missing or outdated documentation

## 🔧 Customization Options

### Environment Variables
```yaml
# Common environment variables across platforms
PYTHON_VERSION: "3.11"
ANSIBLE_VERSION: "latest"
SKIP_MOLECULE: "false"
NOTIFICATION_EMAIL: "team@company.com"
```

### Branch Strategies
```yaml
# Example branch configuration
trigger:
  branches:
    include: [main, develop, release/*]
    exclude: [feature/*, hotfix/*]
```

### Artifact Management
```yaml
# Artifact configuration
artifacts:
  - "**/*.log"           # Build logs
  - "**/test-results.*"  # Test results
  - "**/*security*"      # Security scan results
  - "**/*report*"        # Quality reports
```

## 📊 Monitoring and Reporting

### Metrics to Track
- **Build Success Rate**: Percentage of successful builds
- **Quality Gate Pass Rate**: Percentage passing all quality checks
- **Security Issue Detection**: Number and severity of security findings
- **Test Coverage**: Percentage of code covered by tests

### Dashboard Setup
Most platforms provide dashboards. Key widgets to include:
- Build status trends
- Test result summaries
- Security scan results
- Quality metrics over time

### Notifications
Configure notifications for:
- ✅ **Build success** (main branch only)
- ❌ **Build failures** (all branches)
- 🔒 **Security issues** (immediate)
- 📊 **Weekly quality reports**

## 🚨 Troubleshooting

### Common Issues

#### Permission Errors
```bash
# Solution: Add sudo where needed or use rootless containers
sudo apt-get install -y package-name
```

#### Tool Installation Failures
```bash
# Solution: Use alternative installation methods
pip install --user tool-name
# or
apt-get install python3-tool-name
```

#### Docker Not Available
```bash
# Solution: Skip Docker-dependent tests
if command -v docker &> /dev/null; then
    molecule test
else
    echo "Skipping Docker tests"
fi
```

#### Network/Proxy Issues
```bash
# Solution: Configure proxy settings
export http_proxy=http://proxy:8080
export https_proxy=http://proxy:8080
```

### Platform-Specific Troubleshooting

#### GitLab CI/CD
- Check runner availability: `Settings > CI/CD > Runners`
- Verify Docker executor: Check runner configuration
- Debug with: `gitlab-runner exec docker job-name`

#### GitHub Actions
- Check workflow syntax: GitHub's workflow validator
- Debug with: `act` (local GitHub Actions runner)
- Verify secrets: `Settings > Secrets and variables > Actions`

#### Jenkins
- Check node availability: `Manage Jenkins > Manage Nodes`
- Verify plugins: `Manage Jenkins > Manage Plugins`
- Debug with: Jenkins build console output

## 🔄 Migration Guide

### From Manual Testing
1. Start with `sanity-check` in CI/CD
2. Add `security-check` as warning-only
3. Gradually add full validation
4. Enable quality gates progressively

### Between Platforms
1. Export existing configuration
2. Map stages to new platform syntax
3. Test with non-blocking runs
4. Migrate secrets and variables
5. Update team documentation

## 📞 Support

### Getting Help
1. **Check pipeline logs** - Most issues are in the console output
2. **Validate locally** - Run `make validate` on your machine
3. **Platform documentation** - Refer to your CI/CD platform's docs
4. **Team channels** - Use established communication channels

### Contributing
To improve CI/CD configurations:
1. Test changes locally with `make validate`
2. Create feature branch for CI/CD updates
3. Test on staging environment
4. Document changes in this guide
5. Submit pull/merge request

---

**Best Practice**: Start simple with basic validation, then gradually add advanced features as your team becomes comfortable with the CI/CD pipeline.

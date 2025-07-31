# 🧪 Molecule Testing Troubleshooting Guide

## 🚨 Why Molecule Action May Not Be Starting

### 1. **Dependency Job Failures** ⚠️
The most common reason Molecule doesn't start is that one of its prerequisite jobs failed:

```yaml
needs: [super-linter, security, ansible-syntax-check]
```text

**Check these jobs first:**
- 🔍 **Super Linter** - Code quality issues
- 🛡️ **Security Scan** - Security violations or hardcoded secrets
- 🎭 **Ansible Validation** - Ansible syntax or lint errors

**Solution:** Fix the failing prerequisite jobs first.

### 2. **Skip Molecule Input** 🎮
If you manually triggered the workflow with `skip_molecule: true`:

```yaml
if: ${{ github.event.inputs.skip_molecule != 'true' }}
```text

**Check:** Look at your workflow dispatch inputs - did you set "Skip Molecule testing" to true?

### 3. **Branch or Trigger Conditions** 🌿
The workflow only runs on specific branches and events:

```yaml
on:
  push:
    branches: [main, develop, 'feature/*', 'release/*', 'hotfix/*']
  pull_request:
    branches: [main, develop, 'release/*', 'hotfix/*']
```text

**Check:** Are you on a supported branch?

### 4. **Docker Availability** 🐳
Molecule tests require Docker to be available on the runner:

```yaml
driver:
  name: docker
```text

**GitHub Actions:** Docker is available by default on `ubuntu-latest`
**Self-hosted runners:** May need Docker installation

### 5. **Molecule Configuration Issues** ⚙️
Check your molecule configuration files:

```bash
# Required files:
molecule/default/molecule.yml
molecule/default/converge.yml
molecule/default/verify.yml
```text

## 🔍 Diagnostic Steps

### Step 1: Check Workflow Status
1. Go to **Actions** tab in your repository
2. Click on the latest workflow run
3. Check the status of jobs before Molecule:
   - ⚡ Quick Validation
   - 🔍 Super Linter
   - 🛡️ Security Scan
   - 🎭 Ansible Validation

### Step 2: Check Job Dependencies
Look for these patterns in the workflow logs:

#### ✅ All Prerequisites Passed
```text
super-linter: success
security: success
ansible-syntax-check: success
```text
➡️ Molecule should start

#### ❌ Prerequisite Failed
```text
super-linter: failure
security: success
ansible-syntax-check: success
```text
➡️ Molecule will be skipped

#### ⏸️ Prerequisites Skipped
```text
super-linter: skipped
security: skipped
ansible-syntax-check: skipped
```text
➡️ Check workflow trigger conditions

### Step 3: Manual Testing
Test Molecule locally to isolate issues:

```bash
# Install dependencies
pip install -r requirements.txt

# Test molecule installation
molecule --version
molecule drivers

# List available scenarios
molecule list

# Run molecule tests locally
molecule test
```text

## 🛠️ Common Fixes

### Fix 1: Prerequisite Job Failures

#### Super Linter Issues
```bash
# Check for common linting issues
yamllint .
ansible-lint .
```text

#### Security Scan Issues
```bash
# Check for hardcoded secrets
grep -r "password\|secret\|token" . --include="*.yml"
```text

#### Ansible Validation Issues
```bash
# Check ansible syntax
ansible-playbook --syntax-check playbook.yml
ansible-lint playbook.yml
```text

### Fix 2: Molecule Configuration

#### Missing molecule.yml
Create basic molecule configuration:
```yaml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: "quay.io/ansible/ee-minimal-rhel8:latest"
    command: ${MOLECULE_DOCKER_COMMAND:-""}
    privileged: true
    pre_build_image: true
provisioner:
  name: ansible
verifier:
  name: ansible
```text

#### Missing converge.yml
Create basic converge playbook:
```yaml
---
- name: Converge
  hosts: all
  become: true
  tasks:
    - name: "Include your_role_name"
      include_role:
        name: "your_role_name"
```text

#### Missing verify.yml
Create basic verification:
```yaml
---
- name: Verify
  hosts: all
  gather_facts: false
  tasks:
    - name: Example assertion
      assert:
        that: true
```text

### Fix 3: Requirements Issues

Update requirements.txt:
```pip-requirements
ansible-core>=2.12
ansible-lint
yamllint
molecule>=3.6.1
molecule-docker~=1.1.0
docker
```text

### Fix 4: Docker Issues (Self-hosted runners)
```bash
# Install Docker
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```text

## 🔧 Enhanced Debugging

I've added enhanced debugging to the Molecule job that will show:

- Dependency job results
- Skip molecule setting
- Docker availability
- Molecule installation status
- Available scenarios
- Detailed error logs

### Reading Debug Output
Look for these sections in the Molecule job logs:

1. **🔍 Debug Molecule Prerequisites** - Shows why job started/didn't start
2. **🔍 Pre-flight Molecule Check** - Validates molecule setup
3. **📊 Environment info** - Shows versions and configuration

## 🎯 Quick Checklist

When Molecule doesn't start, check:

- [ ] Are all prerequisite jobs passing? (super-linter, security, ansible-syntax-check)
- [ ] Is `skip_molecule` set to false?
- [ ] Are you on a supported branch?
- [ ] Does the `molecule/` directory exist?
- [ ] Does `molecule/default/molecule.yml` exist?
- [ ] Are molecule dependencies in `requirements.txt`?
- [ ] Is Docker available (for self-hosted runners)?

## 📊 Workflow Visualization

```text
setup-security ✅
     ↓
quick-validation ✅
     ↓
┌─────────────┬──────────────┬────────────────────┐
│ super-linter│   security   │ ansible-syntax-check│
│     ✅      │      ✅      │        ✅          │
└─────────────┴──────────────┴────────────────────┘
                     ↓
              🧪 molecule (starts only if ALL above ✅)
                     ↓
              🚀 publish (starts only if molecule ✅)
                     ↓
              📋 summary (always runs)
```text

## 📞 Getting Help

If Molecule still doesn't start after these checks:

1. **Check the enhanced debug output** in the latest workflow run
2. **Run molecule locally** to isolate the issue
3. **Check GitHub Actions status** for platform issues
4. **Review recent changes** that might have broken the setup

The enhanced debugging will give you much more detailed information about why Molecule isn't starting!

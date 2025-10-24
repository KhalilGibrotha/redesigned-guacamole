# Jira Story Specification – Windows Server Upgrade Automation (Feasibility)

This story represents the initial feasibility and discovery phase for automating the Windows Server in-place upgrade process.  
It covers preliminary research, environment preparation, and validation of automation components required to standardize the process.

---

## 🏷️ Title
Windows Server In-Place Upgrade Automation – Discovery & Feasibility

## 👤 Requestor
Server Operations / Platform Engineering

## 📅 Date
October 2025

## 🧩 Background / Context
The current Windows Server in-place upgrade process (2016 → 2022 and 2019 → 2025) is **manual** and **error-prone**, relying on Server Operations to perform scripted pre-checks and manual CRQ coordination.  
This story seeks to determine the **technical feasibility** of automating key pre-, during-, and post-upgrade tasks using **Ansible** and existing infrastructure integrations.

Primary goals:
- Validate automation of Windows Server upgrades using **WinRM**.
- Define dependencies, guardrails, and RBAC boundaries.
- Capture requirements and integration points for subsequent Pilot and Scale phases.

---

## ✅ Requirements (Acceptance Criteria)
### Pre-Upgrade Phase
- [ ] Define **server inventory child groups** (deployment group structure) with input from Server Ops.  
- [ ] Collect metadata: server role, environment (Prod/Non-Prod), business app, and owner.  
- [ ] Detect if host is **physical or virtual** (via facts or VMware integration).  
- [ ] Validate **disk space** requirements for upgrade image.  
- [ ] Check **upgrade path eligibility** (Windows version mapping).  
- [ ] Detect **pending reboots** due to patching or updates.  
- [ ] Verify **monitoring status** and **mute alerts** (SolarWinds integration).  
- [ ] Identify **active RDP sessions** prior to upgrade.  
- [ ] Send **Teams/email notification** to downstream owners (if available in vars).  

### Upgrade Phase
- [ ] Validate ISO image availability from enterprise share.  
- [ ] Automate upgrade command execution with proper credentials.  
- [ ] Log upgrade progress and capture output.  

### Post-Upgrade Phase
- [ ] Validate OS version post-upgrade.  
- [ ] Confirm monitoring re-enabled (SolarWinds).  
- [ ] Identify failures requiring restore workflow.  
- [ ] Trigger manual QA by Application Support.  
- [ ] Record results for reporting to Server Ops.

### Restore (If Required)
- [ ] Trigger **restore from backup job** (via API or backup system integration).  
- [ ] Notify Ops of restore action and mark for review.

---

## ⚙️ Constraints
- CRQ submissions and communications remain manual, handled by Server Ops.  
- Access to monitoring and backup APIs may require new credentials or integration scope definition.  
- Testing limited to **non-production** systems in Pilot.  
- Compliance reviews required prior to Prod rollout.  

---

## 📂 Approved Scope Category
- [x] Server Provisioning & Builds  
- [x] Patching & Compliance  
- [x] Operational Runbooks  
- [x] Platform Enhancements / Platform Process Development  

---

## 👨‍💼 Manager Approval
*Pending – Leadership Review (Server Ops / Platform Engineering)*

---

## 🎯 Success Criteria (Definition of Done)
- Pre-upgrade job successfully collects all required metadata and validations.  
- Upgrade job executes successfully on a non-production system.  
- Post-upgrade checks and restore validation run cleanly.  
- Results logged and available in Splunk for audit review.  
- Server Ops and Platform Engineering validate readiness for Pilot.

---

## 💡 Impact Measurement

| Metric | Description | Estimated Value |
|--------|--------------|-----------------|
| Hours Saved | Reduction in manual upgrade time per server | TBD |
| Cost Avoided / Saved ($) | Reduced outage risk and repeat work | TBD |
| Risk Reduction | Automated validation reduces failure risk | TBD |
| Compliance Improvement (%) | Consistent pre-upgrade checks and auditability | TBD |

---

## 🗒️ Notes
- Discovery findings will drive future story decomposition into Pre-Upgrade, Upgrade, and Post-Upgrade workflows.  
- Dependencies on SolarWinds and backup systems must be clarified early.  
- WinRM connectivity and EE validation completed previously (reference: AAP Dev Loop testing).  

---

## 🔗 Tracking & Breakdown

**Primary Jira Epic:** `<Jira-####>` – Windows Server In-Place Upgrade Automation

| Jira Issue Key | Title / Description | Notes |
|----------------|---------------------|-------|
| `<Jira-####-A>` | Define Pre-Upgrade Checks & Inventory Structure | Inventory + server metadata logic |
| `<Jira-####-B>` | Implement Upgrade Orchestration | Validate EE and image mount process |
| `<Jira-####-C>` | Post-Upgrade Verification & Restore Workflow | Includes validation, monitoring, and backup triggers |

---

## 🧭 Usage Notes
- This document reflects the **Discovery → Pilot** phase.  
- Subsequent stories will refine automation details for execution and scale.  
- Feasibility validation will inform scope for institutionalization.

---

**Author:** Platform Engineering / Server Operations  
**Version:** Draft v0.3 – Discovery Phase  
**Date:** October 24, 2025

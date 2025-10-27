# Windows Server Upgrade Automation – Program Summary

This initiative aims to automate the end-to-end **Windows Server in-place upgrade process** across Server Operations, improving reliability, reducing manual workload, and standardizing upgrade execution.  
The automation effort will follow the organizational implementation model: **Discovery → Pilot → Scale → Institutionalize**, with each milestone delivering tested functionality and a documented handoff to Server Operations.

---

## 🧩 Background / Context

Current Windows Server upgrades (2016 → 2022, 2019 → 2025) are fully **manual**, involving PowerShell pre-checks, manual CRQ coordination, ISO mounting, and post-upgrade validation.  
This approach:
- Consumes significant time and coordination between Server Ops and Application Support.  
- Creates risk of inconsistency between environments.  
- Lacks end-to-end auditability and repeatability.  

Automation of this process using **Ansible Automation Platform (AAP)** will:
- Replace manual pre-checks and upgrade execution with standardized, reusable playbooks.  
- Introduce controlled integrations with CyberArk (authentication), VMware (image mounting), and Commvault (backup/restore).  
- Reduce dependency on manual CRQ and validation steps by delivering verified automation stages in incremental, testable releases.  

Each milestone’s automation will be validated on pilot systems, after which **Server Operations will integrate the automation into the standard upgrade procedure** and **update documentation accordingly**.

---

## ✅ Requirements

### Functional
- **Pre-Upgrade**
  - Server health validation and metadata collection.
  - Detection of virtual/physical systems, disk capacity, and upgrade eligibility.
  - Pending reboot, RDP session, and monitoring checks (SolarWinds integration future).
- **Backup and Restore**
  - Automated Commvault backup initiation, snapshot, and restore validation.
  - Full recovery testing of pre-upgrade backups.
- **Upgrade**
  - ISO validation and mounting (VMware API).
  - Execution of in-place upgrades via Ansible with CyberArk CCP-managed credentials.
  - Progress logging and real-time failure notifications.
- **Post-Upgrade**
  - Post-upgrade patching, validation, and reporting.
  - Integration of results with Splunk SEIM for audit and compliance visibility.

### Non-Functional
- Automation jobs must be idempotent and compliant with AAP governance standards.  
- All secrets must be handled via CyberArk CCP or AAP credential store.  
- Execution must be isolated to non-production during Pilot and Scale phases.  
- Documentation-as-code updates occur in parallel with feature delivery.

### Integration Requirements
- CyberArk CCP for secure runtime credential retrieval.  
- VMware vCenter API for ISO and snapshot operations.  
- Commvault API for backup and restore.  
- Splunk for job result logging and audit.  
- (Optional future) SolarWinds for monitoring mute/unmute automation.

---

## ⚙️ Constraints

- **CRQ creation and communication remain manual** (Server Ops responsibility).  
- Backup and monitoring integrations depend on access to third-party APIs and credentials.  
- Pilot testing restricted to pre-approved non-production systems.  
- Successive phases depend on prior Server Ops handoff and documentation updates.  
- Integration testing must comply with internal security and change management policies.  
- Execution windows constrained by maintenance schedules and change freeze periods.

---

## 🎯 Success Criteria (Definition of Done)

| Category | Success Indicator | Validation Method |
|-----------|------------------|------------------|
| **Pre-Upgrade** | Automated health and eligibility checks run successfully on pilot inventory. | Job results and Splunk log review. |
| **Backup/Restore** | Backup and restore workflows validate successfully with Commvault. | Test restores validated by Server Ops. |
| **Upgrade** | Upgrade executes successfully via AAP EE with real-time monitoring and rollback readiness. | Pilot execution report and logs. |
| **Post-Upgrade** | OS version validated, monitoring re-enabled, and post-validation report generated. | Server Ops and Application Support QA. |
| **Governance** | Each milestone formally handed off to Server Ops and documented. | Meeting minutes and process updates. |

---

## 💡 Impact Measurement (Strategic Objective Alignment)

| Strategic Objective | Measurement Focus | Expected Impact | Validation Source |
|----------------------|------------------|-----------------|------------------|
| **Accelerate Efficiency** | Reduction in manual effort and upgrade time per system. | ~60% decrease in average upgrade duration; significant reduction in manual pre-checks. | Time tracking, Ops feedback. |
| **Improve Reliability** | Standardized and auditable upgrade process. | Consistent validation across systems; fewer

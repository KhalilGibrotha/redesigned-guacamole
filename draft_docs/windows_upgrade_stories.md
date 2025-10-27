# Windows Server Upgrade Automation – Phase 1 Stories

**Epic:** Pre-Upgrade Core Functionality Delivery (~6 weeks)  
**Phase:** Discovery → Pilot  
**Goal:** Establish standardized, automated pre-upgrade validation workflows that replace manual PowerShell pre-checks.

---

## Story 1 – Define and Publish Server Inventory Structure
**Goal:** Establish child groups and metadata hierarchy for Windows upgrade targets.  
**Dependencies:** Server Ops deployment group definitions.

**Acceptance Criteria:**
- [ ] Inventory groups created in AAP (`group_vars`, child groups for Prod/Non-Prod).  
- [ ] Server Ops review and approval of group structure.  
- [ ] Documented mapping between inventory and deployment groups.

---

## Story 2 – Collect Server Metadata and Facts
**Goal:** Gather system facts (role, environment, OS version, domain, application tag).  
**Dependencies:** WinRM connectivity validated; inventory from Story 1.

**Acceptance Criteria:**
- [ ] Playbook collects metadata and writes to structured JSON or CSV.  
- [ ] Role identification logic (DB, App, Infra) confirmed by Server Ops.  
- [ ] Output stored for use in subsequent pre-checks.

---

## Story 3 – Detect Physical vs Virtual Hosts
**Goal:** Differentiate hardware type to determine backup and snapshot paths.  
**Dependencies:** VMware integration EE image.

**Acceptance Criteria:**
- [ ] Script detects `system_manufacturer` and VM tools presence.  
- [ ] Result stored as inventory fact (`host_type=physical/virtual`).  
- [ ] Validation tested on both hardware and VMware guests.

---

## Story 4 – Disk Space and Upgrade Eligibility Checks
**Goal:** Verify disk capacity and Windows version eligibility for upgrade.  
**Dependencies:** Facts from Story 2.

**Acceptance Criteria:**
- [ ] Playbook validates minimum disk space ( ≥ 20 GB ).  
- [ ] Windows edition/version mapping implemented for 2016→2022, 2019→2025.  
- [ ] Non-eligible systems flagged and reported.

---

## Story 5 – Pending Reboot and Active Session Detection
**Goal:** Prevent upgrade on systems pending reboot or with active RDP sessions.  
**Dependencies:** WinRM permissions.

**Acceptance Criteria:**
- [ ] Playbook detects reboot pending registry keys.  
- [ ] Playbook queries for active RDP sessions and records user list.  
- [ ] Combined status output to report; block upgrade if true.

---

## Story 6 – Generate Answer File for Unattended Upgrade
**Goal:** Build standardized unattend.xml based on collected facts.  
**Dependencies:** Metadata (Story 2) and eligibility (Story 4).

**Acceptance Criteria:**
- [ ] Jinja2 template created for unattend.xml with role-specific settings.  
- [ ] Playbook renders and stores file on target before upgrade.  
- [ ] File validated by Server Ops against manual process.

---

## Story 7 – Notification and Reporting Mechanism
**Goal:** Provide feedback to Server Ops and stakeholders for each pre-check run.  
**Dependencies:** Results from Stories 1-6.

**Acceptance Criteria:**
- [ ] Results written to centralized log file and/or Splunk index.  
- [ ] Optional email/Teams notification sent when checks complete.  
- [ ] Report includes eligible/ineligible status per host.

---

## Story 8 – Integrate Pre-Upgrade Workflow into AAP
**Goal:** Publish the end-to-end Pre-Upgrade job template for pilot execution.  
**Dependencies:** All prior stories complete.

**Acceptance Criteria:**
- [ ] AAP workflow built using execution environment image.  
- [ ] Job template validated on pilot inventory.  
- [ ] Server Ops executes pilot and signs off handoff.  
- [ ] Documentation updated to reflect new automation scope.

---

## Story 9 – Server Ops Handoff & Pilot Validation
**Goal:** Transition Pre-Upgrade automation to Server Ops for testing and documentation update.  
**Dependencies:** Story 8 completion.

**Acceptance Criteria:**
- [ ] Pilot servers tested with new Pre-Upgrade automation.  
- [ ] Server Ops updates manual upgrade documentation.  
- [ ] Sign-off recorded in Jira and meeting notes.  
- [ ] Feedback logged for Phase 2 (Backup & Restore).

---

## Cross-References
- **Epic:** Windows Server Upgrade Automation – Pre-Upgrade Core Functionality  
- **Next Epic:** Backup and Restore Functionality Delivery  
- **Strategic Objectives Supported:**  
  - Accelerate Efficiency  
  - Improve Reliability  
  - Enable Innovation  
  - Foster Continuous Improvement

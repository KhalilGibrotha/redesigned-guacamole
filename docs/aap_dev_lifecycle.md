# Ansible Development & Promotion Lifecycle

**SEO Automation Platform – Desired End State**

---

## 1. Purpose

This document defines the desired end state for **Ansible development, testing, and promotion to production** across the SEO Automation Platform.
It establishes a consistent, governed, and secure development loop aligned with enterprise architecture, DevSecOps, and compliance objectives.

---

## 2. Strategic Alignment

This development lifecycle directly supports the SVP’s **Strategic Automation Objectives**:

1. **Accelerate efficiency** by reducing repetitive, manual tasks.
2. **Improve reliability** through standardized, automated processes.
3. **Enable innovation** by freeing engineers’ time for high-value engineering and optimization work.
4. **Foster a culture of continuous improvement** by embedding automation practices into day-to-day operations.

Our desired state provides structure, automation reuse, and continuous testing to ensure that automation accelerates delivery while maintaining quality and compliance.

---

## 3. Anti‑Patterns and Corrective Design

During current‑state analysis, several anti‑patterns were identified across Ansible and automation workflows. The desired model eliminates these patterns and directly aligns with the strategic automation goals above.

| Anti‑Pattern                                                                       | Why It’s a Problem                                                 | Corrective Pattern (Desired State)                                                                                | Strategic Objective Supported                               |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **Ad‑hoc Ansible runs from developer workstations**                                | Creates configuration drift, bypasses RBAC and audit controls.     | Execute automation exclusively through controlled Execution Environments (EEs) managed by AAP or remote EE nodes. | *Improve reliability* and *Accelerate efficiency*           |
| **Local package installations (e.g., installing pywinrm or collections manually)** | Leads to environment drift and non‑reproducible results.           | Standardize dependencies in `execution-environment.yml` and build controlled, signed EE images.                   | *Improve reliability*                                       |
| **Direct access to production systems from Dev Spaces or local dev machines**      | Violates network segmentation and security policy.                 | Route all execution through approved non‑prod EE nodes or AAP Controller.                                         | *Improve reliability* and *Foster continuous improvement*   |
| **Inconsistent documentation or tribal knowledge**                                 | Slows onboarding, increases risk of error, inhibits collaboration. | Treat documentation as code (Markdown + linting + version control).                                               | *Accelerate efficiency* and *Foster continuous improvement* |
| **Manual promotion of playbooks and EEs**                                          | Increases risk of human error and untracked changes.               | CI/CD pipeline handles EE build, test, sign, and promotion through PAH and AAP orgs.                              | *Accelerate efficiency* and *Enable innovation*             |
| **No structured testing before merge**                                             | Leads to production instability and regressions.                   | Integrate linting and Molecule testing in Dev Spaces and CI pipelines.                                            | *Improve reliability* and *Accelerate efficiency*           |
| **Siloed teams and isolated workflows**                                            | Causes duplicated effort and inconsistent automation practices.    | Shared Dev Spaces templates, central repos, and governance‑driven processes.                                      | *Foster continuous improvement* and *Enable innovation*     |

This structured model ensures all developers follow the same standards, enforce security automatically, and reduce rework across teams.

---

## 4. Development Loop (Inner Loop)

### 4.1 Environment Overview

* **Primary IDE:** OpenShift Dev Spaces
* **Base Tooling:**

  * `ansible-dev-tools` (Ansible, ansible-lint, Molecule, pre-commit)
  * VS Code extensions (markdownlint, YAML schema validation, spell checking)
  * Markdown + Mermaid for docs-as-code
* **Authentication:** OpenShift SSO; credentials injected via Kubernetes Secrets
* **Security Boundary:** No direct access to production networks; outbound allowed only to non-prod subnets and EE nodes

### 4.2 Development Workflow

| Step | Description                                                                                                                                | Tools                              |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------- |
| 1    | **Open Workspace** – Developer launches shared Dev Spaces template; standard repos auto-clone into the workspace.                          | Dev Spaces, Git                    |
| 2    | **Write Code & Docs** – Create or update playbooks, roles, collections, and documentation-as-code (Markdown).                              | VS Code, ansible-dev-tools         |
| 3    | **Lint & Validate** – Run syntax and standards validation locally.                                                                         | ansible-lint, yamllint, pre-commit |
| 4    | **Run Molecule Tests** – Execute Molecule scenarios directly in Dev Spaces using the Docker or delegated driver for fast local validation. | Molecule                           |
| 5    | **Remote EE Testing** – Run full playbook execution inside a **remote EE node** (Podman remote) to validate environment parity.            | ansible-navigator (remote EE)      |
| 6    | **Peer Review** – Submit PR; CI automatically runs lint and Molecule tests.                                                                | GitLab/GitHub CI                   |
| 7    | **Merge & Build EE** – Upon approval, merge triggers CI pipeline that builds and signs a new EE image.                                     | ansible-builder, CI pipeline       |

> **Note:**
> Molecule is part of the inner dev loop and runs locally inside the Dev Spaces container.
> `ansible-navigator` (EE testing) is part of the extended dev loop and runs remotely, since Dev Spaces can’t launch Podman EEs directly.

---

## 5. Execution Environments (EEs)

### 5.1 Standardization

All automation runs occur inside **Execution Environments**—immutable container images built via `ansible-builder` and stored in **Private Automation Hub (PAH)** or **Quay**.

| EE Type      | Purpose                        | Example Tag                          | Build Source                      |
| ------------ | ------------------------------ | ------------------------------------ | --------------------------------- |
| **Dev EE**   | Developer and Molecule testing | `quay.myorg/aap-ee/dev:2025.10.01`   | `execution-environment.yml`       |
| **Stage EE** | Validation and QA testing      | `quay.myorg/aap-ee/stage:2025.10.01` | Same builder, locked dependencies |
| **Prod EE**  | Production job execution       | `quay.myorg/aap-ee/prod:2025.10.01`  | Signed and approved artifact      |

### 5.2 EE Lifecycle

1. **Build:** Developers define dependencies in `execution-environment.yml`.
2. **Scan:** EE image scanned for vulnerabilities via Tenable or Quay Security.
3. **Push:** Tag pushed to internal Quay and mirrored in PAH.
4. **Promote:** Tags are promoted from `dev` → `stage` → `prod` after governance approval.
5. **Consume:** AAP Controller pulls only signed, approved EE tags.

---

## 6. Promotion Model (Outer Loop)

```mermaid
flowchart LR
  A[Dev Spaces] --> B[Molecule Tests]
  B --> C[Remote EE Node (Non-Prod)]
  C --> D[Git Repository (Main Branch)]
  D --> E[CI Validation & EE Build]
  E --> F[Private Automation Hub]
  F --> G[AAP Controller – Develop Org]
  G --> H[AAP Controller – Prod Org]
```

### 6.1 Promotion Flow

| Stage                    | Description                                                                            | Control Mechanism               |
| ------------------------ | -------------------------------------------------------------------------------------- | ------------------------------- |
| **Develop**              | Code and roles authored, linted, and tested (Molecule + remote EE).                    | Dev Spaces pre-commit, Molecule |
| **Commit / Merge**       | Approved PR merges to `main`; CI builds and signs EE image, publishing to **PAH Dev**. | GitLab/GitHub CI                |
| **Stage Validation**     | EE and playbooks tested in **AAP Develop Org** against non-prod targets.               | AAP Job Templates               |
| **Governance Review**    | Architecture Board reviews compliance and cert validation; signs EE tag.               | Governance & Security           |
| **Production Promotion** | EE tag promoted to **PAH Prod**, job templates updated to reference approved tag.      | Platform Admin                  |
| **Audit & Logging**      | All job runs logged to Splunk SEIM; quarterly access audits performed.                 | Compliance Team                 |

---

## 7. RBAC, Compliance, and Governance

| Area                     | Enforcement                                                                                                    |
| ------------------------ | -------------------------------------------------------------------------------------------------------------- |
| **AAP Orgs**             | Separate **Develop** and **Prod** orgs; strict credential isolation.                                           |
| **Inventories**          | Managed centrally with separate dev/test/prod host groups.                                                     |
| **Credentials**          | Stored only in AAP Credential Store or CyberArk; never in repos.                                               |
| **Secrets**              | Mounted as OpenShift Secrets in Dev Spaces or fetched dynamically from Vault.                                  |
| **Access Control**       | Dev Spaces namespaces restricted from prod egress; only remote EE nodes may execute jobs to prod-like systems. |
| **Audit Logging**        | Splunk SEIM integration captures all job and EE runtime events.                                                |
| **Network Segmentation** | Enforced via OpenShift and F5 egress controls.                                                                 |

---

## 8. Documentation-as-Code

All supporting documentation is treated as first-class code assets.

| Type                      | Location                            | Validation                |
| ------------------------- | ----------------------------------- | ------------------------- |
| **Standards & Policies**  | `/standards/`                       | markdownlint, Vale        |
| **Developer Guides**      | `/guides/`                          | markdownlint, link checks |
| **Technical References**  | `/reference/`                       | markdownlint              |
| **Architecture Diagrams** | `/diagrams/`                        | Mermaid syntax check      |
| **Verification Matrices** | `/reference/verification_matrix.md` | Manual QA review          |

---

## 9. Developer Responsibilities

| Area              | Expectation                                                         |
| ----------------- | ------------------------------------------------------------------- |
| **Code Quality**  | Maintain lint and Molecule compliance.                              |
| **Security**      | Use approved EEs, never store secrets in code.                      |
| **Documentation** | Update relevant Markdown docs per change.                           |
| **Peer Review**   | Participate in PR reviews and testing.                              |
| **Governance**    | Follow standards for connection, authentication, and network usage. |

---

## 10. Continuous Improvement

This framework embeds continuous improvement by design:

* Automation, testing, and documentation occur in the same development loop.
* Developers receive immediate feedback via pre-commit hooks and Molecule.
* Shared repos and reusable EEs ensure consistency and reduce drift.
* Governance reviews and quarterly audits identify process improvement opportunities.
* The model scales horizontally as more teams onboard to AAP.

**Outcome:**
This approach directly supports the four Strategic Automation Objectives by:

* **Accelerating efficiency** through reduced manual steps.
* **Improving reliability** via consistent, governed pipelines.
* **Enabling innovation** by freeing engineers from repetitive execution.
* **Fostering continuous improvement** through shared standards and version-controlled documentation.

---

**Author:** SEO Platform Engineering
**Version:** Draft v1.2
**Date:** 2025-10-22

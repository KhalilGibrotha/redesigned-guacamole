---
title: AAP Windows Connection Standard (Governance Policy)
version: 1.0-draft
date: 2025-10-22
audience: Leadership, Architecture Board, Security
classification: Internal
status: Draft
---

# AAP Windows Connection Standard (Governance Policy)

## Document Information

- **Document Type**: Governance Policy
- **Audience**: Leadership, Architecture Board, Security Teams
- **Effective Date**: TBD
- **Review Cycle**: Annual
- **Owner**: Platform Architecture Team

## Purpose and Scope

This document establishes the official security and connectivity standard for managing Windows hosts through Ansible Automation Platform (AAP). This standard defines the approved protocols, transport mechanisms, and authentication methods for Windows automation connectivity.

### Scope

This standard applies to all AAP instances, Execution Environments, and automation workflows that interact with Windows-based systems within the enterprise environment.

## Approved Protocols

### Primary Protocol: PowerShell Remoting Protocol (PSRP)

PSRP is the preferred and primary protocol for Windows host management due to:

- Enhanced security features
- Native PowerShell integration
- Improved error handling and debugging
- Better session management capabilities

### Secondary Protocol: Windows Remote Management (WinRM)

WinRM may be used in specific scenarios where PSRP is not available, subject to additional security controls.

### Prohibited Protocols

The following protocols are not approved for production use:
- SSH to Windows (except for specific approved use cases)
- Telnet
- Remote Desktop Protocol (RDP) for automation
- Unencrypted communication channels

## Required Transport Security

### Transport Layer Security

All Windows connectivity must use:

- **HTTPS only** on port 5986
- **TLS version 1.2 or higher**
- **Valid SSL/TLS certificates** (no self-signed certificates in production)
- **HTTP (port 5985) is prohibited** in production environments

### Certificate Management

- Certificates must be issued by enterprise Certificate Authority
- Certificate validation must be enforced
- Certificate rotation procedures must be documented and automated where possible

## Authentication Standards

### Approved Authentication Methods (Priority Order)

1. **Kerberos Authentication** (Preferred)
   - Integrated with Active Directory
   - No credential storage required
   - Audit trail maintained

2. **Certificate-based Authentication**
   - For service accounts where Kerberos is not feasible
   - Certificates managed through enterprise PKI

3. **CredSSP** (Limited Use)
   - Only for specific scenarios requiring credential delegation
   - Requires explicit approval and documentation
   - Enhanced monitoring required

4. **NTLM** (Fallback Only)
   - Legacy systems only
   - Requires security exception
   - Enhanced logging and monitoring required

### Prohibited Authentication Methods

- Plain text credentials
- Hardcoded passwords in playbooks
- Shared service accounts without proper rotation

## Noncompliance Handling

### Bootstrap Exceptions

Limited exceptions may be granted for:
- Initial system provisioning
- Emergency recovery procedures
- Legacy system integration (temporary)

### Exception Process

1. Security exception request must be submitted
2. Business justification required
3. Compensating controls must be implemented
4. Time-limited approval with review schedule

## Enforcement Mechanisms

### Technical Controls

1. **Ansible Lint Rules**
   - Custom rules to detect non-compliant connection methods
   - Integration with pre-commit hooks
   - CI/CD pipeline validation

2. **AAP Organization Controls**
   - Job template restrictions
   - Inventory variable validation
   - Execution Environment enforcement

3. **Network Controls**
   - Firewall rules blocking HTTP (5985)
   - Network segmentation for automation traffic
   - Monitoring of connection attempts

### Monitoring and Auditing

- All Windows connections logged to SIEM
- Regular compliance assessments
- Automated compliance reporting
- Incident response procedures for violations

## Roles and Responsibilities

### Platform Architecture Team
- Policy maintenance and updates
- Technical standard definition
- Compliance monitoring oversight

### Security Team
- Security exception approval
- Audit and compliance validation
- Incident investigation

### Development Teams
- Implementation compliance
- Exception request submission
- Security control testing

### Platform Operations
- Technical implementation
- Monitoring and alerting
- Remediation activities

## Compliance and Validation

### Regular Assessments

- Quarterly compliance reviews
- Annual policy review and update
- Continuous monitoring through automation

### Validation Requirements

- New Windows integrations must demonstrate compliance
- Existing integrations must be assessed annually
- Non-compliance issues must be remediated within defined timeframes

## References

### External Standards
- Center for Internet Security (CIS) Windows Benchmarks
- NIST Cybersecurity Framework
- Microsoft Security Baselines

### Internal Policies
- Enterprise Security Policy
- Network Security Standards
- Certificate Management Policy
- Access Control Standards

## Document Control

### Revision History

| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| 1.0-draft | 2025-10-22 | Initial draft | TBD |

### Approval Authority

- **Policy Owner**: Chief Information Security Officer
- **Technical Authority**: Platform Architecture Board
- **Final Approval**: Enterprise Architecture Council
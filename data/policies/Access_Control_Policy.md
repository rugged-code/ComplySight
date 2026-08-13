# Access Control Policy

**Company:** NovaTech Solutions
**Policy ID:** SEC-POL-042
**Version:** 1.0
**Effective Date:** January 1, 2026
**Owner:** Information Security Department

## 1. Purpose
The purpose of this policy is to establish the rules and requirements for granting, managing, and revoking access to NovaTech Solutions' information systems, networks, and data. This policy ensures that access is provisioned based on the principle of least privilege, protecting company assets from unauthorized access, modification, or destruction.

## 2. Scope
This policy applies to all NovaTech Solutions employees, contractors, consultants, temporary staff, and third-party vendors who require access to company-owned or managed networks, applications, databases, and physical facilities.

## 3. Definitions
*   **Principle of Least Privilege (PoLP):** The practice of limiting access rights for users to the bare minimum permissions they need to perform their work.
*   **Multi-Factor Authentication (MFA):** An authentication method that requires the user to provide two or more verification factors to gain access to a resource.
*   **Privileged Access:** Elevated system access rights, such as domain administrator, database administrator, or root access, which allow users to bypass standard security controls or alter system configurations.
*   **Service Account:** A non-human account used by an application, system, or service to interact with other systems.

## 4. Policy Requirements

### 4.1 Authentication Requirements
All user accounts must have Multi-Factor Authentication (MFA) enabled and enforced before the user is granted access to any NovaTech Solutions network, application, or system. 

### 4.2 Password Complexity and Rotation
User passwords must be a minimum of 14 characters in length and include at least one uppercase letter, one lowercase letter, one numeric digit, and one special character. Passwords must be changed every 90 days, and users cannot reuse any of their last 5 passwords.

### 4.3 Standard Access Provisioning
All requests for standard system access must be submitted through the IT Service Management (ITSM) portal. Standard access requires documented approval from the requestor’s direct manager prior to account creation or permission assignment.

### 4.4 Privileged Access Provisioning
Requests for Privileged Access (e.g., system administrators, database administrators) must be explicitly approved by both the requestor's direct manager and the Director of Information Security. Privileged access must be provisioned to a separate, dedicated administrative account, not the user's standard daily-use account.

### 4.5 Access Revocation Upon Termination
The IT Operations team must disable all network and system access for departing personnel within 4 hours of the official termination time provided by Human Resources. 

### 4.6 Quarterly Access Reviews
Department managers must review and certify the access rights of all their direct reports on a quarterly basis. Managers must submit their access review certifications to the compliance portal within 14 days of the quarter's end. Any uncertified access will be automatically suspended on the 15th day.

### 4.7 Session Timeout
All interactive system sessions, including workstations, web applications, and VPN connections, must be configured to automatically lock or log out the user after a maximum of 15 minutes of inactivity.

### 4.8 Vendor and Third-Party Access
Third-party vendor access accounts must be provisioned with a hard expiration date not exceeding 30 days from the date of creation. An internal NovaTech Solutions employee must be designated as the sponsor for every vendor account and must manually request an extension if access is required beyond 30 days.

### 4.9 Prohibition of Shared Accounts
The use of shared or generic user accounts (e.g., "marketing_team", "guest_user") for interactive login is strictly prohibited. Every individual accessing NovaTech systems must be issued a unique, named user account.

### 4.10 Remote Network Access
Remote access to the NovaTech Solutions internal network must be established exclusively through the company-approved Virtual Private Network (VPN) client. The VPN client must be configured to disable split-tunneling, forcing all internet traffic through the corporate network inspection tools.

## 5. Roles and Responsibilities
*   **Information Security Department:** Responsible for defining access control standards, monitoring compliance, and approving privileged access requests.
*   **IT Operations:** Responsible for the technical provisioning, modification, and revocation of access rights in accordance with approved requests.
*   **Department Managers:** Responsible for approving access requests for their subordinates and conducting mandatory quarterly access reviews.
*   **End Users:** Responsible for safeguarding their credentials, not sharing accounts, and reporting unauthorized access immediately to the IT Helpdesk.

## 6. Exceptions

### 6.1 Legacy Systems
Legacy systems that inherently cannot support Multi-Factor Authentication (MFA) are exempt from requirement 4.1, provided that the system is isolated on a restricted network segment and the exception is formally documented and approved by the Chief Information Security Officer (CISO).

### 6.2 Service Accounts
Automated service accounts are exempt from the 90-day password rotation requirement (4.2) and MFA requirement (4.1), provided their credentials are dynamically managed and rotated by the enterprise secrets management vault.

### 6.3 Break-Glass Accounts
Emergency "break-glass" administrative accounts used for disaster recovery are exempt from standard provisioning approvals (4.4). However, the use of these accounts must automatically trigger a high-priority alert to the Security Operations Center (SOC) within 1 minute of login.

## 7. Violations and Enforcement
Any employee found to have violated this policy may be subject to disciplinary action, up to and including termination of employment. Third parties violating this policy may have their contracts terminated and access immediately revoked. 

## 8. Policy Review
This policy must be reviewed and updated at least annually by the Information Security Department to ensure alignment with business objectives, technological changes, and emerging threats.

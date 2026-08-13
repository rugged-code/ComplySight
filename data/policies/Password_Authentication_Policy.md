# Password & Authentication Policy

**Company:** NovaTech Solutions
**Policy ID:** SEC-POL-015
**Version:** 1.0
**Effective Date:** January 1, 2026
**Owner:** Identity and Access Management (IAM) Department

## 1. Purpose
The purpose of this Password & Authentication Policy is to establish a secure framework for verifying the identities of users and systems accessing NovaTech Solutions' corporate networks, applications, and data. This policy defines the minimum standards for password creation, rotation, and multi-factor authentication to protect against credential theft, brute-force attacks, and unauthorized access.

## 2. Scope
This policy applies to all NovaTech Solutions employees, contractors, vendors, and automated service accounts that require authentication to access corporate information assets, including internal networks, cloud applications, email systems, and remote access gateways.

## 3. Definitions
*   **Multi-Factor Authentication (MFA):** An authentication mechanism requiring two or more independent credentials (factors) to verify a user's identity (e.g., something you know, something you have, something you are).
*   **Service Account:** A specialized, non-human account used by operating systems, databases, or applications to execute background tasks or integrate with other systems.
*   **Brute-Force Attack:** A trial-and-error method used by attackers to decode encrypted data or discover passwords by systematically attempting all possible combinations.
*   **Enterprise Password Manager:** A centrally managed, approved software application used to securely generate, store, and retrieve complex passwords.

## 4. Policy Requirements

### 4.1 Minimum Password Length
All user-created passwords for interactive accounts must contain a minimum of 15 characters.

### 4.2 Password Complexity
Passwords must include characters from all four of the following categories: at least one uppercase letter (A-Z), at least one lowercase letter (a-z), at least one numeric digit (0-9), and at least one special character (e.g., !, @, #, $, %, ^, &, *).

### 4.3 Password Expiration and Rotation
User passwords must be reset at least once every 180 days. Accounts that have not had a password reset within this timeframe will be automatically locked by the directory service.

### 4.4 Password History
Systems must enforce a password history restriction preventing users from reusing any of their previous 10 passwords. 

### 4.5 Account Lockout Threshold
User accounts must automatically lock after 5 consecutive failed login attempts within a rolling 15-minute window.

### 4.6 Account Lockout Duration
Once an account is locked due to failed authentication attempts, it must remain locked for a minimum of 30 minutes unless identity is manually verified and the account is unlocked by the IT Service Desk.

### 4.7 Multi-Factor Authentication (MFA) Enforcement
MFA must be enforced for all interactive logins originating from outside the corporate local area network (LAN), including VPN connections, cloud-based email access, and external web application portals.

### 4.8 Hardcoded Credentials Prohibition
Passwords, API keys, and authentication tokens must never be hardcoded into source code, automation scripts, or plaintext configuration files. 

### 4.9 Browser Storage Prohibition
Employees are strictly prohibited from using the built-in password saving features of web browsers (e.g., Chrome, Edge, Safari) to store corporate credentials. All credentials must be stored in the approved Enterprise Password Manager.

### 4.10 Default Vendor Passwords
All default, factory, or vendor-supplied passwords on hardware devices and software applications must be changed to meet the complexity requirements of this policy before the asset is connected to the production network.

## 5. Roles and Responsibilities
*   **Identity and Access Management (IAM) Department:** Responsible for implementing authentication controls, managing the directory service, and provisioning MFA tokens.
*   **IT Security:** Responsible for monitoring authentication logs for suspicious activity and conducting periodic password audits.
*   **System Administrators:** Responsible for ensuring all systems under their management are configured to enforce the password rules outlined in this document.
*   **End Users:** Responsible for memorizing or securely storing their passwords, reporting lost MFA devices immediately, and refraining from sharing authentication credentials.

## 6. Exceptions

### 6.1 Automated Service Accounts
Non-interactive service accounts are exempt from the 180-day rotation requirement (Requirement 4.3) provided they are managed by the enterprise secret vault, which is configured to automatically rotate their credentials every 30 days.

### 6.2 Legacy Mainframe Systems
Legacy systems that possess a hard-coded technical limitation capping passwords at 8 characters are exempt from the minimum length rule (Requirement 4.1). These systems must be segmented on a restricted network and can only be accessed via an MFA-protected jump server.

### 6.3 Public Kiosk Accounts
Shared, highly restricted guest accounts used exclusively for public-facing informational kiosks are exempt from the account lockout threshold (Requirement 4.5) to prevent intentional denial-of-service, provided these accounts have zero access to corporate data or the internal intranet.

## 7. Violations and Enforcement
Any attempt to bypass authentication controls, share passwords, or use unauthorized password management tools constitutes a violation of this policy. Violations will be handled in accordance with the corporate Disciplinary Policy and may result in immediate suspension of access privileges, formal reprimand, or termination of employment.

## 8. Policy Review
The Identity and Access Management (IAM) Department will review and update this policy annually, or in response to significant shifts in authentication technologies (e.g., a transition to passwordless architecture) or regulatory compliance requirements.

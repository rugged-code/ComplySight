# Device Usage Policy

**Company:** NovaTech Solutions
**Policy ID:** IT-POL-030
**Version:** 1.0
**Effective Date:** January 1, 2026
**Owner:** IT Asset Management Department

## 1. Purpose
The purpose of this Device Usage Policy is to establish clear and testable requirements for the acceptable use, physical security, and technical maintenance of all devices used to access NovaTech Solutions' corporate networks and data. This ensures the protection of company assets against loss, compromise, or misuse.

## 2. Scope
This policy applies to all NovaTech Solutions employees, contractors, and third-party vendors. It covers all company-issued hardware (laptops, desktop computers, mobile devices, tablets, and peripherals) as well as explicitly approved Bring Your Own Device (BYOD) personal assets that access corporate systems.

## 3. Definitions
*   **Company-Issued Device:** Any computing hardware purchased, leased, or owned by NovaTech Solutions and assigned to personnel.
*   **Bring Your Own Device (BYOD):** A personally owned mobile device or computer that has been authorized by the IT department to access corporate email or applications.
*   **Mobile Device Management (MDM):** Centralized software used by the IT department to administer, secure, and enforce policies on mobile devices and laptops.
*   **Jailbreaking/Rooting:** The process of intentionally bypassing manufacturer or operating system restrictions to gain unauthorized privileged access to a device's file system.

## 4. Policy Requirements

### 4.1 Device Registration
All hardware devices (company-issued or BYOD) utilized to access internal corporate resources must be formally registered in the IT Asset Management portal within 48 hours of physical receipt or BYOD approval.

### 4.2 MDM Enrollment Requirement
All mobile devices (smartphones and tablets) that synchronize corporate email, calendars, or contact data must have the official NovaTech Mobile Device Management (MDM) profile actively installed and communicating with the management server.

### 4.3 Operating System Updates
Users must install approved and IT-pushed Operating System (OS) security updates within 14 calendar days of their release to the enterprise update portal.

### 4.4 Prohibited Software Installation
The downloading, installation, or execution of peer-to-peer (P2P) file-sharing applications, cryptocurrency mining software, and unapproved remote desktop tools is strictly prohibited on all company-issued devices.

### 4.5 Physical Security and Unattended Devices
Company-issued laptops and mobile devices must not be left visible and unattended in public spaces, shared workspaces, or vehicles. When not in active use in a non-secure location, devices must be secured in a locked drawer, cabinet, or trunk.

### 4.6 Jailbreaking and Rooting Prohibition
Connecting a jailbroken (iOS) or rooted (Android) device to any NovaTech Solutions logical network, including the guest Wi-Fi network, is strictly prohibited. 

### 4.7 Lost or Stolen Device Reporting
The loss, theft, or suspected physical compromise of any device containing NovaTech Solutions data must be reported to the IT Helpdesk and Security Operations Center (SOC) within 24 hours of the user discovering the incident.

### 4.8 Asset Return Upon Termination
All company-issued hardware, including laptops, charging cables, corporate badges, and hardware authentication tokens, must be surrendered to the IT Asset Management Department no later than 5:00 PM local time on an employee's final date of termination or contract end.

### 4.9 Local Administrator Rights Restriction
Standard enterprise users are strictly prohibited from holding local administrator or root privileges on company-issued Windows or macOS endpoint devices. 

### 4.10 Unauthorized External Hardware
Connecting unauthorized external media, including personal USB flash drives, external hard drives, or non-company-issued Bluetooth peripherals, to company-issued laptops is prohibited and must be enforced by endpoint port-control software.

## 5. Roles and Responsibilities
*   **IT Asset Management Department:** Responsible for maintaining the hardware inventory, provisioning devices, and collecting returned assets.
*   **Security Operations Center (SOC):** Responsible for monitoring compliance with MDM, patching, and unauthorized software requirements.
*   **Department Managers:** Responsible for ensuring their team members return assets upon termination and for approving specific BYOD requests.
*   **End Users:** Responsible for the physical security of their assigned devices, reporting losses promptly, and applying required updates.

## 6. Exceptions

### 6.1 Developer Administrator Rights
Software Engineers and Systems Architects are exempt from the Local Administrator Rights Restriction (Requirement 4.9) solely on their primary workstation, provided they have completed the "Secure Developer Workstation" training module and obtained documented approval from the VP of Engineering.

### 6.2 Specialized R&D Testing Devices
Dedicated laboratory devices used exclusively by the Research & Development team for vulnerability analysis are exempt from MDM Enrollment (Requirement 4.2) and Operating System Updates (Requirement 4.3), provided these devices are permanently isolated on an offline, air-gapped network segment.

### 6.3 Executive Travel Loaners
"Burner" devices issued specifically for executive travel to high-risk geographic regions are exempt from the 14-day OS update requirement (Requirement 4.3) while the executive is in transit, but must be wiped and destroyed by IT immediately upon return.

## 7. Violations and Enforcement
Failure to adhere to this Device Usage Policy may result in the immediate revocation of network access privileges, confiscation of the device in question, and formal disciplinary action. Willful destruction or failure to return company property may result in financial liability and legal action.

## 8. Policy Review
This policy will be reviewed and updated annually by the IT Asset Management Department and the Chief Information Officer (CIO) to ensure it remains relevant to the evolving technology landscape and organizational risk profile.

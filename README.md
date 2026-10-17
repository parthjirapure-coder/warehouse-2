# 🏢 Warehouse Management (v3)



An intelligent, real-time Warehouse Management System (WMS) built with Flask, SQLite, and Google Sheets Live Sync. Features AI natural language movement logging, real-time live performance tracking for managers and employees, soft deletion & supervisor task restoration, QR code verification, role-based access control, active team presence monitoring, and automatic streaming of all warehouse operations to Google Sheets.



---



## 🌟 Key Features



### 1. 👥 Role-Based Dashboards & Workflows



- **Supervisor Command Center (`/supervisor`)**:

  - **⚡ Real-Time Performance Center**:

    - **⚡ Manager Performance Panel**: Real-time tracking of manager verifications (✔), issue resolutions (🚨), flags raised (✖), and computed performance scores.

    - **⚡ Employee Performance Panel**: Real-time tracking of employee total logs, verified logs, flagged logs, accuracy rates, and performance scores.

  - **⚡ Live Activity Stream with Task Auditing**:

    - Complete real-time audit trail of all warehouse activities.

    - **Soft Deletion & Task Recovery**: Tasks deleted by managers remain visible in Supervisor under the **`🗑️ Deleted Tasks`** tab tagged with `DELETED` and the manager's ID. Supervisors can **`↩️ Restore`** records back to the Active stream or permanently purge them.

    - Filter tabs: **`📋 All Tasks`**, **`⚡ Active`**, and **`🗑️ Deleted Tasks`**.

  - **🟢 Active Users (Currently Working)**: Real-time team presence roster placed prominently with 12s disconnection timeouts.

  - **✏️ Live Credential Editing**: Change display names and reset passwords for any team member with an interactive glassmorphism modal.

  - **Open & Resolved Issues Tracking**: Monitor flags, damage reports, interactive comments, and manager resolutions.

  - **User & QR Administration (`/users`)**: Create, enable/disable, delete users, and regenerate QR codes.

  - **Direct Google Sheet Live Update Link**: One-click link to the connected Google Spreadsheet.



- **Manager Control Center (`/manager`)**:

  - **⚡ Employee Performance Panel**: Real-time employee tracking positioned directly above Verify Live Activity for frontline oversight.

  - **⚡ Verify Live Activity**: Instant 1-click verification (`✔ Verified`, `✖ Flagged`, `🗑️ Delete`) without browser popups or latency.

  - **🚨 Open Issues & Flags**: Investigate damage/missing inventory flags with employee photo attachments and interactive discussion threads.

  - **Common Terminal Broadcasts**: Send warehouse-wide priority messages and confidential direct messages.



- **Employee Workstation (`/employee`)**:

  - **🤖 AI Natural Language Multi-Item Logging**:

    - State-of-the-art AI assistant powered by Groq Qwen-27B (with robust local rule-based fallback).

    - Supports prompts like `"add 70 sofa, 80 car, 90 wheel"`.

    - **Auto-Confirmation**: Automatically parses and confirms item entries immediately without requiring extra button presses.

    - **Interactive Clarification**: Automatically detects missing parameters (e.g. Movement Direction `IN`/`OUT`, Notes/Bay) and prompts only for remaining criteria before auto-logging.

  - **📋 My Recent Activity Management**: Employees can review and delete their own recently logged tasks with instant feedback.

  - **📊 Bulk Excel & CSV File Import**: Drag-and-drop or select `.xlsx`, `.xls`, or `.csv` files with automated column detection, interactive preview table, and 1-click batch logging.

  - **📥 Ready-to-use Sample Templates**: Downloadable `.xlsx` and `.csv` templates.

  - **QR Code Scanner**: Integrated camera and file QR scanner for instant item lookup.

  - **Issue Reporting**: File damaged or missing item reports with instant photo capture and priority flags.



---



### 2. ⚡ Real-Time Zero-Latency Synchronization



- **Server-Sent Events (SSE) & BroadcastChannel**:

  - Direct connection via `/api/live_activity/stream` with 1-second auto-reconnect.

  - Peer-to-peer `BroadcastChannel` (`warehouse_live_activity`) relays actions with 0ms local cross-tab latency.

  - Fallback background polling every 2.5s guarantees state consistency even across browser wakeups.

  - Performance tables, active user counters, and activity streams update seamlessly without full page refreshes.



---



### 3. 📊 Live Google Sheets Automated Sync (7 Sheets in 1)



All warehouse operations automatically synchronize to a single Google Spreadsheet using an asynchronous background queue (`sheet_sync_queue`) with Apps Script v4 in-place row updating:



| Sheet Tab | Contents |

| :--- | :--- |

| **`Manager Performance`** | Manager ID, name, verified logs, resolved issues, flags raised, performance score |

| **`Employee Performance`** | Employee ID, total logs, verified logs, flagged logs, accuracy rate, score |

| **`Manager Report`** | Real-time status report of manager verifications and account activity |

| **`Employee Report`** | Item-by-item chronological log of all employee activities |

| **`Live Movements`** | Complete audit trail of IN/OUT movements, quantities, timestamps, status |

| **`Issues & Flags`** | Open & resolved issues, issue types, resolution notes, managers assigned |

| **`Team Presence`** | Real-time roster of who is currently online (working) vs logged out |



---



### 4. 🔐 Security & User Management



- **Streamlined Login**: Clean and secure login interface without sample placeholders or demo buttons.

- **Password Security**: Passwords are saved as one-way secure hashes using `werkzeug.security.generate_password_hash`.

- **Credential Administration**: Supervisors can edit display names, reset passwords, or adjust roles (`SUP001` is protected).

- **Presence Heartbeat**: Team members ping every 2 seconds (`/api/presence/ping`). Disconnections timeout in 12 seconds, and tab exits broadcast an offline beacon via `navigator.sendBeacon`.



---



## 🚀 Quick Start Guide



### Prerequisites

- Python 3.10+ installed

- Web browser (Chrome, Edge, Firefox, Safari)



### 1. Installation

Clone or navigate to the project directory and install the required dependencies:



```bash

cd warehouse_ai_v3

pip install -r requirements.txt

```



### 2. Run the Application

Launch the Flask development server:



```bash

python app.py

```




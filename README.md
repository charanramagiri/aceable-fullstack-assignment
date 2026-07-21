# 🔎 Aceable Event Search System

## Overview

Aceable Event Search System is a full-stack web application developed as part of the **Aceable Cyber Solutions Full Stack Assignment**.

The application allows users to upload AWS VPC Flow Log event files, automatically parses each uploaded file, stores every event in a SQLite database using Django ORM, and provides fast search capabilities through a responsive React interface.

The backend follows a modular service-oriented architecture where event parsing, file handling, database operations, and API endpoints are cleanly separated, making the application easy to maintain and extend. The data access layer is implemented using Django ORM, allowing the database backend to be switched from SQLite to PostgreSQL in the future with minimal code changes.

---

# 📌 Features

## Backend Features

* Upload one or more AWS VPC Flow Log files
* Validate uploads and prevent duplicate file uploads
* Parse uploaded files immediately during upload
* Store every parsed event in a SQLite database using Django ORM
* Search events using:

  * Search String
  * Earliest Time
  * Latest Time
* Search across multiple event attributes including:

  * Account ID
  * Instance ID
  * Source IP
  * Destination IP
  * Action
  * Log Status
* Return matching events with execution time
* Service-oriented backend architecture
* Database-agnostic design ready for PostgreSQL migration

### Frontend Features

* Modern responsive interface
* Multiple file upload
* Search form with validation
* Loading indicators
* Success and error notifications
* Responsive results table
* Summary cards displaying:

  * Total Matches
  * Search Time

---

## Architecture

```text
                    React (Vite)
                         │
                         ▼
                Django REST API
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
 Save Uploaded File              Parse Uploaded File
 (uploads/events/)                      │
        │                               ▼
        │                     SQLite Database
        │                    (Django ORM)
        │                               │
        └──────────────► Search API ◄───┘
                         │
                         ▼
                    JSON Response
```

---

# 🛠 Tech Stack

## Backend

* Python
* Django
* Django REST Framework
* django-cors-headers

## Frontend

* React
* Vite
* Axios
* CSS

---

# 📂 Project Structure

```text
aceable-fullstack-assignment/
│
├── backend/
│   │
│   ├── config/
│   │
│   ├── events/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── uploads/
│   │   └── events/
│   │
│   └── db.sqlite3        (development only)
│
├── frontend/
│   └── src/
│       ├── api/
│       ├── components/
│       ├── pages/
│       └── styles/
│
└── README.md
```

---

# Database Design

The application stores parsed event data using two related models.

### UploadedFile

Stores metadata about every uploaded event file.

| Field | Description |
|-------|-------------|
| filename | Original uploaded filename |
| uploaded_at | Upload timestamp |
| event_count | Number of parsed events |

### Event

Stores each parsed event as an individual database record linked to its uploaded file.

Important searchable fields include:

- account_id
- instance_id
- srcaddr
- dstaddr
- action
- log_status
- starttime
- endtime

The relationship between UploadedFile and Event is **One-to-Many**, allowing every uploaded file to own multiple parsed events.

---

# ⚙️ Installation

## Clone Repository

```bash
git clone <repository-url>
cd aceable-fullstack-assignment
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

python manage.py runserver
```

Backend runs on:

```text
http://127.0.0.1:8000
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

---

# 🔗 API Endpoints

## Health Check

```http
GET /api/health/
```

---

## Upload Files

```http
POST /api/upload/
```

Content-Type:

```text
multipart/form-data
```

---

## Search Events

```http
POST /api/search/
```

Example Request

```json
{
  "search": "REJECT",
  "earliest_time": 1725850449,
  "latest_time": 1725855086
}
```

Example Response

```json
{
  "count": 56,
  "search_time": 0.018,
  "results": [
    {
      "file_name": "xaa",
      "srcaddr": "159.62.125.136",
      "dstaddr": "30.55.177.194",
      "action": "REJECT",
      "log_status": "OK"
    }
  ]
}
```

---

# 🏗 Architecture

The backend follows a service-oriented architecture to separate business logic from API endpoints.

```text
events/

api/
├── health_views.py
├── upload_views.py
└── search_views.py

services/
├── parser_service.py
├── upload_service.py
├── search_service.py
└── cache_service.py
```

This structure improves readability, maintainability, and scalability.

---

## Design Decisions

* Uploaded files are saved locally for reference and debugging.
* Event files are parsed immediately during upload.
* Parsed events are stored in a SQLite database instead of an in-memory cache.
* Django ORM is used for all database operations, avoiding database-specific code.
* The application is database-agnostic and can be migrated to PostgreSQL by updating the database configuration.
* Search operations are performed directly by the database using indexed fields for improved scalability.
* Duplicate file uploads are prevented by validating filenames before processing.
* Backend responsibilities are separated into dedicated services for upload handling, parsing, searching, and business logic.

---

## Notes

- Uploaded files are stored locally under `uploads/events/` for development and debugging purposes.
- The SQLite database (`db.sqlite3`) and uploaded files are excluded from version control using `.gitignore`.
- When the project is cloned, a fresh database is created using Django migrations and users can upload their own event files for testing.

---

# 👨‍💻 Author

**Charan Ramagiri**

Built as part of the Aceable Cyber Solutions Full Stack Assignment.

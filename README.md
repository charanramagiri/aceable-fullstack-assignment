# Aceable Event Search System

Aceable Event Search System is a full-stack web application for uploading, storing, and searching AWS VPC Flow Log event files. It was developed as part of the **Aceable Cyber Solutions Full Stack Developer Assignment**.

The frontend is built with **React** and **Vite**, while the backend uses **Django REST Framework**. Uploaded files are validated, parsed, stored in SQLite using Django ORM, and can be searched efficiently through REST APIs.

---

## Features

- Upload one or more AWS VPC Flow Log files
- Validate every file before it is saved
- Reject invalid files without writing them to disk or the database
- Prevent duplicate uploads by filename
- Store uploaded-file metadata and parsed events in SQLite
- Search by text, earliest time, and latest time
- Display matching events, result count, and search execution time
- Run the application locally or with Docker Compose

---

## Tech Stack

### Frontend
- React
- Vite
- Axios

### Backend
- Django
- Django REST Framework

### Database
- SQLite (Django ORM)

### Containerization
- Docker
- Docker Compose

---

## Architecture

```text
                React (Vite)
                     │
                     ▼
           Django REST API
                     │
             Upload Validation
                     │
             Save Uploaded File
                     │
               Parse Event File
                     │
                     ▼
          SQLite Database (ORM)
                     │
                     ▼
              Search API Results
```

---

## Project Structure

```text
aceable-fullstack-assignment/
│
├── backend/
│   ├── config/
│   ├── events/
│   │   ├── api/
│   │   ├── migrations/
│   │   ├── services/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles/
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
│
├── uploads/
│   └── events/
│
├── docker-compose.yml
└── README.md
```

---

## Prerequisites

- Python 3.12 or later
- Node.js 22 or later
- npm
- Docker and Docker Compose (optional)

---

# Local Setup

## Backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

### Windows PowerShell

```bash
venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies and start Django:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend API:

```
http://127.0.0.1:8000/api/
```

---

## Frontend

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

Linux/macOS:

```bash
cp .env.example .env
```

Frontend:

```
http://localhost:5173
```

---

## Environment Variables

The frontend uses a single environment variable.

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API base URL |

Example:

```env
VITE_API_URL=http://127.0.0.1:8000/api/
```

When running with Docker Compose, this value is automatically overridden.

---

# Docker Compose

From the project root:

```bash
docker compose up --build
```

The application will be available at:

Frontend:

```
http://localhost:5173
```

Backend:

```
http://localhost:8000/api/
```

Stop the containers:

```bash
docker compose down
```

Docker support is included to provide a consistent development environment and simplify project setup.

---

# API Endpoints

## Health Check

```http
GET /api/health/
```

---

## Upload Event Files

```http
POST /api/upload/
Content-Type: multipart/form-data
```

Upload one or more files using the repeated **files** form field.

Behavior:

- Validates every uploaded file
- Rejects invalid files (HTTP 400)
- Rejects duplicate filenames (HTTP 409)
- Parses valid events
- Stores uploaded-file metadata
- Stores parsed events in SQLite

Example response:

```json
{
  "status": "success",
  "message": "1 file(s) uploaded successfully.",
  "files": [
    "uploads/events/flow-log.txt"
  ]
}
```

---

## Search Events

```http
POST /api/search/
Content-Type: application/json
```

Example request:

```json
{
  "search": "REJECT",
  "earliest_time": 1725850449,
  "latest_time": 1725855086
}
```

All search filters are optional.

Example response:

```json
{
  "count": 1,
  "search_time": 0.0012,
  "results": [
    {
      "file_name": "flow-log.txt",
      "srcaddr": "10.0.0.1",
      "dstaddr": "10.0.0.2",
      "action": "REJECT",
      "log_status": "OK"
    }
  ]
}
```

---

# Data Storage

The application stores:

- Uploaded source files in:

```
uploads/events/
```

- Uploaded file metadata in the **UploadedFile** model
- Parsed event records in the **Event** model
- Event data in **SQLite** using Django ORM

The following are excluded from version control:

- `backend/db.sqlite3`
- `uploads/events/`

This allows every clone of the repository to start with a clean local environment.

---

# Design Decisions

- Uploaded files are validated before being stored.
- Parsed events are stored in SQLite using Django ORM.
- Bulk database inserts are used for efficient event imports.
- Duplicate uploads are prevented using filename validation.
- Search operations query the database instead of reading uploaded files.
- The project supports both local development and Docker Compose.

---

# Verification

Backend:

```bash
cd backend
python manage.py check
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

Docker:

```bash
docker compose up --build
```

Verify:

- File upload works
- Search works
- Docker containers start successfully

---
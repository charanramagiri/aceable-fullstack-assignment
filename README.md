# Aceable Event Search System

A full-stack application built for the Aceable Cyber Solutions assignment to import, store, and search AWS VPC Flow Log events.

The project consists of a **Django REST API** backend and a **React + Vite** frontend. Users can upload compressed log archives, import events into SQLite, and search them through a responsive web interface.

---

## Features

- Upload one or more `.tgz` or `.tar.gz` archives
- Import AWS VPC Flow Log events into SQLite
- Search events using:
  - Account ID
  - Instance ID
  - Source IP
  - Destination IP
  - Action
  - Log Status
  - Earliest Time
  - Latest Time
- Paginated search results
- Duplicate archive-member detection
- Bulk database import for improved performance
- Docker support

---

## Technology Stack

| Layer | Technology |
|--------|------------|
| Frontend | React 19, Vite 8, Axios |
| Backend | Python 3.12, Django 6, Django REST Framework |
| Database | SQLite (Django ORM) |
| Containers | Docker, Docker Compose |

---

## Architecture

```text
React Frontend
       │
       ▼
Django REST API
       │
       ├── Archive Validation
       ├── Archive Streaming
       ├── Event Parsing
       ├── Duplicate Detection
       └── Bulk Database Import
       │
       ▼
SQLite Database
       │
       ▼
Search API
       │
       ▼
React Frontend
```

---

## Upload Workflow

```text
Upload Archive
      │
      ▼
Validate Archive
      │
      ▼
Stream Archive Members
      │
      ▼
Check Duplicate Filenames
      │
      ▼
Parse Events
      │
      ▼
Bulk Insert into SQLite
      │
      ▼
Return Success
```

The upload process is transactional. If an archive is invalid or contains duplicate archive-member filenames, the entire request is rolled back.

---

## Supported Formats

### Upload

- `.tgz`
- `.tar.gz`

### Event Format

Each event line contains 15 whitespace-separated fields:

```text
serialno version account_id instance_id srcaddr dstaddr srcport dstport
protocol packets bytes starttime endtime action log_status
```

---

## Search

The application supports filtering by:

- Account ID
- Instance ID
- Source IP
- Destination IP
- Action
- Log Status
- Earliest Time
- Latest Time

Results are paginated and include the source archive-member filename.

---

# Project Structure

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
│   │   └── tests.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles/
│   ├── .env.example
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml
└── README.md
```

---

# Backend Setup

## Windows

```powershell
python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r backend\requirements.txt

cd backend

python manage.py migrate

python manage.py runserver
```

## Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate

pip install -r backend/requirements.txt

cd backend

python manage.py migrate

python manage.py runserver
```

Backend runs at

```
http://127.0.0.1:8000/
```

---

# Frontend Setup

Open another terminal.

```bash
cd frontend
```

Create environment file.

```
cp .env.example .env
```

Install dependencies.

```bash
npm install
```

Start the application.

```bash
npm run dev
```

Frontend runs at

```
http://localhost:5173
```

---

# Environment Variable

Frontend:

```env
VITE_API_URL=http://127.0.0.1:8000/api/
```

---

# Docker

Build and start both services.

```bash
docker compose up --build
```

Open:

Frontend

```
http://localhost:5173
```

Backend Health

```
http://localhost:8000/api/health/
```

Stop:

```bash
docker compose down
```

---

# API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/health/` | Health check |
| POST | `/api/upload/` | Upload archive(s) |
| POST | `/api/search/` | Search imported events |
| GET | `/admin/` | Django Admin |

---

## Upload Response

```json
{
  "status": "success",
  "message": "676 file(s) uploaded successfully.",
  "files": [
    "events.log"
  ]
}
```

Duplicate archive-member filenames return

```
HTTP 409 Conflict
```

---

## Search Request

```json
{
    "search": "REJECT",
    "earliest_time": 1725850449,
    "latest_time": 1725855086,
    "page": 1,
    "page_size": 20
}
```

---

# Performance

The application was optimized for importing large AWS VPC Flow Log archives.

Performance improvements include:

- Direct archive streaming
- Single-pass event parsing
- Typed event representation
- Bulk database inserts
- Transaction-based imports
- Efficient filename duplicate detection

On the supplied benchmark archive:

| Metric | Value |
|--------|--------|
| Archive Members | 676 |
| Events | 103,520 |
| Import Time | ~19 seconds |

Actual performance depends on system hardware.

---

# Design Decisions

- SQLite was chosen for simplicity and assignment requirements.
- Archives are streamed directly without extracting files to the application filesystem.
- Uploads are wrapped in a single database transaction.
- Duplicate detection is based on archive-member filenames using efficient in-memory sets.
- Bulk inserts are used to reduce database overhead.
- Search supports pagination for better scalability.

---

# Testing

Backend

```bash
python manage.py check

python manage.py test events

python manage.py makemigrations --check
```

Frontend

```bash
npm run lint

npm run build
```

---

# Troubleshooting

### Migration errors

```bash
python manage.py migrate
```

### Database locked

Stop any other process using `backend/db.sqlite3`.

### Port already in use

Ensure ports **8000** and **5173** are available.

### Frontend cannot reach backend

Verify:

```env
VITE_API_URL=http://127.0.0.1:8000/api/
```

Restart the Vite development server after changing the environment file.

---

## License

This project was developed as part of the **Aceable Cyber Solutions Full Stack Assignment**.
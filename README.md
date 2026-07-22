# Aceable Event Search System

Aceable Event Search System is a full-stack assignment application for uploading, storing, and searching AWS VPC Flow Log event files.

The frontend is built with React and Vite. The backend is a Django REST Framework API that validates uploads, stores parsed events in SQLite, and supports search by event fields and time range.

## Features

- Upload one or more AWS VPC Flow Log files
- Validate every file before it is saved
- Reject invalid files without writing them to disk or the database
- Prevent duplicate uploads by filename
- Store uploaded-file metadata and parsed events in SQLite
- Search by text, earliest time, and latest time
- Display matching events, result count, and search execution time
- Run the application locally or with Docker Compose

## Project Structure

```text
aceable-fullstack-assignment/
|- backend/
|  |- config/
|  |- events/
|  |  |- api/
|  |  |- migrations/
|  |  |- services/
|  |  |- models.py
|  |  |- serializers.py
|  |  `- urls.py
|  |- Dockerfile
|  |- entrypoint.sh
|  |- manage.py
|  `- requirements.txt
|- frontend/
|  |- public/
|  |- src/
|  |  |- api/
|  |  |- components/
|  |  |- pages/
|  |  `- styles/
|  |- Dockerfile
|  |- package.json
|  `- vite.config.js
|- docker-compose.yml
`- README.md
```

## Prerequisites

- Python 3.12 or later
- Node.js 22 or later
- npm
- Docker and Docker Compose (optional)

## Local Setup

### Backend

```bash
cd backend
python -m venv venv
```

Activate the environment:

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# Linux or macOS
source venv/bin/activate
```

Install dependencies, apply migrations, and start Django:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`.

### Frontend

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

On Linux or macOS, use `cp .env.example .env` instead of `copy`.

The frontend is available at `http://localhost:5173`.

`VITE_API_URL` in `frontend/.env` controls the API base URL. The default local value is `http://127.0.0.1:8000/api/`.

## Docker Compose

From the repository root:

```bash
docker compose up --build
```

This starts the backend on port 8000 and the frontend on port 5173. Stop the services with:

```bash
docker compose down
```

## API Endpoints

### Health check

```http
GET /api/health/
```

### Upload event files

```http
POST /api/upload/
Content-Type: multipart/form-data
```

Send one or more files using the repeated `files` form field. A valid file is UTF-8 text with one or more VPC Flow Log event lines. Invalid uploads return HTTP 400 and are not saved. Duplicate filenames return HTTP 409.

Successful uploads return:

```json
{
  "status": "success",
  "message": "1 file(s) uploaded successfully.",
  "files": ["path/to/uploaded/file"]
}
```

### Search events

```http
POST /api/search/
Content-Type: application/json
```

All search filters are optional:

```json
{
  "search": "REJECT",
  "earliest_time": 1725850449,
  "latest_time": 1725855086
}
```

The response contains a result count, elapsed search time, and the matching event records:

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

## Data Storage

Uploaded source files are stored under `uploads/events/`. Parsed events and upload metadata are stored in `backend/db.sqlite3` through Django models. Both locations are ignored by Git so each clone can start with its own local data.

## Verification Commands

```bash
# Backend
cd backend
python manage.py check

# Frontend
cd ../frontend
npm run lint
npm run build
```

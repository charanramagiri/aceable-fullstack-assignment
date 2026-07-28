# Aceable Event Search System

A full-stack assignment for importing and searching AWS VPC Flow Log-style
events. A React/Vite frontend sends compressed archives to a Django REST API.
The backend safely streams archive members, validates and parses their events,
and stores searchable metadata and Event rows in SQLite.

## Features

- Upload one or more `.tgz` or `.tar.gz` archives in one request.
- Process archives through Django's uploaded-file interface without creating an
  application-level copy or extracting members to the filesystem. Django may
  temporarily buffer sufficiently large multipart uploads.
- Reject malformed archives, empty archives, links, devices, FIFOs, and invalid
  event files.
- Reject exact, case-sensitive duplicate archive-member basenames from previous
  imports or the current request.
- Roll back the complete request if any archive member is invalid.
- Parse numeric fields once into a typed `ParsedEvent` representation.
- Insert UploadedFile and Event records with Django ORM bulk operations.
- Search by account, instance, source/destination IP, action, log status, and
  time boundaries.
- Paginate results and display the source archive-member filename.
- Emit one structured performance benchmark log per upload attempt.

## Technology stack

| Area | Technology |
|---|---|
| Frontend | React 19, Vite 8, Axios |
| Backend | Python 3.12, Django 6, Django REST Framework |
| Database | SQLite through the Django ORM |
| Validation/testing | Django test framework, Oxlint, Vite build |
| Containers | Docker and Docker Compose |

## Architecture

```text
Browser
  |
  v
React/Vite frontend (localhost:5173)
  |
  v
Django REST API (localhost:8000/api/)
  |-- archive validation and direct TAR/GZIP streaming
  |-- typed event parsing
  |-- request-wide transaction and bulk inserts
  v
SQLite
  |
  v
Paginated search results
```

The backend is separated into API views, archive/parsing/import services, Django
models, and migrations. Search requests query SQLite; they do not reopen the
original archive.

## Upload workflow

```text
POST .tgz/.tar.gz archive(s)
  -> validate extensions
  -> begin transaction.atomic()
  -> load existing UploadedFile member basenames once
  -> open each upload directly with tarfile
  -> accept directories and regular files only
  -> stream each regular member with extractfile()
  -> normalize its basename and check existing/request-local filename sets
     -> return HTTP 409 if the basename is a duplicate
  -> decode and parse events line by line
  -> create ParsedEvent NamedTuple records
  -> create UploadedFile and Event objects
  -> UploadedFile.bulk_create(batch_size=500)
  -> Event.bulk_create(batch_size=1000)
  -> commit transaction
  -> return HTTP 201
```

Directories are ignored. Symlinks, hard links, devices, FIFOs, malformed
archives, archives without regular files, invalid UTF-8, empty event members,
and malformed event lines cause an HTTP 400 response. The transaction ensures
that no rows from the request remain after an import failure.

Duplicate identity is the normalized basename stored in `UploadedFile.filename`,
not the outer archive filename or full internal member path. Matching is exact
and case-sensitive. HTTP 409 is returned if that basename already exists from a
successful import, occurs more than once within one archive, or occurs across
multiple archives in the same request. The complete request rolls back while
previously committed database rows remain unchanged.

The application does not create its own archive copy. Django's configured
upload handlers may temporarily buffer sufficiently large multipart uploads
before the archive is processed.

The current implementation materializes the parsed records and Django Event
objects before the final bulk insert. This uses more memory than a bounded
buffer, but it performed better for the assignment workload.

## Supported archive and event formats

The upload endpoint accepts filenames ending in:

- `.tgz`
- `.tar.gz`

Each regular archive member must be UTF-8 text. Blank lines are ignored. Every
nonblank line must contain exactly these 15 whitespace-separated fields:

```text
serialno version account_id instance_id srcaddr dstaddr srcport dstport
protocol packets bytes starttime endtime action log_status
```

`serialno`, ports, protocol, packet/byte counts, and timestamps must be valid
integers.

## Storage behavior

- Archives are processed through Django's uploaded-file interface.
- The application does not create its own archive copy or extract archive
  members to the filesystem.
- Django may temporarily buffer sufficiently large multipart uploads according
  to its configured upload handlers.
- Neither the original archive nor its members are permanently retained by the
  application.
- One UploadedFile database row is stored per regular archive member.
- Parsed Event rows are stored in `backend/db.sqlite3` during local development.
- Docker Compose bind-mounts `./backend` into the backend container, so its
  SQLite file persists in the local backend directory.

## Search functionality

`POST /api/search/` supports these optional JSON fields:

| Field | Behavior |
|---|---|
| `search` | Case-insensitive substring search across account ID, instance ID, source IP, destination IP, action, and log status |
| `earliest_time` | Requires `starttime >= earliest_time` |
| `latest_time` | Requires `endtime <= latest_time` |
| `page` | Page number; default `1` |
| `page_size` | Results per page; default `20`, maximum `100` |

Results are ordered by Event ID and include the archive-member filename. All
filters are optional. The six text fields intentionally do not have B-tree
indexes because the current leading-wildcard `icontains` queries do not use
them. Indexes remain on `starttime`, `endtime`, and the UploadedFile foreign
key.

## Prerequisites

For local development:

- Python 3.12 or newer
- Node.js 22 and npm

Alternatively, install Docker with Docker Compose support.

## Backend setup

Run these commands from the repository root.

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r .\backend\requirements.txt
Set-Location .\backend
python manage.py migrate
python manage.py runserver
```

### Unix/macOS

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r backend/requirements.txt
cd backend
python manage.py migrate
python manage.py runserver
```

The backend listens on `http://127.0.0.1:8000/`, with APIs under
`http://127.0.0.1:8000/api/`.

### Database migrations

From `backend/` with the virtual environment active:

```bash
python manage.py showmigrations
python manage.py migrate
python manage.py makemigrations --check
```

The repository includes migrations for the initial schema and removal of six
unused text-search indexes.

## Frontend setup

Open a second terminal at the repository root.

### Windows PowerShell

```powershell
Set-Location .\frontend
Copy-Item .env.example .env
npm install
npm run dev
```

### Unix/macOS

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Vite listens on `http://localhost:5173/`.

## Environment variables

The application reads one project-specific environment variable, in the
frontend:

| Variable | Required for | Description |
|---|---|---|
| `VITE_API_URL` | Local frontend and frontend container | Django API base URL, including the trailing `/api/` path |

Placeholder format:

```dotenv
VITE_API_URL=<backend-api-base-url>
```

For local development, copying `frontend/.env.example` supplies the repository's
configured local value. Docker Compose supplies this variable to the frontend
service. The backend settings currently do not read project-specific
environment variables.

## Docker Compose

The repository defines exactly two services:

- `backend`: built from `backend/Dockerfile`, exposed on host port `8000`.
- `frontend`: built from `frontend/Dockerfile`, exposed on host port `5173`.

From the repository root:

```bash
docker compose up --build
```

The backend entrypoint automatically runs `python manage.py migrate`, then
starts Django on `0.0.0.0:8000`. The frontend runs the Vite development server
with `--host`.

Open:

- Frontend: `http://localhost:5173/`
- Backend API base: `http://localhost:8000/api/` (use a route such as
  `/api/health/`)

Stop the services:

```bash
docker compose down
```

The Compose configuration bind-mounts `./backend` to `/app` and `./frontend`
to the frontend container. It also uses an anonymous `/app/node_modules`
volume.

## Testing and verification

Backend commands, run from `backend/`:

```bash
python manage.py test events
python manage.py check
python manage.py makemigrations --check
```

Frontend commands, run from `frontend/`:

```bash
npm run lint
npm run build
```

There is no separate frontend unit-test script in `frontend/package.json`;
linting and a production build are the available frontend verification tasks.

## Performance

The final verified local benchmark imported:

- 676 archive members
- 103,520 Events
- HTTP status `201`
- Approximately 19 seconds of upload request time

The result was measured locally after direct archive streaming, typed parsing,
and removal of six indexes unused by the current substring searches. Performance
depends on CPU, storage, memory, operating system, SQLite state, and other
machine load; approximately 19 seconds is a reference result, not a guarantee.

The backend logs a structured `Archive import benchmark` INFO line for each
upload attempt. Timings are diagnostic only and are not returned in the API
response.

Duplicate initialization loads existing member filenames with one database
query. Request-local Python set membership then checks each streamed member; it
does not execute one query per archive member. Duplicate-check performance
depends on the number of existing and submitted filenames.

## API endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/health/` | Backend health check |
| POST | `/api/upload/` | Upload one or more archives |
| POST | `/api/search/` | Search and paginate stored Events |
| GET/browser | `/admin/` | Django admin |

### Health

```http
GET /api/health/
```

```json
{
  "status": "success",
  "message": "Aceable Backend is running."
}
```

### Upload

```http
POST /api/upload/
Content-Type: multipart/form-data
```

Supply one or more archives using repeated `files` form fields.

Example response for an archive containing one regular event member:

```json
{
  "status": "success",
  "message": "1 file(s) uploaded successfully.",
  "files": ["events.log"]
}
```

Invalid extensions, archives, or event contents return HTTP 400. A successful
request returns HTTP 201. The response message count is the number of
successfully imported regular archive members, not the number of outer
`.tgz`/`.tar.gz` archives submitted. The `files` array contains those members'
basenames in processing order.

Duplicate archive-member basenames return HTTP 409 Conflict with a `detail`
message. For example, when `events.log` was imported previously:

```json
{
  "detail": "An archive member named 'events.log' has already been imported."
}
```

The failed request creates no UploadedFile or Event rows. Rows committed before
that request remain unchanged.

### Search

```http
POST /api/search/
Content-Type: application/json
```

Example request:

```json
{
  "search": "REJECT",
  "earliest_time": 1725850449,
  "latest_time": 1725855086,
  "page": 1,
  "page_size": 20
}
```

The response includes `count`, pagination metadata, `search_time`, and a
`results` array containing all Event fields plus `file_name`.

## Project structure

```text
aceable-fullstack-assignment/
|-- backend/
|   |-- config/                 # Django settings and root URLs
|   |-- events/
|   |   |-- api/                # Health, upload, and search views
|   |   |-- migrations/         # SQLite schema history
|   |   |-- services/           # Archive, parser, import, and search logic
|   |   |-- models.py
|   |   |-- serializers.py
|   |   `-- tests.py
|   |-- Dockerfile
|   |-- entrypoint.sh
|   |-- manage.py
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- api/
|   |   |-- components/
|   |   |-- pages/
|   |   `-- styles/
|   |-- .env.example
|   |-- Dockerfile
|   |-- package.json
|   `-- vite.config.js
|-- docker-compose.yml
`-- README.md
```

## Design decisions and tradeoffs

- **SQLite retained:** appropriate for the assignment and simple local setup,
  but it has a single-writer architecture.
- **Direct streaming:** the application processes Django's uploaded-file object
  without creating its own archive copy or extracting members. Django may
  temporarily buffer large multipart uploads; neither archives nor members are
  permanently retained by the application.
- **Strict archive members:** only directories and regular files are accepted
  to avoid link and special-file risks.
- **Typed parsing:** `ParsedEvent` replaces per-event dictionaries and converts
  numeric values once.
- **Request-wide transaction:** provides all-or-nothing behavior across every
  archive in one upload.
- **Lightweight filename duplicate detection:** exact, case-sensitive member
  basenames are checked using one existing-filename query and request-local
  sets. Contents are not compared: different contents with the same basename
  are duplicates, while identical contents under different basenames are not.
  This is an intentional assignment-level tradeoff.
- **Bulk sizes:** UploadedFile uses `500`; Event uses `1000`. Larger Event
  batches and repeated bounded-buffer flushes did not improve the measured
  workload.
- **Index selection:** time and foreign-key indexes remain. Six text indexes
  were removed because current `icontains` searches use leading wildcards and
  performed full table scans with or without those indexes.
- **Memory tradeoff:** retaining complete parsed and Event lists was faster in
  the tested workload, but memory use scales with archive size.
- **No parallel writers:** avoids SQLite write contention and added complexity.

## Troubleshooting

### Backend

- **`python` is not recognized:** install Python 3.12+ and ensure it is on
  `PATH`; on Unix/macOS, use `python3` to create the virtual environment.
- **PowerShell blocks activation:** review the local execution policy or run
  the virtual environment's Python executable directly.
- **Missing Django/module errors:** activate the virtual environment and rerun
  `python -m pip install -r backend/requirements.txt` from the repository root.
- **Port 8000 is in use:** stop the conflicting process before starting Django.

### Database and migrations

- **`no such table` errors:** run `python manage.py migrate` from `backend/`.
- **`database is locked`:** stop other Django processes or tools using
  `backend/db.sqlite3`, then retry. Do not run multiple SQLite writers.
- **Unexpected migration state:** inspect with `python manage.py showmigrations`
  and run `python manage.py makemigrations --check`.

### Frontend

- **Requests have an empty or incorrect URL:** ensure `frontend/.env` defines
  `VITE_API_URL` and restart Vite after changing it.
- **CORS errors:** use the configured frontend origin
  `http://localhost:5173`; the backend settings allow that origin.
- **Port 5173 is in use:** stop the conflicting process before starting Vite.
- **Dependency errors:** remove only the frontend's generated dependency state
  if appropriate, then rerun `npm install`; do not edit `package-lock.json`
  manually.

### Uploads

- Confirm the outer filename ends in `.tgz` or `.tar.gz`.
- Confirm the archive contains at least one regular UTF-8 event file.
- Confirm each nonblank event line has exactly 15 fields and valid integers.
- Links and special TAR members intentionally invalidate the entire upload.
- An HTTP 409 means a normalized member basename was already imported or was
  repeated in the current request. Renaming only the outer `.tgz`/`.tar.gz`
  file does not change member-basename identity; this identity rule is
  intentional and does not compare contents.
- Large imports retain all parsed records and Event objects until insertion, so
  available memory can limit maximum practical archive size.

### Docker

- **Build or startup fails:** run `docker compose up --build` from the
  repository root and inspect both service logs.
- **Ports are already allocated:** stop local services using `8000` or `5173`.
- **Backend migration failure:** inspect the backend container logs; its
  entrypoint runs migrations before starting the server.
- **Frontend cannot reach the API:** access the app through
  `http://localhost:5173` and confirm the Compose-provided `VITE_API_URL`.
- **Entrypoint interpreter errors on Windows:** ensure
  `backend/entrypoint.sh` retains Unix LF line endings, then rebuild.

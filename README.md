# 🔎 Aceable Event Search System

A full-stack web application built as part of the **Aceable Cyber Solutions Full Stack Assignment**. The application allows users to upload event log files, search events using filters, and view matching results efficiently through a clean and responsive interface.

---

# 📌 Features

### Backend

* Upload one or more event log files
* Parse uploaded event files into structured data
* Search events using:

  * Search String
  * Earliest Time
  * Latest Time
* Return matching events along with:

  * Source file name
  * Source IP
  * Destination IP
  * Action
  * Log Status
* Measure and return search execution time
* In-memory caching for faster searches
* Modular service-oriented architecture

### Frontend

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

├── backend/
│   ├── config/
│   └── events/
│       ├── api/
│       ├── services/
│       ├── serializers.py
│       └── urls.py
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles/
│
└── README.md
```

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

# 🎯 Design Decisions

* Service-oriented backend architecture
* In-memory event cache for improved search performance
* Modular React component structure
* Separation of API communication from UI components
* Responsive user interface
* Reusable services and components

---

# 👨‍💻 Author

**Charan Ramagiri**

Built as part of the Aceable Cyber Solutions Full Stack Assignment.

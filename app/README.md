# ⚡ FastAPI In-Memory CRUD Application with Interactive UI

A clean, beginner-friendly **FastAPI** web application featuring in-memory CRUD operations, interactive single-page UI, automated unit tests with `pytest`, and ready-to-run virtual environment setup.

---

## 📁 Project Structure

```text
app/
├── main.py              # FastAPI application entrypoint, routes, & in-memory store
├── models.py            # Pydantic data schemas (ItemCreate, ItemUpdate, ItemResponse)
├── requirements.txt     # Python project dependencies
├── static/              # Interactive Single-Page Application (SPA) UI
│   ├── index.html       # Clean HTML5 UI dashboard
│   ├── style.css        # Modern, dark-mode CSS styling
│   └── app.js           # Client-side JavaScript connecting to FastAPI CRUD APIs
├── tests/               # Automated API test suite
│   ├── __init__.py
│   └── test_main.py     # 14 comprehensive test cases covering all CRUD endpoints
├── .venv/               # Virtual environment directory (ignored by git)
├── .gitignore           # Ignores .venv, cache, and compiled files
└── README.md            # Setup and execution guide
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ installed on your system.

### 2. Setup Virtual Environment (`venv`)

From the `app` directory (or workspace root), create and activate a virtual environment:

#### Windows (PowerShell):
```powershell
# Navigate into the app directory
cd app

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux (Bash):
```bash
cd app
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

Install the required packages from `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

Installed packages include:
- `fastapi`: Modern, fast web framework for building APIs with Python.
- `uvicorn[standard]`: Lightning-fast ASGI web server implementation.
- `pydantic`: Data validation and settings management using Python type annotations.
- `pytest`: Simple and scalable automated testing framework.
- `httpx`: Next-generation HTTP client used by FastAPI's `TestClient`.

---

### 4. Run the Application

Start the FastAPI application using `uvicorn`:

```bash
# If you are inside the app/ directory:
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Or from the project root:
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access the following in your web browser:
- **Interactive Web UI:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Alternative Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### 5. Run the Automated Tests

Run the test suite using `pytest`:

```bash
# Inside the app/ directory:
pytest -v

# Or with coverage details:
pytest -v -s
```

All 14 test cases validate:
- ✅ Health check endpoint (`/api/health`)
- ✅ Listing all items (`GET /api/items`)
- ✅ Filtering by status, category, and text search
- ✅ Reading a single item by ID (`GET /api/items/{id}`)
- ✅ 404 response handling for non-existent items
- ✅ Creating items with validation (`POST /api/items`)
- ✅ Pydantic schema validation error handling (422 Unprocessable Entity)
- ✅ Updating items completely (`PUT /api/items/{id}`)
- ✅ Partial item updates (`PATCH /api/items/{id}`)
- ✅ Deleting items (`DELETE /api/items/{id}`)
- ✅ Serving the static UI frontend at root (`/`)

---

## 🛠️ API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the interactive Web UI |
| `GET` | `/api/health` | Container & service health check |
| `GET` | `/api/items` | List items (supports `?category=`, `?status=`, `?search=`) |
| `GET` | `/api/items/{item_id}` | Retrieve item details by ID |
| `POST` | `/api/items` | Create a new item |
| `PUT` | `/api/items/{item_id}` | Full update / replacement of an item |
| `PATCH` | `/api/items/{item_id}` | Partial update (e.g. toggle status) |
| `DELETE` | `/api/items/{item_id}` | Delete item by ID |

---

## 🐳 Docker Containerization (Multi-Stage & Non-Root)

### 1. Build the Docker Image
```bash
# Inside the app/ directory:
docker build -t fastapi-app:latest .
```

### 2. Run the Container
```bash
docker run -d --name fastapi-container -p 8000:8000 fastapi-app:latest
```

### 3. Verify Non-Root User Security
```bash
# Check running container user (returns uid=10001(appuser) gid=10001(appgroup))
docker exec fastapi-container whoami
docker exec fastapi-container id
```

### 4. Stop and Remove
```bash
docker stop fastapi-container && docker rm fastapi-container
```

---

## 💡 Notes for DevOps & Containerization (ECS Fargate)

This application is purposefully designed to be container-ready for **Docker** and **AWS ECS Fargate**:
- Multi-stage build minimizes final image size
- Non-root user (`appuser`, UID 10001) for strict least-privilege security compliance
- Standardized port binding (`8000`)
- Built-in `/api/health` endpoint with Docker `HEALTHCHECK` suitable for ALB target group health checks
- In-memory data store requires no external database drivers or dependencies


import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure app directory is in Python path for test execution from any working directory
APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from main import app, store  # noqa: E402
from models import ItemCreate  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    """Reset the in-memory store before each test for test isolation."""
    store.reset()
    # Populate a deterministic baseline
    store.create(
        ItemCreate(
            title="Initial Task 1",
            description="First test task description",
            category="DevOps",
            status="Pending",
        )
    )
    store.create(
        ItemCreate(
            title="Initial Task 2",
            description="Second test task description",
            category="Study",
            status="Completed",
        )
    )
    yield
    store.reset()


def test_health_check():
    """Verify health check endpoint returns 200 OK and accurate metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_items"] == 2
    assert "timestamp" in data


def test_get_items_list():
    """Verify listing all items."""
    response = client.get("/api/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    assert items[0]["title"] == "Initial Task 2"  # Newest first


def test_get_items_filtering():
    """Verify category, status, and search filters."""
    # Filter by category
    res_cat = client.get("/api/items?category=DevOps")
    assert res_cat.status_code == 200
    assert len(res_cat.json()) == 1
    assert res_cat.json()[0]["category"] == "DevOps"

    # Filter by status
    res_status = client.get("/api/items?status=Completed")
    assert res_status.status_code == 200
    assert len(res_status.json()) == 1
    assert res_status.json()[0]["status"] == "Completed"

    # Search by keyword
    res_search = client.get("/api/items?search=First")
    assert res_search.status_code == 200
    assert len(res_search.json()) == 1
    assert res_search.json()[0]["title"] == "Initial Task 1"


def test_get_single_item_success():
    """Verify retrieving an item by ID."""
    response = client.get("/api/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Initial Task 1"


def test_get_single_item_not_found():
    """Verify 404 response for non-existent item."""
    response = client.get("/api/items/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_item_success():
    """Verify creating a new item via POST /api/items."""
    payload = {
        "title": "Deploy to ECS Fargate",
        "description": "Push Docker image to ECR and trigger deployment",
        "category": "DevOps",
        "status": "In Progress",
    }
    response = client.post("/api/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 3
    assert data["title"] == payload["title"]
    assert data["category"] == payload["category"]
    assert data["status"] == payload["status"]
    assert "created_at" in data
    assert "updated_at" in data

    # Verify item count increased
    list_res = client.get("/api/items")
    assert len(list_res.json()) == 3


def test_create_item_validation_error():
    """Verify validation error when title is empty or missing."""
    # Empty title
    response = client.post("/api/items", json={"title": ""})
    assert response.status_code == 422

    # Missing title
    response_missing = client.post("/api/items", json={"description": "No title here"})
    assert response_missing.status_code == 422


def test_update_item_put_success():
    """Verify full update of an existing item."""
    updated_payload = {
        "title": "Initial Task 1 Updated",
        "description": "Updated full description",
        "category": "Engineering",
        "status": "Completed",
    }
    response = client.put("/api/items/1", json=updated_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == updated_payload["title"]
    assert data["category"] == updated_payload["category"]
    assert data["status"] == updated_payload["status"]


def test_update_item_put_not_found():
    """Verify 404 when updating non-existent item."""
    payload = {
        "title": "Non-existent",
        "description": "Does not exist",
        "category": "General",
        "status": "Pending",
    }
    response = client.put("/api/items/999", json=payload)
    assert response.status_code == 404


def test_patch_item_partial_update():
    """Verify partial update of an item using PATCH."""
    patch_payload = {"status": "In Progress"}
    response = client.patch("/api/items/1", json=patch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["status"] == "In Progress"
    assert data["title"] == "Initial Task 1"  # Unchanged


def test_patch_item_not_found():
    """Verify 404 when patching non-existent item."""
    response = client.patch("/api/items/999", json={"status": "In Progress"})
    assert response.status_code == 404


def test_delete_item_success():
    """Verify deleting an item by ID."""
    response = client.delete("/api/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "deleted" in data["message"]

    # Verify item is gone
    get_res = client.get("/api/items/1")
    assert get_res.status_code == 404
    assert len(client.get("/api/items").json()) == 1


def test_delete_item_not_found():
    """Verify 404 when deleting a non-existent item."""
    response = client.delete("/api/items/999")
    assert response.status_code == 404


def test_serve_ui_index():
    """Verify that root / serves HTML UI file."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "TaskFlow" in response.text

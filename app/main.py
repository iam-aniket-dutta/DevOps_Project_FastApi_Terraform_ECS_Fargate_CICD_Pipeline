from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

try:
    from app.models import ItemCreate, ItemResponse, ItemUpdate
except ImportError:
    from models import ItemCreate, ItemResponse, ItemUpdate

# Base directory for relative file lookups
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Task & Item Manager API",
    description="A lightweight, beginner-friendly FastAPI application with in-memory CRUD operations and an interactive UI.",
    version="1.0.0",
)

# Enable CORS for local testing flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InMemoryStore:
    """In-memory data store for managing items without an external database."""

    def __init__(self):
        self._items: Dict[int, ItemResponse] = {}
        self._counter: int = 0
        self._seed_sample_data()

    def _seed_sample_data(self):
        """Seed initial items for instant testing and UI demonstration."""
        sample_items = [
            {
                "title": "Configure ECS Fargate Task Definition",
                "description": "Define container definitions, memory/CPU allocations, and IAM execution roles.",
                "category": "DevOps",
                "status": "In Progress",
            },
            {
                "title": "Setup CI/CD Pipeline Automation",
                "description": "Create automated workflow to test, build Docker image, and deploy to AWS.",
                "category": "DevOps",
                "status": "Pending",
            },
            {
                "title": "Verify FastAPI CRUD Endpoints",
                "description": "Ensure high test coverage and clean API documentation with Swagger UI.",
                "category": "Study",
                "status": "Completed",
            },
            {
                "title": "Configure ECS Task Definition",
                "description": "Configure ECS Task Definition",
                "category": "DevOps",
                "status": "Pending",
            },
            {
                "title": "Build infrastruture using Terraform.",
                "description": "Build infrastruture using Terraform.",
                "category": "DevOps",
                "status": "In Progress",
            },
            {
                "title": "Build CI/CD pipeline using Github Actions.",
                "description": "Build CI/CD pipeline using Github Actions.",
                "category": "DevOps",
                "status": "Pending",
            },
        ]
        for item in sample_items:
            self.create(
                ItemCreate(
                    title=item["title"],
                    description=item["description"],
                    category=item["category"],
                    status=item["status"],
                )
            )

    def list_all(
        self,
        category: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[ItemResponse]:
        results = list(self._items.values())

        if category and category.strip():
            cat = category.strip().lower()
            results = [item for item in results if item.category.lower() == cat]

        if status_filter and status_filter.strip():
            st = status_filter.strip().lower()
            results = [item for item in results if item.status.lower() == st]

        if search and search.strip():
            term = search.strip().lower()
            results = [
                item
                for item in results
                if term in item.title.lower() or (item.description and term in item.description.lower())
            ]

        # Sort with newest updated items first
        return sorted(results, key=lambda x: x.id, reverse=True)

    def get(self, item_id: int) -> Optional[ItemResponse]:
        return self._items.get(item_id)

    def create(self, item_in: ItemCreate) -> ItemResponse:
        self._counter += 1
        now = datetime.now(timezone.utc)
        item = ItemResponse(
            id=self._counter,
            title=item_in.title,
            description=item_in.description or "",
            category=item_in.category or "General",
            status=item_in.status or "Pending",
            created_at=now,
            updated_at=now,
        )
        self._items[item.id] = item
        return item

    def update(self, item_id: int, item_in: ItemCreate) -> Optional[ItemResponse]:
        if item_id not in self._items:
            return None
        existing = self._items[item_id]
        now = datetime.now(timezone.utc)
        updated_item = ItemResponse(
            id=item_id,
            title=item_in.title,
            description=item_in.description or "",
            category=item_in.category or "General",
            status=item_in.status or "Pending",
            created_at=existing.created_at,
            updated_at=now,
        )
        self._items[item_id] = updated_item
        return updated_item

    def patch(self, item_id: int, patch_data: ItemUpdate) -> Optional[ItemResponse]:
        if item_id not in self._items:
            return None
        existing = self._items[item_id]
        now = datetime.now(timezone.utc)
        updated_item = ItemResponse(
            id=item_id,
            title=patch_data.title if patch_data.title is not None else existing.title,
            description=patch_data.description if patch_data.description is not None else existing.description,
            category=patch_data.category if patch_data.category is not None else existing.category,
            status=patch_data.status if patch_data.status is not None else existing.status,
            created_at=existing.created_at,
            updated_at=now,
        )
        self._items[item_id] = updated_item
        return updated_item

    def delete(self, item_id: int) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def reset(self):
        """Reset the store for testing purposes."""
        self._items.clear()
        self._counter = 0


# Shared singleton in-memory database
store = InMemoryStore()


# API Routes
@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint useful for container checks and load balancers."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_items": len(store._items),
    }


@app.get("/api/items", response_model=List[ItemResponse], tags=["Items"])
def get_items(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status (Pending, In Progress, Completed)"),
    search: Optional[str] = Query(None, description="Search term for title or description"),
):
    """Retrieve all items with optional filtering and search."""
    return store.list_all(category=category, status_filter=status, search=search)


@app.get("/api/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def get_item(item_id: int):
    """Retrieve a single item by its ID."""
    item = store.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found.",
        )
    return item


@app.post("/api/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, tags=["Items"])
def create_item(item: ItemCreate):
    """Create a new item in the in-memory store."""
    return store.create(item)


@app.put("/api/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def update_item(item_id: int, item_in: ItemCreate):
    """Full update / replacement of an existing item."""
    updated = store.update(item_id, item_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found.",
        )
    return updated


@app.patch("/api/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def patch_item(item_id: int, patch_data: ItemUpdate):
    """Partial update of an existing item (e.g. status or title)."""
    updated = store.patch(item_id, patch_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found.",
        )
    return updated


@app.delete("/api/items/{item_id}", status_code=status.HTTP_200_OK, tags=["Items"])
def delete_item(item_id: int):
    """Delete an item by its ID."""
    deleted = store.delete(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found.",
        )
    return {"message": f"Item {item_id} deleted successfully", "id": item_id}


# Mount Static Files and Serve UI
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=FileResponse, include_in_schema=False)
def serve_ui():
    """Serve the frontend web UI."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="UI index.html not found.")
    return FileResponse(index_file)

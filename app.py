"""API with pagination with page and size params."""

from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from fastapi.openapi.models import OpenAPI

# Initialize the FastAPI app
app = FastAPI(
    title="RESTful API with Pagination",
    version="1.0.0",
    description="An example of a RESTful API with pagination and OpenAPI 3.1 documentation",
    openapi_version="3.1.0",
)

# Sample data
ITEMS = [{"id": i, "name": f"Item {i}"} for i in range(1, 101)]

# Pydantic model for item
class Item(BaseModel):
    id: int
    name: str

# Pydantic model for paginated response
class PaginatedResponse(BaseModel):
    items: List[Item]
    total: int
    page: int
    size: int
    total_pages: int


@app.get("/items", response_model=PaginatedResponse, tags=["Items"])
async def get_items(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(10, ge=1, le=50, description="Number of items per page (max 50)"),
):
    """
    Get a paginated list of items.
    """
    total_items = len(ITEMS)
    start = (page - 1) * size
    end = start + size

    if start >= total_items:
        raise HTTPException(status_code=404, detail="Page not found")

    paginated_items = ITEMS[start:end]
    total_pages = (total_items + size - 1) // size

    return PaginatedResponse(
        items=paginated_items,
        total=total_items,
        page=page,
        size=size,
        total_pages=total_pages,
    )

# Example metadata for OpenAPI customization
app.openapi = lambda: {
    **app.openapi(),
    "info": {
        **app.openapi().get("info", {}),
        "description": "A simple API demonstrating pagination and OpenAPI 3.1",
    },
}

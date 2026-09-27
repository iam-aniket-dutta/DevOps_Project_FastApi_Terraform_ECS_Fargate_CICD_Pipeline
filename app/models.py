from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title of the item")
    description: Optional[str] = Field(default="", max_length=500, description="Detailed description")
    category: str = Field(default="General", max_length=50, description="Item category (e.g. Work, Study, Personal)")
    status: str = Field(default="Pending", description="Status: Pending, In Progress, Completed")


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    category: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None)


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

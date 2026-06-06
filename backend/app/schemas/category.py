from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str | None = Field(None, min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = Field(None, max_length=500)
    image_id: str | None = Field(None, description="Optional ID of associated Media Asset")
    parent_id: str | None = Field(None, description="Optional parent category ID")
    sort_order: int = Field(0, description="Display sorting weight")
    is_active: bool = Field(True, description="Activation status")


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    slug: str | None = Field(None, min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = Field(None, max_length=500)
    image_id: str | None = Field(None)
    parent_id: str | None = Field(None)
    sort_order: int | None = Field(None)
    is_active: bool | None = Field(None)


class CategoryStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Target status flag")


class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    image_id: str | None
    parent_id: str | None
    level: int
    sort_order: int
    is_active: bool
    created_at: str
    updated_at: str


class CategoryTreeNodeResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    image_id: str | None
    parent_id: str | None
    level: int
    sort_order: int
    is_active: bool
    children: list["CategoryTreeNodeResponse"] = Field(default_factory=list)


CategoryTreeNodeResponse.model_rebuild()

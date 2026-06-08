from fastapi import APIRouter, Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dependencies import get_db, require_role
from app.core.roles import UserRole
from app.models.category import Category
from app.repositories.audit_repository import AuditRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.media_repository import MediaRepository
from app.schemas.auth import TokenData
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryStatusUpdate,
    CategoryTreeNodeResponse,
    CategoryUpdate,
)
from app.schemas.common import Envelope
from app.services.audit_service import AuditService
from app.services.category_service import CategoryService

router = APIRouter()


def get_category_service(db: AsyncDatabase = Depends(get_db)) -> CategoryService:  # type: ignore[type-arg]
    repo = CategoryRepository(db)
    media_repo = MediaRepository(db)
    audit_repo = AuditRepository(db)
    audit_service = AuditService(audit_repo)
    return CategoryService(repo, media_repo, audit_service)


def map_category_response(cat: Category) -> CategoryResponse:
    return CategoryResponse(
        id=cat.id or "",
        name=cat.name,
        slug=cat.slug,
        description=cat.description,
        image_id=cat.image_id,
        parent_id=cat.parent_id,
        level=cat.level,
        sort_order=cat.sort_order,
        is_active=cat.is_active,
        created_at=cat.created_at.isoformat(),
        updated_at=cat.updated_at.isoformat()
    )


# --- Public Endpoints ---

@router.get("", response_model=Envelope[list[CategoryResponse]])
async def list_categories(
    service: CategoryService = Depends(get_category_service)
) -> Envelope[list[CategoryResponse]]:
    """
    Retrieves all active, non-deleted categories in a flat list.
    """
    categories = await service.category_repository.get_active_categories()
    categories.sort(key=lambda x: (x.level, x.sort_order))
    return Envelope(
        success=True,
        message="Active categories retrieved successfully.",
        data=[map_category_response(cat) for cat in categories]
    )


@router.get("/tree", response_model=Envelope[list[CategoryTreeNodeResponse]])
async def get_categories_tree(
    service: CategoryService = Depends(get_category_service)
) -> Envelope[list[CategoryTreeNodeResponse]]:
    """
    Assembles active categories into a nested hierarchy tree.
    """
    tree = await service.get_active_tree()
    return Envelope(
        success=True,
        message="Categories tree compiled successfully.",
        data=tree
    )


@router.get("/admin/all", response_model=Envelope[list[CategoryResponse]])
async def list_all_categories_admin(
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: CategoryService = Depends(get_category_service)
) -> Envelope[list[CategoryResponse]]:
    """
    Retrieves all categories (active, inactive) for administration. Requires admin role.
    """
    categories = await service.list_all_categories()
    categories.sort(key=lambda x: (x.level, x.sort_order))
    return Envelope(
        success=True,
        message="All categories retrieved successfully for admin.",
        data=[map_category_response(cat) for cat in categories]
    )


@router.get("/{slug}", response_model=Envelope[CategoryResponse])
async def get_category_by_slug(
    slug: str,
    service: CategoryService = Depends(get_category_service)
) -> Envelope[CategoryResponse]:
    """
    Fetches details of a single category by its slug.
    """
    cat = await service.get_by_slug(slug)
    return Envelope(
        success=True,
        message="Category retrieved successfully.",
        data=map_category_response(cat)
    )


# --- Admin Endpoints ---

@router.post("", response_model=Envelope[CategoryResponse])
async def create_category(
    request: Request,
    payload: CategoryCreate,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: CategoryService = Depends(get_category_service)
) -> Envelope[CategoryResponse]:
    """
    Creates a new category. Requires administrative clearance.
    """
    ip = request.client.host if request.client else None
    cat = await service.create_category(
        user_id=current_user.user_id,
        is_admin=True,
        request=payload,
        ip_address=ip
    )
    return Envelope(
        success=True,
        message="Category registered successfully.",
        data=map_category_response(cat)
    )


@router.patch("/{id}", response_model=Envelope[CategoryResponse])
async def update_category(
    request: Request,
    id: str,
    payload: CategoryUpdate,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: CategoryService = Depends(get_category_service)
) -> Envelope[CategoryResponse]:
    """
    Updates category attributes. Requires administrative clearance.
    """
    ip = request.client.host if request.client else None
    cat = await service.update_category(
        user_id=current_user.user_id,
        is_admin=True,
        category_id=id,
        request=payload,
        ip_address=ip
    )
    return Envelope(
        success=True,
        message="Category parameters updated successfully.",
        data=map_category_response(cat)
    )


@router.delete("/{id}", response_model=Envelope[None])
async def delete_category(
    request: Request,
    id: str,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: CategoryService = Depends(get_category_service)
) -> Envelope[None]:
    """
    Soft-deletes a category. Requires administrative clearance.
    """
    ip = request.client.host if request.client else None
    await service.delete_category(
        user_id=current_user.user_id,
        is_admin=True,
        category_id=id,
        ip_address=ip
    )
    return Envelope(
        success=True,
        message="Category soft-deleted successfully."
    )


@router.patch("/{id}/status", response_model=Envelope[CategoryResponse])
async def update_category_status(
    request: Request,
    id: str,
    payload: CategoryStatusUpdate,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    service: CategoryService = Depends(get_category_service)
) -> Envelope[CategoryResponse]:
    """
    Activates or deactivates a category. Requires administrative clearance.
    """
    ip = request.client.host if request.client else None
    cat = await service.update_category_status(
        user_id=current_user.user_id,
        is_admin=True,
        category_id=id,
        is_active=payload.is_active,
        ip_address=ip
    )
    return Envelope(
        success=True,
        message=f"Category status revised to {'active' if payload.is_active else 'inactive'} successfully.",
        data=map_category_response(cat)
    )

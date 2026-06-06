import re
from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import (
    BaseAppException,
    NotFoundException,
    PermissionDeniedException,
)
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.repositories.media_repository import MediaRepository
from app.schemas.category import (
    CategoryCreate,
    CategoryTreeNodeResponse,
    CategoryUpdate,
)
from app.services.audit_service import AuditService
from app.services.base import BaseService


def slugify(text: str) -> str:
    """
    Converts a category name to a URL-safe lowercase slug format.
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text


class CategoryService(BaseService[Category]):
    def __init__(
        self,
        repository: CategoryRepository,
        media_repository: MediaRepository,
        audit_service: AuditService
    ):
        super().__init__(repository)
        self.category_repository = repository
        self.media_repository = media_repository
        self.audit_service = audit_service

    async def get_by_slug(self, slug: str) -> Category:
        """
        Retrieves a single non-deleted category by its slug.
        """
        cat = await self.category_repository.get_by_slug(slug)
        if not cat:
            raise NotFoundException("Category not found.")
        return cat

    async def create_category(
        self,
        user_id: str,
        is_admin: bool,
        request: CategoryCreate,
        ip_address: str | None = None
    ) -> Category:
        """
        Registers a new category in the database after checking constraints.
        """
        # Ensure RBAC validation (Admin only)
        if not is_admin:
            raise PermissionDeniedException("Insufficient clearance level to create categories.")

        # Determine/sanitize slug
        slug = request.slug.strip() if request.slug else slugify(request.name)
        if not slug:
            raise BaseAppException("Generated category slug is invalid.", code="INVALID_SLUG", status_code=400)

        # Check slug uniqueness
        existing = await self.category_repository.get_by_slug(slug)
        if existing:
            raise BaseAppException(
                message=f"Category slug '{slug}' is already in use.",
                code="DUPLICATE_SLUG",
                status_code=400
            )

        # Determine level based on parent category
        level = 0
        if request.parent_id:
            parent = await self.category_repository.get_by_id(request.parent_id)
            if not parent or parent.is_deleted:
                raise NotFoundException("Parent category not found.")
            level = parent.level + 1

        # Validate media asset ownership/admin permission checks
        if request.image_id:
            media = await self.media_repository.get_by_id(request.image_id)
            if not media or media.is_deleted:
                raise NotFoundException("Associated media asset not found.")
            if media.uploaded_by != user_id and not is_admin:
                raise PermissionDeniedException("Associated media asset access forbidden.")

        new_category = Category(
            name=request.name.strip(),
            slug=slug,
            description=request.description.strip() if request.description else None,
            image_id=request.image_id,
            parent_id=request.parent_id,
            level=level,
            sort_order=request.sort_order,
            is_active=request.is_active
        )

        inserted = await self.category_repository.insert(new_category)

        await self.audit_service.log_action(
            action="CREATE_CATEGORY",
            target_collection="categories",
            user_id=user_id,
            target_id=inserted.id,
            ip_address=ip_address
        )

        return inserted

    async def update_category(
        self,
        user_id: str,
        is_admin: bool,
        category_id: str,
        request: CategoryUpdate,
        ip_address: str | None = None
    ) -> Category:
        """
        Modifies category settings and recalculates level structures and child nodes.
        """
        if not is_admin:
            raise PermissionDeniedException("Insufficient clearance level to update categories.")

        category = await self.category_repository.get_by_id(category_id)
        if not category or category.is_deleted:
            raise NotFoundException("Category not found.")

        update_data: dict[str, Any] = {"updated_at": datetime.now(UTC)}

        if request.name is not None:
            update_data["name"] = request.name.strip()

        # Update slug if specified
        if request.slug is not None:
            slug = request.slug.strip()
            if not slug:
                raise BaseAppException("Category slug cannot be empty.", code="INVALID_SLUG", status_code=400)
            existing = await self.category_repository.get_by_slug(slug)
            if existing and existing.id != category_id:
                raise BaseAppException(
                    message=f"Category slug '{slug}' is already in use by another category.",
                    code="DUPLICATE_SLUG",
                    status_code=400
                )
            update_data["slug"] = slug

        if request.description is not None:
            update_data["description"] = request.description.strip() if request.description else None

        # Validate media asset
        if request.image_id is not None:
            if request.image_id:
                media = await self.media_repository.get_by_id(request.image_id)
                if not media or media.is_deleted:
                    raise NotFoundException("Associated media asset not found.")
                if media.uploaded_by != user_id and not is_admin:
                    raise PermissionDeniedException("Associated media asset access forbidden.")
            update_data["image_id"] = request.image_id or None

        if request.sort_order is not None:
            update_data["sort_order"] = request.sort_order

        if request.is_active is not None:
            update_data["is_active"] = request.is_active

        # Process parent changes and calculate level recalculations
        if request.parent_id is not None:
            if request.parent_id:
                await self._check_circular_dependency(category_id, request.parent_id)
                parent = await self.category_repository.get_by_id(request.parent_id)
                if not parent or parent.is_deleted:
                    raise NotFoundException("Parent category not found.")
                new_level = parent.level + 1
            else:
                new_level = 0

            update_data["parent_id"] = request.parent_id or None
            update_data["level"] = new_level

            # If level shifted, propagate to descendants recursively
            if new_level != category.level:
                await self._recalculate_descendants_level(category_id, new_level)

        updated = await self.category_repository.update(category_id, update_data)
        if not updated:
            raise BaseAppException("Failed to update category parameters.")

        await self.audit_service.log_action(
            action="UPDATE_CATEGORY",
            target_collection="categories",
            user_id=user_id,
            target_id=category_id,
            ip_address=ip_address
        )

        return updated

    async def delete_category(
        self,
        user_id: str,
        is_admin: bool,
        category_id: str,
        ip_address: str | None = None
    ) -> bool:
        """
        Soft-deletes a category and cascades soft-delete flags recursively to descendants.
        """
        if not is_admin:
            raise PermissionDeniedException("Insufficient clearance level to delete categories.")

        category = await self.category_repository.get_by_id(category_id)
        if not category or category.is_deleted:
            raise NotFoundException("Category not found.")

        success = await self.category_repository.soft_delete(category_id)
        if not success:
            raise BaseAppException("Failed to delete category.")

        # Update deleted_at in db
        await self.category_repository.update(
            category_id,
            {"deleted_at": datetime.now(UTC), "updated_at": datetime.now(UTC)}
        )

        # Cascade soft-deletes recursively to descendants
        await self._soft_delete_descendants(category_id)

        await self.audit_service.log_action(
            action="DELETE_CATEGORY",
            target_collection="categories",
            user_id=user_id,
            target_id=category_id,
            ip_address=ip_address
        )

        return True

    async def update_category_status(
        self,
        user_id: str,
        is_admin: bool,
        category_id: str,
        is_active: bool,
        ip_address: str | None = None
    ) -> Category:
        """
        Revises the activation status of a category.
        """
        if not is_admin:
            raise PermissionDeniedException("Insufficient clearance level to modify category status.")

        category = await self.category_repository.get_by_id(category_id)
        if not category or category.is_deleted:
            raise NotFoundException("Category not found.")

        updated = await self.category_repository.update(
            category_id,
            {"is_active": is_active, "updated_at": datetime.now(UTC)}
        )
        if not updated:
            raise BaseAppException("Failed to revise category status.")

        action_name = "ACTIVATE_CATEGORY" if is_active else "DEACTIVATE_CATEGORY"
        await self.audit_service.log_action(
            action=action_name,
            target_collection="categories",
            user_id=user_id,
            target_id=category_id,
            ip_address=ip_address
        )

        return updated

    async def get_active_tree(self) -> list[CategoryTreeNodeResponse]:
        """
        Assembles all active categories into a hierarchical tree structured by level and sort order.
        """
        categories = await self.category_repository.get_active_categories()
        # Sort by level first to process parent nodes before child nodes in tree creation loop
        categories.sort(key=lambda x: (x.level, x.sort_order))

        nodes_map: dict[str, CategoryTreeNodeResponse] = {}
        roots: list[CategoryTreeNodeResponse] = []

        for cat in categories:
            node = CategoryTreeNodeResponse(
                id=cat.id or "",
                name=cat.name,
                slug=cat.slug,
                description=cat.description,
                image_id=cat.image_id,
                parent_id=cat.parent_id,
                level=cat.level,
                sort_order=cat.sort_order,
                is_active=cat.is_active,
                children=[]
            )
            nodes_map[node.id] = node

            if not cat.parent_id:
                roots.append(node)
            else:
                parent_node = nodes_map.get(cat.parent_id)
                if parent_node:
                    parent_node.children.append(node)

        # Sort children lists recursively
        def sort_node_children(node_list: list[CategoryTreeNodeResponse]) -> None:
            for n in node_list:
                if n.children:
                    n.children.sort(key=lambda x: x.sort_order)
                    sort_node_children(n.children)

        roots.sort(key=lambda x: x.sort_order)
        sort_node_children(roots)
        return roots

    async def _check_circular_dependency(self, category_id: str, proposed_parent_id: str) -> None:
        """
        Recursively walks up ancestry path to prevent cyclic parenting dependencies.
        """
        if category_id == proposed_parent_id:
            raise BaseAppException(
                message="A category cannot be its own parent.",
                code="CIRCULAR_DEPENDENCY",
                status_code=400
            )

        current_parent_id: str | None = proposed_parent_id
        visited = set()
        while current_parent_id:
            if current_parent_id in visited:
                break
            visited.add(current_parent_id)
            if current_parent_id == category_id:
                raise BaseAppException(
                    message="Circular parent-child relationship detected.",
                    code="CIRCULAR_DEPENDENCY",
                    status_code=400
                )
            parent_cat = await self.category_repository.get_by_id(current_parent_id)
            if not parent_cat:
                break
            current_parent_id = parent_cat.parent_id

    async def _recalculate_descendants_level(self, parent_id: str, parent_level: int) -> None:
        """
        Recursively updates depth levels for child categories.
        """
        children = await self.category_repository.get_children(parent_id)
        for child in children:
            if not child.id:
                continue
            new_level = parent_level + 1
            if child.level != new_level:
                await self.category_repository.update(child.id, {"level": new_level})
                await self._recalculate_descendants_level(child.id, new_level)

    async def _soft_delete_descendants(self, parent_id: str) -> None:
        """
        Recursively applies soft-delete state down the category branch.
        """
        children = await self.category_repository.get_children(parent_id)
        for child in children:
            if not child.id:
                continue
            await self.category_repository.soft_delete(child.id)
            await self.category_repository.update(
                child.id,
                {"deleted_at": datetime.now(UTC), "updated_at": datetime.now(UTC)}
            )
            await self._soft_delete_descendants(child.id)

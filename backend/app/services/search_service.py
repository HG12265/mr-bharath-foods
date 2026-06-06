import asyncio
import re
from typing import Any

from app.core.logging import logger
from app.core.search import get_word_search_regex, sanitize_query
from app.models.category import Category
from app.models.product import Product
from app.models.search_analytic import SearchAnalytic
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.search_repository import SearchRepository
from app.services.base import BaseService


class SearchService(BaseService[SearchAnalytic]):
    def __init__(
        self,
        repository: SearchRepository,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
    ):
        super().__init__(repository)
        self.search_repository = repository
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.background_tasks: set[asyncio.Task[Any]] = set()

    async def log_search_query(
        self,
        query: str,
        results_count: int,
        user_id: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        """
        Logs a search query to the database asynchronously.
        """
        try:
            analytic = SearchAnalytic(
                query=query.lower().strip(),
                user_id=user_id,
                ip_address=ip_address,
                results_count=results_count,
            )
            await self.search_repository.insert(analytic)
        except Exception as exc:
            logger.warning(f"Failed to log search analytic: {exc}")

    async def search_products(
        self,
        query: str,
        category_id: str | None = None,
        skip: int = 0,
        limit: int = 10,
        user_id: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[list[Product], int]:
        """
        Searches active, non-deleted products with support for:
        - Typo tolerance regex matching (name, slug, tags, search_keywords)
        - Priority routing based on categories matching search term
        - Prioritizing featured products first
        - Category ID filtering
        - Pagination
        Logs query to search analytics asynchronously.
        """
        cleaned_query = sanitize_query(query)
        words = cleaned_query.split()

        # Base filter: only active, non-deleted products
        product_filter: dict[str, Any] = {
            "status": "active",
            "is_deleted": {"$ne": True},
        }

        if category_id:
            product_filter["category_id"] = category_id

        if words:
            word_conditions = []
            for word in words:
                word_regex = get_word_search_regex(word)

                # Fetch active, non-deleted categories matching this word
                matching_category_ids = []
                category_cursor = self.category_repository.collection.find({
                    "is_active": True,
                    "is_deleted": {"$ne": True},
                    "$or": [
                        {"name": {"$regex": word_regex, "$options": "i"}},
                        {"slug": {"$regex": word_regex, "$options": "i"}},
                    ],
                })
                async for cat in category_cursor:
                    matching_category_ids.append(str(cat["_id"]))

                # Construct word conditions across multiple fields
                conditions: list[dict[str, Any]] = [
                    {"name": {"$regex": word_regex, "$options": "i"}},
                    {"slug": {"$regex": word_regex, "$options": "i"}},
                    {"tags": {"$regex": word_regex, "$options": "i"}},
                    {"search_keywords": {"$regex": word_regex, "$options": "i"}},
                ]

                if matching_category_ids:
                    conditions.append({"category_id": {"$in": matching_category_ids}})

                word_conditions.append({"$or": conditions})

            product_filter["$and"] = word_conditions

        # Run query and fetch total count
        total_count = await self.product_repository.collection.count_documents(product_filter)

        # Atlas Search migration-ready structure:
        # Currently performing regex. Can be swapped directly with Atlas search pipeline.
        cursor = self.product_repository.collection.find(product_filter).sort([
            ("is_featured", -1),
            ("created_at", -1),
        ]).skip(skip).limit(limit)

        products = []
        async for doc in cursor:
            from app.core.money import convert_bson_to_decimals
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            products.append(self.product_repository.model_class.model_validate(doc))

        # Log asynchronously without blocking execution thread
        task = asyncio.create_task(
            self.log_search_query(
                query=cleaned_query,
                results_count=total_count,
                user_id=user_id,
                ip_address=ip_address,
            )
        )
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)

        return products, total_count

    async def search_categories(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10,
        user_id: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[list[Category], int]:
        """
        Searches active, non-deleted categories.
        Logs query to search analytics asynchronously.
        """
        cleaned_query = sanitize_query(query)
        words = cleaned_query.split()

        category_filter: dict[str, Any] = {
            "is_active": True,
            "is_deleted": {"$ne": True},
        }

        if words:
            word_conditions = []
            for word in words:
                word_regex = get_word_search_regex(word)
                word_conditions.append({
                    "$or": [
                        {"name": {"$regex": word_regex, "$options": "i"}},
                        {"slug": {"$regex": word_regex, "$options": "i"}},
                        {"description": {"$regex": word_regex, "$options": "i"}},
                    ]
                })
            category_filter["$and"] = word_conditions

        total_count = await self.category_repository.collection.count_documents(category_filter)

        cursor = self.category_repository.collection.find(category_filter).skip(skip).limit(limit)
        categories = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            categories.append(self.category_repository.model_class.model_validate(doc))

        # Log search query asynchronously
        task = asyncio.create_task(
            self.log_search_query(
                query=cleaned_query,
                results_count=total_count,
                user_id=user_id,
                ip_address=ip_address,
            )
        )
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)

        return categories, total_count

    async def get_autocomplete_suggestions(self, query: str) -> list[str]:
        """
        Generates prefix-based search suggestions from active products and categories.
        """
        cleaned_query = sanitize_query(query)
        word_regex = rf"\b{re.escape(cleaned_query)}"

        suggestions: set[str] = set()

        # 1. Fetch matching active products
        product_cursor = self.product_repository.collection.find({
            "status": "active",
            "is_deleted": {"$ne": True},
            "$or": [
                {"name": {"$regex": word_regex, "$options": "i"}},
                {"tags": {"$regex": word_regex, "$options": "i"}},
                {"search_keywords": {"$regex": word_regex, "$options": "i"}},
            ],
        }).limit(20)

        async for doc in product_cursor:
            name = doc.get("name", "")
            if re.search(word_regex, name, re.IGNORECASE):
                suggestions.add(name.strip())

            for tag in doc.get("tags", []):
                if re.search(word_regex, tag, re.IGNORECASE):
                    suggestions.add(tag.strip())

            for kw in doc.get("search_keywords", []):
                if re.search(word_regex, kw, re.IGNORECASE):
                    suggestions.add(kw.strip())

        # 2. Fetch matching active categories
        category_cursor = self.category_repository.collection.find({
            "is_active": True,
            "is_deleted": {"$ne": True},
            "$or": [
                {"name": {"$regex": word_regex, "$options": "i"}},
                {"slug": {"$regex": word_regex, "$options": "i"}},
            ],
        }).limit(20)

        async for doc in category_cursor:
            name = doc.get("name", "")
            if re.search(word_regex, name, re.IGNORECASE):
                suggestions.add(name.strip())

        # Return sorted list of suggestions limited to 10
        return sorted(suggestions, key=len)[:10]

    async def get_trending_searches(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Returns trending search queries based on logged analytics.
        """
        return await self.search_repository.get_trending_queries(limit=limit)

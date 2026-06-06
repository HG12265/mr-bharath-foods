import math
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.api.v1.categories import map_category_response
from app.api.v1.products import map_product_response
from app.core.dependencies import get_db
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.search_repository import SearchRepository
from app.schemas.common import Envelope, PaginationMeta
from app.schemas.search import AutocompleteResponse, TrendingResponse, TrendingSearch
from app.services.search_service import SearchService

router = APIRouter()


def get_search_service(db: AsyncDatabase = Depends(get_db)) -> SearchService:  # type: ignore[type-arg]
    repo = SearchRepository(db)
    product_repo = ProductRepository(db)
    category_repo = CategoryRepository(db)
    return SearchService(repo, product_repo, category_repo)


@router.get("", response_model=Envelope[Any])
async def search(
    request: Request,
    q: str = Query(..., description="Search term"),
    type: str = Query("product", description="Search target type: 'product' or 'category'"),
    category_id: str | None = Query(None, description="Filter products by category ID"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Limit for pagination"),
    service: SearchService = Depends(get_search_service),
) -> Envelope[Any]:
    """
    Search endpoint supporting product and category targets, pagination, and category filtering.
    Logs searches to analytics.
    """
    user_id = None
    # Safely extract user context if available in request state
    if hasattr(request.state, "user") and request.state.user:
        user_id = str(request.state.user.id)
    ip_address = request.client.host if request.client else None

    mapped_data: list[Any] = []
    if type == "category":
        category_results, total_docs = await service.search_categories(
            query=q,
            skip=skip,
            limit=limit,
            user_id=user_id,
            ip_address=ip_address,
        )
        mapped_data = [map_category_response(cat) for cat in category_results]
    else:
        product_results, total_docs = await service.search_products(
            query=q,
            category_id=category_id,
            skip=skip,
            limit=limit,
            user_id=user_id,
            ip_address=ip_address,
        )
        mapped_data = [map_product_response(prod) for prod in product_results]

    # Calculate pagination meta
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = math.ceil(total_docs / limit) if limit > 0 else 1
    has_next = (skip + limit) < total_docs
    has_prev = skip > 0

    meta = PaginationMeta(
        page=page,
        limit=limit,
        total_docs=total_docs,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )

    return Envelope(
        success=True,
        message=f"Search for '{q}' of type '{type}' completed successfully.",
        data=mapped_data,
        meta=meta,
    )


@router.get("/autocomplete", response_model=Envelope[AutocompleteResponse])
async def autocomplete(
    q: str = Query(..., description="Suggestion prefix query"),
    service: SearchService = Depends(get_search_service),
) -> Envelope[AutocompleteResponse]:
    """
    Autocomplete prefix search endpoint. Returns unique matched suggestion terms.
    """
    suggestions = await service.get_autocomplete_suggestions(q)
    return Envelope(
        success=True,
        message="Autocomplete suggestions retrieved successfully.",
        data=AutocompleteResponse(suggestions=suggestions),
    )


@router.get("/trending", response_model=Envelope[TrendingResponse])
async def trending(
    limit: int = Query(10, ge=1, le=50, description="Trending searches limit"),
    service: SearchService = Depends(get_search_service),
) -> Envelope[TrendingResponse]:
    """
    Trending searches endpoint. Aggregates and returns top search queries.
    """
    trending_data = await service.get_trending_searches(limit)
    trending_items = [
        TrendingSearch(query=item["query"], count=item["count"]) for item in trending_data
    ]
    return Envelope(
        success=True,
        message="Trending searches retrieved successfully.",
        data=TrendingResponse(trending=trending_items),
    )

from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.core.dashboard_rules import validate_dashboard_access
from app.core.dependencies import get_db, require_role
from app.core.roles import UserRole
from app.repositories.customer_repository import CustomerRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.auth import TokenData
from app.schemas.common import Envelope
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


def get_dashboard_service(
    db: AsyncDatabase = Depends(get_db),  # type: ignore[type-arg]
) -> DashboardService:
    order_repo = OrderRepository(db)
    payment_repo = PaymentRepository(db)
    inventory_repo = InventoryRepository(db)
    review_repo = ReviewRepository(db)
    customer_repo = CustomerRepository(db)
    product_repo = ProductRepository(db)
    return DashboardService(
        order_repo=order_repo,
        payment_repo=payment_repo,
        inventory_repo=inventory_repo,
        review_repo=review_repo,
        customer_repo=customer_repo,
        product_repo=product_repo,
    )


@router.get("", response_model=Envelope[DashboardResponse])
async def get_dashboard_analytics(
    current_user: TokenData = Depends(require_role(UserRole.WAREHOUSE)),
    service: DashboardService = Depends(get_dashboard_service),
) -> Envelope[DashboardResponse]:
    """
    Exposes unified dashboard statistics for operations and analytics.
    Restricted to admin and warehouse roles.
    """
    # Double-check rules validation
    validate_dashboard_access(current_user.role)

    dashboard_data = await service.get_dashboard_data(current_user.role)

    return Envelope(
        success=True,
        message="Admin dashboard statistics compiled successfully.",
        data=dashboard_data,
    )

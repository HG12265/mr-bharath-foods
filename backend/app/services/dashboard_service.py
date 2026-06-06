from decimal import Decimal

from app.core.analytics_helpers import (
    calculate_available_stock,
    get_revenue_aggregation_pipeline,
    is_item_low_stock,
)
from app.core.money import convert_bson_to_decimals
from app.core.roles import UserRole
from app.models.order import Order
from app.models.payment import Payment
from app.models.review import Review
from app.repositories.customer_repository import CustomerRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.dashboard import DashboardPaymentProof, DashboardResponse
from app.schemas.inventory import InventoryResponse, WarehouseStockSchema
from app.schemas.order import OrderResponse
from app.schemas.review import ReviewResponse


class DashboardService:
    def __init__(
        self,
        order_repo: OrderRepository,
        payment_repo: PaymentRepository,
        inventory_repo: InventoryRepository,
        review_repo: ReviewRepository,
        customer_repo: CustomerRepository,
        product_repo: ProductRepository,
    ):
        self.order_repository = order_repo
        self.payment_repository = payment_repo
        self.inventory_repository = inventory_repo
        self.review_repository = review_repo
        self.customer_repository = customer_repo
        self.product_repository = product_repo

    async def get_dashboard_data(self, user_role: UserRole) -> DashboardResponse:
        """
        Retrieves dashboard summary statistics and listings.
        Limits visibility for Warehouse role, hiding financials, customers,
        payment proofs, and reviews.
        """
        # 1. Operational data (Visible to both Admin and Warehouse)

        # Confirmed orders count
        confirmed_orders = await self.order_repository.collection.count_documents(
            {"order_status": "confirmed", "is_deleted": {"$ne": True}}
        )

        # Shipped orders count
        shipped_orders = await self.order_repository.collection.count_documents(
            {"fulfillment_status": "shipped", "is_deleted": {"$ne": True}}
        )

        # Delivered orders count
        delivered_orders = await self.order_repository.collection.count_documents(
            {"fulfillment_status": "delivered", "is_deleted": {"$ne": True}}
        )

        # Low stock alerts and count
        low_stock_docs = await self.inventory_repository.get_low_stock_alerts()
        low_stock_alerts = []
        for inv in low_stock_docs:
            on_hand_total = sum(wh.on_hand for wh in inv.warehouse_stock)
            reserved_total = sum(wh.reserved for wh in inv.warehouse_stock)
            available_total = calculate_available_stock(on_hand_total, reserved_total)
            is_low = is_item_low_stock(available_total, inv.safety_stock_level)

            low_stock_alerts.append(
                InventoryResponse(
                    id=inv.id or "",
                    sku=inv.sku,
                    variant_id=inv.variant_id,
                    product_id=inv.product_id,
                    warehouse_stock=[
                        WarehouseStockSchema(
                            warehouse_id=wh.warehouse_id,
                            on_hand=wh.on_hand,
                            reserved=wh.reserved,
                            location_code=wh.location_code,
                        )
                        for wh in inv.warehouse_stock
                    ],
                    safety_stock_level=inv.safety_stock_level,
                    on_hand_total=on_hand_total,
                    reserved_total=reserved_total,
                    available_total=available_total,
                    is_low_stock=is_low,
                    created_at=inv.created_at,
                    updated_at=inv.updated_at,
                )
            )
        low_stock_count = len(low_stock_alerts)

        # Recent orders list
        if user_role == UserRole.WAREHOUSE:
            # Warehouse sees recent operational (confirmed) orders only
            cursor = self.order_repository.collection.find(
                {"order_status": "confirmed", "is_deleted": {"$ne": True}}
            ).sort("created_at", -1).limit(10)
        else:
            # Admin sees all recent orders
            cursor = self.order_repository.collection.find(
                {"is_deleted": {"$ne": True}}
            ).sort("created_at", -1).limit(10)

        recent_orders = []
        async for doc in cursor:
            doc = convert_bson_to_decimals(doc)
            doc["id"] = str(doc["_id"])
            order_obj = Order.model_validate(doc)
            recent_orders.append(OrderResponse(**order_obj.model_dump()))

        # 2. Conditional data loading depending on user role
        if user_role == UserRole.ADMIN:
            # Total orders count
            total_orders = await self.order_repository.collection.count_documents(
                {"is_deleted": {"$ne": True}}
            )

            # Revenue aggregation
            pipeline = get_revenue_aggregation_pipeline()
            rev_cursor = await self.order_repository.collection.aggregate(pipeline)
            rev_docs = []
            async for doc in rev_cursor:
                rev_docs.append(doc)

            total_revenue = Decimal("0.00")
            if rev_docs:
                doc = convert_bson_to_decimals(rev_docs[0])
                total_revenue = doc.get("total_revenue", Decimal("0.00"))

            # Pending payments count and list
            pending_payments = await self.payment_repository.collection.count_documents(
                {"status": "proof_submitted", "is_deleted": {"$ne": True}}
            )

            proof_cursor = self.payment_repository.collection.find(
                {"status": "proof_submitted", "is_deleted": {"$ne": True}}
            ).sort("created_at", -1).limit(10)

            pending_payment_proofs = []
            async for doc in proof_cursor:
                doc = convert_bson_to_decimals(doc)
                doc["id"] = str(doc["_id"])
                payment_obj = Payment.model_validate(doc)
                pending_payment_proofs.append(
                    DashboardPaymentProof(
                        id=payment_obj.id or "",
                        order_id=payment_obj.order_id,
                        order_number=payment_obj.order_number,
                        amount=payment_obj.amount,
                        status=payment_obj.status,
                        screenshot_media_id=payment_obj.screenshot_media_id,
                        created_at=payment_obj.created_at,
                    )
                )

            # Pending reviews count and list
            pending_review_count = await self.review_repository.collection.count_documents(
                {"moderation_status": "pending", "is_deleted": {"$ne": True}}
            )

            review_cursor = self.review_repository.collection.find(
                {"moderation_status": "pending", "is_deleted": {"$ne": True}}
            ).sort("created_at", -1).limit(10)

            pending_reviews = []
            async for doc in review_cursor:
                doc = convert_bson_to_decimals(doc)
                doc["id"] = str(doc["_id"])
                review_obj = Review.model_validate(doc)
                pending_reviews.append(ReviewResponse(**review_obj.model_dump()))

            # Customer registrations count
            total_customers = await self.customer_repository.collection.count_documents(
                {"is_deleted": {"$ne": True}}
            )

            # Products catalog count
            total_products = await self.product_repository.collection.count_documents(
                {"status": "active", "is_deleted": {"$ne": True}}
            )

            return DashboardResponse(
                total_orders=total_orders,
                total_revenue=total_revenue,
                pending_payments=pending_payments,
                confirmed_orders=confirmed_orders,
                shipped_orders=shipped_orders,
                delivered_orders=delivered_orders,
                low_stock_count=low_stock_count,
                pending_review_count=pending_review_count,
                total_customers=total_customers,
                total_products=total_products,
                recent_orders=recent_orders,
                low_stock_alerts=low_stock_alerts,
                pending_payment_proofs=pending_payment_proofs,
                pending_reviews=pending_reviews,
            )

        # 3. Warehouse limited response
        return DashboardResponse(
            total_orders=None,
            total_revenue=None,
            pending_payments=None,
            confirmed_orders=confirmed_orders,
            shipped_orders=shipped_orders,
            delivered_orders=delivered_orders,
            low_stock_count=low_stock_count,
            pending_review_count=None,
            total_customers=None,
            total_products=None,
            recent_orders=recent_orders,
            low_stock_alerts=low_stock_alerts,
            pending_payment_proofs=None,
            pending_reviews=None,
        )

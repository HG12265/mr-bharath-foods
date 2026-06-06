from typing import Any


def get_revenue_aggregation_pipeline() -> list[dict[str, Any]]:
    """
    Returns the MongoDB aggregation pipeline for calculating total revenue
    from non-deleted orders that are paid and not cancelled.
    """
    return [
        {
            "$match": {
                "payment_status": "paid",
                "order_status": {"$ne": "cancelled"},
                "is_deleted": {"$ne": True},
            }
        },
        {
            "$group": {
                "_id": None,
                "total_revenue": {"$sum": "$pricing.grand_total"},
            }
        },
    ]


def calculate_available_stock(on_hand: int, reserved: int) -> int:
    """
    Computes available stock based on physical stock and reservations.
    """
    return on_hand - reserved


def is_item_low_stock(available_stock: int, safety_stock_level: int) -> bool:
    """
    Checks if the available stock falls below safety stock threshold.
    """
    return available_stock < safety_stock_level

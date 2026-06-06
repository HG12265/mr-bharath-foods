from datetime import datetime

from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase


async def generate_next_order_number(db: AsyncDatabase) -> str:  # type: ignore[type-arg]
    """
    Generates a unique order number in the format: MBF-YYYYMMDD-XXXXXX
    Uses an atomic counter in MongoDB.
    """
    today_str = datetime.now().strftime("%Y%m%d")
    counter_id = f"orders_{today_str}"

    res = await db["counters"].find_one_and_update(
        {"_id": counter_id},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    assert res is not None
    seq = res["seq"]
    # Formats to 6 digits, e.g. 000001
    return f"MBF-{today_str}-{seq:06d}"

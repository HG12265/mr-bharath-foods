import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

from app.core.database import db_manager

async def inspect():
    await db_manager.connect_to_database()
    db = db_manager.db
    orders = await db.orders.find().to_list(10)
    print(f"Total orders found: {len(orders)}")
    for o in orders:
        print("Order:", o.get("order_number"), "status:", o.get("order_status"), "payment_status:", o.get("payment_status"), "email:", (o.get("customer_snapshot") or {}).get("email"))

    payments = await db.payments.find().to_list(10)
    print(f"Total payments found: {len(payments)}")
    for p in payments:
        print("Payment:", p.get("_id"), "order_id:", p.get("order_id"), "status:", p.get("status"))

    shipments = await db.shipments.find().to_list(10)
    print(f"Total shipments found: {len(shipments)}")
    for s in shipments:
        print("Shipment:", s.get("_id"), "order_id:", s.get("order_id"), "status:", s.get("status"))

    audit_logs = await db.audit_logs.find().sort("timestamp", -1).to_list(20)
    print(f"Audit logs found: {len(audit_logs)}")
    for a in audit_logs:
        action = a.get("action")
        if "EMAIL" in str(action) or "ORDER" in str(action) or "PAYMENT" in str(action) or "SHIPMENT" in str(action):
            print("Audit:", action, a.get("details"), a.get("timestamp"))

asyncio.run(inspect())


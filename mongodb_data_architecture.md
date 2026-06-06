# MongoDB Data Architecture

## Project: MR. BHARATH FOODS
**Document Version:** 1.2.0  
**Author:** Principal MongoDB Architect & Enterprise Data Engineer  
**Date:** June 6, 2026  
**Status:** Approved for Database Implementation  

---

### Executive Summary

This document details the MongoDB Data Architecture for the **MR. BHARATH FOODS** enterprise e-commerce platform. 

The tech stack comprises **Next.js** (Frontend), **FastAPI** (Backend), **MongoDB Atlas** (Database), and **Cloudflare R2** (Object Storage). The database architecture is optimized for read-heavy, D2C e-commerce workloads, supporting millions of customers and transactions while preserving strict traceability (batch auditing) and compliance metrics.

---

## 1. Collection Design Overview

To maximize throughput and scalability, the database is structured into 19 primary collections.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MONGODB ATLAS DATABASE                          │
├────────────────────┬────────────────────┬──────────────────────────────┤
│  Commerce Context  │ Fulfillment Context│    Operational & CMS Context │
├────────────────────┼────────────────────┼──────────────────────────────┤
│  - products        │  - batches         │  - blog                      │
│  - categories      │  - manufacturers   │  - faqs                      │
│  - customers       │  - inventories     │  - support_tickets           │
│  - carts           │  - orders          │  - notifications             │
│  - subscriptions   │  - return_requests │  - cms_config                │
│  - reviews         │                    │  - audit_logs                │
│  - loyalty_wallets │                    │  - domain_events             │
│  - loyalty_txns    │                    │  - search_analytics          │
│                    │                    │  - media_assets [NEW]        │
└────────────────────┴────────────────────┴──────────────────────────────┘
```

---

## 2. Embedding vs. Referencing Strategy

To leverage MongoDB's performance, we apply the following guidelines:

* **Embed** (1:1 or 1:Few bounded relationships):
  - Product Variants inside `products` (a single food product has few size options: 250ml, 500ml, 1L).
  - SEO and Stats objects inside `products` (low footprint, high read frequency).
  - Addresses inside `customers` (users rarely maintain more than 10 addresses).
  - Shipping and Billing Address snapshots inside `orders` (preserves historical order accuracy if customer address changes later).
  - Lab Certificates inside `batches` (each manufacturing batch has one specific lab report).
* **Reference** (1:Many unbounded or highly transactional relationships):
  - Batches reference `products` and `manufacturers` (preventing document limit size issues and isolating operational inventory logs).
  - Reviews reference `products` (reviews grow continuously over time).
  - Orders reference `customers` (allows independent scalability of billing records).
  - Loyalty Transactions (`loyalty_txns`) reference `loyalty_wallets` (isolates historical audit ledger rows from core balances to prevent 16MB document size threshold breaches).
  - Media Mappings in various documents reference `media_assets` (provides centralized file assets control).

---

## 3. Data Representation Format

For clarity in documenting collection designs, schemas are represented using JSON-compatible types. 
* **Types used**: `ObjectId`, `String`, `Int`, `Double`, `Boolean`, `Date`, `Array`, `Object`.

---

## 4. Product Collection (`products`)

* **Purpose**: Catalog repository storing products, variants, dynamic attributes, SEO configs, and statistics.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "name": "String",
  "slug": "String",
  "description": "String",
  "category_id": "ObjectId",
  "fssai_license_no": "String",
  "sourcing": {
    "region": "String",
    "story": "String",
    "co_packer_id": "ObjectId"
  },
  "media_mappings": [
    {
      "media_asset_id": "ObjectId",
      "sort_order": "Int",
      "role": "String"
    }
  ],
  "attributes": [
    {
      "key": "String",
      "value": "String"
    }
  ],
  "variants": [
    {
      "variant_id": "ObjectId",
      "sku": "String",
      "volume_weight": "String",
      "price": "Double",
      "compare_at_price": "Double",
      "upc": "String",
      "status": "String"
    }
  ],
  "ratings": {
    "average": "Double",
    "count": "Int"
  },
  "seo": {
    "meta_title": "String",
    "meta_description": "String",
    "canonical_url": "String",
    "og_image": "String"
  },
  "stats": {
    "views": "Int",
    "orders": "Int",
    "wishlist_count": "Int",
    "review_count": "Int"
  },
  "status": "String",
  "is_deleted": "Boolean",
  "deleted_at": "Date",
  "created_at": "Date",
  "updated_at": "Date"
}
```

---

## 5. Category Collection (`categories`)

* **Purpose**: Hierarchical classification tree for navigation.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "name": "String",
  "slug": "String",
  "description": "String",
  "parent_id": "ObjectId",
  "gst_rule": {
    "cgst": "Double",
    "sgst": "Double",
    "igst": "Double",
    "hsn_code": "String"
  },
  "status": "String",
  "sort_order": "Int",
  "is_deleted": "Boolean",
  "deleted_at": "Date"
}
```

---

## 6. Variant Collection

* **Decision**: **Embedded** inside the Product collection as an array of documents to minimize query lookup times on Product Detail Pages. Reference structures are bypassed.

---

## 7. Inventory Collection (`inventories`)

* **Purpose**: Real-time stock management decoupled from product metadata.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "variant_id": "ObjectId",
  "sku": "String",
  "warehouse_stock": [
    {
      "warehouse_id": "ObjectId",
      "on_hand": "Int",
      "reserved": "Int",
      "location_code": "String"
    }
  ],
  "safety_stock_level": "Int",
  "updated_at": "Date"
}
```

---

## 8. Batch Collection (`batches`)

* **Purpose**: Food trace lot tracking, linking inventory to partner manufacturers.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "batch_code": "String",
  "product_id": "ObjectId",
  "manufacturer_id": "ObjectId",
  "manufacture_date": "Date",
  "expiry_date": "Date",
  "production_volume": "Int",
  "quarantine_status": "String",
  "lab_certificate": {
    "certificate_no": "String",
    "certifying_body": "String",
    "pdf_url": "String",
    "verification_date": "Date",
    "purity_parameters": {
      "a2_protein": "Boolean",
      "moisture_percentage": "Double",
      "adulteration_test": "String"
    }
  },
  "is_deleted": "Boolean",
  "deleted_at": "Date",
  "created_at": "Date"
}
```

---

## 9. Manufacturer Collection (`manufacturers`)

* **Purpose**: Partner manufacturer and co-packing profiles.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "company_name": "String",
  "fssai_license_no": "String",
  "compliance_status": "String",
  "contact": {
    "email": "String",
    "phone": "String",
    "address": "Object"
  },
  "audit_log": [
    {
      "audit_date": "Date",
      "rating": "String",
      "comments": "String"
    }
  ],
  "is_deleted": "Boolean",
  "deleted_at": "Date"
}
```

---

## 10. Lab Certificate Collection

* **Decision**: **Embedded** inside the Batch collection for rapid loading on Product Detail Pages and simple document-level validation.

---

## 11. Customer Collection (`customers`)

* **Purpose**: Customer identity, profile preferences, addresses, and B2B configurations.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "auth": {
    "email": "String",
    "phone": "String",
    "status": "String"
  },
  "personal_details": {
    "first_name": "String",
    "last_name": "String"
  },
  "addresses": [
    {
      "address_id": "ObjectId",
      "name": "String",
      "phone": "String",
      "street": "String",
      "landmark": "String",
      "pincode": "String",
      "city": "String",
      "state": "String",
      "is_default_shipping": "Boolean",
      "is_default_billing": "Boolean"
    }
  ],
  "b2b_profile": {
    "gstin": "String",
    "credit_limit": "Double",
    "credit_balance": "Double",
    "discount_tier": "String"
  },
  "is_deleted": "Boolean",
  "deleted_at": "Date",
  "created_at": "Date"
}
```

---

## 12. Address Collection

* **Decision**: **Embedded** inside the Customer collection as an array of documents to optimize checkout flows.

---

## 13. Cart Collection (`carts`)

* **Purpose**: Persistent shopping cart sessions for both guest and registered users.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "customer_id": "ObjectId",
  "guest_token": "String",
  "items": [
    {
      "variant_id": "ObjectId",
      "sku": "String",
      "quantity": "Int",
      "added_at": "Date"
    }
  ],
  "expires_at": "Date",
  "status": "String"
}
```

---

## 14. Wishlist Collection (`wishlists`)

* **Purpose**: Stores customer bookmark profiles.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "customer_id": "ObjectId",
  "items": [
    {
      "variant_id": "ObjectId",
      "added_at": "Date"
    }
  ]
}
```

---

## 15. Order Collection (`orders`)

* **Purpose**: Transactional logs. Address details are embedded as snapshots to preserve historical tax/delivery records even if the customer profile changes addresses.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "order_number": "String",
  "customer_id": "ObjectId",
  "order_date": "Date",
  "items": [
    {
      "variant_id": "ObjectId",
      "product_name": "String",
      "sku": "String",
      "quantity": "Int",
      "price": "Double",
      "batch_id": "ObjectId",
      "tax_snapshot": {
        "cgst_rate": "Double",
        "sgst_rate": "Double",
        "igst_rate": "Double",
        "cgst_amount": "Double",
        "sgst_amount": "Double",
        "igst_amount": "Double",
        "hsn_code": "String"
      }
    }
  ],
  "financials": {
    "subtotal": "Double",
    "discount": "Double",
    "tax_total": "Double",
    "shipping_fee": "Double",
    "grand_total": "Double"
  },
  "payment": {
    "gateway_ref": "String",
    "mode": "String",
    "status": "String",
    "timestamp": "Date"
  },
  "shipment": {
    "carrier": "String",
    "tracking_number": "String",
    "status": "String",
    "estimated_delivery": "Date"
  },
  "shipping_address_snapshot": {
    "name": "String",
    "phone": "String",
    "street": "String",
    "landmark": "String",
    "pincode": "String",
    "city": "String",
    "state": "String"
  },
  "billing_address_snapshot": {
    "name": "String",
    "phone": "String",
    "street": "String",
    "landmark": "String",
    "pincode": "String",
    "city": "String",
    "state": "String"
  },
  "status": "String",
  "is_deleted": "Boolean",
  "deleted_at": "Date"
}
```

---

## 16. Payment & Shipment Snapshot Collections

* **Decision**: **Embedded** inside the Order collection to prevent split-brain states and isolate checkout logs in a single operational request.

---

## 18. Subscription Collection (`subscriptions`)

* **Purpose**: Recurring staple deliveries configuration.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "customer_id": "ObjectId",
  "shipping_address_id": "ObjectId",
  "items": [
    {
      "variant_id": "ObjectId",
      "quantity": "Int"
    }
  ],
  "billing_frequency": "String",
  "next_billing_date": "Date",
  "status": "String",
  "is_deleted": "Boolean",
  "deleted_at": "Date",
  "created_at": "Date"
}
```

---

## 19. Loyalty Wallet Collection (`loyalty_wallets`)

* **Purpose**: Stores customer loyalty points balances. Decoupled from transactions to prevent document overflow.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "customer_id": "ObjectId",
  "balance": "Int",
  "tier": "String",
  "updated_at": "Date"
}
```

---

## 19a. Loyalty Transactions Collection (`loyalty_txns`)

* **Purpose**: Separated transactional ledger for point edits, avoiding 16MB document size limits over multi-year lifecycles.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "wallet_id": "ObjectId",
  "customer_id": "ObjectId",
  "points": "Int",
  "type": "String",
  "order_id": "ObjectId",
  "reason": "String",
  "created_at": "Date"
}
```

---

## 20. Review Collection (`reviews`)

* **Purpose**: Stores reviews linked to products.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "product_id": "ObjectId",
  "customer_id": "ObjectId",
  "customer_name": "String",
  "rating": "Int",
  "title": "String",
  "body": "String",
  "media_mappings": [
    {
      "media_asset_id": "ObjectId",
      "sort_order": "Int"
    }
  ],
  "is_verified": "Boolean",
  "status": "String",
  "is_deleted": "Boolean",
  "deleted_at": "Date",
  "created_at": "Date"
}
```

---

## 21. Blog Collection (`blog`)

* **Purpose**: Article content and in-blog buy cards.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "title": "String",
  "slug": "String",
  "author": {
    "name": "String",
    "role": "String"
  },
  "category": "String",
  "content": "String",
  "featured_products": ["ObjectId"],
  "media_mappings": [
    {
      "media_asset_id": "ObjectId",
      "sort_order": "Int"
    }
  ],
  "seo": {
    "meta_title": "String",
    "meta_description": "String"
  },
  "status": "String",
  "is_deleted": "Boolean",
  "deleted_at": "Date",
  "published_at": "Date"
}
```

---

## 22. FAQ Collection (`faqs`)

* **Purpose**: FAQ questions and search tags.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "question": "String",
  "answer": "String",
  "category": "String",
  "tags": ["String"],
  "is_visible": "Boolean",
  "is_deleted": "Boolean",
  "deleted_at": "Date"
}
```

---

## 23. Support Ticket Collection (`support_tickets`)

* **Purpose**: Help desk and ticket routing logs.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "customer_id": "ObjectId",
  "order_id": "ObjectId",
  "status": "String",
  "priority": "String",
  "messages": [
    {
      "sender": "String",
      "body": "String",
      "timestamp": "Date"
    }
  ],
  "is_deleted": "Boolean",
  "deleted_at": "Date",
  "created_at": "Date"
}
```

---

## 24. Notification Collection (`notifications`)

* **Purpose**: Transactional logs tracking communication dispatches.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "customer_id": "ObjectId",
  "channel": "String",
  "template_id": "String",
  "content": "String",
  "status": "String",
  "sent_at": "Date"
}
```

---

## 26. Corporate Gifting Collection (`corporate_gifts`)

* **Purpose**: Custom corporate gift box request records.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "company_name": "String",
  "contact_person": {
    "name": "String",
    "email": "String",
    "phone": "String"
  },
  "quantity": "Int",
  "logo_url": "String",
  "status": "String",
  "is_deleted": "Boolean",
  "deleted_at": "Date",
  "created_at": "Date"
}
```

---

## 27. Audit Log Collection (`audit_logs`)

* **Purpose**: Records administrative and system updates.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "admin_id": "ObjectId",
  "action": "String",
  "target_collection": "String",
  "target_id": "ObjectId",
  "ip_address": "String",
  "timestamp": "Date"
}
```

---

## 28. CMS Collection (`cms_config`)

* **Purpose**: Core dynamic website layout configuration.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "config_key": "String",
  "config_data": "Object",
  "updated_at": "Date"
}
```

---

## 29. Event Collection (`domain_events`)

* **Purpose**: Event-store logging for downstream microservices.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "event_type": "String",
  "payload": "Object",
  "occurred_at": "Date"
}
```

---

## 30. Search Analytics Collection (`search_analytics`)

* **Purpose**: Search diagnostics database.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "query": "String",
  "hits": "Int",
  "no_results": "Boolean",
  "last_searched": "Date"
}
```

---

## 30a. Media Assets Collection (`media_assets`) [NEW]

* **Purpose**: Centralized file control register mapping R2 storage links, sizes, and file types to enable easy media management across the CMS.
* **Document Schema**:
```json
{
  "_id": "ObjectId",
  "filename": "String",
  "mime_type": "String",
  "file_size": "Int",
  "r2_url": "String",
  "s3_etag": "String",
  "usage_scope": "String",
  "is_deleted": "Boolean",
  "deleted_at": "Date",
  "created_at": "Date"
}
```

---

## 31. Indexing Strategy

Indexing is vital for keeping search queries fast on read-heavy D2C platforms.

```
                  [ Product Catalog Read ]  ──► Index: { is_deleted: 1, status: 1, category_id: 1 }
                  [ Product Page Search  ]  ──► Index: { is_deleted: 1, slug: 1 }
                  [ Order History List   ]  ──► Index: { customer_id: 1, order_date: -1 }
```

* **Default Rule**: Every collection must feature indexes on lookup properties. Soft delete properties (`is_deleted`) must be prefixed on index lookups.

---

## 32. Compound Indexes

Optimizes sorted queries and range scans.

* **Product Listings**: `db.products.createIndex({ is_deleted: 1, status: 1, category_id: 1 })`
  - *Purpose*: Optimizes PLP reads filtering by category, ignoring soft-deleted items.
* **Customer Orders**: `db.orders.createIndex({ customer_id: 1, order_date: -1 })`
  - *Purpose*: Speeds up dashboard rendering of a user's recent orders.
* **Loyalty Ledger Audit**: `db.loyalty_txns.createIndex({ customer_id: 1, created_at: -1 })`
  - *Purpose*: Optimizes fast transaction histories retrieval inside loyalty dashboards.

---

## 33. Text Indexes

Optimizes product search bars and help centers.

* **Product Catalog**: `db.products.createIndex({ name: "text", description: "text" }, { weights: { name: 10, description: 2 } })`
  - *Purpose*: Powers the search suggestions and fuzzy matches, prioritizing title keywords over descriptions.
* **FAQs**: `db.faqs.createIndex({ question: "text", answer: "text" })`
  - *Purpose*: Powers support center article lookups.

---

## 34. TTL (Time-To-Live) Indexes

Used for dynamic resource management.

* **Guest Carts**: `db.carts.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 })`
  - *Purpose*: Automatically purges inactive guest carts after expiration (e.g., 14 days) to keep database size optimized.
* **Domain Events**: `db.domain_events.createIndex({ occurred_at: 1 }, { expireAfterSeconds: 2592000 })`
  - *Purpose*: Retains transactional integration events for 30 days before automatic cleanup.

---

## 35. Aggregation Strategy

Aggregation pipelines run on secondary read replicas to prevent impact on primary transaction nodes.

* **Category Sales Reports**:
  - Matches orders in a time window.
  - Unwinds items.
  - Groups by category, summing sales and quantities.
* **Product Stats Update Sync**:
  - Direct cron execution increments views, orders, and review stats inside the embedded `stats` object.

---

## 36. Data Archival Strategy

To maintain high speed as transactions scale into millions of orders:

* **Warm Data**: Orders aged 0–12 months remain in the primary collection.
* **Cold Data Archive**:
  - Orders older than 1 year are moved to a cold archive collection using a scheduled cron execution.
  - For long-term analytical queries, historical orders are exported as compressed JSON files to **Cloudflare R2** object storage, using **MongoDB Atlas Data Lake** to query them in-place if needed.

---

## 37. Backup Strategy

* **Continuous Cloud Backup**: Set up automated point-in-time recovery (PITR) with hourly snapshots retained for 7 days.
* **Snapshot Retentions**: Daily snapshots kept for 30 days; weekly snapshots for 12 weeks; monthly snapshots archived for 1 year in separate secure cloud storage buckets.
* **Compliance Checks**: Monthly tests running automated schema restoration trials to verify backup reliability.

---

## 38. Atlas Cluster Strategy

* **Startup Phase Recommendation**: Launch on a **MongoDB Atlas M10 Dedicated Cluster** (2GB RAM, 10GB Storage, shared IOPS network).
  - *Rationale*: Cost-efficient for launching 2 ghee products with a few hundred users, keeping startup overhead low.
* **Scaling Strategy**: Set up automatic scaling thresholds based on RAM utilization (>75% sustained for 1 hour) to trigger a zero-downtime rolling upgrade to **M30/M40 instances** as product SKUs and user volumes scale.
* **High Availability**: Multi-zone replica set deployment (3-node minimum) to ensure zero-downtime failover configurations:
  - 1 Primary node (writes and immediate reads).
  - 2 Secondary nodes (spread across multiple zones for query scaling and analytical reports).

---

## 39. Sharding Strategy

When database volume exceeds 2TB or concurrent connections spike during festivals, sharding is enabled.

* **Order Collection Sharding**:
  - *Shard Key*: `{ customer_id: "hashed" }`
  - *Rationale*: Distributes transactions evenly across cluster fragments, preventing localized read/write hotspots during peak purchasing events.
* **Product Catalog**: Remains unsharded on all replica instances because it is small (under 1GB) and read-heavy.

---

## 40. Future Scalability Considerations

1. **Schema-less Variant Configuration**: Dynamic properties inside the product variant array let the store support new categories (like Oils or Spices) without altering collections or running database migration scripts.
2. **Read Performance optimization**: Decoupling stock quantities into `inventories` isolates the highly transactional stock-checking queries from the static metadata reads of the `products` catalog.
3. **Soft-Deleted Exclusions**: Enforcing indexed `{ is_deleted: false }` defaults on catalog reads prevents queries from running slow scans against deprecated, archived, or legacy product data.

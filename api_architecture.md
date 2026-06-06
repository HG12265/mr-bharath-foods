# API Architecture Document

## Project: MR. BHARATH FOODS
**Document Version:** 1.1.0  
**Author:** Principal API Architect & Enterprise Backend Architect  
**Date:** June 6, 2026  
**Status:** Approved for Backend Routing Implementation  

---

### Executive Summary

This document defines the Enterprise API Architecture for **MR. BHARATH FOODS**. 

Using **FastAPI** as the backend framework, this RESTful API is designed to handle communication between the **Next.js** frontend, administrative consoles, and third-party logistics (3PL) integrations. It provides strict security controls, rate limiting, dynamic JSON error structures, and event hook architectures, ensuring readiness to transition into microservices as the platform scales.

---

## 1. API Design Principles

* **Statelessness**: Every request must contain all context and tokens required to authorize and process the payload. No server-side session states are maintained.
* **Idempotency**: All `PUT` and `DELETE` requests, alongside critical transactional `POST` requests (like payment confirmations), must support idempotency keys (`Idempotency-Key` header) to prevent duplicate processing.
* **Predictability**: REST resource naming conventions remain strictly pluralized and hierarchical (e.g., `/api/v1/products/{id}/reviews`).

---

## 2. REST Standards

* **HTTP Methods**:
  - `GET`: Retrieve resource data. Safe and idempotent.
  - `POST`: Create a new resource. Non-idempotent by default.
  - `PUT`: Replace an existing resource, or create if not present. Idempotent.
  - `PATCH`: Partially update a resource. Non-idempotent.
  - `DELETE`: Remove a resource (soft delete). Idempotent.
* **Standard Status Codes**:
  - `200 OK`: Successful retrieval or update.
  - `201 Created`: Successful creation.
  - `400 Bad Request`: Validation failure.
  - `401 Unauthorized`: Missing or invalid authentication token.
  - `403 Forbidden`: Authenticated, but lacking permission roles.
  - `404 Not Found`: Resource does not exist.
  - `429 Too Many Requests`: Rate limit exceeded.
  - `500 Internal Server Error`: Server errors.

---

## 3. Authentication Architecture

* **Mechanism**: JWT (JSON Web Tokens) using asymmetric RS256 signatures.
* **Token Structure**:
  - **Access Token**: Short-lived (15 minutes), passed in the `Authorization: Bearer <JWT>` header. Contains user ID, roles, and permissions.
  - **Refresh Token**: Long-lived (30 days), stored in a secure, `HttpOnly`, `SameSite=Strict` cookie.
* **OTP Flow (Mobile/Email)**:
  1. `POST /api/v1/auth/otp/request`: Triggers OTP dispatch via WhatsApp/SMS/Email. Returns an `otp_session_id`.
  2. `POST /api/v1/auth/otp/verify`: Validates OTP against the session ID and returns the JWT access token and refresh cookie.

---

## 4. Role-Based Access Control (RBAC) Architecture

Users are assigned specific roles mapped to granular permissions:

| Role | Target Endpoints | Primary Operations |
| :--- | :--- | :--- |
| **Customer** | `/api/v1/me/*`, `/api/v1/orders` | Create orders, manage own address/subscriptions. |
| **Support Agent** | `/api/v1/support/*`, `/api/v1/orders` (Write) | Process refunds, edit delivery addresses, modify tickets. |
| **Logistics Lead** | `/api/v1/inventories/*`, `/api/v1/shipments/*` | Manage inventory counts, assign shipment tracking. |
| **QA Auditor** | `/api/v1/batches/*`, `/api/v1/manufacturers/*` | Upload lab reports, log facility audits. |
| **Admin** | `/*` (Full access) | Manage catalog prices, modify CMS configurations, adjust roles. |

---

## 5. Public APIs

Open endpoints accessed without authorization headers:
* `GET /api/v1/cms/homepage`: Retrieves current hero configurations, carousel assets, and banner copy.
* `GET /api/v1/faqs`: Retrieves searchable lists of user FAQs.
* `POST /api/v1/contact`: Submits direct support/wholesale messages to support queues.
* `POST /api/v1/trust/verify-batch` [NEW]: Validates a product batch code directly for the public trust portal, returning purity tests, compliance files, and verification timelines.

---

## 6. Product APIs

* `GET /api/v1/products`: Paginated catalog retrieval with filtering parameters.
* `GET /api/v1/products/compare` [NEW]: Compares two or more products side-by-side. Expects query parameter array (e.g., `?ids=ID1,ID2` or `?skus=SKU1,SKU2`).
* `GET /api/v1/products/{slug}`: Retrieves detailed product details, including embedded variants, SEO tags, and aggregated stats.
* `POST /api/v1/products` (Admin Only): Creates a new product document.
* `PATCH /api/v1/products/{id}` (Admin Only): Partially updates metadata or pricing.
* `DELETE /api/v1/products/{id}` (Admin Only): Executes a soft delete by toggling `is_deleted: true`.

---

## 7. Category APIs

* `GET /api/v1/categories`: Retrieves the active category taxonomy tree.
* `POST /api/v1/categories` (Admin Only): Adds a new category node with default GST configurations.
* `PATCH /api/v1/categories/{id}` (Admin Only): Edits layout configurations or tax rules.

---

## 8. Search APIs

* `GET /api/v1/search`: Text-search query endpoint utilizing MongoDB Atlas text search.
  - *Query Params*: `q` (search term), `category` (optional filter).
* `GET /api/v1/search/suggestions`: Fetches autocomplete suggestion keywords matching active characters.

---

## 9. Cart APIs

Supports session synchronization. Carts merge automatically when a guest logs in.

* `GET /api/v1/carts/me`: Retrieves current user's active cart. Fallback logic uses guest token headers if anonymous.
* `POST /api/v1/carts/me/items`: Adds a variant SKU to the cart list.
* `PATCH /api/v1/carts/me/items/{sku}`: Adjusts item quantity.
* `DELETE /api/v1/carts/me/items/{sku}`: Removes an item from the cart.

---

## 10. Checkout APIs

* `POST /api/v1/checkouts/initiate`: Sets up checkout state, validates pincode serviceability, and locks variant inventories.
* `POST /api/v1/checkouts/apply-coupon`: Validates promo codes against cart criteria, returning discounted subtotal.
* `POST /api/v1/checkouts/complete`: Submits delivery selections, creates an order document in a `Pending Payment` state, and returns payment gateway parameters.

---

## 11. Order APIs

* `GET /api/v1/orders/me`: Paginated order history list for the active customer.
* `GET /api/v1/orders/{id}`: Detailed invoice-level order log.
* `POST /api/v1/orders/cod/verify`: Verifies COD order integrity using a verification code input payload.

---

## 12. Payment APIs

* `POST /api/v1/payments/verify`: Validates signature hash returns from payment gateways (e.g., Razorpay) to update order status to `Paid`.
* `POST /api/v1/payments/refund` (Support/Admin Only): Triggers manual transaction reversals.

---

## 13. Shipment APIs

* `GET /api/v1/shipments/track/{tracking_number}`: Retrieves tracking status updates returned from courier APIs.
* `POST /api/v1/shipments/manifest` (Logistics Only): Generates pick/pack sheets and requests carrier pickups.

---

## 14. Wishlist APIs

* `GET /api/v1/wishlists/me`: Retrieves user bookmarked variants.
* `POST /api/v1/wishlists/me/items`: Bookmarks a variant SKU.
* `DELETE /api/v1/wishlists/me/items/{variant_id}`: Removes bookmark.

---

## 15. Review APIs

* `GET /api/v1/products/{id}/reviews`: Paginated reviews list.
* `POST /api/v1/products/{id}/reviews`: Submits a review. Requires a verified buyer authentication token.
* `PATCH /api/v1/reviews/{id}/approve` (Admin Only): Modifies review status to `Approved` or `Flagged`.

---

## 16. Subscription APIs

* `GET /api/v1/subscriptions/me`: Lists customer's recurring delivery orders.
* `POST /api/v1/subscriptions/me`: Creates a recurring product delivery contract.
* `PATCH /api/v1/subscriptions/me/{id}`: Adjusts parameters (skip a cycle, update delivery date, modify quantity).
* `DELETE /api/v1/subscriptions/me/{id}`: Cancels recurring schedule.

---

## 17. Loyalty APIs

* `GET /api/v1/loyalty/me`: Retrieves current point balance and active tier.
* `GET /api/v1/loyalty/me/transactions`: Paginated historical point transaction logs.

---

## 18. Blog APIs

* `GET /api/v1/blog`: Paginated articles list.
* `GET /api/v1/blog/{slug}`: Detailed article content, including embedded recipe schema elements and featured shop cards.

---

## 19. FAQ APIs

* `GET /api/v1/faqs/search`: Text-search querying of support knowledge bases.

---

## 20. Contact APIs

* `POST /api/v1/contacts/inquiry`: Submits general query ticket requests.
* `POST /api/v1/contacts/gifting`: Handles custom bulk corporate gifting forms.

---

## 21. Support APIs

* `GET /api/v1/support/tickets` (Support Only): Paginated view of unresolved customer help requests.
* `POST /api/v1/support/tickets/{id}/messages` (Support/Customer): Appends chat comments to support logs.

---

## 22. B2B APIs

* `GET /api/v1/b2b/catalog`: Returns custom B2B tiered wholesale pricing structures.
* `POST /api/v1/b2b/orders`: Submits wholesale cases orders using trade credit approvals.

---

## 23. Corporate Gifting APIs

* `GET /api/v1/admin/gifting/requests` (Admin Only): Views bulk custom hamper logs.

---

## 24. Batch APIs

* `GET /api/v1/batches/{code}`: Public lookup page endpoint returning traceability parameters.
* `POST /api/v1/batches` (QA Only): Registers a new partner manufacturer production batch.

---

## 25. Manufacturer APIs

* `GET /api/v1/manufacturers` (QA/Admin Only): Lists partner manufacturer directories.
* `POST /api/v1/manufacturers/{id}/audit` (QA Only): Submits facility inspection logs.

---

## 26. Lab Certificate APIs

* `POST /api/v1/batches/{id}/certificate` (QA Only): Links lab validation PDF parameters to a batch.

---

## 27. Inventory APIs

* `GET /api/v1/inventories/{sku}` (Logistics Only): Retrieves stock on-hand allocations.
* `PATCH /api/v1/inventories/{sku}/stock` (Logistics Only): Modifies inventory counts.

---

## 28. Warehouse APIs

* `GET /api/v1/warehouses` (Logistics Only): Returns locations directory.

---

## 29. Notification APIs

* `POST /api/v1/notifications/dispatch` (System Only): Sends automated SMS, Email, or WhatsApp updates.

---

## 29a. Media APIs [NEW]

Supports centralized file asset registrations and pre-signed Cloudflare R2 uploads.

* `POST /api/v1/media/upload` (Admin/QA Only): Generates a pre-signed PUT upload URL for Cloudflare R2 storage or processes direct multipart uploads.
* `GET /api/v1/media/{id}`: Retrieves metadata (dimensions, etag, bucket details, filename) for a media asset.
* `DELETE /api/v1/media/{id}` (Admin Only): Soft deletes an asset from R2 bucket logs.

---

## 29b. Health & Monitoring APIs [NEW]

Provides metrics for infrastructure monitoring, cloud container orchestration (Kubernetes readiness/liveness), and platform uptime monitoring.

* `GET /api/v1/health`: Basic API liveness ping returning uptime and API version status.
* `GET /api/v1/health/database`: Verifies active connection pool state to MongoDB Atlas.
* `GET /api/v1/health/storage`: Validates connectivity and write parameters on Cloudflare R2 object storage.

---

## 30. Analytics & Summary APIs

* `GET /api/v1/admin/analytics/sales` (Admin Only): Returns dashboards logs (AOV, CAC, revenue).
* `GET /api/v1/admin/dashboard` [NEW] (Admin Only): Consolidates multi-module statistics into a single API payload containing total daily revenue, order volume, active customer registrations, pending inventory alerts, and active subscription counters.

---

## 31. CMS APIs

* `PATCH /api/v1/admin/cms/configs/{key}` (Admin Only): Updates visual settings or homepage configurations.

---

## 32. Admin APIs

* `POST /api/v1/admin/users/roles` (Admin Only): Modifies administrative permissions.

---

## 33. Error Response Standards

Every endpoint failure must return a standardized JSON error envelope to ensure Frontend API parsing stability.

```json
{
  "success": false,
  "error": {
    "code": "STRING_ERROR_CODE",
    "message": "User-friendly description explaining the failure.",
    "details": {},
    "timestamp": "Date"
  }
}
```

* **Standard Error Codes**:
  - `AUTHENTICATION_FAILED`: Token missing or expired.
  - `PINCODE_UNSERVICEABLE`: Logistics partners do not service input area.
  - `STOCK_INSUFFICIENT`: Variant quantity requested exceeds available warehouse stock.
  - `RESOURCE_NOT_FOUND`: Database target ID lookup returns null.

---

## 34. Pagination Standards

All list retrieval endpoints must enforce pagination using query parameters to limit server payload size.

* **Parameters**: `page` (default: 1), `limit` (default: 20, max: 100).
* **Response Envelope**:
```json
{
  "items": [],
  "pagination": {
    "current_page": 1,
    "limit": 20,
    "total_items": 142,
    "total_pages": 8
  }
}
```

---

## 35. Filtering & Sorting Standards

Filtering and sorting options are passed as URL query parameters.

* **Sorting Syntax**: `sort=price:asc` or `sort=order_date:desc`.
* **Filtering Syntax**: `filter=price:min:100;price:max:500;attributes.key:value`.

---

## 36. Rate Limiting Strategy

FastAPI middleware implements IP-based and Token-based bucket limit controls.

* **Public APIs**: 60 requests per minute per IP address.
* **Sensitive Endpoints** (`/auth/otp/*`, `/checkouts/complete`): Max 5 attempts per 10 minutes to prevent brute-force attacks and carding fraud.
* **Corporate B2B Accounts**: Expanded limit of 200 requests per minute.

---

## 37. Versioning Strategy

* **URL Routing**: API changes are tracked using version prefixes in the URL path.
  - *Example*: `/api/v1/products` vs `/api/v2/products`.
* **Deprecation Notice**: Legacy API paths append a deprecation warning header (`Deprecation: true`) 90 days before final route removal.

---

## 38. Webhook Strategy

Enables asynchronous system communications with third-party partners (e.g., Shiprocket tracking state adjustments, Razorpay charge events).

* **Header Verifications**: Every inbound webhook call must contain a custom signature header (`X-Hub-Signature`) generated using shared API secret keys to verify request authenticity.
* **Retry Strategy**: Webhooks expecting delivery confirmation will automatically retry using an exponential backoff strategy (up to 5 attempts) upon receiving error codes (non-2xx).

---

## 39. Event Publishing Strategy

The API publishes events asynchronously to decoupling integration jobs.

* **Architecture**: FastAPI background tasks dispatch transactional payloads to the `domain_events` MongoDB collection.
* **Consumer Decoupling**: Downstream services (e.g., ERP sync, CRM automation) consume event logs independently, protecting checkout speed from pipeline failures.

---

## 40. Future Microservice Readiness

To ensure the backend can migrate from a monolith to independent microservices:

* **Logical Decoupling**: Code packages map strictly to domain boundaries. Cross-package actions must use asynchronous events rather than direct database imports.
* **Shared Authentication**: Centralize JWT signature checks in an API Gateway layer (like Kong or AWS API Gateway), leaving downstream microservices to verify payloads without calling databases.

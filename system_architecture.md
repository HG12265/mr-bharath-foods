# System Architecture Document

## Project: MR. BHARATH FOODS
**Document Version:** 1.1.0  
**Author:** Principal Software Architect & Staff Engineer  
**Date:** June 6, 2026  
**Status:** Approved for Implementation  

---

### Executive Summary

This document defines the high-level System Architecture for the **MR. BHARATH FOODS** enterprise platform. 

The architecture leverages **Next.js 15+** (with React Server Components) on the frontend and **FastAPI** (Python) on the backend. Data storage is anchored by **MongoDB Atlas** (Primary Document Store), **Redis** (Caching, Session Store, and Queue Broker), and **Cloudflare R2** (S3-compatible Object Storage). Payment collection uses **Razorpay**, and logistics uses **Shiprocket**. The system is built to scale to millions of users, providing modular code boundaries, strict authentication, and automated fallback capabilities.

---

## 1. System Topology Overview

```
                      ┌─────────────────────────────────┐
                      │        Cloudflare WAF / CDN     │
                      └────────────────┬────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼ (SSR / ISR / Client)                                ▼ (REST API / Webhooks)
┌───────────────────────┐                               ┌───────────────────────┐
│  Next.js 15 Frontend  │                               │    FastAPI Backend    │
│  (Vercel or Docker)   │                               │    (ECS / Gunicorn)   │
└───────────────────────┘                               └──────────┬────────────┘
                                                                   │
                               ┌───────────────────────────────────┼──────────────────────────────────┐
                               ▼ (Cache / Queue)                   ▼ (Transactional DB)               ▼ (Media / Files)
                    ┌───────────────────────┐           ┌───────────────────────┐           ┌───────────────────────┐
                    │    Redis Cache Cluster│           │     MongoDB Atlas     │           │     Cloudflare R2     │
                    └───────────────────────┘           └───────────────────────┘           └───────────────────────┘
```

---

## 2. Frontend Architecture (Next.js 15+)

* **Rendering Patterns**:
  - **Incremental Static Regeneration (ISR)**: Used for Product Listing Pages (PLPs), Category pages (`/shop/ghee`), and Blog articles. Revalidated every 60 minutes to ensure instant loads while keeping prices and SEO schemas fresh.
  - **Server-Side Rendering (SSR)**: Used for Product Detail Pages (PDPs) to display real-time stock balances and the active Batch Lab Certificate.
  - **Static Site Generation (SSG)**: Static pages (About Us, Sourcing Story, FAQs, Legal).
  - **Client-Side Rendering (CSR)**: Shopping Cart drawers, User Profiles, Checkouts, and dynamic Admin dashboards.
* **State Management**: React Context for global UI elements (e.g., active Cart status). React Query (TanStack Query) handles client-side caching and data pre-fetching.
* **UI Foundations**: Styled using **Tailwind CSS** and built with accessible **shadcn/ui** components.

---

## 3. Backend Architecture (FastAPI)

* **Execution Core**: Built on FastAPI, leveraging Python's async capabilities to handle high concurrency.
* **Server Runner**: Managed via **Uvicorn** workers orchestrated by a **Gunicorn** process manager.
* **Architectural Layering**: Enforces a strict separation of concerns using a three-tier model:
  1. **API Router Layer (Controller)**: Handles HTTP requests, parses schemas using Pydantic, and handles routing.
  2. **Service Layer**: Implements business rules, orchestrates operations across repositories, and publishes events.
  3. **Repository Layer**: Directly interacts with the database (using Motor, the async MongoDB driver) and handles data mapping.

---

## 3a. OpenAPI Contract Generation & Client SDKs [NEW]

FastAPI automatically generates live API specification metadata, ensuring strong alignment between backend and frontend systems.

* **Interactive Documentation**: Swagger UI (`/docs`) and ReDoc (`/redoc`) endpoints are enabled in non-production environments to allow support and QA engineers to test routes interactively.
* **Contract-First SDK Generation**: The generated `openapi.json` contract is compiled during CI/CD steps. Tooling (e.g., `openapi-typescript-codegen` or `orval`) compiles this JSON into type-safe TypeScript fetch clients for the Next.js frontend, ensuring zero type drift.
* **Future Mobile Integration**: The same OpenAPI definitions are used to compile client SDKs for future iOS/Android native mobile applications.

---

## 4. Project Folder Structure

A monorepo layout separating frontend layouts, API microservices, and shared configuration files.

```
/mr-bharath-foods
├── /frontend                    # Next.js 15 App Router codebase
│   ├── /src
│   │   ├── /app                 # App routes (layouts, pages, loading, error)
│   │   ├── /components          # Reusable UI elements (shadcn inputs, buttons)
│   │   ├── /hooks               # Custom React Query hooks
│   │   ├── /services            # API consumer definitions
│   │   ├── /styles              # Global styles (Tailwind / Design tokens)
│   │   └── /types               # TypeScript declarations
│   ├── next.config.ts
│   └── package.json
├── /backend                     # FastAPI Application codebase
│   ├── /app
│   │   ├── /api                 # API Routes (v1 controller modules)
│   │   ├── /core                # Configs, Security settings, Database sessions
│   │   ├── /models              # Pydantic schemas (requests/responses)
│   │   ├── /repositories        # Database interactions (Motor queries)
│   │   ├── /services            # Business rules processing
│   │   └── /tasks               # Background workers (Arq task queue definitions)
│   ├── Dockerfile
│   ├── main.py                  # Entrypoint
│   └── requirements.txt
└── docker-compose.yml           # Local multi-container development environment
```

---

## 5. Service Layer Design

* **Principle**: The Service Layer acts as the single source of truth for business logic. 
* **Guidelines**: Services must remain completely decoupled from HTTP protocols. They do not accept HTTP Request objects or return HTTP Responses; instead, they receive pure Python data models (Pydantic objects) and return domain models or throw custom exceptions (e.g., `OutOfStockException`).
* **Cross-Service Communication**: If a service needs to trigger actions in another domain, it publishes a domain event rather than directly calling the other service's repository.

---

## 6. Repository Layer Design

* **Principle**: Decouples business logic from data storage implementations, allowing database changes without altering services.
* **MongoDB Interaction**: Enforced through asynchronous operations using **Motor**. All queries use filters to bypass database-level table scans.
* **Transaction Bounds**: When operations affect multiple collections (e.g., completing a payment, decrementing stock, and creating an invoice), the Repository uses **MongoDB Client Sessions** to wrap writes in an ACID transaction.

---

## 7. Dependency Injection Strategy

* **Frontend**: Next.js 15 uses standard ES6 modules. Context providers inject global client dependencies (e.g., HTTP Fetch clients).
* **Backend**: FastAPI's native `Depends` system handles dependency injection. It manages:
  - Database sessions (injecting active Motor connections).
  - Current authenticated user context (injecting validated JWT scopes).
  - Background worker dispatch queues.
  - External integration clients (Razorpay, Shiprocket).

---

## 8. Authentication & Session Architecture

* **Mechanism**: JWT (JSON Web Tokens) with asymmetric keys.
* **Backend Validation**: FastAPI validates inbound signatures using public keys (`RS256`), checking expiries and token blacklists stored in Redis.
* **Next.js Integration**: Middleware intercepts client requests to `/me/*` and `/checkout/*`. If the access token is missing, the frontend calls `/api/v1/auth/refresh` to exchange the refresh cookie for a new access token. If this fails, the user is redirected to the OTP login screen.

---

## 9. RBAC Implementation Architecture

* **Authorization Engine**: FastAPI dependency injection evaluates permissions dynamically.
* **Workflow**:
  - JWT is parsed to retrieve the user's role profile.
  - A router decorator (e.g., `Depends(PermissionChecker(["EDIT_PRODUCTS"]))`) queries the requested route against the role profile.
  - If allowed, request execution continues. Otherwise, the router throws an HTTP `403 Forbidden` response.

---

## 9a. Feature Flags Strategy [NEW]

To roll out features (e.g., `subscriptions`, `b2b_portal`, `trust_center`) without requiring new code deployments, the platform implements a runtime Feature Flag system.

* **Configuration Storage**: Feature flag states are stored in a dedicated `feature_flags` MongoDB collection and cached in Redis with a 5-minute TTL.
* **Client-Side Evaluation**: Next.js middleware fetches active flags to dynamically render layouts, hiding or showing B2B portals or subscription options.
* **Backend Middleware**: FastAPI route controllers verify the feature flag state before executing requests (e.g., blocking subscription creations if the flag is disabled).

---

## 10. Redis Architecture

Redis serves three primary functions on the backend:

```
                            ┌──────────────────────────────────┐
                            │          REDIS CLUSTER           │
                            ├──────────────────────────────────┤
                            │  - LRU Cache (Products/Configs)  │
                            │  - Session Blacklist (Revocations)│
                            │  - Rate Limiting Token Buckets   │
                            └──────────────────────────────────┘
```

* **Caching**: Stores resolved Category taxonomy trees and common Product attributes, using a 1-hour time-to-live (TTL).
* **Session Store**: Tracks revoked or logged-out JWT tokens until their natural expiry time.
* **Rate Limiting**: Stores token buckets for IP and account limits.

---

## 11. Cloudflare R2 Storage & Optimization Architecture

Cloudflare R2 provides object storage for static files.

* **Upload Workflow**: To secure uploads and minimize server load, the frontend bypasses backend proxies:
  1. Next.js requests a pre-signed URL from FastAPI (`POST /api/v1/media/upload`).
  2. FastAPI validates permissions, requests a pre-signed URL from R2, registers a pending asset inside `media_assets`, and returns the URL.
  3. Next.js uploads the file directly to R2 using a `PUT` request.
* **CDN Distribution**: Cloudflare CDN caches files globally, serving them via optimized image/video subdomains.
* **Media Optimization Pipeline [NEW]**: Upon successful upload, a webhook triggers a background worker task to process the file:
  - Generates optimized **WebP/AVIF** formats.
  - Splits assets into variants: **Original**, **Tablet**, **Mobile**, and **Thumbnail** (100x100).
  - Saves optimized files back to R2, updating the `media_assets` registry.

---

## 12. Background Jobs Architecture

* **Worker Framework**: Built using **Arq** (Redis-based queue manager).
* **Execution**: Worker processes run in separate Docker containers, subscribing to Redis queues.
* **Redis Queue Separation [NEW]**: Instead of a single queue, tasks are partitioned into distinct priority channels:
  - `high_priority`: OTP dispatches, payment confirmation webhooks, and transaction event publishings.
  - `default`: Cart validations, order processing, and subscription billing renewals.
  - `low_priority`: Image optimization pipelines, nightly analytical reports, and data archiving.
  - `dead_letter`: Catches and isolates tasks that fail repeatedly (max 3 retries) for support inspection.

---

## 13. Notification Architecture

Coordinates communications across WhatsApp, SMS, and Email:

```
                     ┌────────────────────────────────┐
                     │     Notification Dispatcher    │
                     └───────────────┬────────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼ (SMS / WhatsApp)        ▼ (Transactional Email)   ▼ (In-App Updates)
 ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
 │   Twilio / Gupshup│     │   Postmark / SES  │     │   WebSocket Push  │
 └───────────────────┘     └───────────────────┘     └───────────────────┘
```

* **Priority Routing**: Transactional order notifications (OTP, Payment Confirmed, Shipped) use dedicated high-priority SMS/WhatsApp dispatch pipelines. Marketing messages are routed through low-priority background queues.

---

## 14. Event Processing Architecture

* **Broker**: Redis Pub/Sub acts as the fast message broker.
* **Transactional Logging**: Events are recorded in the `domain_events` MongoDB collection to provide audit trails.
* **Outbox Pattern**: Changes to business documents (e.g., creating an order) write a corresponding transaction to the event collection in the same database session. A background job polls these entries and publishes them, ensuring events are reliably delivered.

---

## 15. Docker Architecture

Container configurations are split into multi-stage Docker builds to keep production images small.

* **Frontend Build**: Stage 1: Install dependencies and build static Vercel outputs. Stage 2: Deploy using a minimal Node.js Alpine base image.
* **Backend Build**: Stage 1: Compile native dependency libraries. Stage 2: Copy libraries into a slim Python base image, running Uvicorn as a non-root user.
* **Local Development**: Managed via `docker-compose.yml` to orchestrate Next.js, FastAPI, Redis, and a local MongoDB instance.

---

## 16. Environment Variable Strategy

* **Configuration Tool**: FastAPI uses **Pydantic Settings** to validate variables at startup, blocking launch if critical credentials are missing.
* **Management**: Development settings use local `.env` files. Production variables are injected securely using secret managers (e.g., AWS Secrets Manager or HashiCorp Vault).
* **Next.js Separation**: Public variables are prefixed with `NEXT_PUBLIC_` to expose them to browser builds. All other variables (like R2 secret access keys) remain private to server runtimes.

---

## 17. Logging Architecture

* **Framework**: Python's native asynchronous logging system, configured to output structured JSON.
* **Format**:
```json
{
  "timestamp": "Date",
  "level": "INFO",
  "module": "app.services.checkout",
  "trace_id": "UUIDv4",
  "message": "Cart completed successfully.",
  "context": {
    "order_number": "MBF-92842",
    "customer_id": "ObjectId"
  }
}
```
* **Collection**: Log outputs are written to standard console streams (`stdout`) and forwarded to central logging services (such as Datadog or ELK Stack).

---

## 18. Monitoring Architecture

* **APM & Tracing**: **OpenTelemetry** middleware logs request traces across Next.js and FastAPI services.
* **Infrastructure Monitoring**: Datadog or Prometheus scrape resource metrics (CPU, Memory, Network IO, DB Connections).
* **Ecommerce Metrics**: Automated scripts query MongoDB to log daily conversion ratios, checkout drop-offs, and payment failures.

---

## 19. Deployment Architecture

* **Hosting Model**: Deployed across **AWS (Amazon Web Services)**.
* **Services Used**:
  - **AWS ECS (Fargate)**: Runs backend container groups, auto-scaling instances based on average memory and CPU utilization.
  - **Next.js Hosting**: Hosted on **Vercel** or **AWS Amplify** to leverage edge caching and global CDNs.
  - **MongoDB Atlas**: Managed database layer distributed across three availability zones.
  - **Cloudflare**: Handles DNS routing, edge SSL termination, and WAF protection.

---

## 20. CI/CD Pipeline Architecture

```
[ Git Push ] ──► [ Lint & Type Checks ] ──► [ Run Unit Tests ] ──► [ Docker Build & Push ] ──► [ ECS Deploy ]
```

* **Runner**: GitHub Actions or GitLab CI.
* **Pipelines**:
  - **Pull Request Stage**: Runs linting, checks TypeScript compiler rules, and executes unit tests.
  - **Merge to Main Stage**: Automatically builds Docker images, pushes them to AWS ECR, and initiates a rolling deploy to ECS Fargate.

---

## 21. Security Architecture

* **WAF Protection**: Cloudflare blocks bots, SQL injections, and cross-site scripting (XSS) at the edge.
* **API Protection**: Cors headers restrict requests to authorized domains. Sensitive operations are protected by rate limiters.
* **Data Privacy**: Customer details (PII) are encrypted at rest inside MongoDB using AES-256. Private variables are stored securely using secrets managers.

---

## 22. Caching Strategy

```
  Next.js Server (ISR) ──► Redis (Variant Prices/Specs) ──► MongoDB (Primary Read)
  (Expires: 1 hour)        (Expires: 24 hours)             (Cold storage fallback)
```

* **Edge Caching**: Cloudflare caches product images and static pages.
* **Page Caching**: Next.js uses Incremental Static Regeneration (ISR) to cache category landing pages.
* **Database Caching**: Redis caches commonly read product variants and prices.

---

## 23. Scalability Strategy

* **Stateless Scaling**: API servers do not store state, allowing ECS to spin up new instances during traffic surges without disrupting active users.
* **Database Read Scaling**: Read-heavy queries are routed to MongoDB secondary replicas, keeping the primary database node dedicated to checkouts.
* **Task Offloading**: Slow operations (generating tax invoices, sending notifications) are offloaded to background workers to keep checkout times fast.

---

## 24. Failure Recovery Strategy

* **Database Failover**: MongoDB Atlas manages database failover automatically, promoting a secondary replica node in under 30 seconds if the primary node goes offline.
* **Gateway Fallbacks**: If Razorpay experiences issues, the system displays a clear message to switch to alternative payment options.
* **Dead Letter Queues**: Failed background tasks are automatically moved to a Dead Letter Queue (DLQ) in Redis for investigation rather than blocking the main task queue.

---

## 25. Production Readiness Checklist

Before moving the platform to production, ensure these checks are completed:

- [ ] **Secrets Auditing**: No API keys or passwords are committed to code files. Secrets are managed in Cloudflare or AWS Secrets Manager.
- [ ] **Index Verification**: Ensure all search properties in MongoDB collections have corresponding indexes.
- [ ] **Load Testing**: Verify the API handles expected launch traffic levels.
- [ ] **Failover Testing**: Verify database and cache failover routines.
- [ ] **FSSAI Compliance**: Verify FSSAI registrations and FSSAI logo are visible on the storefront footer.
- [ ] **Rate Limiting Verification**: Verify rate limiters block brute-force attempts on sensitive endpoints.
- [ ] **SSL Enforcement**: Verify all HTTP connections redirect to HTTPS using TLS 1.3.
- [ ] **Payment Verification**: Verify webhook signatures are validated for payment confirmation endpoints.
- [ ] **Log Verification**: Verify error outputs do not contain sensitive customer information (PII).
- [ ] **Uptime Checks**: Verify external health monitoring probes are configured.

# Project Folder Structure & File Registry

## Project: MR. BHARATH FOODS
**Document Version:** 1.0.0  
**Author:** Principal Software Architect  
**Date:** June 6, 2026  
**Status:** Approved for Boilerplate Initialization  

---

### Executive Summary

This document outlines the complete project folder structure and file registry for the **MR. BHARATH FOODS** monorepo.

The architecture is divided into two primary services:
1. **/frontend**: Next.js 15+ (TypeScript, Tailwind CSS, shadcn/ui, TanStack Query) using the App Router.
2. **/backend**: FastAPI (Python, MongoDB Atlas, Redis, Arq Task Queues) following a modular repository-service pattern.

---

## 1. Monorepo Root Directory Structure

The monorepo root configures multi-service local environments and documentation.

```
/mr-bharath-foods
├── docker-compose.yml           # Runs local database (MongoDB), cache (Redis), and api services
├── .gitignore                   # Excludes dependencies, configs, and builds across services
├── README.md                    # Setup guides, tech stack details, and contribution instructions
├── /frontend                    # Next.js 15 App Router directory (detailed in Section 2)
└── /backend                     # FastAPI Application directory (detailed in Section 3)
```

---

## 2. Frontend Directory Structure (`/frontend`)

The Next.js 15 application handles rendering, state management, and user interaction.

```
/frontend
├── next.config.ts               # Next.js compiler settings, asset CDN domains (R2 links), and headers
├── package.json                 # Next.js dependencies, linting scripts, and compiler commands
├── tsconfig.json                # TypeScript compilation paths and validation settings
├── tailwind.config.ts           # CSS variables mapped from the Brand Design System
├── postcss.config.mjs           # CSS post-processing presets for Tailwind
├── /src                         # Application source files
│   ├── /app                     # Next.js 15 App Router layout tree
│   │   ├── layout.tsx           # Global HTML document wrapper (fonts, provider layers, analytics GTM)
│   │   ├── page.tsx             # Homepage file containing primary visual grid templates
│   │   ├── globals.css          # Core CSS stylesheet housing brand variables
│   │   ├── /shop                # Shop collection routes
│   │   │   ├── page.tsx         # Category List page (PLP)
│   │   │   └── /[category]      # Dynamic category folders
│   │   │       └── page.tsx     # Dynamic Category landing hubs (e.g., /shop/ghee)
│   │   ├── /products            # Product details routes
│   │   │   └── /[slug]          
│   │   │       └── page.tsx     # Product detail pages (PDP) with batch trace links
│   │   ├── /compare             
│   │   │   └── page.tsx         # Product Compare side-by-side spec sheets page
│   │   ├── /trust               
│   │   │   └── page.tsx         # Trust Portal lookup and certification directories page
│   │   ├── /checkout            
│   │   │   └── page.tsx         # Distraction-free multi-step payment wizard page
│   │   ├── /order               
│   │   │   └── /[id]            
│   │   │       └── page.tsx     # Static invoice summary page and support anchors
│   │   ├── /blog                
│   │   │   ├── page.tsx         # Recipe article index directories page
│   │   │   └── /[slug]          
│   │   │       └── page.tsx     # Detailed post content containing inline buy cards
│   │   └── /account             
│   │       ├── page.tsx         # Customer Portal dashboard (orders, points balances)
│   │       └── /subscriptions   
│   │           └── page.tsx     # Subscription controller portals (Skip, Swap, Cancel)
│   ├── /components              # Reusable component components
│   │   ├── /ui                  # Atomic shadcn components
│   │   │   ├── button.tsx       # Standard action button
│   │   │   ├── badge.tsx        # Status/Curation indicators
│   │   │   ├── input.tsx        # Form input fields
│   │   │   ├── select.tsx       # Dropdown selection fields
│   │   │   ├── table.tsx        # Structured tabular layouts
│   │   │   ├── dialog.tsx       # Pop-up modals
│   │   │   └── drawer.tsx       # Slide-out cards containers (e.g., Cart Drawer)
│   │   ├── /layout              # Structural page blocks
│   │   │   ├── container.tsx    # Width boundary wrappers
│   │   │   └── grid.tsx         # Column configuration adapters
│   │   ├── /navigation          # Navigation headers and footers
│   │   │   ├── header.tsx       # Header menu and search buttons
│   │   │   ├── mobile-nav.tsx   # Sticky bottom-anchored mobile navbar
│   │   │   ├── footer.tsx       # Footer content (disclosures, legal nodes)
│   │   │   └── breadcrumbs.tsx  # Dynamic path locator links
│   │   └── /features            # Domain-specific components
│   │       ├── /catalog         # Product Cards, filter sidebar structures
│   │       ├── /cart            # Slide-over cart item cards
│   │       ├── /checkout        # Multi-step steppers, address forms
│   │       ├── /trust           # Traceability input panels, timeline visualizations
│   │       └── /account         # Loyalty point widgets, subscription calendars
│   ├── /hooks                   # Custom React hooks (React Query consumers)
│   │   ├── use-cart.ts          # Manages cart additions and updates
│   │   ├── use-checkout.ts      # Tracks wizard step validations
│   │   └── use-products.ts      # Handles product fetch, comparisons, and caching
│   ├── /services                # API communication clients
│   │   ├── api-client.ts        # Axios/Fetch setup with JWT interceptors
│   │   ├── product-service.ts   # Retrieves catalog listings and batch certs
│   │   └── checkout-service.ts  # Handles order submissions and coupons
│   ├── /services                # Custom frontend services
│   ├── /styles                  # Design token variables stylesheets
│   └── /types                   # Static TypeScript interface declarations
```

---

## 3. Backend Directory Structure (`/backend`)

The FastAPI application processes API requests, business logic, and background jobs.

```
/backend
├── requirements.txt             # Python packages (FastAPI, Motor, Arq, Pydantic)
├── Dockerfile                   # Multi-stage production container setup
├── main.py                      # Application entrypoint configuring CORS and routes
├── .env.example                 # Templates for Atlas links, R2 keys, and Redis creds
├── /app                         # Main application directory
│   ├── __init__.py              
│   ├── /api                     # Routing layer (Controllers)
│   │   ├── __init__.py          
│   │   ├── deps.py              # FastAPI dependencies (DB context, Auth, rate limiters)
│   │   └── /v1                  # Versioned API endpoints
│   │       ├── __init__.py      
│   │       ├── auth.py          # OTP requests, JWT issuance and refresh
│   │       ├── products.py      # Catalog endpoints and compare lists
│   │       ├── categories.py    # Tax mappings and navigation structures
│   │       ├── carts.py         # Persistent active session carts
│   │       ├── checkouts.py     # Pincode servicing checks and order processing
│   │       ├── orders.py        # Customer transaction histories
│   │       ├── payments.py      # Gateway verifying hooks and refunds
│   │       ├── batches.py       # QA audit logs and traceability lookups
│   │       ├── media.py         # R2 pre-signed URL generation endpoints
│   │       └── health.py        # DB, Storage, and system monitoring probes
│   ├── /core                    # Application configuration modules
│   │   ├── __init__.py          
│   │   ├── config.py            # Pydantic Settings system configurations
│   │   ├── security.py          # RS256 hashing and JWT validations
│   │   └── database.py          # Motor MongoDB Atlas connection handlers
│   ├── /models                  # Data validation validation schemas (Pydantic)
│   │   ├── __init__.py          
│   │   ├── base.py              # Base MongoId validation class models
│   │   ├── product.py           # Catalog dynamic schema validators
│   │   ├── customer.py          # Addresses and profile preferences
│   │   ├── order.py             # Snapshots and payment parameters
│   │   └── batch.py             # Lab certificate validations
│   ├── /repositories            # Raw database operations (Motor)
│   │   ├── __init__.py          
│   │   ├── base.py              # Abstract repository methods (Find, Insert, Update)
│   │   ├── product_repository.py# Product collection queries and filters
│   │   ├── order_repository.py  # Order creation sessions (ACID transactions)
│   │   └── batch_repository.py  # Batch lookup index operations
│   ├── /services                # Business logic services
│   │   ├── __init__.py          
│   │   ├── product_service.py   # Processes product compare charts
│   │   ├── checkout_service.py  # Deducts inventory and verifies coupons
│   │   └── payment_service.py   # Processes Razorpay payment verifications
│   └── /tasks                   # Background workers (Arq)
│       ├── __init__.py          
│       ├── worker.py            # Main queue subscription configuration
│       └── media_tasks.py       # AVIF/WebP image optimizations pipeline
```

---

## 4. Scalability & Code Boundaries

* **Monorepo decoupings**: The monorepo separates Next.js and FastAPI completely, allowing Vercel to host the frontend while AWS Fargate ECS runs the backend independently.
* **Component-Service separation**: The frontend's component layer (`/components`) is decoupled from the api client layer (`/services`). If Next.js moves to a mobile React Native structure, the API services copy over directly without visual rendering issues.
* **Service-Repository boundary**: FastAPI routes never interact with the database directly. They verify routes through dependencies (`deps.py`), call business logic layers (`/services`), and leave the repository layer (`/repositories`) to handle raw database updates.

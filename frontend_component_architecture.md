# Frontend Component Architecture & Inventory

## Project: MR. BHARATH FOODS
**Document Version:** 1.0.0  
**Author:** Principal Frontend Architect & Design System Engineer  
**Date:** June 6, 2026  
**Status:** Approved for Frontend Implementation  

---

### Executive Summary

This document defines the Component Inventory and Frontend Architecture for the **MR. BHARATH FOODS** storefront. 

Designed for **Next.js 15+** and **TypeScript**, the architecture segregates layout structures, navigation blocks, page-level grids, and shared atomic UI elements (powered by **shadcn/ui** and styled with **Tailwind CSS**). It establishes strict boundaries for React Server Components (RSC) vs. Client Components, accessibility requirements (WCAG AAA), and token mappings from the Brand Design System, ensuring future adaptability for React Native mobile builds.

---

## 1. Component Hierarchy (Monorepo Registry)

```
/frontend/src
├── /components
│   ├── /ui                  # Atomic components (Base buttons, inputs, tables)
│   ├── /layout              # Structural elements (Grid, Container, Sidebar)
│   ├── /navigation          # Header, Mobile Nav, Footers, Breadcrumbs
│   └── /features            # Domain-specific components
│       ├── /catalog         # Product Cards, Filter chips, Compare charts
│       ├── /cart            # Cart Drawer, Cart Item lines
│       ├── /checkout        # Wizard Steppers, Address selectors, Payment widgets
│       ├── /trust           # Batch trace inputs, timeline charts, audit logs
│       ├── /account         # Dashboard summaries, subscription calendars
│       └── /admin           # PIM tables, CMS builders, analytics gauges
```

---

## 2. Shared UI Components (Atomic Design System)

* **Button**:
  - *Variants*: Primary (Solid Indian Ink), Secondary (Outlined Indian Ink), Ghost (Text-only), Destructive (Crimson status fill).
  - *Interactive States*: Hover (opacity shifts), Focus (ring outline), Active (98% scaling), Disabled (muted fill).
* **Badge**:
  - *Variants*: Trust Gold ("CURATED"), Sage Green ("✓ Certified A2"), Muted Grey (Standard).
* **Typography**: Custom wrapper elements managing semantic tags (`<h1>`, `<p>`, `<span>`) mapped to Cormorant Garamond and Outfit fonts.

---

## 3. Layout Components

* **Container**: Manages responsive horizontal padding limits across viewports (max-w-7xl, mx-auto).
* **Grid**: A configurable CSS Grid wrapper standardizing column counts and gutters (e.g., 24px grid gap for desktop, 12px for mobile).
* **Flex**: Flexbox layout wrapper managing alignment, distribution, and wrap properties.

---

## 4. Navigation Components

* **Header**: Contains desktop mega-menu dropdowns, logo, search input toggles, and user account buttons.
* **MobileNavbar**: Bottom-anchored sticky bar containing tabs: Home, Search, Account, and Wishlist.
* **Breadcrumb**: Dynamic list generating active paths matching URL parameters (e.g., `Home > Shop > Ghee`).

---

## 5. Homepage Components

* **HeroSection**: Editorial typography stack with background visual layers and dual CTA buttons.
* **EthosBanner**: A 3-column layout highlighting key values (Verification, Auditing, Safety Seals).
* **FeaturedCatalog**: A grid layout displaying cards of featured products.

---

## 6. Product Listing Page (PLP) Components

* **CategoryHero**: Large header component presenting category context.
* **FilterSidebar**: Left-aligned panel containing checkboxes for product attributes and a price slider (collapses to slide-up drawer on mobile).
* **ActiveChips**: Flex row containing removable text chips representing currently active filter selections.

---

## 7. Product Detail Page (PDP) Components

* **ImageGallery**: 1:1 aspect ratio viewer showcasing product photos with zoom overlays and video player drawers.
* **PurchaseCard**: Selector for volume sizes, purchase type toggles (one-time vs. subscription), and add-to-cart buttons.
* **TransparencyTab**: Renders active Batch ID details and downloadable PDF report buttons.

---

## 8. Trust Center Components

* **TrustHeader**: Page introduction banner highlighting quality curation standards.
* **ReportGrid**: Catalog interface listing available lab report files sorted by date and batch.
* **EscalationForm**: Direct contact ticket submission form routed directly to internal QA queues.

---

## 9. Batch Lookup Components

* **BatchSearchBar**: Form input validating batch string profiles (e.g., "UT-2026").
* **TraceTimeline**: Graphic timeline displaying verification milestones from curd-churning to warehouse intake.
* **CertificateCard**: Visual readouts displaying purity testing parameters (A2 protein checks, moisture limits).

---

## 10. Blog Components

* **ArticleCard**: Visual preview cards displaying article metadata and reading times.
* **ShopThePost**: Dynamic sidebar displaying product purchase cards linked to ingredients listed in blog posts.
* **AuthorCard**: Biography widget detailing writer credentials to support E-E-A-T.

---

## 11. Search Components

* **SearchModal**: Full-screen modal overlay containing search input triggers.
* **AutosuggestList**: Real-time keyword suggestion lists showing search analytics matches.
* **NoResultsCard**: Empty fallback page recommending popular categories.

---

## 12. Cart Components

* **CartDrawer**: Slide-out sidebar container managing cart items.
* **CartItem**: Line card showing product thumbnail, quantity buttons, and price summaries.
* **ShippingProgressBar**: Dynamic bar tracking remaining cart value needed to qualify for free shipping.

---

## 13. Checkout Components

* **CheckoutWizard**: 3-step form wizard managing checkout states.
* **AddressSelector**: Radio selection lists showing saved shipping addresses with default check options.
* **GSTINInput**: Conditional input form verifying company registration codes.

---

## 14. Order Components

* **InvoiceCard**: Print-ready order summary displaying billing, shipping, and item details.
* **OrderList**: Scrollable list of past transactions with 1-click reorder buttons.

---

## 15. Wishlist Components

* **WishlistGrid**: Grid card repository showing saved products.
* **WishlistCard**: Muted product card layout containing quick-add triggers and remove buttons.

---

## 16. Account Dashboard Components

* **DashboardOverview**: Split summary panels displaying balance loyalty points, active subscriptions, and recent orders.
* **AddressBook**: Grid layout displaying saved addresses with Edit, Add, and Delete actions.

---

## 17. Subscription Components

* **SubscriptionCard**: Active contract layout displaying delivery dates and cancel links.
* **CycleScheduler**: Interactive date selector allowing users to skip next shipping cycles.
* **SwapSelector**: Dropdown list allowing subscribers to switch product variant items.

---

## 18. B2B Portal Components

* **WholesaleTable**: High-density bulk entry sheet displaying variant lines, wholesale prices, and quantity selectors.
* **CreditIndicator**: Alert bar showing approved trade credit limits and active balances.

---

## 19. Admin Dashboard Components

* **AdminSidebar**: High-contrast navigation links to PIM, Batches, Orders, and CMS controls.
* **StatCard**: Grid layout displaying transaction statistics (AOV, daily conversion rates).

---

## 20. Warehouse Dashboard Components

* **FulfillmentQueue**: Structured data list showing pick lists sorted by order date.
* **IntakeConsole**: Input form mapping incoming stock SKU identifiers, co-packer sources, and expiry dates.

---

## 21. Form Components

* **InputField**: Minimalist input field with floating labels and inline error blocks.
* **SelectDropdown**: Clean selector element with searchable option lists.
* **Checkbox**: Minimal checkbox input with outline focus indicators.

---

## 22. Table Components

* **DataTable**: Standardized list layout featuring horizontal grid lines, zebra rows, and sticky headers.
* **Pagination**: Navigation buttons (First, Prev, Page counter, Next, Last) with row limit controllers.

---

## 23. Modal Components

* **ModalDialog**: Centered overlay window with animated slide-in transitions.
* **QuickView**: PDP preview container launched from product card grids.

---

## 24. Drawer Components

* **SlideDrawer**: Interactive panel sliding in from side edges (e.g., Cart drawer, mobile menu).

---

## 25. Notification Components

* **Toast**: Floating alert notification sliding in from top-right boundaries (e.g., "Added to Cart").
* **AlertBanner**: Top-anchored warning banners (e.g., "Verification Quarantine Active").

---

## 26. Empty State Components

* **EmptyStateCard**: Informational panel featuring descriptive icons, explanatory text, and action buttons.

---

## 27. Loading Skeleton Components

* **ProductSkeleton**: Grey gradient grid mockups displaying card shapes to prevent Cumulative Layout Shift (CLS).
* **TableSkeleton**: Line bars mimicking text tables during administrative data requests.

---

## 28. Error State Components

* **RouteErrorBoundary**: System fallback screen presenting error logs, support numbers, and return-to-shop links.

---

## 29. Component Reuse Strategy

* **DRY (Don't Repeat Yourself)**: Visual components (buttons, input fields) are built once as atomic components in `/components/ui` and referenced by pages.
* **State Separation**: Atomic UI components are purely representational (receive values via props). Business logic is managed in container components (`/components/features`) or page-level controllers.

---

## 30. Design Token Mapping

Design tokens are mapped directly from the Brand Design System to Tailwind configurations:

```css
@theme {
  --color-indian-ink: #1C2321;
  --color-warm-ivory: #FAF9F6;
  --color-saffron: #9E4624;
  --color-deodhar: #1E352F;
  --color-navy: #18324B;
  --color-gold: #C49A45;
  
  --font-editorial: "Cormorant Garamond", serif;
  --font-interface: "Outfit", sans-serif;
  
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
}
```

---

## 31. State Management Boundaries

* **Global UI State**: React Context manages non-persistent UI states (e.g., sidebar visibility, search overlay triggers, active cart drawer open state).
* **Server-Cached State**: React Query (TanStack Query) handles API requests, query caching, and mutations (e.g., cart edits, subscription changes, wishlist additions).
* **Persistent Session State**: Browser local storage stores temporary guest cart tokens, with customer profiles managed by backend session variables.

---

## 32. Server Component vs. Client Component Strategy

Next.js 15 App Router utilizes React Server Components (RSC) to optimize load performance.

* **Server Components (RSC) (Default)**:
  - Used for static pages, category listings (PLP), blog post contents, recipe outlines, and sitemap footers.
  - *Benefits*: Faster page loads, improved search crawler indexing, and reduced client-side JavaScript payloads.
* **Client Components (`"use client"`)**:
  - Used for interactive inputs, checkout steppers, search modals, sliders, cart drawers, dynamic charts, and admin dashboards.
  - *Rule*: Place client components as far down the DOM tree as possible. E.g., render the PDP layout as a Server Component, but make the "Add to Cart" button a Client Component.

---

## 33. Accessibility Requirements (WCAG 2.2 AAA Compliance)

* **Contrast Ratios**: Every text element must meet minimum contrast ratios against backgrounds (minimum 4.5:1 for body copy, 7:1 for editorial headings).
* **ARIA Roles**: Screen-reader accessibility is enforced on interactive elements (e.g., cart drawer container gets `role="dialog"`, buttons get explicit `aria-label`).
* **Keyboard Navigation**: Interactive elements must support full keyboard navigation (Tab indices, Enter trigger buttons, Esc triggers to close drawers).

---

## 34. Responsive Behavior Requirements

* **Grid Auto-folding**: Grids fold responsively across breakpoints (e.g., 4-column product grids on desktop transform to 2-columns on tablet, and 1-column on mobile).
* **Touch Optimization**: Buttons and inputs on mobile must have tap target sizes of at least 48x48 pixels, spaced to prevent accidental activations.
* **Font Scaling**: CSS fluid typography variables automatically adjust text sizes between mobile and desktop limits without breaking column alignments.

---

## 35. Future Mobile App Compatibility Considerations

* **Shared Logic layer**: Business services, API consumers, and React Query data hooks are isolated from UI components in a shared utilities folder (`/services`).
* **Component Translation**: Shared UI layouts avoid custom CSS utilities in favor of component primitives that translate directly to React Native styling variables.
* **Design Token Portability**: Token definitions are exported as JSON files, allowing them to be imported directly by React Native styling engines.

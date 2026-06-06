# Domain Model Architecture

## Project: MR. BHARATH FOODS
**Document Version:** 1.1.0  
**Author:** Principal Domain Architect & Enterprise Database Designer  
**Date:** June 6, 2026  
**Status:** Approved for Database Schema Planning  

---

### Executive Summary

This document defines the Domain Model Architecture for the **MR. BHARATH FOODS** enterprise platform. 

Using Domain-Driven Design (DDD) principles, this architecture outlines Bounded Contexts, Aggregates, Entities, Value Objects, Lifecycles, and Domain Events. It is designed to scale dynamically from the initial Ghee products to hundreds of SKUs across future categories (Oils, Honey, Rice, Spices, Traditional Foods, and Health Foods), while maintaining strict traceability and compliance metrics.

---

## 1. Core Business Entities

The business model relies on curation and selection, dividing operations into core entities:

* **Product / Variant**: The catalog items offered under the brand.
* **Partner Manufacturer**: Certified co-packing partners supplying products.
* **Inventory Batch**: Traceable production batches associated with safety and origin certificates.
* **Customer**: Registered buyers (B2C and B2B).
* **Order / Shipment**: Commercial transaction and physical fulfillment logs.
* **Trust Certificate**: Laboratory verification records proving product purity.
* **Cart**: Active shopping sessions for guest and registered buyers. [NEW]
* **Return Request**: Customer reverse logistics claim logs for eligible orders. [NEW]

---

## 2. Entity Relationships

```
              ┌───────────────────┐
              │   Category        │
              └─────────┬─────────┘
                        │ 1
                        │
                        │ *
  ┌──────────┐ 1      * ┌───────────┐ 1       * ┌──────────┐
  │ Partner  ├──────────┤  Product  ├───────────┤ Variant  │
  └────┬─────┘          └─────┬─────┘           └───┬──────┘
       │                      │ 1                   │ 1
       │ 1                    │                     │
       │                      │ *                   │ *
       │ *       1            │ *       *           │ *
  ┌────┴─────┐ ───────────────┼─────────────────────┘
  │  Batch   │ ◄──────────────┘
  └────┬─────┘
       │ 1
       │
       │ 1
  ┌────┴─────┐
  │ Lab Cert │
  └──────────┘
```

---

## 3. Customer Domain

Contains registered user data and authentication boundaries.

* **Customer (Aggregate Root)**: Represents an individual or organization.
  - *Attributes*: ID, Auth Profile (Phone/Email with OTP credentials), Status (Active/Suspended), Account Type (Standard, VIP, B2B), Created Timestamp.
* **Preference Profile (Value Object)**: Stores dietary indicators (A2, organic, vegan) and default shipping/billing choices.

---

## 4. Product Domain

Contains core product definitions.

* **Product (Aggregate Root)**: A general food classification (e.g., "Uthukuli Ghee").
  - *Attributes*: ID, Name, Slug, Description, FSSAI Registration number, Sourcing Story, Sourcing Origin Region, Status (Draft, Active, Archived).
* **Product Attribute (Value Object)**: Dynamic key-value attributes (e.g., cattle breed: "Gir Cow", extraction method: "Cold-Pressed").

---

## 5. Category Domain

* **Category (Aggregate Root)**: A hierarchical node used for navigation and catalog structure.
  - *Attributes*: ID, Name, Slug, Description, Parent Category ID, Status (Active, Hidden), Meta Tags.
  - *Rules*: Supports nested subcategories (e.g., `Shop > Ghee > Cow Ghee`) with breadcrumb generation capabilities.

---

## 6. Variant Domain

* **Variant (Entity within Product Aggregate)**: Represents buyable configurations of a product (SKU).
  - *Attributes*: ID, SKU, Volume/Weight (e.g., 250ml, 500ml, 1L), Base Price, Comparative Member Price, UPC, Stock Status (In Stock, Out of Stock, Backordered).

---

## 7. Inventory Domain

* **Inventory Item (Aggregate Root)**: Physical stock allocated to storage slots.
  - *Attributes*: ID, Variant SKU, Current On-Hand Stock, Reserved Stock (e.g., locked for cart/subscriptions), Safety Stock Level.
  - *Warehouse Location (Value Object)*: Warehouse ID, Zone, Rack, Shelf identifier.

---

## 8. Batch Domain

Supports the brand's core requirement for traceability.

* **Batch (Aggregate Root)**: A physical production lot supplied by a co-packing partner.
  - *Attributes*: ID, Batch Code, Product ID, Manufacturer ID, Manufacture Date, Expiry Date, Total Production Volume, Quarantine Status (Passed, Failed, Pending Audit).

---

## 9. Manufacturer Domain

* **Partner Manufacturer (Aggregate Root)**: Certified facility profiles co-packing for MR. BHARATH FOODS.
  - *Attributes*: ID, Company Name, Contact Profile, FSSAI License Number, Audit History, Facilities Audit Rating, Active Contract Status (Active, Suspended).

---

## 10. Lab Certificate Domain

* **Lab Certificate (Entity within Batch Aggregate)**: Verification documentation for a batch.
  - *Attributes*: ID, Certifying Authority (e.g., AGMARK, NABL lab), PDF Document Link, Verification Date, Pure A2 Protein Indicator (Boolean), Chemical Purity Profile.

---

## 10a. Cart Domain

Supports active session persistence, guest-to-logged-in conversions, and recovery tracking.

* **Cart (Aggregate Root)**: Represents an active shopping session.
  - *Attributes*: ID, Customer ID (Nullable for Guests), Guest Token, Expiry Date, Cart Status (Active, Converted, Expired/Abandoned).
* **Cart Item (Entity)**: Individual products added by the user.
  - *Attributes*: Variant SKU, Quantity, Added Timestamp.

---

## 11. Order Domain

* **Order (Aggregate Root)**: Represents a transaction.
  - *Attributes*: ID, Order Number, Customer ID, Order Date, Total Amount, Discount Applied, Tax Amount (GST), Fulfillment State, Payment State.
* **Order Item (Entity)**: Individual line items inside an order.
  - *Attributes*: Variant SKU, Quantity, Price, Associated Production Batch ID.

---

## 11a. Return Domain

Supports reverse logistics. While food safety regulations limit returns, the system must support returns for instances of package damage or product defects.

* **Return Request (Aggregate Root)**: A claim filed by a customer.
  - *Attributes*: ID, Order ID, Customer ID, Return Request Code, Return Status (Submitted, Approved, Picked Up, Received, Rejected), Refund Status (Not Applicable, Refund Pending, Refunded, Store Credit Issued).
* **Return Item (Entity)**: Individual items claimed for return.
  - *Attributes*: Order Item ID, Quantity, Return Reason (Value Object containing Reason Code and Customer Notes), Photo Evidence Link.

---

## 12. Payment Domain

* **Payment (Entity within Order Aggregate)**: Financial transaction record.
  - *Attributes*: ID, Payment Gateway Reference ID (e.g., Razorpay ID), Payment Mode (UPI, Card, NetBanking, COD), Amount, Status (Authorized, Captured, Refunded, Failed), Timestamp.

---

## 12a. Tax Domain

Ensures platform compliance with GST changes and dynamic calculation snapshots.

* **Tax Profile (Aggregate Root)**: Geographic taxation settings.
  - *Attributes*: Country Code, State Code.
* **GST Rule (Value Object)**: Rules mapped to food categories (e.g., Ghee: 12% IGST, Oils: 5% IGST).
  - *Attributes*: Product Category ID, CGST Rate, SGST Rate, IGST Rate, HSN Code.
* **Tax Calculation Snapshot (Value Object)**: Stored per order to capture the exact tax rates applied at checkout.

---

## 13. Shipment Domain

* **Shipment (Entity within Order Aggregate)**: Logistics tracking record.
  - *Attributes*: ID, Shipping Carrier ID, Tracking Number, Ship Date, Estimated Delivery Date, Dispatch Warehouse ID, Shipment Status.
* **Shipment Event (Value Object)**: Log events returned by carrier tracking APIs.

---

## 14. Address Domain

* **Address (Value Object / Entity in Customer Aggregate)**: Locational data.
  - *Attributes*: Recipient Name, Phone Number, Street Address, Land Mark, Pincode, City, State, Country, Address Label (Home, Office, Billing, Shipping).

---

## 15. Coupon Domain

* **Coupon / Promotion (Aggregate Root)**: Rules engine for discounts.
  - *Attributes*: ID, Promo Code, Discount Type (Percentage, Fixed Amount, Free Shipping), Value, Expiry Date, Min Order Value, Total Usage Limit, Current Usage Count.

---

## 16. Wishlist Domain

* **Wishlist (Aggregate Root)**: Saves user favorites.
  - *Attributes*: ID, Customer ID, Created Date.
* **Wishlist Item (Entity)**: Variant SKU link.

---

## 17. Review Domain

* **Review (Aggregate Root)**: Customer-submitted feedback.
  - *Attributes*: ID, Product ID, Customer ID, Rating (1 to 5), Title, Body Copy, Media Links (images/video), Verified Buyer Indicator (Boolean), Approval Status (Pending, Approved, Flagged).

---

## 18. Subscription Domain

Supports the kitchen staples subscription model.

* **Subscription (Aggregate Root)**: Recurring delivery contract.
  - *Attributes*: ID, Customer ID, Shipping Address ID, Frequency (e.g., 30 Days), Start Date, Next Billing Date, Active Status (Active, Paused, Cancelled).
* **Subscription Item (Entity)**: Variant SKU, Quantity, Discount Rate.

---

## 19. Loyalty Points Domain

* **Loyalty Wallet (Aggregate Root)**: Customer's point balance ledger.
  - *Attributes*: ID, Customer ID, Total Balance, Tier Status.
* **Loyalty Ledger Entry (Entity)**: Transactional logs (Points Earned, Points Redeemed, Expiry Date, Order ID reference).

---

## 20. Blog Domain

* **Blog Article (Aggregate Root)**: Informational content.
  - *Attributes*: ID, Title, Author ID, Category, Body Content, SEO Metadata (Slug, Keywords), Published Date, Status (Draft, Published).
* **Featured Product Card (Value Object)**: Direct link to products featured in the article for in-blog purchasing.

---

## 21. FAQ Domain

* **FAQ Profile (Aggregate Root)**: Questions/Answers.
  - *Attributes*: ID, Question, Answer, Category Mapping (Checkout, Ghee, Shipping), Search Tags, Visible (Boolean).

---

## 22. Notification Domain

* **Notification Settings (Value Object)**: Manages communication preferences.
* **Notification Dispatcher (Aggregate Root)**: Tracking log for customer communications.
  - *Attributes*: ID, Customer ID, Channel Type (WhatsApp, SMS, Email), Template ID, Content, Delivery Status (Sent, Failed, Read).

---

## 23. Support Ticket Domain

* **Support Ticket (Aggregate Root)**: Customer issue tracker.
  - *Attributes*: ID, Customer ID, Reference Order ID, Channel Sourced, Status (Open, In Progress, Resolved, Escalated), Assigned Support Agent ID, Priority.
* **Ticket Comment (Entity)**: Chat responses between agent and customer.

---

## 24. B2B Customer Domain

* **B2B Profile (Entity within Customer Aggregate)**: Business accounts.
  - *Attributes*: ID, Company Legal Name, GSTIN, Trade Credit Limit, Assigned Account Manager ID, Approved B2B Discount Tier.

---

## 25. Corporate Gift Domain

* **Corporate Gift Request (Aggregate Root)**: custom gift logs.
  - *Attributes*: ID, Company Name, Contact Profile, Delivery Target Date, Total hampers, Branding Logo Asset Link, Quoted Price.

---

## 26. Warehouse Domain

* **Warehouse (Aggregate Root)**: Fulfillments centers location.
  - *Attributes*: ID, Code, Name, Full Address, Contact Profile, Serving Pincodes list (to route orders dynamically).

---

## 27. Audit Domain

* **Audit Log (Aggregate Root)**: System activity logger.
  - *Attributes*: ID, User ID (Admin/Warehouse/Support), Action Performed (e.g., "Updated Batch Stock"), Target Table/Entity, Timestamp, IP Address.

---

## 28. Analytics Domain

* **Metric Snapshot (Aggregate Root)**: Aggregated operational data.
  - *Attributes*: ID, Time Window, Metric Type (CAC, LTV, AOV, RTO rate, Cart Abandonment), Calculated Value.

---

## 29. CMS Domain

* **CMS Config (Aggregate Root)**: Dynamic home layout variables.
  - *Attributes*: ID, Config Key (e.g., "Homepage Hero Carousel"), Config JSON values, Active Status.

---

## 29a. Media Domain

Supports storage integration (Cloudflare R2/S3 object storage) and asset mappings across the catalog.

* **Media Asset (Aggregate Root)**: A file stored in object storage.
  - *Attributes*: ID, Filename, Mime Type, File Size, Target URL (R2 bucket link), S3 ETag, Created Timestamp.
* **Media Mapping (Value Object)**: Links media files to entities (e.g., Product Images, Recipe Videos, Batch Lab PDFs, Partner Audit Reports).
  - *Attributes*: Target Entity Name, Target Entity ID, Mapping Order (e.g., Sort order 1 for hero image).

---

## 29b. Search Domain

Optimizes SEO mapping, query suggestions, and customer search diagnostics.

* **Search Query (Aggregate Root)**: Represents a distinct search keyword searched by users.
  - *Attributes*: ID, Keyword phrase (lowercased), Performance hits, Conversion Rate.
* **Search Log (Entity)**: Daily tracking event log.
  - *Attributes*: Customer ID (Nullable), Keyword, Result Count returned, Selected Variant SKU (Nullable), Timestamp.
* **Search Suggestion (Value Object)**: Pre-compiled keywords displayed on focus inputs.

---

## 30. Role & Permission Domain

* **Role (Aggregate Root)**: Group level authorizations.
  - *Attributes*: ID, Role Name (Admin, Logistics, Support, QA Audit).
* **Permission (Value Object)**: Action rules mapped to roles (e.g., `READ_LAB_CERTS`, `EDIT_PRODUCT_PRICING`).

---

## 31. Event Domain

* **Domain Event Log (Aggregate Root)**: Event Sourcing / Event Log.
  - *Attributes*: ID, Event Type, Payload JSON, Occurred Timestamp, Processed Status.

---

## 32. Entity Lifecycle States

### Order Lifecycle States
```
[Created] ──► [Paid / COD Verified] ──► [Shipped] ──► [Delivered] ──► [Closed]
     │                 │                     │
     └─────────────────┴───────────► [Cancelled/Refunded]
```

### Batch Lifecycle States
```
[Quarantined] ──► [Audited & Lab Approved] ──► [Released for Sale] ──► [Sold Out]
      │
      └─────────► [Audit Failed] (Discarded/Returned)
```

### Return Request Lifecycle States
```
[Submitted] ──► [Approved] ──► [Reverse Pickup Dispatched] ──► [Received at WH] ──► [Inspected & Refunded]
                                                                                └──► [Rejected & Returned]
```

---

## 33. Aggregates

Aggregates define boundary logic:

* **Product Aggregate**: Root: **Product**. Entities: *Variant*. Value Objects: *Product Attribute*.
* **Order Aggregate**: Root: **Order**. Entities: *Order Item*, *Payment*, *Shipment*. Value Objects: *Shipment Event*.
* **Customer Aggregate**: Root: **Customer**. Entities: *B2B Profile*, *Address*. Value Objects: *Preference Profile*.
* **Batch Aggregate**: Root: **Batch**. Entities: *Lab Certificate*.
* **Cart Aggregate [NEW]**: Root: **Cart**. Entities: *Cart Item*.
* **Return Aggregate [NEW]**: Root: **Return Request**. Entities: *Return Item*. Value Objects: *Return Reason*.
* **Tax Aggregate [NEW]**: Root: **Tax Profile**. Value Objects: *GST Rule*, *Tax Calculation Snapshot*.
* **Media Aggregate [NEW]**: Root: **Media Asset**. Value Objects: *Media Mapping*.
* **Search Aggregate [NEW]**: Root: **Search Query**. Entities: *Search Log*. Value Objects: *Search Suggestion*.

---

## 34. Bounded Contexts

```
                     ┌──────────────────────────────────┐
                     │         ECommerce Context        │
                     │  - Product, Variant, Catalog,    │
                     │    Checkout, Subscription, Cart  │
                     └────────────────┬─────────────────┘
                                      │
                                      ▼ Shared Kernel
┌──────────────────────────────────┐  │  ┌──────────────────────────────────┐
│        Fulfillment Context       │◄─┘  │         Identity Context         │
│  - Warehouse, Inventory, Batch,  │     │  - Customer profiles, B2B, Auth, │
│    Shipment, Return Request      │◄────┤    Roles & Permissions           │
└────────────────┬─────────────────┘     └──────────────────────────────────┘
                 │
                 ▼ Upstream / Downstream
┌──────────────────────────────────┐
│      Quality & Audit Context     │
│  - Batch, Lab Cert, Manufacturer │
└──────────────────────────────────┘
```

---

## 35. Domain Events

Critical state changes published to notify downstream systems:

* `OrderCreated`: Fired upon payment capture/COD confirmation. Recommends stock hold.
* `BatchApproved`: QA checks passed. Variants map to this batch and are released for sale.
* `StockDepleted`: Inventory items drop below safety levels. Triggers purchase orders.
* `SubscriptionCharged`: Recurring payment processed. Creates a new fulfillment order.
* `BatchFailedLabAudit`: Flagged as Quarantine Failed. Immediately locks all associated variant listings.
* `CartAbandoned [NEW]`: Triggers recovery emails/WhatsApp prompts.
* `ReturnRequested [NEW]`: Starts the reverse-logistics picker dispatch.
* `RefundInitiated [NEW]`: Requests the payment gateway to process the refund.

---

## 36. Future Scalability Considerations

1. **Category Metadata Expansion**: The dynamic key-value schema for variants ensures that new categories (like Rice aging attributes or Honey flora metrics) can be added without altering the database schema.
2. **Decoupled Fulfillment (3PL)**: Keeping the **Fulfillment Context** isolated from the **Ecommerce Transaction Context** allows for routing logic changes (like switching from self-ship to Shiprocket or Delhivery) without affecting checkout pipelines.
3. **Audit Trails (Agmark / FSSAI)**: Storing historic Batch events ensures compliance logs can be exported directly for regulatory audits.
4. **Cloud Object Storage Strategy**: Implementing pre-signed URLs in the **Media Domain** ensures assets are fetched directly from Cloudflare R2/S3, eliminating load on application servers.

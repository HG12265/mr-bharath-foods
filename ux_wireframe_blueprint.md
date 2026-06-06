# UX Wireframe Blueprint

## Project: MR. BHARATH FOODS
**Document Version:** 1.1.0  
**Author:** Lead UX Architect & Interaction Designer  
**Date:** June 6, 2026  
**Status:** Approved for Frontend Design Execution  

---

### Executive Summary

This document contains low-fidelity ASCII wireframes for the **MR. BHARATH FOODS** enterprise ecommerce storefront. 

The wireframes translate specifications from the approved PRD, Brand Design System, and UX Blueprint into structured layouts, displaying component placement, section hierarchy, and responsive flows for both **Desktop** and **Mobile** viewports. 

---

## Page Navigation Flow Map

```
  [ Homepage ] ──► [ Shop Page (PLP) ] ──► [ Product Detail Page (PDP) ] ──► [ Cart Drawer ]
        │                  │                           │                            │
        │                  ▼                           ▼                            ▼
        ├───► [ Trust Center / Batch Lookup ]  [ Compare Portal ]           [ Checkout Wizard ]
        │                                                                           │
        │                                                                           ▼
  [ Account Dashboard ] ◄─────────────────────────────────────────────── [ Order Success ]
        │                                                                           │
        ├──► [ Subscription Manager ]                                               ▼
        ├──► [ Wishlist ]                                                   [ Order Tracking ]
        └──► [ B2B Portal ]
```

---

## 1. Homepage Wireframe

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   | <- Header (A:Account, C:Cart)
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   HERO PANEL:                                                                                    |
|                                                                                                  |
|   Selecting the Best to Serve the Best.                                                          |
|   We partner with specialized estates, verifying batch purity for every kitchen.                 |
|                                                                                                  |
|   [ EXPLORE PRODUCT RANGE ]    [ ABOUT OUR AUDITS ]                                              |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   WHY BHARATH FOODS?                                                                             |
|   +--------------------------+  +--------------------------+  +--------------------------+       |
|   | ✓ Regional Expertise     |  | ✓ Lab Verification       |  | ✓ Batch Transparency     |       |
|   | Sourced directly from    |  | Every batch analyzed by  |  | Enter batch codes to     |       |
|   | specialized estates.     |  | certified NABL labs.     |  | retrieve compliance PDFs.|       |
|   +--------------------------+  +--------------------------+  +--------------------------+       |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   OUR CORE ETHOS: CURATING TRUST                                                                 |
|   +--------------------------+  +--------------------------+  +--------------------------+       |
|   | [Icon]                   |  | [Icon]                   |  | [Icon]                   |       |
|   | 1. Partner Verification  |  | 2. Purity Lab Auditing   |  | 3. Zero plastic glass    |       |
|   | We audit farm co-packers.|  | Public test certifications|  | Sealed packaging safety  |       |
|   +--------------------------+  +--------------------------+  +--------------------------+       |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   CURATED STAPLES (FEATURED GRID)                                                               |
|   +--------------------------+  +--------------------------+  +--------------------------+       |
|   | [Image: Uthukuli Ghee]   |  | [Image: Rasipuram Ghee]  |  | [Image: Cold-Pressed Oil]|       |
|   | UTHUKULI GHEE     ★★★★★  |  | RASIPURAM GHEE    ★★★★★  |  | COCONUT OIL (COMING SOON)|       |
|   | Batch: UT-2026           |  | Batch: RS-2026           |  | Sourced: Pollachi region |       |
|   | 500ml - ₹599             |  | 500ml - ₹549             |  |                          |       |
|   | [ ADD TO CART ]          |  | [ ADD TO CART ]          |  | [ NOTIFY ME ]            |       |
|   +--------------------------+  +--------------------------+  +--------------------------+       |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
|   FOOTER                                                                                         |
|   FSSAI License No: 12345678901234                                                               |
|   Terms | Privacy | Help Center | B2B Portal                                                     |
+--------------------------------------------------------------------------------------------------+
```

### Mobile Layout
```
+-----------------------------------+
| [=]     MR. BHARATH FOODS     [C] | <- Header ([=] Menu, [C] Cart)
+-----------------------------------+
|                                   |
|  HERO PANEL:                      |
|  Selecting the Best               |
|  to Serve the Best.               |
|                                   |
|  [ EXPLORE PRODUCTS ]             |
|                                   |
+-----------------------------------+
|  WHY BHARATH FOODS?               |
|  - ✓ Regional Expertise           |
|  - ✓ Lab Verification             |
|  - ✓ Batch Transparency           |
|  - ✓ Curated Selection            |
+-----------------------------------+
|  CURATED PRODUCTS                 |
|  +-----------------------------+  |
|  | [Image: Uthukuli Ghee]      |  |
|  | UTHUKULI GHEE        ★★★★★  |  |
|  | Batch: UT-2026              |  |
|  | 500ml - ₹599                |  |
|  | [ ADD TO CART ]             |  |
|  +-----------------------------+  |
+-----------------------------------+
| [H] Home | [S] Search | [A] Account | <- Sticky Footer Navigation
+-----------------------------------+
```

---

## 2. Shop Page (PLP)

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  Breadcrumbs: Home > Shop > Ghee                                                                 |
+--------------------------------------------------------------------------------------------------+
|  HERO: Pure Ghee Curation (Rich, granular clarified butter sourced from traditional estates)     |
+--------------------------------------------------------------------------------------------------+
|  FILTERS                      |   PRODUCTS (Showing 2 items)                 Sort: [ Featured v ]|
|  [ ] Cow Ghee                 |   +------------------------+  +------------------------+         |
|  [ ] A2 Certified             |   | [Image: Uthukuli Ghee] |  | [Image: Rasipuram Ghee]|         |
|                               |   | UTHUKULI GHEE    ★★★★★ |  | RASIPURAM GHEE   ★★★★★ |         |
|  Size:                        |   | Batch: UT-2026         |  | Batch: RS-2026         |         |
|  ( ) 250ml                    |   | 500ml - ₹599           |  | 500ml - ₹549           |         |
|  ( ) 500ml                    |   | [ ADD TO CART ]        |  | [ ADD TO CART ]        |         |
|  ( ) 1L                       |   +------------------------+  +------------------------+         |
|                               |   [ Compare Ghee Varieties ]                                     |
+--------------------------------------------------------------------------------------------------+
|  Blog Articles: "Ayurvedic Benefits of Granular Ghee" | "Understanding Bilona Method"            |
+--------------------------------------------------------------------------------------------------+
```

### Mobile Layout
```
+-----------------------------------+
| [=]     MR. BHARATH FOODS     [C] |
+-----------------------------------+
| [ FILTER FILTERS ]  Sort: [Pop v] |
+-----------------------------------+
| +-------------------------------+ |
| | [Image: Uthukuli Ghee]        | |
| | UTHUKULI GHEE           ★★★★★ | |
| | 500ml - ₹599                  | |
| | [ ADD TO CART ]               | |
| +-------------------------------+ |
+-----------------------------------+
| [H] Home | [S] Search | [A] Account |
+-----------------------------------+
```

---

## 3. Product Detail Page (PDP)

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  Breadcrumbs: Home > Shop > Ghee > Uthukuli Ghee                                                 |
+--------------------------------------------------------------------------------------------------+
|                               │                                                                  |
|   [ PRODUCT IMAGE ]           │   UTHUKULI GHEE                                                  |
|                               │   ★★★★★ (142 Verified Reviews)                                   |
|   - Pure Glass Jar            │   Sourced from open-grazing pasture cows in Uthukuli.             |
|   - Granular Texture zoom     │                                                                  |
|   - Video of Viscosity        │   Size:  ( ) 250ml   (x) 500ml   ( ) 1L                          |
|                               │                                                                  |
|                               │   Purchase Mode:                                                 |
|                               │   (x) One-Time Purchase:  ₹599.00                                |
|                               │   ( ) Subscribe & Save:   ₹539.10 (Every 30 Days)                |
|                               │                                                                  |
|                               │   [ ADD TO CART ]     [ BUY NOW ]                                |
|                               │                                                                  |
|                               │   Active Shipping Batch: UT-2026  [View certificate]             |
+───────────────────────────────┴──────────────────────────────────────────────────────────────────+
|  TAB NAVIGATION: [ Sourcing details ]  [x] [ Lab Certificates ]  [ Customer Reviews ]            |
|  +--------------------------------------------------------------------------------------------+  |
|  | Verified laboratory certifications for Batch UT-2026:                                       |  |
|  | - Agmark Grade: Special Grade                                                              |  |
|  | - Hexane & Adulterants: Not Detected (0%)                                                  |  |
|  | [ DOWNLOAD LAB REPORT PDF ]                                                                |  |
|  +--------------------------------------------------------------------------------------------+  |
+--------------------------------------------------------------------------------------------------+
```

### Mobile Layout
```
+-----------------------------------+
| [=]     MR. BHARATH FOODS     [C] |
+-----------------------------------+
| [ PRODUCT IMAGE SHIFT CAROUSEL ]  |
+-----------------------------------+
| UTHUKULI GHEE                     |
| ★★★★ (142 reviews)               |
|                                   |
| Size: [ 250ml ] [x 500ml ] [ 1L ] |
|                                   |
| [ ADD TO CART ]                   |
| [ SUBSCRIBE & SAVE 10% ]          |
+-----------------------------------+
| Tabs: [ Sourcing ] [x Lab Reports]|
| Download Lab report PDF (UT-2026) |
+-----------------------------------+
| [H] Home | [S] Search | [A] Account |
+-----------------------------------+
```

---

## 3a. Compare Portal Page (/compare) [NEW]

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  Breadcrumbs: Home > Compare Products                                                            |
+--------------------------------------------------------------------------------------------------+
|  PRODUCT COMPARISON SHEETS                                                                       |
|                                                                                                  |
|  METRIC PROFILE       UTHUKULI GHEE                     RASIPURAM GHEE                           |
|  ----------------------------------------------------------------------------------------------  |
|  Product Image        [Image: Uthukuli Ghee]            [Image: Rasipuram Ghee]                  |
|  Aroma Type           Rich, intense, traditional        Mild, sweet, buttery                     |
|  Color & Texture      Deep golden, highly granular      Pale golden, fine-grained                |
|  Sourcing Region      Pastures in Coimbatore            Selected Namakkal cooperative farms      |
|  Primary Extraction   Butter clarification (churned)    Low-heat butter melting                  |
|  Purity Certification Verified (Batch: UT-2026)         Verified (Batch: RS-2026)                |
|  Pricing (500ml)      ₹599.00                           ₹549.00                                  |
|  Actions              [ ADD UTHUKULI TO CART ]          [ ADD RASIPURAM TO CART ]                |
+--------------------------------------------------------------------------------------------------+
```

---

## 4. Trust Center

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS TRUST PORTAL: "Selecting the Best to Serve the Best"                          |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   ENTER YOUR JAR BATCH CODE:                                                                     |
|   [ UT-2026       ]  [ VERIFY TRACEABILITY ]                                                     |
|   (Batch code is printed on the gold neck-seal of your glass jar)                                |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
|   QUALITY STANDARDS LEDGER:                                                                      |
|   +--------------------------+  +--------------------------+  +--------------------------+       |
|   | 1. Double Testing Audit  |  | 2. Facility Inspections  |  | 3. Dynamic GST Invoices  |       |
|   | Co-packer tests +        |  | Surprise audits mapped   |  | Complete tax breakdowns  |       |
|   | independent lab testing. |  | in our partner register. |  | for absolute integrity.  |       |
|   +--------------------------+  +--------------------------+  +--------------------------+       |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
|   ACTIVE LAB REPORT DIRECTORY:                                                                   |
|   - Batch UT-2026 (Uthukuli Ghee)   - Verified 06/01/2026 - [ Download PDF ]                     |
|   - Batch RS-2026 (Rasipuram Ghee) - Verified 05/28/2026 - [ Download PDF ]                     |
|   - Batch CO-2026 (Coconut Oil)     - Quarantined         - [ Locked ]                           |
+--------------------------------------------------------------------------------------------------+
```

---

## 5. Batch Lookup Results Page

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  TRACEABILITY LOG FOR BATCH: UT-2026                                                             |
+--------------------------------------------------------------------------------------------------+
|  STATUS: [ Purity Passed ] (Released for sale: 06/02/2026)                                       |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   BATCH TIMELINE:                                                                                |
|   [ Curd Churned ] ────► [ Lab Checked ] ────► [ Glass Jarred ] ────► [ Sent to WH ]             |
|   05/28/2026             06/01/2026            06/02/2026             06/04/2026                 |
|   Coimbatore farm        NABL Lab Certified    Nitrogen Flushed       Chennai Warehouse          |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
|   CO-PACKER CERTIFICATION PROFILE:                                                               |
|   - Facility Name: Coimbatore Dairy Curation Partners                                            |
|   - FSSAI License: #12345678901234                                                               |
|   - Last Audit Score: 96/100                                                                     |
|                                                                                                  |
|   VERIFIED TEST READOUTS:                                                                        |
|   - Moisture: 0.12% (Standard: <0.3%)  │  - Free Fatty Acids: 0.08% (Standard: <0.2%)            |
|   - Adulteration: 0.00% (Not detected) │  - A2 Beta-Casein: Positive (100% Gir/pasture cow)        |
+--------------------------------------------------------------------------------------------------+
```

---

## 6. Blog & Recipes Hub

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  WELLNESS, TRADITION & NUTRITION BLOG                                                            |
+--------------------------------------------------------------------------------------------------+
|  CATEGORIES: [ All ]  [ Recipes ]  [ Ayurvedic Science ]  [ Partner Spotlights ]                 |
+--------------------------------------------------------------------------------------------------+
|   FEATURED ARTICLE:                                                                              |
|   +--------------------------------------------------------+  +------------------------------+   |
|   | [Image: Sweet Mysore Pak]                              |  | SHOP THE INGREDIENTS         |   |
|   | Why Uthukuli Ghee is the Secret to Mysore Pak           |  |                              |   |
|   | By Chef Sundaram - 06/03/2026                          |  | [Image] Uthukuli Ghee        |   |
|   |                                                        |  | 500ml - ₹599                 |   |
|   | Authentic sweet-making requires high-smoke point ghee  |  | [ ADD TO CART ]              |   |
|   | that maintains a granular mouthfeel. Chef Sundaram     |  |                              |   |
|   | reviews why grazing cows in Tiruppur yield the best...  |  | [Image] Coconut Oil          |   |
|   | [ Read Full Recipe ]                                   |  | 500ml - ₹299                 |   |
|   +--------------------------------------------------------+  +------------------------------+   |
+--------------------------------------------------------------------------------------------------+
```

---

## 7. Cart Drawer (Slide-Over)

### Desktop Overlay
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|                                                                     ||  YOUR CART            [X] |
|                                                                     ||  (2 items)                |
|                                                                     ||  +----------------------+ |
|                                                                     ||  | [Img] Uthukuli Ghee  | |
|                                                                     ||  | 500ml - ₹599         | |
|                                                                     ||  | Qty: [ - ] [ 1 ] [ + ]| |
|                                                                     ||  +----------------------+ |
|                                                                     ||  | [Img] Rasipuram Ghee | |
|                                                                     ||  | 500ml - ₹549         | |
|                                                                     ||  | Qty: [ - ] [ 1 ] [ + ]| |
|                                                                     ||  +----------------------+ |
|                                                                     ||  FREE SHIPPING PROGRESS | |
|                                                                     ||  [=================== ] |
|                                                                     ||  Add ₹52 more for free! | |
|                                                                     ||  +----------------------+ |
|                                                                     ||  Subtotal:       ₹1,148 | |
|                                                                     ||  (GST calc at checkout) | |
|                                                                     ||  [ PROCEED TO CHECKOUT] | |
+--------------------------------------------------------------------------------------------------+
```

---

## 8. Checkout Wizard (Desktop)

### Step 1: Delivery Address
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS  -  SECURE CHECKOUT                                    (No Header links)      |
+--------------------------------------------------------------------------------------------------+
|  STEP PROGRESS: [1. Delivery] ───► [2. Verification] ───► [3. Payment]                           |
+--------------------------------------------------------------------------------------------------+
|  SHIPPING DETAILS                             │  ORDER SUMMARY                                   |
|                                               │  - Uthukuli Ghee x1:    ₹599.00                  |
|  Full Name:                                   │  - Rasipuram Ghee x1:   ₹549.00                  |
|  [_______________________________]            │  - Shipping Fee:        ₹40.00                   |
|  Pincode (Serves check triggers):             │  - IGST Total (12%):    ₹137.76                  |
|  [600001    ] [Check] -> Serviced (Chennai)   │  --------------------------------                |
|  Street Address:                              │  TOTAL DUE:             ₹1,325.76                |
|  [_______________________________]            │                                                  |
|  Mobile Phone (OTP required next):            │  [ ] I want a corporate tax GSTIN invoice        |
|  [_______________________________]            │  GSTIN: [__________________]                     |
|                                               │                                                  |
|  [ CONTINUE TO VERIFICATION ]                 │  Promo Coupon: [_________] [Apply]               |
+--------------------------------------------------------------------------------------------------+
```

---

## 8a. Mobile Checkout Layout [NEW]

Optimized for mobile interfaces, focusing on speed and single-column stacked structures.

```
+-----------------------------------+
|  MR. BHARATH FOODS - CHECKOUT    |
+-----------------------------------+
|  STEP 1 of 3: DELIVERY ADDRESS    |
+-----------------------------------+
|  Full Name:                       |
|  [______________________________] |
|                                   |
|  Pincode (Serviced check):        |
|  [600020   ]  [✓ Checked] Adyar   |
|                                   |
|  Shipping Address:                |
|  [______________________________] |
|                                   |
|  Phone Number (for OTP):          |
|  [______________________________] |
+-----------------------------------+
|  ORDER SUMMARY: (2 items)         |
|  Total Price:  ₹1,148.00          |
|  Tax & Ship:   ₹177.76            |
+-----------------------------------+
|  [ CONTINUE TO VERIFICATION (OTP) ]| <- Bottom Sticky Action Target
+-----------------------------------+
```

---

## 9. Order Success Page

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  ORDER COMPLETED SUCCESSFULLY!                                                                   |
|  Thank you, Gowtham. Your order is registered.                                                   |
+--------------------------------------------------------------------------------------------------+
|  Order ID: #MBF-92842                                                                            |
|  Payment Status: Paid (Razorpay UPI: verify_ref_9921)                                            |
|  Delivery Target: Estimated by Thursday, June 11, 2026                                           |
+--------------------------------------------------------------------------------------------------+
|  VERIFIED BATCH ASSIGNMENT:                                                                      |
|  Your jar is packed from Batch: UT-2026 (Uthukuli A2 Cow Ghee).                                  |
|  [ DOWNLOAD LAB CERTIFICATE PDF ]   [ VIEW BATCH SOURCING INFORMATION ]                          |
+--------------------------------------------------------------------------------------------------+
|  RETENTION BENEFITS EARNED:                                                                      |
|  - You earned 114 "Bharath Points" on this order.                                                |
|  - Account created successfully! Link to dashboard sent to your phone.                           |
|  [ GO TO MY ACCOUNT PORTAL ]                                                                     |
+--------------------------------------------------------------------------------------------------+
```

---

## 10. Order Tracking Page

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  ORDER TRACKING: #MBF-92842                                                                      |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   DELIVERY TIMELINE STATUS (Carrier: Shiprocket Express)                                         |
|                                                                                                  |
|   (x) Order Placed   ──► (x) Quality Packed  ──► (x) Shipped  ──► ( ) Out for Delivery  ──► ( ) Delivered |
|   06/06 10:30am          06/07 09:00am           06/07 04:00pm    Pending                   Pending      |
|   WH Chennai             Batch: UT-2026          Transit Hub      Chennai Center            Home Delivery|
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
|   TRACKING SPECIFICATION SUMMARY:                                                                |
|   - Shipping Destination: Gowtham, Adyar, Chennai - 600020                                       |
|   - Shiprocket AWB: #99281274                                                                    |
|   [ Need help with your delivery? MESSAGE SUPPORT ON WHATSAPP ]                                  |
+--------------------------------------------------------------------------------------------------+
```

---

## 11. Account Dashboard

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  CUSTOMER PORTAL: Welcome back, Gowtham                                                          |
+--------------------------------------------------------------------------------------------------+
|  DASHBOARD LINKS    │  OVERVIEW SUMMARY                                                          |
|                     │                                                                            |
|  [x] Dashboard      │  Active Staple Subscriptions: (1 Active)                                   |
|  [ ] Orders         │  - Uthukuli Ghee 500ml (Qty 1) - Next delivery: 07/06/2026 - [ Manage ]    |
|  [ ] Subscriptions  │                                                                            |
|  [ ] Addresses      │  Loyalty Ledger:                                                           |
|  [ ] Loyalty Ledger │  - Balance: 420 Bharath Points - Level: Gold Tier                         |
|  [ ] Logout         │                                                                            |
|                     │  +----------------------------------------------------------------------+  |
|                     │  | RECENTLY VIEWED PRODUCTS (Repeat purchase shortcuts)                 |  |
|                     │  | +----------------------+  +----------------------+  +--------------+ |  |
|                     │  | | [Img] Uthukuli Ghee  |  | [Img] Rasipuram Ghee |  | [Img] Sesame | |  |
|                     │  | | ₹599.00 - In Stock   |  | ₹549.00 - In Stock   |  | Coming Soon  | |  |
|                     │  | | [ ADD TO CART ]      |  | [ ADD TO CART ]      |  | [ NOTIFY ]   | |  |
|                     │  | +----------------------+  +----------------------+  +--------------+ |  |
|                     │  +----------------------------------------------------------------------+  |
+--------------------------------------------------------------------------------------------------+
```

---

## 11a. Subscription Manager Portal [NEW]

Allows subscribers to manage their recurring kitchen deliveries.

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  MANAGE STAPLE SUBSCRIPTIONS                                                                     |
+--------------------------------------------------------------------------------------------------+
|  ACTIVE CONTRACT: SUB-889124                                                                     |
|  Product: Uthukuli A2 Cow Ghee (500ml) | Qty: 1 | Frequency: Every 30 Days                        |
|  Price: ₹539.10 (Subscription discount applied)                                                  |
|                                                                                                  |
|  NEXT SHIPMENT TARGET:                                                                           |
|  [ Thursday, July 06, 2026 ]                                                                     |
|                                                                                                  |
|  ACTIONS PORTAL:                                                                                 |
|  [ SKIP NEXT SHIPMENT ]   [ PAUSE DELIVERY ]   [ SWAP PRODUCT ]   [ CHANGE NEXT BILL DATE ]      |
|                                                                                                  |
|  ----------------------------------------------------------------------------------------------  |
|  [ CANCEL SUBSCRIPTION CONTRACT ] (No penalties, reactivation allowed anytime)                   |
+--------------------------------------------------------------------------------------------------+
```

---

## 12. Wishlist Page

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS     [Shop Ghee]  [Shop Oils]  [Sourcing Story]  [Trust Center]    [ Q ] [A] [C]   |
+--------------------------------------------------------------------------------------------------+
|  YOUR WISHLIST (3 items saved)                                                                   |
+--------------------------------------------------------------------------------------------------+
|  +------------------------+  +------------------------+  +------------------------+              |
|  | [Image: Uthukuli Ghee] |  | [Image: Coconut Oil]   |  | [Image: Wild Honey]    |              |
|  | UTHUKULI GHEE          |  | COCONUT OIL            |  | WILD RAW HONEY         |              |
|  | 500ml - ₹599           |  | 500ml - ₹299           |  | 250g - ₹399            |              |
|  | Status: In Stock       |  | Status: Out of Stock   |  | Status: Low Stock (3)  |              |
|  |                        |  |                        |  |                        |              |
|  | [ ADD TO CART ]        |  | [ NOTIFY ON R2 STOCK ] |  | [ ADD TO CART ]        |              |
|  | [ Remove from list ]   |  | [ Remove from list ]   |  | [ Remove from list ]   |              |
|  +------------------------+  +------------------------+  +------------------------+              |
+--------------------------------------------------------------------------------------------------+
```

---

## 12a. Empty States Directory [NEW]

Designed to provide clear feedback and next steps when listing pages return no results.

### Empty Cart State
```
+-----------------------------------------------------------------+
|                                                                 |
|                      [ Shopping Cart Icon ]                     |
|                        Your Cart is Empty                       |
|        You haven't added any premium kitchen staples yet.       |
|                                                                 |
|                      [ CONTINUE SHOPPING ]                      |
|                                                                 |
+-----------------------------------------------------------------+
```

### Empty Wishlist State
```
+-----------------------------------------------------------------+
|                                                                 |
|                          [ Heart Icon ]                         |
|                     No Saved Items Found                        |
|       Tap the heart icon on any product page to save here.      |
|                                                                 |
|                     [ BROWSE GHEE CATALOG ]                     |
|                                                                 |
+-----------------------------------------------------------------+
```

### No Orders History State
```
+-----------------------------------------------------------------+
|                                                                 |
|                         [ Receipt Icon ]                        |
|                        No Orders Logged                         |
|           You haven't placed any orders with us yet.            |
|                                                                 |
|                     [ DISCOVER OUR PRODUCTS ]                   |
|                                                                 |
+-----------------------------------------------------------------+
```

### No Search Results State
```
+-----------------------------------------------------------------+
|                                                                 |
|                         [ Magnifier Icon ]                      |
|                       No Search Results Found                   |
|           We couldn't find matches for keyword "Rice".          |
|                                                                 |
|         Try searching for: [ Ghee ] [ Oils ] [ Spices ]         |
|                                                                 |
+-----------------------------------------------------------------+
```

---

## 13. B2B Portal (Retailers & Wholesalers)

### Desktop B2B Account Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS  -  B2B WHOLESALE ENGINE                                       [GST Checked]  |
+--------------------------------------------------------------------------------------------------+
|  GSTIN Verification: 33AAAAA0000A1Z (Active) │ Trade Credit Balance: ₹45,000 / Tier: Silver      |
+--------------------------------------------------------------------------------------------------+
|  BULK ORDER ENTRY SHEET (Wholesale case quantities)                                              |
|                                                                                                  |
|  PRODUCT SKU           CASE QTY (12 jars/case)    UNIT PRICE   TOTAL PRICE   STOCK STATUS        |
|  1. Uthukuli Ghee 500ml  [ 5  ] cases (60 jars)      ₹479.20      ₹28,752     In Stock (WH Chennai)
|  2. Rasipuram Ghee 500ml [ 0  ] cases                ₹439.20      ₹0          In Stock            |
|  3. Sesame Oil 1L        [ 10 ] cases (120 jars)     ₹239.20      ₹28,720     Low Stock           |
|                                                                                                  |
|  ------------------------------------------------------------------------------                  |
|  SUBTOTAL ORDER TOTAL:                                            ₹57,472                        |
|  B2B Trade Credit Check: Approved (Order fits limit)                                             |
|  Estimated Delivery: Pallet freight delivery (3-5 days)                                          |
|                                                                                                  |
|  [ SUBMIT WHOLESALE PALLET ORDER ]                                                               |
+--------------------------------------------------------------------------------------------------+
```

---

## 14. Admin Dashboard (CMS & PIM)

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS ADMIN  -  STORE CONSOLE                                       [Role: Admin]   |
+--------------------------------------------------------------------------------------------------+
|  MODULES: [Dashboard]  [x] [PIM Catalog]  [Batches]  [Orders]  [Customer CRM]  [CMS Page builder]    |
+--------------------------------------------------------------------------------------------------+
|  PIM CATALOG MANAGER                                                [ + ADD NEW FOOD PRODUCT ]   |
|  +--------------------------------------------------------------------------------------------+  |
|  | SEARCH: [ Uthukuli      ]  Category: [ Ghee   v ]  Soft-Deleted: [ Hide Deleted v ]        |  |
|  +--------------------------------------------------------------------------------------------+  |
|                                                                                                  |
|  PRODUCT NAME    CATEGORY  VARIANTS  BASE PRICE  ACTIVE BATCH   STATUS       ACTIONS             |
|  Uthukuli Ghee   Ghee      3 sizes   ₹599.00     UT-2026        Active       [ Edit ] [ Delete ] |
|  Rasipuram Ghee  Ghee      3 sizes   ₹549.00     RS-2026        Active       [ Edit ] [ Delete ] |
|  Coconut Oil     Oils      2 sizes   ₹299.00     CO-2026        Quarantine   [ Edit ] [ Delete ] |
|                                                                                                  |
|  Pagination: [First] [Prev]  Page: [ 1 ] of 3  [Next] [Last]                 Rows per page: [10 v]
+--------------------------------------------------------------------------------------------------+
```

---

## 15. Warehouse Dashboard

### Desktop Layout
```
+--------------------------------------------------------------------------------------------------+
|  MR. BHARATH FOODS LOGISTICS  -  FULFILLMENT CENTER                              [WH: Chennai]   |
+--------------------------------------------------------------------------------------------------+
|  QUEUES: [x] [Pick & Pack (14)]  [Incoming Batches (2)]  [Expiry Warnings (0)]  [Returns (1)]     |
+--------------------------------------------------------------------------------------------------+
|  PICK & PACK WORK QUEUE (FIFO Batch Allocations)                                                 |
|                                                                                                  |
|  ORDER ID   DATE   ITEMS ORDERED          TARGET BATCH   WH LOCATION  PACK STATUS                |
|  #92842     06/06  Uthukuli Ghee 500ml    UT-2026        Zone A-R3    [x] Packed  [ Generate AWB]
|  #92843     06/06  Rasipuram Ghee 500ml   RS-2026        Zone A-R4    [ ] Pending [ Pack Item ]   |
|  #92844     06/06  Sesame Oil 1L          SO-2026        Zone B-R1    [ ] Pending [ Pack Item ]   |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
|  INCOMING INVENTORY REGISTRY (Quarantine Intake logs)                                            |
|  - Register incoming delivery pallet:                                                            |
|    SKU: [ Uthukuli Ghee 500ml v ]  Batch Code: [________]  Expiry Date: [__/__/____]  [ Log Intake ]
+--------------------------------------------------------------------------------------------------+
```

# Brand Design System

## Project: MR. BHARATH FOODS
**Document Version:** 1.1.0  
**Author:** Senior Brand Strategist & Design System Architect  
**Date:** June 6, 2026  
**Status:** Approved / Release candidate  

---

### Executive Summary

This Brand Design System establishes the visual identity, UI guidelines, and digital components for **MR. BHARATH FOODS**. 

To position the company as a premium, corporate Indian food brand ("Selecting the Best to Serve the Best"), we reject typical D2C tropes such as loud primary colors, cartoon mascots, rustic/village-style illustrations, and cluttered layouts. Instead, this system adopts a **modern, sophisticated corporate aesthetic with a subtle Indian soul**—blending editorial typography, structured grids, deep heritage-inspired colors, and generous whitespace.

---

## 1. Brand Personality

The personality of MR. BHARATH FOODS is built on three core pillars:

* **The Curating Authority**: Expert, discerning, selective, and uncompromising on standards. We are not a simple manufacturer; we are taste-makers and quality certifiers.
* **Modern Heritage**: Proud of Indian origins but looking forward. We honor traditional food extraction methods (like Ghee and cold-pressed oils) using contemporary science and corporate efficiency.
* **Corporate Elite**: Clean, structured, highly professional, responsible, and secure. The brand feels closer to a high-end luxury wellness house or premium estate brand than a local provision store.

---

## 2. Brand Tone and Voice

The brand speaks with **dignity, transparency, and clinical precision**, balanced by culinary appreciation.

* **Expert but Accessible**: We explain the science of purity (e.g., A2 protein structure, moisture level in honey) without using overly academic jargon.
* **Understated Elegance**: We do not use hyperbole like "100% BEST GHEE IN INDIA!" Instead, we state facts: *"Sourced from grazing cows in Uthukuli; laboratory-certified purity."*
* **Transparent & Responsible**: Honest admissions of our partner model. We talk about our partners with respect, treating them as co-creators of quality.

---

## 3. Color System

The color palette is inspired by high-end Indian raw ingredients, metals, and landscapes, calibrated for digital screens (accessibility AAA compliance).

```
   [ Indian Ink ]       [ Warm Ivory ]       [ Kashmir Saffron ]    [ Deodhar Forest ]     [ Trust Navy ]     [ Burnished Gold ]
      #1C2321              #FAF9F6              #9E4624              #1E352F              #18324B               #C49A45
   Primary / Dark      Background Base      Accent / Secondary    Accent / Secondary    Corporate / Trust        Highlights
```

---

## 4. Primary Colors

Primary colors establish the dominant theme, providing grounding structure and canvas space.

* **Indian Ink** (`#1C2321`): A very deep, sophisticated slate-black. Used for primary text, structured headers, and deep backgrounds in dark mode.
* **Warm Ivory** (`#FAF9F6`): A clean, soft off-white. Replaces stark `#FFFFFF` to provide warmth and an organic feel without looking aged.
* **Pure Slate White** (`#FFFFFF`): Reserved exclusively for card backgrounds and input containers to stand out from the Warm Ivory base.

---

## 5. Secondary & Trust Colors

Secondary colors represent the richness of Indian agriculture, forests, and professional security.

* **Deodhar Forest Green** (`#1E352F`): A deep, professional pine green representing purity, nature, and raw ingredient quality.
* **Kashmir Saffron** (`#9E4624`): A muted, rich terracotta/rust saffron. Refuses the bright, neon oranges of standard brands in favor of a deeper, sophisticated earth tone.
* **Trust Navy** (`#18324B`): A deep, premium corporate navy blue. Used for order success pages, customer/partner dashboards, corporate trust badges, authentication modules, and B2B portal sections to convey stability and enterprise-level responsibility.

---

## 6. Accent Colors

Used sparingly (less than 5% of visual area) to guide the user's eye, emphasize interactive states, and highlight key selections.

* **Burnished Gold** (`#C49A45`): A metallic, warm bronze-gold. Used for quality seals, selection badges, and active interactive borders.
* **Muted Sage** (`#E2EAE5`): A soft, desaturated green used for background highlights, success states, and search indicators.
* **Terracotta Blush** (`#F7EFE9`): A warm, soft tint of saffron used for card backdrops and warnings.

---

## 6a. Status Colors (System & Admin UI)

Designed primarily for administrative workflows, transactional messaging, dashboards, and system-level user feedback to ensure instant functional utility.

* **Success** (`#2E7D32`): A professional dark emerald green. Used for completed payments, active subscriptions, batch QA approval states, and order deliveries.
* **Warning** (`#C49A45`): A burnished gold. Used for pending facility audits, low-stock warnings, and draft orders.
* **Error** (`#C62828`): An authoritative crimson red. Used for failed transactions, expired batch flags, cancelled orders, and critical validation warnings.
* **Info** (`#1565C0`): A clean, informational blue. Used for shipping transit updates, system tooltips, and non-blocking announcements.

---

## 7. Typography System

The typography system pairs an elegant heritage serif for editorial storytelling with a clean, highly legible geometric sans-serif for interface elements.

* **Editorial / Heading Font**: **Cormorant Garamond** (Google Fonts). An elegant, high-contrast serif typeface.
* **Interface / Body Font**: **Outfit** or **Plus Jakarta Sans** (Google Fonts). A modern geometric sans-serif with clean proportions, optimized for small screen readability.

---

## 8. Heading Styles

All headings use **Cormorant Garamond**, styled with semi-bold or regular weights to maintain an editorial, magazine-like feel.

* **Display 1 (Hero)**: `48px` / Line Height: `1.15` / Tracking: `-0.02em` / Regular (Mobile: `36px`)
* **Heading 1**: `36px` / Line Height: `1.2` / Tracking: `-0.01em` / Semi-Bold (Mobile: `28px`)
* **Heading 2**: `28px` / Line Height: `1.25` / Tracking: `0` / Semi-Bold (Mobile: `22px`)
* **Heading 3**: `20px` / Line Height: `1.3` / Tracking: `0` / Semi-Bold (Mobile: `18px`)

---

## 9. Body Text Styles

All body text and interactive labels use **Outfit** to ensure UI clarity, legibility, and modern corporate structure.

* **Body Large (Intro text)**: `18px` / Line Height: `1.6` / Weight: `Light (300)`
* **Body Regular (Paragraphs)**: `16px` / Line Height: `1.5` / Weight: `Regular (400)`
* **Body Small (Muted copy, metadata)**: `14px` / Line Height: `1.4` / Weight: `Regular (400)` / Color: Muted Indian Ink (60% opacity)
* **Button/Label Text**: `14px` / Line Height: `1.0` / Weight: `Medium (500)` / Case: Uppercase / Tracking: `0.08em`

---

## 10. Spacing System

The spacing system uses an **8px base grid** to ensure consistency across responsive break-points.

* **4px (xxs)**: Micro adjustments (badge padding, icon-text gap).
* **8px (xs)**: Small gaps (input-label gap, review stars).
* **16px (sm)**: Standard padding (within cards, small buttons).
* **24px (md)**: Grid gap, product grid layouts, standard layout gaps.
* **48px (lg)**: Section padding, hero spacing.
* **72px (xl)**: Large editorial separations.

---

## 11. Border Radius System

To project professional structure, we avoid hyper-rounded corners (which feel juvenile) and razor-sharp corners (which feel hostile).

* **0px (Sharp)**: Reserved for premium outer packaging grids or editorial full-width hero sections.
* **4px (Small)**: Buttons, inputs, tags, and small badges.
* **8px (Medium)**: Product cards, category panels, cart overlays.
* **16px (Large)**: Main display banners, promotional cards.

---

## 12. Shadow System

Shadows are soft, diffuse, and rare—reflecting natural studio lighting. We avoid heavy, dark shadows.

* **Elevation 1 (Low)**: `0 2px 8px rgba(28, 35, 33, 0.04)`. Used for buttons and hover card offsets.
* **Elevation 2 (Medium)**: `0 4px 16px rgba(28, 35, 33, 0.06)`. Used for dropdown menus, search modals, and small dialog boxes.
* **Elevation 3 (High)**: `0 12px 32px rgba(28, 35, 33, 0.1)`. Used for cart slides and major modal screens.

---

## 13. Button Design Language

Buttons must feature clear visual hierarchy, combining bold background colors with spacious padding.

```
┌─────────────────────────────────┐
│           ADD TO CART           │  <- Primary Button (Solid Indian Ink #1C2321, White Text)
└─────────────────────────────────┘
┌─────────────────────────────────┐
│        VIEW CERTIFICATE         │  <- Secondary Button (Outlined #1C2321, transparent base)
└─────────────────────────────────┘
```

* **States**:
  - **Hover**: Background shifts slightly (e.g., solid changes opacity to 90%, outlined gets subtle tint).
  - **Active/Click**: 2px inner border overlay or slight scale contraction (98%).
  - **Disabled**: Slate grey fills with white text (40% opacity).

---

## 14. Input Components

Input fields are minimalist, utilizing clear borders and modern typography.

```
  Product Category
  ┌───────────────────────────────────┐
  │ Ghee                              │
  └───────────────────────────────────┘
```
* **Normal**: 1px border using `rgba(28, 35, 33, 0.2)` over a pure white background.
* **Focus**: 1px border using **Burnished Gold** (`#C49A45`) with a subtle 2px glow. Label shifts up slightly.
* **Error**: 1px border using `#D9383A`. Inline error text appears in 12px below the input.

---

## 14a. Form Wizard Design (Stepper & Progress)

For multi-stage checkouts, B2B quote requests, and multi-step admin configurations, wizards must ensure a structured, step-by-step progress flow.

### Stepper Component
* **Layout**: Horizontal on desktop; folds to a simplified step counter (e.g., "Step 2 of 4") on mobile.
* **Completed Step**: Icon circle containing a gold checkmark (`✓`) with a thin border using `Trust Navy` (`#18324B`).
* **Active Step**: Filled circle in `Trust Navy` with the step number in white. Bold label below in `Outfit`.
* **Inactive Step**: Outline circle in light grey (`rgba(28, 35, 33, 0.15)`) with a muted label.
* **Connector Lines**: Horizontal line connecting steps is `1px solid rgba(28, 35, 33, 0.1)`, transitioning to solid `Trust Navy` once the subsequent step is unlocked.

### Progress Bar
* **Empty track**: 4px height, background color set to Muted Sage (`#E2EAE5`), border-radius `2px`.
* **Fill track**: Dynamically fills with `Trust Navy` (`#18324B`) using a smooth ease-in-out transition (`400ms`).

### Validation Style
* **Real-time inline validation**: Trigger validation feedback on field blur. Correct fields display a micro green check icon inside the right edge of the input.
* **Error feedback**: Invalid inputs highlight with a `1.5px solid #C62828` border. Error text appears below the field in `12px Outfit` regular, colored in error crimson. The form layout remains static to prevent visual shifts (CLS).

---

## 15. Card Components

Cards group information cleanly, using subtle containers instead of thick borders.

* **Layout**: No heavy background gradients. Use white backgrounds against the Warm Ivory page base.
* **Borders**: 1px border of `rgba(28, 35, 33, 0.06)` or a clean soft shadow.
* **Hover State**: Cards translate upwards by `4px` and gain a soft Elevation 2 shadow.

---

## 15a. Table Design System (Data & Admin UI)

Tables are critical for administration dashboards (orders, inventory levels, user directories, and batch review logs). They must remain flat, structured, and legible under high data density.

```
  ┌────────────────────────────────────────────────────────────┐
  │ BATCH ID     MANUFACTURER   STATUS         TRACE CODE      │  <- Sticky Header
  ├────────────────────────────────────────────────────────────┤
  │ #GHEE-092    Rasipuram Co  [ Success ]     R-2026-A        │  <- Odd Row (White)
  ├────────────────────────────────────────────────────────────┤
  │ #GHEE-093    Uthukuli Ltd  [ Warning ]     U-2026-B        │  <- Even Zebra Row (Tint)
  └────────────────────────────────────────────────────────────┘
```

* **Structure**: Flat table layout. No vertical grid lines. Horizontal grid lines use a thin `1px solid rgba(28, 35, 33, 0.06)` separator.
* **Zebra Rows**: Alternating rows use a very soft Warm Ivory base (`rgba(28, 35, 33, 0.015)`) on even rows, keeping odd rows pure white.
* **Hover State**: Hovering over a row changes the background color to a subtle warm sand tint (`#F2ECE4` at 40% opacity) and changes the cursor to a pointer for row-level click navigation.
* **Sticky Header**: Headers use a dark backdrop (solid `Indian Ink #1C2321` with white text for high contrast, or a subtle warm grey `#F2ECE4` with bold dark text), locked to the top layout viewport (`position: sticky`) with an Elevation 1 shadow appearing on scroll.
* **Pagination Style**:
  - Outlined arrows (left/right) with `8px` spacing.
  - Active page number highlighted using a solid `Trust Navy` border indicator.
  - Right-aligned "Rows per page" selector (10, 25, 50, 100) using a minimal dropdown input field.

---

## 16. Product Card Design

The product card is a key design element, emphasizing ingredient purity and clear hierarchy.

```
  ┌─────────────────────────────────┐
  │                                 │
  │        [ Studio Photo ]         │
  │     (Clear Jar, White BG)       │
  │                                 │
  ├─────────────────────────────────┤
  │ UTHUKULI GHEE          [ ★ 4.9] │
  │ Batch Trace: UT-2026            │
  │                                 │
  │ 500ml                 ₹599.00   │
  │                                 │
  │ ┌─────────────────────────────┐ │
  │ │         ADD TO CART         │ │
  │ └─────────────────────────────┘ │
  └─────────────────────────────────┘
```

* **Aspect Ratio**: 1:1 square ratio for product image containers to keep alignment clean.
* **Content Stack**:
  1. Product category in small uppercase (Outfit, 12px, muted).
  2. Product Title (Cormorant Garamond, 20px, Indian Ink).
  3. Star rating (Outfit, 12px, inline with title).
  4. Active Batch trace code (Outfit, 11px, green badge or text).
  5. Price and volume variant (Outfit, 14px, bold).
  6. Action button (fits inside card borders).

---

## 17. Badge Styles

Badges are used to highlight certifications, inventory status, and batch quality.

* **Selection Seal**: A gold border enclosing text: "CURATED SELECTION".
* **Purity Verified Badge**: A small, muted sage capsule with a green checkmark icon: "✓ Pure A2 Lab Certified".
* **Stock Badge**: Muted colors (e.g., "Only 10 jars remaining" in Kashmir Saffron text).

---

## 18. Icon System

* **Style**: Thin line icons (2px stroke weight), geometric, non-filled (unless active).
* **Library Recommendation**: **Lucide Icons** or custom SVGs matching the clean geometric lines of the Outfit typeface.
* **Color**: Matches the surrounding text layer (usually Indian Ink).

---

## 19. Navigation Styles

Navigation emphasizes structure and ease of movement:

* **Desktop Header**: Solid white base or transparent shifting to solid white on scroll. Left-aligned logo, center-aligned menu categories (with premium hover dropdown lists), right-aligned utilities (Search, Profile, Cart count).
* **Dropdown Menus**: Features detailed category previews. Instead of text lists, include a small thumbnail of the product (e.g., a mini photo of the ghee jar next to the "Ghee" link).

---

## 20. Footer Design Language

The footer is highly corporate and informative, designed to build trust:

```
  ========================================================================
  MR. BHARATH FOODS           PRODUCTS         TRUST                   NEWSLETTER
  "Selecting the Best..."    - Ghee           - Quality Policy         [ Enter email ]
                             - Oils (Future)  - Sourcing Map
  FSSAI Lic. No: 12345       - Honey (Future) - Lab Reports
  ========================================================================
```

* **Color Background**: Solid **Deodhar Forest Green** (`#1E352F`) with **Warm Ivory** (`#FAF9F6`) text, or solid **Indian Ink** (`#1C2321`) with muted text.
* **Information Included**: Brand FSSAI registration numbers, partner manufacturer compliance statement, links to lab certificates, sitemap, payment partner logos, and legal policies.

---

## 21. Grid System

The platform uses a standard responsive grid layout:

* **Desktop (1440px+)**: 12-column grid / 24px gutter / 120px margins.
* **Tablet (768px - 1024px)**: 8-column grid / 16px gutter / 40px margins.
* **Mobile (320px - 480px)**: 4-column grid / 12px gutter / 16px margins.

---

## 22. White Space Rules

Whitespace is treated as an active design element, not as "empty space."

* **Section Buffers**: Maintain a minimum of `80px` vertical space between homepage sections on desktop.
* **Clean Text Layouts**: Product descriptions must have wide side margins, forcing a reading column width of 650px maximum to encourage focus.

---

## 23. Motion Guidelines

Animations must be smooth and natural, avoiding dramatic transitions.

* **Hover Transitions**: Standardize at `200ms cubic-bezier(0.4, 0, 0.2, 1)`.
* **Menu slide-ins**: Slide and fade from top or side at `300ms cubic-bezier(0.16, 1, 0.3, 1)` for a snappy response.
* **Interactive Elements**: Micro-interactions like stars lighting up or checkmarks drawing in must complete in under `150ms`.

---

## 24. Mobile Design Principles

* **Thumb Zone Layout**: Keep primary CTA buttons (like "Add to Cart" or "Buy Now") in the lower 40% of the screen.
* **Touch-Optimized Filters**: Slide-up filter panels with large tap targets instead of tiny desktop check-boxes.
* **No Page Clutter**: Limit column grids to 2-columns max on mobile for product grids, and 1-column for blogs and checkouts.

---

## 25. Dark Mode Strategy

While the brand is premium-light oriented (using Warm Ivory), Dark Mode must present a clean, night-time aesthetic.

* **Primary Background**: Shift from Warm Ivory to **Indian Ink** (`#1C2321`).
* **Card Fills**: Shift from Pure White to `#252D2B` (a slightly lighter slate variant).
* **Text**: Colors invert from Indian Ink to Warm Ivory.
* **Gold Highlights**: Muted to a slightly brighter Gold (`#E8C26C`) to ensure proper visual contrast against dark backdrops.

---

## 26. Illustration Style

* **No Clipart/Cartoons**: Absolutely no cartoon cows, generic jars, or retro vector art.
* **Geometric Heritage Patterns**: Symmetrical, thin line art patterns inspired by traditional Indian architectural lattices (Jali grids) and clean mandalas.
* **Technical Sourcing Diagrams**: Clean line illustrations showing step-by-step testing workflows (e.g., test tubes, temperature charts, extraction schemas).

---

## 27. Photography Guidelines

Photography is the primary visual driver of brand quality.

```
  ┌─────────────────────────────┐
  │                             │
  │       [ Studio Shot ]       │  <- Isolated, clean lighting, focus on purity.
  │                             │
  └─────────────────────────────┘
  ┌─────────────────────────────┐
  │                             │
  │      [ Heritage Shot ]      │  <- Muted, natural lighting, story-driven context.
  │                             │
  └─────────────────────────────┘
```

* **Studio Product Shots**: Set against neutral, warm grey, or beige backdrops. Symmetrical compositions with soft, diffused shadows. The glass jar must sparkle, highlighting the color and texture of the ghee/oil.
* **Heritage & Ingredient Lifestyle Shots**: Muted colors showing raw materials (e.g., fresh grass fields in Rasipuram, traditional clay pots). Show human hands with age and character, avoiding stock photography models.

---

## 28. Packaging Visual Consistency

The website design must echo the physical packaging design.

* **Minimalist Labels**: Glass jars with clean black and gold typography.
* **Purity Bands**: A signature gold band wrapped around the neck of the jar, matching the gold badges on the website.
* **Unified Fonts**: Physical packaging labels will use Cormorant Garamond and Outfit to maintain absolute brand alignment.

---

## 29. Brand Do's and Don'ts

### Do's
- **Do** showcase lab certificates on product detail pages.
- **Do** maintain generous whitespace and structured grids.
- **Do** use premium studio photography with authentic ingredients.
- **Do** write in a clear, transparent, and authoritative tone.

### Don'ts
- **Don't** use bright, saturated red/yellow promotional banners.
- **Don't** use cartoon cow vectors or rustic farm clip art.
- **Don't** clutter screens with popups, countdown timers, or spin-to-win discount wheels.
- **Don't** claim "The Best" without providing batch lab proof.
- **Don't** use generic stock photos of happy families or clinical labs.

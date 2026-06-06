import { env } from "@/lib/env";

export const siteConfig = {
  name: "Mr. Bharath Foods",
  tagline: "Selecting the Best to Serve the Best",
  description:
    "Expertly curated premium Indian foods. Sourced from heritage regions, laboratory-verified for absolute purity, and trace-certified by batch.",
  url: env.NEXT_PUBLIC_APP_URL,
  ogImage: `${env.NEXT_PUBLIC_APP_URL}/og-image.jpg`,
  fssaiLicenseNumber: "12424999000123", // Example compliance registration
  links: {
    supportEmail: "support@mrbharathfoods.in",
    partnerPortal: "/b2b",
  },
  nav: {
    main: [
      { title: "Home", href: "/" },
      { title: "Shop Catalog", href: "/shop" },
      { title: "Trust Center", href: "/trust" },
      { title: "Compare", href: "/compare" },
      { title: "Recipes & Blog", href: "/blog" },
    ],
    footer: [
      {
        title: "Products",
        items: [
          { title: "Uthukuli A2 Ghee", href: "/products/uthukuli-ghee" },
          { title: "Rasipuram Pure Ghee", href: "/products/rasipuram-ghee" },
          { title: "Cold Pressed Oils (Coming Soon)", href: "#" },
          { title: "Wild Honey (Coming Soon)", href: "#" },
        ],
      },
      {
        title: "Trust Portal",
        items: [
          { title: "Verify Batch Code", href: "/trust" },
          { title: "Sourcing Map", href: "/trust" },
          { title: "Lab Certifications", href: "/trust" },
        ],
      },
      {
        title: "Institutional",
        items: [
          { title: "B2B Procurement Portal", href: "/b2b" },
          { title: "Corporate Gifting Catalog", href: "/corporate-gifting" },
          { title: "Warehouse Dashboard", href: "/warehouse-dashboard" },
        ],
      },
    ],
  },
};

export type SiteConfig = typeof siteConfig;
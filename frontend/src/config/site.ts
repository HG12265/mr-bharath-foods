import { env } from "@/lib/env";

export const siteConfig = {
  name: "Mr. Bharath Foods",
  tagline: "Selecting the Best to Serve the Best",
  description:
    "Expertly curated premium Indian foods. Sourced from heritage regions, laboratory-verified for absolute purity, and trace-certified by batch.",
  url: env.NEXT_PUBLIC_APP_URL,
  ogImage: `${env.NEXT_PUBLIC_APP_URL}/og-image.jpg`,
  fssaiLicenseNumber: "12424999000123",
  twitterHandle: "@mrbharathfoods",
  keywords: [
    "pure ghee online india",
    "rasipuram ghee",
    "uthukuli a2 cow ghee",
    "traditional ghee",
    "premium indian ghee",
    "lab verified ghee",
    "fssai certified ghee",
    "buy ghee online",
    "Mr. Bharath Foods",
  ],
  links: {
    supportEmail: "mrbharathfoods@gmail.com",
    partnerPortal: "/b2b",
  },
  nav: {
    main: [
      { title: "Home", href: "/" },
      { title: "Shop", href: "/shop" },
      { title: "About", href: "/about" },
      { title: "Contact", href: "/contact" },
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
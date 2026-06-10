import { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";

/**
 * Robots.txt generator.
 * Allows all public-facing pages, disallows private/admin routes.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/admin/",
          "/account/",
          "/checkout/",
          "/order/",
          "/api/",
        ],
      },
      {
        // Block AI training crawlers
        userAgent: ["GPTBot", "ChatGPT-User", "Google-Extended", "CCBot"],
        disallow: "/",
      },
    ],
    sitemap: `${siteConfig.url}/sitemap.xml`,
  };
}

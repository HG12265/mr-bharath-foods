import { MetadataRoute } from "next";
import { env } from "@/lib/env";

/**
 * Robots.txt generator.
 * Allows all public-facing pages, disallows private/admin routes.
 */
export default function robots(): MetadataRoute.Robots {
  const appUrl = env.NEXT_PUBLIC_APP_URL;

  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: [
          "/admin",
          "/account",
          "/cart",
          "/checkout",
          "/login",
          "/register",
          "/order",
          "/api",
        ],
      },
      {
        // Block AI training crawlers
        userAgent: ["GPTBot", "ChatGPT-User", "Google-Extended", "CCBot"],
        disallow: "/",
      },
    ],
    sitemap: `${appUrl}/sitemap.xml`,
  };
}

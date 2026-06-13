import type { NextConfig } from "next";

const remotePatterns = [
  {
    protocol: "https" as const,
    hostname: "pub-media.mrbharathfoods.in",
  },
  {
    protocol: "https" as const,
    hostname: "pub-media.bharathdelightfoods.in",
  },
  {
    protocol: "https" as const,
    hostname: "res.cloudinary.com",
  },
];

const mediaBaseUrl = process.env.NEXT_PUBLIC_MEDIA_BASE_URL;
if (mediaBaseUrl) {
  try {
    const url = new URL(mediaBaseUrl);
    if (url.protocol === "https:" || url.protocol === "http:") {
      remotePatterns.push({
        protocol: "https" as const,
        hostname: url.hostname,
      });
    }
  } catch {
    remotePatterns.push({
      protocol: "https" as const,
      hostname: mediaBaseUrl,
    });
  }
}

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns,
  },
};

// eslint-disable-next-line @typescript-eslint/no-require-imports
const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

export default withBundleAnalyzer(nextConfig);

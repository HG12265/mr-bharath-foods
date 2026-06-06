import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    domains: ["pub-media.mrbharathfoods.in"], // Cloudflare R2 subdomain placeholder
  },
};

export default nextConfig;

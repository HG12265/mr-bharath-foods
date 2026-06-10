import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "pub-media.mrbharathfoods.in",
      },
    ],
  },
};

export default nextConfig;

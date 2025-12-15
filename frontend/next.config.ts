import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    // Set the root directory for Turbopack to the monorepo root
    // to correctly resolve packages in npm workspaces
    root: "..",
  },
  experimental: {
    serverActions: {
      bodySizeLimit: "5mb", // Allow CV uploads up to 5MB
    },
  },
};

export default nextConfig;

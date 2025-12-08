import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    // Set the root directory for Turbopack to the current project directory
    // to prevent it from incorrectly inferring the workspace root and watching too many files.
    root: process.cwd(),
  },
};

export default nextConfig;

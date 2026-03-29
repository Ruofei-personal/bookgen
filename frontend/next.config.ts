import type { NextConfig } from "next";

const apiBase =
  process.env.API_URL?.replace(/\/$/, "") ||
  process.env.BACKEND_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8001";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/content/:path*",
        destination: `${apiBase}/content/:path*`,
      },
    ];
  },
};

export default nextConfig;

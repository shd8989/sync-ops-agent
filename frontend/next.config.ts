// frontend/next.config.ts 예시
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*", // FastAPI 메인 진입점 연결
      },
    ];
  },
};

export default nextConfig;
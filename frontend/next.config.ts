import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',
  images: {
    remotePatterns: [
      {
        // MinIO no VPS via Cloudflare Tunnel
        protocol: 'https',
        hostname: 'minio.nutrisaas.com',
        pathname: '/**',
      },
    ],
  },
}

export default nextConfig

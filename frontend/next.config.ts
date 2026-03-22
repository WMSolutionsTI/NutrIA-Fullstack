import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',
  typescript: {
    ignoreBuildErrors: true,
  },
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

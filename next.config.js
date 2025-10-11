/**
 * Next.js Configuration File
 * 
 * This file contains the configuration for the Steam Game Search Engine Next.js application.
 * It includes settings for API routes, image optimization, and other Next.js features.
 * 
 * @see https://nextjs.org/docs/api-reference/next.config.js/introduction
 */

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode for better development experience
  reactStrictMode: true,
  
  // Enable SWC minification for better performance
  swcMinify: true,
  
  // Configure image domains for external images (Steam CDN, etc.)
  images: {
    domains: [
      'cdn.akamai.steamstatic.com',
      'steamcdn-a.akamaihd.net',
      'store.steampowered.com'
    ],
    // Enable image optimization
    unoptimized: false,
  },
  
  // API routes configuration for FastAPI backend
  async rewrites() {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

    return [
      // Main API routes
      {
        source: '/api/v1/:path*',
        destination: `${apiBaseUrl}/api/v1/:path*`,
      },
      // Health check endpoint
      {
        source: '/api/health',
        destination: `${apiBaseUrl}/api/v1/health`,
      },
      // Function library API (for future markdown parsing)
      {
        source: '/api/functions/:path*',
        destination: `${apiBaseUrl}/api/v1/functions/:path*`,
      },
    ];
  },
  
  // Environment variables that should be available on the client side
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // Experimental features (none currently needed for Next.js 14)
  experimental: {
    // Future experimental features can be added here
  },
  
  // Webpack configuration for custom module resolution
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Custom webpack configurations can be added here
    // For example, handling markdown files or other custom file types
    
    return config;
  },
  
  // Headers configuration for security and performance
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;

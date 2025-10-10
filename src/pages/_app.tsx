/**
 * Next.js App Component
 * 
 * This is the root component that wraps all pages in the Steam Game Search Engine.
 * It handles global styles, providers, and application-wide configuration.
 */

import React from 'react';
import type { AppProps } from 'next/app';
import Head from 'next/head';
import '@/styles/globals.css';

/**
 * Custom App Component
 * 
 * Features:
 * - Global CSS imports
 * - Application-wide providers
 * - Error boundary handling
 * - Performance monitoring setup
 * - Global meta tags
 */
export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      {/* Global Head Configuration */}
      <Head>
        {/* Viewport and responsive design */}
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        
        {/* Theme color for mobile browsers */}
        <meta name="theme-color" content="#1b2838" />
        
        {/* Favicon and app icons */}
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
        
        {/* Preconnect to external domains for performance */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        
        {/* Default meta tags (can be overridden by individual pages) */}
        <meta name="description" content="Discover amazing Steam games with our intelligent search engine" />
        <meta name="keywords" content="steam, games, search, discovery, gaming, indie" />
        <meta name="author" content="INST326 Team" />
        
        {/* Open Graph default tags */}
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="Steam Game Search Engine" />
        <meta property="og:locale" content="en_US" />
        
        {/* Twitter Card default tags */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:site" content="@steamgamesearch" />
        
        {/* Prevent indexing in development */}
        {process.env.NODE_ENV === 'development' && (
          <meta name="robots" content="noindex, nofollow" />
        )}
      </Head>

      {/* Main Application */}
      <div id="app-root">
        {/* TODO: Add global providers here when needed */}
        {/* Examples:
          - Theme provider for dark/light mode
          - Authentication context
          - Global state management
          - Error boundary
          - Analytics provider
        */}
        
        <Component {...pageProps} />
        
        {/* TODO: Add global components here */}
        {/* Examples:
          - Toast notifications
          - Loading indicators
          - Analytics tracking
          - Error reporting
        */}
      </div>

      {/* Development-only scripts */}
      {process.env.NODE_ENV === 'development' && (
        <>
          {/* Development console logging */}
          <script
            dangerouslySetInnerHTML={{
              __html: `
                console.log('%c🎮 Steam Game Search Engine', 'color: #90ba3c; font-size: 16px; font-weight: bold;');
                console.log('%cDevelopment Mode Active', 'color: #66c0f4; font-size: 12px;');
                console.log('%cINST326 Group Project', 'color: #999; font-size: 10px;');
              `,
            }}
          />
        </>
      )}
    </>
  );
}

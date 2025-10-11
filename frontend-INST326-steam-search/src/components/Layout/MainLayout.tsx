/**
 * Main Layout Component
 * 
 * This component provides the main layout structure for the Steam Game Search Engine.
 * It includes the header, navigation, main content area, and footer.
 * All pages will be wrapped with this layout to maintain consistency.
 */

import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';

interface MainLayoutProps {
  /** Page content to be rendered */
  children: React.ReactNode;
  /** Page title for SEO */
  title?: string;
  /** Page description for SEO */
  description?: string;
  /** Additional CSS classes for the main container */
  className?: string;
}

/**
 * Main Layout Component
 * 
 * Provides consistent layout structure across all pages including:
 * - SEO-optimized head section
 * - Steam-themed header with navigation
 * - Main content area
 * - Footer with links and information
 */
export default function MainLayout({
  children,
  title = 'Steam Game Search Engine',
  description = 'Discover amazing Steam games with intelligent search and filtering',
  className = '',
}: MainLayoutProps) {
  const router = useRouter();

  /**
   * Check if the current route is active
   */
  const isActiveRoute = (path: string): boolean => {
    return router.pathname === path;
  };

  return (
    <>
      {/* SEO and Meta Tags */}
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="keywords" content="steam, games, search, discovery, gaming" />
        <meta name="author" content="INST326 Team" />
        
        {/* Open Graph tags for social sharing */}
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:type" content="website" />
        <meta property="og:url" content={process.env.NEXT_PUBLIC_APP_URL} />
        
        {/* Twitter Card tags */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
        
        {/* Favicon */}
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
      </Head>

      <div className="min-h-screen bg-steam-blue-dark flex flex-col">
        {/* Header */}
        <header className="bg-steam-blue border-b border-steam-blue-light">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              {/* Logo and Brand */}
              <div className="flex items-center">
                <Link href="/" className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-steam-green rounded flex items-center justify-center">
                    <span className="text-white font-bold text-lg">S</span>
                  </div>
                  <span className="text-white font-bold text-xl">
                    Steam Search Engine
                  </span>
                </Link>
              </div>

              {/* Navigation */}
              <nav className="hidden md:flex space-x-8">
                <Link
                  href="/"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActiveRoute('/')
                      ? 'bg-steam-green text-white'
                      : 'text-gray-300 hover:text-white hover:bg-steam-blue-light'
                  }`}
                >
                  Home
                </Link>
                <Link
                  href="/search"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActiveRoute('/search')
                      ? 'bg-steam-green text-white'
                      : 'text-gray-300 hover:text-white hover:bg-steam-blue-light'
                  }`}
                >
                  Search
                </Link>
                <Link
                  href="/function-library"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActiveRoute('/function-library')
                      ? 'bg-steam-green text-white'
                      : 'text-gray-300 hover:text-white hover:bg-steam-blue-light'
                  }`}
                >
                  Function Library
                </Link>
                <Link
                  href="/api-status"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActiveRoute('/api-status')
                      ? 'bg-steam-green text-white'
                      : 'text-gray-300 hover:text-white hover:bg-steam-blue-light'
                  }`}
                >
                  API Status
                </Link>
                <Link
                  href="/about"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActiveRoute('/about')
                      ? 'bg-steam-green text-white'
                      : 'text-gray-300 hover:text-white hover:bg-steam-blue-light'
                  }`}
                >
                  About
                </Link>
              </nav>

              {/* Mobile menu button - TODO: Implement mobile menu */}
              <div className="md:hidden">
                <button
                  type="button"
                  className="text-gray-300 hover:text-white focus:outline-none focus:text-white"
                  aria-label="Open main menu"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className={`flex-1 ${className}`}>
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-steam-blue border-t border-steam-blue-light">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* About Section */}
              <div>
                <h3 className="text-white font-semibold mb-4">About</h3>
                <p className="text-gray-300 text-sm">
                  Steam Game Search Engine provides intelligent game discovery
                  using advanced search algorithms and semantic understanding.
                </p>
              </div>

              {/* Quick Links */}
              <div>
                <h3 className="text-white font-semibold mb-4">Quick Links</h3>
                <ul className="space-y-2">
                  <li>
                    <Link href="/search" className="text-gray-300 hover:text-white text-sm">
                      Advanced Search
                    </Link>
                  </li>
                  <li>
                    <Link href="/function-library" className="text-gray-300 hover:text-white text-sm">
                      Function Library
                    </Link>
                  </li>
                  <li>
                    <Link href="/about" className="text-gray-300 hover:text-white text-sm">
                      About Project
                    </Link>
                  </li>
                </ul>
              </div>

              {/* Technical Info */}
              <div>
                <h3 className="text-white font-semibold mb-4">Technical</h3>
                <ul className="space-y-2">
                  <li className="text-gray-300 text-sm">
                    Built with Next.js & TypeScript
                  </li>
                  <li className="text-gray-300 text-sm">
                    Powered by FastAPI Backend
                  </li>
                  <li className="text-gray-300 text-sm">
                    INST326 Group Project
                  </li>
                </ul>
              </div>
            </div>

            {/* Copyright */}
            <div className="mt-8 pt-8 border-t border-steam-blue-light">
              <p className="text-center text-gray-400 text-sm">
                © 2024 INST326 Team. This project is for educational purposes.
                Steam is a trademark of Valve Corporation.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}

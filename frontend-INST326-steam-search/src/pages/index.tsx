/**
 * Home Page Component
 * 
 * This is the main landing page for the Steam Game Search Engine.
 * It provides an overview of the application features and a prominent
 * search interface for users to begin discovering games.
 */

import React, { useState } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '@/components/Layout/MainLayout';
import SearchBox from '@/components/Search/SearchBox';

/**
 * Home Page Component
 * 
 * Features:
 * - Hero section with search functionality
 * - Feature highlights
 * - Quick start guide
 * - Recent/popular games showcase (placeholder)
 */
export default function HomePage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');

  /**
   * Handle search submission from the hero search box
   */
  const handleSearch = (query: string) => {
    if (query.trim()) {
      // Navigate to search page with query parameter
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <MainLayout
      title="Steam Game Search Engine - Discover Amazing Games"
      description="Find your next favorite game with our intelligent Steam game search engine. Advanced filtering, semantic search, and personalized recommendations."
    >
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-steam-blue to-steam-blue-dark py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Discover Your Next
            <span className="text-gradient-steam block">Favorite Game</span>
          </h1>
          
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Search through thousands of Steam games with intelligent algorithms
            that understand what you're really looking for.
          </p>

          {/* Hero Search Box */}
          <div className="max-w-2xl mx-auto mb-8">
            <SearchBox
              placeholder="Search for games like 'Hades', 'roguelike', or 'co-op adventure'..."
              onSearch={handleSearch}
              value={searchQuery}
              onChange={setSearchQuery}
              size="large"
            />
          </div>

          {/* Quick Search Examples */}
          <div className="flex flex-wrap justify-center gap-2">
            <span className="text-gray-400 text-sm">Try:</span>
            {['games like Hades', 'local co-op', 'Steam Deck compatible', 'indie roguelike'].map((example) => (
              <button
                key={example}
                onClick={() => handleSearch(example)}
                className="text-steam-green hover:text-steam-green-light text-sm underline"
              >
                "{example}"
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-steam-blue-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">
              Why Our Search Engine?
            </h2>
            <p className="text-gray-300 max-w-2xl mx-auto">
              We've built advanced features to help you find exactly what you're looking for,
              whether it's a specific game or a new experience.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1: Semantic Search */}
            <div className="card-steam p-6 text-center">
              <div className="w-12 h-12 bg-steam-green rounded-lg mx-auto mb-4 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Semantic Search</h3>
              <p className="text-gray-300">
                Search using natural language. Find "games like Hades" or "cozy farming games"
                and get relevant results that understand context.
              </p>
            </div>

            {/* Feature 2: Advanced Filtering */}
            <div className="card-steam p-6 text-center">
              <div className="w-12 h-12 bg-steam-green rounded-lg mx-auto mb-4 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.207A1 1 0 013 6.5V4z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Smart Filtering</h3>
              <p className="text-gray-300">
                Filter by price, platform, co-op type, Steam Deck compatibility,
                and more. Find exactly what fits your needs.
              </p>
            </div>

            {/* Feature 3: Intelligent Ranking */}
            <div className="card-steam p-6 text-center">
              <div className="w-12 h-12 bg-steam-green rounded-lg mx-auto mb-4 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Quality Ranking</h3>
              <p className="text-gray-300">
                Our algorithm considers review quality, player activity, and relevance
                to surface hidden gems, not just popular titles.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Start Section */}
      <section className="py-16 bg-steam-blue">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-8">
            Get Started in Seconds
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-8 h-8 bg-steam-green rounded-full mx-auto mb-4 flex items-center justify-center text-white font-bold">
                1
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Search</h3>
              <p className="text-gray-300">
                Enter what you're looking for in natural language
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-8 h-8 bg-steam-green rounded-full mx-auto mb-4 flex items-center justify-center text-white font-bold">
                2
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Filter</h3>
              <p className="text-gray-300">
                Refine results with our advanced filtering options
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-8 h-8 bg-steam-green rounded-full mx-auto mb-4 flex items-center justify-center text-white font-bold">
                3
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Discover</h3>
              <p className="text-gray-300">
                Find your next favorite game with detailed information
              </p>
            </div>
          </div>

          <div className="mt-8">
            <button
              onClick={() => router.push('/search')}
              className="btn-steam text-lg px-8 py-3"
            >
              Start Searching Now
            </button>
          </div>
        </div>
      </section>

      {/* TODO: Add popular/recent games section */}
      {/* This section would display trending or recently added games */}
      {/* Implementation depends on backend API availability */}
    </MainLayout>
  );
}

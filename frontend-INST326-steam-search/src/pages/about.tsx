/**
 * About Page Component
 * 
 * This page provides information about the Steam Game Search Engine project,
 * including its purpose, features, technology stack, and team information.
 * It serves as both user documentation and project showcase for the INST326 assignment.
 */

import React from 'react';
import MainLayout from '@/components/Layout/MainLayout';

/**
 * About Page Component
 * 
 * Features:
 * - Project overview and mission
 * - Technology stack information
 * - Feature highlights
 * - Team and course information
 * - Architecture overview
 */
export default function AboutPage() {
  return (
    <MainLayout
      title="About - Steam Game Search Engine"
      description="Learn about the Steam Game Search Engine project, its features, technology stack, and the team behind it."
    >
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            About Steam Game Search Engine
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            An intelligent game discovery platform that goes beyond traditional search
            to help you find your next favorite Steam game.
          </p>
        </div>

        {/* Project Overview */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Project Overview</h2>
          <div className="card-steam p-6">
            <p className="text-gray-300 mb-4">
              The Steam Game Search Engine is an advanced search platform designed to address
              the limitations of Steam's current search functionality. Our system combines
              traditional keyword search with semantic understanding and intelligent ranking
              to surface both popular titles and hidden gems.
            </p>
            <p className="text-gray-300 mb-4">
              Unlike conventional search engines that rely primarily on popularity metrics,
              our platform considers multiple factors including review quality, player activity,
              and semantic similarity to provide more relevant and diverse search results.
            </p>
            <p className="text-gray-300">
              This project was developed as part of the INST326 course at the University of Maryland,
              demonstrating advanced software engineering principles, API design, and modern
              web development practices.
            </p>
          </div>
        </section>

        {/* Key Features */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card-steam p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                🔍 Intelligent Search
              </h3>
              <p className="text-gray-300">
                Combines BM25 keyword matching with semantic search using vector embeddings
                to understand natural language queries like "games like Hades" or "cozy farming games".
              </p>
            </div>

            <div className="card-steam p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                🎯 Fusion Ranking
              </h3>
              <p className="text-gray-300">
                Advanced ranking algorithm that balances relevance, review quality, and player
                activity to surface high-quality games that might be overlooked by popularity-based systems.
              </p>
            </div>

            <div className="card-steam p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                🔧 Advanced Filtering
              </h3>
              <p className="text-gray-300">
                Comprehensive filtering options including price range, platform compatibility,
                multiplayer type, and Steam Deck support for precise game discovery.
              </p>
            </div>

            <div className="card-steam p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                📱 Modern Interface
              </h3>
              <p className="text-gray-300">
                Responsive, Steam-themed interface built with React and TypeScript,
                providing an intuitive and familiar user experience.
              </p>
            </div>
          </div>
        </section>

        {/* Technology Stack */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Technology Stack</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Frontend */}
            <div className="card-steam p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Frontend</h3>
              <ul className="space-y-2 text-gray-300">
                <li>• <strong>Next.js 14</strong> - React framework with SSR and routing</li>
                <li>• <strong>TypeScript</strong> - Type-safe JavaScript development</li>
                <li>• <strong>Tailwind CSS</strong> - Utility-first CSS framework</li>
                <li>• <strong>React Hooks</strong> - Modern state management</li>
                <li>• <strong>Axios</strong> - HTTP client for API communication</li>
              </ul>
            </div>

            {/* Backend */}
            <div className="card-steam p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Backend</h3>
              <ul className="space-y-2 text-gray-300">
                <li>• <strong>FastAPI</strong> - High-performance Python web framework</li>
                <li>• <strong>SQLite</strong> - Lightweight database for game metadata</li>
                <li>• <strong>Faiss</strong> - Vector similarity search library</li>
                <li>• <strong>BM25</strong> - Keyword search algorithm</li>
                <li>• <strong>Pydantic</strong> - Data validation and serialization</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Architecture */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">System Architecture</h2>
          <div className="card-steam p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div>
                <div className="w-16 h-16 bg-steam-green rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <span className="text-white font-bold text-xl">UI</span>
                </div>
                <h4 className="text-white font-semibold mb-2">Frontend Layer</h4>
                <p className="text-gray-300 text-sm">
                  Next.js application with TypeScript, providing responsive UI and client-side logic
                </p>
              </div>

              <div>
                <div className="w-16 h-16 bg-steam-green rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <span className="text-white font-bold text-xl">API</span>
                </div>
                <h4 className="text-white font-semibold mb-2">API Layer</h4>
                <p className="text-gray-300 text-sm">
                  FastAPI backend handling search requests, data processing, and ranking algorithms
                </p>
              </div>

              <div>
                <div className="w-16 h-16 bg-steam-green rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <span className="text-white font-bold text-xl">DB</span>
                </div>
                <h4 className="text-white font-semibold mb-2">Data Layer</h4>
                <p className="text-gray-300 text-sm">
                  SQLite database with Faiss vector indices for efficient search and retrieval
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Course Information */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Course Information</h2>
          <div className="card-steam p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Academic Context</h3>
                <ul className="space-y-2 text-gray-300">
                  <li>• <strong>Course:</strong> INST326 - Object-Oriented Programming</li>
                  <li>• <strong>Institution:</strong> University of Maryland</li>
                  <li>• <strong>Semester:</strong> Fall 2024</li>
                  <li>• <strong>Project Type:</strong> Group Assignment</li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Learning Objectives</h3>
                <ul className="space-y-2 text-gray-300">
                  <li>• Object-oriented design principles</li>
                  <li>• API development and integration</li>
                  <li>• Modern web development practices</li>
                  <li>• Software engineering methodologies</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Function Library */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">Function Library</h2>
          <div className="card-steam p-6">
            <p className="text-gray-300 mb-4">
              This project includes a comprehensive function library documenting all major
              components and algorithms used in the system. The library serves both as
              technical documentation and as a demonstration of code organization and
              documentation best practices.
            </p>
            <div className="text-center">
              <a
                href="/function-library"
                className="btn-steam inline-block"
              >
                Explore Function Library
              </a>
            </div>
          </div>
        </section>

        {/* Footer */}
        <section className="text-center">
          <div className="card-steam p-6">
            <h3 className="text-lg font-semibold text-white mb-3">
              Ready to Discover Amazing Games?
            </h3>
            <p className="text-gray-300 mb-6">
              Try our intelligent search engine and find your next favorite Steam game.
            </p>
            <div className="space-x-4">
              <a href="/search" className="btn-steam">
                Start Searching
              </a>
              <a href="/" className="btn-steam">
                Back to Home
              </a>
            </div>
          </div>
        </section>
      </div>
    </MainLayout>
  );
}

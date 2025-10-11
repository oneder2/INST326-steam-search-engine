/**
 * Search Results Component
 * 
 * This component displays search results in a list format with game cards.
 * It handles loading states, error states, and empty results.
 */

import React from 'react';
import Link from 'next/link';
import { GameResult } from '@/types/api';
import { REVIEW_STATUS_CONFIG } from '@/constants/api';

interface SearchResultsProps {
  /** Array of game results to display */
  results: GameResult[];
  /** Whether search is currently loading */
  isLoading: boolean;
  /** Error message if search failed */
  error: string | null;
  /** Current search query */
  query: string;
  /** Callback to retry search */
  onRetry: () => void;
}

/**
 * Individual Game Card Component
 */
function GameCard({ game }: { game: GameResult }) {
  const reviewConfig = REVIEW_STATUS_CONFIG[game.review_status];
  
  return (
    <Link href={`/games/${game.id}`}>
      <div className="card-steam p-6 hover:shadow-steam-hover transition-all duration-200 cursor-pointer">
        <div className="flex items-start justify-between">
          {/* Game Info */}
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-white mb-2 truncate">
              {game.title}
            </h3>
            
            {/* Genres */}
            <div className="flex flex-wrap gap-1 mb-3">
              {game.genres.map((genre) => (
                <span
                  key={genre}
                  className="px-2 py-1 bg-steam-blue-light text-xs text-gray-300 rounded"
                >
                  {genre}
                </span>
              ))}
            </div>
            
            {/* Review Status */}
            <div className="flex items-center gap-2 mb-3">
              <span
                className={`px-2 py-1 text-xs font-medium rounded ${reviewConfig.color} ${reviewConfig.textColor}`}
              >
                {game.review_status}
              </span>
              
              {game.deck_compatible && (
                <span className="px-2 py-1 bg-steam-green text-xs text-white rounded">
                  Steam Deck
                </span>
              )}
            </div>
            
            {/* Relevance Score */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">Relevance:</span>
              <div className="flex-1 bg-steam-blue-dark rounded-full h-2 max-w-24">
                <div
                  className="bg-steam-green h-2 rounded-full transition-all duration-300"
                  style={{ width: `${game.score * 100}%` }}
                />
              </div>
              <span className="text-xs text-gray-400">
                {Math.round(game.score * 100)}%
              </span>
            </div>
          </div>
          
          {/* Price */}
          <div className="ml-4 text-right">
            <div className="text-xl font-bold text-steam-green">
              {game.price === 0 ? 'Free' : `$${game.price.toFixed(2)}`}
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}

/**
 * Loading Skeleton Component
 */
function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 5 }, (_, i) => (
        <div key={i} className="card-steam p-6 animate-pulse">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="h-6 bg-steam-blue-light rounded mb-2 w-3/4" />
              <div className="flex gap-2 mb-3">
                <div className="h-5 bg-steam-blue-light rounded w-16" />
                <div className="h-5 bg-steam-blue-light rounded w-20" />
              </div>
              <div className="h-4 bg-steam-blue-light rounded w-24 mb-3" />
              <div className="h-3 bg-steam-blue-light rounded w-32" />
            </div>
            <div className="ml-4">
              <div className="h-8 bg-steam-blue-light rounded w-16" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Empty Results Component
 */
function EmptyResults({ query }: { query: string }) {
  return (
    <div className="text-center py-12">
      <div className="w-16 h-16 bg-steam-blue-light rounded-full mx-auto mb-4 flex items-center justify-center">
        <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      
      <h3 className="text-xl font-semibold text-white mb-2">
        No games found
      </h3>
      
      <p className="text-gray-300 mb-6 max-w-md mx-auto">
        We couldn't find any games matching "{query}". Try adjusting your search terms or filters.
      </p>
      
      <div className="space-y-2 text-sm text-gray-400">
        <p>Suggestions:</p>
        <ul className="space-y-1">
          <li>• Check your spelling</li>
          <li>• Try broader search terms</li>
          <li>• Remove some filters</li>
          <li>• Search for game genres instead</li>
        </ul>
      </div>
    </div>
  );
}

/**
 * Error State Component
 */
function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="text-center py-12">
      <div className="w-16 h-16 bg-red-900 rounded-full mx-auto mb-4 flex items-center justify-center">
        <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      
      <h3 className="text-xl font-semibold text-white mb-2">
        Search Error
      </h3>
      
      <p className="text-gray-300 mb-6">
        {error}
      </p>
      
      <button
        onClick={onRetry}
        className="btn-steam"
      >
        Try Again
      </button>
    </div>
  );
}

/**
 * Main Search Results Component
 */
export default function SearchResults({
  results,
  isLoading,
  error,
  query,
  onRetry,
}: SearchResultsProps) {
  // Show loading state
  if (isLoading) {
    return <LoadingSkeleton />;
  }
  
  // Show error state
  if (error) {
    return <ErrorState error={error} onRetry={onRetry} />;
  }
  
  // Show empty state
  if (!isLoading && results.length === 0 && query) {
    return <EmptyResults query={query} />;
  }
  
  // Show results
  if (results.length > 0) {
    return (
      <div className="space-y-4">
        {results.map((game) => (
          <GameCard key={game.id} game={game} />
        ))}
      </div>
    );
  }
  
  // Default state (no search performed)
  return (
    <div className="text-center py-12">
      <div className="w-16 h-16 bg-steam-blue-light rounded-full mx-auto mb-4 flex items-center justify-center">
        <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      
      <h3 className="text-xl font-semibold text-white mb-2">
        Start Your Search
      </h3>
      
      <p className="text-gray-300">
        Enter a search term above to discover amazing Steam games
      </p>
    </div>
  );
}

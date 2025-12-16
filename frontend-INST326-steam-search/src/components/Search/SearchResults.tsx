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
 * Individual Game Card Component - Compact Horizontal Layout
 * 
 * Displays comprehensive game information in a space-efficient horizontal layout:
 * - Title and type on same line
 * - Genres/Features labels inline with tags
 * - Stats labels inline with values
 */
function GameCard({ game }: { game: any }) {
  // Format release date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  // Format number with commas
  const formatNumber = (num: number) => {
    return num.toLocaleString('en-US');
  };

  // Get type badge color
  const getTypeBadgeColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'game': return 'bg-blue-600 text-white';
      case 'dlc': return 'bg-purple-600 text-white';
      case 'demo': return 'bg-yellow-600 text-white';
      case 'mod': return 'bg-green-600 text-white';
      default: return 'bg-gray-600 text-white';
    }
  };
  
  return (
    <Link href={`/games/${game.id}`}>
      <div className="card-steam p-5 hover:shadow-steam-hover transition-all duration-200 cursor-pointer">
        {/* Header: Title, Type Badge, and Price on same line */}
        <div className="flex items-center justify-between gap-4 mb-3">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-white leading-tight truncate">
              {game.title}
            </h3>
            
            {/* Type Badge on same line as title */}
            {game.type && (
              <span className={`px-2 py-0.5 text-xs font-medium rounded uppercase flex-shrink-0 ${getTypeBadgeColor(game.type)}`}>
                {game.type}
              </span>
            )}
          </div>
          
          {/* Price */}
          <div className="text-xl font-bold text-steam-green flex-shrink-0">
            {game.price === 0 ? 'Free' : `$${game.price.toFixed(2)}`}
          </div>
        </div>

        {/* Description */}
        {game.description && (
          <p className="text-sm text-gray-300 mb-3 line-clamp-2 leading-relaxed">
            {game.description}
          </p>
        )}

        {/* Genres - Label and tags on same line */}
        {game.genres && game.genres.length > 0 && (
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <div className="flex items-center gap-1.5 flex-shrink-0">
              <svg className="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              <span className="text-xs text-gray-400 font-medium">Genres:</span>
            </div>
            {game.genres.slice(0, 5).map((genre: string) => (
              <span
                key={genre}
                className="px-2.5 py-0.5 bg-steam-blue-light text-xs text-gray-200 rounded-full"
              >
                {genre}
              </span>
            ))}
            {game.genres.length > 5 && (
              <span className="text-xs text-gray-400">
                +{game.genres.length - 5}
              </span>
            )}
          </div>
        )}

        {/* Categories - Label and tags on same line */}
        {game.categories && game.categories.length > 0 && (
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <div className="flex items-center gap-1.5 flex-shrink-0">
              <svg className="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
              <span className="text-xs text-gray-400 font-medium">Features:</span>
            </div>
            {game.categories.slice(0, 4).map((category: string) => (
              <span
                key={category}
                className="px-2 py-0.5 bg-steam-dark border border-steam-blue-light text-xs text-gray-300 rounded"
              >
                {category}
              </span>
            ))}
            {game.categories.length > 4 && (
              <span className="text-xs text-gray-400">
                +{game.categories.length - 4}
              </span>
            )}
          </div>
        )}

        {/* Stats Row - Labels and values on same line */}
        <div className="flex items-center gap-4 pt-3 border-t border-steam-blue-light text-xs flex-wrap">
          {/* Release Date */}
          <div className="flex items-center gap-1.5">
            <svg className="w-3 h-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-gray-500 font-medium">Released:</span>
            <span className="text-gray-300">{formatDate(game.release_date)}</span>
          </div>

          {/* Total Reviews */}
          <div className="flex items-center gap-1.5">
            <svg className="w-3 h-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            <span className="text-gray-500 font-medium">Reviews:</span>
            <span className="text-gray-300">{game.total_reviews ? formatNumber(game.total_reviews) : 'N/A'}</span>
          </div>

          {/* BM25 Score */}
          {game.bm25_score !== undefined && game.bm25_score > 0 && (
            <div className="flex items-center gap-1.5">
              <svg className="w-3 h-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span className="text-gray-500 font-medium">Relevance:</span>
              <span className="text-steam-green font-medium">{game.bm25_score.toFixed(2)}</span>
            </div>
          )}
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
      <div className="space-y-5">
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

/**
 * Game Detail Page Component
 * 
 * This page displays detailed information about a specific Steam game.
 * It fetches game data based on the game ID from the URL and presents
 * comprehensive information including description, screenshots, and metrics.
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import MainLayout from '@/components/Layout/MainLayout';
import { getGameDetail } from '@/services/api';

// Actual game detail type from backend
interface GameDetail {
  game_id: number;
  title: string;
  price: number;
  genres: string[];
  categories: string[];
  short_description?: string;
  detailed_description?: string;
  release_date?: string;
  total_reviews?: number;
  dlc_count?: number;
  type?: string;
}

/**
 * Game Detail Page Component
 * 
 * Features:
 * - Comprehensive game information display
 * - Screenshots and media gallery
 * - Review status and ratings
 * - Platform compatibility information
 * - Related games suggestions (placeholder)
 */
export default function GameDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  
  const [game, setGame] = useState<GameDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch game details when component mounts or ID changes
   */
  useEffect(() => {
    if (id && typeof id === 'string') {
      fetchGameDetails(parseInt(id, 10));
    }
  }, [id]);

  /**
   * Fetch game details from API
   */
  const fetchGameDetails = async (gameId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Call actual API
      // Note: getGameDetail returns ApiResponse<GameDetailResponse>
      // The backend directly returns GameDetail, so response.data IS the GameDetail object
      const response = await getGameDetail(gameId);
      
      console.log('API Response:', response); // Debug log
      
      // response.data is already the GameDetail object from backend
      if (response.data) {
        const data = response.data as any;
        
        // Transform data to match our GameDetail type
        const gameData: GameDetail = {
          game_id: data.game_id,
          title: data.title,
          price: data.price,
          genres: data.genres || [],
          categories: data.categories || [],
          short_description: data.short_description,
          detailed_description: data.detailed_description,
          release_date: data.release_date,
          total_reviews: data.total_reviews,
          dlc_count: data.dlc_count,
          type: data.type,
        };
        
        console.log('Transformed game data:', gameData); // Debug log
        setGame(gameData);
      } else {
        console.error('No data in response:', response);
        throw new Error('Game not found');
      }
    } catch (err) {
      setError('Failed to load game details. Please try again.');
      console.error('Game detail fetch error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Loading state
   */
  if (isLoading) {
    return (
      <MainLayout title="Loading Game Details...">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-steam-blue-light rounded w-1/2 mb-4" />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="h-64 bg-steam-blue-light rounded mb-6" />
                <div className="space-y-3">
                  <div className="h-4 bg-steam-blue-light rounded w-full" />
                  <div className="h-4 bg-steam-blue-light rounded w-3/4" />
                  <div className="h-4 bg-steam-blue-light rounded w-1/2" />
                </div>
              </div>
              <div>
                <div className="h-32 bg-steam-blue-light rounded" />
              </div>
            </div>
          </div>
        </div>
      </MainLayout>
    );
  }

  /**
   * Error state
   */
  if (error || !game) {
    return (
      <MainLayout title="Game Not Found">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <div className="w-16 h-16 bg-red-900 rounded-full mx-auto mb-4 flex items-center justify-center">
            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          
          <h1 className="text-2xl font-bold text-white mb-4">
            {error || 'Game Not Found'}
          </h1>
          
          <p className="text-gray-300 mb-6">
            The game you're looking for doesn't exist or couldn't be loaded.
          </p>
          
          <div className="space-x-4">
            <button
              onClick={() => router.back()}
              className="btn-steam"
            >
              Go Back
            </button>
            <Link href="/search" className="btn-steam">
              Search Games
            </Link>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout
      title={`${game.title} - Steam Game Search Engine`}
      description={game.description}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="mb-6">
          <ol className="flex items-center space-x-2 text-sm text-gray-400">
            <li><Link href="/" className="hover:text-white">Home</Link></li>
            <li>/</li>
            <li><Link href="/search" className="hover:text-white">Search</Link></li>
            <li>/</li>
            <li className="text-white">{game.title}</li>
          </ol>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Game Header */}
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-white mb-2">
                {game.title}
              </h1>
              
              <div className="flex items-center gap-4 mb-4">
                {game.total_reviews !== undefined && game.total_reviews !== null && (
                  <span className="px-3 py-1 bg-steam-blue text-sm text-white rounded">
                    {game.total_reviews.toLocaleString()} Reviews
                  </span>
                )}
                
                <span className={`px-3 py-1 text-sm font-medium rounded ${
                  game.type === 'game' ? 'bg-green-900 text-green-200' : 'bg-blue-900 text-blue-200'
                }`}>
                  {game.type === 'game' ? 'Game' : 'DLC'}
                </span>
              </div>
              
              <div className="flex flex-wrap gap-2">
                {game.genres.map((genre) => (
                  <span
                    key={genre}
                    className="px-2 py-1 bg-steam-blue-light text-sm text-gray-300 rounded"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            </div>

            {/* Description */}
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">About This Game</h2>
              <div className="prose prose-invert max-w-none">
                <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {game.detailed_description || game.short_description || 'No description available.'}
                </p>
              </div>
            </div>

            {/* Game Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Game Information</h3>
                <dl className="space-y-2">
                  {game.release_date && (
                    <>
                      <dt className="text-sm text-gray-400">Release Date</dt>
                      <dd className="text-sm text-white">
                        {new Date(game.release_date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </dd>
                    </>
                  )}
                  <dt className="text-sm text-gray-400">Type</dt>
                  <dd className="text-sm text-white capitalize">{game.type || 'Game'}</dd>
                  
                  {game.dlc_count !== undefined && game.dlc_count > 0 && (
                    <>
                      <dt className="text-sm text-gray-400">DLC Available</dt>
                      <dd className="text-sm text-white">{game.dlc_count} DLC(s)</dd>
                    </>
                  )}
                </dl>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Community</h3>
                <dl className="space-y-2">
                  {game.total_reviews !== undefined && game.total_reviews !== null && (
                    <>
                      <dt className="text-sm text-gray-400">Total Reviews</dt>
                      <dd className="text-sm text-white">{game.total_reviews.toLocaleString()}</dd>
                    </>
                  )}
                  
                  {game.categories && game.categories.length > 0 && (
                    <>
                      <dt className="text-sm text-gray-400">Features</dt>
                      <dd className="text-sm text-white">
                        {game.categories.slice(0, 3).join(', ')}
                        {game.categories.length > 3 && ` +${game.categories.length - 3} more`}
                      </dd>
                    </>
                  )}
                </dl>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div>
            {/* Purchase Info */}
            <div className="card-steam p-6 mb-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-steam-green mb-4">
                  {game.price === 0 ? 'Free' : `$${game.price.toFixed(2)}`}
                </div>
                
                <button className="btn-steam w-full mb-3">
                  View on Steam
                </button>
                
                <p className="text-xs text-gray-400">
                  Prices may vary on Steam store
                </p>
              </div>
            </div>

            {/* TODO: Add related games section */}
            <div className="card-steam p-6">
              <h3 className="text-lg font-semibold text-white mb-4">
                Related Games
              </h3>
              <p className="text-sm text-gray-400">
                Related game recommendations coming soon
              </p>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

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
import { GameDetailResponse } from '@/types/api';
import { REVIEW_STATUS_CONFIG } from '@/constants/api';

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
  
  const [game, setGame] = useState<GameDetailResponse | null>(null);
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
      // TODO: Replace with actual API call
      // const response = await getGameDetail(gameId);
      // setGame(response.data);
      
      // Mock game data for now
      const mockGame: GameDetailResponse = {
        game_id: gameId,
        title: `Mock Game ${gameId}`,
        description: 'A short description of this amazing game.',
        price: 29.99,
        genres: ['Action', 'Adventure', 'Indie'],
        coop_type: 'Online',
        deck_comp: true,
        ranking_metrics: {
          review_stability: 0.85,
          player_activity: 0.92,
        },
        full_description: `This is a comprehensive description of Mock Game ${gameId}. It features exciting gameplay, stunning visuals, and an engaging storyline that will keep you entertained for hours. The game combines elements of action and adventure with innovative mechanics that set it apart from other titles in the genre.`,
        screenshots: [
          'https://via.placeholder.com/800x450/1b2838/ffffff?text=Screenshot+1',
          'https://via.placeholder.com/800x450/2a475e/ffffff?text=Screenshot+2',
          'https://via.placeholder.com/800x450/171a21/ffffff?text=Screenshot+3',
        ],
        trailer_url: 'https://example.com/trailer',
        release_date: '2024-01-15',
        developer: 'Mock Studios',
        publisher: 'Indie Games Inc.',
      };
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setGame(mockGame);
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

  const reviewConfig = REVIEW_STATUS_CONFIG[game.review_status || 'Mixed'];

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
                <span
                  className={`px-3 py-1 text-sm font-medium rounded ${reviewConfig.color} ${reviewConfig.textColor}`}
                >
                  {game.review_status || 'Mixed'}
                </span>
                
                {game.deck_comp && (
                  <span className="px-3 py-1 bg-steam-green text-sm text-white rounded">
                    Steam Deck Compatible
                  </span>
                )}
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

            {/* Screenshots */}
            {game.screenshots && game.screenshots.length > 0 && (
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-white mb-4">Screenshots</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {game.screenshots.map((screenshot, index) => (
                    <div key={index} className="aspect-video bg-steam-blue-light rounded overflow-hidden">
                      <img
                        src={screenshot}
                        alt={`${game.title} screenshot ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Description */}
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">About This Game</h2>
              <div className="prose prose-invert max-w-none">
                <p className="text-gray-300 leading-relaxed">
                  {game.full_description || game.description}
                </p>
              </div>
            </div>

            {/* Game Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Game Information</h3>
                <dl className="space-y-2">
                  {game.developer && (
                    <>
                      <dt className="text-sm text-gray-400">Developer</dt>
                      <dd className="text-sm text-white">{game.developer}</dd>
                    </>
                  )}
                  {game.publisher && (
                    <>
                      <dt className="text-sm text-gray-400">Publisher</dt>
                      <dd className="text-sm text-white">{game.publisher}</dd>
                    </>
                  )}
                  {game.release_date && (
                    <>
                      <dt className="text-sm text-gray-400">Release Date</dt>
                      <dd className="text-sm text-white">
                        {new Date(game.release_date).toLocaleDateString()}
                      </dd>
                    </>
                  )}
                  <dt className="text-sm text-gray-400">Multiplayer</dt>
                  <dd className="text-sm text-white">{game.coop_type}</dd>
                </dl>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Quality Metrics</h3>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">Review Stability</span>
                      <span className="text-white">
                        {Math.round(game.ranking_metrics.review_stability * 100)}%
                      </span>
                    </div>
                    <div className="w-full bg-steam-blue-dark rounded-full h-2">
                      <div
                        className="bg-steam-green h-2 rounded-full transition-all duration-300"
                        style={{ width: `${game.ranking_metrics.review_stability * 100}%` }}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">Player Activity</span>
                      <span className="text-white">
                        {Math.round(game.ranking_metrics.player_activity * 100)}%
                      </span>
                    </div>
                    <div className="w-full bg-steam-blue-dark rounded-full h-2">
                      <div
                        className="bg-steam-green h-2 rounded-full transition-all duration-300"
                        style={{ width: `${game.ranking_metrics.player_activity * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
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

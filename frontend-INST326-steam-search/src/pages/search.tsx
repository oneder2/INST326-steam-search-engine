/**
 * Search Page Component - Phase 1 Implementation
 * 
 * This page provides search and filter functionality for the Steam Game Search Engine.
 * 
 * Phase 1 Features (Current):
 * - Text search in game names
 * - Price range filter
 * - Genre filter
 * - Game type filter
 * - Sort by price, reviews, date, name
 * - Pagination
 * 
 * Phase 2 Features (Future):
 * - Multi-field search (name + description)
 * - More filter options
 * - Search suggestions
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '@/components/Layout/MainLayout';
import SearchBox from '@/components/Search/SearchBox';
import SearchResults from '@/components/Search/SearchResults';
import { GameResult } from '@/types/api';
import { SEARCH_LIMITS } from '@/constants/api';
import { simpleSearch } from '@/services/api';

/**
 * Search Page Component
 * 
 * Manages search state, filters, and pagination.
 * Communicates with backend via POST /api/v1/search/games endpoint.
 */
export default function SearchPage() {
  const router = useRouter();
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [games, setGames] = useState<GameResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalGames, setTotalGames] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  
  // Filter state
  const [priceMax, setPriceMax] = useState<number | undefined>(undefined);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [gameType, setGameType] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('relevance');
  
  // Available genres (could be fetched from API in Phase 2)
  const availableGenres = [
    'Action', 'Adventure', 'RPG', 'Strategy', 'Simulation',
    'Sports', 'Racing', 'Indie', 'Casual', 'Puzzle'
  ];

  /**
   * Load games from API with current search/filter settings
   */
  const loadGames = async (page: number = 1) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const offset = (page - 1) * SEARCH_LIMITS.DEFAULT_LIMIT;
      
      // Build filters object
      const filters: any = {};
      if (priceMax !== undefined && priceMax > 0) {
        filters.price_max = priceMax * 100; // Convert to cents
      }
      if (selectedGenres.length > 0) {
        filters.genres = selectedGenres;
      }
      if (gameType) {
        filters.type = gameType;
      }
      
      // Call search API
      const response = await simpleSearch({
        query: searchQuery,
        filters: Object.keys(filters).length > 0 ? filters : undefined,
        sort_by: sortBy as any,
        offset,
        limit: SEARCH_LIMITS.DEFAULT_LIMIT
      });
      
      // Transform backend response to frontend GameResult format
      const transformedGames = response.data.results.map((game: any) => ({
        id: game.game_id,
        title: game.title,
        score: game.relevance_score || 0,
        price: game.price,
        genres: game.genres || [],
        review_status: 'Mixed', // TODO: Get from backend in Phase 2
        deck_compatible: false, // TODO: Get from backend in Phase 2
        description: game.description || '',
        coop_type: game.coop_type,
        release_date: game.release_date,
        developer: game.developer,
        publisher: game.publisher,
      }));
      
      setGames(transformedGames);
      setTotalGames(response.data.total);
      
    } catch (err) {
      setError('Failed to search games. Please try again.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Initialize page from URL parameters
   */
  useEffect(() => {
    if (!router.isReady) return;
    
    const { q, page, price_max, genres, type, sort } = router.query;
    
    // Parse all parameters first
    const queryStr = (q && typeof q === 'string') ? q : '';
    const pageNum = page && typeof page === 'string' ? parseInt(page, 10) : 1;
    const priceMaxNum = price_max && typeof price_max === 'string' ? parseInt(price_max, 10) : undefined;
    const genreArray = genres ? (Array.isArray(genres) ? genres as string[] : [genres as string]) : [];
    const typeStr = (type && typeof type === 'string') ? type : '';
    const sortStr = (sort && typeof sort === 'string') ? sort : 'relevance';
    
    // Update all state
    setSearchQuery(queryStr);
    setCurrentPage(pageNum);
    setPriceMax(priceMaxNum);
    setSelectedGenres(genreArray);
    setGameType(typeStr);
    setSortBy(sortStr);
    
    // Load games with parsed parameters (not from state)
    loadGamesWithParams(queryStr, priceMaxNum, genreArray, typeStr, sortStr, pageNum);
  }, [router.isReady]);
  
  /**
   * Load games with specific parameters (used by useEffect)
   */
  const loadGamesWithParams = async (
    query: string,
    priceMaxValue: number | undefined,
    genres: string[],
    type: string,
    sort: string,
    page: number
  ) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const offset = (page - 1) * SEARCH_LIMITS.DEFAULT_LIMIT;
      
      // Build filters object
      const filters: any = {};
      if (priceMaxValue !== undefined && priceMaxValue > 0) {
        filters.price_max = priceMaxValue * 100; // Convert to cents
      }
      if (genres.length > 0) {
        filters.genres = genres;
      }
      if (type) {
        filters.type = type;
      }
      
      // Call search API
      const response = await simpleSearch({
        query,
        filters: Object.keys(filters).length > 0 ? filters : undefined,
        sort_by: sort as any,
        offset,
        limit: SEARCH_LIMITS.DEFAULT_LIMIT
      });
      
      // Transform backend response to frontend GameResult format
      const transformedGames = response.data.results.map((game: any) => ({
        id: game.game_id,
        title: game.title,
        score: game.relevance_score || 0,
        price: game.price,
        genres: game.genres || [],
        review_status: 'Mixed',
        deck_compatible: false,
        description: game.description || '',
        coop_type: game.coop_type,
        release_date: game.release_date,
        developer: game.developer,
        publisher: game.publisher,
      }));
      
      setGames(transformedGames);
      setTotalGames(response.data.total);
      
    } catch (err) {
      setError('Failed to search games. Please try again.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Update URL with current search parameters
   */
  const updateURL = () => {
    const params = new URLSearchParams();
    
    if (searchQuery) params.set('q', searchQuery);
    if (currentPage > 1) params.set('page', currentPage.toString());
    if (priceMax) params.set('price_max', priceMax.toString());
    if (selectedGenres.length > 0) {
      selectedGenres.forEach(genre => params.append('genres', genre));
    }
    if (gameType) params.set('type', gameType);
    if (sortBy !== 'relevance') params.set('sort', sortBy);
    
    const queryString = params.toString();
    const newUrl = queryString ? `/search?${queryString}` : '/search';
    
    router.push(newUrl, undefined, { shallow: true });
  };

  /**
   * Handle search submission
   */
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    updateURL();
    loadGames(1);
  };

  /**
   * Handle filter changes
   */
  const handleFilterChange = () => {
    setCurrentPage(1);
    updateURL();
    loadGames(1);
  };

  /**
   * Handle page change
   */
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    updateURL();
    loadGames(page);
  };

  /**
   * Calculate pagination info
   */
  const totalPages = Math.ceil(totalGames / SEARCH_LIMITS.DEFAULT_LIMIT);
  const hasGames = games.length > 0;
  const showPagination = totalPages > 1;

  /**
   * Generate page numbers to display
   */
  const getPageNumbers = () => {
    const pages: number[] = [];
    const maxPagesToShow = 5;
    
    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      let startPage = Math.max(1, currentPage - 2);
      let endPage = Math.min(totalPages, currentPage + 2);
      
      if (currentPage <= 3) {
        endPage = maxPagesToShow;
      } else if (currentPage >= totalPages - 2) {
        startPage = totalPages - maxPagesToShow + 1;
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
    }
    
    return pages;
  };

  return (
    <MainLayout
      title={searchQuery ? `Search: ${searchQuery} - Steam Game Search Engine` : 'Search Games - Steam Game Search Engine'}
      description="Search for Steam games with filters and sorting"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-4">
            Search Games
          </h1>
          
          {/* Search Box */}
          <div className="max-w-2xl">
            <SearchBox
              value={searchQuery}
              onChange={setSearchQuery}
              onSearch={handleSearch}
              placeholder="Search for games by name..."
              size="large"
              autoFocus={!searchQuery}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-steam-dark border border-steam-blue-light rounded-lg p-6 sticky top-4">
              <h2 className="text-xl font-semibold text-white mb-4">Filters</h2>
              
              {/* Price Filter */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Max Price (USD)
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={priceMax || ''}
                  onChange={(e) => {
                    const value = e.target.value ? parseInt(e.target.value) : undefined;
                    setPriceMax(value);
                  }}
                  onBlur={(e) => {
                    const value = e.target.value ? parseInt(e.target.value) : undefined;
                    setCurrentPage(1);
                    loadGamesWithParams(searchQuery, value, selectedGenres, gameType, sortBy, 1);
                  }}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      const value = priceMax;
                      setCurrentPage(1);
                      loadGamesWithParams(searchQuery, value, selectedGenres, gameType, sortBy, 1);
                    }
                  }}
                  className="w-full px-3 py-2 bg-steam-blue border border-steam-blue-light rounded text-white focus:outline-none focus:border-steam-green"
                  placeholder="Any"
                />
              </div>
              
              {/* Genre Filter */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Genres
                </label>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {availableGenres.map(genre => (
                    <label key={genre} className="flex items-center text-gray-300 hover:text-white cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedGenres.includes(genre)}
                        onChange={(e) => {
                          const newGenres = e.target.checked 
                            ? [...selectedGenres, genre]
                            : selectedGenres.filter(g => g !== genre);
                          setSelectedGenres(newGenres);
                          // Immediately trigger search with new genres
                          setCurrentPage(1);
                          loadGamesWithParams(searchQuery, priceMax, newGenres, gameType, sortBy, 1);
                        }}
                        className="mr-2"
                      />
                      <span className="text-sm">{genre}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Type Filter */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Type
                </label>
                <select
                  value={gameType}
                  onChange={(e) => {
                    const newType = e.target.value;
                    setGameType(newType);
                    setCurrentPage(1);
                    loadGamesWithParams(searchQuery, priceMax, selectedGenres, newType, sortBy, 1);
                  }}
                  className="w-full px-3 py-2 bg-steam-blue border border-steam-blue-light rounded text-white focus:outline-none focus:border-steam-green"
                >
                  <option value="">All Types</option>
                  <option value="game">Games Only</option>
                  <option value="dlc">DLC Only</option>
                </select>
              </div>
              
              {/* Clear Filters */}
              <button
                onClick={() => {
                  setPriceMax(undefined);
                  setSelectedGenres([]);
                  setGameType('');
                  setCurrentPage(1);
                  loadGamesWithParams(searchQuery, undefined, [], '', sortBy, 1);
                }}
                className="w-full px-4 py-2 bg-steam-blue border border-steam-blue-light rounded text-white hover:bg-steam-blue-light transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>

          {/* Results Area */}
          <div className="lg:col-span-3">
            {/* Results Header */}
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-white">
                  {searchQuery ? `Results for "${searchQuery}"` : 'All Games'}
                  {totalGames > 0 && (
                    <span className="text-gray-300 font-normal ml-2">
                      ({totalGames.toLocaleString()} found)
                    </span>
                  )}
                </h2>
              </div>
              
              {/* Sort Dropdown */}
              <div>
                <select
                  value={sortBy}
                  onChange={(e) => {
                    const newSort = e.target.value;
                    setSortBy(newSort);
                    setCurrentPage(1);
                    loadGamesWithParams(searchQuery, priceMax, selectedGenres, gameType, newSort, 1);
                  }}
                  className="px-3 py-2 bg-steam-blue border border-steam-blue-light rounded text-white text-sm focus:outline-none focus:border-steam-green"
                >
                  <option value="relevance">Sort by Relevance</option>
                  <option value="price_asc">Price: Low to High</option>
                  <option value="price_desc">Price: High to Low</option>
                  <option value="reviews">Most Reviewed</option>
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                  <option value="name">Name (A-Z)</option>
                </select>
              </div>
            </div>

            {/* Search Results */}
            <SearchResults
              results={games}
              isLoading={isLoading}
              error={error}
              query={searchQuery}
              onRetry={() => loadGames(currentPage)}
            />

            {/* Pagination */}
            {showPagination && hasGames && !isLoading && (
              <div className="mt-8 flex justify-center">
                <nav className="flex items-center space-x-2" aria-label="Pagination">
                  {/* Previous Button */}
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-4 py-2 text-sm font-medium bg-steam-blue border border-steam-blue-light rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-steam-blue-light transition-colors text-white"
                    aria-label="Previous page"
                  >
                    Previous
                  </button>
                  
                  {/* Page Numbers */}
                  {getPageNumbers().map((page) => (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`px-4 py-2 text-sm font-medium border rounded transition-colors ${
                        page === currentPage
                          ? 'bg-steam-green border-steam-green text-white'
                          : 'bg-steam-blue border-steam-blue-light text-gray-300 hover:bg-steam-blue-light'
                      }`}
                      aria-label={`Page ${page}`}
                      aria-current={page === currentPage ? 'page' : undefined}
                    >
                      {page}
                    </button>
                  ))}
                  
                  {/* Next Button */}
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="px-4 py-2 text-sm font-medium bg-steam-blue border border-steam-blue-light rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-steam-blue-light transition-colors text-white"
                    aria-label="Next page"
                  >
                    Next
                  </button>
                </nav>
              </div>
            )}

            {/* Pagination Info */}
            {hasGames && !isLoading && (
              <div className="mt-4 text-center text-sm text-gray-400">
                Showing {((currentPage - 1) * SEARCH_LIMITS.DEFAULT_LIMIT) + 1} - {Math.min(currentPage * SEARCH_LIMITS.DEFAULT_LIMIT, totalGames)} of {totalGames.toLocaleString()} games
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

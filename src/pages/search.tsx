/**
 * Search Page Component
 * 
 * This page provides the main search interface for the Steam Game Search Engine.
 * It includes search input, filters, results display, and pagination.
 * Users can perform both keyword and semantic searches with advanced filtering.
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '@/components/Layout/MainLayout';
import SearchBox from '@/components/Search/SearchBox';
import SearchFilters from '@/components/Search/SearchFilters';
import SearchResults from '@/components/Search/SearchResults';
import { SearchQuerySchema, SearchFilters as SearchFiltersType, GameResult } from '@/types/api';
import { SEARCH_LIMITS } from '@/constants/api';

/**
 * Search Page Component
 * 
 * Features:
 * - Advanced search with filters
 * - Real-time search results
 * - Pagination
 * - URL state management
 * - Loading and error states
 */
export default function SearchPage() {
  const router = useRouter();
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchFiltersType>({});
  const [results, setResults] = useState<GameResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  /**
   * Initialize search from URL parameters
   */
  useEffect(() => {
    if (router.isReady) {
      const { q, page, ...filterParams } = router.query;
      
      if (q && typeof q === 'string') {
        setSearchQuery(q);
      }
      
      if (page && typeof page === 'string') {
        setCurrentPage(parseInt(page, 10) || 1);
      }
      
      // Parse filter parameters from URL
      const urlFilters: SearchFiltersType = {};
      if (filterParams.price_max && typeof filterParams.price_max === 'string') {
        urlFilters.price_max = parseInt(filterParams.price_max, 10);
      }
      if (filterParams.coop_type && typeof filterParams.coop_type === 'string') {
        urlFilters.coop_type = filterParams.coop_type as any;
      }
      if (filterParams.platform) {
        urlFilters.platform = Array.isArray(filterParams.platform) 
          ? filterParams.platform as string[]
          : [filterParams.platform as string];
      }
      
      setFilters(urlFilters);
      
      // Perform search if query exists
      if (q && typeof q === 'string') {
        performSearch(q, urlFilters, parseInt(page as string, 10) || 1);
      }
    }
  }, [router.isReady, router.query]);

  /**
   * Update URL with current search parameters
   */
  const updateURL = (query: string, newFilters: SearchFiltersType, page: number = 1) => {
    const params = new URLSearchParams();
    
    if (query) params.set('q', query);
    if (page > 1) params.set('page', page.toString());
    
    // Add filter parameters
    if (newFilters.price_max) params.set('price_max', newFilters.price_max.toString());
    if (newFilters.coop_type) params.set('coop_type', newFilters.coop_type);
    if (newFilters.platform && newFilters.platform.length > 0) {
      newFilters.platform.forEach(platform => params.append('platform', platform));
    }
    
    const queryString = params.toString();
    const newUrl = queryString ? `/search?${queryString}` : '/search';
    
    router.push(newUrl, undefined, { shallow: true });
  };

  /**
   * Perform search with current parameters
   */
  const performSearch = async (query: string, searchFilters: SearchFiltersType, page: number = 1) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const searchParams: SearchQuerySchema = {
        query: query.trim(),
        filters: searchFilters,
        limit: SEARCH_LIMITS.DEFAULT_LIMIT,
        offset: (page - 1) * SEARCH_LIMITS.DEFAULT_LIMIT,
      };
      
      // TODO: Replace with actual API call
      // const response = await searchGames(searchParams);
      // setResults(response.data.results);
      // setTotalResults(response.data.total);
      
      // Mock search results for now
      const mockResults: GameResult[] = [
        {
          id: 1,
          title: `Mock Game Result for "${query}"`,
          score: 0.95,
          price: 19.99,
          genres: ['Action', 'Indie'],
          review_status: 'Very Positive',
          deck_compatible: true,
        },
        {
          id: 2,
          title: `Another Game Like "${query}"`,
          score: 0.87,
          price: 29.99,
          genres: ['Adventure', 'RPG'],
          review_status: 'Positive',
          deck_compatible: false,
        },
      ];
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setResults(mockResults);
      setTotalResults(42); // Mock total
      
    } catch (err) {
      setError('Failed to search games. Please try again.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle search submission
   */
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    updateURL(query, filters, 1);
    performSearch(query, filters, 1);
  };

  /**
   * Handle filter changes
   */
  const handleFiltersChange = (newFilters: SearchFiltersType) => {
    setFilters(newFilters);
    setCurrentPage(1);
    updateURL(searchQuery, newFilters, 1);
    
    if (searchQuery.trim()) {
      performSearch(searchQuery, newFilters, 1);
    }
  };

  /**
   * Handle page change
   */
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    updateURL(searchQuery, filters, page);
    performSearch(searchQuery, filters, page);
  };

  /**
   * Calculate pagination info
   */
  const totalPages = Math.ceil(totalResults / SEARCH_LIMITS.DEFAULT_LIMIT);
  const hasResults = results.length > 0;
  const showPagination = totalPages > 1;

  return (
    <MainLayout
      title={searchQuery ? `Search: ${searchQuery} - Steam Game Search Engine` : 'Search Games - Steam Game Search Engine'}
      description="Search for Steam games with advanced filters and intelligent ranking"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-4">
            Search Games
          </h1>
          
          {/* Main Search Box */}
          <div className="max-w-2xl">
            <SearchBox
              value={searchQuery}
              onChange={setSearchQuery}
              onSearch={handleSearch}
              placeholder="Search for games, genres, or descriptions..."
              size="large"
              autoFocus={!searchQuery}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <SearchFilters
              filters={filters}
              onFiltersChange={handleFiltersChange}
              disabled={isLoading}
            />
          </div>

          {/* Results Area */}
          <div className="lg:col-span-3">
            {/* Results Header */}
            {searchQuery && (
              <div className="mb-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-white">
                      Search Results
                      {totalResults > 0 && (
                        <span className="text-gray-300 font-normal ml-2">
                          ({totalResults.toLocaleString()} games found)
                        </span>
                      )}
                    </h2>
                    <p className="text-gray-400 mt-1">
                      Showing results for "{searchQuery}"
                    </p>
                  </div>
                  
                  {/* TODO: Add sort options */}
                  <div className="hidden sm:block">
                    <select className="input-steam text-sm">
                      <option>Sort by Relevance</option>
                      <option>Sort by Price (Low to High)</option>
                      <option>Sort by Price (High to Low)</option>
                      <option>Sort by Rating</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Search Results */}
            <SearchResults
              results={results}
              isLoading={isLoading}
              error={error}
              query={searchQuery}
              onRetry={() => performSearch(searchQuery, filters, currentPage)}
            />

            {/* Pagination */}
            {showPagination && hasResults && (
              <div className="mt-8 flex justify-center">
                <nav className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-3 py-2 text-sm bg-steam-blue border border-steam-blue-light rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-steam-blue-light"
                  >
                    Previous
                  </button>
                  
                  {/* Page numbers */}
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const page = i + 1;
                    return (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`px-3 py-2 text-sm border rounded ${
                          page === currentPage
                            ? 'bg-steam-green border-steam-green text-white'
                            : 'bg-steam-blue border-steam-blue-light text-gray-300 hover:bg-steam-blue-light'
                        }`}
                      >
                        {page}
                      </button>
                    );
                  })}
                  
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="px-3 py-2 text-sm bg-steam-blue border border-steam-blue-light rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-steam-blue-light"
                  >
                    Next
                  </button>
                </nav>
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

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

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import MainLayout from '@/components/Layout/MainLayout';
import SearchBox from '@/components/Search/SearchBox';
import SearchResults from '@/components/Search/SearchResults';
import { GameResult } from '@/types/api';
import { SEARCH_LIMITS } from '@/constants/api';
import { simpleSearch, semanticSearch, hybridSearch, exportSearchResultsCSV, exportSearchResultsJSON, importGamesFromCSV, importGamesFromJSON } from '@/services/api';
import { exportSearchPreset, importSearchPreset, SearchPreset, savePresetToLocalStorage, loadPresetsFromLocalStorage } from '@/services/searchPresets';

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
  const [searchMode, setSearchMode] = useState<'bm25' | 'semantic' | 'hybrid'>('bm25'); // Phase 4: Search mode selector
  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [exportLimit, setExportLimit] = useState(100); // Export limit 1-100
  const presetInputRef = useRef<HTMLInputElement>(null);
  const [savedPresets, setSavedPresets] = useState<SearchPreset[]>([]);
  const [showPresetsMenu, setShowPresetsMenu] = useState(false);
  
  // Available genres (could be fetched from API in Phase 2)
  const availableGenres = [
    'Action', 'Adventure', 'RPG', 'Strategy', 'Simulation',
    'Sports', 'Racing', 'Indie', 'Casual', 'Puzzle'
  ];

  /**
   * Load games from API with current search/filter settings
   * Phase 4: Supports BM25, Semantic, and Hybrid search modes
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
      
      // Call appropriate search API based on search mode
      let response: any;
      if (searchMode === 'semantic') {
        // Semantic search: vector similarity
        response = await semanticSearch({
          query: searchQuery,
          filters: Object.keys(filters).length > 0 ? filters : undefined,
          offset,
          limit: SEARCH_LIMITS.DEFAULT_LIMIT
        });
      } else if (searchMode === 'hybrid') {
        // Hybrid search: BM25 + Semantic fusion
        response = await hybridSearch({
          query: searchQuery,
          filters: Object.keys(filters).length > 0 ? filters : undefined,
          sort_by: sortBy as any,
          offset,
          limit: SEARCH_LIMITS.DEFAULT_LIMIT
        }, 0.5); // alpha = 0.5 for balanced fusion
      } else {
        // BM25 search: keyword matching (default)
        response = await simpleSearch({
          query: searchQuery,
          filters: Object.keys(filters).length > 0 ? filters : undefined,
          sort_by: sortBy as any,
          offset,
          limit: SEARCH_LIMITS.DEFAULT_LIMIT
        });
      }
      
      // Transform backend response to frontend GameResult format
      const transformedGames = response.data.results.map((game: any) => ({
        id: game.game_id,
        title: game.title,
        score: game.similarity_score || game.fusion_score || game.bm25_score || game.relevance_score || 0,
        price: game.price,
        genres: game.genres || [],
        categories: game.categories || [],
        review_status: 'Mixed', // TODO: Get from backend in Phase 2
        deck_compatible: false, // TODO: Get from backend in Phase 2
        description: game.description || '',
        coop_type: game.coop_type,
        release_date: game.release_date,
        type: game.type || 'game',
        total_reviews: game.total_reviews || 0,
        bm25_score: game.bm25_score,
        similarity_score: game.similarity_score, // Phase 4: Semantic search score
        fusion_score: game.fusion_score, // Phase 4: Hybrid search score
        relevance_score: game.relevance_score, // Relevance score for display
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
   * Phase 4: Supports BM25, Semantic, and Hybrid search modes
   * 
   * @param mode - Search mode override (to avoid React state delay)
   */
  const loadGamesWithParams = async (
    query: string,
    priceMaxValue: number | undefined,
    genres: string[],
    type: string,
    sort: string,
    page: number,
    mode?: 'bm25' | 'semantic' | 'hybrid' // Optional mode override
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
      
      // Use provided mode or fall back to state (for backward compatibility)
      const currentMode = mode || searchMode;
      
      // Call appropriate search API based on search mode
      let response: any;
      if (currentMode === 'semantic') {
        // Semantic search: vector similarity
        response = await semanticSearch({
          query,
          filters: Object.keys(filters).length > 0 ? filters : undefined,
          offset,
          limit: SEARCH_LIMITS.DEFAULT_LIMIT
        });
      } else if (currentMode === 'hybrid') {
        // Hybrid search: BM25 + Semantic fusion
        response = await hybridSearch({
          query,
          filters: Object.keys(filters).length > 0 ? filters : undefined,
          sort_by: sort as any,
          offset,
          limit: SEARCH_LIMITS.DEFAULT_LIMIT
        }, 0.5); // alpha = 0.5 for balanced fusion
      } else {
        // BM25 search: keyword matching (default)
        response = await simpleSearch({
          query,
          filters: Object.keys(filters).length > 0 ? filters : undefined,
          sort_by: sort as any,
          offset,
          limit: SEARCH_LIMITS.DEFAULT_LIMIT
        });
      }
      
      // Transform backend response to frontend GameResult format
      const transformedGames = response.data.results.map((game: any) => ({
        id: game.game_id,
        title: game.title,
        score: game.similarity_score || game.fusion_score || game.bm25_score || game.relevance_score || 0,
        price: game.price,
        genres: game.genres || [],
        categories: game.categories || [],
        review_status: 'Mixed',
        deck_compatible: false,
        description: game.description || '',
        coop_type: game.coop_type,
        release_date: game.release_date,
        type: game.type || 'game',
        total_reviews: game.total_reviews || 0,
        bm25_score: game.bm25_score,
        similarity_score: game.similarity_score, // Phase 4: Semantic search score
        fusion_score: game.fusion_score, // Phase 4: Hybrid search score
        relevance_score: game.relevance_score, // Relevance score for display
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
   * Load saved presets on mount
   */
  useEffect(() => {
    setSavedPresets(loadPresetsFromLocalStorage());
  }, []);

  /**
   * Export current search preset
   */
  const handleExportSearchPreset = () => {
    try {
      const presetName = prompt('Enter a name for this search preset:', 
        `My ${selectedGenres.join('+')} Search`);
      
      if (presetName === null) return; // User cancelled
      
      exportSearchPreset(
        searchQuery,
        {
          genres: selectedGenres,
          priceMax: priceMax,
          gameType: gameType,
        },
        sortBy,
        presetName || undefined
      );
      
      alert('✅ Search preset exported successfully!');
    } catch (error) {
      console.error('Export preset failed:', error);
      alert('❌ Failed to export preset. Please try again.');
    }
  };

  /**
   * Import and apply search preset
   */
  const handleImportSearchPreset = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    try {
      const preset = await importSearchPreset(file);
      
      // Apply the preset to current search state
      setSearchQuery(preset.query);
      setSelectedGenres(preset.filters.genres || []);
      setPriceMax(preset.filters.price_max ? preset.filters.price_max / 100 : undefined);
      setGameType(preset.filters.type || '');
      setSortBy(preset.sort_by);
      setCurrentPage(1);
      
      // Save to localStorage
      savePresetToLocalStorage(preset);
      setSavedPresets(loadPresetsFromLocalStorage());
      
      // Execute search with imported preset
      await loadGamesWithParams(
        preset.query,
        preset.filters.price_max ? preset.filters.price_max / 100 : undefined,
        preset.filters.genres || [],
        preset.filters.type || '',
        preset.sort_by,
        1
      );
      
      alert(`✅ Loaded preset: "${preset.name}"\nExecuting search...`);
    } catch (error: any) {
      console.error('Import preset failed:', error);
      alert(`❌ Import failed: ${error.message || 'Please try again.'}`);
    } finally {
      setIsImporting(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  /**
   * Apply a saved preset from localStorage
   */
  const handleApplySavedPreset = async (preset: SearchPreset) => {
    try {
      // Apply the preset
      setSearchQuery(preset.query);
      setSelectedGenres(preset.filters.genres || []);
      setPriceMax(preset.filters.price_max ? preset.filters.price_max / 100 : undefined);
      setGameType(preset.filters.type || '');
      setSortBy(preset.sort_by);
      setCurrentPage(1);
      setShowPresetsMenu(false);
      
      // Execute search
      await loadGamesWithParams(
        preset.query,
        preset.filters.price_max ? preset.filters.price_max / 100 : undefined,
        preset.filters.genres || [],
        preset.filters.type || '',
        preset.sort_by,
        1
      );
      
      alert(`✅ Applied preset: "${preset.name}"`);
    } catch (error) {
      console.error('Apply preset failed:', error);
      alert('❌ Failed to apply preset.');
    }
  };

  /**
   * Handle export to CSV
   */
  const handleExportCSV = async () => {
    setIsExporting(true);
    try {
      // Build filters object, only include if there are actual filters
      let filters: any = null;
      if (priceMax !== undefined && priceMax > 0) {
        filters = filters || {};
        filters.price_max = priceMax * 100; // Convert to cents
      }
      if (selectedGenres.length > 0) {
        filters = filters || {};
        filters.genres = selectedGenres;
      }
      if (gameType) {
        filters = filters || {};
        filters.type = gameType;
      }
      
      await exportSearchResultsCSV({
        query: searchQuery || '',  // Ensure it's a string
        filters: filters,  // Pass null if no filters
        sort_by: sortBy as any,
        offset: 0,
        limit: exportLimit, // User-defined export limit (1-100)
      });
      
      // Show success message (could use a toast notification)
      alert('✅ CSV file downloaded successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      alert('❌ Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  /**
   * Handle export to JSON
   */
  const handleExportJSON = async () => {
    setIsExporting(true);
    try {
      // Build filters object, only include if there are actual filters
      let filters: any = null;
      if (priceMax !== undefined && priceMax > 0) {
        filters = filters || {};
        filters.price_max = priceMax * 100; // Convert to cents
      }
      if (selectedGenres.length > 0) {
        filters = filters || {};
        filters.genres = selectedGenres;
      }
      if (gameType) {
        filters = filters || {};
        filters.type = gameType;
      }
      
      await exportSearchResultsJSON({
        query: searchQuery || '',  // Ensure it's a string
        filters: filters,  // Pass null if no filters
        sort_by: sortBy as any,
        offset: 0,
        limit: exportLimit, // User-defined export limit (1-100)
      });
      
      // Show success message (could use a toast notification)
      alert('✅ JSON file downloaded successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      alert('❌ Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  // Removed old import functions - replaced by search preset import

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
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
                <div>
                  <h2 className="text-xl font-semibold text-white">
                    {searchQuery ? `Results for "${searchQuery}"` : 'All Games'}
                    {totalGames > 0 && (
                      <span className="text-gray-300 font-normal ml-2">
                        ({totalGames.toLocaleString()} found)
                      </span>
                    )}
                  </h2>
                  {/* Phase 4: Display current search mode */}
                  {searchQuery && (
                    <div className="mt-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-steam-blue-light text-steam-green border border-steam-green">
                        {searchMode === 'bm25' && '🔍 BM25 (Keyword Matching)'}
                        {searchMode === 'semantic' && '🧠 Semantic (Meaning Matching)'}
                        {searchMode === 'hybrid' && '🔀 Hybrid (BM25 + Semantic)'}
                      </span>
                    </div>
                  )}
                </div>
                
                {/* Controls Row */}
                <div className="flex items-center gap-3 flex-wrap">
                  {/* Phase 4: Search Mode Selector */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Search Mode</label>
                    <select
                      value={searchMode}
                      onChange={(e) => {
                        const newMode = e.target.value as 'bm25' | 'semantic' | 'hybrid';
                        setSearchMode(newMode);
                        setCurrentPage(1);
                        // Trigger search with new mode (pass mode directly to avoid React state delay)
                        loadGamesWithParams(searchQuery, priceMax, selectedGenres, gameType, sortBy, 1, newMode);
                      }}
                      className="px-3 py-2 bg-steam-blue border border-steam-blue-light rounded text-white text-sm focus:outline-none focus:border-steam-green"
                      title="Select search algorithm: BM25 (keywords), Semantic (meaning), or Hybrid (both)"
                    >
                      <option value="bm25">BM25 (Keywords)</option>
                      <option value="semantic">Semantic (Meaning)</option>
                      <option value="hybrid">Hybrid (Both)</option>
                    </select>
                  </div>
                  
                  {/* Sort Dropdown */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Sort By</label>
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
                      <option value="name_desc">Name (Z-A)</option>
                    </select>
                  </div>
                </div>
              </div>
              
              {/* Search Preset & Export Buttons */}
              <div className="flex items-center gap-4">
                {/* Search Preset Controls */}
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-400">Search Presets:</span>
                  
                  {/* Export Current Search */}
                  <button
                    onClick={handleExportSearchPreset}
                    disabled={isLoading}
                    className="px-3 py-2 bg-indigo-600 border border-indigo-500 rounded text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    title="Save current search settings"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                    </svg>
                    Save Search
                  </button>
                  
                  {/* Import Search Preset */}
                  <input
                    ref={presetInputRef}
                    type="file"
                    accept=".json"
                    onChange={handleImportSearchPreset}
                    className="hidden"
                  />
                  <button
                    onClick={() => presetInputRef.current?.click()}
                    disabled={isImporting || isLoading}
                    className="px-3 py-2 bg-indigo-600 border border-indigo-500 rounded text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    title="Load saved search settings"
                  >
                    {isImporting ? (
                      <>
                        <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Loading...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                        </svg>
                        Load Search
                      </>
                    )}
                  </button>
                  
                  {/* Recent Presets Dropdown */}
                  {savedPresets.length > 0 && (
                    <div className="relative">
                      <button
                        onClick={() => setShowPresetsMenu(!showPresetsMenu)}
                        className="px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm font-medium hover:bg-gray-600 transition-colors flex items-center gap-2"
                        title="Quick access to recent searches"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Recent ({savedPresets.length})
                      </button>
                      
                      {showPresetsMenu && (
                        <div className="absolute right-0 mt-2 w-80 bg-[#1b2838] border border-steam-blue-light rounded-md shadow-2xl z-20 max-h-96 overflow-y-auto">
                          <div className="p-2 bg-[#1b2838]">
                            <div className="text-xs text-gray-400 px-2 py-1 border-b border-gray-700 mb-2 bg-[#16202d]">
                              Recent Search Presets
                            </div>
                            {savedPresets.slice().reverse().map((preset, idx) => (
                              <button
                                key={preset.timestamp}
                                onClick={() => handleApplySavedPreset(preset)}
                                className="w-full text-left px-3 py-2 text-sm text-gray-300 bg-[#16202d] hover:bg-[#2a475e] rounded mb-1 transition-colors"
                              >
                                <div className="font-medium text-white">{preset.name}</div>
                                <div className="text-xs text-gray-400 mt-1">{preset.description}</div>
                                <div className="text-xs text-gray-500 mt-1">
                                  {new Date(preset.timestamp).toLocaleString()}
                                </div>
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Export Game List Buttons */}
                {hasGames && (
                  <div className="flex items-center gap-3 border-l border-gray-700 pl-4">
                    <span className="text-sm text-gray-400">Export game list:</span>
                    
                    {/* Export Limit Selector */}
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-gray-400">Limit:</label>
                      <input
                        type="number"
                        min="1"
                        max="100"
                        value={exportLimit}
                        onChange={(e) => {
                          const val = parseInt(e.target.value);
                          if (val >= 1 && val <= 100) {
                            setExportLimit(val);
                          }
                        }}
                        className="w-16 px-2 py-1 bg-steam-dark border border-steam-blue-light rounded text-white text-sm text-center focus:outline-none focus:border-steam-green"
                      />
                    </div>
                    
                    <button
                      onClick={handleExportCSV}
                      disabled={isExporting || isLoading}
                      className="px-4 py-2 bg-steam-green border border-steam-green-light rounded text-white text-sm font-medium hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    >
                    {isExporting ? (
                      <>
                        <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Exporting...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Export CSV
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleExportJSON}
                    disabled={isExporting || isLoading}
                    className="px-4 py-2 bg-steam-blue border border-steam-blue-light rounded text-white text-sm font-medium hover:bg-steam-blue-light disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                  >
                    {isExporting ? (
                      <>
                        <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Exporting...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Export JSON
                      </>
                    )}
                  </button>
                </div>
                )}
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

/**
 * Function Search Component
 * 
 * This component provides search and filtering capabilities for the function library.
 * It includes text search, category filtering, and sorting options to help users
 * quickly find the functions they need.
 */

import React from 'react';

interface FunctionSearchProps {
  /** Current search query */
  searchQuery: string;
  /** Callback when search query changes */
  onSearchChange: (query: string) => void;
  /** Currently selected category */
  selectedCategory: string;
  /** Callback when category selection changes */
  onCategoryChange: (category: string) => void;
  /** Available categories */
  categories: string[];
  /** Whether search is disabled (e.g., during loading) */
  isLoading?: boolean;
}

/**
 * Function Search Component
 * 
 * Features:
 * - Real-time text search across function names, descriptions, and tags
 * - Category filtering dropdown
 * - Clear search functionality
 * - Search statistics display
 * - Keyboard shortcuts support
 */
export default function FunctionSearch({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  categories,
  isLoading = false,
}: FunctionSearchProps) {
  /**
   * Handle search input change
   */
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onSearchChange(e.target.value);
  };

  /**
   * Handle category selection change
   */
  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onCategoryChange(e.target.value);
  };

  /**
   * Clear all filters
   */
  const clearFilters = () => {
    onSearchChange('');
    onCategoryChange('all');
  };

  /**
   * Handle keyboard shortcuts
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const searchInput = e.currentTarget as HTMLInputElement;
      searchInput.focus();
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
      onSearchChange('');
    }
  };

  /**
   * Check if any filters are active
   */
  const hasActiveFilters = searchQuery.trim() !== '' || selectedCategory !== 'all';

  /**
   * Format category name for display
   */
  const formatCategoryName = (category: string) => {
    if (category === 'all') return 'All Categories';
    return category;
  };

  return (
    <div className="bg-steam-blue border border-steam-blue-light rounded-steam p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">
          Search Functions
        </h2>
        
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            disabled={isLoading}
            className="text-sm text-steam-green hover:text-steam-green-light disabled:opacity-50 transition-colors"
          >
            Clear Filters
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Search Input */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            onKeyDown={handleKeyDown}
            placeholder="Search functions by name, description, or tags..."
            disabled={isLoading}
            className={`
              input-steam w-full pl-10 pr-4 py-3
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          />
          
          {/* Clear search button */}
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-white transition-colors"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Filters Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Category
            </label>
            <select
              value={selectedCategory}
              onChange={handleCategoryChange}
              disabled={isLoading}
              className={`
                input-steam w-full
                ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {formatCategoryName(category)}
                </option>
              ))}
            </select>
          </div>

          {/* Complexity Filter - TODO: Implement */}
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Complexity
            </label>
            <select
              disabled={true}
              className="input-steam w-full opacity-50 cursor-not-allowed"
            >
              <option>All Levels (Coming Soon)</option>
            </select>
          </div>

          {/* Sort Options - TODO: Implement */}
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Sort By
            </label>
            <select
              disabled={true}
              className="input-steam w-full opacity-50 cursor-not-allowed"
            >
              <option>Relevance (Coming Soon)</option>
            </select>
          </div>
        </div>

        {/* Search Tips */}
        <div className="bg-steam-blue-dark p-4 rounded border border-steam-blue-light">
          <h3 className="text-sm font-medium text-white mb-2">Search Tips</h3>
          <ul className="text-xs text-gray-300 space-y-1">
            <li>• Use <kbd className="px-1 py-0.5 bg-steam-blue-light rounded text-xs">Ctrl+K</kbd> to quickly focus the search box</li>
            <li>• Search by function name, description, or tags</li>
            <li>• Use category filters to narrow down results</li>
            <li>• Press <kbd className="px-1 py-0.5 bg-steam-blue-light rounded text-xs">Esc</kbd> to clear the search</li>
          </ul>
        </div>

        {/* Active Filters Summary */}
        {hasActiveFilters && (
          <div className="flex flex-wrap items-center gap-2 pt-2">
            <span className="text-sm text-gray-400">Active filters:</span>
            
            {searchQuery && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-steam-green bg-opacity-20 text-steam-green text-xs rounded">
                Search: "{searchQuery}"
                <button
                  onClick={() => onSearchChange('')}
                  className="hover:text-steam-green-light"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            )}
            
            {selectedCategory !== 'all' && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-steam-green bg-opacity-20 text-steam-green text-xs rounded">
                Category: {formatCategoryName(selectedCategory)}
                <button
                  onClick={() => onCategoryChange('all')}
                  className="hover:text-steam-green-light"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

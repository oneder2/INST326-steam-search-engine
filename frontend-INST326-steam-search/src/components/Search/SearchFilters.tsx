/**
 * Search Filters Component
 * 
 * This component provides advanced filtering options for game search.
 * It includes filters for price, platform, co-op type, and other game attributes
 * as defined in the API contract.
 */

import React from 'react';
import { SearchFilters as SearchFiltersType, CoopType, Platform } from '@/types/api';
import { PRICE_RANGES, COOP_TYPES, PLATFORMS } from '@/constants/api';

interface SearchFiltersProps {
  /** Current filter values */
  filters: SearchFiltersType;
  /** Callback when filters change */
  onFiltersChange: (filters: SearchFiltersType) => void;
  /** Whether filters are disabled (e.g., during loading) */
  disabled?: boolean;
}

/**
 * Search Filters Component
 * 
 * Provides a comprehensive set of filters for game search including:
 * - Price range selection
 * - Platform compatibility
 * - Co-op type preferences
 * - Steam Deck compatibility
 */
export default function SearchFilters({
  filters,
  onFiltersChange,
  disabled = false,
}: SearchFiltersProps) {
  /**
   * Update a specific filter value
   */
  const updateFilter = <K extends keyof SearchFiltersType>(
    key: K,
    value: SearchFiltersType[K]
  ) => {
    const newFilters = { ...filters };

    // Handle different types of empty values
    if (value === undefined || value === null) {
      delete newFilters[key];
    } else if (typeof value === 'string' && value === '') {
      delete newFilters[key];
    } else if (Array.isArray(value) && value.length === 0) {
      delete newFilters[key];
    } else {
      newFilters[key] = value;
    }

    onFiltersChange(newFilters);
  };

  /**
   * Handle platform selection (multiple selection)
   */
  const handlePlatformChange = (platform: Platform, checked: boolean) => {
    const currentPlatforms = filters.platform || [];
    let newPlatforms: Platform[];
    
    if (checked) {
      newPlatforms = [...currentPlatforms, platform];
    } else {
      newPlatforms = currentPlatforms.filter(p => p !== platform);
    }
    
    updateFilter('platform', newPlatforms.length > 0 ? newPlatforms : undefined);
  };

  /**
   * Clear all filters
   */
  const clearAllFilters = () => {
    onFiltersChange({});
  };

  /**
   * Check if any filters are active
   */
  const hasActiveFilters = Object.keys(filters).length > 0;

  return (
    <div className="bg-steam-blue border border-steam-blue-light rounded-steam p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            disabled={disabled}
            className="text-sm text-steam-green hover:text-steam-green-light disabled:opacity-50"
          >
            Clear All
          </button>
        )}
      </div>

      <div className="space-y-6">
        {/* Price Filter */}
        <div>
          <label className="block text-sm font-medium text-white mb-3">
            Price Range
          </label>
          <div className="space-y-2">
            {PRICE_RANGES.map((range) => (
              <label key={`${range.min}-${range.max}`} className="flex items-center">
                <input
                  type="radio"
                  name="priceRange"
                  value={range.max}
                  checked={filters.price_max === range.max}
                  onChange={(e) => updateFilter('price_max', parseInt(e.target.value, 10))}
                  disabled={disabled}
                  className="mr-2 text-steam-green focus:ring-steam-green"
                />
                <span className="text-gray-300 text-sm">{range.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Co-op Type Filter */}
        <div>
          <label className="block text-sm font-medium text-white mb-3">
            Multiplayer Type
          </label>
          <select
            value={filters.coop_type || ''}
            onChange={(e) => updateFilter('coop_type', e.target.value as CoopType || undefined)}
            disabled={disabled}
            className="input-steam w-full text-sm"
          >
            <option value="">Any</option>
            {COOP_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Platform Filter */}
        <div>
          <label className="block text-sm font-medium text-white mb-3">
            Platform Compatibility
          </label>
          <div className="space-y-2">
            {PLATFORMS.map((platform) => (
              <label key={platform.value} className="flex items-center">
                <input
                  type="checkbox"
                  checked={(filters.platform || []).includes(platform.value as Platform)}
                  onChange={(e) => handlePlatformChange(platform.value as Platform, e.target.checked)}
                  disabled={disabled}
                  className="mr-2 text-steam-green focus:ring-steam-green rounded"
                />
                <span className="text-gray-300 text-sm">{platform.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Steam Deck Compatibility */}
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.platform?.includes(Platform.STEAM_DECK) || false}
              onChange={(e) => handlePlatformChange(Platform.STEAM_DECK, e.target.checked)}
              disabled={disabled}
              className="mr-2 text-steam-green focus:ring-steam-green rounded"
            />
            <span className="text-white text-sm font-medium">Steam Deck Compatible</span>
          </label>
          <p className="text-xs text-gray-400 mt-1 ml-6">
            Show only games verified for Steam Deck
          </p>
        </div>

        {/* TODO: Add more filters as needed */}
        {/* Genre Filter */}
        <div>
          <label className="block text-sm font-medium text-white mb-3">
            Genre (Coming Soon)
          </label>
          <div className="text-sm text-gray-400">
            Genre filtering will be available in a future update
          </div>
        </div>

        {/* Release Date Filter */}
        <div>
          <label className="block text-sm font-medium text-white mb-3">
            Release Date (Coming Soon)
          </label>
          <div className="text-sm text-gray-400">
            Filter by release date coming soon
          </div>
        </div>
      </div>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="mt-6 pt-6 border-t border-steam-blue-light">
          <h4 className="text-sm font-medium text-white mb-2">Active Filters:</h4>
          <div className="space-y-1">
            {filters.price_max !== undefined && (
              <div className="text-xs text-gray-300">
                Price: {PRICE_RANGES.find(r => r.max === filters.price_max)?.label}
              </div>
            )}
            {filters.coop_type && (
              <div className="text-xs text-gray-300">
                Co-op: {COOP_TYPES.find(t => t.value === filters.coop_type)?.label}
              </div>
            )}
            {filters.platform && filters.platform.length > 0 && (
              <div className="text-xs text-gray-300">
                Platforms: {filters.platform.map(p => 
                  PLATFORMS.find(pl => pl.value === p)?.label
                ).join(', ')}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Search Box Component
 * 
 * A reusable search input component with suggestions, validation,
 * and different size variants. Used throughout the application
 * for game search functionality.
 */

import React, { useState, useEffect, useRef } from 'react';
import { UI_CONFIG, SEARCH_LIMITS } from '@/constants/api';
import { getSearchSuggestions } from '@/services/api';

interface SearchBoxProps {
  /** Current search value */
  value: string;
  /** Callback when value changes */
  onChange: (value: string) => void;
  /** Callback when search is submitted */
  onSearch: (query: string) => void;
  /** Placeholder text */
  placeholder?: string;
  /** Size variant */
  size?: 'small' | 'medium' | 'large';
  /** Whether to show search suggestions */
  showSuggestions?: boolean;
  /** Custom CSS classes */
  className?: string;
  /** Whether the input is disabled */
  disabled?: boolean;
  /** Whether to auto-focus the input */
  autoFocus?: boolean;
}

/**
 * Search Box Component
 * 
 * Features:
 * - Real-time search suggestions (when enabled)
 * - Keyboard navigation for suggestions
 * - Input validation and character limits
 * - Multiple size variants
 * - Debounced suggestion fetching
 */
export default function SearchBox({
  value,
  onChange,
  onSearch,
  placeholder = 'Search for games...',
  size = 'medium',
  showSuggestions = true,
  className = '',
  disabled = false,
  autoFocus = false,
}: SearchBoxProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestionsList, setShowSuggestionsList] = useState(false);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout>();

  /**
   * Get size-specific CSS classes
   */
  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return 'px-3 py-2 text-sm';
      case 'large':
        return 'px-6 py-4 text-lg';
      default:
        return 'px-4 py-3 text-base';
    }
  };

  /**
   * Handle input value change with validation
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    
    // Enforce character limit
    if (newValue.length <= SEARCH_LIMITS.MAX_QUERY_LENGTH) {
      onChange(newValue);
      
      // Fetch suggestions if enabled and value is long enough
      if (showSuggestions && newValue.length >= SEARCH_LIMITS.MIN_QUERY_LENGTH) {
        debouncedFetchSuggestions(newValue);
      } else {
        setSuggestions([]);
        setShowSuggestionsList(false);
      }
    }
  };

  /**
   * Debounced function to fetch search suggestions
   */
  const debouncedFetchSuggestions = (query: string) => {
    // Clear previous debounce
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Set new debounce
    debounceRef.current = setTimeout(async () => {
      if (query.trim().length >= SEARCH_LIMITS.MIN_QUERY_LENGTH) {
        setIsLoading(true);
        try {
          // TODO: Search suggestions API not yet implemented
          // Temporarily disable to prevent 404 errors
          // const response = await getSearchSuggestions(query);
          // setSuggestions(response.data.suggestions);
          setSuggestions([]);
          setShowSuggestionsList(false);
        } catch (error) {
          console.error('Failed to fetch suggestions:', error);
          setSuggestions([]);
        } finally {
          setIsLoading(false);
        }
      }
    }, UI_CONFIG.SUGGESTIONS_DEBOUNCE_DELAY);
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim() && !disabled) {
      onSearch(value.trim());
      setShowSuggestionsList(false);
    }
  };

  /**
   * Handle keyboard navigation
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestionsList || suggestions.length === 0) {
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        break;
      
      case 'ArrowUp':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        break;
      
      case 'Enter':
        if (selectedSuggestionIndex >= 0) {
          e.preventDefault();
          const selectedSuggestion = suggestions[selectedSuggestionIndex];
          onChange(selectedSuggestion);
          onSearch(selectedSuggestion);
          setShowSuggestionsList(false);
        }
        break;
      
      case 'Escape':
        setShowSuggestionsList(false);
        setSelectedSuggestionIndex(-1);
        break;
    }
  };

  /**
   * Handle suggestion click
   */
  const handleSuggestionClick = (suggestion: string) => {
    onChange(suggestion);
    onSearch(suggestion);
    setShowSuggestionsList(false);
  };

  /**
   * Handle input focus
   */
  const handleFocus = () => {
    if (suggestions.length > 0) {
      setShowSuggestionsList(true);
    }
  };

  /**
   * Handle input blur (with delay to allow suggestion clicks)
   */
  const handleBlur = () => {
    setTimeout(() => {
      setShowSuggestionsList(false);
      setSelectedSuggestionIndex(-1);
    }, 200);
  };

  // Cleanup debounce on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  return (
    <div className={`relative ${className}`}>
      <form onSubmit={handleSubmit} className="relative">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          disabled={disabled}
          autoFocus={autoFocus}
          className={`
            input-steam w-full pr-12 ${getSizeClasses()}
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
          maxLength={SEARCH_LIMITS.MAX_QUERY_LENGTH}
        />
        
        {/* Search Button */}
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className={`
            absolute right-2 top-1/2 transform -translate-y-1/2
            p-2 text-gray-400 hover:text-steam-green
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors duration-200
          `}
        >
          {isLoading ? (
            <div className="animate-spin w-5 h-5 border-2 border-gray-400 border-t-steam-green rounded-full" />
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          )}
        </button>
      </form>

      {/* Suggestions Dropdown */}
      {showSuggestionsList && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-1 bg-steam-blue border border-steam-blue-light rounded-steam shadow-steam max-h-60 overflow-y-auto"
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={suggestion}
              onClick={() => handleSuggestionClick(suggestion)}
              className={`
                w-full text-left px-4 py-2 hover:bg-steam-blue-light
                transition-colors duration-150
                ${index === selectedSuggestionIndex ? 'bg-steam-blue-light' : ''}
                ${index === 0 ? 'rounded-t-steam' : ''}
                ${index === suggestions.length - 1 ? 'rounded-b-steam' : ''}
              `}
            >
              <span className="text-white">{suggestion}</span>
            </button>
          ))}
        </div>
      )}

      {/* Character Count (for large inputs) */}
      {size === 'large' && value.length > SEARCH_LIMITS.MAX_QUERY_LENGTH * 0.8 && (
        <div className="absolute right-0 -bottom-6 text-xs text-gray-400">
          {value.length}/{SEARCH_LIMITS.MAX_QUERY_LENGTH}
        </div>
      )}
    </div>
  );
}

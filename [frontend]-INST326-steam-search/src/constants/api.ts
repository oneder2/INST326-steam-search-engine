/**
 * API Constants
 * 
 * This file contains all API-related constants including endpoints,
 * error codes, limits, and other configuration values used throughout
 * the application.
 */

// ============================================================================
// API Endpoints
// ============================================================================

export const API_ENDPOINTS = {
  // Core search endpoints
  SEARCH_GAMES: '/api/v1/search/games',
  SEARCH_SUGGEST: '/api/v1/search/suggest',
  
  // Game data endpoints
  GAME_DETAIL: '/api/v1/games',
  
  // Utility endpoints
  HEALTH: '/api/v1/health',
  VERSION: '/api/v1/version',
} as const;

// ============================================================================
// Error Codes (from API Contract Section 4.2)
// ============================================================================

export const ERROR_CODES = {
  // Client errors (4xx)
  VALIDATION_FAILED: 4001,
  RESOURCE_NOT_FOUND: 4004,
  RATE_LIMITED: 4290,
  
  // Server errors (5xx)
  INTERNAL_ERROR: 5000,
} as const;

export const HTTP_STATUS_CODES = {
  OK: 200,
  BAD_REQUEST: 400,
  NOT_FOUND: 404,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
} as const;

// ============================================================================
// Search Configuration
// ============================================================================

export const SEARCH_LIMITS = {
  /** Default number of results per page */
  DEFAULT_LIMIT: 20,
  /** Maximum number of results per page */
  MAX_LIMIT: 100,
  /** Minimum search query length */
  MIN_QUERY_LENGTH: 1,
  /** Maximum search query length */
  MAX_QUERY_LENGTH: 500,
} as const;

export const PAGINATION = {
  /** Default offset for pagination */
  DEFAULT_OFFSET: 0,
  /** Default page size */
  DEFAULT_PAGE_SIZE: 20,
} as const;

// ============================================================================
// Filter Options
// ============================================================================

export const PRICE_RANGES = [
  { label: 'Free', min: 0, max: 0 },
  { label: 'Under $5', min: 0, max: 5 },
  { label: '$5 - $15', min: 5, max: 15 },
  { label: '$15 - $30', min: 15, max: 30 },
  { label: '$30 - $60', min: 30, max: 60 },
  { label: 'Over $60', min: 60, max: 999 },
] as const;

export const COOP_TYPES = [
  { value: 'Local', label: 'Local Co-op' },
  { value: 'Online', label: 'Online Co-op' },
  { value: 'Both', label: 'Local & Online' },
  { value: 'None', label: 'Single Player' },
] as const;

export const PLATFORMS = [
  { value: 'Windows', label: 'Windows' },
  { value: 'SteamDeck', label: 'Steam Deck' },
  { value: 'Mac', label: 'macOS' },
  { value: 'Linux', label: 'Linux' },
] as const;

// ============================================================================
// Review Status Configuration
// ============================================================================

export const REVIEW_STATUS_CONFIG = {
  'Very Positive': {
    color: 'rating-very-positive',
    textColor: 'text-white',
    threshold: 0.9,
  },
  'Positive': {
    color: 'rating-positive',
    textColor: 'text-white',
    threshold: 0.7,
  },
  'Mixed': {
    color: 'rating-mixed',
    textColor: 'text-black',
    threshold: 0.5,
  },
  'Negative': {
    color: 'rating-negative',
    textColor: 'text-white',
    threshold: 0.3,
  },
  'Very Negative': {
    color: 'rating-very-negative',
    textColor: 'text-white',
    threshold: 0.0,
  },
} as const;

// ============================================================================
// Request Configuration
// ============================================================================

export const REQUEST_CONFIG = {
  /** Default request timeout in milliseconds */
  DEFAULT_TIMEOUT: 10000,
  /** Retry attempts for failed requests */
  RETRY_ATTEMPTS: 3,
  /** Delay between retry attempts in milliseconds */
  RETRY_DELAY: 1000,
} as const;

// ============================================================================
// Cache Configuration
// ============================================================================

export const CACHE_CONFIG = {
  /** Cache duration for search results in milliseconds */
  SEARCH_RESULTS_TTL: 5 * 60 * 1000, // 5 minutes
  /** Cache duration for game details in milliseconds */
  GAME_DETAILS_TTL: 30 * 60 * 1000, // 30 minutes
  /** Cache duration for search suggestions in milliseconds */
  SUGGESTIONS_TTL: 60 * 60 * 1000, // 1 hour
} as const;

// ============================================================================
// UI Configuration
// ============================================================================

export const UI_CONFIG = {
  /** Debounce delay for search input in milliseconds */
  SEARCH_DEBOUNCE_DELAY: 300,
  /** Debounce delay for suggestions in milliseconds */
  SUGGESTIONS_DEBOUNCE_DELAY: 200,
  /** Animation duration for transitions in milliseconds */
  ANIMATION_DURATION: 200,
} as const;

// ============================================================================
// Feature Flags
// ============================================================================

export const FEATURES = {
  /** Enable semantic search functionality */
  SEMANTIC_SEARCH: process.env.NEXT_PUBLIC_ENABLE_SEMANTIC_SEARCH === 'true',
  /** Enable advanced filtering options */
  ADVANCED_FILTERS: process.env.NEXT_PUBLIC_ENABLE_ADVANCED_FILTERS === 'true',
  /** Enable debug mode */
  DEBUG_MODE: process.env.NEXT_PUBLIC_DEBUG === 'true',
} as const;

// ============================================================================
// Validation Rules
// ============================================================================

export const VALIDATION = {
  /** Regular expression for valid search queries */
  SEARCH_QUERY_PATTERN: /^[a-zA-Z0-9\s\-_.,!?'"()]+$/,
  /** Maximum price value */
  MAX_PRICE: 999.99,
  /** Minimum price value */
  MIN_PRICE: 0,
} as const;

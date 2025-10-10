/**
 * API Types and Interfaces
 * 
 * This file contains TypeScript type definitions for all API requests and responses
 * based on the API contract documentation. These types ensure type safety when
 * communicating with the backend FastAPI service.
 * 
 * @see docs/技术文档/API 契约与后端实现文档.md
 */

// ============================================================================
// Core Data Models (Section 1 from API Contract)
// ============================================================================

/**
 * Game information entity - core metadata for Steam games
 * Stored in SQLite database
 */
export interface GameInfo {
  /** Steam game ID (Primary Key) */
  game_id: number;
  /** Game title */
  title: string;
  /** Game description */
  description: string;
  /** Game price in USD */
  price: number;
  /** Array of game genres */
  genres: string[];
  /** Cooperation type */
  coop_type: CoopType;
  /** Steam Deck compatibility */
  deck_comp: boolean;
}

/**
 * Search index data for BM25 and vector embeddings
 * Stored in Faiss/BM25 files
 */
export interface SearchIndex {
  /** Game ID reference */
  game_id: number;
  /** BM25 relevance score */
  bm25_score: number;
  /** Vector embedding for semantic search */
  vector_embedding: number[];
}

/**
 * Ranking metrics for fusion ranking algorithm
 */
export interface RankingMetrics {
  /** Review stability score */
  review_stability: number;
  /** Player activity score */
  player_activity: number;
}

/**
 * Standard error response structure
 * All API errors must return this structure
 */
export interface ErrorResponse {
  /** Error code for programmatic handling */
  error_code: number;
  /** Human-readable error message */
  message: string;
  /** Additional error details */
  details: string;
}

// ============================================================================
// Enums and Constants
// ============================================================================

/**
 * Cooperation types for multiplayer games
 */
export enum CoopType {
  LOCAL = 'Local',
  ONLINE = 'Online',
  BOTH = 'Both',
  NONE = 'None'
}

/**
 * Platform types for game compatibility
 */
export enum Platform {
  WINDOWS = 'Windows',
  STEAM_DECK = 'SteamDeck',
  MAC = 'Mac',
  LINUX = 'Linux'
}

/**
 * Review status based on review stability
 */
export enum ReviewStatus {
  VERY_POSITIVE = 'Very Positive',
  POSITIVE = 'Positive',
  MIXED = 'Mixed',
  NEGATIVE = 'Negative',
  VERY_NEGATIVE = 'Very Negative'
}

// ============================================================================
// API Request/Response Types (Section 3 from API Contract)
// ============================================================================

/**
 * Search query filters for game search
 */
export interface SearchFilters {
  /** Maximum price in USD */
  price_max?: number;
  /** Cooperation type filter */
  coop_type?: CoopType;
  /** Platform compatibility filter */
  platform?: Platform[];
}

/**
 * Request body for POST /api/v1/search/games
 */
export interface SearchQuerySchema {
  /** User search query text */
  query: string;
  /** Optional filters */
  filters?: SearchFilters;
  /** Result limit (max 100, default 20) */
  limit?: number;
  /** Pagination offset (default 0) */
  offset?: number;
}

/**
 * Individual game result in search response
 */
export interface GameResult {
  /** Steam game ID */
  id: number;
  /** Game title */
  title: string;
  /** Fusion ranking score (0.0 - 1.0) */
  score: number;
  /** Current price in USD */
  price: number;
  /** Game genres */
  genres: string[];
  /** Review status based on stability */
  review_status: ReviewStatus;
  /** Steam Deck compatibility */
  deck_compatible: boolean;
}

/**
 * Response for successful game search
 * Returns array of GameResult ordered by fusion ranking score (descending)
 */
export interface GameResultSchema {
  /** Array of game results */
  results: GameResult[];
  /** Total number of results available */
  total: number;
  /** Current page offset */
  offset: number;
  /** Number of results per page */
  limit: number;
  /** Search query that was executed */
  query: string;
  /** Applied filters */
  filters: SearchFilters;
}

/**
 * Response for search suggestions
 * GET /api/v1/search/suggest
 */
export interface SearchSuggestionsResponse {
  /** Array of suggested search terms */
  suggestions: string[];
  /** Input prefix that generated these suggestions */
  prefix: string;
}

/**
 * Detailed game information response
 * GET /api/v1/games/{game_id}
 */
export interface GameDetailResponse extends GameInfo {
  /** Additional ranking metrics */
  ranking_metrics: RankingMetrics;
  /** Full game description */
  full_description?: string;
  /** Game screenshots URLs */
  screenshots?: string[];
  /** Game trailer URL */
  trailer_url?: string;
  /** Release date */
  release_date?: string;
  /** Developer name */
  developer?: string;
  /** Publisher name */
  publisher?: string;
  /** Review status based on review stability */
  review_status?: string;
}

// ============================================================================
// API Client Types
// ============================================================================

/**
 * Configuration for API client
 */
export interface ApiConfig {
  /** Base URL for API endpoints */
  baseUrl: string;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Default headers */
  headers?: Record<string, string>;
}

/**
 * API response wrapper with metadata
 */
export interface ApiResponse<T> {
  /** Response data */
  data: T;
  /** HTTP status code */
  status: number;
  /** Response headers */
  headers: Record<string, string>;
  /** Request timestamp */
  timestamp: number;
}

/**
 * API error with additional context
 */
export interface ApiError extends Error {
  /** HTTP status code */
  status?: number;
  /** Error response from server */
  response?: ErrorResponse;
  /** Request that caused the error */
  request?: any;
}

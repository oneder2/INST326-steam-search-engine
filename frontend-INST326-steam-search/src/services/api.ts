/**
 * API Service Layer - FastAPI Backend Integration
 *
 * This module provides a centralized API client for communicating with the
 * Python FastAPI backend of the Steam Game Search Engine. It implements all
 * the endpoints defined in the API contract and provides type-safe methods
 * for frontend components.
 *
 * Backend Technology: Python FastAPI with SQLite, Faiss, and BM25
 *
 * @see docs/技术文档/API 契约与后端实现文档.md
 * @see docs/functions/backend/ - Python function documentation
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  ApiConfig,
  ApiResponse,
  ApiError,
  SearchQuerySchema,
  GameResultSchema,
  SearchSuggestionsResponse,
  GameDetailResponse,
  ErrorResponse,
} from '@/types/api';

/**
 * Default API configuration
 */
const DEFAULT_CONFIG: ApiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
};

/**
 * API Client Class
 * 
 * Provides methods for all API endpoints with proper error handling,
 * request/response transformation, and TypeScript type safety.
 */
export class ApiClient {
  private client: AxiosInstance;

  constructor(config: Partial<ApiConfig> = {}) {
    const finalConfig = { ...DEFAULT_CONFIG, ...config };
    
    this.client = axios.create({
      baseURL: finalConfig.baseUrl,
      timeout: finalConfig.timeout,
      headers: finalConfig.headers,
    });

    // Request interceptor for logging and authentication
    this.client.interceptors.request.use(
      (config) => {
        // TODO: Add authentication headers if needed
        // config.headers.Authorization = `Bearer ${token}`;
        
        if (process.env.NODE_ENV === 'development') {
          console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        }
        
        return config;
      },
      (error) => {
        return Promise.reject(this.handleError(error));
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        return Promise.reject(this.handleError(error));
      }
    );
  }

  /**
   * Handle API errors and transform them to ApiError format
   */
  private handleError(error: any): ApiError {
    const apiError: ApiError = new Error('API Error');
    
    if (error.response) {
      // Server responded with error status
      apiError.status = error.response.status;
      apiError.response = error.response.data as ErrorResponse;
      apiError.message = apiError.response?.message || 'Server Error';
    } else if (error.request) {
      // Request was made but no response received
      apiError.message = 'Network Error: No response from server';
      apiError.request = error.request;
    } else {
      // Something else happened
      apiError.message = error.message || 'Unknown Error';
    }

    return apiError;
  }

  /**
   * Transform axios response to ApiResponse format
   */
  private transformResponse<T>(response: AxiosResponse<T>): ApiResponse<T> {
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
      timestamp: Date.now(),
    };
  }

  // ========================================================================
  // Core API Methods
  // ========================================================================

  /**
   * Search for games using the unified search endpoint
   * POST /api/v1/search/games
   */
  async searchGames(query: SearchQuerySchema): Promise<ApiResponse<GameResultSchema>> {
    try {
      const response = await this.client.post<GameResultSchema>('/api/v1/search/games', query);
      return this.transformResponse(response);
    } catch (error) {
      throw error; // Error is already handled by interceptor
    }
  }

  /**
   * Get search suggestions based on input prefix
   * GET /api/v1/search/suggest
   */
  async getSearchSuggestions(prefix: string): Promise<ApiResponse<SearchSuggestionsResponse>> {
    try {
      const response = await this.client.get<SearchSuggestionsResponse>('/api/v1/search/suggest', {
        params: { prefix },
      });
      return this.transformResponse(response);
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get detailed information for a specific game
   * GET /api/v1/games/{game_id}
   */
  async getGameDetail(gameId: number): Promise<ApiResponse<GameDetailResponse>> {
    try {
      const response = await this.client.get<GameDetailResponse>(`/api/v1/games/${gameId}`);
      return this.transformResponse(response);
    } catch (error) {
      throw error;
    }
  }

  // ========================================================================
  // Utility Methods
  // ========================================================================

  /**
   * Check API health/status
   * GET /api/v1/health (assuming this endpoint exists)
   */
  async checkHealth(): Promise<ApiResponse<{ status: string; timestamp: number }>> {
    try {
      const response = await this.client.get('/api/v1/health');
      return this.transformResponse(response);
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get API version information
   * GET /api/v1/version (assuming this endpoint exists)
   */
  async getVersion(): Promise<ApiResponse<{ version: string; build: string }>> {
    try {
      const response = await this.client.get('/api/v1/version');
      return this.transformResponse(response);
    } catch (error) {
      throw error;
    }
  }
}

// ========================================================================
// Singleton Instance and Convenience Functions
// ========================================================================

/**
 * Default API client instance
 */
export const apiClient = new ApiClient();

/**
 * Convenience function for game search
 * Wraps the API client method for easier use in components
 */
export const searchGames = (query: SearchQuerySchema) => apiClient.searchGames(query);

/**
 * Convenience function for search suggestions
 */
export const getSearchSuggestions = (prefix: string) => apiClient.getSearchSuggestions(prefix);

/**
 * Convenience function for game details
 */
export const getGameDetail = (gameId: number) => apiClient.getGameDetail(gameId);

/**
 * Convenience function for API health check
 */
export const checkApiHealth = () => apiClient.checkHealth();

// Export the ApiClient class as default
export default ApiClient;

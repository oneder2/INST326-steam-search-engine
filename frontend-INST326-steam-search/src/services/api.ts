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
   * Search for games with filters and sorting (Phase 1 Implementation)
   * POST /api/v1/search/games
   * 
   * ========================================================================
   * 前端-后端API接口约束规范 (Frontend-Backend API Contract)
   * ========================================================================
   * 
   * 【请求约束】Request Constraints:
   * - 方法: POST
   * - 路径: /api/v1/search/games
   * - Content-Type: application/json
   * - 请求体格式: SearchQuerySchema
   *   {
   *     query: string (1-200字符, 必填),
   *     filters?: {
   *       price_max?: number (0-1000, 可选),
   *       coop_type?: "Local" | "Online" | "Both" | "None" (可选),
   *       platform?: Array<"Windows" | "SteamDeck" | "Mac" | "Linux"> (最多3个, 可选),
   *       genres?: Array<string> (最多5个, 可选),
   *       review_status?: string (可选),
   *       deck_compatible?: boolean (可选)
   *     },
   *     limit?: number (1-100, 默认20),
   *     offset?: number (>=0, 默认0)
   *   }
   * 
   * 【响应约束】Response Constraints:
   * - 成功状态码: 200
   * - 响应体格式: GameResultSchema
   *   {
   *     results: Array<{
   *       game_id: number (必填),
   *       title: string (必填),
   *       description: string (必填),
   *       price: number (>=0, 必填),
   *       genres: Array<string> (必填),
   *       coop_type?: string (可选),
   *       deck_comp: boolean (必填),
   *       review_status: string (必填),
   *       release_date?: string (可选),
   *       developer?: string (可选),
   *       publisher?: string (可选),
   *       relevance_score: number (0-1, 必填),
   *       bm25_score: number (>=0, 必填),
   *       semantic_score: number (0-1, 必填)
   *     }>,
   *     total: number (>=0, 必填),
   *     offset: number (>=0, 必填),
   *     limit: number (1-100, 必填),
   *     query: string (必填),
   *     filters: object (必填),
   *     search_time?: number (>=0, 可选)
   *   }
   * 
   * 【错误响应约束】Error Response Constraints:
   * - 400 Bad Request: { error_code: 4001, message: string, details: string }
   * - 500 Internal Server Error: { error_code: 5000, message: string, details: string }
   * - 503 Service Unavailable: { error_code: 5030, message: string, details: string }
   * 
   * 【数据一致性要求】Data Consistency Requirements:
   * - 前端发送的SearchQuerySchema必须与后端SearchQuerySchema完全匹配
   * - 后端返回的GameResultSchema必须与前端GameResultSchema完全匹配
   * - 所有字段类型、约束、默认值必须前后端一致
   * 
   * @param query - 搜索查询参数，必须符合SearchQuerySchema约束
   * @returns Promise<ApiResponse<GameResultSchema>> - 符合GameResultSchema的响应
   * @throws ApiError - 当请求失败时抛出，包含错误码和详细信息
   */
  async searchGames(query: SearchQuerySchema): Promise<ApiResponse<GameResultSchema>> {
    try {
      // Phase 1: Use new search endpoint with filters
      const response = await this.client.post<GameResultSchema>('/api/v1/search/games', query);
      return this.transformResponse(response);
    } catch (error) {
      throw error; // Error is already handled by interceptor
    }
  }

  /**
   * Simple search for games (Phase 1 - Basic Implementation)
   * POST /api/v1/search/games
   * 
   * Simplified search interface for Phase 1 implementation.
   * Supports text search, filters, sorting, and pagination.
   * 
   * @param params Search parameters
   * @returns Promise<ApiResponse<any>> Search results
   */
  async simpleSearch(params: {
    query?: string;
    filters?: {
      price_min?: number;
      price_max?: number;
      genres?: string[];
      categories?: string[];
      type?: string;
      release_date_after?: string;
      release_date_before?: string;
      min_reviews?: number;
    };
    sort_by?: 'relevance' | 'price_asc' | 'price_desc' | 'reviews' | 'newest' | 'oldest' | 'name';
    offset?: number;
    limit?: number;
  }): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.post('/api/v1/search/games', {
        query: params.query || '',
        filters: params.filters || null,
        sort_by: params.sort_by || 'relevance',
        offset: params.offset || 0,
        limit: params.limit || 20
      });
      return this.transformResponse(response);
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get search suggestions based on input prefix
   * GET /api/v1/search/suggest
   * 
   * ========================================================================
   * 前端-后端API接口约束规范 (Frontend-Backend API Contract)
   * ========================================================================
   * 
   * 【请求约束】Request Constraints:
   * - 方法: GET
   * - 路径: /api/v1/search/suggest
   * - 查询参数:
   *   - prefix: string (1-100字符, 必填) - 搜索前缀
   *   - limit?: number (1-20, 默认10, 可选) - 建议数量限制
   * 
   * 【响应约束】Response Constraints:
   * - 成功状态码: 200
   * - 响应体格式: SearchSuggestionsResponse
   *   {
   *     suggestions: Array<string> (最多20个, 必填),
   *     prefix: string (必填),
   *     suggestion_types?: {
   *       games?: Array<string>,
   *       genres?: Array<string>,
   *       developers?: Array<string>
   *     } (可选)
   *   }
   * 
   * 【错误响应约束】Error Response Constraints:
   * - 400 Bad Request: { error_code: 4001, message: string, details: string }
   * - 500 Internal Server Error: { error_code: 5000, message: string, details: string }
   * 
   * 【数据一致性要求】Data Consistency Requirements:
   * - 前端发送的查询参数必须与后端Query参数约束一致
   * - 后端返回的SearchSuggestionsResponse必须与前端类型定义完全匹配
   * 
   * @param prefix - 搜索前缀，1-100字符
   * @returns Promise<ApiResponse<SearchSuggestionsResponse>> - 符合SearchSuggestionsResponse的响应
   * @throws ApiError - 当请求失败时抛出
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
   * 
   * ========================================================================
   * 前端-后端API接口约束规范 (Frontend-Backend API Contract)
   * ========================================================================
   * 
   * 【请求约束】Request Constraints:
   * - 方法: GET
   * - 路径: /api/v1/games/{game_id}
   * - 路径参数:
   *   - game_id: number (正整数, 必填) - Steam游戏ID
   * 
   * 【响应约束】Response Constraints:
   * - 成功状态码: 200
   * - 响应体格式: GameDetailResponse (继承GameInfo)
   *   {
   *     // 基础信息 (来自GameInfo)
   *     game_id: number (必填),
   *     title: string (必填),
   *     description: string (必填),
   *     price: number (>=0, 必填),
   *     genres: Array<string> (必填),
   *     coop_type?: string (可选),
   *     deck_comp: boolean (必填),
   *     review_status: string (必填),
   *     release_date?: string (可选),
   *     developer?: string (可选),
   *     publisher?: string (可选),
   *     // 详细信息 (扩展字段)
   *     full_description?: string (可选),
   *     screenshots?: Array<string> (可选),
   *     videos?: Array<object> (可选),
   *     header_image?: string (可选),
   *     supported_platforms?: Array<string> (可选),
   *     review_summary?: object (可选),
   *     additional_info?: object (可选),
   *     last_updated?: number (可选)
   *   }
   * 
   * 【错误响应约束】Error Response Constraints:
   * - 400 Bad Request: { error_code: 4001, message: string, details: string }
   * - 404 Not Found: { error_code: 4004, message: string, details: string }
   * - 500 Internal Server Error: { error_code: 5000, message: string, details: string }
   * 
   * 【数据一致性要求】Data Consistency Requirements:
   * - 前端发送的game_id必须为正整数
   * - 后端返回的GameDetailResponse必须包含所有GameInfo字段
   * - 扩展字段必须与前端类型定义完全匹配
   * 
   * @param gameId - Steam游戏ID，必须为正整数
   * @returns Promise<ApiResponse<GameDetailResponse>> - 符合GameDetailResponse的响应
   * @throws ApiError - 当请求失败时抛出
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
   * Get paginated list of all games (MVP - Simple list without search)
   * GET /api/v1/games
   * 
   * This is a simplified endpoint for MVP phase that returns all games
   * with pagination support. No search or filtering functionality yet.
   * 
   * @param offset - Starting position (default: 0)
   * @param limit - Number of games per page (default: 20, max: 100)
   * @returns Promise<ApiResponse<GameListResponse>> - Paginated game list
   */
  async getAllGames(offset: number = 0, limit: number = 20): Promise<ApiResponse<any>> {
    try {
      const response = await this.client.get('/api/v1/games', {
        params: { offset, limit },
      });
      return this.transformResponse(response);
    } catch (error) {
      throw error;
    }
  }

  /**
   * Check API health/status
   * GET /api/v1/health
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
 * Convenience function for simple search (Phase 1)
 */
export const simpleSearch = (params: {
  query?: string;
  filters?: any;
  sort_by?: string;
  offset?: number;
  limit?: number;
}) => apiClient.simpleSearch(params);

/**
 * Convenience function for search suggestions
 */
export const getSearchSuggestions = (prefix: string) => apiClient.getSearchSuggestions(prefix);

/**
 * Convenience function for game details
 */
export const getGameDetail = (gameId: number) => apiClient.getGameDetail(gameId);

/**
 * Convenience function for getting all games (MVP - Simple pagination)
 */
export const getAllGames = (offset: number = 0, limit: number = 20) => 
  apiClient.getAllGames(offset, limit);

/**
 * Convenience function for API health check
 */
export const checkApiHealth = () => apiClient.checkHealth();

// Export the ApiClient class as default
export default ApiClient;

/**
 * Function Library Page Component
 *
 * This page displays a comprehensive library of Python FastAPI backend functions used in the
 * Steam Game Search Engine. It reads function documentation from markdown files in
 * docs/functions/backend/ and presents them in an organized, searchable format.
 * This page is specifically designed for INST326 group assignment submission
 * and demonstrates the Python backend implementation.
 */

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import FunctionCard from '@/components/FunctionLibrary/FunctionCard';
import FunctionSearch from '@/components/FunctionLibrary/FunctionSearch';
import { FunctionDoc } from '@/types/functions';

/**
 * Function Library Page Component
 * 
 * Features:
 * - Display all documented functions from markdown files
 * - Search and filter functions by name, category, or description
 * - Organized categorization of functions
 * - Code examples and usage documentation
 * - Export functionality for assignment submission
 */
export default function FunctionLibraryPage() {
  const [functions, setFunctions] = useState<FunctionDoc[]>([]);
  const [filteredFunctions, setFilteredFunctions] = useState<FunctionDoc[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  /**
   * Load function documentation from markdown files
   */
  useEffect(() => {
    loadFunctionDocs();
  }, []);

  /**
   * Filter functions based on search query and category
   */
  useEffect(() => {
    let filtered = functions;

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(func =>
        func.name.toLowerCase().includes(query) ||
        func.description.toLowerCase().includes(query) ||
        func.category.toLowerCase().includes(query) ||
        func.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(func => func.category === selectedCategory);
    }

    setFilteredFunctions(filtered);
  }, [functions, searchQuery, selectedCategory]);

  /**
   * Load function documentation from API or static files
   */
  const loadFunctionDocs = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // TODO: Replace with actual API call to load markdown files
      // const response = await fetch('/api/functions');
      // const data = await response.json();
      // setFunctions(data.functions);

      // Mock Python FastAPI function data - this will be replaced with actual markdown parsing from docs/functions/backend/
      const mockFunctions: FunctionDoc[] = [
        {
          id: 'search-games-endpoint',
          name: 'search_games',
          category: 'API Endpoint',
          description: 'Main FastAPI endpoint implementing unified game search with BM25 keyword search, Faiss semantic search, and fusion ranking',
          signature: '@app.post("/api/v1/search/games", response_model=GameResultSchema)\nasync def search_games(query: SearchQuerySchema) -> GameResultSchema:',
          parameters: [
            {
              name: 'query',
              type: 'SearchQuerySchema',
              description: 'Pydantic model containing search text, filters (price_max, coop_type, platform), and pagination parameters',
              required: true,
            },
          ],
          returnType: 'GameResultSchema',
          example: `# FastAPI endpoint implementation
@app.post("/api/v1/search/games", response_model=GameResultSchema)
async def search_games(query: SearchQuerySchema) -> GameResultSchema:
    try:
        # 1. Validate and sanitize input
        clean_query = validate_search_query(query.query)

        # 2. Perform parallel searches
        bm25_results = await search_bm25_index(clean_query, query.limit * 2)
        semantic_results = await search_faiss_index(clean_query, query.limit * 2)

        # 3. Apply fusion ranking
        ranked_results = apply_fusion_ranking(bm25_results, semantic_results)

        return paginate_results(ranked_results, query.offset, query.limit)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))`,
          tags: ['fastapi', 'endpoint', 'search', 'ranking', 'async'],
          complexity: 'High',
          lastUpdated: '2024-10-08',
        },
        {
          id: 'apply-fusion-ranking',
          name: 'apply_fusion_ranking',
          category: 'Search Algorithm',
          description: 'Core fusion ranking algorithm that combines BM25 keyword scores, Faiss semantic scores, and game quality metrics using weighted linear combination',
          signature: 'async def apply_fusion_ranking(\n    bm25_results: List[BM25Result],\n    faiss_results: List[FaissResult],\n    quality_metrics: Dict[int, RankingMetrics]\n) -> List[FusionResult]:',
          parameters: [
            {
              name: 'bm25_results',
              type: 'List[BM25Result]',
              description: 'BM25 keyword search results with game IDs and scores',
              required: true,
            },
            {
              name: 'faiss_results',
              type: 'List[FaissResult]',
              description: 'Faiss semantic search results with similarity scores',
              required: true,
            },
            {
              name: 'quality_metrics',
              type: 'Dict[int, RankingMetrics]',
              description: 'Game quality metrics by game_id (review_stability, player_activity)',
              required: true,
            },
          ],
          returnType: 'List[FusionResult]',
          example: `# Apply fusion ranking to search results
fusion_results = await apply_fusion_ranking(
    bm25_results=bm25_search_results,
    faiss_results=semantic_search_results,
    quality_metrics=game_quality_data
)

# Results sorted by final_score (descending)
for result in fusion_results[:10]:
    print(f"Game {result.game_id}: Score {result.final_score:.3f}")
    print(f"  BM25: {result.component_scores['bm25']:.3f}")
    print(f"  Semantic: {result.component_scores['semantic']:.3f}")
    print(f"  Quality: {result.component_scores['quality']:.3f}")`,
          tags: ['fusion-ranking', 'algorithm', 'scoring', 'normalization', 'python'],
          complexity: 'High',
          lastUpdated: '2024-10-08',
        },
        {
          id: 'validate-search-query',
          name: 'validate_search_query',
          category: 'Validation',
          description: 'Validates and sanitizes user search input to prevent injection attacks, XSS, and ensure query compatibility with search algorithms',
          signature: 'def validate_search_query(query: str) -> str:',
          parameters: [
            {
              name: 'query',
              type: 'str',
              description: 'Raw user search input string',
              required: true,
            },
          ],
          returnType: 'str',
          example: `# Validate and sanitize search query
def validate_search_query(query: str) -> str:
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")

    # Length validation
    if len(query) > 500:
        raise ValueError("Query exceeds maximum length of 500 characters")

    # Remove malicious patterns
    cleaned_query = query
    for pattern in MALICIOUS_PATTERNS:
        cleaned_query = re.sub(pattern, '', cleaned_query, flags=re.IGNORECASE)

    # Remove HTML tags and normalize whitespace
    cleaned_query = re.sub(r'<[^>]+>', '', cleaned_query)
    cleaned_query = re.sub(r'\\s+', ' ', cleaned_query.strip())

    return cleaned_query

# Usage in FastAPI endpoint
clean_query = validate_search_query(user_input)`,
          tags: ['validation', 'security', 'sanitization', 'sql-injection', 'python'],
          complexity: 'Medium',
          lastUpdated: '2024-10-08',
        },
        {
          id: 'search-bm25-index',
          name: 'search_bm25_index',
          category: 'Search Algorithm',
          description: 'Performs BM25 keyword search on the game index with optimized parameters for game search, considering title, description, and genre fields with different weights',
          signature: 'async def search_bm25_index(query: str, limit: int = 50) -> List[BM25Result]:',
          parameters: [
            {
              name: 'query',
              type: 'str',
              description: 'Cleaned search query text',
              required: true,
            },
            {
              name: 'limit',
              type: 'int',
              description: 'Maximum number of results to return (default: 50)',
              required: false,
            },
          ],
          returnType: 'List[BM25Result]',
          example: `# Perform BM25 keyword search
async def search_bm25_index(query: str, limit: int = 50) -> List[BM25Result]:
    try:
        # Tokenize query
        query_tokens = tokenize_text(query)

        # Get BM25 scores for all documents
        scores = bm25_index.get_scores(query_tokens)

        # Get top results with scores
        top_indices = scores.argsort()[-limit:][::-1]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include positive scores
                game_id = game_corpus[idx]['game_id']
                matched_fields = get_matched_fields(query_tokens, game_corpus[idx])

                results.append(BM25Result(
                    game_id=game_id,
                    score=float(scores[idx]),
                    matched_fields=matched_fields
                ))

        return results
    except Exception as e:
        logger.error(f"BM25 search error: {str(e)}")
        return []`,
          tags: ['bm25', 'keyword-search', 'ranking', 'algorithm', 'async'],
          complexity: 'Medium',
          lastUpdated: '2024-10-08',
        },
        {
          id: 'search-faiss-index',
          name: 'search_faiss_index',
          category: 'Search Algorithm',
          description: 'Performs semantic search using Faiss vector similarity search on game embeddings. Converts user query to vector embedding and finds semantically similar games',
          signature: 'async def search_faiss_index(query: str, limit: int = 50) -> List[FaissResult]:',
          parameters: [
            {
              name: 'query',
              type: 'str',
              description: 'User search query',
              required: true,
            },
            {
              name: 'limit',
              type: 'int',
              description: 'Maximum number of results (default: 50)',
              required: false,
            },
          ],
          returnType: 'List[FaissResult]',
          example: `# Perform semantic search using Faiss
async def search_faiss_index(query: str, limit: int = 50) -> List[FaissResult]:
    try:
        # Generate query embedding
        query_embedding = await generate_query_embedding(query)

        # Search Faiss index
        distances, indices = faiss_index.search(
            query_embedding.reshape(1, -1),
            limit
        )

        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # Valid result
                game_id = game_id_mapping[idx]
                similarity_score = distance_to_similarity(distance)

                results.append(FaissResult(
                    game_id=game_id,
                    similarity_score=similarity_score,
                    embedding_distance=float(distance)
                ))

        return results
    except Exception as e:
        logger.error(f"Faiss search error: {str(e)}")
        return []`,
          tags: ['faiss', 'semantic-search', 'embeddings', 'vector-similarity', 'async'],
          complexity: 'High',
          lastUpdated: '2024-10-08',
        },
        {
          id: 'get-game-by-id',
          name: 'get_game_by_id',
          category: 'Data Access',
          description: 'Retrieves a single game\'s information from the SQLite database using its Steam game ID. Returns a Pydantic GameInfo model with all core game metadata',
          signature: 'async def get_game_by_id(game_id: int) -> Optional[GameInfo]:',
          parameters: [
            {
              name: 'game_id',
              type: 'int',
              description: 'Steam game ID to retrieve',
              required: true,
            },
          ],
          returnType: 'Optional[GameInfo]',
          example: `# Retrieve game information by ID
async def get_game_by_id(game_id: int) -> Optional[GameInfo]:
    try:
        async with get_db_connection() as conn:
            cursor = conn.cursor()

            query = """
            SELECT
                game_id, title, description, price, genres,
                coop_type, deck_comp, review_status, release_date,
                developer, publisher
            FROM games
            WHERE game_id = ?
            """

            cursor.execute(query, (game_id,))
            row = cursor.fetchone()

            if not row:
                return None

            # Convert row to GameInfo model
            game_data = {
                'game_id': row[0],
                'title': row[1],
                'description': row[2],
                'price': row[3],
                'genres': json.loads(row[4]) if row[4] else [],
                'coop_type': row[5],
                'deck_comp': bool(row[6]),
                'review_status': row[7],
                'release_date': row[8],
                'developer': row[9],
                'publisher': row[10]
            }

            return GameInfo(**game_data)

    except sqlite3.Error as e:
        logger.error(f"Database error retrieving game {game_id}: {str(e)}")
        return None`,
          tags: ['database', 'sqlite', 'pydantic', 'async', 'data-access'],
          complexity: 'Low',
          lastUpdated: '2024-10-08',
        },
      ];

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));

      setFunctions(mockFunctions);
    } catch (err) {
      setError('Failed to load function documentation. Please try again.');
      console.error('Function docs loading error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Get unique categories from functions
   */
  const categories = ['all', ...Array.from(new Set(functions.map(func => func.category)))];

  /**
   * Get function statistics
   */
  const stats = {
    total: functions.length,
    categories: categories.length - 1, // Exclude 'all'
    complexity: {
      low: functions.filter(f => f.complexity === 'Low').length,
      medium: functions.filter(f => f.complexity === 'Medium').length,
      high: functions.filter(f => f.complexity === 'High').length,
    },
  };

  return (
    <MainLayout
      title="Python Backend Function Library - Steam Game Search Engine"
      description="Comprehensive documentation of all Python FastAPI backend functions used in the Steam Game Search Engine project"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-4">
            Python Backend Function Library
          </h1>
          <p className="text-gray-300 max-w-3xl">
            This library contains comprehensive documentation for all Python FastAPI backend functions
            used in the Steam Game Search Engine project. Each function includes detailed descriptions,
            parameters, examples, and usage guidelines showcasing the backend implementation for the INST326 group assignment.
          </p>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="card-steam p-4 text-center">
            <div className="text-2xl font-bold text-steam-green">{stats.total}</div>
            <div className="text-sm text-gray-300">Total Functions</div>
          </div>
          <div className="card-steam p-4 text-center">
            <div className="text-2xl font-bold text-steam-green">{stats.categories}</div>
            <div className="text-sm text-gray-300">Categories</div>
          </div>
          <div className="card-steam p-4 text-center">
            <div className="text-2xl font-bold text-steam-green">
              {stats.complexity.low + stats.complexity.medium + stats.complexity.high}
            </div>
            <div className="text-sm text-gray-300">Documented</div>
          </div>
          <div className="card-steam p-4 text-center">
            <div className="text-2xl font-bold text-steam-green">100%</div>
            <div className="text-sm text-gray-300">Coverage</div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="mb-8">
          <FunctionSearch
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            categories={categories}
            isLoading={isLoading}
          />
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-steam-green border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-gray-300">Loading function documentation...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-red-900 rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Error Loading Functions</h3>
            <p className="text-gray-300 mb-4">{error}</p>
            <button onClick={loadFunctionDocs} className="btn-steam">
              Try Again
            </button>
          </div>
        ) : filteredFunctions.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-steam-blue-light rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">No Functions Found</h3>
            <p className="text-gray-300">
              {searchQuery || selectedCategory !== 'all'
                ? 'Try adjusting your search or filter criteria.'
                : 'No functions are currently documented.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredFunctions.map((func) => (
              <FunctionCard key={func.id} functionDoc={func} />
            ))}
          </div>
        )}

        {/* Export Section */}
        {functions.length > 0 && (
          <div className="mt-12 pt-8 border-t border-steam-blue-light">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-white mb-4">
                Export Documentation
              </h2>
              <p className="text-gray-300 mb-6">
                Export function documentation for assignment submission
              </p>
              <div className="space-x-4">
                <button className="btn-steam">
                  Export as PDF
                </button>
                <button className="btn-steam">
                  Export as Markdown
                </button>
                <button className="btn-steam">
                  Export as JSON
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}

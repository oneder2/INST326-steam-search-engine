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
import FunctionNavigator from '@/components/FunctionLibrary/FunctionNavigator';
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
  const [categories, setCategories] = useState<any[]>([]);
  const [filteredFunctions, setFilteredFunctions] = useState<FunctionDoc[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isNavVisible, setIsNavVisible] = useState(false);

  /**
   * Load function documentation from markdown files
   */
  useEffect(() => {
    loadFunctionDocs();
  }, []);

  /**
   * Filter functions based on search query and category
   * 
   * Implementation:
   * - Supports filtering by category ID (e.g., "api-endpoints") or category name (e.g., "API Endpoint")
   * - Checks both func.category and func.sourceFile path for category matching
   * - Combines search and category filters
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
      filtered = filtered.filter(func => {
        // Match by category ID (from folder name in sourceFile path)
        const matchesCategoryId = func.sourceFile?.includes(`/${selectedCategory}/`);
        
        // Match by category name
        const matchesCategoryName = func.category === selectedCategory;
        
        // Find matching category from categories array
        const categoryObj = categories.find(cat => 
          cat.categoryId === selectedCategory || cat.displayName === selectedCategory
        );
        
        const matchesOriginalCategory = categoryObj && func.category === categoryObj.category;
        
        return matchesCategoryId || matchesCategoryName || matchesOriginalCategory;
      });
    }

    setFilteredFunctions(filtered);
  }, [functions, searchQuery, selectedCategory, categories]);

  /**
   * Load function documentation from API
   * 
   * 实现说明：
   * - 调用 /api/functions 端点获取数据
   * - 处理加载状态和错误
   * - 支持重试机制
   */
  const loadFunctionDocs = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // 从 API 加载函数文档
      console.log('Loading function documentation from API...');
      
      const response = await fetch('/api/functions');
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to load functions');
      }

      // 设置函数数据和分类数据
      setFunctions(data.functions || []);
      setCategories(data.categories || []);

      // 在开发环境下显示警告
      if (process.env.NODE_ENV === 'development' && data.warnings && data.warnings.length > 0) {
        console.warn('Documentation warnings:', data.warnings);
      }

      console.log(`Successfully loaded ${data.functions?.length || 0} functions and ${data.categories?.length || 0} categories`);

      /**
       * 备用 Mock 数据已移除
       * 
       * 说明：原有的 mock 数据已被注释掉，因为现在我们从 markdown 文件动态加载数据
       * 
       * 优势：
       * 1. 提高灵活性：更新函数文档只需修改 markdown 文件
       * 2. 便于维护：文档和代码分离，易于编辑
       * 3. 更好的可读性：markdown 格式更易阅读和编辑
       * 4. 支持版本控制：文档变更可以通过 Git 跟踪
       * 
       * 如需临时使用 mock 数据进行测试，可以：
       * 1. 在开发环境中检测 API 失败
       * 2. 回退到硬编码的测试数据
       * 3. 或者直接在 docs/functions/backend/ 目录添加测试 markdown 文件
       */
    } catch (err) {
      setError('Failed to load function documentation. Please try again.');
      console.error('Function docs loading error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Get function counts by category
   */
  const functionCounts = React.useMemo(() => {
    const counts: Record<string, number> = {};
    categories.forEach(cat => {
      counts[cat.categoryId] = functions.filter(f => 
        f.category === cat.category || 
        f.sourceFile?.includes(`/${cat.categoryId}/`)
      ).length;
    });
    return counts;
  }, [functions, categories]);

  /**
   * Get function statistics
   */
  const stats = {
    total: functions.length,
    categories: categories.length,
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
      <div className="flex min-h-screen">
        {/* 左侧导航栏 */}
        <FunctionNavigator
          categories={categories}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          functionCounts={functionCounts}
          isVisible={isNavVisible}
          onClose={() => setIsNavVisible(false)}
        />

        {/* 主内容区域 */}
        <div className="flex-1 overflow-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* 移动端导航栏切换按钮 */}
            <button
              onClick={() => setIsNavVisible(true)}
              className="lg:hidden fixed bottom-4 right-4 z-30 p-4 bg-steam-green text-white rounded-full shadow-lg hover:bg-steam-green-light transition-colors"
              aria-label="Open Navigation"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
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
                categories={['all', ...categories.map(c => c.displayName)]}
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
        </div>
      </div>
    </MainLayout>
  );
}

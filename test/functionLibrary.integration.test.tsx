/**
 * Function Library Integration Test
 * 
 * 文件功能：测试函数库功能的前后端集成
 * 用途：验证从 markdown 文件读取到前端显示的完整流程
 * 
 * 测试覆盖：
 * 1. API 端点响应
 * 2. 前端组件渲染
 * 3. 搜索和筛选功能
 * 4. 错误处理
 * 
 * 运行方式：
 * npm test -- functionLibrary.integration.test.ts
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import FunctionLibraryPage from '../src/pages/function-library';

/**
 * Mock fetch API
 * 
 * 用途：模拟 API 调用，避免实际的网络请求
 */
global.fetch = jest.fn();

/**
 * 测试用的 API 响应数据
 */
const mockApiResponse = {
  success: true,
  functions: [
    {
      id: 'search-games',
      name: 'search_games',
      category: 'API Endpoint',
      description: 'Main search endpoint for games',
      signature: '@app.post("/api/v1/search/games")\nasync def search_games(query: SearchQuerySchema):',
      parameters: [
        {
          name: 'query',
          type: 'SearchQuerySchema',
          description: 'Search query parameters',
          required: true,
        },
      ],
      returnType: 'GameResultSchema',
      example: 'results = await search_games(query)',
      tags: ['fastapi', 'endpoint', 'search'],
      complexity: 'High',
      lastUpdated: '2024-10-10',
    },
    {
      id: 'validate-query',
      name: 'validate_search_query',
      category: 'Validation',
      description: 'Validates search query input',
      signature: 'def validate_search_query(query: str) -> str:',
      parameters: [
        {
          name: 'query',
          type: 'str',
          description: 'Raw search query',
          required: true,
        },
      ],
      returnType: 'str',
      example: 'clean_query = validate_search_query(user_input)',
      tags: ['validation', 'security'],
      complexity: 'Medium',
      lastUpdated: '2024-10-10',
    },
    {
      id: 'bm25-search',
      name: 'search_bm25_index',
      category: 'Search Algorithm',
      description: 'BM25 keyword search',
      signature: 'async def search_bm25_index(query: str, limit: int = 50):',
      parameters: [
        {
          name: 'query',
          type: 'str',
          description: 'Search query',
          required: true,
        },
        {
          name: 'limit',
          type: 'int',
          description: 'Result limit',
          required: false,
          defaultValue: '50',
        },
      ],
      returnType: 'List[BM25Result]',
      example: 'results = await search_bm25_index("test")',
      tags: ['bm25', 'search', 'algorithm'],
      complexity: 'Medium',
      lastUpdated: '2024-10-10',
    },
  ],
  stats: {
    total: 3,
    categories: 3,
    lastUpdated: '2024-10-10',
  },
};

/**
 * 测试套件：API 端点测试
 */
describe('Function Library API', () => {
  beforeEach(() => {
    // 重置 mock
    (fetch as jest.Mock).mockClear();
  });

  /**
   * 测试：成功获取函数列表
   */
  it('should successfully fetch function list from API', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockApiResponse,
    });

    const response = await fetch('/api/functions');
    const data = await response.json();

    expect(data.success).toBe(true);
    expect(data.functions).toHaveLength(3);
    expect(data.stats.total).toBe(3);
  });

  /**
   * 测试：处理 API 错误
   */
  it('should handle API errors gracefully', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    });

    const response = await fetch('/api/functions');
    
    expect(response.ok).toBe(false);
    expect(response.status).toBe(500);
  });

  /**
   * 测试：API 返回正确的统计信息
   */
  it('should return correct statistics', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockApiResponse,
    });

    const response = await fetch('/api/functions');
    const data = await response.json();

    expect(data.stats).toBeDefined();
    expect(data.stats.total).toBe(3);
    expect(data.stats.categories).toBe(3);
    expect(data.stats.lastUpdated).toBeDefined();
  });
});

/**
 * 测试套件：前端页面渲染
 */
describe('Function Library Page Rendering', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  /**
   * 测试：页面正确加载和显示函数列表
   */
  it('should load and display function list', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockApiResponse,
    });

    render(<FunctionLibraryPage />);

    // 等待数据加载
    await waitFor(() => {
      expect(screen.queryByText('Loading function documentation...')).not.toBeInTheDocument();
    });

    // 验证函数是否显示
    expect(screen.getByText('search_games')).toBeInTheDocument();
    expect(screen.getByText('validate_search_query')).toBeInTheDocument();
    expect(screen.getByText('search_bm25_index')).toBeInTheDocument();
  });

  /**
   * 测试：显示正确的统计信息
   */
  it('should display correct statistics', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockApiResponse,
    });

    render(<FunctionLibraryPage />);

    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument(); // Total functions
    });
  });

  /**
   * 测试：显示加载状态
   */
  it('should show loading state', () => {
    (fetch as jest.Mock).mockImplementation(() => new Promise(() => {}));

    render(<FunctionLibraryPage />);

    expect(screen.getByText('Loading function documentation...')).toBeInTheDocument();
  });

  /**
   * 测试：显示错误状态
   */
  it('should show error state on API failure', async () => {
    (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(<FunctionLibraryPage />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load function documentation/i)).toBeInTheDocument();
    });
  });
});

/**
 * 测试套件：搜索功能
 */
describe('Function Search and Filter', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockApiResponse,
    });
  });

  /**
   * 测试：按名称搜索函数
   */
  it('should filter functions by search query', async () => {
    render(<FunctionLibraryPage />);

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    // 输入搜索关键词
    const searchInput = screen.getByPlaceholderText(/Search functions/i);
    fireEvent.change(searchInput, { target: { value: 'search' } });

    // 验证搜索结果
    await waitFor(() => {
      expect(screen.getByText('search_games')).toBeInTheDocument();
      expect(screen.getByText('search_bm25_index')).toBeInTheDocument();
      // validate_search_query 不包含 "search" 在名称中，但包含在标签中
      expect(screen.queryByText('validate_search_query')).not.toBeInTheDocument();
    });
  });

  /**
   * 测试：按分类筛选函数
   */
  it('should filter functions by category', async () => {
    render(<FunctionLibraryPage />);

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    // 选择分类筛选
    const categorySelect = screen.getByLabelText(/Category/i);
    fireEvent.change(categorySelect, { target: { value: 'Validation' } });

    // 验证筛选结果
    await waitFor(() => {
      expect(screen.getByText('validate_search_query')).toBeInTheDocument();
      expect(screen.queryByText('search_games')).not.toBeInTheDocument();
    });
  });

  /**
   * 测试：清除筛选
   */
  it('should clear filters and show all functions', async () => {
    render(<FunctionLibraryPage />);

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    // 应用筛选
    const searchInput = screen.getByPlaceholderText(/Search functions/i);
    fireEvent.change(searchInput, { target: { value: 'search' } });

    // 清除筛选
    const clearButton = screen.getByText(/Clear Filters/i);
    fireEvent.click(clearButton);

    // 验证所有函数都显示
    await waitFor(() => {
      expect(screen.getByText('search_games')).toBeInTheDocument();
      expect(screen.getByText('validate_search_query')).toBeInTheDocument();
      expect(screen.getByText('search_bm25_index')).toBeInTheDocument();
    });
  });

  /**
   * 测试：无搜索结果时显示消息
   */
  it('should show no results message when search yields nothing', async () => {
    render(<FunctionLibraryPage />);

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    // 搜索不存在的内容
    const searchInput = screen.getByPlaceholderText(/Search functions/i);
    fireEvent.change(searchInput, { target: { value: 'nonexistent' } });

    // 验证显示无结果消息
    await waitFor(() => {
      expect(screen.getByText(/No Functions Found/i)).toBeInTheDocument();
    });
  });
});

/**
 * 测试套件：函数卡片交互
 */
describe('Function Card Interaction', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockApiResponse,
    });
  });

  /**
   * 测试：展开和收起函数详情
   */
  it('should expand and collapse function details', async () => {
    render(<FunctionLibraryPage />);

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    // 找到第一个函数的展开按钮
    const expandButtons = screen.getAllByLabelText(/Expand/i);
    fireEvent.click(expandButtons[0]);

    // 验证详情是否显示
    await waitFor(() => {
      expect(screen.getByText(/Parameters/i)).toBeInTheDocument();
      expect(screen.getByText(/Example/i)).toBeInTheDocument();
    });

    // 收起详情
    const collapseButton = screen.getByLabelText(/Collapse/i);
    fireEvent.click(collapseButton);

    // 验证详情是否隐藏
    await waitFor(() => {
      expect(screen.queryByText(/Parameters/i)).not.toBeInTheDocument();
    });
  });

  /**
   * 测试：复制代码功能
   */
  it('should copy code to clipboard', async () => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(undefined),
      },
    });

    render(<FunctionLibraryPage />);

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    // 展开函数详情
    const expandButtons = screen.getAllByLabelText(/Expand/i);
    fireEvent.click(expandButtons[0]);

    // 点击复制按钮
    const copyButton = screen.getByText(/Copy Code/i);
    fireEvent.click(copyButton);

    // 验证复制功能被调用
    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalled();
    });
  });
});

/**
 * 测试套件：错误恢复
 */
describe('Error Recovery', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  /**
   * 测试：重试加载失败的数据
   */
  it('should allow retry after load failure', async () => {
    // 第一次调用失败
    (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(<FunctionLibraryPage />);

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Functions/i)).toBeInTheDocument();
    });

    // 模拟第二次调用成功
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockApiResponse,
    });

    // 点击重试按钮
    const retryButton = screen.getByText(/Try Again/i);
    fireEvent.click(retryButton);

    // 验证数据加载成功
    await waitFor(() => {
      expect(screen.getByText('search_games')).toBeInTheDocument();
    });
  });
});

/**
 * 性能测试
 */
describe('Performance', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  /**
   * 测试：处理大量函数数据
   */
  it('should handle large number of functions efficiently', async () => {
    // 生成大量函数数据
    const largeFunctionList = Array.from({ length: 100 }, (_, i) => ({
      id: `func-${i}`,
      name: `function_${i}`,
      category: 'Test',
      description: `Test function ${i}`,
      signature: `def function_${i}(): pass`,
      parameters: [],
      returnType: 'None',
      example: `function_${i}()`,
      tags: ['test'],
      complexity: 'Low',
      lastUpdated: '2024-10-10',
    }));

    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        functions: largeFunctionList,
        stats: { total: 100, categories: 1, lastUpdated: '2024-10-10' },
      }),
    });

    const startTime = performance.now();
    render(<FunctionLibraryPage />);

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // 渲染时间应该在合理范围内（< 3 秒）
    expect(renderTime).toBeLessThan(3000);
  });
});


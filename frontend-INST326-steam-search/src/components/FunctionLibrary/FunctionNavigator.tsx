/**
 * Function Library Navigator Component
 * 
 * 文件功能：函数库侧边导航栏组件
 * 用途：显示函数分类，支持快速切换和过滤
 * 
 * 功能：
 * 1. 显示所有分类及其图标
 * 2. 显示每个分类的函数数量
 * 3. 支持点击切换分类
 * 4. 高亮当前选中分类
 * 5. 响应式设计（移动端可收起）
 * 
 * 可扩展性：
 * - TODO: 添加搜索功能
 * - TODO: 添加收藏功能
 * - TODO: 添加最近访问记录
 */

import React, { useState } from 'react';

/**
 * 分类数据类型
 */
interface Category {
  category: string;
  categoryId: string;
  displayName: string;
  icon: string;
  order: number;
  description: string;
  purpose?: string;
}

/**
 * 组件 Props
 */
interface FunctionNavigatorProps {
  /** 分类列表 */
  categories: Category[];
  /** 当前选中的分类ID */
  selectedCategory: string;
  /** 分类切换回调 */
  onCategoryChange: (categoryId: string) => void;
  /** 每个分类的函数数量 */
  functionCounts: Record<string, number>;
  /** 是否显示导航栏（移动端控制） */
  isVisible?: boolean;
  /** 关闭导航栏回调（移动端） */
  onClose?: () => void;
}

/**
 * Function Navigator Component
 * 
 * 左侧导航栏，显示所有函数分类
 */
export default function FunctionNavigator({
  categories,
  selectedCategory,
  onCategoryChange,
  functionCounts,
  isVisible = true,
  onClose,
}: FunctionNavigatorProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  /**
   * 处理分类点击
   */
  const handleCategoryClick = (categoryId: string) => {
    onCategoryChange(categoryId);
    // 移动端点击后关闭导航栏
    if (onClose) {
      onClose();
    }
  };

  /**
   * 获取分类的函数数量
   */
  const getCategoryCount = (categoryId: string): number => {
    return functionCounts[categoryId] || 0;
  };

  /**
   * 计算总函数数
   */
  const totalFunctions = Object.values(functionCounts).reduce((sum, count) => sum + count, 0);

  return (
    <>
      {/* 移动端遮罩层 */}
      {isVisible && onClose && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* 导航栏容器 */}
      <div
        className={`
          fixed lg:sticky top-0 left-0 h-screen
          bg-steam-blue border-r border-steam-blue-light
          overflow-y-auto z-50
          transition-all duration-300 ease-in-out
          ${isVisible ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${isCollapsed ? 'w-16' : 'w-64'}
        `}
      >
        {/* 导航栏头部 */}
        <div className="p-4 border-b border-steam-blue-light">
          <div className="flex items-center justify-between">
            {!isCollapsed && (
              <h2 className="text-lg font-semibold text-white">
                📚 Categories
              </h2>
            )}
            
            {/* Collapse/Expand button (desktop only) */}
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="hidden lg:block p-2 text-gray-400 hover:text-white transition-colors rounded hover:bg-steam-blue-light"
              aria-label={isCollapsed ? 'Expand' : 'Collapse'}
            >
              <svg
                className={`w-5 h-5 transition-transform ${isCollapsed ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            {/* Close button (mobile only) */}
            {onClose && (
              <button
                onClick={onClose}
                className="lg:hidden p-2 text-gray-400 hover:text-white transition-colors"
                aria-label="Close"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Total count */}
          {!isCollapsed && (
            <div className="mt-2 text-sm text-gray-400">
              {totalFunctions} total functions
            </div>
          )}
        </div>

        {/* All categories option */}
        <div className="p-2">
          <button
            onClick={() => handleCategoryClick('all')}
            className={`
              w-full flex items-center gap-3 px-3 py-3 rounded-lg
              transition-all duration-200
              ${selectedCategory === 'all'
                ? 'bg-steam-green text-white shadow-lg'
                : 'text-gray-300 hover:bg-steam-blue-light hover:text-white'
              }
            `}
          >
            <span className="text-2xl flex-shrink-0">📂</span>
            {!isCollapsed && (
              <>
                <div className="flex-1 text-left">
                  <div className="font-medium">All Functions</div>
                  <div className="text-xs opacity-75">{totalFunctions} functions</div>
                </div>
              </>
            )}
          </button>
        </div>

        {/* Category list */}
        <nav className="p-2 space-y-1">
          {categories.map((category) => {
            const count = getCategoryCount(category.categoryId);
            const isSelected = selectedCategory === category.categoryId;

            return (
              <button
                key={category.categoryId}
                onClick={() => handleCategoryClick(category.categoryId)}
                className={`
                  w-full flex items-center gap-3 px-3 py-3 rounded-lg
                  transition-all duration-200
                  group
                  ${isSelected
                    ? 'bg-steam-green text-white shadow-lg'
                    : 'text-gray-300 hover:bg-steam-blue-light hover:text-white'
                  }
                `}
                title={isCollapsed ? category.displayName : category.description}
              >
                {/* Icon */}
                <span className="text-2xl flex-shrink-0">{category.icon}</span>

                {/* Category info (shown when expanded) */}
                {!isCollapsed && (
                  <>
                    <div className="flex-1 text-left min-w-0">
                      <div className="font-medium truncate">{category.displayName}</div>
                      <div className="text-xs opacity-75 truncate">
                        {count} {count === 1 ? 'function' : 'functions'}
                      </div>
                    </div>

                    {/* Count badge */}
                    <span
                      className={`
                        flex-shrink-0 px-2 py-1 text-xs font-medium rounded-full
                        ${isSelected
                          ? 'bg-white text-steam-green'
                          : 'bg-steam-blue-light text-gray-300 group-hover:bg-steam-blue-dark'
                        }
                      `}
                    >
                      {count}
                    </span>
                  </>
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom help text (shown when expanded) */}
        {!isCollapsed && (
          <div className="p-4 mt-auto border-t border-steam-blue-light">
            <div className="text-xs text-gray-400">
              <p className="mb-2">💡 Tips:</p>
              <ul className="space-y-1 list-disc list-inside">
                <li>Click category to filter</li>
                <li>Functions grouped by purpose</li>
                <li>Search & filter supported</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </>
  );
}


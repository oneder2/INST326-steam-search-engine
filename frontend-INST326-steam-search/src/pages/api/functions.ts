/**
 * Function Library API Endpoint
 * 
 * 文件功能：提供函数库数据的 API 接口
 * 用途：读取 markdown 文档并返回解析后的函数文档数据
 * 
 * API 端点：GET /api/functions
 * 
 * 功能说明：
 * 1. 读取 docs/functions/backend/ 目录下的所有 markdown 文件
 * 2. 使用 markdownParser 解析文件内容
 * 3. 返回 JSON 格式的函数文档数组
 * 4. 实现错误处理和日志记录
 * 
 * 可扩展性：
 * - TODO: 添加缓存机制减少文件读取
 * - TODO: 支持按分类/标签筛选
 * - TODO: 添加分页功能
 * - TODO: 支持实时文档更新通知
 */

import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { parseMultipleMarkdownFiles, validateFunctionDoc } from '@/utils/markdownParser';
import { FunctionDoc } from '@/types/functions';

/**
 * API 响应类型定义
 */
interface FunctionsApiResponse {
  /** 是否成功 */
  success: boolean;
  /** 函数文档数组 */
  functions?: FunctionDoc[];
  /** 分类信息数组 */
  categories?: Array<any>;
  /** 统计信息 */
  stats?: {
    total: number;
    categories: number;
    lastUpdated: string;
  };
  /** 错误信息 */
  error?: string;
  /** 警告信息 */
  warnings?: string[];
}

/**
 * 获取 markdown 文件目录的绝对路径
 * 
 * @returns markdown 文件目录的绝对路径
 * 
 * 实现说明：
 * - 使用 process.cwd() 获取项目根目录
 * - 拼接相对路径到文档目录
 */
function getMarkdownDirectory(): string {
  // 项目根目录
  const projectRoot = process.cwd();
  // 文档目录路径
  const docsPath = path.join(projectRoot, 'docs', 'functions', 'backend');
  
  return docsPath;
}

/**
 * 读取指定目录下的所有 markdown 文件（支持嵌套目录）
 * 
 * @param dirPath - 目录路径
 * @returns markdown 文件内容数组，包含相对路径信息
 * 
 * 实现说明：
 * - 递归读取子目录
 * - 只读取 .md 文件
 * - 过滤隐藏文件和特殊文件（README.md）
 * - 读取文件内容为 UTF-8 字符串
 */
function readMarkdownFiles(dirPath: string): Array<{ filename: string; content: string; category: string }> {
  const results: Array<{ filename: string; content: string; category: string }> = [];
  
  try {
    // 检查目录是否存在
    if (!fs.existsSync(dirPath)) {
      throw new Error(`Directory not found: ${dirPath}`);
    }

    // 读取目录中的所有项目
    const items = fs.readdirSync(dirPath);

    for (const item of items) {
      const itemPath = path.join(dirPath, item);
      const stat = fs.statSync(itemPath);

      // 如果是目录，递归读取
      if (stat.isDirectory()) {
        // 跳过特殊目录
        if (item === 'old_format' || item.startsWith('.')) {
          continue;
        }

        // 读取子目录中的文件
        const subDirFiles = fs.readdirSync(itemPath);
        
        for (const file of subDirFiles) {
          if (file.endsWith('.md') && !file.startsWith('.')) {
            const filePath = path.join(itemPath, file);
            const content = fs.readFileSync(filePath, 'utf-8');
            
            console.log(`Read file: ${item}/${file} (${content.length} bytes)`);
            
            results.push({
              filename: file,
              content,
              category: item, // 子目录名作为分类
            });
          }
        }
      } 
      // 如果是文件且是 markdown（排除 README.md）
      else if (item.endsWith('.md') && item !== 'README.md' && !item.startsWith('.')) {
        const content = fs.readFileSync(itemPath, 'utf-8');
        
        console.log(`Read file: ${item} (${content.length} bytes)`);
        
        results.push({
          filename: item,
          content,
          category: 'uncategorized', // 根目录文件标记为未分类
        });
      }
    }

    console.log(`Found ${results.length} markdown files in ${dirPath} and subdirectories`);
    return results;
  } catch (error) {
    console.error('Error reading markdown files:', error);
    throw error;
  }
}

/**
 * 读取分类信息
 * 
 * @param dirPath - 后端文档根目录
 * @returns 分类信息数组
 */
function readCategories(dirPath: string): Array<any> {
  const categories: Array<any> = [];
  
  try {
    const items = fs.readdirSync(dirPath);
    
    for (const item of items) {
      const itemPath = path.join(dirPath, item);
      const stat = fs.statSync(itemPath);
      
      // 只处理目录
      if (!stat.isDirectory() || item === 'old_format' || item.startsWith('.')) {
        continue;
      }
      
      // 查找 category.json 文件
      const categoryFile = path.join(itemPath, 'category.json');
      
      if (fs.existsSync(categoryFile)) {
        const content = fs.readFileSync(categoryFile, 'utf-8');
        const categoryData = JSON.parse(content);
        categories.push(categoryData);
        console.log(`Loaded category: ${categoryData.displayName}`);
      }
    }
    
    // 按 order 排序
    categories.sort((a, b) => (a.order || 999) - (b.order || 999));
    
    return categories;
  } catch (error) {
    console.error('Error reading categories:', error);
    return [];
  }
}

/**
 * 计算函数库统计信息
 * 
 * @param functions - 函数文档数组
 * @returns 统计信息对象
 */
function calculateStats(functions: FunctionDoc[]) {
  // 获取所有唯一的分类
  const categories = new Set(functions.map(func => func.category));

  // 获取最新的更新日期
  const dates = functions.map(func => func.lastUpdated).sort();
  const lastUpdated = dates[dates.length - 1] || 'Unknown';

  return {
    total: functions.length,
    categories: categories.size,
    lastUpdated,
  };
}

/**
 * 验证所有函数文档并收集警告
 * 
 * @param functions - 函数文档数组
 * @returns 警告信息数组
 */
function collectValidationWarnings(functions: FunctionDoc[]): string[] {
  const allWarnings: string[] = [];

  functions.forEach(func => {
    const validation = validateFunctionDoc(func);
    
    if (!validation.isValid) {
      allWarnings.push(`${func.name}: ${validation.errors.join(', ')}`);
    }
    
    if (validation.warnings.length > 0) {
      allWarnings.push(`${func.name}: ${validation.warnings.join(', ')}`);
    }
  });

  return allWarnings;
}

/**
 * API Handler - 处理函数库数据请求
 * 
 * @param req - Next.js API 请求对象
 * @param res - Next.js API 响应对象
 * 
 * 支持的请求方法：
 * - GET: 获取所有函数文档
 * 
 * 查询参数（未来扩展）：
 * - category: 按分类筛选
 * - tag: 按标签筛选
 * - search: 搜索关键词
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<FunctionsApiResponse>
) {
  // 只允许 GET 请求
  if (req.method !== 'GET') {
    return res.status(405).json({
      success: false,
      error: 'Method not allowed. Use GET.',
    });
  }

  try {
    console.log('API /api/functions called');

    // 1. 获取 markdown 文件目录
    const markdownDir = getMarkdownDirectory();
    console.log(`Markdown directory: ${markdownDir}`);

    // 2. 读取分类信息
    const categories = readCategories(markdownDir);
    console.log(`Loaded ${categories.length} categories`);

    // 3. 读取所有 markdown 文件
    const markdownFiles = readMarkdownFiles(markdownDir);

    if (markdownFiles.length === 0) {
      return res.status(404).json({
        success: false,
        error: 'No markdown files found in docs/functions/backend/',
      });
    }

    // 4. 解析 markdown 文件
    const functions = parseMultipleMarkdownFiles(markdownFiles);

    if (functions.length === 0) {
      return res.status(500).json({
        success: false,
        error: 'Failed to parse any functions from markdown files',
      });
    }

    // 5. 计算统计信息
    const stats = calculateStats(functions);

    // 6. 验证文档并收集警告（仅在开发环境）
    const warnings = process.env.NODE_ENV === 'development' 
      ? collectValidationWarnings(functions) 
      : undefined;

    // 7. 返回成功响应
    console.log(`Successfully parsed ${functions.length} functions from ${categories.length} categories`);

    return res.status(200).json({
      success: true,
      functions,
      categories,
      stats,
      warnings,
    });

  } catch (error) {
    // 错误处理
    console.error('Error in /api/functions:', error);

    const errorMessage = error instanceof Error ? error.message : 'Unknown error';

    return res.status(500).json({
      success: false,
      error: `Failed to load function documentation: ${errorMessage}`,
    });
  }
}

/**
 * API 配置
 * 
 * 禁用 body parser，因为这是一个 GET 请求
 */
export const config = {
  api: {
    bodyParser: false,
  },
};


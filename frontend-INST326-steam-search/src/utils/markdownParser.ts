/**
 * Markdown Parser Utility for Function Library
 * 
 * 文件功能：解析 markdown 格式的函数文档并转换为 FunctionDoc 类型
 * 用途：从 docs/functions/backend/ 目录下的 markdown 文件中提取函数文档
 * 
 * 主要功能：
 * 1. 解析 markdown 文件的特定格式
 * 2. 提取函数元数据（名称、分类、复杂度等）
 * 3. 解析参数列表
 * 4. 提取代码示例
 * 5. 处理标签和相关函数
 * 
 * 可扩展性：
 * - TODO: 支持更多 markdown 格式变体
 * - TODO: 添加缓存机制提高性能
 * - TODO: 支持多语言文档解析
 */

import { FunctionDoc, FunctionParameter } from '@/types/functions';

/**
 * 从 markdown 文本中解析单个函数文档
 * 
 * @param markdownText - markdown 格式的函数文档文本
 * @param sectionText - 单个函数的文档部分
 * @returns 解析后的 FunctionDoc 对象
 * 
 * 实现说明：
 * - 使用正则表达式匹配各个部分
 * - 按照固定的 markdown 格式进行解析
 * - 处理可选字段（如 notes, relatedFunctions）
 */
function parseFunctionSection(sectionText: string): FunctionDoc | null {
  try {
    // 提取函数名称（## 标题）
    const nameMatch = sectionText.match(/^##\s+(.+)$/m);
    if (!nameMatch) {
      console.warn('Function name not found in section');
      return null;
    }
    const name = nameMatch[1].trim();

    // 提取元数据（Category, Complexity, Last Updated）
    const categoryMatch = sectionText.match(/\*\*Category:\*\*\s+(.+)$/m);
    const complexityMatch = sectionText.match(/\*\*Complexity:\*\*\s+(Low|Medium|High)$/m);
    const lastUpdatedMatch = sectionText.match(/\*\*Last Updated:\*\*\s+(.+)$/m);

    if (!categoryMatch || !complexityMatch || !lastUpdatedMatch) {
      console.warn(`Missing metadata for function: ${name}`);
      return null;
    }

    const category = categoryMatch[1].trim();
    const complexity = complexityMatch[1].trim() as 'Low' | 'Medium' | 'High';
    const lastUpdated = lastUpdatedMatch[1].trim();

    // 提取描述（### Description 之后的内容）
    const descriptionMatch = sectionText.match(/###\s+Description\s+(.+?)(?=###|$)/s);
    const description = descriptionMatch ? descriptionMatch[1].trim() : '';

    // 提取函数签名（### Signature 中的代码块）
    const signatureMatch = sectionText.match(/###\s+Signature\s+```[\w]*\s+(.+?)```/s);
    const signature = signatureMatch ? signatureMatch[1].trim() : '';

    // 提取参数列表（### Parameters 部分）
    const parameters = parseParameters(sectionText);

    // 提取返回类型（### Returns 部分）
    const returnsMatch = sectionText.match(/###\s+Returns\s+- `?([^:`]+)`?:/);
    const returnType = returnsMatch ? returnsMatch[1].trim() : 'void';

    // 提取代码示例（### Example 中的代码块）
    const exampleMatch = sectionText.match(/###\s+Example\s+```[\w]*\s+(.+?)```/s);
    const example = exampleMatch ? exampleMatch[1].trim() : '';

    // 提取注释（### Notes 部分）
    const notesMatch = sectionText.match(/###\s+Notes\s+(.+?)(?=###|$)/s);
    const notes = notesMatch ? notesMatch[1].trim() : undefined;

    // 提取相关函数（### Related Functions 部分）
    const relatedFunctions = parseRelatedFunctions(sectionText);

    // 提取标签（### Tags 部分）
    const tags = parseTags(sectionText);

    // 生成唯一 ID（从函数名转换为 kebab-case）
    const id = name.toLowerCase().replace(/_/g, '-');

    return {
      id,
      name,
      category: category as any, // Type assertion for category
      description,
      signature,
      parameters,
      returnType,
      example,
      tags,
      complexity,
      lastUpdated,
      notes: notes || undefined,
      relatedFunctions: relatedFunctions.length > 0 ? relatedFunctions : undefined,
    };
  } catch (error) {
    console.error('Error parsing function section:', error);
    return null;
  }
}

/**
 * 解析参数列表
 * 
 * @param sectionText - 函数文档部分文本
 * @returns 参数数组
 * 
 * 格式示例：
 * - `param_name` (type, required): description
 * - `param_name` (type, optional): description (default: value)
 */
function parseParameters(sectionText: string): FunctionParameter[] {
  const parameters: FunctionParameter[] = [];

  // 提取 Parameters 部分
  const paramsMatch = sectionText.match(/###\s+Parameters\s+(.+?)(?=###|$)/s);
  if (!paramsMatch) {
    return parameters;
  }

  const paramsText = paramsMatch[1];

  // 匹配每个参数行
  // 格式: - `param_name` (type, required/optional): description
  const paramRegex = /-\s+`?([^`(]+)`?\s+\(([^,)]+),\s*(required|optional)\):\s*(.+?)(?=\n-|\n###|$)/gs;
  
  let match;
  while ((match = paramRegex.exec(paramsText)) !== null) {
    const name = match[1].trim();
    const type = match[2].trim();
    const required = match[3].trim() === 'required';
    const description = match[4].trim();

    // 提取默认值（如果有）
    const defaultMatch = description.match(/\(default:\s*([^)]+)\)/i);
    const defaultValue = defaultMatch ? defaultMatch[1].trim() : undefined;

    parameters.push({
      name,
      type,
      description: description.replace(/\(default:[^)]+\)/i, '').trim(),
      required,
      defaultValue,
    });
  }

  return parameters;
}

/**
 * 解析相关函数列表
 * 
 * @param sectionText - 函数文档部分文本
 * @returns 相关函数名称数组
 * 
 * 格式示例：
 * - [function_name](#anchor)
 */
function parseRelatedFunctions(sectionText: string): string[] {
  const relatedFunctions: string[] = [];

  const relatedMatch = sectionText.match(/###\s+Related Functions\s+(.+?)(?=###|$)/s);
  if (!relatedMatch) {
    return relatedFunctions;
  }

  const relatedText = relatedMatch[1];

  // 匹配 markdown 链接格式: [text](#anchor)
  const linkRegex = /-\s+\[([^\]]+)\]/g;
  
  let match;
  while ((match = linkRegex.exec(relatedText)) !== null) {
    relatedFunctions.push(match[1].trim());
  }

  return relatedFunctions;
}

/**
 * 解析标签列表
 * 
 * @param sectionText - 函数文档部分文本
 * @returns 标签数组
 * 
 * 格式示例：
 * #tag1 #tag2 #tag3
 */
function parseTags(sectionText: string): string[] {
  const tagsMatch = sectionText.match(/###\s+Tags\s+(.+?)(?=\n##|\n---|$)/s);
  if (!tagsMatch) {
    return [];
  }

  const tagsText = tagsMatch[1].trim();

  // 提取所有 # 开头的标签
  const tagRegex = /#([\w-]+)/g;
  const tags: string[] = [];
  
  let match;
  while ((match = tagRegex.exec(tagsText)) !== null) {
    tags.push(match[1]);
  }

  return tags;
}

/**
 * 从完整的 markdown 文件内容中解析所有函数文档
 * 
 * @param markdownContent - 完整的 markdown 文件内容
 * @returns 解析后的函数文档数组
 * 
 * 实现说明：
 * - 按照 ## 标题分割文档（每个函数一个二级标题）
 * - 过滤掉第一个部分（通常是文件标题）
 * - 逐个解析每个函数部分
 */
export function parseMarkdownFile(markdownContent: string): FunctionDoc[] {
  const functions: FunctionDoc[] = [];

  try {
    // 按照 ## 分割文档（每个函数一个部分）
    // 注意：第一个部分通常是文件标题，需要跳过
    const sections = markdownContent.split(/^##(?=\s)/m);

    // 跳过第一个部分（文件标题和描述）
    for (let i = 1; i < sections.length; i++) {
      const section = '##' + sections[i]; // 重新添加 ## 标记
      const functionDoc = parseFunctionSection(section);
      
      if (functionDoc) {
        functions.push(functionDoc);
      }
    }

    console.log(`Successfully parsed ${functions.length} functions from markdown`);
  } catch (error) {
    console.error('Error parsing markdown file:', error);
  }

  return functions;
}

/**
 * 从多个 markdown 文件中解析所有函数文档
 * 
 * @param files - markdown 文件内容数组，格式为 { filename, content, category }
 * @returns 所有解析后的函数文档数组
 * 
 * 用途：批量处理多个文档文件
 * 
 * Updated: Now supports category information from nested directories
 */
export function parseMultipleMarkdownFiles(
  files: Array<{ filename: string; content: string; category?: string }>
): FunctionDoc[] {
  const allFunctions: FunctionDoc[] = [];

  for (const file of files) {
    try {
      console.log(`Parsing file: ${file.category ? file.category + '/' : ''}${file.filename}`);
      const functions = parseMarkdownFile(file.content);
      
      // Add source file information to each function
      functions.forEach(func => {
        if (file.category && file.category !== 'uncategorized') {
          func.sourceFile = `docs/functions/backend/${file.category}/${file.filename}`;
        } else {
          func.sourceFile = `docs/functions/backend/${file.filename}`;
        }
      });

      allFunctions.push(...functions);
    } catch (error) {
      console.error(`Error parsing file ${file.filename}:`, error);
    }
  }

  console.log(`Total functions parsed: ${allFunctions.length}`);
  return allFunctions;
}

/**
 * 验证解析后的函数文档是否完整
 * 
 * @param functionDoc - 函数文档对象
 * @returns 验证结果对象
 * 
 * 验证项：
 * - 必填字段是否存在
 * - 参数格式是否正确
 * - 示例代码是否存在
 */
export function validateFunctionDoc(functionDoc: FunctionDoc): {
  isValid: boolean;
  errors: string[];
  warnings: string[];
} {
  const errors: string[] = [];
  const warnings: string[] = [];

  // 检查必填字段
  if (!functionDoc.id) errors.push('Missing id');
  if (!functionDoc.name) errors.push('Missing name');
  if (!functionDoc.category) errors.push('Missing category');
  if (!functionDoc.description) errors.push('Missing description');
  if (!functionDoc.signature) errors.push('Missing signature');
  if (!functionDoc.returnType) errors.push('Missing returnType');
  if (!functionDoc.complexity) errors.push('Missing complexity');
  if (!functionDoc.lastUpdated) errors.push('Missing lastUpdated');

  // 检查建议字段
  if (!functionDoc.example || functionDoc.example.length === 0) {
    warnings.push('Missing code example');
  }
  
  if (!functionDoc.tags || functionDoc.tags.length === 0) {
    warnings.push('No tags specified');
  }

  if (functionDoc.parameters.length === 0) {
    warnings.push('No parameters documented');
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
  };
}


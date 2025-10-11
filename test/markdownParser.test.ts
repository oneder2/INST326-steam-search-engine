/**
 * Markdown Parser Test Suite
 * 
 * 文件功能：测试 markdown 解析器的功能
 * 用途：验证 markdownParser.ts 中的所有函数是否正常工作
 * 
 * 测试覆盖：
 * 1. 解析单个函数文档
 * 2. 解析完整的 markdown 文件
 * 3. 参数解析
 * 4. 标签提取
 * 5. 相关函数提取
 * 6. 错误处理
 * 
 * 运行方式：
 * npm test -- markdownParser.test.ts
 */

import { parseMarkdownFile, parseMultipleMarkdownFiles, validateFunctionDoc } from '../src/utils/markdownParser';
import { FunctionDoc } from '../src/types/functions';

/**
 * 测试用的 markdown 内容样本
 */
const sampleMarkdown = `# FastAPI Backend - Test Functions

## test_function

**Category:** Search Algorithm
**Complexity:** Medium
**Last Updated:** 2024-10-10

### Description
This is a test function for validating the markdown parser. It demonstrates all the standard fields that should be parsed correctly.

### Signature
\`\`\`python
async def test_function(query: str, limit: int = 10) -> List[Result]:
\`\`\`

### Parameters
- \`query\` (str, required): The search query string
- \`limit\` (int, optional): Maximum number of results (default: 10)

### Returns
- \`List[Result]\`: List of search results

### Example
\`\`\`python
# Example usage
results = await test_function("test query", limit=20)
for result in results:
    print(result)
\`\`\`

### Notes
- This is a test function
- It includes all required fields
- Used for testing the parser

### Related Functions
- [another_function](#another_function)
- [helper_function](#helper_function)

### Tags
#test #parser #validation

---

## another_test_function

**Category:** API Endpoint
**Complexity:** High
**Last Updated:** 2024-10-10

### Description
Another test function with minimal fields to test optional parameter handling.

### Signature
\`\`\`python
def another_test_function(param: str) -> bool:
\`\`\`

### Parameters
- \`param\` (str, required): A parameter

### Returns
- \`bool\`: True if successful

### Example
\`\`\`python
result = another_test_function("test")
\`\`\`

### Tags
#test #endpoint
`;

/**
 * 测试套件：Markdown 文件解析
 */
describe('parseMarkdownFile', () => {
  /**
   * 测试：解析有效的 markdown 文件
   */
  it('should parse valid markdown file with multiple functions', () => {
    const functions = parseMarkdownFile(sampleMarkdown);
    
    // 应该解析出 2 个函数
    expect(functions).toHaveLength(2);
    
    // 第一个函数的基本信息
    expect(functions[0].name).toBe('test_function');
    expect(functions[0].category).toBe('Search Algorithm');
    expect(functions[0].complexity).toBe('Medium');
    expect(functions[0].lastUpdated).toBe('2024-10-10');
  });

  /**
   * 测试：正确解析函数描述
   */
  it('should correctly parse function description', () => {
    const functions = parseMarkdownFile(sampleMarkdown);
    
    expect(functions[0].description).toContain('test function');
    expect(functions[0].description).toContain('markdown parser');
  });

  /**
   * 测试：正确解析函数签名
   */
  it('should correctly parse function signature', () => {
    const functions = parseMarkdownFile(sampleMarkdown);
    
    expect(functions[0].signature).toContain('async def test_function');
    expect(functions[0].signature).toContain('query: str');
    expect(functions[0].signature).toContain('limit: int = 10');
  });

  /**
   * 测试：正确解析参数列表
   */
  it('should correctly parse function parameters', () => {
    const functions = parseMarkdownFile(sampleMarkdown);
    
    expect(functions[0].parameters).toHaveLength(2);
    
    // 第一个参数（必填）
    expect(functions[0].parameters[0].name).toBe('query');
    expect(functions[0].parameters[0].type).toBe('str');
    expect(functions[0].parameters[0].required).toBe(true);
    expect(functions[0].parameters[0].description).toContain('search query');
    
    // 第二个参数（可选，有默认值）
    expect(functions[0].parameters[1].name).toBe('limit');
    expect(functions[0].parameters[1].type).toBe('int');
    expect(functions[0].parameters[1].required).toBe(false);
    expect(functions[0].parameters[1].defaultValue).toBe('10');
  });

  /**
   * 测试：正确解析返回类型
   */
  it('should correctly parse return type', () => {
    const functions = parseMarkdownFile(sampleMarkdown);
    
    expect(functions[0].returnType).toBe('List[Result]');
  });

  /**
   * 测试：正确解析代码示例
   */
  it('should correctly parse code example', () => {
    const functions = parseMarkdownFile(sampleMarkdown);
    
    expect(functions[0].example).toContain('await test_function');
    expect(functions[0].example).toContain('for result in results');
  });

  /**
   * 测试：正确解析标签
   */
  it('should correctly parse tags', () => {
    const functions = parseMarkdownFile(sampleMarkdown);
    
    expect(functions[0].tags).toContain('test');
    expect(functions[0].tags).toContain('parser');
    expect(functions[0].tags).toContain('validation');
    expect(functions[0].tags).toHaveLength(3);
  });

  /**
   * 测试：正确解析相关函数
   */
  it('should correctly parse related functions', () => {
    const functions = parseMarkdownFile(sampleMarkdown);
    
    expect(functions[0].relatedFunctions).toContain('another_function');
    expect(functions[0].relatedFunctions).toContain('helper_function');
    expect(functions[0].relatedFunctions).toHaveLength(2);
  });

  /**
   * 测试：正确解析注释（Notes）
   */
  it('should correctly parse notes', () => {
    const functions = parseMarkdownFile(sampleMarkdown);
    
    expect(functions[0].notes).toBeDefined();
    expect(functions[0].notes).toContain('test function');
  });

  /**
   * 测试：处理缺少可选字段的函数
   */
  it('should handle functions with missing optional fields', () => {
    const functions = parseMarkdownFile(sampleMarkdown);
    
    // 第二个函数没有 notes 和 relatedFunctions
    expect(functions[1].notes).toBeUndefined();
    expect(functions[1].relatedFunctions).toBeUndefined();
  });

  /**
   * 测试：处理空的 markdown 内容
   */
  it('should return empty array for empty markdown', () => {
    const functions = parseMarkdownFile('');
    
    expect(functions).toHaveLength(0);
  });

  /**
   * 测试：处理无效的 markdown 格式
   */
  it('should handle invalid markdown gracefully', () => {
    const invalidMarkdown = 'This is not a valid function documentation';
    const functions = parseMarkdownFile(invalidMarkdown);
    
    // 不应该抛出错误，而是返回空数组
    expect(functions).toHaveLength(0);
  });
});

/**
 * 测试套件：多文件解析
 */
describe('parseMultipleMarkdownFiles', () => {
  /**
   * 测试：解析多个 markdown 文件
   */
  it('should parse multiple markdown files', () => {
    const files = [
      { filename: 'file1.md', content: sampleMarkdown },
      { filename: 'file2.md', content: sampleMarkdown },
    ];
    
    const functions = parseMultipleMarkdownFiles(files);
    
    // 应该解析出 4 个函数（每个文件 2 个）
    expect(functions).toHaveLength(4);
  });

  /**
   * 测试：为函数添加源文件信息
   */
  it('should add source file information to functions', () => {
    const files = [
      { filename: 'test_file.md', content: sampleMarkdown },
    ];
    
    const functions = parseMultipleMarkdownFiles(files);
    
    expect(functions[0].sourceFile).toBe('docs/functions/backend/test_file.md');
  });

  /**
   * 测试：处理部分文件解析失败
   */
  it('should continue parsing even if one file fails', () => {
    const files = [
      { filename: 'valid.md', content: sampleMarkdown },
      { filename: 'invalid.md', content: 'invalid content' },
      { filename: 'valid2.md', content: sampleMarkdown },
    ];
    
    const functions = parseMultipleMarkdownFiles(files);
    
    // 应该解析出 4 个函数（2 个有效文件 × 2 个函数）
    expect(functions).toHaveLength(4);
  });
});

/**
 * 测试套件：函数文档验证
 */
describe('validateFunctionDoc', () => {
  /**
   * 测试：验证完整的函数文档
   */
  it('should validate complete function documentation', () => {
    const completeFunction: FunctionDoc = {
      id: 'test-function',
      name: 'test_function',
      category: 'Search Algorithm',
      description: 'Test function description',
      signature: 'def test_function(): pass',
      parameters: [],
      returnType: 'None',
      example: 'test_function()',
      tags: ['test'],
      complexity: 'Low',
      lastUpdated: '2024-10-10',
    };
    
    const validation = validateFunctionDoc(completeFunction);
    
    expect(validation.isValid).toBe(true);
    expect(validation.errors).toHaveLength(0);
  });

  /**
   * 测试：检测缺少必填字段
   */
  it('should detect missing required fields', () => {
    const incompleteFunction = {
      id: 'test',
      name: 'test_function',
      // 缺少其他必填字段
    } as any;
    
    const validation = validateFunctionDoc(incompleteFunction);
    
    expect(validation.isValid).toBe(false);
    expect(validation.errors.length).toBeGreaterThan(0);
  });

  /**
   * 测试：检测缺少建议字段并生成警告
   */
  it('should warn about missing recommended fields', () => {
    const functionWithoutExample: FunctionDoc = {
      id: 'test-function',
      name: 'test_function',
      category: 'Search Algorithm',
      description: 'Test function',
      signature: 'def test_function(): pass',
      parameters: [],
      returnType: 'None',
      example: '', // 空示例
      tags: [], // 空标签
      complexity: 'Low',
      lastUpdated: '2024-10-10',
    };
    
    const validation = validateFunctionDoc(functionWithoutExample);
    
    // 应该是有效的，但有警告
    expect(validation.isValid).toBe(true);
    expect(validation.warnings.length).toBeGreaterThan(0);
    expect(validation.warnings.some(w => w.includes('example'))).toBe(true);
    expect(validation.warnings.some(w => w.includes('tags'))).toBe(true);
  });
});

/**
 * 集成测试：完整的工作流程
 */
describe('Integration: Complete workflow', () => {
  /**
   * 测试：完整的文档加载和解析流程
   */
  it('should successfully parse real markdown files', () => {
    // 这个测试模拟了 API 端点的实际工作流程
    const files = [
      { filename: 'api_endpoints.md', content: sampleMarkdown },
    ];
    
    // 1. 解析文件
    const functions = parseMultipleMarkdownFiles(files);
    
    // 2. 验证结果
    expect(functions.length).toBeGreaterThan(0);
    
    // 3. 验证每个函数
    functions.forEach(func => {
      const validation = validateFunctionDoc(func);
      
      // 所有解析出的函数都应该通过基本验证
      expect(validation.isValid).toBe(true);
      
      // 检查源文件信息是否添加
      expect(func.sourceFile).toBeDefined();
    });
  });
});

/**
 * 边界情况测试
 */
describe('Edge cases', () => {
  /**
   * 测试：处理非常长的描述
   */
  it('should handle very long descriptions', () => {
    const longDescription = 'A'.repeat(10000);
    const markdown = `# Test\n\n## test_func\n\n**Category:** Test\n**Complexity:** Low\n**Last Updated:** 2024-10-10\n\n### Description\n${longDescription}\n\n### Signature\n\`\`\`\ndef test(): pass\n\`\`\`\n\n### Parameters\nNone\n\n### Returns\n- \`None\`\n\n### Example\n\`\`\`\ntest()\n\`\`\`\n\n### Tags\n#test`;
    
    const functions = parseMarkdownFile(markdown);
    
    expect(functions).toHaveLength(1);
    expect(functions[0].description.length).toBeGreaterThan(1000);
  });

  /**
   * 测试：处理特殊字符
   */
  it('should handle special characters in function names', () => {
    const markdown = `# Test\n\n## test_function_with_numbers_123\n\n**Category:** Test\n**Complexity:** Low\n**Last Updated:** 2024-10-10\n\n### Description\nTest\n\n### Signature\n\`\`\`\ndef test(): pass\n\`\`\`\n\n### Parameters\nNone\n\n### Returns\n- \`None\`\n\n### Example\n\`\`\`\ntest()\n\`\`\`\n\n### Tags\n#test`;
    
    const functions = parseMarkdownFile(markdown);
    
    expect(functions[0].name).toBe('test_function_with_numbers_123');
  });

  /**
   * 测试：处理空的代码块
   */
  it('should handle empty code blocks', () => {
    const markdown = `# Test\n\n## test_func\n\n**Category:** Test\n**Complexity:** Low\n**Last Updated:** 2024-10-10\n\n### Description\nTest\n\n### Signature\n\`\`\`python\n\`\`\`\n\n### Parameters\nNone\n\n### Returns\n- \`None\`\n\n### Example\n\`\`\`python\n\`\`\`\n\n### Tags\n#test`;
    
    const functions = parseMarkdownFile(markdown);
    
    expect(functions).toHaveLength(1);
    expect(functions[0].signature).toBe('');
    expect(functions[0].example).toBe('');
  });
});


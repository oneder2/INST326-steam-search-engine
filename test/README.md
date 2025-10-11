# Function Library Testing Guide

## 测试文件说明

本目录包含函数库功能的测试文件，用于验证 markdown 文档解析和前端显示功能的正确性。

### 测试文件结构

```
test/
├── README.md                            # 本文件
├── markdownParser.test.ts               # Markdown 解析器单元测试
└── functionLibrary.integration.test.tsx # 函数库集成测试
```

---

## 测试文件详情

### 1. markdownParser.test.ts

**用途**: 测试 markdown 解析器的所有功能

**测试覆盖**:
- ✅ 解析单个函数文档
- ✅ 解析完整的 markdown 文件
- ✅ 参数列表解析
- ✅ 标签提取
- ✅ 相关函数提取
- ✅ 函数签名解析
- ✅ 代码示例提取
- ✅ 错误处理

**运行命令**:
```bash
npm test markdownParser.test.ts
```

**测试套件**:
1. `parseMarkdownFile` - 测试 markdown 文件解析
2. `parseMultipleMarkdownFiles` - 测试多文件解析
3. `validateFunctionDoc` - 测试文档验证
4. `Integration` - 集成测试
5. `Edge cases` - 边界情况测试

---

### 2. functionLibrary.integration.test.tsx

**用途**: 测试函数库功能的前后端集成

**测试覆盖**:
- ✅ API 端点响应
- ✅ 前端组件渲染
- ✅ 搜索功能
- ✅ 筛选功能
- ✅ 错误处理和恢复
- ✅ 用户交互（展开/收起、复制代码）
- ✅ 性能测试

**运行命令**:
```bash
npm test functionLibrary.integration.test.tsx
```

**测试套件**:
1. `Function Library API` - API 端点测试
2. `Function Library Page Rendering` - 页面渲染测试
3. `Function Search and Filter` - 搜索和筛选测试
4. `Function Card Interaction` - 卡片交互测试
5. `Error Recovery` - 错误恢复测试
6. `Performance` - 性能测试

---

## 运行所有测试

### 运行全部测试
```bash
npm test
```

### 运行特定测试文件
```bash
npm test <filename>
```

### 运行测试并生成覆盖率报告
```bash
npm run test:coverage
```

### 监听模式运行测试（开发时使用）
```bash
npm run test:watch
```

---

## 测试结果说明

### 成功的测试输出
```
PASS  test/markdownParser.test.ts
  ✓ parseMarkdownFile
    ✓ should parse valid markdown file with multiple functions (5ms)
    ✓ should correctly parse function description (2ms)
    ...

Test Suites: 2 passed, 2 total
Tests:       25 passed, 25 total
Snapshots:   0 total
Time:        2.456s
```

### 失败的测试输出
```
FAIL  test/markdownParser.test.ts
  ✗ should parse valid markdown (10ms)
    
    Expected: 2
    Received: 0
    
    at Object.<anonymous> (test/markdownParser.test.ts:45:10)
```

---

## 测试最佳实践

### 1. 测试命名规范
- 使用描述性的测试名称
- 遵循 "should + 动作 + 预期结果" 格式
- 例如: `should parse valid markdown file with multiple functions`

### 2. 测试结构 (AAA Pattern)
```typescript
it('should do something', () => {
  // Arrange - 准备测试数据
  const input = 'test data';
  
  // Act - 执行被测试的操作
  const result = functionToTest(input);
  
  // Assert - 验证结果
  expect(result).toBe('expected output');
});
```

### 3. 使用 Mock 数据
- 避免依赖外部服务
- 使用 jest.fn() 模拟函数
- 使用 jest.mock() 模拟模块

### 4. 测试边界情况
- 空输入
- 无效输入
- 极大/极小值
- 特殊字符

---

## 调试测试

### 查看详细输出
```bash
npm test -- --verbose
```

### 只运行失败的测试
```bash
npm test -- --onlyFailures
```

### 使用 console.log 调试
在测试中添加 console.log，输出会显示在测试结果中：
```typescript
it('should debug test', () => {
  const data = getData();
  console.log('Debug data:', data);
  expect(data).toBeDefined();
});
```

### 使用 VS Code 调试器
1. 在测试文件中设置断点
2. 打开 VS Code 的调试面板
3. 选择 "Jest: Current File"
4. 点击运行按钮

---

## 添加新测试

### 创建新的测试文件
1. 在 `test/` 目录创建新文件
2. 文件命名格式: `<feature>.test.ts` 或 `<feature>.integration.test.ts`
3. 导入必要的测试工具:
```typescript
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
```

### 测试文件模板
```typescript
/**
 * Feature Test Suite
 * 
 * 文件功能：测试某个功能
 * 用途：验证功能是否正常工作
 */

describe('Feature Name', () => {
  beforeEach(() => {
    // 每个测试前的设置
  });

  afterEach(() => {
    // 每个测试后的清理
  });

  it('should do something', () => {
    // 测试实现
    expect(true).toBe(true);
  });
});
```

---

## 持续集成 (CI)

### GitHub Actions 配置
测试会在以下情况自动运行：
- Push 到任何分支
- 创建 Pull Request
- 合并到 main 分支

### CI 测试流程
1. 安装依赖
2. 运行类型检查
3. 运行 ESLint
4. 运行所有测试
5. 生成覆盖率报告

---

## 测试覆盖率目标

| 类型 | 目标覆盖率 | 当前覆盖率 |
|------|-----------|-----------|
| 语句 | ≥ 80% | - |
| 分支 | ≥ 75% | - |
| 函数 | ≥ 80% | - |
| 行数 | ≥ 80% | - |

### 查看覆盖率报告
```bash
npm run test:coverage
```

报告会生成在 `coverage/` 目录，使用浏览器打开 `coverage/lcov-report/index.html` 查看详细报告。

---

## 常见问题

### Q: 测试运行很慢
A: 
1. 使用 `--maxWorkers=4` 限制并行worker数量
2. 检查是否有超时的测试
3. 使用 mock 替代实际的 API 调用

### Q: 测试在 CI 中失败但本地通过
A:
1. 检查环境变量配置
2. 确保依赖版本一致
3. 检查文件路径（区分大小写）
4. 查看 CI 日志获取详细错误信息

### Q: 如何跳过某个测试
A:
```typescript
it.skip('test to skip', () => {
  // 这个测试会被跳过
});
```

### Q: 如何只运行某个测试
A:
```typescript
it.only('only run this test', () => {
  // 只运行这个测试
});
```

---

## 相关文档

- [Jest 官方文档](https://jestjs.io/)
- [React Testing Library 文档](https://testing-library.com/react)
- [DEVELOPMENT.md](../DEVELOPMENT.md) - 开发指南
- [README.md](../README.md) - 项目说明

---

## 维护记录

| 日期 | 更改内容 | 维护人 |
|------|---------|--------|
| 2024-10-10 | 创建测试文件和测试指南 | - |

---

**注意**: 在提交代码前，请确保所有测试都通过。使用 `npm test` 运行所有测试。


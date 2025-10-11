# Function Library 快速上手指南

## 🚀 5 分钟快速上手

欢迎使用全新的 Function Library！本指南将帮助你快速了解如何使用新的分类导航系统。

---

## 📖 新功能一览

### ✨ 主要亮点

1. **📁 分类文件夹** - 函数按用途组织到 4 个目录
2. **🧭 左侧导航栏** - 可视化导航，一键切换分类
3. **📄 分类说明** - 每个分类都有详细的用途说明
4. **📱 响应式** - 完美支持桌面端和移动端

---

## 🗂️ 目录结构

```
docs/functions/backend/
│
├── 🌐 api-endpoints/          ← API 端点（4 个函数）
│   ├── category.json          ← 分类说明文件
│   ├── search_games.md
│   ├── get_game_detail.md
│   ├── get_search_suggestions.md
│   └── health_check.md
│
├── 🔍 search-algorithms/      ← 搜索算法（3 个函数）
│   ├── category.json
│   ├── search_bm25_index.md
│   ├── search_faiss_index.md
│   └── apply_fusion_ranking.md
│
├── 💾 data-access/            ← 数据访问（4 个函数）
│   ├── category.json
│   ├── get_game_by_id.md
│   ├── get_games_by_ids.md
│   ├── load_bm25_index.md
│   └── load_faiss_index.md
│
└── 🔒 validation/             ← 验证安全（1 个函数）
    ├── category.json
    └── validate_search_query.md
```

---

## 🎯 使用场景

### 场景 1: 查找 API 端点函数
```
1. 访问 /function-library
2. 点击左侧 "🌐 API 端点"
3. 看到 4 个 API 相关函数
4. 点击查看详细文档
```

### 场景 2: 了解搜索算法
```
1. 点击左侧 "🔍 搜索算法"
2. 查看 3 个核心算法
3. 阅读融合排序的实现
4. 复制示例代码使用
```

### 场景 3: 查看分类说明
```
方式 1（网页）:
- 点击分类查看函数列表
- 分类信息会显示在顶部

方式 2（文件）:
- cat docs/functions/backend/api-endpoints/category.json
- 查看完整的分类元数据
```

### 场景 4: 更新函数文档
```
1. 定位文件
   vim docs/functions/backend/api-endpoints/search_games.md

2. 编辑内容

3. 保存文件

4. 刷新网页 → 立即生效！
```

---

## 🧭 导航栏使用

### 桌面端

**展开状态**（默认）:
```
┌─────────────────────────┐
│ 📚 函数分类     [← 收起]│
│ 共 12 个函数             │
├─────────────────────────┤
│ 📂 全部函数        [12] │
├─────────────────────────┤
│ 🌐 API 端点         [4] │ ← 选中高亮
│ 🔍 搜索算法         [3] │
│ 💾 数据访问         [4] │
│ 🔒 验证与安全       [1] │
└─────────────────────────┘
```

**收起状态**（节省空间）:
```
┌────┐
│ [→]│
├────┤
│ 📂 │
├────┤
│ 🌐 │ ← 选中
│ 🔍 │
│ 💾 │
│ 🔒 │
└────┘
```

### 移动端

**隐藏状态**（默认）:
```
                  [☰] ← 浮动按钮
                      （右下角）
```

**显示状态**（点击后）:
```
[遮罩]  ┌──────────────┐
[背景]  │ 📚 函数分类 [X]│
        │ 共 12 个函数  │
        ├──────────────┤
        │ 📂 全部 [12] │
        │ 🌐 API   [4] │
        │ 🔍 搜索  [3] │
        │ 💾 数据  [4] │
        │ 🔒 安全  [1] │
        └──────────────┘
```

---

## 📝 常见操作

### 1. 查看某个分类的所有函数
```bash
# 命令行方式
ls docs/functions/backend/api-endpoints/

# 网页方式
访问 /function-library → 点击 "🌐 API 端点"
```

### 2. 搜索特定函数
```bash
# 在分类中搜索
grep -r "search_games" docs/functions/backend/api-endpoints/

# 全局搜索
grep -r "search_games" docs/functions/backend/
```

### 3. 查看分类详情
```bash
# 查看 API Endpoints 分类信息
cat docs/functions/backend/api-endpoints/category.json

# 美化输出
cat docs/functions/backend/api-endpoints/category.json | jq
```

### 4. 统计信息
```bash
# 统计每个分类的函数数
for dir in docs/functions/backend/*/; do 
  count=$(ls -1 "$dir"/*.md 2>/dev/null | wc -l)
  echo "$(basename "$dir"): $count 个函数"
done

# API 方式
curl http://localhost:3000/api/functions | jq .stats
```

### 5. 添加新函数
```bash
# 1. 在对应分类创建文件
vim docs/functions/backend/api-endpoints/my_new_endpoint.md

# 2. 按照格式编写

# 3. 保存 → 自动出现在列表中！
```

---

## 🎨 分类说明详解

每个 `category.json` 包含：

```json
{
  "category": "API Endpoint",           // 分类名称
  "categoryId": "api-endpoints",        // 文件夹名
  "displayName": "API 端点",            // 显示名称
  "icon": "🌐",                         // 图标
  "order": 1,                           // 排序顺序
  "description": "简短描述",            // 一句话说明
  "purpose": "详细用途说明",            // 完整描述
  "characteristics": [...],             // 特性列表
  "commonPatterns": [...],              // 常见模式
  "relatedCategories": [...],           // 关联分类
  "bestPractices": [...],               // 最佳实践
  // ... 更多元数据
}
```

### 如何使用分类信息

**在代码中**:
```typescript
// API 自动返回
const response = await fetch('/api/functions');
const data = await response.json();
console.log(data.categories); // 所有分类信息
```

**在文档中**:
- 了解分类用途
- 学习最佳实践
- 查看性能指标
- 理解安全威胁（Validation 分类）

---

## 💡 最佳实践

### 查找函数
1. **知道函数名**: 直接搜索或打开对应文件
2. **知道用途**: 通过分类导航查找
3. **不确定**: 使用搜索功能

### 阅读文档
1. **快速了解**: 看函数签名和描述
2. **深入学习**: 展开查看参数和示例
3. **理解分类**: 阅读 category.json

### 更新文档
1. **小改动**: 直接编辑对应 .md 文件
2. **新函数**: 创建新文件放入对应分类
3. **新分类**: 创建新目录 + category.json

---

## 🔧 高级功能

### 导航栏功能

| 功能 | 操作 |
|------|------|
| 切换分类 | 点击分类名称 |
| 查看所有 | 点击 "全部函数" |
| 收起导航 | 点击 ← 按钮（桌面） |
| 展开导航 | 点击 → 按钮 |
| 移动端显示 | 点击右下角 ☰ 按钮 |
| 移动端关闭 | 点击遮罩或 X 按钮 |

### 搜索功能

| 搜索类型 | 说明 |
|---------|------|
| 按名称 | 输入函数名 |
| 按描述 | 输入功能关键词 |
| 按标签 | 输入标签名 |
| 按分类 | 使用导航栏或下拉框 |

---

## 📊 快速参考

### 分类速查表

| 图标 | 分类 | 函数数 | 主要用途 |
|------|------|--------|----------|
| 🌐 | API Endpoints | 4 | 处理HTTP请求 |
| 🔍 | Search Algorithms | 3 | 搜索和排序 |
| 💾 | Data Access | 4 | 数据库操作 |
| 🔒 | Validation | 1 | 安全防护 |

### 常用函数速查

| 需求 | 函数 | 分类 |
|------|------|------|
| 搜索游戏 | search_games | 🌐 API |
| 获取详情 | get_game_detail | 🌐 API |
| BM25 搜索 | search_bm25_index | 🔍 Search |
| 语义搜索 | search_faiss_index | 🔍 Search |
| 融合排序 | apply_fusion_ranking | 🔍 Search |
| 查询单个 | get_game_by_id | 💾 Data |
| 批量查询 | get_games_by_ids | 💾 Data |
| 输入验证 | validate_search_query | 🔒 Validation |

---

## ❓ 常见问题

### Q: 找不到某个函数？
A: 
1. 使用导航栏按分类查找
2. 使用搜索框搜索函数名
3. 查看 `backend/README.md` 完整索引

### Q: 如何知道函数在哪个分类？
A: 
- 打开函数文件，看 `**Category:**` 字段
- 或查看文件所在的目录名

### Q: category.json 是做什么的？
A: 
- 存储分类的元数据
- 提供分类说明、用途、最佳实践
- 前端导航栏使用这些信息

### Q: 导航栏可以自定义吗？
A: 
- 可以！编辑对应的 `category.json`
- 修改 `displayName`, `icon`, `order` 等字段
- 刷新页面即可看到效果

### Q: 如何添加新分类？
A:
```bash
# 1. 创建目录
mkdir docs/functions/backend/my-category

# 2. 创建 category.json
vim docs/functions/backend/my-category/category.json

# 3. 添加函数文件
vim docs/functions/backend/my-category/my_function.md

# 4. 刷新网页 → 自动识别！
```

---

## 🎓 学习路径

### 新手入门
1. 浏览 `/function-library` 页面
2. 点击不同分类了解结构
3. 查看几个函数文档
4. 阅读 category.json 了解分类

### 进阶使用
1. 使用搜索功能查找函数
2. 阅读相关函数链接
3. 复制代码示例测试
4. 了解最佳实践

### 高级开发
1. 编辑现有文档
2. 添加新函数文档
3. 创建自定义分类
4. 贡献文档改进

---

## 📱 移动端提示

### 如何打开导航栏
- 点击右下角的 **☰ 浮动按钮**
- 导航栏从左侧滑出

### 如何关闭导航栏
- 点击 **X 关闭按钮**（右上角）
- 或点击背景遮罩
- 或选择一个分类（自动关闭）

---

## 🔗 快速链接

### 在线访问
- **Function Library**: `http://localhost:3000/function-library`
- **API Endpoint**: `http://localhost:3000/api/functions`

### 本地文件
- **函数索引**: `docs/functions/backend/README.md`
- **分类目录**: `docs/functions/backend/`
- **项目文档**: `README.md`

### 详细文档
- **[最终总结](FINAL_SUMMARY.md)** - 完整的重构总结
- **[分类结构](CATEGORIZED_STRUCTURE_SUMMARY.md)** - 分类系统说明
- **[单文件架构](SINGLE_FILE_PER_FUNCTION_SUMMARY.md)** - 单文件说明

---

## 🎯 下一步

### 探索功能
- [ ] 访问 Function Library 页面
- [ ] 尝试左侧导航栏
- [ ] 切换不同分类
- [ ] 使用搜索功能
- [ ] 查看 category.json

### 实践操作
- [ ] 编辑一个函数文档
- [ ] 查看 Git diff
- [ ] 添加一个新函数
- [ ] 理解分类组织

### 深入学习
- [ ] 阅读所有 category.json
- [ ] 理解每个分类的用途
- [ ] 学习最佳实践
- [ ] 探索相关函数

---

## 💪 小贴士

### 效率提升
- ⚡ 使用导航栏而不是搜索（已知分类时）
- ⚡ 收藏常用函数的文件路径
- ⚡ 使用编辑器的文件导航功能
- ⚡ 熟悉分类可以快速定位

### 文档编辑
- 📝 遵循现有格式
- 📝 参考同分类的其他函数
- 📝 填写完整的字段
- 📝 提供可运行的示例

### 团队协作
- 🤝 每人负责特定分类
- 🤝 独立文件减少冲突
- 🤝 使用清晰的提交信息
- 🤝 及时同步文档变更

---

## 📞 获取帮助

### 遇到问题？

1. **查看文档**
   - [backend/README.md](functions/backend/README.md) - 完整索引
   - [DEVELOPMENT.md](../DEVELOPMENT.md) - 开发指南

2. **查看示例**
   - 参考现有函数文档
   - 查看 category.json 示例

3. **联系团队**
   - 通过课程渠道
   - 提交 Issue
   - 发起讨论

---

## 🎉 开始使用

现在就开始探索新的 Function Library！

```bash
# 启动开发服务器
npm run dev

# 访问函数库
# → http://localhost:3000/function-library

# 享受全新的分类导航体验！🚀
```

---

**版本**: 2.0.0  
**更新**: 2024-10-10  
**状态**: ✅ 可用

**Happy Coding! 🎊**


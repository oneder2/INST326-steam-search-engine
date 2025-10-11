# Backend Function Documentation

## 📋 文档结构

本目录包含所有 Python FastAPI 后端函数的文档。**每个函数都有独立的 markdown 文件**，提高了可读性和可维护性。

### 文件组织

```
docs/functions/backend/
├── README.md                      # 本文件
├── old_format/                    # 旧格式备份（多函数文件）
│   ├── api_endpoints.md
│   ├── search_algorithms.md
│   └── data_access.md
├── apply_fusion_ranking.md        # 融合排序算法
├── get_game_by_id.md              # 按ID获取游戏
├── get_game_detail.md             # 获取游戏详情
├── get_games_by_ids.md            # 批量获取游戏
├── get_search_suggestions.md      # 搜索建议
├── health_check.md                # 健康检查
├── load_bm25_index.md             # 加载BM25索引
├── load_faiss_index.md            # 加载Faiss索引
├── search_bm25_index.md           # BM25搜索
├── search_faiss_index.md          # Faiss语义搜索
├── search_games.md                # 主搜索端点
└── validate_search_query.md       # 查询验证
```

---

## 📊 函数分类

### API Endpoints（API 端点）- 4 个函数
| 函数名 | 文件 | 复杂度 | 说明 |
|--------|------|--------|------|
| `search_games` | [search_games.md](search_games.md) | High | 主搜索端点 |
| `get_search_suggestions` | [get_search_suggestions.md](get_search_suggestions.md) | Medium | 搜索建议 |
| `get_game_detail` | [get_game_detail.md](get_game_detail.md) | Low | 游戏详情 |
| `health_check` | [health_check.md](health_check.md) | Low | 健康检查 |

### Search Algorithms（搜索算法）- 4 个函数
| 函数名 | 文件 | 复杂度 | 说明 |
|--------|------|--------|------|
| `search_bm25_index` | [search_bm25_index.md](search_bm25_index.md) | Medium | BM25关键词搜索 |
| `search_faiss_index` | [search_faiss_index.md](search_faiss_index.md) | High | Faiss语义搜索 |
| `apply_fusion_ranking` | [apply_fusion_ranking.md](apply_fusion_ranking.md) | High | 融合排序算法 |
| `validate_search_query` | [validate_search_query.md](validate_search_query.md) | Medium | 查询验证 |

### Data Access（数据访问）- 4 个函数
| 函数名 | 文件 | 复杂度 | 说明 |
|--------|------|--------|------|
| `get_game_by_id` | [get_game_by_id.md](get_game_by_id.md) | Low | 按ID获取游戏 |
| `get_games_by_ids` | [get_games_by_ids.md](get_games_by_ids.md) | Medium | 批量获取游戏 |
| `load_bm25_index` | [load_bm25_index.md](load_bm25_index.md) | Medium | 加载BM25索引 |
| `load_faiss_index` | [load_faiss_index.md](load_faiss_index.md) | High | 加载Faiss索引 |

**总计**: 12 个函数

---

## 📝 文档格式

每个函数文档文件遵循统一格式：

```markdown
# function_name

## function_name

**Category:** API Endpoint | Search Algorithm | Data Access | Validation
**Complexity:** Low | Medium | High
**Last Updated:** YYYY-MM-DD

### Description
函数的详细描述...

### Signature
\`\`\`python
def function_name(param: type) -> ReturnType:
\`\`\`

### Parameters
- `param` (type, required): 参数描述
- `param2` (type, optional): 参数描述 (default: value)

### Returns
- `ReturnType`: 返回值描述

### Example
\`\`\`python
# 使用示例
result = function_name(value)
\`\`\`

### Notes
- 注意事项1
- 注意事项2

### Related Functions
- [other_function](#other_function)

### Tags
#tag1 #tag2 #tag3
```

---

## 🔧 使用指南

### 查看函数文档

1. **通过网页**: 访问 `/function-library` 页面
2. **直接阅读**: 在 GitHub 或本地打开对应的 `.md` 文件
3. **搜索**: 使用 grep 或编辑器搜索功能

### 更新现有函数文档

1. 定位文件: `docs/functions/backend/<function_name>.md`
2. 编辑文件内容
3. 保存文件
4. 刷新网页 - 更改自动生效

### 添加新函数文档

1. 创建新文件: `docs/functions/backend/<function_name>.md`
2. 按照标准格式编写文档
3. 保存文件
4. 函数将自动出现在 Function Library 页面

### 搜索函数

```bash
# 搜索函数名
grep -r "function_name" docs/functions/backend/

# 搜索标签
grep -r "#tag" docs/functions/backend/

# 搜索分类
grep -r "Category: API Endpoint" docs/functions/backend/
```

---

## ✨ 优势

### 一文件一函数的优势

1. **更清晰**: 每个文件专注于一个函数，避免混乱
2. **易查找**: 通过文件名直接定位函数文档
3. **易维护**: 修改单个函数不影响其他文档
4. **易协作**: 多人可同时编辑不同函数的文档
5. **版本控制**: Git diff 更清晰，冲突更少

### 与代码的关联

```
backend/main.py                    docs/functions/backend/
├── def search_games()     →      ├── search_games.md
├── def apply_fusion_ranking() → ├── apply_fusion_ranking.md
└── def validate_query()   →      └── validate_search_query.md
```

---

## 📈 文档统计

| 指标 | 数值 |
|------|------|
| 总函数数 | 12 |
| API 端点 | 4 |
| 搜索算法 | 4 |
| 数据访问 | 4 |
| 高复杂度 | 4 |
| 中复杂度 | 5 |
| 低复杂度 | 3 |

---

## 🔄 迁移说明

### 旧格式 → 新格式

**旧格式**（多函数文件）:
```
api_endpoints.md
  ├── search_games
  ├── get_search_suggestions
  ├── get_game_detail
  └── health_check
```

**新格式**（单函数文件）:
```
search_games.md
get_search_suggestions.md
get_game_detail.md
health_check.md
```

### 迁移工具

使用 `scripts/split_functions.py` 可以将旧格式转换为新格式：

```bash
python3 scripts/split_functions.py
```

旧文件备份在 `old_format/` 目录中。

---

## 📚 相关文档

- [README.md](../../../README.md) - 项目主文档
- [Function Library 更新日志](../../log/FUNCTION_LIBRARY_UPDATE.md) - 详细更新记录
- [测试指南](../../../test/README.md) - 测试说明

---

## 🤝 贡献指南

### 编写新函数文档

1. **遵循格式**: 使用标准 markdown 格式
2. **完整信息**: 填写所有必填字段
3. **代码示例**: 提供可运行的示例
4. **清晰描述**: 用简洁语言解释功能
5. **添加标签**: 便于搜索和分类

### 审查清单

- [ ] 函数名称与文件名一致
- [ ] 包含所有必填字段
- [ ] 代码示例可运行
- [ ] 参数描述完整
- [ ] 返回值说明清楚
- [ ] 添加相关函数链接
- [ ] 标签合理准确

---

## 📞 获取帮助

遇到问题？

1. 查看 [DEVELOPMENT.md](../../../DEVELOPMENT.md) 开发指南
2. 查看现有函数文档作为参考
3. 通过课程渠道联系开发团队

---

**最后更新**: 2024-10-10
**维护者**: INST326 开发团队


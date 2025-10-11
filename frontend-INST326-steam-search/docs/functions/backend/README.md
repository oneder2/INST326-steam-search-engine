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
├── api-endpoints/                 # API端点函数
│   ├── category.json
│   ├── search_games.md
│   ├── get_search_suggestions.md
│   ├── get_game_detail.md
│   └── health_check.md
├── search-algorithms/             # 搜索算法函数
│   ├── category.json
│   ├── search_bm25_index.md
│   ├── search_faiss_index.md
│   ├── apply_fusion_ranking.md
│   └── merge_search_results.md
├── data-access/                   # 数据访问函数
│   ├── category.json
│   ├── get_game_by_id.md
│   ├── get_games_by_ids.md
│   ├── load_bm25_index.md
│   ├── load_faiss_index.md
│   └── search_games_by_title.md
├── validation/                    # 验证函数
│   ├── category.json
│   ├── validate_search_query.md
│   └── detect_malicious_patterns.md
├── configuration/                 # 配置管理函数
│   ├── category.json
│   ├── get_settings.md
│   └── validate_configuration.md
├── utilities/                     # 工具函数
│   ├── category.json
│   ├── sanitize_input.md
│   ├── tokenize_text.md
│   ├── normalize_text.md
│   └── log_security_event.md
└── caching/                       # 缓存管理函数
    ├── category.json
    ├── cache_search_results.md
    └── clear_search_cache.md
```

---

## 📊 函数分类

### API Endpoints（API 端点）- 4 个函数
| 函数名 | 文件 | 复杂度 | 说明 |
|--------|------|--------|------|
| `search_games` | [api-endpoints/search_games.md](api-endpoints/search_games.md) | High | 主搜索端点 |
| `get_search_suggestions` | [api-endpoints/get_search_suggestions.md](api-endpoints/get_search_suggestions.md) | Medium | 搜索建议 |
| `get_game_detail` | [api-endpoints/get_game_detail.md](api-endpoints/get_game_detail.md) | Low | 游戏详情 |
| `health_check` | [api-endpoints/health_check.md](api-endpoints/health_check.md) | Low | 健康检查 |

### Search Algorithms（搜索算法）- 4 个函数
| 函数名 | 文件 | 复杂度 | 说明 |
|--------|------|--------|------|
| `search_bm25_index` | [search-algorithms/search_bm25_index.md](search-algorithms/search_bm25_index.md) | Medium | BM25关键词搜索 |
| `search_faiss_index` | [search-algorithms/search_faiss_index.md](search-algorithms/search_faiss_index.md) | High | Faiss语义搜索 |
| `apply_fusion_ranking` | [search-algorithms/apply_fusion_ranking.md](search-algorithms/apply_fusion_ranking.md) | High | 融合排序算法 |
| `merge_search_results` | [search-algorithms/merge_search_results.md](search-algorithms/merge_search_results.md) | Medium | 搜索结果合并 |

### Data Access（数据访问）- 5 个函数
| 函数名 | 文件 | 复杂度 | 说明 |
|--------|------|--------|------|
| `get_game_by_id` | [data-access/get_game_by_id.md](data-access/get_game_by_id.md) | Low | 按ID获取游戏 |
| `get_games_by_ids` | [data-access/get_games_by_ids.md](data-access/get_games_by_ids.md) | Medium | 批量获取游戏 |
| `load_bm25_index` | [data-access/load_bm25_index.md](data-access/load_bm25_index.md) | Medium | 加载BM25索引 |
| `load_faiss_index` | [data-access/load_faiss_index.md](data-access/load_faiss_index.md) | High | 加载Faiss索引 |
| `search_games_by_title` | [data-access/search_games_by_title.md](data-access/search_games_by_title.md) | Medium | 按标题搜索游戏 |

### Validation（验证）- 2 个函数
| 函数名 | 文件 | 复杂度 | 说明 |
|--------|------|--------|------|
| `validate_search_query` | [validation/validate_search_query.md](validation/validate_search_query.md) | Medium | 查询验证 |
| `detect_malicious_patterns` | [validation/detect_malicious_patterns.md](validation/detect_malicious_patterns.md) | Medium | 恶意模式检测 |

### Configuration（配置管理）- 2 个函数
| 函数名 | 文件 | 复杂度 | 说明 |
|--------|------|--------|------|
| `get_settings` | [configuration/get_settings.md](configuration/get_settings.md) | Medium | 获取应用设置 |
| `validate_configuration` | [configuration/validate_configuration.md](configuration/validate_configuration.md) | Medium | 配置验证 |

### Utilities（工具函数）- 4 个函数
| 函数名 | 文件 | 复杂度 | 说明 |
|--------|------|--------|------|
| `sanitize_input` | [utilities/sanitize_input.md](utilities/sanitize_input.md) | Low | 输入清理 |
| `tokenize_text` | [utilities/tokenize_text.md](utilities/tokenize_text.md) | Medium | 文本分词 |
| `normalize_text` | [utilities/normalize_text.md](utilities/normalize_text.md) | Low | 文本标准化 |
| `log_security_event` | [utilities/log_security_event.md](utilities/log_security_event.md) | Low | 安全事件日志 |

### Caching（缓存管理）- 2 个函数
| 函数名 | 文件 | 复杂度 | 说明 |
|--------|------|--------|------|
| `cache_search_results` | [caching/cache_search_results.md](caching/cache_search_results.md) | Medium | 缓存搜索结果 |
| `clear_search_cache` | [caching/clear_search_cache.md](caching/clear_search_cache.md) | Low | 清理搜索缓存 |

**总计**: 23 个函数

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
| 总函数数 | 23 |
| API 端点 | 4 |
| 搜索算法 | 4 |
| 数据访问 | 5 |
| 验证 | 2 |
| 配置管理 | 2 |
| 工具函数 | 4 |
| 缓存管理 | 2 |
| 高复杂度 | 3 |
| 中复杂度 | 12 |
| 低复杂度 | 8 |

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

**最后更新**: 2024-10-11
**维护者**: INST326 开发团队

---

## 🆕 最新更新 (2024-10-11)

### 新增函数分类
- **Configuration（配置管理）**: 2个函数，用于应用配置和验证
- **Utilities（工具函数）**: 4个函数，提供通用工具和安全功能
- **Caching（缓存管理）**: 2个函数，实现搜索结果缓存和管理

### 新增核心函数
1. `merge_search_results` - 搜索结果合并算法
2. `search_games_by_title` - 按标题搜索游戏（支持模糊匹配）
3. `detect_malicious_patterns` - 恶意模式检测和安全防护
4. `get_settings` - 应用配置管理
5. `validate_configuration` - 配置验证
6. `sanitize_input` - 输入清理和安全处理
7. `tokenize_text` - 文本分词和预处理
8. `normalize_text` - 文本标准化
9. `log_security_event` - 安全事件日志记录
10. `cache_search_results` - 搜索结果缓存
11. `clear_search_cache` - 缓存清理和管理

### 函数库扩展成果
- **函数总数**: 从12个增加到23个（增长92%）
- **分类数量**: 从4个增加到7个
- **覆盖范围**: 完整覆盖API、搜索、数据、验证、配置、工具、缓存等所有核心功能
- **实用性**: 所有函数都有完整的实现示例和使用说明


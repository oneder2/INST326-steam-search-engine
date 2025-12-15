# Steam Game Search Engine - 项目技术栈与API规范文档

## 📋 项目基本信息

### 项目概述
- **项目名称**: Steam Game Search Engine (Steam游戏搜索引擎)
- **项目类型**: 学术项目 (INST326 - Object-Oriented Programming)
- **机构**: 马里兰大学 (University of Maryland)
- **架构模式**: Monorepo微服务架构
- **开发语言**: 前端 TypeScript/React, 后端 Python

### 项目目标
构建一个智能游戏发现平台，结合高级搜索算法与现代Web技术，帮助用户找到他们喜欢的Steam游戏。

### 核心功能
1. **智能搜索**: 结合BM25关键词匹配与语义向量搜索
2. **融合排名**: 平衡相关性、评价质量和玩家活跃度的算法
3. **高级过滤**: 价格、平台、多人类型、Steam Deck兼容性等全面过滤器
4. **现代界面**: 响应式、Steam主题的UI，使用React和TypeScript构建

---

## 🛠️ 技术栈详解

### 前端技术栈 (Next.js)

#### 核心框架
- **Next.js 14**: React框架，支持SSR和路由
- **TypeScript**: 类型安全的JavaScript开发
- **React Hooks**: 现代状态管理

#### UI与样式
- **Tailwind CSS**: 工具优先的CSS框架，Steam主题
- **响应式设计**: 移动优先方法

#### HTTP客户端
- **Axios**: 用于与FastAPI后端通信的HTTP客户端
- **请求拦截器**: 自动错误处理和日志记录
- **响应拦截器**: 统一错误处理

#### 开发工具
- **ESLint**: 代码检查和质量检查
- **Prettier**: 代码格式化
- **Jest**: 单元测试框架
- **TypeScript Compiler**: 类型检查

### 后端技术栈 (Python FastAPI)

#### 核心框架
- **FastAPI**: 高性能Python Web框架
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI服务器，用于生产部署

#### 数据库
- **Supabase (PostgreSQL)**: 主要数据库，用于游戏元数据（标题、描述、价格、类型）
- **SQLite**: 本地开发的备用数据库选项（向后兼容）

#### 搜索引擎
- **Faiss**: 向量相似度搜索库，用于语义搜索
- **BM25**: 关键词搜索算法实现
- **Sentence Transformers**: 文本嵌入生成

#### 数据处理
- **异步编程**: asyncio用于异步数据库操作
- **连接池**: 数据库连接管理

---

## 🔄 数据传输策略

### 1. 前端 → 后端数据传输

#### 请求格式
- **协议**: HTTP/HTTPS
- **方法**: GET, POST
- **内容类型**: `application/json`
- **编码**: UTF-8

#### 请求头规范
```typescript
{
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'User-Agent': 'Steam-Search-Engine-Frontend/1.0'
}
```

#### 请求体结构
所有POST请求使用JSON格式，遵循Pydantic Schema定义。

#### 超时配置
- **默认超时**: 10秒 (10000ms)
- **重试策略**: 3次重试，每次间隔1秒

### 2. 后端 → 前端数据传输

#### 响应格式
- **内容类型**: `application/json`
- **状态码**: 遵循RESTful标准
- **编码**: UTF-8

#### 响应头
```http
Content-Type: application/json
X-Process-Time: 0.125
X-API-Version: 1.0.0
```

#### 成功响应结构
```json
{
  "data": { /* 响应数据 */ },
  "status": 200,
  "headers": { /* 响应头 */ },
  "timestamp": 1234567890
}
```

#### 错误响应结构
```json
{
  "error_code": 4001,
  "message": "Invalid search query",
  "details": "Query cannot be empty"
}
```

### 3. 后端 → 数据库数据传输

#### Supabase (PostgreSQL)
- **连接方式**: 通过Supabase客户端库
- **连接池**: 自动管理
- **查询方式**: SQL查询，返回JSON格式
- **数据类型映射**: 
  - PostgreSQL INTEGER → Python int
  - PostgreSQL TEXT → Python str
  - PostgreSQL JSONB → Python List/Dict

#### SQLite (备用)
- **连接方式**: sqlite3库，异步上下文管理器
- **连接池**: 自定义连接池管理
- **查询方式**: SQL查询，使用Row工厂模式
- **数据类型映射**: 
  - SQLite INTEGER → Python int
  - SQLite TEXT → Python str
  - SQLite JSON → Python List/Dict (通过json.loads)

### 4. 搜索索引数据传输

#### Faiss向量索引
- **存储格式**: 二进制文件 (.faiss)
- **加载时机**: 应用启动时一次性加载
- **内存管理**: 常驻内存，支持快速向量搜索
- **数据流**: 
  1. 启动时从文件加载到内存
  2. 搜索时在内存中执行向量相似度计算
  3. 返回游戏ID和相似度分数

#### BM25关键词索引
- **存储格式**: Pickle文件 (.pkl)
- **加载时机**: 应用启动时一次性加载
- **内存管理**: 常驻内存，支持快速关键词匹配
- **数据流**: 
  1. 启动时从文件加载到内存
  2. 搜索时在内存中执行BM25评分计算
  3. 返回游戏ID和BM25分数

---

## 📡 API调用规范

### API基础配置

#### 基础URL
- **开发环境**: `http://localhost:8000`
- **生产环境**: 通过环境变量 `NEXT_PUBLIC_API_BASE_URL` 配置

#### API版本
- **当前版本**: `/api/v1`
- **版本前缀**: 所有API端点以 `/api/v1` 开头

#### 认证
- **当前状态**: 无需认证（开发阶段）
- **未来扩展**: 预留认证头支持（TODO注释标记）

---

### 核心API端点

#### 1. 游戏搜索 API

**端点**: `POST /api/v1/search/games`

**请求体 (SearchQuerySchema)**:
```json
{
  "query": "roguelike games",
  "filters": {
    "price_max": 30,
    "coop_type": "Local",
    "platform": ["Windows", "SteamDeck"],
    "genres": ["Action", "Adventure"],
    "review_status": "Very Positive",
    "deck_compatible": true
  },
  "limit": 20,
  "offset": 0
}
```

**字段说明**:
- `query` (string, 必填): 搜索查询文本，1-200字符
- `filters` (object, 可选): 过滤器对象
  - `price_max` (integer, 可选): 最大价格（美元），0-1000
  - `coop_type` (enum, 可选): 合作类型 - "Local", "Online", "Both", "None"
  - `platform` (array, 可选): 平台列表 - ["Windows", "SteamDeck", "Mac", "Linux"]，最多3个
  - `genres` (array, 可选): 游戏类型列表，最多5个
  - `review_status` (string, 可选): 评价状态
  - `deck_compatible` (boolean, 可选): Steam Deck兼容性
- `limit` (integer, 可选): 每页结果数，1-100，默认20
- `offset` (integer, 可选): 分页偏移量，默认0

**成功响应 (200)**:
```json
{
  "results": [
    {
      "game_id": 12345,
      "title": "Epic Adventure Game",
      "description": "An amazing action-adventure game",
      "price": 29.99,
      "genres": ["Action", "Adventure"],
      "coop_type": "online",
      "deck_comp": true,
      "review_status": "Very Positive",
      "release_date": "2023-06-15",
      "developer": "Amazing Studios",
      "publisher": "Great Games Inc",
      "relevance_score": 0.95,
      "bm25_score": 8.5,
      "semantic_score": 0.87
    }
  ],
  "total": 150,
  "offset": 0,
  "limit": 20,
  "query": "roguelike games",
  "filters": {
    "price_max": 30,
    "coop_type": "Local",
    "platform": ["Windows", "SteamDeck"]
  },
  "search_time": 0.125
}
```

**错误响应**:
- `400 Bad Request`: 无效的搜索查询
  ```json
  {
    "error_code": 4001,
    "message": "Invalid search query",
    "details": "Query cannot be empty"
  }
  ```
- `500 Internal Server Error`: 内部服务器错误
  ```json
  {
    "error_code": 5000,
    "message": "Internal search error",
    "details": "Search engine not initialized"
  }
  ```

**前端调用示例**:
```typescript
import { searchGames } from '@/services/api';

const response = await searchGames({
  query: "roguelike games",
  filters: {
    price_max: 30,
    coop_type: "Local",
    platform: ["Windows", "SteamDeck"]
  },
  limit: 20,
  offset: 0
});

// 访问结果
const games = response.data.results;
const total = response.data.total;
```

---

#### 2. 搜索建议 API

**端点**: `GET /api/v1/search/suggest`

**查询参数**:
- `prefix` (string, 必填): 搜索前缀，1-100字符
- `limit` (integer, 可选): 建议数量，1-20，默认10

**请求示例**:
```
GET /api/v1/search/suggest?prefix=action&limit=10
```

**成功响应 (200)**:
```json
{
  "suggestions": [
    "action games",
    "action adventure",
    "action rpg",
    "action shooter"
  ],
  "prefix": "action",
  "suggestion_types": {
    "games": ["Action Game 1", "Action Game 2"],
    "genres": ["Action", "Action-Adventure"],
    "developers": ["Action Studios"]
  }
}
```

**错误响应**:
- `400 Bad Request`: 无效的前缀
- `500 Internal Server Error`: 内部服务器错误

**前端调用示例**:
```typescript
import { getSearchSuggestions } from '@/services/api';

const response = await getSearchSuggestions("action");
const suggestions = response.data.suggestions;
```

---

#### 3. 游戏详情 API

**端点**: `GET /api/v1/games/{game_id}`

**路径参数**:
- `game_id` (integer, 必填): Steam游戏ID，必须为正整数

**请求示例**:
```
GET /api/v1/games/12345
```

**成功响应 (200)**:
```json
{
  "game_id": 12345,
  "title": "Epic Adventure Game",
  "description": "Short description",
  "full_description": "Detailed description...",
  "price": 29.99,
  "genres": ["Action", "Adventure", "RPG"],
  "tags": ["Singleplayer", "Story Rich"],
  "coop_type": "online",
  "deck_comp": true,
  "supported_platforms": ["Windows", "Mac", "Linux"],
  "review_status": "Very Positive",
  "review_summary": {
    "total_reviews": 15000,
    "positive_percentage": 87
  },
  "release_date": "2023-06-15",
  "developer": "Amazing Studios",
  "publisher": "Great Games Inc",
  "screenshots": [
    "https://example.com/screenshot1.jpg"
  ],
  "additional_info": {
    "last_updated": 1234567890,
    "data_source": "supabase"
  }
}
```

**错误响应**:
- `400 Bad Request`: 无效的游戏ID
- `404 Not Found`: 游戏未找到
- `500 Internal Server Error`: 内部服务器错误

**前端调用示例**:
```typescript
import { getGameDetail } from '@/services/api';

const response = await getGameDetail(12345);
const game = response.data;
```

---

#### 4. 健康检查 API

**端点**: `GET /api/v1/health`

**请求示例**:
```
GET /api/v1/health
```

**成功响应 (200)**:
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "search_engine": "initialized",
    "indices": "loaded"
  }
}
```

**前端调用示例**:
```typescript
import { checkApiHealth } from '@/services/api';

const response = await checkApiHealth();
const health = response.data;
```

---

#### 5. 热门游戏 API

**端点**: `GET /api/v1/search/popular`

**查询参数**:
- `limit` (integer, 可选): 游戏数量，1-50，默认10

**请求示例**:
```
GET /api/v1/search/popular?limit=10
```

**成功响应 (200)**:
```json
[
  {
    "game_id": 12345,
    "title": "Popular Game",
    "description": "Game description",
    "price": 29.99,
    "genres": ["Action"],
    "review_status": "Very Positive"
  }
]
```

---

#### 6. 按类型获取游戏 API

**端点**: `GET /api/v1/search/genres/{genre}`

**路径参数**:
- `genre` (string, 必填): 游戏类型名称

**查询参数**:
- `limit` (integer, 可选): 游戏数量，1-50，默认20

**请求示例**:
```
GET /api/v1/search/genres/Action?limit=20
```

**成功响应 (200)**:
```json
[
  {
    "game_id": 12345,
    "title": "Action Game",
    "description": "Game description",
    "price": 29.99,
    "genres": ["Action"],
    "review_status": "Very Positive"
  }
]
```

---

#### 7. 相似游戏推荐 API

**端点**: `GET /api/v1/games/{game_id}/similar`

**路径参数**:
- `game_id` (integer, 必填): Steam游戏ID

**查询参数**:
- `limit` (integer, 可选): 推荐数量，默认5

**请求示例**:
```
GET /api/v1/games/12345/similar?limit=5
```

**成功响应 (200)**:
```json
[
  {
    "game_id": 12346,
    "title": "Similar Game",
    "description": "Game description",
    "price": 24.99,
    "genres": ["Action", "Adventure"],
    "review_status": "Positive"
  }
]
```

---

#### 8. 游戏评价信息 API

**端点**: `GET /api/v1/games/{game_id}/reviews`

**路径参数**:
- `game_id` (integer, 必填): Steam游戏ID

**请求示例**:
```
GET /api/v1/games/12345/reviews
```

**成功响应 (200)**:
```json
{
  "game_id": 12345,
  "game_title": "Epic Adventure Game",
  "review_status": "Very Positive",
  "review_summary": {
    "overall_status": "Very Positive",
    "recommendation_percentage": 85,
    "total_reviews": 25000,
    "recent_reviews": "Very Positive"
  },
  "review_breakdown": {
    "positive": 21250,
    "negative": 3750,
    "total": 25000
  },
  "last_updated": 1234567890
}
```

---

## 🔄 完整数据流程

### 搜索流程数据流

```
用户输入查询
    ↓
前端组件 (React)
    ↓
API客户端 (Axios)
    ↓ HTTP POST /api/v1/search/games
    ↓ JSON请求体
后端路由 (FastAPI)
    ↓
请求验证 (Pydantic)
    ↓
搜索引擎控制器 (GameSearchEngine)
    ↓
并行执行:
    ├─ BM25搜索 (内存索引)
    ├─ 语义搜索 (Faiss向量索引)
    └─ 数据库查询 (Supabase/SQLite)
    ↓
融合排名算法
    ↓
应用过滤器
    ↓
格式化响应 (Pydantic)
    ↓ HTTP 200 + JSON响应体
前端接收响应
    ↓
更新UI状态
    ↓
渲染搜索结果
```

### 游戏详情流程数据流

```
用户点击游戏
    ↓
前端组件 (React)
    ↓
API客户端 (Axios)
    ↓ HTTP GET /api/v1/games/{game_id}
后端路由 (FastAPI)
    ↓
参数验证 (Pydantic Path)
    ↓
搜索引擎控制器
    ↓
数据库查询 (Supabase/SQLite)
    ↓
格式化响应 (Pydantic)
    ↓ HTTP 200 + JSON响应体
前端接收响应
    ↓
更新UI状态
    ↓
渲染游戏详情页面
```

---

## 📊 数据模型映射

### 前端TypeScript类型 ↔ 后端Pydantic模型

| 前端类型 | 后端模型 | 说明 |
|---------|---------|------|
| `SearchQuerySchema` | `SearchQuerySchema` | 搜索查询请求 |
| `GameResultSchema` | `GameResultSchema` | 搜索结果响应 |
| `GameDetailResponse` | `GameDetailResponse` | 游戏详情响应 |
| `SearchSuggestionsResponse` | `SearchSuggestionsResponse` | 搜索建议响应 |
| `ErrorResponse` | `ErrorResponse` | 错误响应 |

### 数据库模型 ↔ API模型

| 数据库字段 | API字段 | 类型转换 |
|-----------|---------|---------|
| `game_id` | `game_id` | INTEGER → int |
| `title` | `title` | TEXT → str |
| `description` | `description` | TEXT → str |
| `price` | `price` | REAL → float |
| `genres` | `genres` | JSONB → List[str] |
| `coop_type` | `coop_type` | TEXT → Optional[str] |
| `deck_comp` | `deck_comp` | BOOLEAN → bool |
| `review_status` | `review_status` | TEXT → str |

---

## 🛡️ 错误处理规范

### HTTP状态码映射

| HTTP状态码 | 错误码 | 场景 |
|-----------|--------|------|
| 200 | - | 成功响应 |
| 400 | 4001 | 参数验证失败 |
| 404 | 4004 | 资源未找到 |
| 429 | 4290 | 请求频率限制 |
| 500 | 5000 | 内部服务器错误 |
| 503 | - | 服务不可用（搜索引擎未初始化） |

### 前端错误处理

```typescript
try {
  const response = await searchGames(query);
  // 处理成功响应
} catch (error: ApiError) {
  if (error.status === 400) {
    // 处理客户端错误
  } else if (error.status === 500) {
    // 处理服务器错误
  } else {
    // 处理其他错误
  }
}
```

### 后端错误处理

```python
try:
    # 执行搜索
    results = await search_engine.search_games(...)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
except NotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
except Exception as e:
    logger.error(f"Search error: {str(e)}")
    raise HTTPException(status_code=500, detail="Internal search error")
```

---

## 🔐 安全规范

### 输入验证
- **前端**: TypeScript类型检查 + 运行时验证
- **后端**: Pydantic模型验证 + 自定义验证器

### 数据清理
- **查询字符串**: 自动去除多余空格，限制长度
- **过滤器**: 验证枚举值，限制数组长度
- **路径参数**: 验证整数范围

### CORS配置
```python
allow_origins=["http://localhost:3000", "https://production-domain.com"]
allow_credentials=True
allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allow_headers=["*"]
```

---

## 📈 性能优化策略

### 前端优化
- **请求去抖**: 搜索输入300ms延迟
- **响应缓存**: 
  - 搜索结果: 5分钟TTL
  - 游戏详情: 30分钟TTL
  - 搜索建议: 1小时TTL
- **分页加载**: 默认20条，最大100条

### 后端优化
- **索引预加载**: 启动时一次性加载所有索引到内存
- **数据库连接池**: 复用数据库连接
- **异步处理**: 使用async/await进行并发操作
- **响应压缩**: 自动压缩JSON响应

---

## 📝 日志记录规范

### 前端日志
- **开发环境**: 控制台输出所有API请求
- **生产环境**: 仅记录错误

### 后端日志
- **请求日志**: 记录所有API请求（方法、路径、状态码、耗时）
- **搜索日志**: 记录搜索查询、结果数量、耗时
- **错误日志**: 记录异常堆栈信息
- **性能日志**: 记录关键操作的执行时间

---

## 🔄 版本控制

### API版本
- **当前版本**: v1
- **版本前缀**: `/api/v1`
- **向后兼容**: 新版本保持向后兼容

### 数据模型版本
- **Pydantic模型**: 通过字段可选性保持兼容
- **数据库迁移**: 通过Supabase迁移工具管理

---

## 📚 相关文档

- [API契约文档](API-contract-backend.md)
- [前端开发指南](../frontend-INST326-steam-search/DEVELOPMENT.md)
- [后端README](../backend-INST326-steam-search/README.md)
- [主项目README](../../README.md)

---

**文档版本**: 1.0.0  
**最后更新**: 2024-12-19  
**维护者**: INST326开发团队


# Steam Game Search Engine - Backend

Python FastAPI后端服务，为Steam游戏搜索引擎项目提供智能搜索功能。

## 项目概述 / Overview

本后端提供智能游戏搜索功能，使用以下技术：
- **BM25算法**: 基于关键词的搜索
- **Faiss向量搜索**: 语义相似度搜索
- **融合排序**: 结合两种搜索方法获得最优结果

This backend provides intelligent game search capabilities using:
- **BM25 Algorithm**: For keyword-based search
- **Faiss Vector Search**: For semantic similarity search
- **Fusion Ranking**: Combines both search methods for optimal results

## 功能特性 / Features

- 🔍 **混合搜索**: BM25 + 语义搜索与融合排序
- 🎮 **游戏数据库**: 包含全面游戏元数据的SQLite数据库
- 🚀 **快速API**: 高性能异步端点
- 📊 **健康监控**: 内置健康检查和状态监控
- 🔧 **可配置**: 基于环境变量的配置
- 📚 **自动文档**: Swagger/OpenAPI文档位于 `/docs`

## 快速开始 / Quick Start

### 前置要求 / Prerequisites

- Python 3.13+ (已更新依赖库以支持Python 3.13)
- pip 或 conda

### 安装步骤 / Installation

1. **克隆仓库 / Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend-INST326-steam-search
   ```

2. **安装依赖 / Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **设置环境 / Set up environment**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件配置你的设置 / Edit .env with your configuration
   ```

4. **运行服务器 / Run the server**
   ```bash
   python main.py
   ```

API将在 `http://localhost:8000` 可用

## 📋 API Endpoints

### Core Endpoints

#### Search Games
```bash
POST /api/v1/search/games
Content-Type: application/json

{
  "query": "roguelike games",
  "filters": {
    "price_max": 30,
    "coop_type": "Local",
    "platform": ["Windows", "SteamDeck"]
  },
  "limit": 20,
  "offset": 0
}
```

#### Get Game Details
```bash
GET /api/v1/games/{game_id}
```

#### Search Suggestions
```bash
GET /api/v1/search/suggest?prefix=rogue
```

#### Health Check
```bash
GET /api/v1/health
```

## 架构 / Architecture

### 核心组件 / Core Components

1. **FastAPI应用** (`main.py`)
   - API端点和请求处理
   - 中间件配置
   - 错误处理

2. **搜索算法** (`search_algorithms.py`)
   - BM25关键词搜索实现
   - Faiss语义搜索与嵌入
   - 融合排序算法

3. **数据库层** (`database.py`)
   - SQLite数据库操作
   - 游戏数据模型和查询
   - 连接管理

4. **配置管理** (`config.py`)
   - 环境变量管理
   - 设置验证
   - 功能开关

### 搜索流程 / Search Flow

1. **查询验证**: 输入清理和验证
2. **并行搜索**: BM25和Faiss搜索并发运行
3. **融合排序**: 使用加权评分合并结果
4. **过滤**: 应用用户指定的过滤器
5. **分页**: 返回分页结果

## 🧪 Testing

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test search endpoint
curl -X POST http://localhost:8000/api/v1/search/games \
  -H "Content-Type: application/json" \
  -d '{"query": "roguelike games", "limit": 5}'

# Test game details
curl http://localhost:8000/api/v1/games/1
```

## 最新更新 / Latest Updates

### 2024-10-11 - Python 3.13兼容性更新

✅ **依赖库版本更新**:
- `faiss-cpu`: 1.8.0 → 1.12.0 (支持Python 3.13)
- `fastapi`: 0.104.1 → 0.118.3 (支持Python 3.13)
- `pydantic`: 2.5.0 → 2.12.0 (支持Python 3.13)
- `numpy`: 1.24.3 → 2.3.3 (支持Python 3.13)
- `scikit-learn`: 1.3.2 → 1.7.2 (支持Python 3.13)
- `sentence-transformers`: 2.2.2 → 5.1.1 (最新版本)

✅ **核心功能实现**:
- 完整的搜索算法模块（BM25 + Faiss + 融合排序）
- 数据库访问层与异步操作
- 配置管理系统
- 健康检查和监控
- API端点完整实现
- 错误处理和日志记录

✅ **开发工具**:
- API测试脚本 (`test_api.py`)
- 环境变量配置模板
- 详细的中文和英文注释

### 部署 / Deployment

#### 本地开发 / Local Development

```bash
# 安装依赖 / Install dependencies
pip install -r requirements.txt

# 使用自动重载运行 / Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 生产部署 / Production Deployment

```bash
# 安装生产依赖 / Install production dependencies
pip install -r requirements.txt

# 使用Gunicorn运行（推荐）/ Run with Gunicorn (recommended)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Render部署 / Render Deployment

项目已配置为在Render平台部署，支持Python 3.13环境。

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

1. **导入错误**: 确保所有依赖都已安装
   ```bash
   pip install -r requirements.txt
   ```

2. **数据库未找到**: 检查 `.env` 中的 `DATABASE_URL`
   ```bash
   # 验证数据库文件存在 / Verify database file exists
   ls -la data/games_data.db
   ```

3. **搜索索引缺失**: 如果缺失，索引将自动创建
   ```bash
   # 检查索引文件 / Check index files
   ls -la data/*.faiss data/*.pkl
   ```

4. **端口已被使用**: 在 `.env` 中更改端口或终止现有进程
   ```bash
   # 查找使用端口8000的进程 / Find process using port 8000
   lsof -i :8000
   ```

### 调试模式 / Debug Mode

启用调试模式以获取详细错误信息：

```bash
# 在 .env 文件中 / In .env file
DEBUG=true
LOG_LEVEL=DEBUG
```

## 贡献 / Contributing

1. Fork仓库
2. 创建功能分支
3. 进行更改
4. 为新功能添加测试
5. 运行测试套件
6. 提交拉取请求

## 许可证 / License

本项目是INST326课程作业的一部分。

## 支持 / Support

如有问题或疑问：
1. 查看故障排除部分
2. 查看 `/docs` 的API文档
3. 通过课程渠道联系开发团队

---

## 🆕 最新更新 (2024-10-11)

### 函数库扩展完成
- ✅ **新增 `utilities.py` 模块**: 包含工具函数和安全功能
- ✅ **实现输入清理**: `sanitize_input()` 函数防止XSS和注入攻击
- ✅ **恶意模式检测**: `detect_malicious_patterns()` 函数检测安全威胁
- ✅ **文本处理功能**: `normalize_text()` 和 `tokenize_text()` 函数
- ✅ **安全事件日志**: `log_security_event()` 函数记录安全事件
- ✅ **搜索结果合并**: `merge_search_results()` 函数合并多算法结果
- ✅ **按标题搜索**: `search_games_by_title()` 函数支持模糊匹配
- ✅ **前后端同步**: 与前端function-library文档完全同步

### 函数库统计
- **总函数数**: 23个（满足作业要求的15+个函数）
- **分类数量**: 7个（API端点、搜索算法、数据访问、验证、配置、工具、缓存）
- **实现状态**: 所有核心函数都有完整的代码实现和文档
- **测试覆盖**: 所有API端点都通过了集成测试

### 技术亮点
- **模块化架构**: 清晰分离不同功能模块
- **安全防护**: 全面的输入验证和恶意模式检测
- **异步支持**: 全面使用async/await提高性能
- **错误处理**: 完善的异常处理和日志记录
- **类型安全**: 使用Pydantic进行数据验证
- **文档完善**: 中英文双语注释和详细文档

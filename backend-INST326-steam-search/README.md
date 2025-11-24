# Steam Game Search Engine - Backend (面向对象重构版)

Python FastAPI后端服务，为Steam游戏搜索引擎项目提供智能搜索功能。**已重构为面向对象架构，满足INST326课程要求。**

## 项目概述 / Overview

本后端采用**面向对象设计**，提供智能游戏搜索功能，使用以下技术：
- **BM25算法**: 基于关键词的搜索（模拟实现）
- **语义搜索**: 基于游戏类型和描述的相似度搜索（模拟实现）
- **融合排序**: 结合两种搜索方法获得最优结果
- **面向对象架构**: 6个核心类，体现OOP设计原则

This backend uses **Object-Oriented Design** to provide intelligent game search capabilities:
- **BM25 Algorithm**: For keyword-based search (mock implementation)
- **Semantic Search**: For genre and description similarity search (mock implementation)
- **Fusion Ranking**: Combines both search methods for optimal results
- **OOP Architecture**: 6 core classes demonstrating OOP design principles

## 🏗️ 架构设计 / Architecture Design

### 模块化分层架构 / Modular Layered Architecture

项目采用现代化的分层模块架构，清晰分离关注点：

The project uses modern layered modular architecture with clear separation of concerns:

```
backend-INST326-steam-search/
├── app/                           # 应用核心代码 / Application core code
│   ├── __init__.py
│   ├── main.py                    # FastAPI应用入口 / FastAPI application entry point
│   ├── api/                       # API层 / API layer
│   │   ├── __init__.py
│   │   ├── routes/                # API路由 / API routes
│   │   │   ├── __init__.py
│   │   │   ├── search.py          # 搜索端点 / Search endpoints
│   │   │   ├── games.py           # 游戏端点 / Game endpoints
│   │   │   └── health.py          # 健康检查端点 / Health check endpoints
│   │   ├── schemas/               # Pydantic模型 / Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── common.py          # 通用模型 / Common models
│   │   │   ├── game.py            # 游戏模型 / Game models
│   │   │   ├── search.py          # 搜索模型 / Search models
│   │   │   └── health.py          # 健康检查模型 / Health models
│   │   └── middleware/            # 中间件 / Middleware
│   ├── core/                      # 核心业务逻辑 / Core business logic
│   │   ├── __init__.py
│   │   ├── engine.py              # GameSearchEngine主控制器 / Main controller
│   │   ├── search/                # 搜索算法 / Search algorithms
│   │   │   ├── __init__.py
│   │   │   └── service.py         # SearchService搜索服务 / Search service
│   │   ├── security/              # 安全管理 / Security management
│   │   │   ├── __init__.py
│   │   │   └── manager.py         # SecurityManager安全管理器 / Security manager
│   │   └── monitoring/            # 监控服务 / Monitoring services
│   │       ├── __init__.py
│   │       └── health.py          # HealthMonitor健康监控 / Health monitor
│   ├── data/                      # 数据访问层 / Data access layer
│   │   ├── __init__.py
│   │   ├── models.py              # 数据模型 / Data models
│   │   ├── providers/             # 数据提供者 / Data providers
│   │   │   ├── __init__.py
│   │   │   └── mock.py            # MockDataProvider模拟数据 / Mock data provider
│   │   └── repositories/          # 仓库模式 / Repository pattern
│   │       ├── __init__.py
│   │       └── game_repository.py # GameRepository游戏仓库 / Game repository
│   ├── utils/                     # 工具函数 / Utility functions
│   │   ├── __init__.py
│   │   ├── logging.py             # 日志工具 / Logging utilities
│   │   ├── text.py                # 文本处理 / Text processing
│   │   └── validators.py          # 验证器 / Validators
│   └── config/                    # 配置管理 / Configuration management
│       ├── __init__.py
│       ├── settings.py            # 应用设置 / Application settings
│       └── constants.py           # 常量定义 / Constants definition
├── tests/                         # 测试代码 / Test code
│   ├── __init__.py
│   ├── test_restructured_api.py   # API集成测试 / API integration tests
│   ├── unit/                      # 单元测试 / Unit tests
│   ├── integration/               # 集成测试 / Integration tests
│   └── fixtures/                  # 测试数据 / Test fixtures
├── docs/                          # 文档 / Documentation
├── scripts/                       # 脚本工具 / Scripts
├── requirements/                  # 依赖管理 / Dependencies
│   ├── base.txt                   # 基础依赖 / Base dependencies
│   ├── dev.txt                    # 开发依赖 / Development dependencies
│   └── test.txt                   # 测试依赖 / Test dependencies
├── main_new.py                    # 应用入口点 / Application entry point
└── README.md                      # 项目文档 / Project documentation
```

### 架构优势 / Architecture Benefits

1. **模块化设计** / **Modular Design**
   - 清晰的职责分离 / Clear separation of responsibilities
   - 易于维护和扩展 / Easy to maintain and extend
   - 支持独立测试 / Supports independent testing

2. **分层架构** / **Layered Architecture**
   - API层：处理HTTP请求和响应 / API layer: Handles HTTP requests and responses
   - 核心层：业务逻辑和服务 / Core layer: Business logic and services
   - 数据层：数据访问和模型 / Data layer: Data access and models
   - 工具层：通用工具和配置 / Utils layer: Common utilities and configuration

3. **可扩展性** / **Scalability**
   - 新功能可以轻松添加到对应模块 / New features can be easily added to corresponding modules
   - 支持插件化架构 / Supports plugin architecture
   - 便于微服务拆分 / Easy to split into microservices

## 🏗️ 面向对象架构 / Object-Oriented Architecture

### 核心类设计 / Core Class Design

1. **`GameSearchEngine`** - 主控制器类 / Main Controller Class
   - 协调所有服务组件 / Orchestrates all service components
   - 提供统一的API接口 / Provides unified API interface
   - 管理组件生命周期 / Manages component lifecycle

2. **`MockDataProvider`** - 模拟数据提供者类 / Mock Data Provider Class
   - 提供50个多样化的游戏数据 / Provides 50 diverse game data entries
   - 模拟数据库操作 / Simulates database operations
   - 支持异步接口 / Supports async interface

3. **`SearchService`** - 搜索服务类 / Search Service Class
   - 实现BM25关键词搜索算法 / Implements BM25 keyword search algorithm
   - 实现语义搜索算法 / Implements semantic search algorithm
   - 融合排序算法 / Fusion ranking algorithm

4. **`SecurityManager`** - 安全管理类 / Security Manager Class
   - 输入验证和清理 / Input validation and sanitization
   - 恶意模式检测 / Malicious pattern detection
   - 安全事件记录 / Security event logging

5. **`HealthMonitor`** - 健康监控类 / Health Monitor Class
   - 系统组件状态监控 / System component status monitoring
   - 性能指标收集 / Performance metrics collection
   - 资源使用监控 / Resource usage monitoring

6. **`GameInfo`** - 游戏信息数据类 / Game Information Data Class
   - 增强的数据验证 / Enhanced data validation
   - 搜索文本生成 / Search text generation
   - 过滤器匹配 / Filter matching

## 功能特性 / Features

- 🔍 **混合搜索**: BM25 + 语义搜索与融合排序（模拟实现）
- 🎮 **模拟游戏数据**: 50个多样化的游戏数据用于演示
- 🚀 **快速API**: 高性能异步端点
- 📊 **健康监控**: 内置健康检查和状态监控
- 🔧 **可配置**: 基于环境变量的配置
- 📚 **自动文档**: Swagger/OpenAPI文档位于 `/docs`
- 🏗️ **面向对象**: 6个核心类，满足INST326课程要求

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

2. **创建虚拟环境 / Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   ```

3. **安装基本依赖 / Install basic dependencies**
   ```bash
   pip install fastapi uvicorn pydantic pydantic-settings psutil requests
   ```

4. **运行服务器 / Run the server**
   ```bash
   # 使用主入口点 / Use main entry point
   python3 main.py

   # 或者直接运行模块 / Or run module directly
   python3 -m app.main

   # 使用uvicorn直接运行 / Run directly with uvicorn
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **测试API / Test the API**
   ```bash
   # 运行重构后的API测试 / Run restructured API tests
   python3 tests/test_restructured_api.py

   # 或运行所有测试 / Or run all tests
   python3 -m pytest tests/
   ```

API将在 `http://localhost:8000` 可用，文档位于 `http://localhost:8000/docs`

### 🧪 测试 / Testing

#### API 测试 / API Tests

运行完整的API测试套件：
```bash
python3 tests/test_restructured_api.py
```

测试包括：
- ✅ 健康检查端点
- ✅ 游戏搜索功能（4种不同查询）
- ✅ 游戏详情获取（4个游戏ID）
- ✅ 搜索建议功能（4种前缀）

#### 继承和多态测试 / Inheritance and Polymorphism Tests

运行继承和多态的单元测试：
```bash
pytest tests/unit/test_inheritance_polymorphism.py -v
```

测试包括：
- ✅ 抽象基类测试（不能实例化抽象类）
- ✅ 继承关系测试（派生类继承自基类）
- ✅ 多态行为测试（基类引用、运行时多态）
- ✅ 方法重写测试（check_health 方法重写）
- ✅ 组合关系测试（GameRepository 包含 DataProvider）

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

## 🏗️ 面向对象设计详解 / Object-Oriented Design Details

### 继承层次结构 / Inheritance Hierarchy

项目实现了清晰的继承层次结构，满足 Project 3 的要求：

The project implements a clear inheritance hierarchy, meeting Project 3 requirements:

```
                    DataProvider (抽象基类 / Abstract Base Class)
                    - 使用 abc 模块定义抽象接口
                    - 强制派生类实现所有抽象方法
                           |
                           |
        ┌──────────────────┴──────────────────┐
        |                                      |
MockDataProvider                      DatabaseProvider
(模拟数据提供者)                        (数据库提供者)
- 实现所有抽象方法                      - 实现所有抽象方法
- 重写 check_health()                  - 重写 check_health()
- 调用 super().__init__()              - 调用 super().__init__()
```

**继承关系特点**:
- ✅ 基类使用 `ABC` 和 `@abstractmethod` 定义抽象接口
- ✅ 2个派生类（MockDataProvider, DatabaseProvider）
- ✅ 派生类实现所有抽象方法
- ✅ 使用 `super()` 调用父类构造函数
- ✅ 方法重写（check_health）

### 多态行为 / Polymorphic Behavior

项目在多处展示了多态行为：

The project demonstrates polymorphic behavior in multiple places:

**1. 类型声明多态**:
```python
# GameRepository 中使用基类类型引用
self.provider: DataProvider = MockDataProvider()  # 或 DatabaseProvider()
```

**2. 运行时多态**:
```python
# 根据配置创建不同的派生类实例
if use_mock_data:
    self.provider: DataProvider = MockDataProvider()
else:
    self.provider: DataProvider = DatabaseProvider()

# 相同的接口调用，不同的实现（多态）
game = await self.provider.get_game_by_id(1)
```

**3. 方法重写多态**:
```python
# 派生类重写基类方法
class MockDataProvider(DataProvider):
    async def check_health(self) -> bool:
        basic_health = await super().check_health()  # 调用父类方法
        # 添加派生类特定的验证逻辑
        return result
```

### 组合关系 / Composition Relationship

**GameRepository 和 DataProvider 的关系**:
- **关系类型**: 组合（Composition）
- **关系描述**: GameRepository "has-a" DataProvider
- **设计理由**: 
  - 需要在运行时切换不同的数据源
  - 保持类的单一职责
  - 降低耦合度，提高可测试性

```python
class GameRepository:
    def __init__(self, use_mock_data: bool = True):
        # 组合关系：GameRepository 包含 DataProvider 实例
        if use_mock_data:
            self.provider: DataProvider = MockDataProvider()
        else:
            self.provider: DataProvider = DatabaseProvider()
```

### 类图关系 / Class Diagram Relationships

```
                    DataProvider (抽象基类)
                           |
        ┌──────────────────┴──────────────────┐
        |                                      |
MockDataProvider                      DatabaseProvider
        │                                      │
        └──────────────────┬───────────────────┘
                           │ (组合 / Composition)
                    ┌───────────────┐
                    │GameRepository │
                    │ - provider    │
                    │   : DataProvider│
                    └───────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        |                                      |
SearchService                          GameSearchEngine
(搜索服务)                            (主控制器)
```

### 设计模式应用 / Design Patterns Applied

1. **抽象工厂模式 (Abstract Factory Pattern)**
   - `DataProvider` 作为抽象工厂
   - `MockDataProvider` 和 `DatabaseProvider` 作为具体工厂

2. **策略模式 (Strategy Pattern)**
   - `DataProvider` 定义策略接口
   - `MockDataProvider` 和 `DatabaseProvider` 是具体策略
   - `GameRepository` 使用策略

3. **模板方法模式 (Template Method Pattern)**
   - `DataProvider.check_health()` 定义算法骨架
   - 派生类可以重写特定步骤

4. **仓库模式 (Repository Pattern)**
   - `GameRepository` 抽象数据访问逻辑
   - 隐藏数据源的实现细节

### OOP原则体现 / OOP Principles Demonstrated

- **封装 (Encapsulation)**: 每个类都有明确的职责边界
- **继承 (Inheritance)**: DataProvider → MockDataProvider, DatabaseProvider
- **多态 (Polymorphism)**: 基类引用、运行时多态、方法重写
- **抽象 (Abstraction)**: 使用抽象基类定义接口契约
- **组合 (Composition)**: GameRepository 包含 DataProvider 实例

### Project 3 要求满足情况 / Project 3 Requirements Status

✅ **继承层次 (Inheritance Hierarchy)**
- 基类：DataProvider（抽象基类）
- 派生类：MockDataProvider, DatabaseProvider（2个派生类）
- 方法重写：check_health() 方法
- 使用 super() 调用父类构造函数

✅ **抽象基类 (Abstract Base Classes)**
- 使用 `abc` 模块：`from abc import ABC, abstractmethod`
- 定义抽象方法：5个抽象方法
- 强制实现：不能实例化未实现所有抽象方法的类

✅ **多态 (Polymorphism)**
- 基类类型引用：`provider: DataProvider`
- 运行时多态：根据配置创建不同的派生类实例
- 方法重写：派生类重写 check_health() 方法

✅ **组合 (Composition)**
- GameRepository "has-a" DataProvider
- 运行时可以切换不同的提供者
- 文档说明了选择组合而非继承的理由

📚 **详细文档**: 参见 `docs/ARCHITECTURE_OOP.md`

### 文件结构 / File Structure

```
backend-INST326-steam-search/
├── main.py                    # FastAPI应用入口
├── game_search_engine.py      # 主控制器类
├── mock_data_provider.py      # 模拟数据提供者类
├── search_service.py          # 搜索服务类
├── security_manager.py        # 安全管理类
├── health_monitor.py          # 健康监控类
├── database.py               # GameInfo数据类
├── config.py                 # 配置类
├── test_oop_api.py           # API测试脚本
└── requirements.txt          # 依赖列表
```

## 更新日志 / Changelog

### 2024-12-XX - Project 3: 继承、多态和组合实现

🚀 **重大更新 - 高级OOP特性实现**:
- ✅ 实现继承层次结构（DataProvider → MockDataProvider, DatabaseProvider）
- ✅ 使用抽象基类（ABC模块）强制接口实现
- ✅ 实现多态行为（基类引用、运行时多态、方法重写）
- ✅ 实现组合关系（GameRepository 包含 DataProvider）
- ✅ 添加全面的继承和多态测试
- ✅ 创建详细的架构文档（ARCHITECTURE_OOP.md）

🏗️ **架构改进**:
- 创建抽象基类 DataProvider 定义统一接口
- 重构 MockDataProvider 和 DatabaseProvider 继承基类
- 更新 GameRepository 使用多态（基类类型引用）
- 实现方法重写（check_health 方法）
- 使用 super() 调用父类构造函数

### 2024-11-02 - 面向对象架构重构

🚀 **重大更新 - OOP架构重构**:
- ✅ 创建6个核心类，满足INST326课程要求
- ✅ 实现完整的面向对象设计模式
- ✅ 50个多样化的模拟游戏数据
- ✅ 模拟BM25和语义搜索算法
- ✅ 融合排序算法实现
- ✅ 完整的API测试套件
- ✅ 所有端点100%测试通过

🏗️ **架构改进**:
- 从函数式编程转换为面向对象编程
- 使用现代FastAPI生命周期管理
- 改进的错误处理和日志记录
- 更好的代码组织和可维护性

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
# 安装开发依赖 / Install development dependencies
pip install -r requirements/development.txt

# 使用主入口点运行 / Run with main entry point
python3 main.py

# 或使用uvicorn直接运行 / Or run directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 生产部署 / Production Deployment

```bash
# 安装生产依赖 / Install production dependencies
pip install -r requirements/production.txt

# 使用Gunicorn运行（推荐）/ Run with Gunicorn (recommended)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用主入口点 / Or use main entry point
python3 main.py
```

#### Render部署 / Render Deployment

项目已优化为在Render平台部署，支持现代化的模块架构。

The project is optimized for deployment on Render platform with modern modular architecture.

**部署步骤 / Deployment Steps:**

1. **连接GitHub仓库 / Connect GitHub Repository**
   - 在Render控制台创建新的Web Service
   - 连接到您的GitHub仓库
   - Create new Web Service in Render dashboard
   - Connect to your GitHub repository

2. **配置构建设置 / Configure Build Settings**
   ```yaml
   # Build Command / 构建命令
   pip install -r requirements/production.txt

   # Start Command / 启动命令
   python3 main.py

   # 或使用Gunicorn / Or use Gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

3. **环境变量 / Environment Variables**
   ```bash
   # 必需的环境变量 / Required environment variables
   ENVIRONMENT=production
   HOST=0.0.0.0
   PORT=8000  # Render会自动设置 / Render sets this automatically
   DEBUG=false
   LOG_LEVEL=info

   # 可选的环境变量 / Optional environment variables
   API_TITLE="Steam Game Search Engine"
   API_VERSION="2.0.0"
   ```

4. **健康检查 / Health Check**
   ```bash
   # Render健康检查端点 / Render health check endpoint
   GET /api/v1/health
   ```

**Render配置文件示例 / Render Configuration Example:**

创建 `render.yaml` 文件（可选）/ Create `render.yaml` file (optional):

```yaml
services:
  - type: web
    name: steam-game-search-engine
    env: python
    buildCommand: pip install -r requirements/production.txt
    startCommand: python3 main.py
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: false
      - key: LOG_LEVEL
        value: info
    healthCheckPath: /api/v1/health
```

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

## 🔄 项目重构历程 / Project Restructuring Journey

### 重构目标 / Restructuring Goals

本项目经历了从扁平化结构到模块化架构的重构过程：

This project underwent restructuring from flat structure to modular architecture:

1. **提高可维护性** / **Improve Maintainability**
   - 从16个平铺文件重构为分层模块结构
   - Restructured from 16 flat files to layered modular structure

2. **增强可读性** / **Enhance Readability**
   - 按功能域分组，清晰的层次结构
   - Grouped by functional domains with clear hierarchy

3. **支持扩展性** / **Support Scalability**
   - 便于添加新功能和模块
   - Easy to add new features and modules

### 重构前后对比 / Before and After Comparison

**重构前 (Before Restructuring):**
```
backend-INST326-steam-search/
├── main.py
├── game_search_engine.py
├── search_service.py
├── mock_data_provider.py
├── security_manager.py
├── health_monitor.py
├── database.py
├── utilities.py
├── config.py
├── test_api.py
├── test_oop_api.py
└── ... (16+ files in root)
```

**重构后 (After Restructuring):**
```
backend-INST326-steam-search/
├── app/                    # 模块化应用结构
│   ├── api/               # API层分离
│   ├── core/              # 核心业务逻辑
│   ├── data/              # 数据访问层
│   ├── utils/             # 工具函数
│   └── config/            # 配置管理
├── tests/                 # 测试代码分离
├── docs/                  # 文档独立
└── main_new.py           # 新入口点
```

### 重构成果 / Restructuring Results

✅ **100%测试通过率** - All tests passing
✅ **模块化架构** - Modular architecture
✅ **清晰的职责分离** - Clear separation of concerns
✅ **易于维护和扩展** - Easy to maintain and extend
✅ **符合Python最佳实践** - Follows Python best practices

### 技术亮点
- **模块化架构**: 清晰分离不同功能模块
- **安全防护**: 全面的输入验证和恶意模式检测
- **异步支持**: 全面使用async/await提高性能
- **错误处理**: 完善的异常处理和日志记录
- **类型安全**: 使用Pydantic进行数据验证
- **文档完善**: 中英文双语注释和详细文档

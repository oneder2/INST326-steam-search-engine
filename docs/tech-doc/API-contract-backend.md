# **API 契约与后端实现文档 V2.2**

文件名称： Steam Game Search Engine \- API 契约 V2.2  
创建人：

创建日期： 2025/10/05  
关联 SRS/版本： SRS V1.0

## **1\. 核心数据模型 (Data Model)**

(强调数据模型是整个系统的数据字典，所有组件必须以此为准)

| 实体名称 | 关键字段 (类型) | 关系 (FK) | 描述 |
| :---- | :---- | :---- | :---- |
| **GameInfo** | game\_id (PK, Integer), title (String), description (String), price (Decimal), genres (Array/String), coop\_type (Enum), deck\_comp (Boolean) | N/A | 游戏核心元数据，存储在 SQLite 中。 |
| **SearchIndex** | game\_id (Integer), bm25\_score (Float), vector\_embedding (Vector) | N/A | 搜索索引和向量数据，存储在 Faiss/BM25 文件中。 |
| **RankingMetrics** | review\_stability (Float), player\_activity (Float) | N/A | 用于融合排名的指标数据。 |
| **ErrorResponse** | error\_code (Integer), message (String), details (String) | N/A | 通用错误响应结构，所有 API 错误必须返回此结构。 |

## **2\. 接口边界 2：后端 \- 数据存储接口（数据访问层）**

**目的：** 规范后端服务 (FastAPI) 如何加载和查询本地数据文件。

### **2.1 结构化数据访问 (SQLite)**

* **服务/模块：** data\_access.py / db\_connector.py  
* **关键函数：** load\_all\_games(), get\_game\_by\_ids(ids: List\[int\])  
* **输出规范：** 必须返回 Pydantic 兼容的 GameInfo 对象列表。

### **2.2 索引数据访问 (Faiss/BM25)**

* **服务/模块：** search\_index\_loader.py  
* **关键函数：** load\_faiss\_index(), load\_bm25\_index()  
* **输出规范：** 必须返回已加载到内存中的索引对象实例。  
* **限制：** 索引文件必须在后端服务启动时**只加载一次**。

## **3\. 接口边界 4：前端 \- 后端 API（对外 RESTful API）**

### **3.1 核心接口：统一游戏搜索**

**路径：** POST /api/v1/search/games

#### **请求体结构 (Request Body \- SearchQuerySchema)**

| 字段名 | 类型 | 是否必填 | 约束/描述 |
| :---- | :---- | :---- | :---- |
| **query** | String | 是 | 用户输入的搜索文本。 |
| **filters** | Object | 否 (默认 {}) | 筛选条件的键值对。 |
| filters.price\_max | Integer | 否 | 游戏最大价格（USD）。 |
| filters.coop\_type | Enum (String) | 否 | 合作类型：Local, Online。 |
| filters.platform | Array of String | 否 | 平台过滤：Windows, SteamDeck。 |
| **limit** | Integer | 否 (默认 20\) | 返回结果数量上限 (Max: 100)。 |
| **offset** | Integer | 否 (默认 0\) | 分页偏移量。 |

#### **成功响应结构 (Response 200 \- GameResultSchema)**

返回一个包含游戏结果对象的数组，按融合排名分数降序排列。  
| 字段名 | 类型 | 描述 | 示例 |  
| :--- | :--- | :--- | :--- |  
| id | Integer | Steam 游戏 ID。 | 123456 |  
| title | String | 游戏标题。 | Game A |  
| score | Float | 最终融合排名得分 (0.0 \- 1.0)。 | 0.95 |  
| price | Decimal | 游戏当前价格 (USD)。 | 19.99 |  
| genres | Array of String | 游戏类型列表。 | Rouge like |  
| **review\_status** | String | 根据评论稳定性得出的状态。 | Very Positive | | **deck\_compatible** | Boolean | 是否兼容 Steam Deck。 | true |

### **3.2 辅助接口：搜索建议**

路径： GET /api/v1/search/suggest  
描述： 根据部分输入，提供潜在的搜索关键词建议。  
| 属性 | 详情 |  
| :--- | :--- |  
| 请求参数 | Query: prefix (String) \- 用户已输入的文本前缀。 |  
| 成功响应 (200) | \["roguelike", "roguelite games", "games like Hades"\] |

### **3.3 数据接口：获取特定游戏详情**

路径： GET /api/v1/games/{game\_id}  
描述： 根据游戏 ID 获取其完整详情数据。  
| 属性 | 详情 |  
| :--- | :--- |  
| 请求参数 | Path: game\_id (Integer) |  
| 成功响应 (200) | 返回完整的 GameInfo \+ RankingMetrics 字段的 JSON 对象。 |

## **4\. 业务逻辑与错误规范**

### **4.1 核心业务流程：搜索与融合排名**

1. **输入处理：** 接收查询，分离关键词和语义部分。  
2. **并行查询：** 1\. 使用 BM25 查询关键词索引；2. 使用 Embedding+Faiss 查询语义索引。  
3. **数据提取：** 从 SQLite 中快速提取两组查询结果对应的 GameInfo。  
4. **特征工程：** 计算并归一化活跃度、评论稳定性和 BM25/Faiss 得分。  
5. **融合排名：** 应用加权公式进行最终排序。  
6. **过滤应用：** 对最终列表应用用户指定的过滤器。

### **4.2 标准错误响应结构与错误码定义**

所有非 2XX 的 HTTP 响应都必须遵循**统一的 ErrorResponse JSON 结构**。

#### **错误码定义**

| 状态码 (HTTP) | 自定义 Error Code | 描述 | 适用场景 |
| :---- | :---- | :---- | :---- |
| **400 Bad Request** | 4001 | 输入参数验证失败 | 查询参数为空、过滤参数格式错误（FastAPI/Pydantic 验证失败）。 |
| **404 Not Found** | 4004 | 资源未找到 | 游戏 ID 不存在、搜索查询无结果。 |
| **429 Too Many Requests** | 4290 | 速率限制 | 客户端在短时间内发送过多请求。 |
| **500 Internal Server Error** | 5000 | 未知系统错误 | 数据库/Faiss 文件读取失败、融合排名算法运行时异常。 |

**后续步骤：** 前后端开发团队依据此契约并行开发，同时 DevOps 团队准备部署环境。
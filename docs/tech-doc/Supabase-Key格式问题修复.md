# Supabase Key 格式问题修复

## 🔴 问题描述

后端启动时出现 "Invalid API key" 错误，即使环境变量已正确加载。

**错误日志**:
```
✅ SUPABASE_KEY loaded (length: 46)
🔍 SupabaseProvider: Key starts with: sb_publish...
❌ Failed to initialize Supabase client: Invalid API key
```

## 🔍 根本原因

**Key 格式不匹配**:
- 当前使用的 key: `sb_publishable_SRQy_SujM87ooPXX_uNqUA_RywMFt_J`（publishable key 格式）
- Supabase Python 客户端需要: JWT 格式的 anon key（通常以 `eyJ` 开头）

**Key 类型说明**:
1. **Publishable Key** (`sb_publishable_...`):
   - 用于前端 JavaScript SDK
   - 不能用于 Python 客户端
   - 是 Supabase 的新格式

2. **Anon Key** (`eyJ...`):
   - JWT 格式的匿名密钥
   - 用于后端 Python 客户端
   - 具有读取权限（受 RLS 策略限制）

3. **Service Role Key** (`eyJ...`):
   - JWT 格式的管理密钥
   - 绕过 RLS 策略
   - 仅用于服务器端管理操作（不推荐用于常规 API 调用）

## ✅ 解决方案

### 步骤 1: 获取正确的 Anon Key

1. 登录 [Supabase Dashboard](https://supabase.com/dashboard)
2. 选择你的项目
3. 导航到: **Project Settings > API**
4. 找到 **"anon public"** key（不是 "publishable key"）
5. 复制这个 key（应该以 `eyJ` 开头，是 JWT 格式）

### 步骤 2: 更新 .env 文件

在 `backend-INST326-steam-search/.env` 文件中更新 `SUPABASE_KEY`:

```env
# 修改前（错误）:
SUPABASE_KEY=sb_publishable_SRQy_SujM87ooPXX_uNqUA_RywMFt_J

# 修改后（正确）:
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJjYW91anB6aG95cmluaGF5ZHl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTk5OTk5OTksImV4cCI6MjAxNTU3NTk5OX0.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 步骤 3: 重启后端服务

```bash
cd backend-INST326-steam-search
python3 main.py
```

## 🔧 代码修复

### 1. 添加 Key 格式验证

在 `app/data/providers/supabase.py` 中添加了格式验证：

```python
# 验证 key 格式
if self.supabase_key and self.supabase_key.startswith("sb_publishable_"):
    error_msg = (
        "❌ Invalid Supabase key format detected!\n"
        "   The key starts with 'sb_publishable_' which is a publishable key format.\n"
        "   Supabase Python client requires a JWT format anon key (usually starts with 'eyJ').\n"
        ...
    )
    raise ValueError("Invalid Supabase key format: publishable key detected, anon key required")
```

### 2. 增强错误提示

当出现 "Invalid API key" 错误时，会显示详细的故障排除指南：

```
🔧 TROUBLESHOOTING: Invalid API Key Error
======================================================================
The Supabase Python client requires a JWT format anon key.

To fix this:
1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Navigate to: Project Settings > API
4. Find the 'anon public' key (NOT the publishable key)
5. The anon key should start with 'eyJ' (JWT format)
6. Update SUPABASE_KEY in your .env file with the anon key

Note: Publishable keys (starting with 'sb_publishable_') are for
      frontend use only and cannot be used with the Python client.
======================================================================
```

## 📋 Key 格式对比

| Key 类型 | 格式 | 用途 | Python 客户端支持 |
|---------|------|------|------------------|
| **Anon Key** | `eyJhbGciOiJIUzI1NiIs...` | 后端 API 调用 | ✅ 支持 |
| **Publishable Key** | `sb_publishable_...` | 前端 JavaScript SDK | ❌ 不支持 |
| **Service Role Key** | `eyJhbGciOiJIUzI1NiIs...` | 服务器端管理 | ✅ 支持（但不推荐） |

## ✅ 验证方法

重启后端服务后，应该看到：

```
✅ SUPABASE_KEY loaded (length: 200+)  # anon key 通常更长
🔍 SupabaseProvider: Key starts with: eyJhbGci...
✅ SupabaseProvider initialized with URL: https://bcaoujpzhoyrinhaydyu.s...
✅ Using table: steam.games_prod
```

## 📝 注意事项

1. **安全性**:
   - Anon key 是公开的，但受 RLS（Row Level Security）策略保护
   - Service role key 应该保密，不要提交到代码仓库

2. **前端 vs 后端**:
   - 前端使用: `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY` (publishable key)
   - 后端使用: `SUPABASE_KEY` (anon key)

3. **权限**:
   - 确保 anon key 有访问 `steam` schema 的权限
   - 检查 Supabase Dashboard 中的 RLS 策略

---

**修复完成时间**: 2024-12-19  
**状态**: ✅ 完成（需要用户更新 .env 文件中的 key）


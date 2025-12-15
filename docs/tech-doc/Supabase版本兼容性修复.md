# Supabase 版本兼容性修复

## 🔴 问题描述

后端启动时出现错误：`Client.__init__() got an unexpected keyword argument 'proxy'`

**错误日志**:
```
❌ Failed to initialize Supabase client: Client.__init__() got an unexpected keyword argument 'proxy'
```

## 🔍 根本原因

**版本兼容性问题**:
1. **httpx 0.28+ 移除了 `proxies` 参数**：在 httpx 0.28.0 版本中，`proxies` 参数被移除，导致依赖该参数的库出现兼容性问题
2. **Supabase 客户端库依赖旧版 httpx API**：Supabase 2.25.1 及其依赖（gotrue, supafunc）需要 `httpx<0.28`
3. **websockets 版本不兼容**：realtime 客户端需要 `websockets.asyncio` API，需要 websockets 15.0+

## ✅ 解决方案

### 1. 降级 httpx 到兼容版本

```bash
pip install httpx==0.27.2
```

**原因**:
- `gotrue 2.9.1` 需要 `httpx<0.28,>=0.24`
- `supafunc 0.3.3` 需要 `httpx<0.26,>=0.24`
- httpx 0.27.2 满足这些要求

### 2. 升级 Supabase 客户端库

```bash
pip install --upgrade supabase
```

**升级后的版本**:
- `supabase`: 2.25.1 (从 2.3.4 升级)
- `postgrest`: 2.25.1 (从 0.13.1 升级)
- `realtime`: 2.25.1 (从 1.0.6 升级)
- `storage3`: 2.25.1 (从 0.7.7 升级)

### 3. 升级 websockets

```bash
pip install --upgrade websockets
```

**原因**:
- realtime 客户端需要 `websockets.asyncio.client` API
- 这个 API 在 websockets 15.0+ 中可用

## 📋 修复后的版本组合

| 库 | 修复前版本 | 修复后版本 | 说明 |
|---|----------|----------|------|
| **supabase** | 2.3.4 | 2.25.1 | 升级到最新版本 |
| **httpx** | 0.25.2 | 0.27.2 | 降级到兼容版本（避免 0.28+） |
| **websockets** | 12.0 | 15.0.1 | 升级以支持 `websockets.asyncio` API |
| **postgrest** | 0.13.1 | 2.25.1 | 随 supabase 升级 |
| **realtime** | 1.0.6 | 2.25.1 | 随 supabase 升级 |

## ✅ 验证方法

测试 Supabase 客户端创建：

```bash
python3 -c "from supabase import create_client; from app.config.settings import get_settings; s = get_settings(); client = create_client(s.supabase_url, s.supabase_key); print('✅ Supabase client created successfully')"
```

应该看到：
```
✅ Supabase client created successfully
```

## 📝 requirements.txt 更新

已更新 `requirements/production.txt`：

```txt
# Database
# Note: Updated to latest compatible versions to fix proxy parameter error
supabase>=2.25.0
postgrest>=2.25.0
websockets>=15.0  # Required by realtime client (needs websockets.asyncio API)

# HTTP client for external requests
# Note: httpx 0.27.2 is compatible with supabase 2.25.1 and gotrue 2.9.1
# httpx 0.28+ removed 'proxies' parameter causing compatibility issues
httpx==0.27.2
```

## 🎯 关键修复点

1. ✅ **httpx 版本锁定**：使用 0.27.2 避免 0.28+ 的兼容性问题
2. ✅ **Supabase 升级**：升级到 2.25.1 获得最新功能和修复
3. ✅ **websockets 升级**：升级到 15.0+ 支持新的 asyncio API
4. ✅ **依赖同步**：确保所有相关库版本兼容

## 📝 注意事项

1. **不要升级 httpx 到 0.28+**：会导致 proxy 参数错误
2. **保持 websockets >= 15.0**：realtime 客户端需要新 API
3. **定期检查依赖兼容性**：Supabase 生态系统更新频繁

---

**修复完成时间**: 2024-12-19  
**状态**: ✅ 完成


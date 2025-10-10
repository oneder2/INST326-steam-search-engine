# Deployment Guide - Steam Game Search Engine

This document provides comprehensive instructions for deploying the Steam Game Search Engine to Render.com, including both frontend (Next.js) and backend (Python FastAPI) services.

## 🚀 Quick Start

### Prerequisites

1. **Render.com Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Code must be in a GitHub repository
3. **Environment Variables**: Prepare required environment variables
4. **Data Files**: Ensure game data and indices are available

### One-Click Deployment

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/oneder2/INST326-steam-searcher-engine)

## 📋 Manual Deployment Steps

### Step 1: Prepare Repository

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify Files**:
   - `render.yaml` - Render configuration
   - `Dockerfile.frontend` - Frontend container
   - `Dockerfile.backend` - Backend container
   - `requirements.txt` - Python dependencies
   - `package.json` - Node.js dependencies

### Step 2: Deploy Backend Service

1. **Create New Web Service** in Render Dashboard
2. **Connect Repository**: Select your GitHub repository
3. **Configure Service**:
   - **Name**: `steam-search-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (for development)

4. **Environment Variables**:
   ```env
   PYTHON_VERSION=3.11.0
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   DATABASE_URL=sqlite:///data/games_data.db
   FAISS_INDEX_PATH=data/game_embeddings.faiss
   BM25_INDEX_PATH=data/bm25_index.pkl
   CORS_ORIGINS=https://steam-search-frontend.onrender.com
   API_RATE_LIMIT=100
   CACHE_TTL=3600
   ```

5. **Health Check Path**: `/api/v1/health`

### Step 3: Deploy Frontend Service

1. **Create New Web Service** in Render Dashboard
2. **Connect Repository**: Select the same GitHub repository
3. **Configure Service**:
   - **Name**: `steam-search-frontend`
   - **Environment**: `Node`
   - **Build Command**: `npm ci && npm run build`
   - **Start Command**: `npm start`
   - **Plan**: Free (for development)

4. **Environment Variables**:
   ```env
   NODE_ENV=production
   NEXT_PUBLIC_API_BASE_URL=https://steam-search-backend.onrender.com
   NEXT_PUBLIC_APP_URL=https://steam-search-frontend.onrender.com
   NEXT_PUBLIC_DEBUG=false
   ```

5. **Health Check Path**: `/`

### Step 4: Configure Custom Domains (Optional)

1. **Add Custom Domain** in service settings
2. **Configure DNS** to point to Render
3. **SSL Certificate** will be automatically provisioned

## 🔧 Configuration Details

### Backend Configuration

#### Required Files
- `main.py` - FastAPI application entry point
- `requirements.txt` - Python dependencies
- `data/` - Directory for game data and indices

#### API Endpoints
- `GET /api/v1/health` - Health check
- `POST /api/v1/search/games` - Game search
- `GET /api/v1/search/suggest` - Search suggestions
- `GET /api/v1/games/{id}` - Game details

#### Performance Settings
- **Workers**: 1 (Free tier limitation)
- **Memory**: 512MB (Free tier)
- **CPU**: Shared (Free tier)
- **Timeout**: 30 seconds

### Frontend Configuration

#### Required Files
- `package.json` - Node.js dependencies
- `next.config.js` - Next.js configuration
- `src/` - Source code directory

#### Build Settings
- **Node Version**: 18.x
- **Build Command**: `npm ci && npm run build`
- **Output Directory**: `.next`

#### Performance Settings
- **Memory**: 512MB (Free tier)
- **CPU**: Shared (Free tier)
- **Static Assets**: Automatically optimized

## 🌍 Environment Variables

### Backend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PYTHON_VERSION` | Python version | `3.11.0` | No |
| `ENVIRONMENT` | Deployment environment | `production` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `DATABASE_URL` | SQLite database path | `sqlite:///data/games_data.db` | Yes |
| `FAISS_INDEX_PATH` | Faiss index file path | `data/game_embeddings.faiss` | Yes |
| `BM25_INDEX_PATH` | BM25 index file path | `data/bm25_index.pkl` | Yes |
| `CORS_ORIGINS` | Allowed CORS origins | Frontend URL | Yes |
| `API_RATE_LIMIT` | API rate limit per minute | `100` | No |
| `CACHE_TTL` | Cache time-to-live (seconds) | `3600` | No |

### Frontend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NODE_ENV` | Node environment | `production` | No |
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL | Backend service URL | Yes |
| `NEXT_PUBLIC_APP_URL` | Frontend app URL | Frontend service URL | Yes |
| `NEXT_PUBLIC_DEBUG` | Debug mode | `false` | No |
| `NEXT_PUBLIC_GA_ID` | Google Analytics ID | - | No |

## 📊 Monitoring and Logging

### Health Checks

#### Backend Health Check
```bash
curl https://steam-search-backend.onrender.com/api/v1/health
```

Expected Response:
```json
{
  "status": "healthy",
  "timestamp": 1699123456,
  "services": {
    "database": "healthy",
    "bm25_index": "healthy",
    "faiss_index": "healthy"
  },
  "version": "1.0.0"
}
```

#### Frontend Health Check
```bash
curl https://steam-search-frontend.onrender.com/
```

Expected: HTTP 200 status with HTML content

### Logging

#### Backend Logs
- **Location**: Render Dashboard > Service > Logs
- **Format**: JSON structured logs
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

#### Frontend Logs
- **Location**: Render Dashboard > Service > Logs
- **Format**: Next.js standard logs
- **Includes**: Build logs, runtime logs, error logs

### Metrics

#### Performance Metrics
- **Response Time**: P95 < 1000ms
- **Error Rate**: < 1%
- **Uptime**: > 99%
- **Memory Usage**: < 80% of allocated

#### Business Metrics
- **Search Requests**: Tracked via API logs
- **Function Library Views**: Tracked via frontend analytics
- **User Engagement**: Page views, session duration

## 🔒 Security

### HTTPS
- **SSL/TLS**: Automatically provisioned by Render
- **Certificate**: Let's Encrypt (auto-renewal)
- **HSTS**: Enabled by default

### CORS Configuration
```python
# Backend CORS settings
CORS_ORIGINS = [
    "https://steam-search-frontend.onrender.com",
    "http://localhost:3000"  # Development only
]
```

### Security Headers
```yaml
# Configured in render.yaml
headers:
  - name: X-Frame-Options
    value: DENY
  - name: X-Content-Type-Options
    value: nosniff
  - name: Referrer-Policy
    value: strict-origin-when-cross-origin
```

## 🚨 Troubleshooting

### Common Issues

#### Build Failures

**Frontend Build Fails**:
```bash
# Check Node.js version
node --version  # Should be 18.x

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Backend Build Fails**:
```bash
# Check Python version
python --version  # Should be 3.11.x

# Install dependencies locally
pip install -r requirements.txt
```

#### Runtime Errors

**Backend 500 Errors**:
1. Check logs in Render Dashboard
2. Verify environment variables
3. Ensure data files are accessible
4. Check database connectivity

**Frontend Loading Issues**:
1. Verify API_BASE_URL is correct
2. Check CORS configuration
3. Verify backend is running
4. Check browser console for errors

#### Performance Issues

**Slow Response Times**:
1. Check database query performance
2. Verify index files are loaded
3. Monitor memory usage
4. Consider upgrading to paid plan

**High Memory Usage**:
1. Monitor Faiss index size
2. Optimize BM25 index
3. Implement request caching
4. Consider memory-efficient alternatives

### Debug Commands

```bash
# Test backend locally
uvicorn main:app --reload --port 8000

# Test frontend locally
npm run dev

# Check API connectivity
curl -v https://steam-search-backend.onrender.com/api/v1/health

# Monitor logs
render logs --service steam-search-backend --follow
```

## 📈 Scaling

### Free Tier Limitations
- **Memory**: 512MB per service
- **CPU**: Shared resources
- **Sleep**: Services sleep after 15 minutes of inactivity
- **Build Time**: 10 minutes maximum

### Upgrade Recommendations

#### For Production Use
1. **Starter Plan** ($7/month per service)
   - 1GB RAM
   - Dedicated CPU
   - No sleep
   - Custom domains

2. **Standard Plan** ($25/month per service)
   - 2GB RAM
   - More CPU resources
   - Advanced metrics
   - Priority support

#### Performance Optimizations
1. **Database**: Consider PostgreSQL for production
2. **Caching**: Implement Redis for API caching
3. **CDN**: Use Render's CDN for static assets
4. **Load Balancing**: Multiple service instances

## 🔄 CI/CD Pipeline

### Automatic Deployment

Render automatically deploys when you push to the main branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Deployment starts automatically
```

### Manual Deployment

Using the deployment script:

```bash
# Full deployment
./scripts/deploy.sh

# Check status only
./scripts/deploy.sh status

# Health checks only
./scripts/deploy.sh health
```

### Deployment Hooks

Configure webhooks in Render Dashboard:
- **Build Start**: Notify team
- **Build Success**: Update status page
- **Build Failure**: Alert developers

## 📞 Support

### Resources
- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Render Community**: [community.render.com](https://community.render.com)
- **Status Page**: [status.render.com](https://status.render.com)

### Getting Help
1. **Check Logs**: Render Dashboard > Service > Logs
2. **Review Documentation**: This file and Render docs
3. **Community Support**: Render community forums
4. **Contact Support**: For paid plans only

---

**Note**: This deployment guide is specifically configured for the INST326 Steam Game Search Engine project. Adjust configurations as needed for your specific requirements.

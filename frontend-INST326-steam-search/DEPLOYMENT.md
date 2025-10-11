# Frontend Deployment Guide - Steam Game Search Engine

This document provides comprehensive instructions for deploying the **Frontend Service** of the Steam Game Search Engine monorepo to Render.com.

## 🏗️ Monorepo Context

This deployment guide covers the **frontend service only**. The project structure is:

```
INST326-steam-searcher-engine/           # Monorepo root
├── frontend-INST326-steam-search/     # This service (Next.js)
├── backend-INST326-steam-search/      # Backend API service
└── docs/                                # Shared documentation
```

**Important**: Frontend and backend services deploy **independently** from their respective directories.

## 🚀 Quick Start

### Prerequisites

1. **Render.com Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Monorepo must be in a GitHub repository
3. **Environment Variables**: Prepare frontend-specific environment variables
4. **Backend Service**: Backend must be deployed first (see backend deployment guide)

### One-Click Deployment

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/oneder2/INST326-steam-searcher-engine)

## 📋 Frontend Deployment Steps

### Step 1: Prepare Monorepo

1. **Push to GitHub**:
   ```bash
   # From monorepo root
   git add .
   git commit -m "Prepare frontend for Render deployment"
   git push origin main
   ```

2. **Verify Frontend Files**:
   - `frontend-INST326-steam-search/package.json` - Node.js dependencies
   - `frontend-INST326-steam-search/render.yaml` - Render configuration
   - `frontend-INST326-steam-search/next.config.js` - Next.js configuration
   - `frontend-INST326-steam-search/src/` - Source code

### Step 2: Deploy Backend Service First

**Important**: The backend must be deployed before the frontend.

1. **Create Backend Service** in Render Dashboard
2. **Configure Backend**:
   - **Repository**: `https://github.com/oneder2/INST326-steam-searcher-engine`
   - **Root Directory**: `backend-INST326-steam-search`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements-core.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Note Backend URL**: Save the backend service URL (e.g., `https://steam-search-backend.onrender.com`)

### Step 3: Deploy Frontend Service

1. **Create New Web Service** in Render Dashboard
2. **Connect Repository**: Select your GitHub repository
3. **Configure Frontend Service**:
   - **Name**: `steam-search-frontend`
   - **Repository**: `https://github.com/oneder2/INST326-steam-searcher-engine`
   - **Root Directory**: `frontend-INST326-steam-search`
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

## 📁 Monorepo Service Structure

The monorepo is organized into separate services:

- **Frontend**: `frontend-INST326-steam-search/` - Next.js application (this service)
- **Backend API**: `backend-INST326-steam-search/` - FastAPI service
- **Shared Documentation**: `docs/` - Project-wide documentation

Each service has its own dependencies and deployment configuration.

### Step 4: Configure Custom Domains (Optional)

1. **Add Custom Domain** in service settings
2. **Configure DNS** to point to Render
3. **SSL Certificate** will be automatically provisioned

## 🔧 Frontend Configuration Details

### Required Files (in `frontend-INST326-steam-search/`)
- `package.json` - Node.js dependencies and scripts
- `next.config.js` - Next.js configuration
- `src/` - Source code directory
- `public/` - Static assets
- `render.yaml` - Render deployment configuration

### Build Settings
- **Node Version**: 18.x
- **Root Directory**: `frontend-INST326-steam-search`
- **Build Command**: `npm ci && npm run build`
- **Start Command**: `npm start`
- **Output Directory**: `.next`

### Performance Settings
- **Memory**: 512MB (Free tier)
- **CPU**: Shared (Free tier)
- **Static Assets**: Automatically optimized by Next.js
- **Timeout**: 30 seconds

### API Integration
- **Backend Communication**: Via `NEXT_PUBLIC_API_BASE_URL`
- **CORS**: Configured in backend service
- **Error Handling**: Implemented in frontend API client
- **Health Checks**: Frontend health at `/`, Backend health at `/api/v1/health`

## 🌍 Frontend Environment Variables

### Required Environment Variables

| Variable | Description | Example Value | Required |
|----------|-------------|---------------|----------|
| `NODE_ENV` | Node environment | `production` | No |
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL | `https://steam-search-backend.onrender.com` | Yes |
| `NEXT_PUBLIC_APP_URL` | Frontend app URL | `https://steam-search-frontend.onrender.com` | Yes |
| `NEXT_PUBLIC_DEBUG` | Debug mode | `false` | No |

### Optional Environment Variables

| Variable | Description | Example Value | Required |
|----------|-------------|---------------|----------|
| `NEXT_PUBLIC_GA_ID` | Google Analytics ID | `G-XXXXXXXXXX` | No |
| `NEXT_PUBLIC_SENTRY_DSN` | Sentry error tracking | `https://...` | No |

### Environment Configuration Examples

#### Production Environment
```env
NODE_ENV=production
NEXT_PUBLIC_API_BASE_URL=https://steam-search-backend.onrender.com
NEXT_PUBLIC_APP_URL=https://steam-search-frontend.onrender.com
NEXT_PUBLIC_DEBUG=false
```

#### Development Environment
```env
NODE_ENV=development
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_DEBUG=true
```

### Backend Environment Variables

For backend environment variables, see the backend deployment guide in `../backend-INST326-steam-search/README.md`.

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

## 🚨 Frontend Troubleshooting

### Common Issues

#### Build Failures

**Frontend Build Fails**:
```bash
# Check Node.js version (should be 18.x)
node --version

# Clear cache and reinstall (in frontend directory)
cd frontend-INST326-steam-search
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Monorepo Path Issues**:
```bash
# Verify you're in the correct directory
pwd  # Should end with frontend-INST326-steam-search

# Check if Render is using correct root directory
# Root Directory should be: frontend-INST326-steam-search
```

#### Runtime Errors

**Frontend Loading Issues**:
1. **Check API Connection**:
   ```bash
   # Test backend health from frontend
   curl https://steam-search-backend.onrender.com/api/v1/health
   ```

2. **Verify Environment Variables**:
   - `NEXT_PUBLIC_API_BASE_URL` points to correct backend URL
   - Backend service is deployed and running
   - CORS is configured in backend for frontend domain

3. **Check Browser Console**:
   - Network errors indicate API connectivity issues
   - CORS errors indicate backend CORS misconfiguration
   - 404 errors indicate incorrect API endpoints

**API Communication Errors**:
1. **Backend Not Responding**:
   - Verify backend service is deployed and running
   - Check backend health endpoint
   - Verify backend URL in environment variables

2. **CORS Errors**:
   - Backend must include frontend domain in CORS_ORIGINS
   - Check browser network tab for preflight requests
   - Verify backend CORS configuration

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
# Test frontend locally (from frontend directory)
cd frontend-INST326-steam-search
npm run dev

# Test both services locally
npm run monorepo:dev

# Check API connectivity
curl -v https://steam-search-backend.onrender.com/api/v1/health

# Test frontend build locally
npm run build
npm start

# Monitor logs in Render Dashboard
# Go to: Dashboard > Service > Logs
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

## 🔄 Frontend CI/CD Pipeline

### Automatic Deployment

Render automatically deploys the frontend when you push changes to the main branch:

```bash
# From monorepo root
git add .
git commit -m "frontend: update feature"
git push origin main
# Frontend deployment starts automatically
```

### Manual Deployment

Trigger manual deployment in Render Dashboard:

1. Go to **Render Dashboard** > **steam-search-frontend**
2. Click **Manual Deploy** > **Deploy latest commit**
3. Monitor build logs for any issues

### Deployment Workflow

1. **Code Changes**: Make changes in `frontend-INST326-steam-search/`
2. **Local Testing**: Test locally with `npm run dev`
3. **Integration Testing**: Test with backend using `npm run monorepo:dev`
4. **Commit & Push**: Push to main branch
5. **Auto Deploy**: Render automatically builds and deploys
6. **Verification**: Check deployed frontend and API connectivity

### Deployment Hooks

Configure webhooks in Render Dashboard:
- **Build Start**: Notify team of frontend deployment
- **Build Success**: Update status page
- **Build Failure**: Alert frontend developers

## 📞 Support

### Resources
- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Render Community**: [community.render.com](https://community.render.com)
- **Status Page**: [status.render.com](https://status.render.com)

### Getting Help
1. **Check Logs**: Render Dashboard > steam-search-frontend > Logs
2. **Review Documentation**:
   - This file (frontend deployment)
   - `../backend-INST326-steam-search/README.md` (backend deployment)
   - `../../README.md` (monorepo overview)
3. **Community Support**: Render community forums
4. **Contact Support**: For paid plans only

### Related Documentation
- [Main Project README](../../README.md) - Monorepo overview
- [Frontend Development Guide](DEVELOPMENT.md) - Development setup
- [Backend Documentation](../backend-INST326-steam-search/README.md) - Backend deployment
- [Shared Documentation](../../docs/) - Project-wide documentation

---

**Note**: This deployment guide is specifically configured for the **frontend service** of the INST326 Steam Game Search Engine monorepo. For backend deployment, see the backend service documentation.

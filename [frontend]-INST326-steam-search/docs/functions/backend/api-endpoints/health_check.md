# health_check

## health_check

**Category:** API Endpoint
**Complexity:** Low
**Last Updated:** 2024-10-08

### Description
Health check endpoint for monitoring service availability and system status. Verifies database connectivity, search index availability, and overall system health.

### Signature
```python
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
```

### Parameters
None

### Returns
- `HealthResponse`: Health status information:
  - `status` (str): Overall health status ("healthy", "degraded", "unhealthy")
  - `timestamp` (int): Unix timestamp of health check
  - `services` (Dict[str, str]): Individual service statuses
  - `version` (str): API version

### Example
```python
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    timestamp = int(time.time())
    services = {}
    
    try:
        # Check database connectivity
        db_status = await check_database_health()
        services["database"] = "healthy" if db_status else "unhealthy"
        
        # Check search indices
        bm25_status = check_bm25_index_health()
        faiss_status = check_faiss_index_health()
        services["bm25_index"] = "healthy" if bm25_status else "unhealthy"
        services["faiss_index"] = "healthy" if faiss_status else "unhealthy"
        
        # Determine overall status
        unhealthy_services = [k for k, v in services.items() if v == "unhealthy"]
        
        if not unhealthy_services:
            overall_status = "healthy"
        elif len(unhealthy_services) < len(services):
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        return HealthResponse(
            status=overall_status,
            timestamp=timestamp,
            services=services,
            version=API_VERSION
        )
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=timestamp,
            services={"error": str(e)},
            version=API_VERSION
        )
```

### Notes
- Always returns 200 status code (health info in response body)
- Performs quick checks to avoid timeout issues
- Used by load balancers and monitoring systems
- Logs health check failures for debugging

### Related Functions
- [check_database_health](#check_database_health)
- [check_bm25_index_health](#check_bm25_index_health)
- [check_faiss_index_health](#check_faiss_index_health)

### Tags
#fastapi #endpoint #health #monitoring #status

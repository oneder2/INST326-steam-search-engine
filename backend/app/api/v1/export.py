"""
Export API Endpoints

Provides endpoints for exporting search results to various formats.
Required for Project 4 data persistence requirements.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from supabase import Client
from app.database import get_db
from app.services.search_service import SearchService
from app.services.persistence_service import PersistenceService
from app.models.search import SearchRequest
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/export/csv",
    summary="Export Search Results to CSV",
    description="Export search results to CSV file for download"
)
async def export_search_results_csv(
    request: SearchRequest,
    db: Client = Depends(get_db)
):
    """
    Export search results to CSV format.
    
    This endpoint:
    1. Executes the search query
    2. Exports results to CSV file
    3. Returns file for download
    """
    try:
        logger.info(f"📥 Export CSV request RECEIVED")
        logger.info(f"   Query: '{request.query}'")
        logger.info(f"   Filters: {request.filters}")
        logger.info(f"   Sort: {request.sort_by}")
        logger.info(f"   Offset: {request.offset}")
        logger.info(f"   Limit: {request.limit}")
        logger.info(f"   Full request dict: {request.dict()}")
        
        # Execute search - pass individual parameters, not the request object
        search_service = SearchService(db)
        results_dict = await search_service.search(
            query=request.query,
            filters=request.filters,
            sort_by=request.sort_by,
            offset=request.offset,
            limit=request.limit
        )
        
        # Extract games list from results dictionary
        games_list = results_dict['results'] if isinstance(results_dict, dict) else results_dict.results
        
        logger.info(f"Found {len(games_list)} results to export")
        
        # Export to CSV
        persistence = PersistenceService()
        file_path = persistence.export_to_csv(
            games_list,
            f"search_results_{request.query or 'all'}.csv"
        )
        
        if not file_path:
            raise HTTPException(status_code=500, detail="Failed to export CSV")
        
        logger.info(f"✅ Exported search results to CSV: {file_path}")
        
        return FileResponse(
            path=str(file_path),
            media_type='text/csv',
            filename=file_path.name
        )
        
    except Exception as e:
        logger.error(f"❌ Export CSV failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/export/json",
    summary="Export Search Results to JSON",
    description="Export search results to JSON file for download"
)
async def export_search_results_json(
    request: SearchRequest,
    db: Client = Depends(get_db)
):
    """
    Export search results to JSON format.
    """
    try:
        logger.info(f"📥 Export JSON request: query='{request.query}', filters={request.filters}")
        
        # Execute search - pass individual parameters, not the request object
        search_service = SearchService(db)
        results_dict = await search_service.search(
            query=request.query,
            filters=request.filters,
            sort_by=request.sort_by,
            offset=request.offset,
            limit=request.limit
        )
        
        # Extract games list from results dictionary
        games_list = results_dict['results'] if isinstance(results_dict, dict) else results_dict.results
        
        logger.info(f"Found {len(games_list)} results to export")
        
        # Export to JSON
        persistence = PersistenceService()
        file_path = persistence.export_to_json(
            games_list,
            f"search_results_{request.query or 'all'}.json"
        )
        
        if not file_path:
            raise HTTPException(status_code=500, detail="Failed to export JSON")
        
        logger.info(f"✅ Exported search results to JSON: {file_path}")
        
        return FileResponse(
            path=str(file_path),
            media_type='application/json',
            filename=file_path.name
        )
        
    except Exception as e:
        logger.error(f"❌ Export JSON failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/history",
    summary="Get Search History",
    description="Retrieve saved search history"
)
async def get_search_history():
    """
    Retrieve search history from persistent storage.
    """
    try:
        persistence = PersistenceService()
        history = persistence.load_search_history()
        
        return {
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"❌ Load history failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


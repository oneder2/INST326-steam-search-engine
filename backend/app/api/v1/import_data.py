"""
Import API Endpoints

Provides endpoints for importing game data from CSV and JSON files.
Required for Project 4 data persistence requirements.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.persistence_service import PersistenceService
from pathlib import Path
import logging
import tempfile
import shutil

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/import/csv",
    summary="Import Games from CSV",
    description="Upload and import game data from a CSV file"
)
async def import_games_from_csv(
    file: UploadFile = File(...)
):
    """
    Import game data from CSV file.
    
    This endpoint:
    1. Receives uploaded CSV file
    2. Validates and parses the data
    3. Returns imported game count
    
    Args:
        file: Uploaded CSV file
    
    Returns:
        Dictionary with import status and count
    """
    try:
        logger.info(f"📥 Import CSV request: filename='{file.filename}'")
        
        # Validate file extension
        if not file.filename or not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload a CSV file."
            )
        
        # Create temporary file to save upload
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            # Copy uploaded file to temp file
            shutil.copyfileobj(file.file, temp_file)
            temp_path = Path(temp_file.name)
        
        try:
            # Import data using persistence service
            persistence = PersistenceService()
            imported_data = persistence.import_games_from_csv(str(temp_path))
            
            if imported_data is None:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to parse CSV file. Please check the file format."
                )
            
            count = len(imported_data)
            logger.info(f"✅ Successfully imported {count} games from CSV")
            
            return {
                "success": True,
                "message": f"Successfully imported {count} games",
                "count": count,
                "filename": file.filename
            }
            
        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Import CSV failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/import/json",
    summary="Import Games from JSON",
    description="Upload and import game data from a JSON file"
)
async def import_games_from_json(
    file: UploadFile = File(...)
):
    """
    Import game data from JSON file.
    
    This endpoint:
    1. Receives uploaded JSON file
    2. Validates and parses the data
    3. Returns imported game count
    
    Args:
        file: Uploaded JSON file
    
    Returns:
        Dictionary with import status and count
    """
    try:
        logger.info(f"📥 Import JSON request: filename='{file.filename}'")
        
        # Validate file extension
        if not file.filename or not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload a JSON file."
            )
        
        # Create temporary file to save upload
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            # Copy uploaded file to temp file
            shutil.copyfileobj(file.file, temp_file)
            temp_path = Path(temp_file.name)
        
        try:
            # Import data using persistence service
            persistence = PersistenceService()
            imported_data = persistence.import_games_from_json(str(temp_path))
            
            if imported_data is None:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to parse JSON file. Please check the file format."
                )
            
            count = len(imported_data)
            logger.info(f"✅ Successfully imported {count} games from JSON")
            
            return {
                "success": True,
                "message": f"Successfully imported {count} games",
                "count": count,
                "filename": file.filename
            }
            
        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Import JSON failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.services.health_service import is_healthy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get('/health', status_code=status.HTTP_200_OK)
async def health():
    if is_healthy():
        return JSONResponse(content={'healthy': 'so_true'})

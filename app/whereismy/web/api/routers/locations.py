# app/whereismy/web/api/routers/locations.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.whereismy.web.api.deps import get_db_session_dep
from app.whereismy.core.repository.location_repository import LocationRepository
from app.whereismy.core.models import Location

router = APIRouter()

@router.get("/locations/", response_model=List[Location])
async def get_locations(db_session: AsyncSession = Depends(get_db_session_dep)):
    """
    Получить список всех локаций.
    """
    location_repo = LocationRepository(db_session)
    locations = await location_repo.get_list(db_session) # Используем get_list
    return locations

# Добавим эндпоинт для получения локации по ID
@router.get("/locations/{location_id}", response_model=Location)
async def get_location(location_id: int, db_session: AsyncSession = Depends(get_db_session_dep)):
    """
    Получить локацию по ID.
    """
    location_repo = LocationRepository(db_session)
    location = await location_repo.get(db_session, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

# Здесь можно добавить эндпоинты для создания, обновления, удаления локации (требует аутентификации модератора)

# app/whereismy/web/api/routers/categories.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.whereismy.web.api.deps import get_db_session_dep
from app.whereismy.core.repository.category_repository import CategoryRepository
from app.whereismy.core.models import Category

router = APIRouter()

@router.get("/categories/", response_model=List[Category])
async def get_categories(db_session: AsyncSession = Depends(get_db_session_dep)):
    """
    Получить список всех категорий.
    """
    category_repo = CategoryRepository(db_session)
    categories = await category_repo.get_list(db_session) # Используем get_list
    return categories

# Добавим эндпоинт для получения категории по ID
@router.get("/categories/{category_id}", response_model=Category)
async def get_category(category_id: int, db_session: AsyncSession = Depends(get_db_session_dep)):
    """
    Получить категорию по ID.
    """
    category_repo = CategoryRepository(db_session)
    category = await category_repo.get(db_session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# Здесь можно добавить эндпоинты для создания, обновления, удаления категории (требует аутентификации модератора)

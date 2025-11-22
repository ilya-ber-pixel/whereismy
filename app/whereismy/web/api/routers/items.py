# app/whereismy/web/api/routers/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.whereismy.web.api.deps import get_db_session_dep
from app.whereismy.core.repository.item_repository import ItemRepository
from app.whereismy.core.repository.user_repository import UserRepository # Для проверок в будущем
from app.whereismy.services.items_service import ItemsService
from app.whereismy.core.models import Item

router = APIRouter()

# В будущем лучше инъецировать сервисы через DI-контейнер.
# Пока создаем их внутри роутера.
# Это не идеально, но работает для начала.
# Для простоты инициализируем репозитории и сервис внутри эндпоинта.

@router.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_found_item(
    item_data: ItemCreate, # Pydantic-модель для входящих данных
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Создать новое объявление о находке.
    """
    item_repo = ItemRepository(db_session)
    user_repo = UserRepository(db_session) # Предполагаем, что ID пользователя придет из аутентификации
    items_service = ItemsService(item_repo, user_repo)

    # В реальности user_id должен приходить из аутентификации
    user_id = 1 # Заглушка

    # Вызываем сервис
    new_item = await items_service.create_found_item(
        session=db_session,
        title=item_data.title,
        description=item_data.description,
        category_id=item_data.category_id,
        location_id=item_data.location_id,
        user_id=user_id # Предполагаем, что приходит из аутентификации
    )
    return new_item

@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, db_session: AsyncSession = Depends(get_db_session_dep)):
    """
    Получить объявление по ID.
    """
    item_repo = ItemRepository(db_session)
    item = await item_repo.get(db_session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/items/", response_model=List[Item])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Получить список объявлений с пагинацией.
    """
    item_repo = ItemRepository(db_session)
    items = await item_repo.get_list(db_session, skip=skip, limit=limit) # Используем get_list
    return items

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db_session: AsyncSession = Depends(get_db_session_dep)):
    """
    Архивировать объявление (пользователем или модератором).
    """
    item_repo = ItemRepository(db_session)
    user_repo = UserRepository(db_session)
    items_service = ItemsService(item_repo, user_repo)

    # В реальности user_id должен приходить из аутентификации
    user_id = 1 # Заглушка

    success = await items_service.archive_item(db_session, item_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found or not authorized to archive")
    return # 204 No Content

# --- Pydantic-модель для создания ---
# Эту модель нужно определить, например, в отдельном файле или здесь.
# Пока определим здесь для примера.
from pydantic import BaseModel

class ItemCreate(BaseModel):
    title: str
    description: str
    category_id: int
    location_id: int | None = None # Используем | None для Optional

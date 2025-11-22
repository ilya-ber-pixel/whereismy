# app/whereismy/web/admin/routes.py
from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.whereismy.web.api.deps import get_db_session_dep
from app.whereismy.web.api.security import get_current_moderator
from app.whereismy.core.repository.item_repository import ItemRepository
from app.whereismy.core.repository.category_repository import CategoryRepository
from app.whereismy.core.repository.location_repository import LocationRepository
from app.whereismy.core.repository.user_repository import UserRepository
from app.whereismy.services.items_service import ItemsService
from app.whereismy.core.models import User # Импортируем модель User

# Указываем путь к папке с шаблонами
templates = Jinja2Templates(directory="app/whereismy/web/templates")

# Создаем роутер для админ-панели
router = APIRouter(
    prefix="/admin", # Все роуты будут начинаться с /admin
    tags=["admin"],
    # dependencies=[Depends(get_current_moderator)] # <- Опционально: защищаем все роуты в роутере сразу
)

# Роут для страницы входа (доступен всем, не требует аутентификации модератора)
@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    """
    Отображает страницу входа.
    """
    return templates.TemplateResponse("login.html", {"request": request})

# Роут для основной панели (требует аутентификации модератора)
@router.get("/dashboard", response_class=HTMLResponse)
async def get_admin_dashboard(
    request: Request,
    current_moderator: User = Depends(get_current_moderator), # Защищаем роут
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Отображает основную панель модератора (список объявлений).
    """
    item_repo = ItemRepository(db_session)
    items = await item_repo.get_list(db_session, skip=0, limit=100) # Получаем список объявлений

    # Рендерим шаблон, передав ему список объявлений и текущего модератора
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "items": items,
            "current_moderator": current_moderator # Передаем имя модератора в шаблон
        }
    )

# Роут для редактирования объявления (GET - отображение формы)
@router.get("/items/{item_id}/edit", response_class=HTMLResponse)
async def get_edit_item_form(
    request: Request,
    item_id: int,
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Отображает форму редактирования объявления.
    """
    item_repo = ItemRepository(db_session)
    category_repo = CategoryRepository(db_session)
    location_repo = LocationRepository(db_session)

    item = await item_repo.get(db_session, item_id)
    if not item:
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_404_NOT_FOUND)

    categories = await category_repo.get_list(db_session)
    locations = await location_repo.get_list(db_session)

    return templates.TemplateResponse(
        "edit_item.html",
        {
            "request": request,
            "item": item,
            "categories": categories,
            "locations": locations,
            "current_moderator": current_moderator
        }
    )

# Роут для редактирования объявления (POST - обработка формы)
@router.post("/items/{item_id}/edit", response_class=HTMLResponse)
async def post_edit_item_form(
    request: Request,
    item_id: int,
    title: str = Form(...),
    description: str = Form(...),
    category_id: int = Form(...),
    location_id: int | None = Form(None), # Используем | None
    status: str = Form(...),
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Обрабатывает отправленную форму редактирования объявления.
    """
    item_repo = ItemRepository(db_session)
    # user_repo не нужен для обновления, но ItemsService его требует
    user_repo = UserRepository(db_session)
    items_service = ItemsService(item_repo, user_repo)

    item = await item_repo.get(db_session, item_id)
    if not item:
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_404_NOT_FOUND)

    # Обновляем поля объекта Item
    item.title = title
    item.description = description
    item.category_id = category_id
    item.location_id = location_id
    item.status = status # Предполагаем, что строка соответствует enum в БД

    # Вызываем репозиторий для обновления
    updated_item = await item_repo.update(db_session, item, item) # Обновляем самим собой

    # Перенаправляем обратно на панель
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

# Роут для архивации объявления
@router.post("/items/{item_id}/archive")
async def archive_item(
    item_id: int,
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Архивирует объявление (для модератора).
    """
    item_repo = ItemRepository(db_session)
    user_repo = UserRepository(db_session) # ItemsService требует user_repo
    items_service = ItemsService(item_repo, user_repo)

    # Вызываем метод сервиса, передав ему ID модератора как ID пользователя
    # (в реальности может быть отдельная логика для модераторов)
    success = await items_service.archive_item(db_session, item_id, current_moderator.user_id)

    if success:
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    else:
        # Обработка ошибки (например, объявление не найдено)
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_404_NOT_FOUND)

# Роут для удаления объявления
@router.post("/items/{item_id}/delete")
async def delete_item(
    item_id: int,
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Удаляет объявление (для модератора).
    """
    item_repo = ItemRepository(db_session)
    # Для простоты, просто удаляем из БД. В реальности может быть архивация или сложная логика.
    success = await item_repo.delete(db_session, item_id)

    if success:
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    else:
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_404_NOT_FOUND)

# Роут для управления категориями
@router.get("/categories", response_class=HTMLResponse)
async def get_manage_categories(
    request: Request,
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Отображает страницу управления категориями.
    """
    category_repo = CategoryRepository(db_session)
    categories = await category_repo.get_list(db_session)

    return templates.TemplateResponse(
        "manage_categories.html",
        {
            "request": request,
            "categories": categories,
            "current_moderator": current_moderator
        }
    )

# Роут для создания категории (POST)
@router.post("/categories/")
async def create_category(
    name: str = Form(...),
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Обрабатывает создание новой категории.
    """
    category_repo = CategoryRepository(db_session)
    # Создаем объект категории (предполагаем модель Category с полем name)
    from app.whereismy.core.models import Category
    new_category = Category(name=name)
    await category_repo.create(db_session, new_category)

    return RedirectResponse(url="/admin/categories", status_code=status.HTTP_302_FOUND)

# Роут для обновления категории (POST)
@router.post("/categories/{category_id}")
async def update_category(
    category_id: int,
    name: str = Form(...),
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Обрабатывает обновление категории.
    """
    category_repo = CategoryRepository(db_session)
    category = await category_repo.get(db_session, category_id)
    if not category:
        return RedirectResponse(url="/admin/categories", status_code=status.HTTP_404_NOT_FOUND)

    category.name = name
    await category_repo.update(db_session, category, category)

    return RedirectResponse(url="/admin/categories", status_code=status.HTTP_302_FOUND)

# Роут для удаления категории (POST)
@router.post("/categories/{category_id}/delete")
async def delete_category(
    category_id: int,
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Обрабатывает удаление категории.
    """
    category_repo = CategoryRepository(db_session)
    # Важно: проверить зависимости перед удалением!
    # Проверим, нет ли объявлений, связанных с этой категорией
    item_repo = ItemRepository(db_session)
    # Это упрощённая проверка. В реальности нужен запрос к БД.
    # from sqlalchemy import select
    # stmt = select(Item).where(Item.category_id == category_id)
    # result = await db_session.execute(stmt)
    # items = result.scalars().all()
    # if items:
    #     # Не удаляем, если есть связанные объявления
    #     return RedirectResponse(url="/admin/categories", status_code=status.HTTP_400_BAD_REQUEST)

    success = await category_repo.delete(db_session, category_id)

    if success:
        return RedirectResponse(url="/admin/categories", status_code=status.HTTP_302_FOUND)
    else:
        return RedirectResponse(url="/admin/categories", status_code=status.HTTP_404_NOT_FOUND)

# Роут для управления локациями (аналогично категориям)
@router.get("/locations", response_class=HTMLResponse)
async def get_manage_locations(
    request: Request,
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Отображает страницу управления локациями.
    """
    location_repo = LocationRepository(db_session)
    locations = await location_repo.get_list(db_session)

    return templates.TemplateResponse(
        "manage_locations.html",
        {
            "request": request,
            "locations": locations,
            "current_moderator": current_moderator
        }
    )

# Роут для создания локации (POST)
@router.post("/locations/")
async def create_location(
    name: str = Form(...),
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Обрабатывает создание новой локации.
    """
    location_repo = LocationRepository(db_session)
    from app.whereismy.core.models import Location
    new_location = Location(name=name)
    await location_repo.create(db_session, new_location)

    return RedirectResponse(url="/admin/locations", status_code=status.HTTP_302_FOUND)

# Роут для обновления локации (POST)
@router.post("/locations/{location_id}")
async def update_location(
    location_id: int,
    name: str = Form(...),
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Обрабатывает обновление локации.
    """
    location_repo = LocationRepository(db_session)
    location = await location_repo.get(db_session, location_id)
    if not location:
        return RedirectResponse(url="/admin/locations", status_code=status.HTTP_404_NOT_FOUND)

    location.name = name
    await location_repo.update(db_session, location, location)

    return RedirectResponse(url="/admin/locations", status_code=status.HTTP_302_FOUND)

# Роут для удаления локации (POST)
@router.post("/locations/{location_id}/delete")
async def delete_location(
    location_id: int,
    current_moderator: User = Depends(get_current_moderator),
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Обрабатывает удаление локации.
    """
    location_repo = LocationRepository(db_session)
    # Проверка зависимостей (аналогично категории)
    success = await location_repo.delete(db_session, location_id)

    if success:
        return RedirectResponse(url="/admin/locations", status_code=status.HTTP_302_FOUND)
    else:
        return RedirectResponse(url="/admin/locations", status_code=status.HTTP_404_NOT_FOUND)

# app/whereismy/bot/handlers/search_item.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from app.whereismy.core.database import get_db_session
from app.whereismy.core.repository.item_repository import ItemRepository
from app.whereismy.services.items_service import ItemsService

router = Router()

@router.message(Command("search"))
async def cmd_search_start(message: Message):
    """
    Начало сценария поиска. Запрашивает описание.
    """
    await message.answer("Опишите, какую вещь вы ищете. Я постараюсь найти похожие объявления.")

# Простой обработчик текста как запроса для поиска
@router.message(F.text) # Это может пересекаться с другими хендлерами, нужно уточнить фильтры
async def process_search_query(message: Message):
    """
    Обработка текста как поискового запроса.
    """
    query_text = message.text

    # Создаем сессию, репозиторий и сервис
    async with get_db_session() as session: # Опять напрямую
        item_repo = ItemRepository(session)
        # user_repo не нужен для поиска, но ItemsService его требует
        # Потенциально, можно создать отдельный сервис поиска или модифицировать ItemsService
        # или внедрять зависимости через DI.
        # Пока оставим как есть.
        from app.whereismy.core.repository.user_repository import UserRepository
        user_repo = UserRepository(session)
        items_service = ItemsService(item_repo, user_repo)

        # Вызываем сервис для поиска
        similar_items = await items_service.find_similar_found_items(
            session=session,
            query_description=query_text,
            limit=5 # Пока фиксированное количество
        )

    if similar_items:
        response_text = "Вот похожие объявления, которые я нашёл:\n\n"
        for item in similar_items:
            response_text += f"- {item.title}: {item.description}\n"
            # Здесь можно добавить фото, если оно есть
            # и способ связи, если он указан как "contact_me"
            if item.contact_method == "contact_me":
                 response_text += f"  Связаться: {item.author.username or 'Неизвестно'} (ID: {item.author.telegram_id})\n" # Обратите внимание: это требует связи с User
            elif item.contact_method == "left_at":
                 response_text += f"  Оставлена в: {item.location.name if item.location else 'Неизвестно'}\n"
            response_text += "\n"
    else:
        response_text = "К сожалению, я не нашёл похожих объявлений."

    await message.answer(response_text)

# app/whereismy/bot/handlers/my_items.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.whereismy.core.database import get_db_session
from app.whereismy.core.repository.item_repository import ItemRepository
from app.whereismy.core.repository.user_repository import UserRepository
from app.whereismy.services.items_service import ItemsService

router = Router()

@router.message(Command("my_items"))
async def cmd_my_items(message: Message):
    """
    Отображает список объявлений пользователя.
    """
    user_id = message.from_user.id

    async with get_db_session() as session: # Опять напрямую
        item_repo = ItemRepository(session)
        user_repo = UserRepository(session)
        items_service = ItemsService(item_repo, user_repo)

        user_items = await items_service.get_user_items(session, user_id)

    if user_items:
        response_text = "Ваши активные объявления:\n\n"
        for item in user_items:
            response_text += f"- ID: {item.id}, {item.title}: {item.description}\n"
            # Клавиатура для архивации
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Архивировать", callback_data=f"archive_{item.id}")]
            ])
            await message.answer(response_text, reply_markup=keyboard)
            response_text = "" # Очищаем для следующей итерации
    else:
        await message.answer("У вас нет активных объявлений.")

# Обработчик для архивации через callback
@router.callback_query(F.data.startswith("archive_"))
async def process_archive(callback: CallbackQuery):
    """
    Обработка архивации объявления.
    """
    item_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    async with get_db_session() as session:
        item_repo = ItemRepository(session)
        user_repo = UserRepository(session)
        items_service = ItemsService(item_repo, user_repo)

        success = await items_service.archive_item(session, item_id, user_id)

    if success:
        await callback.answer("Объявление архивировано.")
        await callback.message.edit_reply_markup(reply_markup=None) # Убираем кнопку
    else:
        await callback.answer("Не удалось архивировать объявление. Возможно, оно не существует или вы не автор.", show_alert=True)

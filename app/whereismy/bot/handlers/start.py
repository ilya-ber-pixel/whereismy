# app/whereismy/bot/handlers/start.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    """
    await message.answer(
        "Привет! Я бот для поиска потерянных и найденных вещей.\n"
        "Вы можете:\n"
        "- Сообщить о найденной вещи (/find)\n"
        "- Поискать свою потерю (/search)\n"
        "- Управлять своими объявлениями (/my_items)"
    )

# app/whereismy/bot/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage # Для простоты, можно использовать RedisStorage
from app.whereismy.config import settings # Используем общий файл настроек
from app.whereismy.bot.handlers import start, find_item, search_item, my_items # Импортируем хендлеры

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Точка входа
async def main():
    # Инициализируем бота
    bot = Bot(token=settings.telegram_bot_token) # Токен берем из настроек

    # Инициализируем диспетчер с хранилищем состояний FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрируем роутеры (хендлеры)
    dp.include_router(start.router)
    dp.include_router(find_item.router)
    dp.include_router(search_item.router)
    dp.include_router(my_items.router)

    # Запускаем бота
    try:
        logging.info("Starting bot...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

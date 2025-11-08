import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram import F
from supabase import create_client
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Подключаемся к Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Получаем токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Нашёл"), KeyboardButton(text="Потерял")],
        [KeyboardButton(text="Мои объявления")]
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я бот «WhereIsMy?»\n"
        "Помогаю находить потерянные вещи в университете 🎓",
        reply_markup=main_menu
    )

# Регистрируем роутер
dp.include_router(router)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
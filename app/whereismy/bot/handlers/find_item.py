# app/whereismy/bot/handlers/find_item.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.whereismy.bot.states import FindItemStateGroup
from app.whereismy.core.database import get_db_session
from app.whereismy.core.repository.item_repository import ItemRepository
from app.whereismy.core.repository.category_repository import CategoryRepository
from app.whereismy.core.repository.location_repository import LocationRepository
from app.whereismy.core.repository.user_repository import UserRepository
from app.whereismy.services.items_service import ItemsService

router = Router()

@router.message(Command("find"))
async def cmd_find_start(message: Message, state: FSMContext):
    """
    Начало сценария подачи объявления о находке.
    """
    # Здесь можно отправить инструкции и перейти к первому шагу
    await message.answer("Вы хотите сообщить о находке или потере? (Ответьте 'найдено' или 'потеряно')")
    await state.set_state(FindItemStateGroup.waiting_for_type)

@router.message(FindItemStateGroup.waiting_for_type, F.text.lower().in_(["найдено", "потеряно"]))
async def process_type(message: Message, state: FSMContext):
    """
    Обработка типа (найдено/потеряно). Переход к фото.
    """
    item_type = message.text.lower()
    # Сохраняем тип во временном состоянии
    await state.update_data(item_type=item_type)
    await message.answer("Отправьте фото найденной вещи.")
    await state.set_state(FindItemStateGroup.waiting_for_photo)

# ... (обработчики для фото, описания, категории, локации, способа связи)
# Эти обработчики будут использовать get_db_session_dep,
# создавать репозитории и сервисы (или внедрять их),
# и вызывать соответствующие методы сервиса items_service.create_found_item.
# Пример для описания:
@router.message(FindItemStateGroup.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """
    Обработка описания. Переход к выбору категории.
    """
    description = message.text
    await state.update_data(description=description)

    # Получаем список категорий из БД через репозиторий
    async with get_db_session() as session: # Нужно будет переделать на зависимость, как в API
        category_repo = CategoryRepository(session)
        categories = await category_repo.get_list(session) # Используем get_list

    # Формируем inline-клавиатуру с категориями
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat.name, callback_data=f"cat_{cat.id}")] for cat in categories
    ])

    await message.answer("Выберите категорию вещи:", reply_markup=keyboard)
    await state.set_state(FindItemStateGroup.waiting_for_category)

# Обработчик для выбора категории через callback
@router.callback_query(FindItemStateGroup.waiting_for_category, F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора категории. Переход к выбору локации.
    """
    category_id = int(callback.data.split("_")[1])
    await state.update_data(category_id=category_id)

    # Получаем список локаций из БД через репозиторий
    async with get_db_session() as session:
        location_repo = LocationRepository(session)
        locations = await location_repo.get_list(session) # Используем get_list

    # Формируем inline-клавиатуру с локациями
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=loc.name, callback_data=f"loc_{loc.id}")] for loc in locations
    ])

    await callback.message.edit_text("Выберите место, где была найдена вещь:")
    await callback.message.answer("Выберите локацию:", reply_markup=keyboard)
    await state.set_state(FindItemStateGroup.waiting_for_location)

# ... и так далее для остальных состояний ...

# Последний обработчик, который завершает FSM и вызывает сервис
@router.callback_query(FindItemStateGroup.waiting_for_contact_method, F.data.startswith("contact_"))
async def process_contact_method(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора способа связи. Завершение FSM и сохранение в БД.
    """
    contact_method = callback.data.split("_")[1]
    await state.update_data(contact_method=contact_method)

    # Получаем все данные из состояния
    data = await state.get_data()
    item_type = data['item_type']
    description = data['description']
    category_id = data['category_id']
    location_id = data['location_id']
    user_id = callback.from_user.id # ID пользователя из Telegram

    # Здесь нужно создать сессию, репозитории, сервис и вызвать его метод
    async with get_db_session() as session: # Опять используем напрямую, нужно улучшить
        item_repo = ItemRepository(session)
        user_repo = UserRepository(session)
        items_service = ItemsService(item_repo, user_repo)

        # Вызываем сервис для создания объявления
        # Пока не реализовано сохранение фото
        new_item = await items_service.create_found_item(
            session=session,
            title=f"Объявление от {callback.from_user.first_name}", # В реальности title может формироваться по-другому
            description=description,
            category_id=category_id,
            location_id=location_id,
            user_id=user_id
        )

    await callback.message.edit_text(f"Спасибо! Ваше объявление (ID: {new_item.id}) успешно добавлено.")
    await state.clear() # Сбрасываем состояние FSM

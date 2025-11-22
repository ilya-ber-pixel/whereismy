# app/whereismy/bot/states.py
from aiogram.fsm.state import State, StatesGroup

class FindItemStateGroup(StatesGroup):
    """
    Группа состояний для сценария "Я нашёл вещь".
    """
    waiting_for_type = State() # Ожидаем тип (найдено/потеряно)
    waiting_for_photo = State() # Ожидаем фото
    waiting_for_description = State() # Ожидаем описание
    waiting_for_category = State() # Ожидаем выбор категории
    waiting_for_location = State() # Ожидаем выбор локации
    waiting_for_contact_method = State() # Ожидаем способ связи

# class SearchItemStateGroup(StatesGroup):
#     # Можно добавить состояния для сценария поиска, если он будет сложным
#     waiting_for_search_query = State()

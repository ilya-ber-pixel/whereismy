from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
# 1. Импортируем нашу модель настроек
from app.whereismy.config import settings

# 2. Используем строку подключения из настроек, вместо os.getenv напрямую
DATABASE_URL = settings.database_url

# Асинхронный движок. Он устанавливает соединение с базой данных.
engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Раскомментируйте для логирования SQL-запросов
)

# Асинхронная сессия. Это "рабочая лошадка", через которую мы будем выполнять запросы.
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Зависимость для получения сессии в FastAPI (если будем использовать)
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

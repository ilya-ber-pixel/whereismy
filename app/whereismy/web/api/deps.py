# app/whereismy/web/api/deps.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.whereismy.core.database import get_db_session

# Зависимость для получения сессии БД
# Роуты будут использовать эту зависимость, чтобы получить доступ к БД.
async def get_db_session_dep() -> AsyncSession:
    async for session in get_db_session():
        try:
            yield session
        finally:
            await session.close()

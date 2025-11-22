# app/whereismy/core/repository/location_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.whereismy.core.models import Location
from app.whereismy.core.repository.base import BaseRepository

class LocationRepository(BaseRepository[Location]):
    """
    Репозиторий для работы с локациями (Location).
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session, Location)

    # Можно добавить специфичные методы, например:
    async def get_by_name(self, name: str) -> Location | None:
        """Найти локацию по её имени."""
        from sqlalchemy import select
        stmt = select(Location).where(Location.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

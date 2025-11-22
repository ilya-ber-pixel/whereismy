# app/whereismy/web/api/security.py
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.whereismy.config import settings
from app.whereismy.core.models.user import User, UserRole
from app.whereismy.core.repository.user_repository import UserRepository
from app.whereismy.web.api.deps import get_db_session_dep
from app.whereismy.web.api.schemas.auth import TokenData

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема для получения токена из заголовка
security = HTTPBearer()

# Секретный ключ и алгоритм для JWT
SECRET_KEY = settings.secret_key # Добавить в config.py
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли plain_password с hashed_password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Создает JWT токен."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db_session: AsyncSession = Depends(get_db_session_dep)
) -> User:
    """Получает текущего пользователя из токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_username(token_data.username) # Добавить метод в UserRepository
    if user is None:
        raise credentials_exception
    return user

async def get_current_moderator(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Проверяет, является ли текущий пользователь модератором."""
    if current_user.role != UserRole.MODERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not allowed"
        )
    return current_user

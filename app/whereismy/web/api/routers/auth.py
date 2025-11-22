# app/whereismy/web/api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.whereismy.web.api.deps import get_db_session_dep
from app.whereismy.core.repository.user_repository import UserRepository
from app.whereismy.web.api.schemas.auth import LoginData, Token
from app.whereismy.web.api.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/auth/login", response_model=Token)
async def login_for_access_token(
    login_data: LoginData, # Pydantic-модель для тела запроса
    db_session: AsyncSession = Depends(get_db_session_dep)
):
    """
    Аутентифицирует пользователя и возвращает токен.
    """
    user_repo = UserRepository(db_session)
    # Ищем модератора с указанным именем
    user = await user_repo.get_moderator_by_username(login_data.username)

    if not user or not verify_password(login_data.password, user.hashed_password): # Предполагаем, что в модели User есть поле hashed_password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Создаем токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

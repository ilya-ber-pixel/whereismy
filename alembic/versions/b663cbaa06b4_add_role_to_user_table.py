"""Add role to user table

Revision ID: b663cbaa06b4
Revises: 276c1612ddc3
Create Date: 2025-11-22 20:39:21.890956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b663cbaa06b4'
down_revision: Union[str, Sequence[str], None] = '276c1612ddc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создаем ENUM тип в базе данных
    user_role_enum = sa.Enum('USER', 'MODERATOR', name='userrole')
    user_role_enum.create(op.get_bind(), checkfirst=True) # checkfirst=True предотвращает ошибку, если тип уже существует

    # 2. Добавляем колонку, используя созданный ENUM тип
    op.add_column('users', sa.Column('role', user_role_enum, nullable=False, server_default='USER')) # Указываем server_default

    # 3. Добавляем колонку для хеша пароля
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))



def downgrade() -> None:
    # 1. Удаляем колонки
    op.drop_column('users', 'hashed_password')
    op.drop_column('users', 'role')

    # 2. Удаляем ENUM тип из базы данных
    user_role_enum = sa.Enum('USER', 'MODERATOR', name='userrole')
    user_role_enum.drop(op.get_bind(), checkfirst=True) # checkfirst=True предотвращает ошибку, если тип уже удален

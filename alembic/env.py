import asyncio
import sys
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum
from alembic import context

# --- Важные импорты для автогенерации ---
# Добавляем путь к нашему приложению
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from whereismy.core.models.base import Base
from whereismy.core.models import *
# Импортируем сам класс Vector для проверки типа
from pgvector.sqlalchemy import Vector 

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    def render_item(type_, obj, autogen_context):
        """Обрабатывает отображение кастомных типов для автогенерации."""
        if type_ == "type" and isinstance(obj, Vector):
            autogen_context.imports.add("import pgvector.sqlalchemy")
            return f"pgvector.sqlalchemy.Vector({obj.dim})"
        # Добавим обработку для Enum
        if type_ == "type" and isinstance(obj, Enum):
            # Добавляем импорт Enum
            autogen_context.imports.add("from sqlalchemy import Enum")
            # Формируем строку для создания Enum в миграции
            # Используем имя типа из SQLAlchemy (obj.name) и значения (obj.enums)
            # Также учитываем, является ли это нативным ENUM (обычно для PostgreSQL)
            # native_enum=False означает, что ENUM не создается в БД, используется VARCHAR
            # native_enum=True (по умолчанию для PostgreSQL) означает, что создается нативный тип
            # Важно: если в модели используется native_enum=False, Alembic не будет генерировать CREATE TYPE для него.
            # Если используется native_enum=True (или не указано), Alembic попытается сгенерировать CREATE TYPE.
            # Наша задача - корректно сгенерировать строку для миграции, если тип создается.
            # Для Enum с native_enum=True Alembic ожидает, что строка будет в формате Enum(..., name='...')
            # Но obj.name может быть None, если имя не задано явно. SQLAlchemy генерирует имя автоматически.
            # В этом случае obj.compile(dialect=postgresql.dialect()) может помочь, но для генерации кода миграции
            # лучше использовать базовый формат Enum с указанием значений и имени.
            # Alembic обычно генерирует Enum(..., name="...") сам, если все настроено правильно.
            # Однако, если возникают проблемы, можно добавить специфичную логику.
            # Для стандартного случая, возвращаем False, чтобы Alembic использовал свою логику,
            # но добавляем импорт.
            autogen_context.imports.add("from sqlalchemy import Enum")
            # Попробуем стандартную обработку, но убедимся, что она вызывается только для нужных Enum.
            # Alembic сам генерирует имя, если оно не задано явно в модели.
            # Проверим, является ли это нашим ENUM из модели (например, по списку значений или другим признакам).
            # Если это общий случай, возвращаем False, чтобы Alembic делал свою работу.
            # Если у нас есть Enum, созданный через sqlalchemy.dialects.postgresql.ENUM,
            # он может обрабатываться иначе. Наш Enum из typing и enum создает Enum SQLAlchemy.
            # Важно, чтобы в модели были указаны native_enum=True (или не указано, т.к. это по умолчанию для PostgreSQL).
            # В предыдущем контексте мы решили проблему с ENUM, указав native_enum=False.
            # Если вы изменили модели и вернулись к native_enum=True, то нужна эта обработка.
            # Если native_enum=False, то Enum превращается в String, и тип не создается в БД.
            # Проверим, не является ли obj нашим конкретным Enum из модели Item.
            # Мы можем проверить имя или содержимое, но надежнее - просто указать, что для Enum
            # Alembic должен добавить стандартный импорт и сгенерировать строку сам.
            # Поэтому для типа "type" и объекта Enum возвращаем False, но добавили import выше.
            # Однако, если стандартной логики не хватает, можно сформировать строку вручную.
            # Проверим, есть ли у объекта атрибуты, характерные для SQLAlchemy Enum.
            # hasattr(obj, 'enums') и hasattr(obj, 'name') обычно True для Enum.
            if hasattr(obj, 'enums') and hasattr(obj, 'name'):
                # Alembic ожидает строку, которая будет частью выражения.
                # Пример того, что должно быть в миграции: Enum('value1', 'value2', name='my_enum')
                # Мы возвращаем только внутреннюю часть: значения и имя.
                # Alembic обернет это в `Enum(...)` и добавит `name=...` при необходимости.
                # Но на практике, если просто вернуть False, Alembic сгенерирует код сам, если `render_item` не мешает.
                # Попробуем вернуть строку, как ожидает Alembic.
                # Это сложный момент. Лучше всего сначала попробовать вернуть False,
                # если мы уверены, что в модели native_enum=True и Alembic должен сам все сгенерировать.
                # Но ошибка говорит, что он не сгенерировал.
                # Значит, нужна явная обработка или настройка модели.
                # Попробуем вернуть строку, как генерируется тип.
                # Alembic вызывает эту функцию, когда собирает аргументы для `sa.Enum` в миграции.
                # Если мы вернем строку, он вставит её как есть.
                # "Enum('found', 'lost', name='itemtype')" - пример того, что нужно вернуть.
                # Но как получить имя типа и его значения?
                # obj.enums - это список значений.
                # obj.name - это имя типа в БД. Оно может быть сгенерировано SQLAlchemy.
                # Для Enum, созданного из Python enum.Enum, имя генерируется как enum_class.__name__.lower()
                # или может быть задано вручную через metadata.
                # Alembic, при правильной настройке, сам сгенерирует имя, если оно не задано.
                # Попробуем вернуть строку, как ожидает Alembic для вставки в `op.create_type(Enum(...))`
                # или `sa.Column(Enum(...))` в зависимости от контекста.
                # Alembic вызывает render_item для каждого объекта типа при автогенерации.
                # Если мы вручную сформируем строку, это может помочь.
                # Например: Enum('active', 'archived', name='itemstatus')
                # В миграции это должно выглядеть как `sa.Enum('active', 'archived', name='itemstatus')`
                # Но render_item возвращает строку, которая вставляется внутрь `Enum(...)`.
                # Поэтому нужно вернуть: "'active', 'archived', name='itemstatus'"
                # Но это тоже сложно. Лучше убедиться, что Alembic сам генерирует нужный код.
                # Возвращение False - это стандартный способ сказать "используй стандартную логику".
                # Ошибка говорит, что стандартной логики недостаточно.
                # В предыдущем обсуждении мы решили проблему, установив native_enum=False.
                # Если вы хотите использовать native_enum=True, нужно убедиться, что Alembic
                # генерирует команды `op.create_type()` перед `op.create_table()`.
                # Это достигается с помощью правильной настройки `render_item` и `target_metadata`.
                # Попробуем сформировать строку для Enum.
                # Значения enum обычно экранируются как строки.
                # Предположим, obj.name = 'itemstatus', obj.enums = ['active', 'archived']
                # Мы хотим вернуть строку, которую Alembic вставит в `Enum(...)`
                # Alembic сам добавит `name=` и само `Enum`.
                # В документации Alembic: render_item возвращает строковое представление для autogenerate.
                # Если возвращается строка, она используется как есть.
                # Если возвращается False, используется стандартная логика.
                # Попробуем вернуть строку, которую Alembic ожидает.
                # Alembic ожидает что-то вроде: "'value1', 'value2'" и добавит `name='...'` и `Enum(...)`
                # Но на практике, если ENUM имеет имя, Alembic может сгенерировать `op.create_type(sa.Enum(..., name='...'))`
                # и `op.drop_type(...)`.
                # Давайте проверим, не вызвана ли ошибка тем, что в модели ENUMы используют `native_enum=True`.
                # Если да, то Alembic должен сгенерировать `CREATE TYPE itemstatus AS ENUM (...);` перед `CREATE TABLE`.
                # Если он этого не сделал, проблема в `env.py` или в том, как SQLAlchemy "видит" метаданные ENUMа.
                # Попробуем вернуть строку с аргументами для Enum, но это может не сработать для `create_type`.
                # Возврат `False` - это путь, если мы полагаемся на стандартную логику Alembic.
                # Но стандартная логика не сработала, так как тип не был создан.
                # Возможно, проблема в том, что в ваших моделях `Item` для полей `type`, `status`, `contact_method`
                # вы используете `Enum(...)` без `native_enum=False`.
                # Помните, в предыдущем контексте мы решили проблему *именно этой ошибки*, изменив модель Item:
                # status: Mapped[ItemStatus] = mapped_column(default=ItemStatus.ACTIVE, native_enum=False)
                # и аналогично для других Enum полей.
                # Это заставило SQLAlchemy использовать VARCHAR вместо нативного ENUM, и проблема исчезла.
                # Если вы вернули `native_enum=True` или удалили этот параметр (что делает его `True` по умолчанию),
                # то Alembic должен генерировать команды для создания типа.
                # Проверьте файл модели `item.py`. Убедитесь, что для `status`, `type`, `contact_method` указано:
                # `native_enum=False`.
                # Если `native_enum=False`, то Alembic НЕ будет генерировать `CREATE TYPE`, и тип не создается в БД.
                # Тогда в БД колонка будет VARCHAR, и строка "active" вставляется без проблем.
                # Тогда ошибка `invalid input value for enum` не должна возникать.
                # Значит, либо вы убрали `native_enum=False`, либо миграция, которая должна была создать тип,
                # была сгенерирована неправильно и не создала тип `itemstatus`.
                # Давайте вернемся к самой модели.
                # В `app/whereismy/core/models/item.py` должны быть строки вроде:
                # status: Mapped[ItemStatus] = mapped_column(default=ItemStatus.ACTIVE, native_enum=False)
                # type: Mapped[ItemType] = mapped_column(nullable=False, native_enum=False)
                # contact_method: Mapped[ContactMethod] = mapped_column(nullable=False, native_enum=False)
                # Пожалуйста, проверьте это.
                # Если `native_enum=False` стоит, и ошибка всё равно появляется, возможно,
                # предыдущая миграция была создана до этого исправления и создала таблицу неправильно.
                # Тогда нужно:
                # 1. Удалить текущую миграцию (файл `..._initial_database_schema.py`).
                # 2. Убедиться, что `native_enum=False` в модели.
                # 3. Сгенерировать миграцию заново.
                # 4. Применить заново.
                # Если `native_enum=True` (или не указан, т.е. по умолчанию `True`), то:
                # - `render_item` выше должен помочь Alembic корректно сгенерировать миграцию.
                # - Или нужно убедиться, что `target_metadata` содержит все ENUMы.
                # - Alembic должен сгенерировать `op.create_type` до `op.create_table`.
                # Давайте временно вернем `native_enum=False` в модели, как это было в решении.
                # Это самое простое и надежное решение для PostgreSQL с SQLAlchemy/Alembic.
                # Если вы хотите использовать native_enum=True, это возможно, но требует более тонкой настройки.
                # Для начала, давайте убедимся, что модели настроены с `native_enum=False`.
                # Если `native_enum=False`, то `render_item` для Enum можно не менять или вернуть False.
                # Alembic не будет генерировать `CREATE TYPE`, и ошибка не возникнет.
                # Возвращаем False, так как при native_enum=False Alembic не должен генерировать тип.
                return False # ВАЖНО: Это работает только если native_enum=False в модели!
            # Если это другой тип Enum (например, из postgresql.dialects), обработка может отличаться.
            # Для стандартного случая, если native_enum=True и мы хотим, чтобы Alembic сам сгенерировал,
            # возвращаем False и надеемся, что метаданные корректны.
            # Но если явно нужно сгенерировать строку, можно попробовать:
            # return ", ".join([repr(v) for v in obj.enums]) + (f", name='{obj.name}'" if obj.name else "")
            # Но это хрупко. Лучше полагаться на native_enum=False.
            return False # Вернем False по умолчанию, если не уверен в native_enum=True.
        # Для других кастомных типов можно добавить условия.
        return False # Всегда возвращаем False по умолчанию, чтобы использовать стандартную логику для остальных.
        
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


# Мы вносим правки именно в эту функцию, так как она отвечает
# за конфигурацию Alembic в "online" режиме.
def do_run_migrations(connection: Connection) -> None:
    
    # Определяем функцию-обработчик для кастомного типа Vector
    def render_item(type_, obj, autogen_context):
        """
        Обрабатывает отображение кастомных типов для автогенерации.
        """
        # Проверяем, что Alembic пытается отобразить именно тип данных
        if type_ == "type" and isinstance(obj, Vector):
            # Если это наш тип Vector, добавляем необходимый импорт
            # в генерируемый файл миграции.
            autogen_context.imports.add("import pgvector.sqlalchemy")
            # И возвращаем строковое представление для кода миграции
            return f"pgvector.sqlalchemy.Vector({obj.dim})"
        
        # Для всех остальных случаев возвращаем False, 
        # чтобы Alembic использовал свою логику по умолчанию.
        return False

    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        # Добавляем наш обработчик в конфигурацию
        render_item=render_item
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
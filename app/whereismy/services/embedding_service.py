# app/whereismy/services/embedding_service.py
import logging
from sentence_transformers import SentenceTransformer
from app.whereismy.config import settings # Предполагаем, что путь к модели будет в настройках

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Сервис для генерации эмбеддингов (векторов) из текста.
    Использует sentence-transformers.
    """
    def __init__(self, model_name_or_path: str):
        """
        Инициализирует сервис, загружая модель.

        Args:
            model_name_or_path (str): Путь или имя модели Hugging Face.
        """
        logger.info(f"Загрузка модели sentence-transformers: {model_name_or_path}")
        # Загружаем модель. sentence_transformers сама определит, использовать ли CPU или CUDA.
        # Так как мы установили CPU-only версию PyTorch, она будет использовать CPU.
        self.model = SentenceTransformer(model_name_or_path)
        logger.info("Модель загружена успешно.")

    async def embed_text(self, text: str) -> list[float]:
        """
        Асинхронно генерирует эмбеддинг для заданного текста.

        Args:
            text (str): Входной текст.

        Returns:
            list[float]: Векторное представление текста.
        """
        # sentence-transformers работает синхронно внутри, но мы оборачиваем в async
        # на случай, если в будущем понадобится асинхронная загрузка или кэширование.
        # Для CPU-моделей и небольшого текста задержка минимальна.
        logger.debug(f"Векторизация текста: {text[:50]}...") # Логируем начало
        embedding = self.model.encode(text)
        logger.debug("Векторизация завершена.")
        return embedding.tolist() # Возвращаем как список Python для совместимости с JSON/SQLAlchemy

# --- Создание глобального экземпляра ---
# В реальных приложениях часто используют DI-контейнеры (например, FastDepends).
# Для простоты идем с глобальной инициализацией.
# Путь к модели берем из конфига.
embedding_service = EmbeddingService(settings.embedding_model_path)

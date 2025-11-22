# app/whereismy/web/api/main.py
from fastapi import FastAPI
from app.whereismy.web.api.routers import auth, items, categories, locations
from app.whereismy.web.admin.routes import router as admin_router

app = FastAPI(title="WhereIsMy API", version="0.1.0")

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(items.router, prefix="/api/v1", tags=["items"])
app.include_router(categories.router, prefix="/api/v1", tags=["categories"])
app.include_router(locations.router, prefix="/api/v1", tags=["locations"])
app.include_router(admin_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to WhereIsMy API"}

# Точка входа для uvicorn (например, `uvicorn app.whereismy.web.api.main:app --reload`)
# Это можно оставить здесь или вынести в отдельный скрипт запуска.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

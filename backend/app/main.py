from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth, tables, users, websocket
import asyncio

app = FastAPI(title="Dice Game API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yoloto.clava.space",
        "http://yoloto.clava.space",  # Для редиректа
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(tables.router)
app.include_router(users.router)
app.include_router(websocket.router)


@app.on_event("startup")
async def startup_event():
    """Инициализация базы данных при запуске"""
    await init_db()
    
    # Создать начальные столы, если их нет
    from app.database import AsyncSessionLocal
    from app.models.table import Table
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Table))
        tables = result.scalars().all()
        
        if not tables:
            # Создать 3 стола с разными ставками
            from decimal import Decimal
            tables_data = [
                {"name": "Стол #1", "bet_amount": Decimal("500.00")},
                {"name": "Стол #2", "bet_amount": Decimal("1000.00")},
                {"name": "Стол #3", "bet_amount": Decimal("2000.00")},
            ]
            
            for table_data in tables_data:
                table = Table(**table_data)
                db.add(table)
            
            await db.commit()


@app.get("/")
async def root():
    return {"message": "Dice Game API"}


@app.get("/health")
async def health():
    return {"status": "ok"}


from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.database import engine, Base
from src.routers import admin, cart, product
# from .broker import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await broker.start()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # await broker.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(admin.router)
app.include_router(cart.router)
app.include_router(product.router)

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api_v1.routes import user_routes, transactions_route
from db.database import close_mongo_connection, connect_to_mongo


#Database connection management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await connect_to_mongo()
    yield
    # Shutdown logic
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(transactions_route.router, prefix='/api/v1', tags=['transactions'])
app.include_router(user_routes.router, prefix='/api/v1', tags=['users'])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

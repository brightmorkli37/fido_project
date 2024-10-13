from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.api_v1.routes import transactions_route, user_routes
from db.mongodb import close_mongo_connection, connect_to_mongo


#Database connection management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await connect_to_mongo()
    yield
    # Shutdown logic
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(transactions_route.router)
app.include_router(user_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from routes import transactions, users
from db.mongodb import close_mongo_connection, connect_to_mongo

app = FastAPI()

app.include_router(transactions.router)
app.include_router(users.router)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
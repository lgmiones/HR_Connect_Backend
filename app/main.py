from fastapi import FastAPI
from app.api.router import api_router
from app.db.session import Base, engine

# Create tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HR Connect Backend")
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "HR Connect API is running"}

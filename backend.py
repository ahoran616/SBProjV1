from fastapi import FastAPI
from app.routes import router

app = FastAPI()

# Optional: a root route
@app.get("/")
def root():
    return {"message": "Hello from FastAPI backend!"}

# Include routes from app/routes.py
app.include_router(router)

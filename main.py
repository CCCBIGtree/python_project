from fastapi import FastAPI

from core.config import get_settings
from core.database import Base, engine
from routers import auth, habits

settings = get_settings()
app = FastAPI(title=settings.app_name)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(habits.router)


@app.get("/")
def health_check():
    return {"message": "Habit Tracker API is running"}

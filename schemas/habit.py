from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class HabitOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckInCreate(BaseModel):
    checkin_date: date | None = None


class CheckInOut(BaseModel):
    id: int
    habit_id: int
    checkin_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HabitStats(BaseModel):
    habit_id: int
    habit_name: str
    total_days: int
    completed_days: int
    completion_rate: float
    current_streak: int
    longest_streak: int

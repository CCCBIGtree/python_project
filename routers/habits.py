from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import decode_token
from models.habit import Habit, HabitCheckIn
from models.user import User
from schemas.habit import CheckInCreate, CheckInOut, HabitCreate, HabitOut, HabitStats

router = APIRouter(prefix="/habits", tags=["habits"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("", response_model=HabitOut, status_code=status.HTTP_201_CREATED)
def create_habit(
    payload: HabitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    habit = Habit(name=payload.name, description=payload.description, owner_id=user.id)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("", response_model=list[HabitOut])
def list_habits(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Habit).filter(Habit.owner_id == user.id).order_by(Habit.id.desc()).all()


@router.post("/{habit_id}/checkin", response_model=CheckInOut, status_code=status.HTTP_201_CREATED)
def check_in(
    habit_id: int,
    payload: CheckInCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.owner_id == user.id).first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    target_date = payload.checkin_date or date.today()
    existing = (
        db.query(HabitCheckIn)
        .filter(HabitCheckIn.habit_id == habit.id, HabitCheckIn.checkin_date == target_date)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already checked in for this date")

    checkin = HabitCheckIn(habit_id=habit.id, checkin_date=target_date)
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


@router.get("/{habit_id}/stats", response_model=HabitStats)
def get_stats(
    habit_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.owner_id == user.id).first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    checkins = (
        db.query(HabitCheckIn)
        .filter(HabitCheckIn.habit_id == habit.id)
        .order_by(HabitCheckIn.checkin_date.asc())
        .all()
    )

    completed_days = len(checkins)
    if completed_days == 0:
        return HabitStats(
            habit_id=habit.id,
            habit_name=habit.name,
            total_days=0,
            completed_days=0,
            completion_rate=0.0,
            current_streak=0,
            longest_streak=0,
        )

    first_day = checkins[0].checkin_date
    last_day = max(date.today(), checkins[-1].checkin_date)
    total_days = (last_day - first_day).days + 1
    completion_rate = round((completed_days / total_days) * 100, 2)

    longest_streak = 1
    current_streak = 0
    running_streak = 1

    checkin_dates = [c.checkin_date for c in checkins]
    for i in range(1, len(checkin_dates)):
        if (checkin_dates[i] - checkin_dates[i - 1]).days == 1:
            running_streak += 1
        else:
            longest_streak = max(longest_streak, running_streak)
            running_streak = 1
    longest_streak = max(longest_streak, running_streak)

    today = date.today()
    last_checked = checkin_dates[-1]
    if last_checked == today:
        current_streak = running_streak
    elif (today - last_checked).days == 1:
        current_streak = running_streak
    else:
        current_streak = 0

    return HabitStats(
        habit_id=habit.id,
        habit_name=habit.name,
        total_days=total_days,
        completed_days=completed_days,
        completion_rate=completion_rate,
        current_streak=current_streak,
        longest_streak=longest_streak,
    )

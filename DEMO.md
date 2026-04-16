# Habit Tracker API Demo

## 1) Install dependencies
```bash
pip install -r requirements.txt
```

## 2) Run the script demo
```bash
python demo.py
```

## 3) Expected flow
The demo will automatically execute:
1. Register (`POST /auth/register`)
2. Login (`POST /auth/login`)
3. Create habit (`POST /habits`)
4. Daily check-in (`POST /habits/{habit_id}/checkin`)
5. View stats (`GET /habits/{habit_id}/stats`)
6. List habits (`GET /habits`)

You should see status codes `201` / `200` and JSON payloads printed in terminal.

# Frontend Quick Start (React + JavaScript)

## 1) Start backend API
From project root:
```bash
uvicorn main:app --reload
```

## 2) Start frontend
Open another terminal:
```bash
cd frontend
npm install
npm run dev
```

Default frontend URL: `http://127.0.0.1:5173`

## 3) Optional API URL override
If your backend is not running at `http://127.0.0.1:8000`, create `frontend/.env`:
```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Included pages/functions
- Register & Login
- Create habit
- List habits
- Daily check-in
- Habit stats panel

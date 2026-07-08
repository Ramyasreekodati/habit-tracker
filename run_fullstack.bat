@echo off
echo Starting GrowthOS (React + FastAPI) Execution Engine...

echo [1/2] Starting FastAPI Backend...
cd backend
start cmd /k "venv\Scripts\activate && uvicorn main:app --reload"
cd ..

echo [2/2] Starting React Frontend...
cd frontend
start cmd /k "npm run dev"
cd ..

echo GrowthOS is running! The backend is on port 8000 and the frontend is on port 5173.

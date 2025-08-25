@echo off
echo Starting JudgeLab Local Development Environment...
echo.

echo Step 1: Installing dependencies...
call npm run setup:local
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Setting up environment files...
if not exist "apps\web\.env.local" (
    if exist "apps\web\.env.example" (
        copy "apps\web\.env.example" "apps\web\.env.local"
        echo Created apps\web\.env.local from example
    ) else (
        echo NEXT_PUBLIC_API_URL=http://localhost:8000 > apps\web\.env.local
        echo Created basic apps\web\.env.local
    )
)

if not exist "apps\api\.env" (
    if exist "apps\api\.env.example" (
        copy "apps\api\.env.example" "apps\api\.env"
        echo Created apps\api\.env from example
    ) else (
        echo DATABASE_URL=postgresql://judgelab:judgelab_dev@localhost:5432/judgelab > apps\api\.env
        echo REDIS_URL=redis://localhost:6379 >> apps\api\.env
        echo JWT_SECRET=dev_secret_change_in_production >> apps\api\.env
        echo ENVIRONMENT=development >> apps\api\.env
        echo Created basic apps\api\.env
    )
)

echo.
echo Step 3: Starting services...
echo.
echo Choose startup option:
echo 1. Full Docker setup (recommended for first run)
echo 2. Web frontend only (requires PostgreSQL and Redis running)
echo 3. All services separately (advanced)
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Starting all services with Docker...
    docker-compose up --build
) else if "%choice%"=="2" (
    echo Starting web frontend only...
    echo Make sure PostgreSQL and Redis are running!
    echo PostgreSQL: localhost:5432, database: judgelab, user: judgelab, password: judgelab_dev
    echo Redis: localhost:6379
    echo.
    start cmd /k "cd apps\web && npm run dev"
) else if "%choice%"=="3" (
    echo Starting all services in separate windows...
    echo Make sure PostgreSQL and Redis are running!
    echo.
    start cmd /k "cd apps\api && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    start cmd /k "cd apps\web && npm run dev"
    start cmd /k "cd worker && python -m celery worker -A main:app --loglevel=info"
    echo Services started in separate command windows
    pause
) else (
    echo Invalid choice
    pause
    exit /b 1
)
#!/bin/bash
set -e

echo "Starting JudgeLab Local Development Environment..."
echo

echo "Step 1: Installing dependencies..."
npm run setup:local
echo

echo "Step 2: Setting up environment files..."
if [ ! -f "apps/web/.env.local" ]; then
    if [ -f "apps/web/.env.example" ]; then
        cp "apps/web/.env.example" "apps/web/.env.local"
        echo "Created apps/web/.env.local from example"
    else
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > "apps/web/.env.local"
        echo "Created basic apps/web/.env.local"
    fi
fi

if [ ! -f "apps/api/.env" ]; then
    if [ -f "apps/api/.env.example" ]; then
        cp "apps/api/.env.example" "apps/api/.env"
        echo "Created apps/api/.env from example"
    else
        cat > "apps/api/.env" << EOF
DATABASE_URL=postgresql://judgelab:judgelab_dev@localhost:5432/judgelab
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev_secret_change_in_production
ENVIRONMENT=development
EOF
        echo "Created basic apps/api/.env"
    fi
fi

echo
echo "Step 3: Starting services..."
echo
echo "Choose startup option:"
echo "1. Full Docker setup (recommended for first run)"
echo "2. Web frontend only (requires PostgreSQL and Redis running)"
echo "3. All services separately (advanced)"
echo
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "Starting all services with Docker..."
        docker-compose up --build
        ;;
    2)
        echo "Starting web frontend only..."
        echo "Make sure PostgreSQL and Redis are running!"
        echo "PostgreSQL: localhost:5432, database: judgelab, user: judgelab, password: judgelab_dev"
        echo "Redis: localhost:6379"
        echo
        cd apps/web && npm run dev
        ;;
    3)
        echo "Starting all services separately..."
        echo "Make sure PostgreSQL and Redis are running!"
        echo
        
        # Start API in background
        echo "Starting API server..."
        (cd apps/api && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000) &
        API_PID=$!
        
        # Start worker in background  
        echo "Starting worker..."
        (cd worker && python -m celery worker -A main:app --loglevel=info) &
        WORKER_PID=$!
        
        # Start web frontend
        echo "Starting web frontend..."
        cd apps/web && npm run dev
        
        # Cleanup on exit
        trap "kill $API_PID $WORKER_PID" EXIT
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
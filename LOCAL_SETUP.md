# Local Development Setup Guide

This guide helps you run JudgeLab locally without CI/CD dependencies.

## Quick Start

### Windows
```cmd
start-local.bat
```

### Linux/Mac
```bash
./start-local.sh
```

## Manual Setup

### Prerequisites

**Required:**
- Node.js 18+
- Python 3.12+

**Optional (if not using Docker for databases):**
- PostgreSQL 15+
- Redis 7+

### Step 1: Install Dependencies

```bash
npm run setup:local
```

This installs:
- Root npm dependencies
- Web frontend dependencies (apps/web)

### Step 2: Set Up Environment Files

**Web Frontend (.env.local):**
```bash
cp apps/web/.env.example apps/web/.env.local
```

**API Backend (.env):**
```bash
cp apps/api/.env.example apps/api/.env
```

If examples don't exist, create basic ones:

**apps/web/.env.local:**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**apps/api/.env:**
```
DATABASE_URL=postgresql://judgelab:judgelab_dev@localhost:5432/judgelab
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev_secret_change_in_production
ENVIRONMENT=development
```

### Step 3: Install Python Dependencies

```bash
# API dependencies
cd apps/api
pip install -r requirements.txt

# Worker dependencies  
cd ../../worker
pip install -r requirements.txt
cd ..
```

### Step 4: Set Up Databases

**Option A: Use Docker (Recommended)**
```bash
npm run dev:databases
# or
docker-compose up postgres redis -d
```

**Option B: Local PostgreSQL/Redis**
- Install PostgreSQL 15+ and Redis 7+ locally
- Create database: `createdb judgelab`
- Start Redis: `redis-server`

### Step 5: Run Database Migrations and Seeding

```bash
cd apps/api
alembic upgrade head
python -m scripts.seed_data
cd ../..
```

### Step 6: Start Services

**All at once (separate terminals):**
```bash
# Terminal 1: API
npm run dev:api

# Terminal 2: Web
npm run dev:web

# Terminal 3: Worker
npm run dev:worker
```

**Or use the startup scripts:**
- Windows: `start-local.bat` → Choose option 3
- Linux/Mac: `./start-local.sh` → Choose option 3

## Access Points

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Default Login

- **Admin**: admin@judgelab.dev / admin123
- **Author**: author@judgelab.dev / author123  
- **Student**: student@judgelab.dev / student123

## Common Issues

### Port Conflicts
If ports 3000, 8000 are taken, modify:
- Web: Change `dev` script in `apps/web/package.json`
- API: Add `--port 8001` to `dev:api` script

### Database Connection Issues
1. Check PostgreSQL is running: `pg_isready -h localhost`
2. Check Redis is running: `redis-cli ping`
3. Verify connection strings in `.env` files

### Missing Dependencies
```bash
# Reinstall everything
npm run setup:local
cd apps/api && pip install -r requirements.txt
cd ../../worker && pip install -r requirements.txt
```

## Development Workflow

### Code Changes
- **Frontend**: Hot reload enabled, changes reflect immediately
- **Backend**: Auto-reload enabled with uvicorn --reload
- **Worker**: Restart manually after changes

### Testing
```bash
npm run test:web    # Frontend tests
npm run test:api    # Backend tests  
npm run lint        # All linting
npm run typecheck   # Type checking
```

### Database Changes
```bash
# Create migration
npm run migration "description"

# Apply migrations  
npm run migrate
```

## CI/CD Dependencies Disabled

The following CI/CD features are disabled for local-only setup:
- Docker image building and publishing
- Container security scanning
- Deployment to staging/production
- SonarCloud integration

Basic testing and linting still work via GitHub Actions for code quality.
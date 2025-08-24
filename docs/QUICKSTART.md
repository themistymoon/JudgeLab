# JudgeLab Quickstart Guide

This guide will get you up and running with JudgeLab in under 10 minutes.

## Prerequisites

Ensure you have the following installed:

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** v2.0+
- **Git** for cloning the repository

Optional for development:
- **Node.js 18+** and **npm** (for frontend development)
- **Python 3.12+** (for backend development)
- **.NET 8.0 SDK** (for Windows agent development)

## Step 1: Clone the Repository

```bash
git clone https://github.com/judgelab/judgelab.git
cd judgelab
```

## Step 2: Environment Setup

Copy environment files and customize if needed:

```bash
# Copy environment templates
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
cp worker/.env.example worker/.env
```

The default configuration works out-of-the-box for local development.

## Step 3: Start All Services

```bash
# Build and start all services
make dev

# Alternative: use docker-compose directly
docker-compose up --build
```

This command will:
1. ✅ Start PostgreSQL and Redis containers
2. ✅ Build API, Web, and Worker images
3. ✅ Run database migrations
4. ✅ Seed initial data
5. ✅ Start all services with hot reloading

## Step 4: Verify Installation

Wait for all services to start (about 2-3 minutes), then check:

### Web Interface
- Navigate to **http://localhost**
- You should see the JudgeLab homepage

### API Documentation  
- Visit **http://localhost/api/v1/docs**
- Interactive Swagger UI should load

### Health Checks
```bash
# Check all services are running
docker-compose ps

# Should show all services as "Up"
```

## Step 5: Test the Platform

### Create an Account
1. Go to **http://localhost**
2. Click "Get Started" or "Sign Up"
3. Create a student account

### Or Use Default Accounts
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@judgelab.dev | admin123 |
| Author | author@judgelab.dev | author123 |
| Student | student@judgelab.dev | student123 |

### Solve Your First Problem
1. Login as a student
2. Browse to "Problems"
3. Try solving "Sum Array Elements" (easy problem)
4. Submit your solution and see the results!

## Step 6: Windows Agent (Optional)

To test the lockdown agent on Windows:

```bash
cd agent-win
dotnet run
```

This will:
- Launch a locked-down browser
- Monitor system integrity
- Send heartbeats to the platform
- Block unauthorized actions

## Common Issues

### Port Conflicts
If ports 80, 3000, 5432, 6379, or 8000 are busy:

```bash
# Stop conflicting services or modify docker-compose.yml
sudo lsof -i :80  # Check what's using port 80
```

### Database Connection Issues
```bash
# Reset database and restart
docker-compose down -v
docker-compose up --build
```

### Permission Issues (Linux)
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Slow Performance
```bash
# Increase Docker memory allocation to 8GB+
# Stop unnecessary services:
docker-compose stop web  # If only testing API
```

## Next Steps

- 📖 Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand system design
- 🔨 Check [AUTHORING_GUIDE.md](AUTHORING_GUIDE.md) to create problems
- 🛡️ Review [SECURITY.md](SECURITY.md) for security features
- 🚀 See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Development Workflow

```bash
# Hot reload development
make dev

# Run tests
make test

# Check code quality
make lint
make format

# Create database migration
npm run migration "Add new feature"

# Reset everything
make clean && make dev
```

## Stopping Services

```bash
# Stop services but keep data
docker-compose stop

# Stop and remove everything (including data)
docker-compose down -v
```

---

**Need help?** Check our [troubleshooting guide](TROUBLESHOOTING.md) or open an [issue](https://github.com/judgelab/judgelab/issues).
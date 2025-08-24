# JudgeLab

[![CI/CD Pipeline](https://github.com/judgelab/judgelab/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/judgelab/judgelab/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Security](https://img.shields.io/badge/Security-First-green.svg)](docs/SECURITY.md)

> A production-quality online judge platform with advanced security features and lockdown exam browser

JudgeLab combines a competitive programming platform with enterprise-grade security, featuring a Windows lockdown agent for secure assessments, comprehensive judging system, and gamification elements.

## 🚀 Features

### 🛡️ Security-First Design
- **Lockdown Agent**: Windows app with WebView2 that blocks copy/paste, screenshots, and detects AI tools
- **Integrity Monitoring**: Real-time detection of multiple displays, unauthorized processes, and violations
- **Sandboxed Execution**: Docker-isolated judge workers with resource limits and security profiles
- **Network Isolation**: Judge containers run with `--network none` for maximum security

### 🏆 Online Judge Platform  
- **Multi-Language Support**: Python, C++, Java, JavaScript, Go, Rust
- **Advanced Judging**: Custom checkers, time/memory limits, detailed test results
- **Problem Authoring**: Rich markdown editor, test case management, availability windows
- **Timed Assessments**: Configurable solve limits, attempt tracking, late submission handling

### 🎮 Gamification
- **XP & Levels**: Earn points for solving problems, with difficulty multipliers
- **Badges & Achievements**: First AC, speed solves, streaks, clutch completions
- **Leaderboards**: Real-time rankings with seasonal competitions
- **Progress Tracking**: Solve streaks, fastest times, problem statistics

### ⚙️ Enterprise Ready
- **Scalable Architecture**: Microservices with Docker Compose orchestration
- **Database Migrations**: Alembic-managed schema with seed data
- **CI/CD Pipeline**: GitHub Actions with security scanning and multi-stage deployment
- **Monitoring**: Structured logging, health checks, and integrity audit trails

## 🏃‍♂️ Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.12+ (for backend development) 
- .NET 8.0 (for Windows agent development)

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/judgelab/judgelab.git
cd judgelab

# Start all services
make dev
```

This will:
1. Start PostgreSQL and Redis containers
2. Run database migrations
3. Seed initial data (admin, author, sample problems)
4. Launch API, Web, and Worker services
5. Start Nginx reverse proxy

### Access the Platform

- **Web Interface**: http://localhost
- **API Documentation**: http://localhost/api/v1/docs  
- **Admin Panel**: Login with `admin@judgelab.dev` / `admin123`

### Default Accounts

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| Admin | admin@judgelab.dev | admin123 | Platform administration |
| Author | author@judgelab.dev | author123 | Problem creation |
| Student | student@judgelab.dev | student123 | Testing submissions |

## 🏗️ Architecture

```mermaid
graph TB
    Agent[Windows Agent] --> Nginx[Nginx Proxy]
    Web[Next.js Frontend] --> Nginx
    Nginx --> API[FastAPI Backend]
    API --> DB[(PostgreSQL)]
    API --> Redis[(Redis)]
    API --> Worker[Celery Worker]
    Worker --> Docker[Docker Engine]
    Worker --> DB
```

### Components

- **apps/api**: FastAPI backend with authentication, problem management, judging API
- **apps/web**: Next.js frontend with Monaco editor, problem browser, submissions
- **worker**: Celery-based judge system with Docker execution
- **agent-win**: Windows lockdown browser with integrity monitoring
- **infra**: Docker configurations, Nginx proxy, database initialization

## 🔐 Security Model

### Threat Model
JudgeLab addresses academic integrity in online coding assessments:

**Assets**: Student submissions, problem test cases, assessment integrity
**Actors**: Students, instructors, system administrators  
**Trust Boundaries**: Network perimeter, container isolation, process boundaries
**Primary Threats**: Code plagiarism, external assistance, unauthorized tool usage

### Mitigations

| Threat | Mitigation | Implementation |
|--------|------------|----------------|
| Copy/Paste | Clipboard blocking | Low-level Windows hooks |
| Screenshots | Print screen detection | WH_KEYBOARD_LL hook |
| AI Assistance | Process monitoring | Window enumeration + signatures |
| Multiple Displays | Display detection | Win32 EnumDisplayDevices |
| Network Assistance | Lockdown browser | WebView2 with domain restrictions |
| Code Injection | Sandboxing | Docker with seccomp/AppArmor profiles |

See [SECURITY.md](docs/SECURITY.md) and [THREAT_MODEL.md](docs/THREAT_MODEL.md) for detailed analysis.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART](docs/QUICKSTART.md) | Step-by-step setup guide |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | System design and components |
| [AUTHORING_GUIDE](docs/AUTHORING_GUIDE.md) | Creating problems and tests |
| [SECURITY](docs/SECURITY.md) | Security features and policies |
| [THREAT_MODEL](docs/THREAT_MODEL.md) | Security analysis and risks |
| [ROADMAP](docs/ROADMAP.md) | Development phases and milestones |
| [CONTRIBUTING](docs/CONTRIBUTING.md) | Development guidelines |

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/judgelab/judgelab/issues)
- **Security**: Report security issues to security@judgelab.dev

---

**Built with ❤️ for secure, fair coding assessments**

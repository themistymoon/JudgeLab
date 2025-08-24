# Contributing to JudgeLab

We welcome contributions from the community! This guide will help you get started.

## 🚀 Quick Start for Contributors

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch
4. **Make** your changes with tests
5. **Submit** a pull request

## 📋 Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ and npm
- Python 3.12+ and pip
- .NET 8.0 SDK (for Windows agent)
- Git

### Local Environment
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/judgelab.git
cd judgelab

# Install pre-commit hooks
npm install -g pre-commit
pre-commit install

# Start development environment
make dev
```

## 🎯 How to Contribute

### 🐛 Bug Reports
Create an issue with:
- **Clear title** and description
- **Steps to reproduce** the bug
- **Expected vs actual behavior**
- **Environment details** (OS, Docker version, etc.)
- **Screenshots** if relevant

### 💡 Feature Requests  
Before proposing new features:
1. Check existing issues and discussions
2. Consider if it fits JudgeLab's security-first mission
3. Provide use cases and implementation ideas
4. Be open to alternative solutions

### 🔧 Code Contributions

#### Areas Where We Need Help
- 🛡️ **Security**: Improve lockdown agent, add security tests
- 🎮 **Gamification**: New badge types, achievement systems
- 🔍 **Judge System**: Additional language support, custom checkers
- 📱 **UI/UX**: Mobile responsiveness, accessibility improvements  
- 📚 **Documentation**: Tutorials, API docs, troubleshooting guides

#### Getting Started
1. Look for issues labeled `good-first-issue`
2. Comment on the issue to claim it
3. Join our [Discord](https://discord.gg/judgelab) for discussion
4. Follow our coding standards (below)

## 📝 Coding Standards

### General Principles
- **Security First**: All code must consider security implications
- **Type Safety**: Use TypeScript/Python typing throughout
- **Testing**: Include tests for new functionality
- **Documentation**: Update docs for API/behavior changes

### Python (API & Worker)
```python
# Use type hints
def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user with validation."""
    pass

# Follow PEP 8 with 100 character line limit
# Use ruff for linting and formatting
```

### TypeScript (Web Frontend)
```typescript
// Use strict types
interface User {
  id: number
  email: string
  role: UserRole
}

// Functional components with hooks
export function UserProfile({ user }: { user: User }) {
  // Component implementation
}
```

### C# (Windows Agent)
```csharp
// Use modern C# features
public class IntegrityMonitor : IIntegrityMonitor
{
    private readonly ILogger<IntegrityMonitor> _logger;
    
    // Async/await for I/O operations
    public async Task<bool> StartMonitoringAsync()
    {
        // Implementation
    }
}
```

## 🧪 Testing Guidelines

### Test Coverage Requirements
- **Backend**: Minimum 80% coverage for new code
- **Frontend**: Test critical user flows and components
- **Integration**: Test API endpoints and database operations

### Running Tests
```bash
# All tests
make test

# Component-specific
npm run test:api
npm run test:web
cd agent-win && dotnet test
```

### Test Types
1. **Unit Tests**: Individual functions and classes
2. **Integration Tests**: API endpoints, database operations
3. **E2E Tests**: Full user workflows with Playwright
4. **Security Tests**: Input validation, authorization checks

## 🔒 Security Considerations

### Security Review Required
- Changes to authentication/authorization
- Modifications to judge worker isolation
- Updates to lockdown agent monitoring
- New API endpoints handling user data

### Security Guidelines
- **Input Validation**: Validate all user inputs
- **SQL Injection**: Use parameterized queries
- **XSS Prevention**: Sanitize outputs properly  
- **CSRF Protection**: Include CSRF tokens
- **Rate Limiting**: Add rate limits for new endpoints

## 📖 Documentation

### Required Documentation
- **API Changes**: Update OpenAPI/Swagger specs
- **Configuration**: Document new environment variables
- **Features**: Add user-facing documentation
- **Security**: Update security policies if needed

### Documentation Style
- Use clear, concise language
- Include code examples
- Add diagrams for complex flows
- Test instructions actually work

## 📋 Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally (`make test`)
- [ ] Linting passes (`make lint`) 
- [ ] Documentation updated
- [ ] No merge conflicts with main

### PR Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] No regressions introduced

## Security Impact
Describe any security implications.

## Checklist
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added
```

### Review Process
1. **Automated Checks**: CI must pass
2. **Code Review**: At least one maintainer approval
3. **Security Review**: Required for security-sensitive changes  
4. **Testing**: QA verification for major features
5. **Deployment**: Staged rollout for significant changes

## 🌟 Recognition

### Contributors
- Added to CONTRIBUTORS.md
- Recognition in release notes
- Invitation to contributor Discord channel
- JudgeLab stickers and swag

### Maintainers
Active contributors may be invited to become maintainers with:
- Commit access to repository
- Ability to review and merge PRs
- Input on project roadmap and decisions
- Additional responsibilities and expectations

## 🎭 Code of Conduct

### Our Pledge
We are committed to making participation in JudgeLab a harassment-free experience for everyone, regardless of:
- Age, body size, disability, ethnicity, gender identity/expression
- Level of experience, nationality, personal appearance, race, religion
- Sexual identity and orientation

### Expected Behavior
- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences  
- Gracefully accept constructive criticism
- Focus on what's best for the community
- Show empathy towards other community members

### Unacceptable Behavior
- Harassment, trolling, or discriminatory language
- Publishing others' private information
- Personal attacks or political arguments
- Any conduct inappropriate in a professional setting

### Enforcement
Report violations to conduct@judgelab.dev. All complaints will be reviewed and investigated promptly and fairly.

## 📞 Getting Help

### Community Support
- **GitHub Discussions**: General questions and ideas
- **Discord**: Real-time chat and collaboration
- **Stack Overflow**: Technical questions (tag: judgelab)

### Maintainer Contact
- **General**: hello@judgelab.dev
- **Security**: security@judgelab.dev  
- **Legal**: legal@judgelab.dev

---

Thank you for contributing to JudgeLab! 🚀
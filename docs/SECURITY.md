# Security Policy

JudgeLab is designed with security as a first-class concern, particularly for academic integrity in coding assessments.

## Security Model Overview

### Assets Protected
- Student submissions and source code
- Problem test cases and solutions
- Assessment integrity and authenticity
- User authentication data
- System configuration and secrets

### Trust Boundaries
1. **Network Perimeter**: Internet ↔ Platform
2. **Container Isolation**: Host ↔ Judge workers  
3. **Process Boundaries**: Agent ↔ System processes
4. **Database Layer**: Application ↔ Data storage

## Lockdown Agent Security

### Windows Agent Protection
- **Process Isolation**: Runs with minimal privileges
- **Code Signing**: Binaries signed with certificate (production)
- **Tamper Detection**: Integrity checks against modification
- **Network Validation**: TLS certificate pinning to platform

### Monitoring Capabilities
- **Display Detection**: Prevents multi-monitor setups
- **Process Enumeration**: Detects unauthorized applications
- **Window Tracking**: Monitors foreground applications
- **Keyboard Interception**: Blocks dangerous key combinations
- **Clipboard Protection**: Prevents copy/paste operations

### AI Tool Detection
```json
{
  "processes": ["chatgpt", "copilot", "claude", "bard"],
  "windowTitles": ["ChatGPT", "GitHub Copilot", "Claude"],
  "urls": ["chat.openai.com", "claude.ai", "copilot.github.com"]
}
```

### Integrity Events
All violations are logged with:
- Timestamp and session ID
- Violation type and severity
- Process/window context
- User and attempt correlation

## Judge System Security

### Container Isolation
```yaml
security_opt:
  - "no-new-privileges:true"
  - "seccomp:unconfined"  # TODO: Custom profile
  - "apparmor:unconfined"  # TODO: Custom profile

network_mode: "none"  # No network access
cap_drop: ["ALL"]     # Drop all capabilities
read_only: true       # Immutable filesystem
tmpfs: 
  /tmp: "size=100m,noexec"  # Temporary space
```

### Resource Limits
- **CPU**: 100% of one core maximum
- **Memory**: Configurable limit (256MB default)
- **Time**: Execution timeout with buffer
- **Output**: Size limits prevent DoS attacks
- **Processes**: PID limits prevent fork bombs

### Secure Execution Pipeline
1. Source code stored in isolated temporary directory
2. Container created with security constraints
3. Code compiled/executed with timeout
4. Results extracted and container destroyed
5. Temporary files securely cleaned up

## Network Security

### TLS Configuration
- **API Endpoints**: TLS 1.3 with HSTS headers
- **Agent Communication**: Certificate pinning
- **Internal Services**: mTLS for service-to-service

### Rate Limiting
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=web:10m rate=30r/s;
```

### CORS Policy
- Restricted to configured domains
- No wildcard origins in production
- Credentials only for authenticated endpoints

## Data Protection

### Encryption at Rest
- Database: PostgreSQL with encryption
- File Storage: Encrypted judge artifacts
- Secrets: HashiCorp Vault (recommended)

### Encryption in Transit
- All external communications via HTTPS/WSS
- Internal service mesh with mTLS
- Database connections with SSL

### Data Retention
```yaml
integrity_events: 365 days    # Academic year retention
judge_artifacts: 30 days      # Source code and outputs  
submission_logs: 180 days     # Grading and appeal period
user_sessions: 7 days         # Authentication tokens
```

## Authentication & Authorization

### User Authentication
- **Local Accounts**: bcrypt password hashing
- **OAuth Integration**: GitHub, Google (configurable)
- **Session Management**: JWT tokens with rotation
- **MFA Support**: TOTP for admin accounts

### Role-Based Access Control
```yaml
Roles:
  - student: Submit solutions, view own submissions
  - author: Create problems, manage test cases
  - admin: Platform administration, user management

Permissions:
  - problems:create (author, admin)
  - problems:publish (admin)
  - integrity:review (admin)
  - users:manage (admin)
```

## Incident Response

### Monitoring & Alerting
- **Failed Authentication**: Rate limiting and lockout
- **Integrity Violations**: Real-time alerts to administrators
- **System Anomalies**: Resource usage and error rate monitoring
- **Security Events**: Centralized logging with SIEM integration

### Incident Classification
- **P0 Critical**: System compromise, data breach
- **P1 High**: Integrity violations, privilege escalation
- **P2 Medium**: Authentication bypass, DoS attacks
- **P3 Low**: Configuration issues, minor violations

## Vulnerability Management

### Security Scanning
- **Container Images**: Trivy vulnerability scanning
- **Dependencies**: Automated dependency checks
- **Code Analysis**: Static analysis with SonarQube
- **Penetration Testing**: Annual third-party assessment

### Patch Management
- **OS Updates**: Monthly security patches
- **Dependencies**: Automated updates for security fixes
- **Critical Patches**: Emergency deployment within 24 hours

## Privacy & Compliance

### Data Collection
- **Minimum Necessary**: Only data required for functionality
- **User Consent**: Clear privacy policy and consent flows
- **Data Subject Rights**: Access, portability, deletion requests

### Academic Integrity Policy
Students using JudgeLab agree to:
- Use only approved resources during assessments
- Not attempt to bypass security measures
- Report integrity violations or security concerns
- Accept monitoring during exam sessions

### Accommodation Support
- **Disability Accommodations**: Alternative assessment methods
- **Technical Issues**: Grace periods and manual review options
- **False Positives**: Appeals process for integrity violations

## Threat Model

See [THREAT_MODEL.md](THREAT_MODEL.md) for detailed threat analysis.

## Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

### Contact Information
- **Email**: security@judgelab.dev
- **PGP Key**: [Available on keybase](https://keybase.io/judgelab)
- **Response Time**: 48 hours acknowledgment, 30 days resolution

### Disclosure Policy
- **Coordinated Disclosure**: Work with security team before public release
- **Bounty Program**: Recognition and rewards for valid findings
- **Credit**: Public acknowledgment (with permission) after resolution

---

*This security policy is reviewed quarterly and updated as needed.*
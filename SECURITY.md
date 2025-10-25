# Security Policy

## Supported Versions

We actively maintain security updates for the following versions of Bulk File Renamer:

| Version | Supported          | Notes |
| ------- | ------------------ | ----- |
| 1.0.x   | :white_check_mark: | Current stable release |
| < 1.0   | :x:                | Pre-release versions not supported |

## Reporting a Vulnerability

We take security seriously and appreciate your help in keeping Bulk File Renamer secure for all users.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities privately using one of these methods:

1. **GitHub Security Advisories**
   - Go to: https://github.com/dominic-ritzmann/bulk-file-renamer/security/advisories/new
   - Click "Report a vulnerability"
   - Fill out the security advisory form

### What to Include

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Impact**: Potential impact and affected systems
- **Environment**: Operating system, Python version, app version
- **Proof of Concept**: If applicable, include a minimal proof of concept
- **Suggested Fix**: If you have ideas for fixing the issue

### What to Expect

**Response Timeline:**
- **Initial Response**: Within 24-48 hours
- **Status Updates**: Weekly updates on progress
- **Resolution**: Typically within 30 days for critical issues

**Our Process:**
1. **Acknowledgment**: We'll confirm receipt of your report
2. **Investigation**: We'll investigate and validate the vulnerability
3. **Fix Development**: We'll develop and test a fix
4. **Release**: We'll release a security update
5. **Disclosure**: We'll coordinate public disclosure

**What You Can Expect:**
- **Confidentiality**: Your report will be kept confidential until resolved
- **Credit**: You'll be credited for responsible disclosure (if desired)
- **Updates**: Regular updates on our progress
- **Recognition**: Public acknowledgment of your contribution

### Vulnerability Severity

We classify vulnerabilities using the following severity levels:

| Severity | Description | Response Time |
|----------|-------------|---------------|
| **Critical** | Remote code execution, data breach | 24 hours |
| **High** | Privilege escalation, data exposure | 48 hours |
| **Medium** | Information disclosure, DoS | 1 week |
| **Low** | Minor security issues | 2 weeks |

### Security Best Practices

**For Users:**
- **Keep Updated**: Always use the latest version
- **Verify Downloads**: Download only from official sources
- **Report Issues**: Report any suspicious behavior
- **Use Antivirus**: Keep your antivirus software updated

**For Developers:**
- **Code Review**: All code changes are reviewed
- **Dependency Scanning**: Regular dependency vulnerability scanning
- **Secure Development**: Following secure coding practices
- **Testing**: Comprehensive security testing

### Security Features

Bulk File Renamer includes several security features:

- **File Validation**: Validates file operations before execution
- **Permission Checks**: Verifies file system permissions
- **Input Sanitization**: Sanitizes user inputs to prevent injection
- **Safe File Operations**: Uses safe file handling practices
- **Error Handling**: Secure error handling without information disclosure

### Third-Party Dependencies

We regularly monitor and update third-party dependencies:

- **Dependabot**: Automated dependency updates
- **Security Scanning**: Regular vulnerability scanning
- **Minimal Dependencies**: Only essential dependencies included
- **Version Pinning**: Specific version requirements for security

### Security Updates

**Release Schedule:**
- **Critical**: Immediate release
- **High**: Within 1 week
- **Medium**: Within 1 month
- **Low**: Next regular release

**Notification Methods:**
- **GitHub Releases**: Security updates marked clearly
- **Email**: Notifications for critical vulnerabilities
- **In-App**: Update notifications within the application

### Responsible Disclosure

We follow responsible disclosure practices:

1. **Private Reporting**: Vulnerabilities reported privately first
2. **Coordinated Disclosure**: Public disclosure coordinated with fix release
3. **Credit**: Proper credit given to security researchers
4. **Timeline**: Reasonable time given for fix development

### Contact Information

**Security Team:**
- **Primary**: GitHub Security Advisories
- **Response Time**: 24-48 hours

**General Security Questions:**
- **[GitHub Discussions](https://github.com/ritzmanndominic/bulk_file_renamer/discussions)**: For general security questions
- **[Documentation](https://github.com/ritzmanndominic/bulk_file_renamer/blob/main/bulk_file_renamer/docs/README.md)**: Check our documentation

### Legal

**Safe Harbor:**
- Security research conducted in good faith is welcome
- We won't pursue legal action against security researchers
- Please act in good faith and avoid causing harm

**Scope:**
- Only test against your own installations
- Don't access or modify data that isn't yours
- Don't disrupt our services or other users

---

**Thank you for helping keep Bulk File Renamer secure!**

*Last updated: October 2025*

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- 🗄️ Database support for persistent key storage
- 🌐 Web UI for key management and monitoring
- 📊 Advanced analytics dashboard with statistics
- 🔍 Enhanced search algorithms with ML-based filtering
- 🔐 Encrypted key storage with access control
- 📱 Mobile app for monitoring on the go
- 🤖 AI-powered key validation optimization

---

## [0.0.2-beta] - 2025-01-07

### Added
- 📚 Comprehensive documentation (README.md, README_CN.md)
- 🧹 Project cleanup and reorganization scripts
- 📁 Improved project structure with clear separation of concerns
- 🐳 Production-ready Docker configurations
- 🚀 Zero-downtime deployment script
- 📝 Detailed configuration examples
- 🔧 Makefile for common operations

### Changed
- ♻️ Refactored module import system for better reliability
- 📦 Updated dependencies to latest stable versions
- 🎯 Optimized search queries for better results
- ⚡ Improved parallel validation performance

### Fixed
- 🐛 Fixed module import errors in parallel scanner
- 🔧 Fixed path issues in Docker environment
- 📂 Fixed data directory auto-creation
- 🔐 Fixed permission issues in containerized deployment

### Renamed
- 📝 Renamed `hajimi_king_parallel.py` to `api_key_scanner.py` for better clarity

### Security
- 🔒 Added .dockerignore to prevent sensitive file exposure
- 🛡️ Implemented non-root user in Docker containers
- 🔐 Enhanced environment variable security

---

## [0.0.1-beta] - 2024-12-15

### Added
- 🎉 Initial beta release
- 🔍 GitHub code search functionality
- ⚡ Parallel key validation system
- 🐳 Basic Docker support
- 📊 External synchronization to Gemini Balancer and GPT Load
- 📈 Incremental scanning with checkpoint support
- 🌐 Proxy rotation support
- 📝 Basic logging system

### Known Issues
- Module import errors in some environments
- Limited error handling for network failures
- No persistent storage for discovered keys
- Basic UI/UX for configuration

---

## [0.0.1-alpha] - 2024-11-01

### Added
- 🚀 Initial proof of concept
- 🔍 Basic GitHub search implementation
- ✅ Simple key validation
- 📁 File-based storage

### Notes
- This was the initial development version
- Not recommended for production use
- Many features were experimental

---

## Version History Summary

| Version | Release Date | Status | Major Features |
|---------|--------------|--------|----------------|
| 0.0.2-beta | 2025-01-07 | Current | Documentation, Docker, Cleanup |
| 0.0.1-beta | 2024-12-15 | Stable | Parallel validation, External sync |
| 0.0.1-alpha | 2024-11-01 | Deprecated | Initial concept |

---

## Upgrade Guide

### From 0.0.1-beta to 0.0.2-beta

1. **Backup your data**
   ```bash
   cp -r data/ data_backup/
   ```

2. **Update configuration**
   - New environment variables added
   - Check `env.example` for new options

3. **Update Docker setup**
   ```bash
   docker-compose down
   docker-compose pull
   docker-compose up -d
   ```

4. **Run cleanup script**
   ```bash
   python cleanup_project.py
   ```

### From 0.0.1-alpha to 0.0.2-beta

1. **Complete reinstallation recommended**
   - Too many breaking changes
   - Backup any important data first

2. **Migration steps**
   ```bash
   # Backup old data
   mv hajimi-king hajimi-king-old
   
   # Fresh installation
   git clone https://github.com/yourusername/hajimi-king.git
   cd hajimi-king
   
   # Copy old keys if needed
   cp ../hajimi-king-old/data/keys/* data/keys/
   ```

---

## Deprecation Notices

### Deprecated in 0.0.2-beta
- `app/hajimi_king.py` - Use `app/api_key_scanner.py` instead
- Single-threaded validation - Parallel validation is now default
- Old file naming convention - New date-based naming

### Removed in 0.0.2-beta
- Legacy configuration format
- Synchronous GitHub API calls
- Manual proxy configuration

---

## Security Advisories

### 2025-01-07 - Low Severity
- Fixed potential path traversal in file operations
- Recommendation: Update to 0.0.2-beta

### 2024-12-20 - Medium Severity
- API keys were stored in plain text logs
- Fixed in 0.0.1-beta patch
- Recommendation: Rotate any exposed keys

---

## Contributors

Thanks to all contributors who have helped shape Hajimi King:

- [@yourusername](https://github.com/yourusername) - Project creator
- [@contributor1](https://github.com/contributor1) - Docker improvements
- [@contributor2](https://github.com/contributor2) - Documentation
- [@contributor3](https://github.com/contributor3) - Bug fixes

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for full list.

---

## How to Contribute

1. Check [current issues](https://github.com/yourusername/hajimi-king/issues)
2. Read [CONTRIBUTING.md](CONTRIBUTING.md)
3. Submit PRs against `develop` branch
4. Ensure all tests pass
5. Update documentation as needed

---

[Unreleased]: https://github.com/yourusername/hajimi-king/compare/v0.0.2-beta...HEAD
[0.0.2-beta]: https://github.com/yourusername/hajimi-king/compare/v0.0.1-beta...v0.0.2-beta
[0.0.1-beta]: https://github.com/yourusername/hajimi-king/compare/v0.0.1-alpha...v0.0.1-beta
[0.0.1-alpha]: https://github.com/yourusername/hajimi-king/releases/tag/v0.0.1-alpha
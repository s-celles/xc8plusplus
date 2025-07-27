# GitHub Actions Version Updates

This document tracks the updated GitHub Actions to resolve deprecation warnings and use the latest stable versions.

## Updated Actions

### CI Workflow (`ci.yml`)
- ✅ `actions/setup-python@v4` → `actions/setup-python@v5`
- ✅ `actions/upload-artifact@v3` → `actions/upload-artifact@v4`
- ✅ `codecov/codecov-action@v3` → `codecov/codecov-action@v4`

### Documentation Workflow (`pages.yml`)
- ✅ `actions/setup-python@v4` → `actions/setup-python@v5`
- ✅ `actions/configure-pages@v3` → `actions/configure-pages@v4`
- ✅ `actions/upload-pages-artifact@v2` → `actions/upload-pages-artifact@v3`
- ✅ `actions/deploy-pages@v2` → `actions/deploy-pages@v4`

### Release Workflow (`release.yml`)
- ✅ `actions/setup-python@v4` → `actions/setup-python@v5`
- ✅ `softprops/action-gh-release@v1` → `softprops/action-gh-release@v2`

### Pre-commit Configuration (`.pre-commit-config.yaml`)
- ✅ `pre-commit-hooks@v4.5.0` → `pre-commit-hooks@v4.6.0`
- ✅ `black@23.12.1` → `black@24.8.0`
- ✅ `flake8@7.0.0` → `flake8@7.1.1`
- ✅ `mypy@v1.8.0` → `mypy@v1.11.2`
- ✅ `bandit@1.7.6` → `bandit@1.7.9`

## Key Changes

### actions/upload-artifact@v4
- **Breaking Change**: The main difference is in how artifacts are handled
- **Benefit**: Better performance and more reliable artifact uploads
- **Migration**: No changes needed in our usage patterns

### actions/setup-python@v5
- **Benefit**: Better caching and Node.js 20 runtime
- **Migration**: Seamless upgrade, no breaking changes

### codecov/codecov-action@v4
- **Benefit**: Improved security and performance
- **Migration**: May require token configuration for private repos

### GitHub Pages Actions
- **Benefit**: Enhanced security and performance for Pages deployment
- **Migration**: Automatic, no configuration changes needed

## Testing
All workflows have been tested and are compatible with the current project structure. The test suite continues to pass with these updates.

## Future Maintenance
- Dependabot will automatically create PRs for future action updates
- Monitor GitHub's changelog for deprecation notices
- Update this document when new versions are adopted

# Common Python Testing & Build Issues - Prevention Guide

## 🔴 Critical Issues (Must Fix Immediately)

### 1. Unused Imports (Flake8 F401)
**Symptom:** `F401 'module' imported but unused`

**Causes:**
- Leftover imports from refactoring
- Copy-pasted code with unnecessary imports
- IDE auto-imports not cleaned up

**Prevention:**
```bash
# Pre-commit hook with Flake8
# IDE: Enable "Optimize Imports on Save"
# Use: flake8 --select=F401 to check only unused imports
```

**Fix:**
```python
# ❌ Bad
import asyncio  # Not used anywhere
from unittest.mock import Mock  # Not used

# ✅ Good
# Only import what you use
```

---

### 2. Code Formatting Inconsistencies (Black)
**Symptom:** `would reformat X files`

**Causes:**
- Different Black versions (local vs CI)
- Not running Black before commit
- Manual formatting overrides

**Prevention:**
```bash
# Pin Black version
black==25.12.0

# Pre-commit hook
pre-commit install

# Run before commit
black .
```

**Fix:**
```bash
cd backend
black .
git add -A
git commit -m "style: Format with Black"
```

---

### 3. Import Order Issues (E402, I001)
**Symptom:** `E402 module level import not at top of file`

**Causes:**
- Imports after code execution
- sys.path manipulation before imports
- Circular import workarounds

**Prevention:**
```python
# ✅ Correct order
# 1. Standard library
import os
import sys

# 2. Third-party
import pytest
from fastapi import FastAPI

# 3. Local
from my_module import MyClass

# 4. sys.path manipulation (if absolutely necessary)
sys.path.insert(0, str(Path(__file__).parent))
```

**Fix with isort:**
```bash
isort backend/tests/*.py
```

---

## ⚠️ Common Issues (Should Fix Soon)

### 4. Missing Type Hints
**Symptom:** mypy errors, runtime type errors

**Causes:**
- Legacy code without types
- Quick prototyping
- Lack of type checking enforcement

**Prevention:**
```python
# ❌ Bad
def process_data(data):
    return data.upper()

# ✅ Good
from typing import Optional

def process_data(data: str) -> str:
    return data.upper()

def get_user(user_id: int) -> Optional[dict]:
    # Returns dict or None
    pass
```

---

### 5. Hardcoded Secrets/Credentials
**Symptom:** Bandit B105, B106 errors

**Causes:**
- Quick testing
- Forgotten to use environment variables
- Copy-pasted examples

**Prevention:**
```python
# ❌ Bad
API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"

# ✅ Good
import os
API_KEY = os.getenv("API_KEY")
PASSWORD = os.getenv("PASSWORD")
```

---

### 6. Overly Complex Functions
**Symptom:** Flake8 C901 complexity too high

**Causes:**
- Too many nested if/else
- Long functions
- Multiple responsibilities

**Prevention:**
```python
# ❌ Bad (complexity > 10)
def process(data):
    if condition1:
        if condition2:
            if condition3:
                # ... many nested levels

# ✅ Good (break into smaller functions)
def validate_data(data):
    return condition1 and condition2

def process(data):
    if not validate_data(data):
        return
    # ... simpler logic
```

---

### 7. Missing Docstrings
**Symptom:** pydocstyle D100, D101 errors

**Causes:**
- Quick prototyping
- Lack of documentation culture
- Unclear requirements

**Prevention:**
```python
# ❌ Bad
def calculate_total(items):
    return sum(items)

# ✅ Good
def calculate_total(items: list[float]) -> float:
    """
    Calculate the total sum of numeric items.

    Args:
        items: List of numeric values to sum

    Returns:
        The total sum of all items

    Raises:
        TypeError: If items contains non-numeric values
    """
    return sum(items)
```

---

### 8. Inconsistent Naming Conventions
**Symptom:** Pylint C0103 naming convention violations

**Causes:**
- Not following PEP 8
- Copy-pasted code from other languages
- Lack of style guide

**Prevention:**
```python
# ❌ Bad
def CalculateTotal(ItemList):  # PascalCase for function
    MyVariable = 0  # PascalCase for variable

# ✅ Good (PEP 8)
def calculate_total(item_list):  # snake_case for functions
    my_variable = 0  # snake_case for variables

class MyClass:  # PascalCase for classes
    CONSTANT_VALUE = 100  # UPPER_CASE for constants
```

---

## 📋 Testing-Specific Issues

### 9. Test Isolation Problems
**Symptom:** Tests pass individually but fail together

**Causes:**
- Shared state between tests
- Not cleaning up resources
- Order-dependent tests

**Prevention:**
```python
import pytest

# ✅ Use fixtures for setup/teardown
@pytest.fixture(autouse=True)
def cleanup_sessions():
    """Cleanup after each test"""
    yield
    if os.path.exists("sessions"):
        shutil.rmtree("sessions")

# ✅ Don't rely on test order
def test_create():
    # Each test should be independent
    pass
```

---

### 10. Async Test Issues
**Symptom:** `RuntimeWarning: coroutine was never awaited`

**Causes:**
- Missing `await` keyword
- Not marking test as async
- Wrong pytest plugin

**Prevention:**
```python
# ❌ Bad
def test_async_function():
    result = my_async_function()  # Missing await

# ✅ Good
@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result is not None
```

---

### 11. Mock/Patch Issues
**Symptom:** Tests don't mock correctly, real APIs called

**Causes:**
- Wrong patch target
- Patch applied after import
- Not using context managers

**Prevention:**
```python
from unittest.mock import patch, Mock

# ❌ Bad
@patch('my_module.external_api')  # Wrong target
def test_function(mock_api):
    pass

# ✅ Good
@patch('module_under_test.external_api')  # Patch where it's used
def test_function(mock_api):
    mock_api.return_value = {"status": "success"}
    result = my_function()
    assert result["status"] == "success"
```

---

### 12. Fixture Scope Issues
**Symptom:** Fixtures not shared/isolated correctly

**Causes:**
- Wrong fixture scope
- Not understanding scope levels
- Fixture dependencies

**Prevention:**
```python
# Fixture scopes: function (default), class, module, session

@pytest.fixture(scope="function")  # New instance per test
def user():
    return User(name="Test")

@pytest.fixture(scope="session")  # One instance for all tests
def database():
    db = Database()
    yield db
    db.close()
```

---

## 🛠️ Build-Specific Issues

### 13. Dependency Version Conflicts
**Symptom:** `pip install` fails, incompatible versions

**Causes:**
- Unpinned dependencies
- Transitive dependency conflicts
- Different Python versions

**Prevention:**
```bash
# ✅ Pin all dependencies
pip freeze > requirements.txt

# ✅ Use pip-tools
pip-compile requirements.in

# ✅ Specify Python version
python_requires='>=3.11,<3.14'
```

---

### 14. PYTHONPATH Issues
**Symptom:** `ModuleNotFoundError` in CI but works locally

**Causes:**
- Different working directories
- Missing PYTHONPATH configuration
- Relative imports

**Prevention:**
```yaml
# CI/CD workflow
- name: Run tests
  run: |
    cd backend
    export PYTHONPATH=$PYTHONPATH:$(pwd)
    pytest
```

---

### 15. Platform-Specific Issues
**Symptom:** Tests pass on Mac/Linux, fail on Windows

**Causes:**
- Path separators (/ vs \)
- Line endings (LF vs CRLF)
- Case-sensitive file systems

**Prevention:**
```python
# ✅ Use pathlib for cross-platform paths
from pathlib import Path

file_path = Path("data") / "file.txt"  # Works on all platforms

# ✅ Use os.path.join
import os
file_path = os.path.join("data", "file.txt")
```

---

## 📊 Action Items Checklist

### Immediate (Do Now)
- [ ] Install pre-commit hooks
- [ ] Run Black on all files
- [ ] Remove unused imports
- [ ] Pin all dependency versions
- [ ] Configure PYTHONPATH in CI

### Short-term (This Week)
- [ ] Add type hints to new code
- [ ] Configure isort
- [ ] Set up bandit security scanning
- [ ] Add docstrings to public functions
- [ ] Review and reduce function complexity

### Medium-term (This Month)
- [ ] Add mypy type checking
- [ ] Achieve 90% test coverage
- [ ] Add complexity limits to Flake8
- [ ] Create CONTRIBUTING.md
- [ ] Set up automated dependency updates

### Long-term (This Quarter)
- [ ] Add type hints to all code
- [ ] Implement full Pylint checking
- [ ] Set up code quality dashboard
- [ ] Regular security audits
- [ ] Performance profiling

---

## 🚀 Quick Reference Commands

```bash
# Format code
black backend/

# Sort imports
isort backend/

# Check linting
flake8 backend/

# Type checking
mypy backend/

# Security scan
bandit -r backend/

# Run tests with coverage
pytest --cov=backend --cov-report=term-missing

# Install pre-commit hooks
pre-commit install

# Run all pre-commit checks
pre-commit run --all-files

# Update dependencies
pip-compile --upgrade requirements.in
```

---

## 📚 Resources

- **PEP 8:** https://pep8.org/
- **Black:** https://black.readthedocs.io/
- **Flake8:** https://flake8.pycqa.org/
- **mypy:** https://mypy.readthedocs.io/
- **pytest:** https://docs.pytest.org/
- **pre-commit:** https://pre-commit.com/

---

**Last Updated:** 2025-12-25
**Maintained By:** Development Team

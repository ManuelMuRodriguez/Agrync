# Testing

Agrync has three independent test suites: a backend test suite for the FastAPI application, a frontend unit test suite, and an end-to-end (E2E) browser test suite.

---

## Backend tests

**Location:** `agrync_backend/tests/`  
**Runner:** `pytest` + `pytest-asyncio`  
**Result:** 99 passed, 1 xfailed

### Stack

| Package | Purpose |
|---|---|
| `pytest-asyncio` | `asyncio` mode for async test functions |
| `mongomock-motor` | In-memory MongoDB — no Docker required for tests |
| `httpx[asyncio]` | `AsyncClient` with `ASGITransport` for request simulation |
| `Beanie` (test init) | Re-initialised per test with the mock motor client |

### How isolation works

The `conftest.py` in `tests/` performs the following for each test:

1. Sets all required environment variables in `os.environ` at import time.
2. Creates a `mongomock_motor.AsyncMongoMockClient` instance.
3. Initialises `Beanie` with the mock client and all document models:
   - `User`, `ModbusDevice`, `Task`
4. Builds an `httpx.AsyncClient` using `ASGITransport(app=app)` pointing at the FastAPI app.
5. Tears down the mock client after the test to keep state isolated.

### env vars set in conftest

```python
os.environ["ACCESS_TOKEN_SECRET_KEY"] = "test_secret_key"
os.environ["REFRESH_TOKEN_SECRET_KEY"] = "test_refresh_key"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_MINUTES"] = "1440"
os.environ["ADMIN_EMAIL"] = "admin@test.com"
```

### Test files

| File | Covers |
|---|---|
| `test_auth.py` | `/validate`, `/login`, `/refresh`, `/register`, `/logout`, `/info` |
| `test_modbus_logic.py` | Modbus router: create/read/update/delete devices, slaves and variables |
| `test_models.py` | Pydantic model validation: required fields, defaults, constraints |
| `test_tasks.py` | Task start/stop/state endpoints and the locking mechanism |
| `test_utils.py` | `datetime.py` and `password.py` utility functions |

### Running the suite

```bash
cd agrync_backend
pytest
```

To run with verbose output:

```bash
pytest -v
```

To run a single file:

```bash
pytest tests/test_auth.py -v
```

### Adding a new test

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_example(async_client: AsyncClient):
    response = await async_client.get("/api/v1/something")
    assert response.status_code == 200
```

The `async_client` fixture is defined in `conftest.py` and injects a fully-configured `AsyncClient` with a mock MongoDB.

---

## Frontend unit tests

**Location:** `agrync_frontend/src/test/`  
**Runner:** Vitest  
**Config:** `agrync_frontend/vitest.config.ts`  
**Result:** 49/49 passed

### Run

```bash
cd agrync_frontend
npm run test
```

To run once (CI mode):

```bash
npm run test -- --run
```

### Coverage

```bash
npm run test -- --coverage
```

---

## Frontend E2E tests

**Location:** `agrync_frontend/e2e/`  
**Runner:** Playwright  
**Config:** `agrync_frontend/playwright.config.cjs`  
**Result:** 11/11 passed

### Test files

| File | Covers |
|---|---|
| `login.spec.cjs` | Login flow: valid credentials, invalid credentials, redirect to dashboard |
| `protected-routes.spec.cjs` | Unauthenticated access redirects to login; authenticated access succeeds |

### Run

```bash
cd agrync_frontend
npx playwright test --config playwright.config.cjs
```

To run a single spec:

```bash
npx playwright test e2e/login.spec.cjs --config playwright.config.cjs
```

To open the Playwright HTML report after a run:

```bash
npx playwright show-report
```

> **Prerequisites**: The full Docker Compose stack must be running when executing E2E tests: `docker compose up -d`

---

## All suites together

```bash
# Backend
cd agrync_backend && pytest

# Frontend unit
cd agrync_frontend && npm run test -- --run

# Frontend E2E (requires running stack)
cd agrync_frontend && npx playwright test --config playwright.config.cjs
```

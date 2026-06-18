# API Service

Target: `FastAPI`

Initial modules:
- `auth`
- `rbac`
- `cases`
- `documents`
- `knowledge`
- `analysis`
- `chat`
- `drafting`
- `export`
- `audit`
- `plans`

Suggested substructure:
- `app/api`
- `app/domain`
- `app/services`
- `app/repositories`
- `app/workers`
- `tests`

Implemented starter:
- `app/main.py`
- `app/api/routes/auth.py`
- `app/services/auth_service.py`
- `tests/test_auth_password_recovery.py`

Run locally:

```bash
uvicorn app.main:app --app-dir services/api --reload
pytest services/api/tests
```

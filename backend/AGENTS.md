# FastAPI Backend - Agent Guidelines

## Development Commands
- **Run server**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **Database migrations**: `alembic upgrade head` (apply) / `alembic revision --autogenerate -m "description"` (create)
- **Test single file**: `pytest tests/test_module.py::test_function -v` (no test framework currently set up)
- **Install dependencies**: `pip install -r requirements.txt`

## Code Style Guidelines
- **Imports**: Standard library → third-party → local app imports, each group separated by blank line
- **Formatting**: Use 4-space indentation, line length ~88 characters
- **Type hints**: Required for all function parameters and return values using `typing` module
- **Naming**: `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_CASE` for constants
- **Async patterns**: Use `async/await` consistently for database operations and I/O
- **Error handling**: Raise `HTTPException` with appropriate status codes and descriptive messages
- **Dependencies**: Use FastAPI's `Depends()` for database sessions and service injection
- **Models**: SQLAlchemy models inherit from `Base`, Pydantic schemas use `BaseModel` with `from_attributes = True`
- **Security**: Passwords must be hashed using `get_password_hash()`, never store plain text passwords
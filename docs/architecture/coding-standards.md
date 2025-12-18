# Coding Standards

## Critical Fullstack Rules

-   **Public and Protected Routes:** The main dashboard route (`/`) **must** be publicly accessible without requiring authentication. All other application routes (e.g., `/cvs/upload`, `/profile`) **must** be protected and require a logged-in user. Unauthenticated users attempting to access protected routes **must** be redirected to the login page (`/login`).
-   **Type Sharing:** All TypeScript types and interfaces shared between the frontend and backend API (e.g., data models, API payloads) **must** be defined in the `packages/shared-types` package and imported from there. Do not redefine types in the frontend.
-   **API Calls:** All frontend API interactions **must** be channeled through the centralized `API Service Layer` (`/services`). Never make direct `fetch` or `axios` calls from UI components.
-   **Backend Modularity:** All new backend logic **must** be encapsulated within a feature module in `apps/backend/app/modules/`. Each module must follow the `router.py`, `service.py`, `schemas.py`, `models.py` pattern.
-   **Cookie Security:** Do not attempt to read or write authentication tokens from client-side JavaScript. Rely on `HttpOnly` cookies and the backend to manage the session. The frontend must use `withCredentials: true` (or the equivalent) for all API calls.
-   **Environment Variables:** Access environment variables only through a dedicated configuration module (e.g., `app/core/config.py` in the backend). Never access `process.env` directly within frontend components or backend business logic.
-   **State Updates:** In React components, never mutate state directly. Always use the setter function from `useState` or dispatch actions for reducers.

## SQLAlchemy Async Rules

When working with SQLAlchemy in an async environment, follow these rules to avoid `MissingGreenlet` errors and session management issues:

### 1. Store Attribute Values Before Commit

**Problem:** After calling `db.commit()`, SQLAlchemy will **expire** all objects in the session. If you access an attribute after commit, SQLAlchemy will attempt to lazy-load from the database, causing errors in async context.

```python
# ❌ WRONG - Accessing attribute after commit
async def update_item(item_id: int, current_user: User, db: AsyncSession):
    item = await get_item(db, item_id)
    item.status = "updated"
    await db.commit()
    
    # ERROR: current_user.email will trigger lazy-load after session expired
    logger.info(f"Updated by {current_user.email}")

# ✅ CORRECT - Store value before commit
async def update_item(item_id: int, current_user: User, db: AsyncSession):
    user_email = current_user.email  # Store before commit
    
    item = await get_item(db, item_id)
    item.status = "updated"
    await db.commit()
    
    logger.info(f"Updated by {user_email}")  # Use stored variable
```

### 2. Use Eager Loading for Relationships

**Problem:** Lazy-loaded relationships do not work in async context after the query has completed.

```python
# ❌ WRONG - Lazy loading relationship
async def get_user_with_cvs(user_id: int, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    
    # ERROR: user.cvs will trigger lazy-load
    return {"user": user, "cv_count": len(user.cvs)}

# ✅ CORRECT - Eager loading with selectinload
from sqlalchemy.orm import selectinload

async def get_user_with_cvs(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(User)
        .options(selectinload(User.cvs))  # Load CVs together with User
        .where(User.id == user_id)
    )
    user = result.scalar_one()
    
    return {"user": user, "cv_count": len(user.cvs)}  # OK
```

### 3. Refresh Object After Commit If Continued Use Is Needed

```python
# ✅ CORRECT - Refresh to reload fresh data
async def create_item(data: ItemCreate, db: AsyncSession):
    item = Item(**data.dict())
    db.add(item)
    await db.commit()
    await db.refresh(item)  # Reload item with fresh data from DB
    
    return item  # OK - item has been refreshed
```

### 4. Do Not Pass ORM Objects Outside Session Context

```python
# ❌ WRONG - Returning ORM object that may be accessed after session closes
async def get_user(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one()  # Dangerous if caller accesses lazy attributes

# ✅ CORRECT - Convert to Pydantic model or dict
async def get_user(user_id: int, db: AsyncSession) -> UserResponse:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    return UserResponse.model_validate(user)  # Safe - converted to Pydantic
```

### 5. Quick Reference

| Scenario | Solution |
|----------|----------|
| Need attribute after `commit()` | Store in variable before commit |
| Need to access relationship | Use `selectinload()` or `joinedload()` |
| Need to use object after commit | Call `await db.refresh(obj)` |
| Return data from function | Convert to Pydantic model |

## Naming Conventions

| Element | Frontend Convention | Backend Convention | Example |
| :--- | :--- | :--- | :--- |
| Components (React) | `PascalCase` | N/A | `UserProfile.tsx` |
| Hooks (React) | `camelCase` with `use` prefix | N/A | `useAuth.ts` |
| API Routes | N/A | `kebab-case` | `/api/v1/user-profile` |
| Database Tables | N/A | `snake_case` (plural) | `user_profiles`, `cvs` |
| Python Variables/Functions | N/A | `snake_case` | `get_current_user` |
| Python Classes | N/A | `PascalCase` | `class AuthService:` |
| TypeScript Types/Interfaces | `PascalCase` | N/A | `interface UserProfile {}` |

---
"""
Seed Test Users Script

This script creates test users for each role:
- admin@example.com (admin)
- jobseeker@example.com (job_seeker)
- recruiter@example.com (recruiter)

Usage:
    python -m scripts.seed_users
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.modules.users.models import User
# Import related models to resolve relationships
from app.modules.cv.models import CV  # noqa: F401
from app.modules.jobs.models import JobDescription  # noqa: F401
from app.modules.ai.models import CVAnalysis  # noqa: F401


# Test users configuration
TEST_USERS = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True,
    },
    {
        "email": "jobseeker@example.com",
        "password": "test123",
        "full_name": "Job Seeker User",
        "role": "job_seeker",
        "is_active": True,
    },
    {
        "email": "recruiter@example.com",
        "password": "test123",
        "full_name": "Recruiter User",
        "role": "recruiter",
        "is_active": True,
    },
]


async def seed_user(db: AsyncSession, user_data: dict) -> tuple[bool, str]:
    """
    Create a test user if they don't exist.
    
    Returns:
        Tuple of (created: bool, message: str)
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data["email"])
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        # Update role if different
        if existing_user.role != user_data["role"]:
            existing_user.role = user_data["role"]
            existing_user.is_active = user_data["is_active"]
            await db.commit()
            return True, f"Updated existing user: {user_data['email']} -> role={user_data['role']}"
        return False, f"User already exists: {user_data['email']}"
    
    # Create new user
    hashed_password = get_password_hash(user_data["password"])
    new_user = User(
        email=user_data["email"],
        hashed_password=hashed_password,
        full_name=user_data["full_name"],
        role=user_data["role"],
        is_active=user_data["is_active"],
    )
    db.add(new_user)
    await db.commit()
    
    return True, f"Created user: {user_data['email']} (role={user_data['role']})"


async def main():
    """Main function to seed all test users."""
    print("=" * 60)
    print("Seeding Test Users")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        for user_data in TEST_USERS:
            created, message = await seed_user(db, user_data)
            status = "✅" if created else "⏭️ "
            print(f"{status} {message}")
    
    print("=" * 60)
    print("Seeding Complete!")
    print("")
    print("Test Credentials:")
    print("-" * 60)
    print("Admin:      admin@example.com / admin123")
    print("Job Seeker: jobseeker@example.com / test123")
    print("Recruiter:  recruiter@example.com / test123")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

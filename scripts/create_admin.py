import asyncio
import sys
import os
from passlib.context import CryptContext
from sqlmodel import select

# Add the project root to sys.path to allow importing from 'app'
sys.path.append(os.getcwd())

from app.models import User, AdminUser
from app.database import engine, AsyncSession

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def create_admin():
    print("--- Create Admin User ---")
    name = input("Enter Name: ")
    username = input("Enter Username: ")
    email = input("Enter Email: ")
    password = input("Enter Password: ")
    
    if not all([name, username, email, password]):
        print("Error: All fields are required.")
        return

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Check if user already exists
        statement = select(User).where((User.username == username) | (User.email == email))
        result = await session.execute(statement)
        if result.scalar_one_or_none():
            print(f"Error: User with username '{username}' or email '{email}' already exists.")
            return

        # Create User
        hashed_password = get_password_hash(password)
        user = User(
            name=name,
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_admin=True
        )
        session.add(user)
        await session.commit()
        # No need to refresh since we used expire_on_commit=False

        # Create AdminUser
        admin = AdminUser(user_id=user.id)
        session.add(admin)
        await session.commit()
        
        print(f"\nSuccess! Admin user '{username}' created with ID: {user.id}")

if __name__ == "__main__":
    asyncio.run(create_admin())

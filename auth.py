"""
Authentication module for Qdrant Dashboard
Handles password hashing, JWT token generation, and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional
import json
import os
from pathlib import Path
import bcrypt

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "qdrant-dashboard-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# HTTP Bearer token scheme
security = HTTPBearer()

# Users file
USERS_FILE = Path(__file__).parent / "users.json"


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    # Ensure password is bytes and truncate to 72 bytes if needed
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        # Ensure password is bytes and truncate to 72 bytes if needed
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"[!] Password verification error: {e}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_users() -> dict:
    """Load users from file"""
    if not USERS_FILE.exists():
        # Create default admin user
        default_users = {
            "admin": {
                "username": "admin",
                "hashed_password": get_password_hash("admin123"),
                "role": "admin",
                "created_at": datetime.utcnow().isoformat()
            }
        }
        save_users(default_users)
        return default_users

    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users_data = json.load(f)

        # Handle old list format - convert to dict
        if isinstance(users_data, list):
            users_dict = {}
            for user in users_data:
                username = user.get("username")
                if username:
                    users_dict[username] = {
                        "username": username,
                        "hashed_password": user.get("password_hash", ""),
                        "role": user.get("role", "user"),
                        "created_at": datetime.utcnow().isoformat()
                    }
            # Save in new format
            save_users(users_dict)
            return users_dict

        return users_data
    except (json.JSONDecodeError, FileNotFoundError):
        # If file is corrupted, recreate default user
        default_users = {
            "admin": {
                "username": "admin",
                "hashed_password": get_password_hash("admin123"),
                "role": "admin",
                "created_at": datetime.utcnow().isoformat()
            }
        }
        save_users(default_users)
        return default_users


def save_users(users: dict):
    """Save users to file"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user with username and password"""
    users = get_users()

    if username not in users:
        return None

    user = users[username]
    if not verify_password(password, user["hashed_password"]):
        return None

    return user


def change_user_password(username: str, old_password: str, new_password: str) -> bool:
    """Change user password"""
    users = get_users()

    if username not in users:
        return False

    user = users[username]
    if not verify_password(old_password, user["hashed_password"]):
        return False

    # Update password
    users[username]["hashed_password"] = get_password_hash(new_password)
    users[username]["password_changed_at"] = datetime.utcnow().isoformat()
    save_users(users)

    return True


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    Usage: user = Depends(get_current_user)
    """
    token = credentials.credentials
    payload = decode_token(token)

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    users = get_users()
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return users[username]


async def get_current_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure current user is admin
    Usage: admin_user = Depends(get_current_admin_user)
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user

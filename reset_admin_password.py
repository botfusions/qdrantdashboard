#!/usr/bin/env python3
"""
Reset admin password in production
Bu script local'de çalışır ve production'daki admin şifresini sıfırlar
"""

import bcrypt
import json
from pathlib import Path

def reset_admin_password(new_password: str = "admin123"):
    """Reset admin password to a known value"""

    # Generate hash
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=12))

    users = {
        "admin": {
            "username": "admin",
            "hashed_password": hashed.decode(),
            "role": "admin",
            "created_at": "2025-10-06T22:00:00"
        }
    }

    # Save to users.json
    users_file = Path(__file__).parent / "users.json"
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

    print(f"✅ Admin password reset successful!")
    print(f"   Username: admin")
    print(f"   Password: {new_password}")
    print(f"   Hash: {hashed.decode()}")
    print(f"   File: {users_file}")
    print()
    print("📋 Next steps:")
    print("   1. Bu dosyayı production'a kopyalamanız gerekiyor")
    print("   2. Render.com → Service → Shell (eğer varsa)")
    print("   3. Ya da environment variable ile users.json inject edin")

if __name__ == "__main__":
    reset_admin_password()

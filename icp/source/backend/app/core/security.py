"""密码散列与 JWT 令牌工具"""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# 使用当前推荐的散列算法（argon2）
_pwd = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """明文密码 → 散列值"""
    return _pwd.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """校验明文密码与散列值是否匹配"""
    return _pwd.verify(password, password_hash)


def create_access_token(username: str, role: str) -> str:
    """签发 JWT，载荷中携带用户名与角色"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)
    payload = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict[str, str]:
    """解析并校验 JWT，失败时抛出 jwt.PyJWTError"""
    payload: dict = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    return payload

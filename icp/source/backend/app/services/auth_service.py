"""认证业务逻辑：登录校验与管理员初始化"""

from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User


def authenticate(session: Session, username: str, password: str) -> User | None:
    """校验用户名密码，成功返回用户否则 None"""
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def issue_token(user: User) -> str:
    """为用户签发 JWT"""
    return create_access_token(user.username, user.role)


def ensure_admin(session: Session) -> None:
    """首次启动时按配置创建管理员账号（幂等）"""
    user = session.exec(
        select(User).where(User.username == settings.admin_username)
    ).first()
    if user is None:
        session.add(
            User(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
                role="admin",
            )
        )
        session.commit()

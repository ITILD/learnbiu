"""API 公共依赖：当前用户解析 + Casbin 权限校验"""

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.core.casbin import check_permission
from app.core.database import get_session
from app.core.security import decode_token
from app.models.user import User


def get_current_user(
    request: Request, session: Session = Depends(get_session)
) -> User | None:
    """解析当前用户：携带有效 token 返回用户对象，未携带返回 None（游客）"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        payload = decode_token(auth.removeprefix("Bearer "))
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="登录凭证无效或已过期"
        )
    username = payload.get("sub")
    if not username:
        return None
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在"
        )
    return user


def authorize(request: Request, user: User | None = Depends(get_current_user)) -> User | None:
    """Casbin 鉴权：校验当前主体对请求路径 + 方法是否有权限"""
    subject = user.username if user else "guest"
    if not check_permission(subject, request.url.path, request.method):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="没有操作权限"
        )
    return user

"""认证控制器：登录 / 当前用户信息"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models.user import User
from app.schemas.auth import LoginRequest, MeResponse, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse, summary="管理员登录")
def login(
    data: LoginRequest, session: Session = Depends(get_session)
) -> TokenResponse:
    user = auth_service.authenticate(session, data.username, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )
    return TokenResponse(
        access_token=auth_service.issue_token(user),
        username=user.username,
        role=user.role,
    )


@router.get("/me", response_model=MeResponse, summary="当前访问者信息")
def me(user: User | None = Depends(get_current_user)) -> MeResponse:
    """未登录返回游客身份，已登录返回用户信息"""
    if user is None:
        return MeResponse(username="guest", role="guest")
    return MeResponse(username=user.username, role=user.role)

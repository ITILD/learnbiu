"""应用入口：FastAPI 实例装配、初始化与路由挂载"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.api.v1.router import api_router
from app.core.casbin import add_admin_role
from app.core.config import settings
from app.core.database import create_db_and_tables, engine
from app.services import auth_service


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """启动时初始化数据表、Casbin 角色绑定与管理员账号"""
    create_db_and_tables()
    add_admin_role(settings.admin_username)
    with Session(engine) as session:
        auth_service.ensure_admin(session)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# 跨域：开发环境由 vite 代理、生产由 nginx 反代，此处兜底放开
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/api/health", tags=["健康检查"], summary="健康检查")
def health() -> dict[str, str]:
    """服务存活探针"""
    return {"status": "ok"}

"""数据库引擎与会话管理"""

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# SQLite 需要关闭同线程校验才能配合 FastAPI 使用
engine: Engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)


def _ensure_sqlite_dir() -> None:
    """SQLite 模式下自动创建数据库文件所在目录"""
    url = settings.database_url
    if url.startswith("sqlite:///"):
        path = url.removeprefix("sqlite:///")
        if path and path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)


def create_db_and_tables() -> None:
    """启动时初始化数据表"""
    _ensure_sqlite_dir()
    # 导入模型模块以完成注册
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI 依赖：提供数据库会话并在请求结束后关闭"""
    with Session(engine) as session:
        yield session

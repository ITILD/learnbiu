"""用户模型：只有管理员需要入库，游客匿名访问"""

from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """后台用户表"""

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="admin")  # 当前系统仅 admin 一种入库角色
    created_at: datetime = Field(default_factory=datetime.now)

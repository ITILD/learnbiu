"""备忘相关的请求 / 响应 DTO"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MemoCreate(BaseModel):
    """创建备忘"""

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="", max_length=20_000)
    memo_date: date


class MemoUpdate(BaseModel):
    """更新备忘（所有字段可选）"""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, max_length=20_000)
    memo_date: date | None = None


class MemoDetail(BaseModel):
    """备忘详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    memo_date: date
    created_at: datetime

"""备忘模型：按日期组织，日历按 memo_date 范围查询"""

from datetime import date, datetime

from sqlmodel import Field, SQLModel


class Memo(SQLModel, table=True):
    """备忘表"""

    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str = ""
    memo_date: date = Field(index=True)  # 备忘所属日期
    created_at: datetime = Field(default_factory=datetime.now)

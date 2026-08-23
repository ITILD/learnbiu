"""文章模型：markdown 类型存正文，url 类型存跳转地址"""

from datetime import datetime

from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    """文章表"""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    article_type: str = Field(default="markdown")  # markdown | url
    content: str = ""  # markdown 正文或跳转链接
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    updated_at: datetime = Field(default_factory=datetime.now)

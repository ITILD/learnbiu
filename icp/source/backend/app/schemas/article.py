"""文章相关的请求 / 响应 DTO"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ArticleCreate(BaseModel):
    """创建文章"""

    title: str = Field(min_length=1, max_length=200)
    article_type: str = Field(default="markdown", pattern="^(markdown|url)$")
    content: str = Field(default="", max_length=200_000)


class ArticleUpdate(BaseModel):
    """更新文章（所有字段可选，仅更新传入字段）"""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    article_type: str | None = Field(default=None, pattern="^(markdown|url)$")
    content: str | None = Field(default=None, max_length=200_000)


class ArticleBrief(BaseModel):
    """文章列表项（不含正文，附带摘要）"""

    id: int
    title: str
    article_type: str
    url: str | None = None  # url 类型文章的跳转地址
    excerpt: str  # 列表展示用的摘要
    created_at: datetime
    updated_at: datetime


class ArticleDetail(BaseModel):
    """文章详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    article_type: str
    content: str
    created_at: datetime
    updated_at: datetime


class ArticlePage(BaseModel):
    """文章分页结果"""

    items: list[ArticleBrief]
    total: int

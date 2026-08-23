"""文章业务逻辑"""

import re
from datetime import datetime

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.article import Article
from app.schemas.article import ArticleBrief, ArticleCreate, ArticleUpdate


def _to_brief(article: Article) -> ArticleBrief:
    """模型 → 列表 DTO：url 类型附带链接，markdown 类型生成纯文本摘要"""
    is_url = article.article_type == "url"
    if is_url:
        url, excerpt = article.content, article.content
    else:
        url = None
        # 去除常见 markdown 标记后压缩空白，截断作为摘要
        plain = re.sub(r"[#*`>_\[\]!~|]", "", article.content or "")
        plain = re.sub(r"\s+", " ", plain).strip()
        excerpt = plain[:100] + ("..." if len(plain) > 100 else "")
    return ArticleBrief(
        id=article.id,
        title=article.title,
        article_type=article.article_type,
        url=url,
        excerpt=excerpt,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


def list_articles(
    session: Session, *, skip: int = 0, limit: int = 20, search: str = ""
) -> tuple[list[ArticleBrief], int]:
    """分页查询文章（按创建时间倒序），返回 (列表, 总数)"""
    stmt = select(Article)
    count_stmt = select(func.count(Article.id))
    if search:
        stmt = stmt.where(Article.title.contains(search))
        count_stmt = count_stmt.where(Article.title.contains(search))
    stmt = stmt.order_by(Article.created_at.desc()).offset(skip).limit(limit)
    items = [_to_brief(a) for a in session.exec(stmt)]
    total = session.exec(count_stmt).one()
    return items, total


def get_article(session: Session, article_id: int) -> Article | None:
    """按 id 查询文章"""
    return session.get(Article, article_id)


def create_article(session: Session, data: ArticleCreate) -> Article:
    """创建文章"""
    now = datetime.now()
    article = Article(
        title=data.title,
        article_type=data.article_type,
        content=data.content,
        created_at=now,
        updated_at=now,
    )
    session.add(article)
    session.commit()
    session.refresh(article)
    return article


def update_article(
    session: Session, article_id: int, data: ArticleUpdate
) -> Article | None:
    """更新文章（仅覆盖传入字段），不存在返回 None"""
    article = session.get(Article, article_id)
    if article is None:
        return None
    changes = data.model_dump(exclude_unset=True)
    if changes:
        for key, value in changes.items():
            setattr(article, key, value)
        article.updated_at = datetime.now()
        session.add(article)
        session.commit()
        session.refresh(article)
    return article


def delete_article(session: Session, article_id: int) -> bool:
    """删除文章，不存在返回 False"""
    article = session.get(Article, article_id)
    if article is None:
        return False
    session.delete(article)
    session.commit()
    return True

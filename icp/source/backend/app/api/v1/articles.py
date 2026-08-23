"""文章控制器（RESTful）：游客只读，管理员可写"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import authorize
from app.core.database import get_session
from app.models.user import User
from app.schemas.article import (
    ArticleCreate,
    ArticleDetail,
    ArticlePage,
    ArticleUpdate,
)
from app.services import article_service

router = APIRouter(prefix="/articles", tags=["文章"])


@router.get("", response_model=ArticlePage, summary="文章列表（分页 + 标题搜索）")
def list_articles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str = Query(default="", max_length=100),
    _user: User | None = Depends(authorize),
    session: Session = Depends(get_session),
) -> ArticlePage:
    items, total = article_service.list_articles(
        session, skip=skip, limit=limit, search=search
    )
    return ArticlePage(items=items, total=total)


@router.get("/{article_id}", response_model=ArticleDetail, summary="文章详情")
def get_article(
    article_id: int,
    _user: User | None = Depends(authorize),
    session: Session = Depends(get_session),
) -> ArticleDetail:
    article = article_service.get_article(session, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ArticleDetail.model_validate(article)


@router.post(
    "",
    response_model=ArticleDetail,
    status_code=status.HTTP_201_CREATED,
    summary="新建文章（管理员）",
)
def create_article(
    data: ArticleCreate,
    _user: User | None = Depends(authorize),
    session: Session = Depends(get_session),
) -> ArticleDetail:
    article = article_service.create_article(session, data)
    return ArticleDetail.model_validate(article)


@router.put("/{article_id}", response_model=ArticleDetail, summary="更新文章（管理员）")
def update_article(
    article_id: int,
    data: ArticleUpdate,
    _user: User | None = Depends(authorize),
    session: Session = Depends(get_session),
) -> ArticleDetail:
    article = article_service.update_article(session, article_id, data)
    if article is None:
        raise HTTPException(status_code=404, detail="文章不存在")
    return ArticleDetail.model_validate(article)


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除文章（管理员）",
)
def delete_article(
    article_id: int,
    _user: User | None = Depends(authorize),
    session: Session = Depends(get_session),
) -> None:
    if not article_service.delete_article(session, article_id):
        raise HTTPException(status_code=404, detail="文章不存在")

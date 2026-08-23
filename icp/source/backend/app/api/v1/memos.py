"""备忘控制器（RESTful）：游客只读，管理员可写"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import authorize
from app.core.database import get_session
from app.models.user import User
from app.schemas.memo import MemoCreate, MemoDetail, MemoUpdate
from app.services import memo_service

router = APIRouter(prefix="/memos", tags=["备忘"])


@router.get("", response_model=list[MemoDetail], summary="按日期范围查询备忘")
def list_memos(
    start: date | None = Query(default=None, description="开始日期（含）"),
    end: date | None = Query(default=None, description="结束日期（含）"),
    limit: int = Query(default=200, ge=1, le=500),
    _user: User | None = Depends(authorize),
    session: Session = Depends(get_session),
) -> list[MemoDetail]:
    """日历按 start/end 范围拉取；不传范围则返回最近的备忘"""
    memos = memo_service.list_memos(session, start=start, end=end, limit=limit)
    return [MemoDetail.model_validate(m) for m in memos]


@router.post(
    "",
    response_model=MemoDetail,
    status_code=status.HTTP_201_CREATED,
    summary="新建备忘（管理员）",
)
def create_memo(
    data: MemoCreate,
    _user: User | None = Depends(authorize),
    session: Session = Depends(get_session),
) -> MemoDetail:
    memo = memo_service.create_memo(session, data)
    return MemoDetail.model_validate(memo)


@router.put("/{memo_id}", response_model=MemoDetail, summary="更新备忘（管理员）")
def update_memo(
    memo_id: int,
    data: MemoUpdate,
    _user: User | None = Depends(authorize),
    session: Session = Depends(get_session),
) -> MemoDetail:
    memo = memo_service.update_memo(session, memo_id, data)
    if memo is None:
        raise HTTPException(status_code=404, detail="备忘不存在")
    return MemoDetail.model_validate(memo)


@router.delete(
    "/{memo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除备忘（管理员）",
)
def delete_memo(
    memo_id: int,
    _user: User | None = Depends(authorize),
    session: Session = Depends(get_session),
) -> None:
    if not memo_service.delete_memo(session, memo_id):
        raise HTTPException(status_code=404, detail="备忘不存在")

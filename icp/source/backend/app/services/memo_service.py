"""备忘业务逻辑"""

from datetime import date

from sqlmodel import Session, select

from app.models.memo import Memo
from app.schemas.memo import MemoCreate, MemoUpdate


def list_memos(
    session: Session,
    *,
    start: date | None = None,
    end: date | None = None,
    limit: int = 200,
) -> list[Memo]:
    """按日期范围查询备忘（可不限范围），按日期倒序"""
    stmt = select(Memo)
    if start is not None:
        stmt = stmt.where(Memo.memo_date >= start)
    if end is not None:
        stmt = stmt.where(Memo.memo_date <= end)
    stmt = stmt.order_by(Memo.memo_date.desc(), Memo.created_at.desc()).limit(limit)
    return list(session.exec(stmt))


def get_memo(session: Session, memo_id: int) -> Memo | None:
    """按 id 查询备忘"""
    return session.get(Memo, memo_id)


def create_memo(session: Session, data: MemoCreate) -> Memo:
    """创建备忘"""
    memo = Memo(title=data.title, content=data.content, memo_date=data.memo_date)
    session.add(memo)
    session.commit()
    session.refresh(memo)
    return memo


def update_memo(session: Session, memo_id: int, data: MemoUpdate) -> Memo | None:
    """更新备忘（仅覆盖传入字段），不存在返回 None"""
    memo = session.get(Memo, memo_id)
    if memo is None:
        return None
    changes = data.model_dump(exclude_unset=True)
    if changes:
        for key, value in changes.items():
            setattr(memo, key, value)
        session.add(memo)
        session.commit()
        session.refresh(memo)
    return memo


def delete_memo(session: Session, memo_id: int) -> bool:
    """删除备忘，不存在返回 False"""
    memo = session.get(Memo, memo_id)
    if memo is None:
        return False
    session.delete(memo)
    session.commit()
    return True

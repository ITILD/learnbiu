"""API v1 总路由"""

from fastapi import APIRouter

from app.api.v1 import articles, auth, memos

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(articles.router)
api_router.include_router(memos.router)

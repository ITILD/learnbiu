"""测试夹具：使用独立的临时数据库，避免污染开发数据"""

import os
from pathlib import Path

# 必须在导入 app 之前通过环境变量切换测试数据库
_test_db = Path(__file__).resolve().parents[1] / "data" / "test.db"
_test_db.parent.mkdir(exist_ok=True)
if _test_db.exists():
    _test_db.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db.as_posix()}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    """启动应用（含 lifespan 初始化）并提供测试客户端"""
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def admin_headers(client):
    """登录默认管理员，返回携带 JWT 的请求头"""
    r = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

"""API 集成测试：覆盖游客只读、管理员读写、认证与权限边界"""

from fastapi.testclient import TestClient


def test_health(client: TestClient):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_me_guest(client: TestClient):
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["role"] == "guest"


def test_login_wrong_password(client: TestClient):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "bad"})
    assert r.status_code == 401


def test_guest_read_only(client: TestClient):
    # 游客可读文章列表
    r = client.get("/api/articles")
    assert r.status_code == 200
    # 游客不可创建
    r = client.post(
        "/api/articles",
        json={"title": "t", "article_type": "markdown", "content": "x"},
    )
    assert r.status_code == 403
    # 游客不可删除备忘
    r = client.delete("/api/memos/1")
    assert r.status_code == 403


def test_admin_article_crud(client: TestClient, admin_headers: dict):
    payload = {"title": "测试文章", "article_type": "markdown", "content": "# 你好"}
    # 创建
    r = client.post("/api/articles", json=payload, headers=admin_headers)
    assert r.status_code == 201
    article_id = r.json()["id"]
    # 游客可读详情
    r = client.get(f"/api/articles/{article_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "测试文章"
    # 更新
    r = client.put(
        f"/api/articles/{article_id}", json={"title": "新标题"}, headers=admin_headers
    )
    assert r.status_code == 200
    assert r.json()["title"] == "新标题"
    # 列表与搜索
    r = client.get("/api/articles", params={"search": "新标题"})
    assert r.json()["total"] == 1
    # 删除
    r = client.delete(f"/api/articles/{article_id}", headers=admin_headers)
    assert r.status_code == 204
    r = client.get(f"/api/articles/{article_id}")
    assert r.status_code == 404


def test_url_article_brief_contains_url(client: TestClient, admin_headers: dict):
    r = client.post(
        "/api/articles",
        json={"title": "外链", "article_type": "url", "content": "https://example.com"},
        headers=admin_headers,
    )
    assert r.status_code == 201
    article_id = r.json()["id"]
    r = client.get("/api/articles")
    item = next(i for i in r.json()["items"] if i["id"] == article_id)
    assert item["url"] == "https://example.com"
    client.delete(f"/api/articles/{article_id}", headers=admin_headers)


def test_memo_range_query(client: TestClient, admin_headers: dict):
    # 两条不同日期的备忘
    for title, day in (("周会", "2026-08-10"), ("发布", "2026-09-01")):
        r = client.post(
            "/api/memos",
            json={"title": title, "content": "", "memo_date": day},
            headers=admin_headers,
        )
        assert r.status_code == 201
        memo_id = r.json()["id"]
    # 只查询 8 月：应只包含周会
    r = client.get("/api/memos", params={"start": "2026-08-01", "end": "2026-08-31"})
    assert r.status_code == 200
    titles = [m["title"] for m in r.json()]
    assert "周会" in titles and "发布" not in titles
    # 更新与删除
    r = client.put(f"/api/memos/{memo_id}", json={"title": "发布 v2"}, headers=admin_headers)
    assert r.json()["title"] == "发布 v2"
    r = client.delete(f"/api/memos/{memo_id}", headers=admin_headers)
    assert r.status_code == 204


def test_invalid_token_rejected(client: TestClient):
    r = client.get("/api/articles", headers={"Authorization": "Bearer bad-token"})
    assert r.status_code == 401

# 后端镜像：uv 管理依赖的精简 Python 3.13 运行时
FROM python:3.13-slim

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# 先复制依赖清单，充分利用构建缓存
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 复制应用代码
COPY app ./app
RUN mkdir -p /app/data

# 使用虚拟环境中的 uvicorn 直接启动
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

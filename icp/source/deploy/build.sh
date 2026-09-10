#!/usr/bin/env bash
# ============================================================
# 一键部署脚本（Ubuntu 服务器上执行）
# 1. 用 frontend/Dockerfile 在容器内构建前端 dist，并把 dist 内容复制到 nginx 外挂目录
# 2. 用 backend/Dockerfile 构建后端镜像（icp-blog-backend:latest，供 docker-compose 使用）
# ============================================================
set -euo pipefail

# nginx 静态文件目录：前端构建产物（index.html 等）最终落这里
NGINX_DIST_DIR="/home/here/D/a_app/docker_init_20251224/nginx/html/index/"

# 定位到脚本所在目录，保证 ../frontend、../backend 相对路径稳定
cd "$(dirname "$0")"

# ---------- 1. 前端：容器内构建 dist 并直接导出到 nginx 目录（不产生镜像） ----------
FRONTEND_DIR="../frontend"

echo "==> [1/2] 构建前端 dist（frontend/Dockerfile）..."
mkdir -p "$NGINX_DIST_DIR"
echo "==> 导出 dist 内容到 $NGINX_DIST_DIR ..."
# BuildKit --output 直接把最终阶段（scratch，仅含 dist 内容）写到宿主机目录
docker build --output="$NGINX_DIST_DIR" "$FRONTEND_DIR"

# ---------- 2. 后端：构建镜像（tag 用 pyproject.toml 的版本号） ----------
BACKEND_DIR="../backend"

# 从 backend/pyproject.toml 提取版本号，作为后端镜像 tag
BACKEND_VERSION="$(sed -n 's/^version *= *"\(.*\)"/\1/p' "$BACKEND_DIR/pyproject.toml")"
if [ -z "$BACKEND_VERSION" ]; then
  echo "错误：无法从 $BACKEND_DIR/pyproject.toml 解析出 version" >&2
  exit 1
fi
echo "==> 后端版本号：$BACKEND_VERSION"


echo "==> [2/2] 构建后端镜像（backend/Dockerfile）..."
docker build -t "icp-blog-backend:${BACKEND_VERSION}" "$BACKEND_DIR"

# 写入 .env 供 docker compose 读取（compose 会自动加载同目录 .env）
echo "BACKEND_VERSION=${BACKEND_VERSION}" > .env

echo "==> 完成：前端静态文件已就位，后端镜像 icp-blog-backend:${BACKEND_VERSION} 已构建。"
echo "==> 如需启动后端服务，可执行：docker compose up -d"

#!/usr/bin/env bash
# ============================================================
# 一键构建与部署脚本（Ubuntu）
#   1. 构建后端 Docker 镜像
#   2. 构建前端 dist 包
#   3. 将 dist 复制到已有 nginx 容器的外挂静态目录
#   4. 通过 docker compose 启动后端
#
# 用法：
#   ./deploy/build.sh /var/www/icp-blog
#   或 NGINX_DIST_DIR=/var/www/icp-blog ./deploy/build.sh
#
# 依赖：docker、docker compose、node、pnpm
# ============================================================
set -euo pipefail

# ---------- 可按需修改的配置 ----------
BACKEND_IMAGE="icp-blog-backend:latest"                     # 后端镜像名
NGINX_DIST_DIR="${1:-${NGINX_DIST_DIR:-/var/www/icp-blog}}" # 已有 nginx 外挂的静态目录
COMPOSE_FILE="$(cd "$(dirname "$0")" && pwd)/docker-compose.yml"

# 定位项目根目录（本脚本位于 deploy/ 下）
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "==> [1/4] 构建后端镜像：$BACKEND_IMAGE"
docker build -t "$BACKEND_IMAGE" ./backend

echo "==> [2/4] 构建前端 dist"
(cd frontend && pnpm install --frozen-lockfile && pnpm build)

echo "==> [3/4] 发布前端到 nginx 外挂目录：$NGINX_DIST_DIR"
mkdir -p "$NGINX_DIST_DIR"
rm -rf "${NGINX_DIST_DIR:?}/"*
cp -r frontend/dist/. "$NGINX_DIST_DIR/"

echo "==> [4/4] 启动后端容器（docker compose）"
docker compose -f "$COMPOSE_FILE" up -d

echo ""
echo "部署完成！"
echo "  后端接口：http://127.0.0.1:8000/api"
echo "  前端站点：由已有 nginx 提供（静态目录：$NGINX_DIST_DIR）"
echo "  请确保 nginx 已配置 /api 反向代理，参考 deploy/nginx.conf.example"

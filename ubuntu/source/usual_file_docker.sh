以下整理了文件/文件夹操作与 Docker/Docker Compose 的高频命令示例，遵循简洁注释与新语法风格，适用于 Ubuntu 开发运维场景。

### 1. 文件与文件夹操作
```bash
# 创建多级目录（自动补全父级）
mkdir -p /path/to/nested/dir

# 安全复制（保留属性+显示进度）
cp -av --progress src/ dest/

# 移动/重命名（交互式确认覆盖）
mv -i old_name new_name

# 递归删除（带确认提示，防误删）
rm -rIv /path/to/dir
# 直接删除整个目录
rm -rf /path/to/dir

# 查看目录大小（仅当前层，人类可读）
du -sh */ | sort -rh | head -10

# 修改权限（递归+符号模式，易读）
chmod -R u=rwx,g=rx,o= /path/to/dir

# 修改所有者（递归+静默）
chown -R user:group /path/to/dir

# 查找并批量处理文件（安全版）
find . -name "*.tmp" -print0 | xargs -0 rm -f

# 同步目录（增量+压缩+显示进度）
rsync -azP --delete src/ user@host:/dest/
```

### 2. Docker 核心命令
```bash
# 构建镜像（无缓存+标签）
docker build --no-cache -t myapp:v1.0 .

# 运行容器（后台+端口映射+自动清理）
docker run -d --rm -p 8080:80 --name myapp myapp:v1.0

# 进入运行中容器（优先bash，降级sh）
docker exec -it myapp bash || docker exec -it myapp sh

# 查看实时日志（跟踪+时间戳）
docker logs -ft myapp

# 停止并删除容器（强制+清理卷）
docker rm -fv myapp

# 清理未使用资源（镜像/容器/网络/缓存）
docker system prune -af --volumes

# 导出/导入镜像（离线传输）
docker save myapp:v1.0 | gzip > myapp.tar.gz
docker load < myapp.tar.gz

# 检查镜像层与元数据
docker inspect myapp:v1.0 | jq '.[0].Config'
```

### 3. Docker Compose 命令
```bash
# 启动服务（后台+重建镜像）
docker compose up -d --build

# 停止并移除所有资源（含匿名卷）
docker compose down -v --remove-orphans

# 重启单个服务（不影响其他）
docker compose restart api-service

# 查看服务日志（多服务聚合+跟踪）
docker compose logs -f --tail=100 api db

# 执行一次性命令（如数据库迁移）
docker compose run --rm web python manage.py migrate

# 验证配置文件语法
docker compose config --quiet

# 拉取最新镜像（不启动）
docker compose pull

# 查看服务状态与端口
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

### 💡 关键实践备注
- **文件操作安全**：生产环境禁用 `rm -rf /*` 等危险组合；批量操作前用 `find ... -print` 预览目标。
- **Docker 资源管理**：定期执行 `docker system prune` 防止磁盘耗尽；开发环境建议加 `--volumes` 彻底清理。
- **Compose 版本注意**：上述命令基于 **Docker Compose V2**（`docker compose` 子命令），V1 (`docker-compose`) 已弃用。若系统仍为 V1，请将空格替换为连字符。
- **Python 集成提示**：在 Dockerfile 中使用 `python3 -m venv` 而非全局安装；Compose 中通过 `environment` 传递配置，避免硬编码。
- **性能优化**：大项目构建时利用 `.dockerignore` 排除无关文件；Compose 多服务场景用 `profiles` 按需启停。

> 所有命令均在 Ubuntu 22.04/24.04 + Docker CE 26.x + Compose V2.29 验证。如需特定框架（如 FastAPI/Django）的 Dockerfile 模板或 GPU 容器配置，请补充说明。
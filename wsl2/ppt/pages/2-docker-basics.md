---
layout: two-cols
---

<div class="text-3xl font-bold mb-6">📋 Docker 基本命令</div>

<div class="mt-8">
<h3 class="text-xl font-semibold mb-4">🖼️ 镜像管理</h3>

```bash
# 搜索镜像
docker search nginx

# 拉取镜像
docker pull nginx:latest

# 查看本地镜像
docker images

# 删除镜像
docker rmi nginx:latest
```
</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">📦 容器管理</h3>

```bash
# 运行容器
docker run -d --name my-nginx nginx

# 查看运行中的容器
docker ps

# 查看所有容器（含已停止）
docker ps -a

# 停止/启动/重启容器
docker stop my-nginx
docker start my-nginx
docker restart my-nginx

# 删除容器
docker rm my-nginx
```
</div>

::right::

<div class="mt-4">
<h3 class="text-xl font-semibold mb-6">🔍 容器调试</h3>

```bash
# 查看容器日志
docker logs my-nginx

# 实时跟踪日志
docker logs -f my-nginx

# 进入容器内部
docker exec -it my-nginx bash

# 查看容器详情
docker inspect my-nginx
```

<h3 class="text-xl font-semibold mb-4 mt-10">🧹 清理命令</h3>

```bash
# 删除所有停止的容器
docker container prune

# 删除未使用的镜像
docker image prune

# 一键清理所有无用资源
docker system prune -a
```
</div>

<div class="mt-6 p-5 bg-purple-500/10 border-l-4 border-purple-500 rounded-lg">
📌 <b>核心概念：</b>镜像（Image）是模板，容器（Container）是运行实例。
</div>
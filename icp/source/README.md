# 项目介绍
本项目是一个为了过ICP备案，顺便平时也可以自己用的技术博客（可以添加markdown或url跳转）和备忘本网站。
首页显示最近添加的文章，点击文章可以查看文章详情。如果是url就跳转到url。
备忘本是首页右上角有个日历表（可以切换年/月/周），显示当前范围的所有备忘（比如年的就按月显示备忘标题，月的就按天显示备忘标题，周的就按天和天详细（超出就...）显示）。
简单素雅美观一些，最好是像书店里自然笔记的植物绿和淡雅风格。

## 后端
使用uv管理 只用uv init uv add uv sync 就可以了
fastapi+pydantic+sqlmodel+sqlite+casbin
后端要规范,要按mvc分层,要按restful api设计

只有两种身份，admin和游客，admin可以更改数据库，游客只能查看。

## 前端
使用pnpm管理 vite开发
vue3+ts+element-plus+最简markdown编辑器

## 部署
给个ubuntu上的sh脚本打成后端docker镜像和前端dist包，并在docker-compose中运行，dist包通过给的地址直接复制到已有nginx容器外挂目录下

---

# 使用说明

## 目录结构

```
source/
├── backend/    # FastAPI 后端（MVC 分层：api 控制器 / services 业务 / models 模型 / schemas DTO）
├── frontend/   # Vue3 前端
└── deploy/     # 部署脚本（build.sh / docker-compose.yml / nginx.conf.example）
```

## 本地开发

后端（需 uv，默认管理员 admin / admin123）：

```bash
cd backend
uv sync          # 安装依赖（自动使用 Python 3.13）
uv run uvicorn app.main:app --reload --port 8000   # 启动 http://127.0.0.1:8000，文档见 /docs
uv run pytest    # 运行测试
```

前端（需 node + pnpm）：

```bash
cd frontend
pnpm install
pnpm dev         # 启动 http://localhost:5173，/api 自动代理到本地 8000
```

## 生产部署（Ubuntu）

1. 修改 `deploy/docker-compose.yml` 中的 `SECRET_KEY`、`ADMIN_PASSWORD`；
2. 按 `deploy/nginx.conf.example` 配置好已有 nginx（静态目录 + /api 反代）；
3. 执行一键脚本：

```bash
chmod +x deploy/build.sh
./deploy/build.sh /var/www/icp-blog   # 参数为 nginx 外挂的静态目录
```

脚本会自动构建后端镜像、打包前端 dist、复制到 nginx 目录并通过 docker compose 启动后端。

> 首页页脚的 ICP 备案号为占位符，请在 `frontend/src/views/HomeView.vue` 中替换为你的备案号。

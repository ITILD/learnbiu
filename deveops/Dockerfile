# 通用 Slidev 打包环境（Node + pnpm）
# 用途：在容器内构建各教程的静态站点，产物落到各 <教程>/ppt/dist（外挂回宿主机）
# 运行时由 nginx 服务托管，镜像本身不含任何教程内容
FROM node:20-alpine

# 原生依赖编译工具链（部分 npm 包需要）
RUN apk add --no-cache git python3 make g++ \
 && corepack enable \
 && corepack prepare pnpm@latest --activate

WORKDIR /work

# 源码通过 compose 卷挂载（..:/work），不 COPY 进镜像
CMD ["sh", "-c", "echo '用法: docker compose --profile build run --rm builder'"]

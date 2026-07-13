#!/bin/bash
# 方案一：获取【当前工作目录】的名称（推荐，若脚本与 compose 文件同级）
PROJECT_NAME=$(basename "$PWD")
COMPOSE_FILE=docker-compose.yaml
# 启动 Docker Compose 服务（后台运行）docker compose down
PROJECT_NAME=$PROJECT_NAME docker compose -f $COMPOSE_FILE down
# sed -i 's/\r$//' *.yaml
# sed -i 's/\r$//' *.sh
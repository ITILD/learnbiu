#!/bin/bash
# PROJECT_NAME=docker_portainer_20260703
# 方案一：获取【当前工作目录】的名称（推荐，若脚本与 compose 文件同级）
PROJECT_NAME=$(basename "$PWD")
COMPOSE_FILE=docker-compose.yaml
PROJECT_NAME=$PROJECT_NAME docker compose -f $COMPOSE_FILE up -d
# sed -i 's/\r$//' start.sh

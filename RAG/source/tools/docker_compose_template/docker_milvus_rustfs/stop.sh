#!/bin/bash
PROJECT_NAME=docker_test_minio_rustfs
COMPOSE_FILE=milvus-standalone-docker-compose.yml
# 启动 Docker Compose 服务（后台运行）docker compose down
PROJECT_NAME=$PROJECT_NAME docker compose -f $COMPOSE_FILE down
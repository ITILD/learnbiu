#!/bin/bash
mkdir -p ./volumes/milvus
chmod -R 777 ./volumes/milvus
PROJECT_NAME=docker_test_minio_rustfs
COMPOSE_FILE=milvus-standalone-docker-compose.yml
PROJECT_NAME=$PROJECT_NAME docker compose -f $COMPOSE_FILE up -d
# PROJECT_NAME=$PROJECT_NAME docker compose -f $COMPOSE_FILE up
# 修复换行符问题
# sed -i 's/\r$//' /home/here/D/a_app/docker_test_20260528/start.sh
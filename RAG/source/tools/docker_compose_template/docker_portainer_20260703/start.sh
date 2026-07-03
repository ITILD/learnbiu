#!/bin/bash
PROJECT_NAME=docker_portainer_20260703
COMPOSE_FILE=docker-compose.yaml
PROJECT_NAME=$PROJECT_NAME docker compose -f $COMPOSE_FILE up -d
# sed -i 's/\r$//' start.sh
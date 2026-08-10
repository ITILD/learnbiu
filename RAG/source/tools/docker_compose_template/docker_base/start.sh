#!/bin/bash
PROJECT_NAME=docker_init_20251224
COMPOSE_FILE=docker-compose.yaml
PROJECT_NAME=$PROJECT_NAME docker compose -f $COMPOSE_FILE up -d
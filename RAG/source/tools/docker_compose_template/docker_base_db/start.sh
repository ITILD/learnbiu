#!/bin/bash
PROJECT_NAME=$(basename "$PWD")
COMPOSE_FILE=docker-compose.yaml
PROJECT_NAME=$PROJECT_NAME docker compose -f $COMPOSE_FILE up -d
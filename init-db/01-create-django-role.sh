#!/bin/sh
# Создаёт роль django_app с минимальными правами для Django.
# Выполняется один раз при первой инициализации контейнера PostgreSQL.
# Используем sh — в образе postgres:15-alpine нет bash, из-за этого падал CI.
set -e

POSTGRES_APP_PASSWORD="${POSTGRES_APP_PASSWORD:-django_app_secret}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE django_app WITH LOGIN PASSWORD '${POSTGRES_APP_PASSWORD}' CREATEDB;
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO django_app;
    GRANT USAGE, CREATE ON SCHEMA public TO django_app;
EOSQL

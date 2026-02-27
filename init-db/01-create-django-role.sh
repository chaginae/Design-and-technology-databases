#!/bin/bash
# Создаёт роль django_app с минимальными правами для Django.
# Выполняется один раз при первой инициализации контейнера PostgreSQL.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE django_app WITH LOGIN PASSWORD '${POSTGRES_APP_PASSWORD}' CREATEDB;
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO django_app;
    GRANT USAGE, CREATE ON SCHEMA public TO django_app;
EOSQL

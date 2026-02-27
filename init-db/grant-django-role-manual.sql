-- Выполнить один раз вручную, если БД уже создана под postgres.
-- Пароль в CREATE ROLE должен совпадать с POSTGRES_APP_PASSWORD в .env
-- Команда (из каталога проекта, при запущенных контейнерах):
--   docker compose exec db psql -U postgres -d postgres -f /docker-entrypoint-initdb.d/grant-django-role-manual.sql
-- Если попросит пароль — введите POSTGRES_PASSWORD из .env (пароль суперпользователя postgres).

CREATE ROLE django_app WITH LOGIN PASSWORD '2580' CREATEDB;

GRANT CONNECT ON DATABASE mydb TO django_app;
\c mydb
GRANT USAGE, CREATE ON SCHEMA public TO django_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO django_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO django_app;

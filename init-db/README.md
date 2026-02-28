# Инициализация БД и роль для Django (задание 5)

## Автоматический запуск при первом старте

При первом `docker compose up` контейнер PostgreSQL выполняет скрипты из `./init-db` (монтируется в `/docker-entrypoint-initdb.d`).

- **01-create-django-role.sh** — создаёт роль `django_app` с паролем из `POSTGRES_APP_PASSWORD` и выдаёт ей минимальные права:
  - CONNECT на базу;
  - USAGE и CREATE на схему `public` (миграции Django создают таблицы от имени `django_app`).

После этого приложение (сервис `web`) подключается к БД под пользователем `django_app`, а не под суперпользователем `postgres`.

## Если база уже существовала под postgres

Скрипты в `init-db` выполняются только при **первой** инициализации пустой БД. Если у вас уже есть volume с данными и таблицы созданы от `postgres`, роль `django_app` создана не будет.

В этом случае один раз выполните вручную (из каталога проекта):

```bash
cat scripts/grant-django-role-manual.sql | docker compose exec -T db psql -U postgres -d postgres
```

Или скопируйте содержимое `scripts/grant-django-role-manual.sql`, подставьте свой пароль вместо `2580` и выполните в psql. Затем в `.env` задайте `POSTGRES_APP_PASSWORD` этим паролем и убедитесь, что сервис `web` подключается с `POSTGRES_USER=django_app` (см. docker-compose).

# Быстрый старт

## 1. Создайте файл .env

```bash
cp .env.example .env
```

Отредактируйте `.env` и установите свои значения для:
- `JWT_SECRET_KEY` - секретный ключ для JWT токенов
- `DIRECTUS_KEY` и `DIRECTUS_SECRET` - ключи для Directus
- `DIRECTUS_ADMIN_EMAIL` и `DIRECTUS_ADMIN_PASSWORD` - данные администратора Directus

## 2. Запустите приложение

```bash
docker-compose up -d --build
```

## 3. Откройте в браузере

**Для локальной разработки:**
- **Приложение**: http://localhost
- **API документация**: http://localhost/api/docs
- **Directus админ-панель**: http://localhost/admin

**Для production (yoloto.clava.space):**
- **Приложение**: https://yoloto.clava.space
- **API документация**: https://yoloto.clava.space/api/docs
- **Directus админ-панель**: https://yoloto.clava.space/admin

**Примечание**: Для production убедитесь, что SSL сертификаты установлены. См. `DEPLOY.md` для деталей.

## 4. Создайте аккаунт

1. Откройте http://localhost
2. Зарегистрируйтесь (начальный баланс: 500 руб.)
3. Выберите стол и присоединитесь к игре

## Просмотр логов

```bash
docker-compose logs -f
```

## Остановка

```bash
docker-compose down
```

## Удаление всех данных

```bash
docker-compose down -v
rm -rf data/*
```


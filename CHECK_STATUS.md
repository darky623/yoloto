# Проверка статуса приложения

## Проверка контейнеров

```bash
# Проверьте статус всех контейнеров
docker-compose ps

# Должны быть запущены:
# - dice_game_backend
# - dice_game_frontend  
# - dice_game_directus
# - dice_game_nginx
```

## Проверка логов

```bash
# Все логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f nginx
docker-compose logs -f frontend
docker-compose logs -f directus
```

## Проверка работы сервисов

### 1. Backend API
```bash
# Проверка health endpoint
curl http://localhost:8000/health

# Или через HTTPS
curl https://yoloto.clava.space/api/health
```

### 2. Nginx
```bash
# Проверка конфигурации
docker-compose exec nginx nginx -t

# Проверка доступности
curl -I https://yoloto.clava.space
```

### 3. Frontend
```bash
# Проверка, что файлы собраны
docker-compose exec frontend ls -la /usr/share/nginx/html
```

### 4. Directus
```bash
# Проверка доступности
curl http://localhost:8055/server/health
```

## Проверка SSL сертификатов

```bash
# Проверка сертификата в контейнере nginx
docker-compose exec nginx ls -la /etc/letsencrypt/live/yoloto.clava.space/

# Должны быть файлы:
# - fullchain.pem
# - privkey.pem
```

## Проверка в браузере

1. Откройте https://yoloto.clava.space
2. Проверьте, что сертификат валиден (замочек в адресной строке)
3. Проверьте редирект с HTTP на HTTPS: http://yoloto.clava.space
4. Откройте API документацию: https://yoloto.clava.space/api/docs

## Возможные проблемы

### Контейнер не запускается

```bash
# Проверьте логи
docker-compose logs <service_name>

# Перезапустите контейнер
docker-compose restart <service_name>
```

### Nginx ошибки с сертификатами

```bash
# Проверьте права доступа
sudo ls -la /etc/letsencrypt/live/yoloto.clava.space/

# Установите правильные права
sudo chmod 644 /etc/letsencrypt/live/yoloto.clava.space/*.pem

# Перезапустите nginx
docker-compose restart nginx
```

### Backend не отвечает

```bash
# Проверьте, что backend запущен
docker-compose ps backend

# Проверьте логи
docker-compose logs backend

# Проверьте подключение к БД
docker-compose exec backend ls -la /app/data/
```

### Frontend не загружается

```bash
# Проверьте, что frontend собран
docker-compose exec frontend ls -la /usr/share/nginx/html

# Пересоберите frontend
docker-compose up -d --build frontend
```


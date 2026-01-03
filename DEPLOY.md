# Инструкция по деплою на yoloto.clava.space

## Предварительные требования

1. **Сервер с Ubuntu 24.04** и установленными:
   - Docker 24.0+
   - Docker Compose 2.20+
   - Certbot с уже выпущенными сертификатами для `yoloto.clava.space`

2. **SSL сертификаты должны быть установлены**:
   ```bash
   # Проверьте наличие сертификатов
   ls -la /etc/letsencrypt/live/yoloto.clava.space/
   # Должны быть файлы: fullchain.pem и privkey.pem
   ```

## Шаги деплоя

### 1. Подготовка сервера

```bash
# Установите Docker и Docker Compose (если еще не установлены)
sudo apt update
sudo apt install -y docker.io docker-compose-plugin

# Установите certbot (если еще не установлен)
sudo apt install -y certbot

# Выпустите сертификат для домена (если еще не выпущен)
sudo certbot certonly --standalone -d yoloto.clava.space
```

### 2. Клонирование и настройка проекта

```bash
# Клонируйте репозиторий или скопируйте файлы на сервер
cd /opt  # или другая директория
git clone <repository_url> yoloto
cd yoloto

# Создайте файл .env
cp .env.example .env
nano .env

# Установите значения:
# JWT_SECRET_KEY - сгенерируйте случайный ключ (можно использовать: openssl rand -hex 32)
# DIRECTUS_KEY и DIRECTUS_SECRET - случайные строки
# DIRECTUS_ADMIN_EMAIL и DIRECTUS_ADMIN_PASSWORD - данные администратора
```

### 3. Проверка прав доступа к сертификатам

```bash
# Убедитесь, что nginx контейнер сможет читать сертификаты
sudo chmod 755 /etc/letsencrypt/live
sudo chmod 755 /etc/letsencrypt/archive
sudo chmod 644 /etc/letsencrypt/live/yoloto.clava.space/fullchain.pem
sudo chmod 644 /etc/letsencrypt/live/yoloto.clava.space/privkey.pem
```

### 4. Создание директории для certbot верификации

```bash
sudo mkdir -p /var/www/certbot
sudo chmod 755 /var/www/certbot
```

### 5. Запуск приложения

```bash
# Соберите и запустите контейнеры
docker-compose up -d --build

# Проверьте статус
docker-compose ps

# Просмотрите логи
docker-compose logs -f
```

### 6. Настройка автообновления сертификатов

Certbot сертификаты нужно обновлять каждые 90 дней. Настройте cron:

```bash
# Откройте crontab
sudo crontab -e

# Добавьте строку для автоматического обновления (проверка каждый день в 3:00)
0 3 * * * certbot renew --quiet --deploy-hook "docker-compose -f /opt/yoloto/docker-compose.yml exec -T nginx nginx -s reload"
```

### 7. Настройка файрвола (если используется)

```bash
# Разрешите HTTP и HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Проверьте статус
sudo ufw status
```

## Проверка работы

1. Откройте в браузере: https://yoloto.clava.space
2. Проверьте, что редирект с HTTP на HTTPS работает: http://yoloto.clava.space
3. Проверьте API: https://yoloto.clava.space/api/docs
4. Проверьте WebSocket соединение (откройте консоль браузера)

## Обновление приложения

```bash
cd /opt/yoloto
git pull
docker-compose down
docker-compose up -d --build
```

## Мониторинг

```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f nginx

# Проверка использования ресурсов
docker stats
```

## Troubleshooting

### Проблема: Nginx не может прочитать сертификаты

```bash
# Проверьте права доступа
ls -la /etc/letsencrypt/live/yoloto.clava.space/

# Если нужно, измените права
sudo chmod 644 /etc/letsencrypt/live/yoloto.clava.space/*.pem
```

### Проблема: 502 Bad Gateway

```bash
# Проверьте, что backend запущен
docker-compose ps

# Проверьте логи backend
docker-compose logs backend
```

### Проблема: WebSocket не работает

```bash
# Проверьте конфигурацию nginx
docker-compose exec nginx nginx -t

# Перезагрузите nginx
docker-compose exec nginx nginx -s reload
```

### Обновление сертификата вручную

```bash
# Обновите сертификат
sudo certbot renew

# Перезагрузите nginx
docker-compose exec nginx nginx -s reload
```

## Резервное копирование

```bash
# Создайте резервную копию базы данных
docker-compose exec backend cp /app/data/game.db /app/data/game.db.backup

# Или скопируйте всю директорию data
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

## Остановка приложения

```bash
docker-compose down
```

## Полное удаление

```bash
# Остановите и удалите контейнеры
docker-compose down -v

# Удалите образы (опционально)
docker-compose down --rmi all

# Удалите директорию проекта
rm -rf /opt/yoloto
```


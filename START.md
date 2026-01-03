# Запуск приложения на yoloto.clava.space

## ✅ Сертификаты установлены

Сертификаты находятся в правильных местах:
- `/etc/letsencrypt/live/yoloto.clava.space/fullchain.pem`
- `/etc/letsencrypt/live/yoloto.clava.space/privkey.pem`

## Шаги запуска

### 1. Проверьте права доступа к сертификатам

```bash
# Проверьте, что файлы существуют и читаемы
ls -la /etc/letsencrypt/live/yoloto.clava.space/

# Если нужно, установите правильные права
sudo chmod 644 /etc/letsencrypt/live/yoloto.clava.space/fullchain.pem
sudo chmod 644 /etc/letsencrypt/live/yoloto.clava.space/privkey.pem
```

### 2. Убедитесь, что используется production конфигурация

```bash
# Проверьте, что nginx.conf содержит настройки для yoloto.clava.space
grep "yoloto.clava.space" nginx/nginx.conf
```

Если нужно переключиться с локальной на production:
```bash
# Убедитесь, что используется правильный файл
# nginx/nginx.conf должен содержать HTTPS настройки
```

### 3. Создайте директорию для certbot верификации (если еще не создана)

```bash
sudo mkdir -p /var/www/certbot
sudo chmod 755 /var/www/certbot
```

### 4. Запустите приложение

```bash
# Перейдите в директорию проекта
cd /path/to/yoloto

# Запустите контейнеры
docker-compose up -d --build

# Проверьте статус
docker-compose ps

# Просмотрите логи
docker-compose logs -f
```

### 5. Проверьте работу

1. **HTTP редирект на HTTPS:**
   ```bash
   curl -I http://yoloto.clava.space
   # Должен вернуть 301 редирект на https://
   ```

2. **HTTPS доступ:**
   - Откройте в браузере: https://yoloto.clava.space
   - Проверьте, что сертификат валиден (замочек в адресной строке)

3. **API:**
   - https://yoloto.clava.space/api/docs

4. **WebSocket:**
   - Откройте консоль браузера на странице игры
   - Должно быть сообщение "WebSocket connected"

### 6. Проверка логов Nginx

```bash
# Проверьте логи nginx на ошибки
docker-compose logs nginx

# Если есть ошибки с сертификатами, проверьте:
docker-compose exec nginx ls -la /etc/letsencrypt/live/yoloto.clava.space/
```

## Возможные проблемы

### Проблема: Nginx не может прочитать сертификаты

**Решение:**
```bash
# Проверьте права доступа
sudo ls -la /etc/letsencrypt/live/yoloto.clava.space/

# Установите правильные права
sudo chmod 755 /etc/letsencrypt/live
sudo chmod 755 /etc/letsencrypt/archive
sudo chmod 644 /etc/letsencrypt/live/yoloto.clava.space/*.pem

# Перезапустите nginx
docker-compose restart nginx
```

### Проблема: 502 Bad Gateway

**Решение:**
```bash
# Проверьте, что backend запущен
docker-compose ps backend

# Проверьте логи backend
docker-compose logs backend

# Перезапустите все сервисы
docker-compose restart
```

### Проблема: SSL ошибка в браузере

**Решение:**
```bash
# Проверьте конфигурацию nginx
docker-compose exec nginx nginx -t

# Проверьте, что сертификаты смонтированы в контейнер
docker-compose exec nginx ls -la /etc/letsencrypt/live/yoloto.clava.space/

# Перезагрузите nginx
docker-compose exec nginx nginx -s reload
```

## Тестирование SSL

```bash
# Проверьте SSL сертификат
openssl s_client -connect yoloto.clava.space:443 -servername yoloto.clava.space

# Или используйте онлайн сервисы:
# https://www.ssllabs.com/ssltest/analyze.html?d=yoloto.clava.space
```

## Автоматическое обновление сертификатов

Сертификаты Let's Encrypt действительны 90 дней. Настройте автоматическое обновление:

```bash
# Добавьте в crontab
sudo crontab -e

# Добавьте строку (проверка каждый день в 3:00)
0 3 * * * certbot renew --quiet --deploy-hook "cd /path/to/yoloto && docker-compose exec -T nginx nginx -s reload"
```

## Остановка

```bash
docker-compose down
```

## Перезапуск

```bash
docker-compose restart
# или
docker-compose down && docker-compose up -d
```


# Игра в кости - MVP

Многопользовательская браузерная игра в кости с системой ставок и призового фонда, работающая в режиме реального времени.

## Технологический стек

### Backend
- **Python 3.11+**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0+** - ORM
- **SQLite** - база данных
- **WebSocket** - реальное время
- **JWT** - аутентификация

### Frontend
- **Svelte 5** - фреймворк
- **Vite** - сборщик
- **WebSocket API** - реальное время

### Инфраструктура
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - reverse proxy
- **Directus** - админ-панель

## Структура проекта

```
yoloto/
├── backend/          # FastAPI приложение
├── frontend/         # Svelte 5 приложение
├── nginx/            # Конфигурация Nginx
├── data/             # База данных SQLite
├── docker-compose.yml
└── README.md
```

## Быстрый старт

### Требования
- Docker 24.0+
- Docker Compose 2.20+

### Установка и запуск

1. **Клонируйте репозиторий** (если есть) или используйте текущую директорию

2. **Создайте файл `.env`** на основе `.env.example`:
```bash
cp .env.example .env
```

3. **Отредактируйте `.env`** и установите свои значения:
```env
JWT_SECRET_KEY=your_secret_key_here_change_in_production
DIRECTUS_KEY=directus_key_here
DIRECTUS_SECRET=directus_secret_here
DIRECTUS_ADMIN_EMAIL=admin@example.com
DIRECTUS_ADMIN_PASSWORD=admin_password_change_in_production
```

4. **Запустите приложение**:
```bash
docker-compose up -d --build
```

5. **Откройте в браузере**:
- Приложение: http://localhost
- API документация: http://localhost/api/docs
- Directus админ-панель: http://localhost/admin

## Разработка

### Backend

Для разработки backend локально:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

Для разработки frontend локально:

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен на http://localhost:5173

## API Endpoints

### Аутентификация
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `GET /api/auth/me` - Информация о пользователе

### Столы
- `GET /api/tables` - Список столов
- `GET /api/tables/{id}` - Информация о столе
- `POST /api/tables/{id}/join` - Присоединиться к столу
- `POST /api/tables/{id}/leave` - Покинуть стол

### WebSocket
- `WS /ws/{table_id}?token={jwt_token}` - Подключение к столу

## Игровая механика

1. **Ожидание игроков** - Игроки присоединяются к столу, делая ставку
2. **Обратный отсчет** - Когда набирается минимум 2 игрока, запускается таймер на 60 секунд
3. **Бросок костей** - Каждому игроку генерируется случайное число от 1 до 20
4. **Определение победителя** - Игрок с наибольшим числом выигрывает весь призовой фонд
5. **Новый раунд** - После 5 секунд показа результата начинается новый раунд

## Особенности

- ✅ Регистрация и авторизация пользователей
- ✅ Множественные игровые столы с разными ставками
- ✅ Реальное время через WebSocket
- ✅ Автоматический старт игры при наборе игроков
- ✅ Система транзакций и баланса
- ✅ История игр
- ✅ Админ-панель Directus

## Переменные окружения

Создайте файл `.env` в корне проекта:

```env
JWT_SECRET_KEY=your_secret_key_here
DIRECTUS_KEY=directus_key_here
DIRECTUS_SECRET=directus_secret_here
DIRECTUS_ADMIN_EMAIL=admin@example.com
DIRECTUS_ADMIN_PASSWORD=admin_password
```

## Обновление

```bash
git pull
docker-compose down
docker-compose up -d --build
```

## Логи

Просмотр логов всех сервисов:
```bash
docker-compose logs -f
```

Логи конкретного сервиса:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

## Остановка

```bash
docker-compose down
```

Для удаления всех данных (включая базу данных):
```bash
docker-compose down -v
```

## Troubleshooting

### Проблемы с портами
Если порты 80, 8000 или 8055 заняты, измените их в `docker-compose.yml`

### Проблемы с базой данных
База данных создается автоматически при первом запуске. Если возникают проблемы, удалите директорию `data/` и перезапустите.

### Проблемы с WebSocket
Убедитесь, что Nginx правильно настроен для проксирования WebSocket соединений.

## Лицензия

MIT


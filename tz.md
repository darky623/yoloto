# Техническое задание: MVP веб-игры в кости

## 1. Общее описание проекта

### 1.1 Назначение
Многопользовательская браузерная игра в кости с системой ставок и призового фонда, работающая в режиме реального времени.

### 1.2 Целевая аудитория
Пользователи, заинтересованные в простых многопользовательских играх с элементами азарта.

### 1.3 Ключевые особенности
- Игра в режиме реального времени через WebSocket
- Множественные игровые столы с разными ставками
- Система раундов с автоматическим стартом
- Режим наблюдателя для зарегистрированных пользователей

---

## 2. Функциональные требования

### 2.1 Система аутентификации

#### 2.1.1 Регистрация
- **Поля**: логин (уникальный), пароль, подтверждение пароля
- **Валидация**:
  - Логин: 3-20 символов, латиница, цифры, underscore
  - Пароль: минимум 6 символов
- **Начальный баланс**: 500 рублей (виртуальная валюта)

#### 2.1.2 Авторизация
- Вход по логину и паролю
- Сессия с использованием JWT токенов
- Автоматический logout при неактивности (опционально)

#### 2.1.3 Профиль пользователя
- Отображение: логин, текущий баланс
- История последних 10 игр (опционально для MVP)

### 2.2 Игровая механика

#### 2.2.1 Игровой стол (Table)
**Параметры стола:**
- ID стола
- Название стола (например: "Стол #1")
- Фиксированная ставка (bet amount): 500, 1000, 2000 руб.
- Призовой фонд (prize pool): сумма всех ставок текущего раунда
- Минимальное количество игроков для старта: 2
- Максимальное количество игроков: 6
- Список текущих игроков
- Статус стола: waiting (ожидание), countdown (отсчет), rolling (определение результата), finished (завершен раунд)

#### 2.2.2 Игровой процесс

**Фаза 1: Ожидание игроков (waiting)**
- Игроки видят доступные столы и их параметры
- Игрок может присоединиться к столу, если:
  - За столом < 6 игроков
  - У игрока достаточно средств для ставки
  - Стол в статусе waiting или countdown
- При присоединении:
  - Со счета списывается сумма ставки
  - Игрок добавляется в список участников раунда
  - Призовой фонд увеличивается на сумму ставки
  - Все игроки видят обновление в реальном времени

**Фаза 2: Обратный отсчет (countdown)**
- Запускается автоматически при достижении минимум 2 игроков
- Таймер: 60 секунд обратного отсчета
- Отображается для всех игроков синхронно
- В этой фазе новые игроки могут присоединяться (до достижения 6 игроков)
- Если во время countdown игрок остается один (другие вышли), таймер останавливается, возврат к фазе waiting

**Фаза 3: Бросок костей (rolling)**
- Запускается автоматически по истечении таймера
- Сервер генерирует случайное число от 1 до 20 для каждого игрока
- Длительность фазы: 3-5 секунд (анимация)
- Результаты отправляются всем подключенным пользователям одновременно

**Фаза 4: Определение победителя (finished)**
- Игрок с наибольшим числом выигрывает весь призовой фонд
- При равенстве наибольших чисел:
  - Призовой фонд делится поровну между победителями
- Баланс победителя увеличивается на сумму выигрыша
- Результат отображается 5 секунд
- Автоматический переход к новому раунду (Фаза 1)

**Фаза 5: Новый раунд**
- Стол очищается (все игроки удаляются из активного раунда)
- Призовой фонд обнуляется
- Статус возвращается в waiting
- Игроки могут снова присоединиться

#### 2.2.3 Дополнительные правила
- Игрок может участвовать только за одним столом одновременно
- Наблюдатели могут смотреть игру за любым столом без ставок
- Если у игрока недостаточно средств, кнопка "Присоединиться" неактивна
- История всех игр сохраняется в базе данных

### 2.3 Интерфейс пользователя

#### 2.3.1 Страница входа/регистрации
- Форма входа (логин, пароль)
- Форма регистрации (логин, пароль, подтверждение)
- Переключение между формами

#### 2.3.2 Главная страница (Lobby)
**Верхняя панель:**
- Логин пользователя
- Текущий баланс
- Кнопка выхода

**Список столов:**
- Карточки всех доступных столов
- Для каждого стола отображается:
  - Название
  - Размер ставки
  - Призовой фонд
  - Количество игроков (текущее/максимальное)
  - Статус (ожидание/идет игра/обратный отсчет)
  - Кнопка "Присоединиться" / "Наблюдать"

#### 2.3.3 Страница игрового стола
**Информационная панель:**
- Название стола
- Призовой фонд
- Ставка
- Таймер обратного отсчета (если активен)
- Статус игры

**Игровая область:**
- Визуализация игроков (до 6 позиций по кругу)
- Для каждого игрока:
  - Логин
  - Визуальное представление (аватар/иконка)
  - Результат броска (число от 1 до 20) - показывается после rolling
- Центральная область с анимацией кости

**Управление:**
- Кнопка "Сделать ставку" (если игрок не участвует)
- Кнопка "Покинуть стол"
- Статус участия игрока

**Обновления в реальном времени:**
- Присоединение/выход игроков
- Изменение призового фонда
- Обновление таймера
- Результаты броска
- Объявление победителя

---

## 3. Технические требования

### 3.1 Архитектура системы

```
[Клиент (Browser)] <--WebSocket/HTTP--> [Nginx] <--> [Backend API] <--> [SQLite DB]
                                           |
                                           └--> [Directus Admin]
```

### 3.2 Backend

#### 3.2.1 Технологический стек
- **Язык**: Python 3.11+
- **Фреймворк**: FastAPI (рекомендуется для простоты, async, встроенной поддержки WebSocket)
- **База данных**: SQLite
- **ORM**: SQLAlchemy 2.0+
- **WebSocket**: встроенный в FastAPI
- **Аутентификация**: JWT (библиотека python-jose)
- **Валидация**: Pydantic (встроена в FastAPI)

#### 3.2.2 Структура базы данных

**Таблица: users**
```sql
id: INTEGER PRIMARY KEY AUTOINCREMENT
username: VARCHAR(20) UNIQUE NOT NULL
password_hash: VARCHAR(255) NOT NULL
balance: DECIMAL(10, 2) DEFAULT 500.00
created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Таблица: tables**
```sql
id: INTEGER PRIMARY KEY AUTOINCREMENT
name: VARCHAR(50) NOT NULL
bet_amount: DECIMAL(10, 2) NOT NULL
min_players: INTEGER DEFAULT 2
max_players: INTEGER DEFAULT 6
status: VARCHAR(20) DEFAULT 'waiting'
created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Таблица: game_rounds**
```sql
id: INTEGER PRIMARY KEY AUTOINCREMENT
table_id: INTEGER NOT NULL (FK: tables.id)
round_number: INTEGER NOT NULL
prize_pool: DECIMAL(10, 2) NOT NULL
status: VARCHAR(20) DEFAULT 'waiting'
started_at: TIMESTAMP
finished_at: TIMESTAMP
created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Таблица: round_players**
```sql
id: INTEGER PRIMARY KEY AUTOINCREMENT
round_id: INTEGER NOT NULL (FK: game_rounds.id)
user_id: INTEGER NOT NULL (FK: users.id)
dice_result: INTEGER (1-20, NULL до броска)
bet_amount: DECIMAL(10, 2) NOT NULL
won_amount: DECIMAL(10, 2) DEFAULT 0
is_winner: BOOLEAN DEFAULT FALSE
joined_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**Таблица: transactions**
```sql
id: INTEGER PRIMARY KEY AUTOINCREMENT
user_id: INTEGER NOT NULL (FK: users.id)
round_id: INTEGER (FK: game_rounds.id, nullable)
amount: DECIMAL(10, 2) NOT NULL (отрицательная для ставок)
type: VARCHAR(20) NOT NULL (bet, win, refund)
balance_after: DECIMAL(10, 2) NOT NULL
created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### 3.2.3 API Endpoints

**Аутентификация:**
- `POST /api/auth/register` - регистрация
- `POST /api/auth/login` - вход (возвращает JWT)
- `GET /api/auth/me` - информация о текущем пользователе

**Игровые столы:**
- `GET /api/tables` - список всех столов
- `GET /api/tables/{table_id}` - информация о конкретном столе
- `POST /api/tables/{table_id}/join` - присоединиться к столу
- `POST /api/tables/{table_id}/leave` - покинуть стол

**WebSocket:**
- `WS /ws/{table_id}` - подключение к столу для получения обновлений в реальном времени

**Пользователь:**
- `GET /api/user/balance` - текущий баланс
- `GET /api/user/history` - история игр (опционально)

#### 3.2.4 WebSocket события

**От сервера к клиенту:**
```json
{
  "type": "player_joined",
  "data": {
    "player_id": 123,
    "username": "player1",
    "players_count": 2,
    "prize_pool": 1000
  }
}

{
  "type": "player_left",
  "data": {
    "player_id": 123,
    "username": "player1",
    "players_count": 1,
    "prize_pool": 500
  }
}

{
  "type": "countdown_started",
  "data": {
    "seconds": 60
  }
}

{
  "type": "countdown_update",
  "data": {
    "seconds_left": 45
  }
}

{
  "type": "game_rolling",
  "data": {
    "round_id": 456
  }
}

{
  "type": "game_result",
  "data": {
    "round_id": 456,
    "results": [
      {"player_id": 123, "username": "player1", "dice": 15},
      {"player_id": 124, "username": "player2", "dice": 18}
    ],
    "winners": [
      {"player_id": 124, "username": "player2", "won_amount": 1000}
    ]
  }
}

{
  "type": "round_finished",
  "data": {
    "next_round_in": 5
  }
}

{
  "type": "error",
  "data": {
    "message": "Insufficient balance"
  }
}
```

**От клиента к серверу:**
```json
{
  "type": "join_table",
  "data": {
    "table_id": 1
  }
}

{
  "type": "leave_table",
  "data": {
    "table_id": 1
  }
}
```

#### 3.2.5 Игровая логика (Game Loop)

**Background Task для каждого стола:**
1. Мониторинг количества игроков
2. Запуск таймера при достижении min_players
3. Обработка обратного отсчета (отправка обновлений каждую секунду)
4. Генерация случайных чисел по истечении таймера
5. Определение победителя(ей)
6. Начисление выигрыша
7. Задержка 5 секунд
8. Сброс раунда и переход к ожиданию

**Использовать**: `asyncio` tasks для параллельной обработки нескольких столов

### 3.3 Frontend

#### 3.3.1 Технологический стек
- **Фреймворк**: **Svelte 5** (легковесный, простой синтаксис, отличная работа с реактивностью)
- **UI библиотека**: **Skeleton UI** или **DaisyUI** (готовые компоненты, красивые стили)
- **Сборка**: Vite
- **WebSocket клиент**: нативный WebSocket API или библиотека `socket.io-client`
- **HTTP клиент**: fetch API или axios
- **Роутинг**: Svelte Router или SvelteKit (если нужен SSR)

#### 3.3.2 Структура страниц
```
/login - страница входа/регистрации
/lobby - главная страница со списком столов
/table/:id - страница игрового стола
```

#### 3.3.3 Компоненты

**Страница Login:**
- LoginForm
- RegisterForm

**Страница Lobby:**
- Header (баланс, логин, выход)
- TableCard (карточка стола)
- TableList (список столов)

**Страница Table:**
- TableHeader (название, призовой фонд, ставка)
- Timer (обратный отсчет)
- GameBoard (игровая область с позициями игроков)
- PlayerSlot (слот игрока с логином и результатом)
- DiceAnimation (анимация кости)
- ActionButtons (присоединиться/выйти)
- ResultModal (модальное окно с результатами)

#### 3.3.4 Управление состоянием
- **Svelte stores** для глобального состояния:
  - `userStore` - данные пользователя, баланс
  - `tablesStore` - список столов
  - `currentTableStore` - состояние текущего стола

#### 3.3.5 WebSocket подключение
- Установка соединения при входе на страницу стола
- Автоматическое переподключение при разрыве
- Обработка всех входящих событий
- Отправка команд на сервер

### 3.4 Directus (Admin Panel)

#### 3.4.1 Назначение
- Управление пользователями (просмотр, редактирование баланса, блокировка)
- Просмотр истории игр
- Настройка столов (создание, изменение ставок)
- Мониторинг транзакций

#### 3.4.2 Настройка
- Подключение к существующей SQLite базе
- Настройка коллекций для всех таблиц
- Создание ролей и прав доступа
- Настройка дашборда для администраторов

#### 3.4.3 Доступ
- Отдельный URL: `/admin` (через Nginx proxy)
- Аутентификация через встроенную систему Directus

### 3.5 Nginx

#### 3.5.1 Роль
- Reverse proxy для backend API
- Обслуживание статических файлов frontend
- Проксирование WebSocket соединений
- Маршрутизация запросов к Directus

#### 3.5.2 Конфигурация
```nginx
server {
    listen 80;
    server_name example.com;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Directus Admin
    location /admin {
        proxy_pass http://directus:8055;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3.6 Docker Compose

#### 3.6.1 Сервисы

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: dice_game_backend
    environment:
      - DATABASE_URL=sqlite:///./data/game.db
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: dice_game_frontend
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend

  directus:
    image: directus/directus:latest
    container_name: dice_game_directus
    environment:
      - KEY=${DIRECTUS_KEY}
      - SECRET=${DIRECTUS_SECRET}
      - DB_CLIENT=sqlite3
      - DB_FILENAME=/directus/database/data.db
      - ADMIN_EMAIL=${DIRECTUS_ADMIN_EMAIL}
      - ADMIN_PASSWORD=${DIRECTUS_ADMIN_PASSWORD}
    volumes:
      - ./data:/directus/database
      - directus_uploads:/directus/uploads
    ports:
      - "8055:8055"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: dice_game_nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
      - directus
    restart: unless-stopped

volumes:
  directus_uploads:
```

#### 3.6.2 Переменные окружения (.env)
```
JWT_SECRET_KEY=your_secret_key_here
DIRECTUS_KEY=directus_key_here
DIRECTUS_SECRET=directus_secret_here
DIRECTUS_ADMIN_EMAIL=admin@example.com
DIRECTUS_ADMIN_PASSWORD=admin_password
```

### 3.7 Деплой на Ubuntu 24.04

#### 3.7.1 Требования к серверу
- Ubuntu 24.04 LTS
- Docker 24.0+
- Docker Compose 2.20+
- Минимум 2GB RAM
- 20GB свободного места на диске

#### 3.7.2 Процесс развертывания
```bash
# 1. Клонирование репозитория
git clone <repository_url>
cd dice-game

# 2. Настройка переменных окружения
cp .env.example .env
nano .env

# 3. Сборка и запуск
docker-compose up -d --build

# 4. Проверка статуса
docker-compose ps

# 5. Просмотр логов
docker-compose logs -f
```

#### 3.7.3 Обновление
```bash
git pull
docker-compose down
docker-compose up -d --build
```

---

## 4. Нефункциональные требования

### 4.1 Производительность
- Время ответа API: < 200ms
- Задержка WebSocket сообщений: < 100ms
- Поддержка одновременно: до 100 активных пользователей
- Поддержка до 20 игровых столов одновременно

### 4.2 Безопасность
- Хеширование паролей с использованием bcrypt
- JWT токены с ограниченным временем жизни (24 часа)
- Валидация всех входящих данных
- Защита от SQL injection (через ORM)
- Rate limiting для API endpoints (опционально)
- CORS настройка для production

### 4.3 Надежность
- Автоматический restart сервисов при падении (Docker)
- Логирование всех критических операций
- Graceful shutdown для сохранения состояния игр
- Backup базы данных (ежедневный cron job)

### 4.4 Масштабируемость
- Архитектура позволяет горизонтальное масштабирование backend
- Возможность замены SQLite на PostgreSQL в будущем
- Разделение статики и API

### 4.5 Удобство использования
- Адаптивный дизайн (responsive)
- Поддержка основных браузеров (Chrome, Firefox, Safari, Edge)
- Интуитивный интерфейс
- Минимальное время загрузки страниц

---

## 5. Структура проекта

```
dice-game/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI приложение
│   │   ├── config.py            # Конфигурация
│   │   ├── database.py          # Подключение к БД
│   │   ├── models/              # SQLAlchemy модели
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── table.py
│   │   │   ├── game_round.py
│   │   │   └── transaction.py
│   │   ├── schemas/             # Pydantic схемы
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── table.py
│   │   │   └── game.py
│   │   ├── routers/             # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── tables.py
│   │   │   ├── users.py
│   │   │   └── websocket.py
│   │   ├── services/            # Бизнес-логика
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── game_service.py
│   │   │   └── table_manager.py
│   │   └── utils/               # Вспомогательные функции
│   │       ├── __init__.py
│   │       ├── security.py
│   │       └── dependencies.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic/                 # Миграции (опционально)
│
├── frontend/
│   ├── src/
│   │   ├── lib/                 # Svelte компоненты
│   │   │   ├── components/
│   │   │   │   ├── Auth/
│   │   │   │   │   ├── LoginForm.svelte
│   │   │   │   │   └── RegisterForm.svelte
│   │   │   │   ├── Lobby/
│   │   │   │   │   ├── Header.svelte
│   │   │   │   │   ├── TableCard.svelte
│   │   │   │   │   └── TableList.svelte
│   │   │   │   └── Game/
│   │   │   │       ├── TableHeader.svelte
│   │   │   │       ├── Timer.svelte
│   │   │   │       ├── GameBoard.svelte
│   │   │   │       ├── PlayerSlot.svelte
│   │   │   │       ├── DiceAnimation.svelte
│   │   │   │       └── ActionButtons.svelte
│   │   │   ├── stores/
│   │   │   │   ├── userStore.js
│   │   │   │   ├── tablesStore.js
│   │   │   │   └── currentTableStore.js
│   │   │   └── services/
│   │   │       ├── api.js
│   │   │       └── websocket.js
│   │   ├── routes/
│   │   │   ├── +page.svelte     # Login
│   │   │   ├── lobby/
│   │   │   │   └── +page.svelte
│   │   │   └── table/
│   │   │       └── [id]/
│   │   │           └── +page.svelte
│   │   ├── app.html
│   │   └── app.css
│   ├── static/
│   ├── Dockerfile
│   ├── package.json
│   ├── svelte.config.js
│   └── vite.config.js
│
├── nginx/
│   └── nginx.conf
│
├── data/                        # SQLite база и uploads
│   └── game.db
│
├── docker-compose.yml
├── .env.example
├── .env
├── .gitignore
└── README.md
```

---

## 6. Этапы разработки MVP

### Этап 1: Подготовка инфраструктуры (1-2 дня)
- [ ] Настройка структуры проекта
- [ ] Создание Docker Compose конфигурации
- [ ] Настройка базы данных SQLite
- [ ] Базовая конфигурация Nginx

### Этап 2: Backend разработка (4-5 дней)
- [ ] Создание моделей БД и миграций
- [ ] Реализация системы аутентификации (JWT)
- [ ] Разработка API endpoints
- [ ] Реализация WebSocket соединений
- [ ] Разработка игровой логики (game loop)
- [ ] Тестирование backend функционала

### Этап 3: Frontend разработка (4-5 дней)
- [ ] Настройка Svelte проекта
- [ ] Разработка страницы Login/Register
- [ ] Разработка страницы Lobby
- [ ] Разработка страницы Table
- [ ] Интеграция с WebSocket
- [ ] Интеграция с API
- [ ] Создание анимаций и визуальных эффектов

### Этап 4: Интеграция Directus (1 день)
- [ ] Установка и настройка Directus
- [ ] Подключение к базе данных
- [ ] Настройка коллекций и прав доступа
- [ ] Создание административного дашборда

### Этап 5: Тестирование и деплой (2-3 дня)
- [ ] Интеграционное тестирование
- [ ] Тестирование WebSocket в нагрузке
- [ ] Тестирование на разных устройствах
- [ ] Деплой на production сервер
- [ ] Настройка мониторинга и логирования
- [ ] Документация для пользователей

**Общая оценка: 12-16 дней разработки**

---

## 7. Возможные расширения (Post-MVP)

### 7.1 Функциональные
- Чат между игроками
- Система достижений
- Рейтинг игроков
- Приватные столы с паролем
- Возможность пополнения баланса (интеграция платежей)
- Бонусная система и промокоды
- Режим турниров
- Статистика игрока

### 7.2 Технические
- Миграция на PostgreSQL
- Redis для кеширования и pub/sub
- Система очередей (Celery) для фоновых задач
- Мониторинг (Prometheus + Grafana)
- CI/CD pipeline
- Автоматическое тестирование
- HTTPS сертификаты (Let's Encrypt)

---

## 8. Критерии готовности MVP

- [x] Пользователь может зарегистрироваться и войти в систему
- [x] Пользователь видит список доступных столов
- [x] Пользователь может присоединиться к столу
- [x] Игра стартует автоматически при достижении 2 игроков
- [x] Обратный отсчет отображается корректно для всех игроков
- [x] Результаты броска генерируются на сервере
- [x] Победитель определяется правильно
- [x] Баланс обновляется корректно
- [x] Все игроки видят одинаков
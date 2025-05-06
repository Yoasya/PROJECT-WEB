# SWAGcraft - Интернет-магазин Minecraft-тематической одежды

SWAGcraft - это современный интернет-магазин, специализирующийся на продаже пародийной одежды с тематикой Minecraft. Проект разработан с использованием Flask и Bootstrap 5.

## Функциональные возможности

- Адаптивный дизайн для всех устройств
- Каталог товаров с фильтрацией по категориям
- Корзина покупок с возможностью добавления/удаления товаров
- Система оформления заказов
- Административная панель для управления товарами
- Система аутентификации пользователей

## Технологии

- Backend: Python 3.10+, Flask 2.3, SQLAlchemy 2.0
- Frontend: Bootstrap 5, JavaScript
- База данных: SQLite (разработка), PostgreSQL (продакшен)
- Дополнительные компоненты:
  - Flask-Login для аутентификации
  - Flask-Admin для админ-панели
  - Flask-Limiter для защиты от DDoS
  - Flask-WTF для форм

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Yoasya/PROJECT-WEB.git
cd swagcraft
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env и добавьте необходимые переменные окружения:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///swagcraft.db
```

5. Инициализируйте базу данных:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Запустите приложение:
```bash
python app.py
```

Приложение будет доступно по адресу: http://localhost:5000

## Структура проекта

```
swagcraft/
├── app.py              # Основной файл приложения
├── requirements.txt    # Зависимости проекта
├── static/            # Статические файлы
│   ├── css/
│   ├── js/
│   └── uploads/       # Загруженные изображения
├── templates/         # HTML шаблоны
│   ├── base.html
│   ├── index.html
│   ├── catalog.html
│   ├── cart.html
│   ├── checkout.html
│   ├── login.html
│   └── register.html
└── README.md
```

## Тестирование

Для запуска тестов используйте команду:
```bash
pytest
```

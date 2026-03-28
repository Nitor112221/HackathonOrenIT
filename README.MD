# Проект для хакатона Орен ИТ

## Установка и запуск

### Требования
* python 3.11
* Docker (для работы Redis и тестирующей системы)
* Git (установка репозитория)

### 1. Клонирование репозитория

```bash
git clone https://github.com/Nitor112221/HackathonOrenIT
cd HackathonOrenIT
```

### 2. Создание виртуального окружения
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install --upgrade pip
pip install -r requirements/prod.txt
```

### 4. Переход в директорию с кодом
```bash
cd hackathon
```

### 5. Настройка переменных окружения
#### Скопируйте файл template.env в .env и отредактируйте при необходимости (не меняйте debug режим, если поставить его на false, то статику надо раздавать из отдельного места):
```bash
cp template.env .env
```

### 6. Применение миграций базы данных
```bash
python manage.py migrate
```

### 7. Загрузите заготовленные данные (модули, уроки, задания)
```bash
python manage.py loaddata fixtures/data.json
```

### 8. Запуск Redis в Docker
```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 9. Запуск Celery worker
```bash
celery -A hackathon worker --loglevel=info -P prefork
```

### 10 Запуск Запуск Django server (в другом терминале из папки hackathon)
```bash
python manage.py runserver
```
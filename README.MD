# Проект для хакатона Орен ИТ

### Команды для запуска

## Создание виртуального окружения для проекта:
* Создание виртуального окружения: 
```bash
python3 -m venv .venv
```
* Активация виртуального окружения (Linux):
```bash
source .venv/bin/activate
```
* Активация виртуального окружения (Windows):
```bash
.venv/Scripts/activate
```
## Установка зависимостей
* Зависимости для разработки: 
```bash
pip install -r requirements/dev.txt
```

## Запуск

```bash
cd hackathon
```

```bash
python manage.py migrate
```

```bash
python manage.py loaddata fixtures/data.json
```

```bash
python manage.py runserver
```
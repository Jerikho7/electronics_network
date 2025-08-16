# Система управления электронной торговой сетью

Веб-приложение для управления иерархической сетью по продаже электроники с API и админ-панелью на Django.

## Основные возможности

- **Трехуровневая структура сети**:
  - Завод (уровень 0)
  - Розничная сеть (уровень 1)
  - ИП (уровень 2)
- **Полное управление** через админку и REST API
- **Учет задолженностей** с иерархией поставщиков
- **Фильтрация** по стране/городу
- **Разграничение прав доступа**

## Требования

- Python 3.8+
- Django 3+
- DRF 3.10+
- PostgreSQL 10+

## Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/ваш-username/electronics-network.git
cd electronics-network
```
### 2. Установка Poetry (если не установлен)
```bash
pip install poetry
```
### 3. Установка зависимостей
```bash
poetry install --no-root
```
### 4. Настройка окружения
```bash
cp .env.example .env
# Отредактируйте .env файл
```
### 5. Применение миграций
```bash
python run python manage.py migrate
```
### 6. Создание суперпользователя
```bash
python run python manage.py createsuperuser
```
### 7. Запуск сервера
```bash
python run python manage.py runserver
```



# Калькулятор позиції дрона

Python-додаток для розрахунку позиції дрона на основі контрольних точок,
азимута та координат зображення.

## Огляд

Цей проект надає інструменти для визначення географічного положення дрона,
використовуючи:

- Відому контрольну точку (з широтою та довготою)
- Азимут дрона (компасний напрямок)
- Піксельні координати контрольної точки на зображенні з камери дрона

## Встановлення

Цей проект використовує Poetry для керування залежностями.

```bash
# Клонувати репозиторій
git clone https://github.com/AlexGrytsai/DronePosition.git
cd DronePosition

# Встановити залежності
poetry install
```

## Використання

Приклад базового використання:

```python
from src.entity import Drone, GeoPoint, ImagePoint
from src.services import GeoService

# Створити дрон з типовим азимутом (335°)
drone = Drone()

# Створити геосервіс з типовими розмірами зображення (640x512)
geo_service = GeoService()

# Визначити контрольну точку (відомі географічні координати)
control_geo_point = GeoPoint(50.603694, 30.650625)

# Визначити, де ця контрольна точка з'являється на зображенні з камери дрона
control_image_point = ImagePoint(558, 328)

# Розрахувати позицію дрона
drone_position = geo_service.calculate_drone_position(
    control_geo_point,
    drone.azimuth,
    control_image_point,
)

print(f"Координати дрона: {drone_position}")
```

## Структура проекту

- `src/entity/` - Основні моделі даних (Drone, GeoPoint, ImagePoint)
- `src/services/` - Бізнес-логіка для географічних розрахунків
- `main.py` - Точка входу до додатку

## Вимоги

- Python 3.12+
- Залежності, перелічені в pyproject.toml

## Розробка

Цей проект використовує:

- Black для форматування коду
- Flake8 для перевірки коду

Запуск форматування:

```bash
poetry run black .
```

Запуск перевірки:

```bash
poetry run flake8
```

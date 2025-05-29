# Калькулятор позиції дрона

Python-додаток для розрахунку позиції дрона на основі контрольних точок,
азимута та координат зображення, а також керування дроном.

## Огляд

Цей проект надає інструменти для:

- Визначення географічного положення дрона, використовуючи:
  - Відому контрольну точку (з широтою та довготою)
  - Азимут дрона (компасний напрямок)
  - Піксельні координати контрольної точки на зображенні з камери дрона
- Керування дроном через DroneKit:
  - Підключення до дрона або симулятора
  - Зліт та посадка
  - Політ до заданих координат
  - Поворот до заданого азимута

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

### Розрахунок позиції дрона

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

### Керування дроном

```python
from dronekit import LocationGlobalRelative
from src.entity import Drone

# Створення екземпляра дрона
dron = Drone()

# Підключення та підготовка до польоту
dron.turn_on()
dron.arm_vehicle()

# Зліт на висоту 100 метрів
dron.takeoff(target_altitude=100)

# Визначення цільової точки
target_point = LocationGlobalRelative(50.443326, 30.448078, 100)

# Поворот до цільової точки
dron.turn_to_target_point(target_point)

# Політ до цільової точки
dron.fly_to(target_point, power=1200)

# Поворот до заданого азимута
dron.turn_to_target_azimuth(target_azimuth=350)
```

## Структура проекту

- `src/entity/` - Основні моделі даних (Drone, GeoPoint, ImagePoint)
- `src/services/` - Бізнес-логіка для географічних розрахунків та навігації
- `src/drone_mission.py` - Приклад місії для дрона
- `main.py` - Точка входу до додатку

## Вимоги

- Python 3.12+
- DroneKit та DroneKit-SITL для симуляції та керування дроном
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

from __future__ import annotations


class GeoPoint:
    """
    Клас, що представляє географічну точку з координатами широти та довготи.
    """

    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = latitude
        self.longitude = longitude

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GeoPoint):
            return (
                self.latitude == other.latitude
                and self.longitude == other.longitude
            )
        return False

    def __hash__(self) -> int:
        return hash((self.latitude, self.longitude))

    def __str__(self) -> str:
        return f"Point({self.latitude}, {self.longitude})"


class ImagePoint:
    """
    Клас, що представляє точку на зображенні з координатами x та y.
    """

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ImagePoint):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __str__(self) -> str:
        return f"Point({self.x}, {self.y})"

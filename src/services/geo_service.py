import math
from abc import ABC, abstractmethod
from typing import Tuple

from src.entity.image import Image
from src.entity.point import GeoPoint, ImagePoint


class GeoBaseService(ABC):
    @abstractmethod
    def calculate_drone_position(
        self,
        control_geo_point: GeoPoint,
        azimuth: float,
        control_image_point: Image,
    ) -> GeoPoint:
        pass


class GeoService(GeoBaseService):
    """Клас для виконання географічних розрахунків."""

    EARTH_RADIUS: int = 6371000  # радіус Землі в метрах
    PIXELS_PER_METER: float = 1 / 0.38

    def __init__(self, image: Image = Image()) -> None:
        self._image = image

    @property
    def image(self) -> Image:
        return self._image

    @image.setter
    def image(self, image: Image) -> None:
        self._image = image

    @property
    def pixels_per_meter(self) -> float:
        return self.PIXELS_PER_METER

    @pixels_per_meter.setter
    def pixels_per_meter(self, pixels_per_meter: float) -> None:
        self.PIXELS_PER_METER = pixels_per_meter

    def calculate_drone_position(
        self,
        control_geo_point: GeoPoint,
        azimuth: float,
        control_image_point: ImagePoint,
    ) -> GeoPoint:
        pixel_offset = self._calculate_pixel_offset(
            self._image, control_image_point
        )

        meter_offset = self._convert_pixels_to_meters(pixel_offset)

        geo_offset = self._apply_rotation(meter_offset, azimuth)

        return self._calculate_new_position(control_geo_point, geo_offset)

    @staticmethod
    def _calculate_pixel_offset(
        image: Image,
        control_image_point: ImagePoint,
    ) -> Tuple[float, float]:
        """
        Обчислює зсув у пікселях між центром зображення та контрольною точкою.
        """
        return (
            control_image_point.x - image.center.x,
            control_image_point.y - image.center.y,
        )

    def _convert_pixels_to_meters(
        self, pixel_offset: Tuple[float, float]
    ) -> Tuple[float, float]:
        """Конвертує зміщення у пікселях у метри."""
        dx_pixels, dy_pixels = pixel_offset
        dx_meters = dx_pixels / self.PIXELS_PER_METER
        dy_meters = dy_pixels / self.PIXELS_PER_METER
        return dx_meters, dy_meters

    @staticmethod
    def _apply_rotation(
        meter_offset: Tuple[float, float], azimuth: float
    ) -> Tuple[float, float]:
        """Застосовує поворот для отримання географічного усунення."""
        dx_meters, dy_meters = meter_offset
        azimuth_rad = math.radians(azimuth)

        rotation_matrix = [
            [math.sin(azimuth_rad), -math.cos(azimuth_rad)],
            [math.cos(azimuth_rad), math.sin(azimuth_rad)],
        ]

        east_offset = (
            rotation_matrix[0][0] * dx_meters
            + rotation_matrix[0][1] * dy_meters
        )
        north_offset = (
            rotation_matrix[1][0] * dx_meters
            + rotation_matrix[1][1] * dy_meters
        )

        return east_offset, north_offset

    def _calculate_new_position(
        self, control_point: GeoPoint, geo_offset: Tuple[float, float]
    ) -> GeoPoint:
        """
        Обчислює нову позицію на основі вихідної точки та географічного
        усунення.
        """
        east_offset, north_offset = geo_offset

        # Конвертація зсувів у різницю широти/довготи
        lat_diff = (north_offset / self.EARTH_RADIUS) * (180 / math.pi)
        lon_diff = (
            (east_offset / self.EARTH_RADIUS)
            * (180 / math.pi)
            / math.cos(math.radians(control_point.latitude))
        )

        return GeoPoint(
            control_point.latitude - lat_diff,
            control_point.longitude - lon_diff,
        )

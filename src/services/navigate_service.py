import math
from abc import ABC, abstractmethod

from dronekit import LocationGlobalRelative


class NavigateBaseService(ABC):
    EARTH_RADIUS: int = 6371000

    @staticmethod
    @abstractmethod
    def get_azimuth(
        current_location: LocationGlobalRelative,
        destination_location: LocationGlobalRelative,
    ) -> float:
        """Повертає азимут від поточної точки до цільової точки."""
        pass

    @abstractmethod
    def get_distance_to_destination(
        self,
        current_location: LocationGlobalRelative,
        destination_location: LocationGlobalRelative,
    ) -> float:
        """Повертає відстань від поточної точки до цільової точки."""
        pass

    @staticmethod
    @abstractmethod
    def get_turn_direction(current_yaw, target_yaw) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def get_azimuth_diff(
        current_azimuth: float, target_azimuth: float
    ) -> float:
        pass


class NavigateService(NavigateBaseService):
    @staticmethod
    def get_azimuth(
        current_location: LocationGlobalRelative,
        destination_location: LocationGlobalRelative,
    ) -> float:
        lat1 = math.radians(current_location.lat)
        lat2 = math.radians(destination_location.lat)
        diff_long = math.radians(
            destination_location.lon - current_location.lon
        )

        x = math.sin(diff_long) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (
            math.sin(lat1) * math.cos(lat2) * math.cos(diff_long)
        )
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)

        return (initial_bearing + 360) % 360

    def get_distance_to_destination(
        self,
        current_location: LocationGlobalRelative,
        destination_location: LocationGlobalRelative,
    ) -> float:
        lat1, lon1 = math.radians(current_location.lat), math.radians(
            current_location.lon
        )
        lat2, lon2 = math.radians(destination_location.lat), math.radians(
            destination_location.lon
        )
        a = (
            math.sin((lat2 - lat1) / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin((lon2 - lon1) / 2) ** 2
        )
        return (
            self.EARTH_RADIUS * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        )

    @staticmethod
    def get_turn_direction(current_yaw, target_yaw) -> bool:
        delta = (target_yaw - current_yaw + 360) % 360

        if delta == 0:
            return False
        elif delta <= 180:
            return True
        else:
            return False

    @staticmethod
    def get_azimuth_diff(
        current_azimuth: float, target_azimuth: float
    ) -> float:
        diff = (target_azimuth - current_azimuth + 360) % 360
        return diff if diff <= 180 else diff - 360  # діапазон [-180, 180]

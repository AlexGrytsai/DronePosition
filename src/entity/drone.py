from src.entity.exceptions import AzimuthException


class Drone:
    """
    Клас, що представляє дрон з певними координатами та напрямком.
    """

    def __init__(self, azimuth: float = 335) -> None:
        self._azimuth = azimuth

    @property
    def azimuth(self) -> float:
        return self._azimuth

    @azimuth.setter
    def azimuth(self, azimuth: float) -> None:
        if azimuth < 0 or azimuth > 360:
            raise AzimuthException(
                "Азимут повинен бути в діапазоні від 0 до 360"
            )
        self._azimuth = azimuth

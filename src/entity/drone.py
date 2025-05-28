import logging
import time
from typing import Optional

from dronekit import LocationGlobalRelative, VehicleMode, connect
from dronekit_sitl import SITL

from src.entity.exceptions import AzimuthException

logger = logging.getLogger(__name__)


class Drone:
    """
    Клас, що представляє дрон з певними координатами та напрямком.
    """

    def __init__(
        self,
        home_point: Optional[LocationGlobalRelative],
        mode: Optional[str],
        azimuth: Optional[float] = 335,
    ) -> None:
        self._azimuth = azimuth
        self._vehicle = None
        self._mode = VehicleMode(mode) if mode else VehicleMode("ALT_HOLD")
        self._home_point = home_point or LocationGlobalRelative(
            50.450739, 30.461242
        )
        self._ready_to_fly = False

    def turn_on(self) -> bool:
        if not self._vehicle:
            logger.info("Підключення до дрону...")
            self._install_home_point()
            self._vehicle = connect(
                "tcp:127.0.0.1:5762", wait_ready=True, heartbeat_timeout=60
            )
            self._vehicle.mode = self._mode

            logger.info(
                f"Підключення успішне. Режим польоту: {self._mode}"
                f"Домашня точка: {self._vehicle.location.global_frame}"
            )
        logger.info(
            f"Дрон увімкнено. "
            f"Домашня точка: {self._vehicle.location.global_frame}"
        )
        return True

    def arm_vehicle(self) -> bool:
        if not self._vehicle:
            logger.warning("Дрон не підключено")
            return False
        logger.info("Запусків моторів...")

        while not self._vehicle.is_armable:
            logger.info("Очікування на готовність до польоту...")
            time.sleep(1)

        self._vehicle.armed = True

        while not self._vehicle.armed:
            logger.info("Очікування на запуск моторів...")
            time.sleep(1)
        logger.info("Мотори запущено. Дрон готовий до польоту.")

        self._ready_to_fly = True
        return True

    def takeoff(self, target_altitude: float = 100) -> bool:
        if not self._ready_to_fly:
            logger.warning("Дрон не готовий до польоту")
            return False
        while True:
            current_altitude = self._vehicle.location.global_relative_frame.alt
            if current_altitude >= target_altitude * 0.85:
                self._vehicle.channels.overrides["3"] = 1800
            self._vehicle.channels.overrides["3"] = 2500

            logger.info(f"Altitude: {current_altitude}")
            if current_altitude >= target_altitude * 0.95:
                logger.info(f"Reached target altitude - {current_altitude}")
                self._vehicle.channels.overrides["3"] = 1500
                break
            time.sleep(1)
        return True

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

    def _install_home_point(self) -> None:
        logger.info("Встановлення координат точки взлету")

        sitl = SITL()
        sitl.download("copter", "stable", verbose=True)
        sitl_args = [
            "-I0",
            "--model",
            "quad",
            f"--home={self._home_point.lat},{self._home_point.lon},0,0",
        ]
        sitl.launch(sitl_args, await_ready=True, restart=True)

import logging
import time
from typing import Optional

from dronekit import (
    LocationGlobalRelative,
    VehicleMode,
    connect,
    Vehicle,
)
from dronekit_sitl import SITL

from src.entity.exceptions import AzimuthException
from src.services.navigate_service import NavigateBaseService, NavigateService

logger = logging.getLogger(__name__)


class Drone:
    """
    Клас, що представляє дрон з певними координатами та напрямком.
    """

    def __init__(
        self,
        home_point: Optional[LocationGlobalRelative] = None,
        mode: Optional[str] = None,
        navigation_service: Optional[NavigateBaseService] = None,
        azimuth: Optional[float] = 335,
    ) -> None:
        self._azimuth = azimuth
        self._vehicle: Optional[Vehicle] = None
        self._mode = VehicleMode(mode) if mode else VehicleMode("ALT_HOLD")
        self._home_point = home_point or LocationGlobalRelative(
            50.450739, 30.461242
        )
        self._navigation_service = navigation_service or NavigateService()
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
            self._vehicle.channels.overrides["3"] = 3000

            logger.info(f"Висота: {current_altitude}")
            if current_altitude >= target_altitude * 0.95:
                logger.info(f"Досягнуто потрібну висоту - {current_altitude}")
                self._vehicle.channels.overrides["3"] = 1500
                break
            time.sleep(1)
        return True

    def turn_to_target_azimuth(
        self,
        target_azimuth: float,
    ) -> None:
        logger.info(f"Поворот до азимуту: {target_azimuth:.2f}°")
        self.azimuth = target_azimuth

        self._turn_to_target_azimuth()

    def turn_to_target_point(
        self,
        target_point: LocationGlobalRelative,
    ) -> None:
        """
        Розвертає дрон до цільової точки.
        """

        self.azimuth = self._navigation_service.get_azimuth(
            self._vehicle.location.global_relative_frame, target_point
        )
        logger.info(f"Розрахований азимут: {self.azimuth:.2f}°")

        self._turn_to_target_azimuth()

    def fly_to(
        self,
        target_location: LocationGlobalRelative,
        min_distance: float = 2.0,
        power: int = 1300,
    ):
        """
        Летить до цільової точки з азимут-корекцією через 10% відстані.
        """
        _power = power
        distance_to_target = (
            self._navigation_service.get_distance_to_destination(
                self._vehicle.location.global_relative_frame, target_location
            )
        )
        logger.info(f"Відстань до цільової точки: {distance_to_target:.2f} м")
        while True:
            distance = self._navigation_service.get_distance_to_destination(
                self._vehicle.location.global_relative_frame, target_location
            )

            if distance <= min_distance:
                logger.info(
                    f"Досягнуто цільової точки. Відстань: {distance:.2f} м"
                )
                self._vehicle.channels.overrides["2"] = 1500  # стоп
                break

            elif distance <= distance_to_target * 0.9:
                self._vehicle.channels.overrides["2"] = 1500  # стоп
                distance_to_target = distance
                logger.info(f"Відстань до цільової точки: {distance:.2f} м")

                logger.info("Корекція курсу...")
                self.turn_to_target_point(target_location)
                logger.info("Корекція курсу завершена")

                if distance_to_target <= 30:
                    _power = 1400
                elif distance_to_target <= 50:
                    _power = 1300

                self._move_forward(power=_power)
            else:
                self._move_forward(power=_power)

    def _move_forward(self, power: int = 1300):
        self._vehicle.channels.overrides["2"] = power

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

    def _turn_to_target_azimuth(self) -> None:
        while True:
            current_heading = self._vehicle.heading
            diff = self._navigation_service.get_azimuth_diff(
                current_heading, self.azimuth
            )

            logger.info(
                f"Поточний азимут: {current_heading:.2f}°, Δ={diff:.2f}°"
            )

            if abs(diff) <= 1:
                self._vehicle.channels.overrides["4"] = 1500  # стоп
                logger.info("Досягнуто цільового напрямку.")
                break

            if abs(diff) > 15 or abs(diff) <= 10:
                power = 1530 if diff > 0 else 1470
            else:
                power = 1600 if diff > 0 else 1400
            self._vehicle.channels.overrides["4"] = power
            time.sleep(0.1)


if __name__ == "__main__":
    dron = Drone()

    dron.turn_on()
    dron.arm_vehicle()
    dron.takeoff(target_altitude=20)

    target_point = LocationGlobalRelative(50.443326, 30.448078, 20)

    dron.fly_to(target_point, power=1200)

    dron.turn_to_target_azimuth(target_azimuth=350)

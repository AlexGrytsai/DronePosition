from src.entity import Drone
from src.entity.point import GeoPoint, ImagePoint
from src.services import GeoService


def main(
    drone: Drone = Drone(),
    geo_service: GeoService = GeoService(),
    control_geo_point: GeoPoint = GeoPoint(50.603694, 30.650625),
    control_image_point: ImagePoint = ImagePoint(558, 328),
) -> GeoPoint:
    return geo_service.calculate_drone_position(
        control_geo_point,
        drone.azimuth,
        control_image_point,
    )


if __name__ == "__main__":
    print(f"Координати Центру зображення: {main()}")

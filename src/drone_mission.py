from dronekit import LocationGlobalRelative

from src.entity import Drone

if __name__ == "__main__":
    dron = Drone()

    altitude = 100

    dron.turn_on()
    dron.arm_vehicle()
    dron.takeoff(target_altitude=altitude)

    target_point = LocationGlobalRelative(50.443326, 30.448078, altitude)

    dron.turn_to_target_point(target_point)

    dron.fly_to(target_point, power=1200)

    dron.turn_to_target_azimuth(target_azimuth=350)

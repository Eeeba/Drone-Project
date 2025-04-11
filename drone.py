from djitellopy import Tello
from time import sleep

pilot = Tello()

pilot.connect()
pilot.takeoff()

sleep(1)
pilot.move_left(100)
sleep(1)
pilot.rotate_clockwise(90)
sleep(1)
pilot.move_forward(100)
sleep(1)

pilot.land()
from djitellopy import Tello
from time import sleep

pilot = Tello()

pilot.connect()
pilot.takeoff()

sleep(1)
pilot.move_left(50)
sleep(1)
pilot.rotate_clockwise
sleep(1)
pilot.move_forward(10)
sleep(1)

pilot.land()
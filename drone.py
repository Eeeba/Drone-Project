from djitellopy import tello
from time import sleep

pilot = tello.Tello()

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
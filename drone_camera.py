from djitellopy import tello
from time import sleep
import cv2
import threading

pilot = tello.Tello()

# shows the camera frames
def camera_on():
    while True:
        frame = pilot.get_frame_read().frame
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('e'):
            break
    cv2.destroyAllWindows()
    
# some random commands for the drone to follow
def random_moves():
    sleep(3)
    pilot.move_up(150)
    sleep(3)
    pilot.flip("b")
    sleep(2)
    pilot.flip("f")
    pilot.move_down(100)
    sleep(3)
    pilot.rotate_clockwise()
    sleep(3)
    pilot.land()
    
# completing the tasks together
def joined_tasks():
    pilot.connect()
    sleep(3)
    pilot.takeoff()
    sleep(3)
    pilot.streamon()
    
    task1 = threading.Thread(target = camera_on, args=())
    task2 = threading.Thread(target = random_moves, args=())
    
    task1.start()
    task2.start()
    
    task1.join()
    task2.join()
    
    pilot.streamoff()
    pilot.end()
    
# makes sure this program is only performed
    if __name__ == "__main__": joined_tasks()
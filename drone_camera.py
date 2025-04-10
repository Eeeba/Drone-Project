import cv2
from djitellopy import tello
from time import sleep
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
    sleep(10)
    pilot.move_up(50)
    sleep(10)
    pilot.move_forward(50)
    sleep(10)
    pilot.land()
    
# completing the tasks together
def main():
    pilot.connect()
    sleep(10)
    pilot.takeoff()
    sleep(10)
    pilot.streamon()
    
    task1 = threading.Thread(target=camera_on, args=())
    task2 = threading.Thread(target=random_moves, args=())
    
    task1.start()
    task2.start()
    
    task1.join()
    task2.join()
    
    pilot.streamoff()
    pilot.end()
    
    # makes sure this program is only performed
if __name__ == "__main__": 
    main()
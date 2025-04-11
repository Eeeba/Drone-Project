import cv2
import numpy as np
from djitellopy import tello

# Connect to Tello
drone = tello.Tello()
drone.connect()
drone.streamon()

# Takeoff
drone.takeoff()

try:
    while True:
        # Get the current frame from Tello
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (640, 480))

        # Convert to HSV for color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the color range for tracking (e.g., red)
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask1 + mask2

        # Find contours (i.e., detected blobs of color)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            cx = x + w // 2
            cy = y + h // 2

            # Draw rectangle and center dot
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

            # Movement logic (basic)
            if cx < 270:
                drone.rotate_counter_clockwise(10)
            elif cx > 370:
                drone.rotate_clockwise(10)

        # Display result
        cv2.imshow("Tello Camera", frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    drone.land()
    drone.streamoff()
    cv2.destroyAllWindows()

# Python code for Multiple Color Detection using Tello Drone
import numpy as np
import cv2
import time
import djitellopy as tello

# Connect to Tello
pilot = tello.Tello()
try:
    pilot.connect()
    print(f"Battery: {pilot.get_battery()}%")
    pilot.streamon()
except Exception as e:
    print(f"Failed to connect to Tello: {e}")
    exit()

# Get video stream reader
frame_reader = pilot.get_frame_read()

# Define kernel for morphological operations
kernel = np.ones((5, 5), "uint8")

last_log_time = time.time()

while True:
    # Get the current frame from Tello's camera
    frame = frame_reader.frame

    # Convert the frame from BGR to HSV color space
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define color ranges and masks
    
    # red
    red_lower = np.array([136, 87, 50], np.uint8)
    red_upper = np.array([180, 255, 200], np.uint8)
    red_mask = cv2.inRange(hsvFrame, red_lower, red_upper)

    # green
    green_lower = np.array([35, 52, 72], np.uint8)
    green_upper = np.array([85, 255, 255], np.uint8)
    green_mask = cv2.inRange(hsvFrame, green_lower, green_upper)

    # blue
    blue_lower = np.array([94, 80, 2], np.uint8)
    blue_upper = np.array([120, 255, 255], np.uint8)
    blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper)
    
    # orange
    orange_lower = np.array([5, 150, 150], np.uint8)
    orange_upper = np.array([15, 255, 255], np.uint8)
    orange_mask = cv2.inRange(hsvFrame, orange_lower, orange_upper)
    
    # yellow
    yellow_lower = np.array([25, 150, 150], np.uint8)
    yellow_upper = np.array([35, 255, 255], np.uint8)
    yellow_mask = cv2.inRange(hsvFrame, yellow_lower, yellow_upper)
    
    # purple
    purple_lower = np.array([130, 50, 50], np.uint8)
    purple_upper = np.array([160, 255, 255], np.uint8)
    purple_mask = cv2.inRange(hsvFrame, purple_lower, purple_upper)
    

    # Dilate the masks
    red_mask = cv2.dilate(red_mask, kernel)
    green_mask = cv2.dilate(green_mask, kernel)
    blue_mask = cv2.dilate(blue_mask, kernel)
    orange_mask = cv2.dilate(orange_mask, kernel)
    yellow_mask = cv2.dilate(yellow_mask, kernel)
    purple_mask = cv2.dilate(purple_mask, kernel)

    # Apply bitwise AND to extract colored regions
    res_red = cv2.bitwise_and(frame, frame, mask=red_mask)
    res_green = cv2.bitwise_and(frame, frame, mask=green_mask)
    res_blue = cv2.bitwise_and(frame, frame, mask=blue_mask)
    res_orange = cv2.bitwise_and(frame, frame, mask=orange_mask)
    res_yellow = cv2.bitwise_and(frame, frame, mask=yellow_mask)
    res_purple = cv2.bitwise_and(frame, frame, mask=purple_mask)

    # Detect and draw contours for each color
    def draw_contours(mask, color_name, color_bgr):
        global last_log_time
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color_bgr, 2)
                cv2.putText(frame, f"{color_name} Colour", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_bgr, 2)

        # Only log once every 10 seconds
        if time.time() - last_log_time > 5:
            with open("colors.txt", "a") as color_log:
                color_log.write(color_name + "\n")
            last_log_time = time.time()

    draw_contours(red_mask, "Red", (0, 0, 150))
    draw_contours(green_mask, "Green", (0, 255, 0))
    draw_contours(blue_mask, "Blue", (255, 0, 0))
    draw_contours(yellow_mask, "Yellow", (0, 255, 255))
    draw_contours(orange_mask, "Orange", (10, 90, 190))
    draw_contours(purple_mask, "Purple", (64, 0, 64))

    # Show the output frame
    cv2.imshow("Multiple Color Detection in Real-Time", frame)

    # Wait for key press for exit
    if cv2.waitKey(1) & 0xFF == ord('b'):
        pilot.streamoff()
        cv2.destroyAllWindows()
        break

    # Delay to limit the frame rate (~30 FPS)
    time.sleep(0.03)

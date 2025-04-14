import cv2
import numpy as np
from djitellopy import tello

# Connect to Tello
pilot = tello.Tello()
pilot.connect()

# Start video stream
pilot.streamon()
frame_read = pilot.get_frame_read()

# Define HSV ranges for multiple colors
color_ranges = {
    'red': ((0, 120, 70), (10, 255, 255)),
    'green': ((36, 50, 70), (89, 255, 255)),
    'blue': ((90, 60, 70), (128, 255, 255)),
    'yellow': ((20, 100, 100), (30, 255, 255)),
    'orange': ((10, 100, 100), (25, 255, 255)),
    'purple': ((129, 50, 30), (158, 255, 120)),
}

# Corresponding display colors (BGR)
display_colors = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'yellow': (0, 255, 255),
    'orange': (0, 165, 255),
    'purple': (128, 0, 128),
}

while True:
    frame = frame_read.frame
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for color_name, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 50:
                x, y, w, h = cv2.boundingRect(cnt)
                padding = 10
                cv2.rectangle(frame, 
                (x - padding, y - padding), 
                (x + w + padding, y + h + padding), 
                display_colors[color_name], 
                2)
                cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, display_colors[color_name], 2)
                
                if 'red' not in color_log:
                    with open("colors.txt", "a") as log:
                        color_log.write(f"RED\n")
                        color_log.add("green")
                
                # Open file to save detected color names
                color_log = open("colors.txt", "a")
                # Write to file
                color_log.write(color_name + "\n")
                file = open("colors.txt", "r")
                print(file.read())

    cv2.imshow("Color Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

color_log.close()
pilot.streamoff()
cv2.destroyAllWindows()

# Circle detection for hoops

while True:
    frame = pilot.get_frame_read().frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 5)
    cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 0, 0), -1)

    cv2.imshow("Tello Circle Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
cv2.destroyAllWindows()
pilot.streamoff()


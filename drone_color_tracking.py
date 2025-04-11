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
    'red1': ((0, 120, 70), (10, 255, 255)),
    'red2': ((170, 120, 70), (180, 255, 255)),
    'green': ((36, 50, 70), (89, 255, 255)),
    'blue': ((90, 60, 70), (128, 255, 255)),
    'yellow': ((20, 100, 100), (30, 255, 255)),
}

# Corresponding display colors (BGR)
display_colors = {
    'red1': (0, 0, 255),
    'red2': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'yellow': (0, 255, 255),
}

while True:
    frame = frame_read.frame
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for color_name, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), display_colors[color_name], 2)
                cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, display_colors[color_name], 2)

    cv2.imshow("Color Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

pilot.streamoff()
cv2.destroyAllWindows()

# Some code to recognize circles for capturing focus on the hoops

while True:
    frame = pilot.get_frame_read().frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 5)

    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
        param1=50, param2=30, minRadius=10, maxRadius=200
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

    cv2.imshow("Tello Circle Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
pilot.streamoff()

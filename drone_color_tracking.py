import numpy as np
import cv2
import time
import djitellopy as tello

# Connect to Tello
pilot = tello.Tello()

try:
    pilot.connect()
    pilot.streamon()
except Exception as e:
    print(f"Failed to connect to Tello: {e}")
    exit()

frame_reader = pilot.get_frame_read()
kernel = np.ones((5, 5), "uint8")
last_log_time = time.time()

HISTORY = 1000
VAR_THRESHOLD = 100
DETECT_SHADOWS = False

def create_bg_subtractor():

    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history = HISTORY, 
        varThreshold = VAR_THRESHOLD, 
        detectShadows = DETECT_SHADOWS
    )
    
    return bg_subtractor

bg_subtractor = create_bg_subtractor()

colors = [
    {
        "name": "Red",
        "bgr": (60, 30, 235),
        "ranges": [
            (np.array([0, 120, 70]), np.array([10, 255, 255])),
            (np.array([170, 120, 70]), np.array([180, 255, 255]))
        ]
    },
    {
        "name": "Green",
        "bgr": (0, 255, 0),
        "ranges": [(np.array([36, 100, 100]), np.array([86, 255, 255]))]
    },
    {
        "name": "Blue",
        "bgr": (255, 0, 0),
        "ranges": [(np.array([94, 80, 2]), np.array([120, 255, 255]))]
    },
    {
        "name": "Yellow",
        "bgr": (0, 255, 255),
        "ranges": [(np.array([25, 150, 150]), np.array([35, 255, 255]))]
    },
    {
        "name": "Orange",
        "bgr": (10, 90, 190),
        "ranges": [(np.array([10, 150, 150]), np.array([30, 255, 255]))]
    },
    {
        "name": "Purple",
        "bgr": (64, 0, 64),
        "ranges": [(np.array([130, 50, 50]), np.array([160, 255, 255]))]
    }
]

while True:
    frame = frame_reader.frame
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    fg_mask = bg_subtractor.apply(frame)

    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.dilate(fg_mask, kernel)

    black_background = np.zeros_like(frame)

    for color in colors:
        
        full_mask = None
        for lower, upper in color["ranges"]:
            mask = cv2.inRange(hsvFrame, lower, upper)
            full_mask = mask if full_mask is None else full_mask | mask

        full_mask = cv2.dilate(full_mask, kernel)

        foreground_color_mask = cv2.bitwise_and(full_mask, fg_mask)

        contours, _ = cv2.findContours(foreground_color_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color["bgr"], 2)
                cv2.putText(frame, f"{color['name']} Colour", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color["bgr"], 2)

                if time.time() - last_log_time > 10:
                    with open("colors.txt", "a") as color_log:
                        color_log.write(color["name"] + "\n")
                    last_log_time = time.time()

        color_region = cv2.bitwise_and(frame, frame, mask=foreground_color_mask)
        black_background = cv2.add(black_background, color_region)

    cv2.imshow("Color Detection", black_background)

    if cv2.waitKey(1) & 0xFF == ord('b'):
        
        pilot.streamoff()
        cv2.destroyAllWindows()
        break

    time.sleep(0.03)

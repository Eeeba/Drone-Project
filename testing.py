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

frame_reader = pilot.get_frame_read()
kernel = np.ones((5, 5), "uint8")
last_log_time = time.time()

# Initialize background subtractor
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

# Define colors and ranges
colors = [
    {
        "name": "Red",
        "bgr": (0, 0, 150),
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
        "ranges": [(np.array([5, 150, 150]), np.array([15, 255, 255]))]
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

    # Apply background subtraction to create the foreground mask
    fg_mask = bg_subtractor.apply(frame)

    # Optional: clean up foreground mask (removes small noise or shadow)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.dilate(fg_mask, kernel)

    # Create a black background for the output
    black_background = np.zeros_like(frame)

    for color in colors:
        # Combine color masks
        full_mask = None
        for lower, upper in color["ranges"]:
            mask = cv2.inRange(hsvFrame, lower, upper)
            full_mask = mask if full_mask is None else full_mask | mask

        # Dilate the mask to reduce noise
        full_mask = cv2.dilate(full_mask, kernel)

        # Apply the foreground mask to the color mask (keep only foreground objects)
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

        # Add detected colored regions to the black background
        color_region = cv2.bitwise_and(frame, frame, mask=foreground_color_mask)
        black_background = cv2.add(black_background, color_region)

    # Show the output frame with black background
    cv2.imshow("Tello Color Detection with Blacked-Out Background", black_background)

    # Optional: view the foreground mask for debugging
    # cv2.imshow("Foreground Mask", fg_mask)

    if cv2.waitKey(1) & 0xFF == ord('b'):
        pilot.streamoff()
        cv2.destroyAllWindows()
        break

    time.sleep(0.03)

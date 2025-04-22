import cv2
import numpy as np
import pygame
import time
from djitellopy import Tello

S = 60
FPS = 30

class TelloColorGUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tello Color Detection Control")
        self.screen = pygame.display.set_mode([960, 720])
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)

        self.tello = Tello()
        self.tello.connect()
        self.tello.set_speed(10)
        self.tello.streamoff()
        self.tello.streamon()

        self.frame_reader = self.tello.get_frame_read()

        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.send_rc_control = False
        self.running = True
        self.last_log_time = time.time()

        self.kernel = np.ones((5, 5), "uint8")

        self.colors = [
            {"name": "Red", "bgr": (60, 30, 235), "ranges": [(np.array([0, 120, 70]), np.array([10, 255, 255])),
                                                             (np.array([170, 120, 70]), np.array([180, 255, 255]))]},
            {"name": "Green", "bgr": (0, 255, 0), "ranges": [(np.array([36, 100, 100]), np.array([86, 255, 255]))]},
            {"name": "Blue", "bgr": (255, 0, 0), "ranges": [(np.array([100, 150, 100]), np.array([130, 255, 255]))]},
            {"name": "Yellow", "bgr": (0, 255, 255), "ranges": [(np.array([25, 200, 200]), np.array([35, 255, 255]))]},
            {"name": "Orange", "bgr": (10, 90, 190), "ranges": [(np.array([10, 150, 150]), np.array([30, 255, 255]))]},
            {"name": "Purple", "bgr": (64, 0, 64), "ranges": [(np.array([130, 50, 50]), np.array([160, 255, 255]))]}
        ]

        self.selected_color_idx = 0  # Default to first color (Red)

    def process_color_detection(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        black_background = np.zeros_like(frame)

        color = self.colors[self.selected_color_idx]  # Only process selected color

        full_mask = None
        for lower, upper in color["ranges"]:
            mask = cv2.inRange(hsv, lower, upper)
            full_mask = mask if full_mask is None else full_mask | mask

        full_mask = cv2.dilate(full_mask, self.kernel)
        contours, _ = cv2.findContours(full_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(black_background, (x, y), (x + w, y + h), color["bgr"], 2)
                cv2.putText(black_background, f"{color['name']}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color["bgr"], 2)
                if time.time() - self.last_log_time > 20:
                    with open("colors.txt", "a") as f:
                        f.write(f"{color['name']}\n")
                    self.last_log_time = time.time()

        color_region = cv2.bitwise_and(frame, frame, mask=full_mask)
        black_background = cv2.add(black_background, color_region)

        return black_background

    def update(self):
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity,
                                       self.up_down_velocity, self.yaw_velocity)

    def keydown(self, key):
        if key == pygame.K_UP: self.for_back_velocity = S
        elif key == pygame.K_DOWN: self.for_back_velocity = -S
        elif key == pygame.K_LEFT: self.left_right_velocity = -S
        elif key == pygame.K_RIGHT: self.left_right_velocity = S
        elif key == pygame.K_w: self.up_down_velocity = S
        elif key == pygame.K_s: self.up_down_velocity = -S
        elif key == pygame.K_a: self.yaw_velocity = -S
        elif key == pygame.K_d: self.yaw_velocity = S
        elif key == pygame.K_t:
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:
            self.tello.land()
            self.send_rc_control = False
        elif key == pygame.K_f:
            self.tello.flip('b')
            time.sleep(2)
        elif key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
            self.selected_color_idx = key - pygame.K_1
            print(f"[INFO] Switched to color: {self.colors[self.selected_color_idx]['name']}")

    def keyup(self, key):
        if key in [pygame.K_UP, pygame.K_DOWN]: self.for_back_velocity = 0
        elif key in [pygame.K_LEFT, pygame.K_RIGHT]: self.left_right_velocity = 0
        elif key in [pygame.K_w, pygame.K_s]: self.up_down_velocity = 0
        elif key in [pygame.K_a, pygame.K_d]: self.yaw_velocity = 0

    def run(self):
        print("[INFO] Starting Tello Color Detection GUI")
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            frame = self.frame_reader.frame
            processed = self.process_color_detection(frame.copy())

            battery = self.tello.get_battery()
            cv2.putText(processed, f"Battery: {battery}%", (5, 700),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
            processed = np.rot90(processed)
            processed = np.flipud(processed)
            surface = pygame.surfarray.make_surface(processed)

            self.screen.blit(surface, (0, 0))
            pygame.display.update()

        self.shutdown()

    def shutdown(self):
        print("[INFO] Shutting down...")
        self.tello.streamoff()
        self.tello.end()
        pygame.quit()


def main():
    gui = TelloColorGUI()
    gui.run()

if __name__ == "__main__":
    main()

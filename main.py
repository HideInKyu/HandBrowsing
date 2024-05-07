#! /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
import cv2
from cvzone.HandTrackingModule import HandDetector
import csv
import os
import time

class GestureState:
    def handle(self, context, landmarks, hand_type):
        pass

class NoGestureState(GestureState):
    def handle(self, context, landmarks, hand_type):
        context.detect_gesture(landmarks, hand_type)

class PinchState(GestureState):
    def __init__(self):
        self.start_position = None
        self.gesture_id = None
        self.is_dragging = False
        self.last_position = None

    def handle(self, context, landmarks, hand_type):
        current_position = {i: (landmarks[i][0], landmarks[i][1]) for i in range(21)}
        thumb_to_index = context.calculate_distance(landmarks[4], landmarks[8])
        
        if thumb_to_index >= context.pinchDist:
            if self.start_position:
                if self.is_dragging:
                    context.handle_gesture('Pinch and Drag', self.gesture_id, 'release', self.last_position, hand_type)
                else:
                    context.handle_gesture('Pinch', self.gesture_id, 'release', self.last_position, hand_type)
                context.state = NoGestureState()
        else:
            if self.start_position is None:
                self.start_position = current_position
                self.gesture_id = context.next_gesture_id()
                self.last_position = current_position
                context.handle_gesture('Pinch', self.gesture_id, 'start', self.start_position, hand_type)
                print(f"Pinch{self.gesture_id} Detected by {hand_type}")
            else:
                movement_direction = context.get_movement_direction(self.start_position[8], current_position[8])
                if movement_direction and not self.is_dragging:
                    print(f"Pinch and Drag {movement_direction} Detected by {hand_type}")
                    context.handle_gesture('Pinch and Drag', self.gesture_id, movement_direction, self.start_position, hand_type)
                    self.is_dragging = True
                self.last_position = current_position

class GestureContext:
    def __init__(self):
        self.state = NoGestureState()
        self.pinchDist = 45
        self.detector = HandDetector(maxHands=2, detectionCon=0.8)
        self.gesture_counter = 0
        self.setup_csv()

    def setup_csv(self):
        self.csv_file_path = 'detailed_gesture_data.csv'
        self.file_exists = os.path.isfile(self.csv_file_path)
        self.csv_file = open(self.csv_file_path, 'a', newline='')
        self.writer = csv.writer(self.csv_file)
        if not self.file_exists:
            self.writer.writerow([
                'time_stamp', 'hand_type', 'gesture_id', 'gesture_name', 'gesture_phase', 'wrist_x', 'wrist_y',
                'thumb_x', 'thumb_y', 'index_x', 'index_y', 'middle_x', 'middle_y',
                'ring_x', 'ring_y', 'pinky_x', 'pinky_y'
            ])

    def calculate_distance(self, point1, point2):
        return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) ** 0.5

    def handle_gesture(self, gesture_name, gesture_id, phase, positions, hand_type):
        row = [time.time(), hand_type, gesture_id, gesture_name, phase]
        for i in range(21):
            row.extend([positions[i][0], positions[i][1]])
        self.writer.writerow(row)

    def detect_gesture(self, landmarks, hand_type):
        thumb_to_index = self.calculate_distance(landmarks[4], landmarks[8])
        if thumb_to_index < self.pinchDist and isinstance(self.state, NoGestureState):
            self.state = PinchState()

    def next_gesture_id(self):
        self.gesture_counter += 1
        return self.gesture_counter

    def process_frame(self, landmarks, hand_type):
        self.state.handle(self, landmarks, hand_type)

    def get_movement_direction(self, start_pos, current_pos):
        dx, dy = current_pos[0] - start_pos[0], current_pos[1] - start_pos[1]
        if abs(dx) > 20 or abs(dy) > 20:  # Threshold to determine significant movement
            if abs(dx) > abs(dy):
                return 'left' if dx > 0 else 'right'
            else:
                return 'up' if dy < 0 else 'down'
        return None

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
context = GestureContext()

while True:
    success, img = cap.read()
    if not success:
        continue

    hands, img = context.detector.findHands(img)
    if hands:
        for hand in hands:
            context.process_frame(hand['lmList'], hand['type'])

    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
context.csv_file.close()

#! /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
import cv2
import time
from cvzone.HandTrackingModule import HandDetector
import keyboard

# Function to calculate distance between two points
def calculate_distance(pt1, pt2):
    return ((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)**0.5

# Initialize variables
movement_threshold = 0
stability_count = 0
stable_frames_required = 0
last_position = None
pinch_threshold = 40  # Threshold for considering a pinch
double_click_timeout = 0.4  # Time threshold for double click
hold_timeout = 0.4  # Time threshold to detect holding
last_pinch_time = 0
pinch_count = 0
pinch_released = True
is_holding = False
single_click_pending = False
single_click_time = 0

# Define an alias for the 'f' key
keyboard.add_abbreviation('f', 'f')
keyboard.add_abbreviation('@@n@@', 'shift+n')

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Hand Detector
detector = HandDetector(maxHands=1, detectionCon=0.8)

while True:
    # Get the frame from the webcam
    success, img = cap.read()

    # Hands
    hands, img = detector.findHands(img)

    current_time = time.time()
    if hands:
        hand = hands[0]
        lmList = hand['lmList']
        wrist_point = lmList[0]
        hand_type = hand['type']

        if last_position:
            movement = calculate_distance(wrist_point, last_position)
            if movement < movement_threshold:
                stability_count += 1
            else:
                stability_count = 0
        last_position = wrist_point

        thumb_tip = lmList[4]
        index_tip = lmList[8]
        distance = calculate_distance(thumb_tip, index_tip)

        # Manage pinch detection
        if distance < pinch_threshold and stability_count >= stable_frames_required:
            if pinch_released:
                if current_time - last_pinch_time < double_click_timeout:
                    if single_click_pending:
                        if hand_type == 'Right':
                            keyboard.press_and_release('right')  # Right hand double pinch
                            print(f"{hand_type} hand double pinch -> Right Arrow")
                        else:
                            keyboard.press_and_release('left')  # Left hand double pinch
                            print(f"{hand_type} hand double pinch -> Left Arrow")
                        single_click_pending = False
                    pinch_count = 0
                else:
                    single_click_pending = True
                    single_click_time = current_time
                last_pinch_time = current_time
                pinch_released = False
            if current_time - last_pinch_time > hold_timeout and not is_holding:
                if hand_type == 'Right':
                    keyboard.press_and_release('command+right')  # Left hand hold click
                    print(f"{hand_type} hand hold click -> 'command+right'")
                else:
                    keyboard.press_and_release('command+left')  # Left hand hold click
                    print(f"{hand_type} hand hold click -> Command+Left")
                is_holding = True
                single_click_pending = False  # Ensure no single click is processed
        else:
            if not pinch_released:
                if is_holding:
                    if hand_type == 'Right':
                        print(f"{hand_type} hand is not pinching")
                    else:
                        print(f"{hand_type} hand is not pinching")
                    is_holding = False
                elif pinch_count == 1 and not is_holding:
                    if hand_type == 'Right':
                        keyboard.press_and_release('space')  # Right hand single click
                        print(f"{hand_type} hand single click -> Space")
                    else:
                        keyboard.write('f')  # Left hand single click using alias
                        print(f"{hand_type} hand single click -> 'F'")
                    pinch_count = 0
                pinch_released = True
    else:
        last_position = None
        stability_count = 0

    # Process pending single click only if not holding
    if single_click_pending and current_time - single_click_time > double_click_timeout and not is_holding:
        if hand_type == 'Right':
            keyboard.press_and_release('space')  # Right hand single click
            print(f"{hand_type} hand single click -> Space")
        else:
            keyboard.write('f')  # Left hand single click using alias
            print(f"{hand_type} hand single click -> 'F'")
        single_click_pending = False

    cv2.imshow("Image", img)
    # Check for 'q' key press
    if cv2.waitKey(1) == ord('q'):
        break

# Release the webcam and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()

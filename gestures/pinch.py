#! /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
import cv2
import mediapipe as mp
import time

# Function to calculate distance between two points
def calculate_distance(pt1, pt2):
    return ((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)**0.5

# Initialize variables
movement_threshold = 0  # Threshold for detecting movement (unused in this context)
stability_count = 0  # Counter to ensure stability before detecting a gesture
stable_frames_required = 0  # Number of stable frames required before detecting a gesture
last_position = None  # Last known position of the hand
pinch_threshold = 40  # Threshold for considering a pinch (in pixels, may need to adjust)
double_click_timeout = 0.4  # Time threshold for double click
hold_timeout = 0.4  # Time threshold to detect holding
last_pinch_time = 0  # Last time a pinch was detected
pinch_released = True  # Flag to check if pinch was released
is_holding = False  # Flag to check if holding
single_click_pending = False  # Flag to check if a single click is pending
single_click_time = 0  # Time when a single click was detected

# MediaPipe hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.8)
mp_drawing = mp.solutions.drawing_utils

# Webcam setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

while True:
    # Get the frame from the webcam
    success, img = cap.read()

    # Convert the image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    current_time = time.time()
    
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        wrist_point = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

        wrist_coords = (wrist_point.x * img.shape[1], wrist_point.y * img.shape[0])
        thumb_coords = (thumb_tip.x * img.shape[1], thumb_tip.y * img.shape[0])
        index_coords = (index_tip.x * img.shape[1], index_tip.y * img.shape[0])

        if last_position:
            movement = calculate_distance(wrist_coords, last_position)
            if movement < movement_threshold:
                stability_count += 1
            else:
                stability_count = 0
        last_position = wrist_coords

        distance = calculate_distance(thumb_coords, index_coords)

        # Manage pinch detection
        if distance < pinch_threshold and stability_count >= stable_frames_required:
            if pinch_released:
                if current_time - last_pinch_time < double_click_timeout:
                    # Double pinch detected
                    print("Double pinch detected")
                    single_click_pending = False
                else:
                    single_click_pending = True
                    single_click_time = current_time
                last_pinch_time = current_time
                pinch_released = False
            if current_time - last_pinch_time > hold_timeout and not is_holding:
                # Holding detected
                print("Hold detected")
                is_holding = True
                single_click_pending = False  # Ensure no single click is processed
        else:
            if not pinch_released:
                if is_holding:
                    print("Released hold")
                    is_holding = False
                elif single_click_pending:
                    if current_time - single_click_time > double_click_timeout:
                        # Single pinch detected
                        print("Single pinch detected")
                        single_click_pending = False
                pinch_released = True
    else:
        last_position = None
        stability_count = 0

    # Process pending single click only if not holding
    if single_click_pending and current_time - single_click_time > double_click_timeout and not is_holding:
        print("Single pinch detected")
        single_click_pending = False

    # Draw hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Image", img)
    # Check for 'q' key press
    if cv2.waitKey(1) == ord('q'):
        break

# Release the webcam and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()

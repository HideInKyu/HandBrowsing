#! /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
import cv2
import mediapipe as mp

from models.model import GestureRecognizer
from views.view import display_frame

from gestures.clap import ClapGesture
from gestures.close_hand import CloseHandGesture
from gestures.hand_movement import HandMovement
from gestures.hand_rotation import HandRotation
from gestures.open_hand import OpenHandGesture
from gestures.pinch_pull import PinchPullGesture
from gestures.pinch import PinchGesture
from gestures.prayer import PrayerGesture
from gestures.pronation_lower import PronationLowerGesture
from gestures.supination_raise import SupinationRaiseGesture
from gestures.swipe import SwipeGesture
from gestures.two_finger_swipe import TwoFingerSwipeGesture

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

cap = cv2.VideoCapture(0)  # Capture video from camera

with hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue
        
        # Flip the image horizontally for a later selfie-view display
        # Convert the BGR image to RGB
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # Process the image and detect hands
        results = hands.process(image)

        # Draw the hand annotations on the image
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()

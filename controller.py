#! /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
import sys
import os
import cv2
import mediapipe as mp

from gestures.pinch import PinchGesture

class HandGestureController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
        self.gestures = [
            PinchGesture(),
            # Add other gesture recognizers here
        ]
        self.cap = cv2.VideoCapture(0)  # Capture video from camera

    def process_frame(self, frame):
        frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(frame_bgr, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                # Detect gestures
                for gesture in self.gestures:
                    if gesture.detect(hand_landmarks):
                        cv2.putText(frame_bgr, gesture.__class__.__name__, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        return frame_bgr

    def run(self):
        with self.hands:
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    continue

                processed_frame = self.process_frame(frame)
                cv2.imshow('Hand Gesture Recognition', processed_frame)

                if cv2.waitKey(5) & 0xFF == 27:
                    break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    controller = HandGestureController()
    controller.run()

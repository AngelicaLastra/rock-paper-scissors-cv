import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import random
import math
import os
import sys
import time

MODEL_PATH = "./hand_landmarker.task"

current_gesture = None
current_hand_landmarks = None

def distance(a, b):
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

def print_result(result, output_image, timestamp_ms):
    global current_gesture, current_hand_landmarks

    if not result.hand_landmarks:
        current_gesture = None
        current_hand_landmarks = None
        return

    landmarks = result.hand_landmarks[0]
    current_hand_landmarks = landmarks
    wrist = landmarks[0]

    index_extended  = distance(landmarks[8],  wrist) > distance(landmarks[6],  wrist)
    middle_extended = distance(landmarks[12], wrist) > distance(landmarks[10], wrist)
    ring_extended   = distance(landmarks[16], wrist) > distance(landmarks[14], wrist)
    pinky_extended  = distance(landmarks[20], wrist) > distance(landmarks[18], wrist)

    if not index_extended and not middle_extended and not ring_extended and not pinky_extended:
        current_gesture = "rock"
    elif index_extended and middle_extended and not ring_extended and not pinky_extended:
        current_gesture = "scissors"
    elif index_extended and middle_extended and ring_extended and pinky_extended:
        current_gesture = "paper"
    else:
        current_gesture = None


def play_game(player_choice):
    rules = {
        'rock': 'scissors',
        'paper': 'rock',
        'scissors': 'paper'
    }

    pc_choice = random.choice(list(rules.keys()))

    if player_choice == pc_choice:
        result = "It's a tie!"
        color = (255, 255, 0)   # yellow
    elif rules[player_choice] == pc_choice:
        result = "You win!"
        color = (0, 255, 0)     # green
    else:
        result = "PC wins!"
        color = (0, 0, 255)     # red

    return pc_choice, result, color


def main():
    global current_gesture, current_hand_landmarks

    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at '{MODEL_PATH}'")
        print("Download it from: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models")
        sys.exit(1)

    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        result_callback=print_result
    )

    landmarker = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        print("Make sure a camera is connected and not in use by another application.")
        sys.exit(1)

    timestamp_ms = 0
    game_active = True
    pc_choice = None
    outcome = None
    outcome_color = (255, 255, 255)
    player_final = None
    countdown_end = None

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            if countdown_end is None:
                print("Get ready! Show your hand in 3... 2... 1...")
                countdown_end = time.time() + 3

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            landmarker.detect_async(mp_image, timestamp_ms)
            timestamp_ms += 33

            remaining = math.ceil(countdown_end - time.time())

            if remaining > 0:
                cv2.putText(frame, str(remaining), (300, 250),
                            cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 5)

            elif game_active:
                if current_gesture:
                    player_final = current_gesture
                    pc_choice, outcome, outcome_color = play_game(player_final)
                    game_active = False
                else:
                    cv2.putText(frame, "Show your gesture!", (50, 250),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)

            # Display Results on Screen
            if not game_active and outcome:
                cv2.putText(frame, f"You: {player_final}",  (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
                cv2.putText(frame, f"PC:  {pc_choice}",     (50, 180),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 100, 0), 3)
                cv2.putText(frame, outcome,                  (50, 280),
                            cv2.FONT_HERSHEY_SIMPLEX, 2,   outcome_color, 4)
                cv2.putText(frame, "Press R to play again",  (50, 420),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,   (200, 200, 200), 2)

            # Show live gesture label during countdown
            if game_active and current_gesture:
                cv2.putText(frame, current_gesture, (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            # Draw hand landmarks
            if current_hand_landmarks:
                h, w, _ = frame.shape
                HAND_CONNECTIONS = [
                    (0,1),(1,2),(2,3),(3,4),
                    (0,5),(5,6),(6,7),(7,8),
                    (0,9),(9,10),(10,11),(11,12),
                    (0,13),(13,14),(14,15),(15,16),
                    (0,17),(17,18),(18,19),(19,20),
                    (5,9),(9,13),(13,17),
                ]
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in current_hand_landmarks]
                for i, j in HAND_CONNECTIONS:
                    cv2.line(frame, pts[i], pts[j], (255, 255, 255), 1)
                for pt in pts:
                    cv2.circle(frame, pt, 5, (0, 0, 255), -1)

            cv2.imshow("Rock Paper Scissors", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:       # Escape to quit
                break
            elif key == ord('r') and not game_active:   # R to play again
                countdown_end = time.time() + 3
                game_active = True
                pc_choice = None
                outcome = None
                player_final = None
                print("\nGet ready! Show your hand in 3... 2... 1...")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

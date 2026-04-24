import cv2
import mediapipe as mp
import time
import math

def main():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not access the camera.")
        return
    
    # Set resolution to 1280x720
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_draw = mp.solutions.drawing_utils

    # FPS calculation
    fps = 0.0
    prev_time = time.time()

    print("Press 'q' to quit.")
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                print("kpt num: ", hand_landmarks)

        # Display FPS
        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time)
        prev_time = curr_time
        fps_text = f"FPS: {fps:.2f}"
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Gesture Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

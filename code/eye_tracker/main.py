
import cv2
import mediapipe as mp
import math
import os
import pygame


# --- Configuration ---
EAR_THRESHOLD = 0.20  # You can adjust this value if your eyes aren't detecting properly.
CLOSED_FRAMES_THRESHOLD = 5  # Number of consecutive frames the eye must be closed to trigger the sound

def initialize_sound():
    sound_file = "fahhhhh.mp3"
    if not os.path.exists(sound_file):
        print(f"Error: '{sound_file}' not found! Please place your audio file in the project folder.")
        exit(1)
    
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)

def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def calculate_ear(landmarks, indices):
    """
    Computes the Eye Aspect Ratio (EAR) given an eye's landmarks.
    """
    # Horizontal distance
    h = distance(landmarks[indices[0]], landmarks[indices[1]])
    
    # Vertical distances
    v1 = distance(landmarks[indices[2]], landmarks[indices[4]])
    v2 = distance(landmarks[indices[3]], landmarks[indices[5]])
    
    if h == 0:
        return 0
    return (v1 + v2) / (2.0 * h)

def main():
    print("Initializing models and sound...")
    initialize_sound()
    
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    
    base_options = mp_python.BaseOptions(model_asset_path='face_landmarker.task')
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    detector = vision.FaceLandmarker.create_from_options(options)

    # Indices for Mediapipe Face Mesh landmarks
    # [Left corner, Right corner, Top 1, Top 2, Bottom 1, Bottom 2]
    LEFT_EYE = [33, 133, 159, 158, 145, 153]
    RIGHT_EYE = [362, 263, 386, 385, 374, 380]

    # Try modifying the webcam backend to DirectShow (CAP_DSHOW) for Windows
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    closed_frames = 0
    is_playing = False

    print("Ready! Looking for your eyes... Press 'q' to quit.")

    while True:
        success, image = cap.read()
        if not success:
            print("Failed to read frame from webcam.")
            break
        
        # Convert back and forth for mediapipe processing
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        results = detector.detect(mp_image)

        avg_ear = 0.0
        if getattr(results, 'face_landmarks', None):
            for face_landmarks in results.face_landmarks:
                left_ear = calculate_ear(face_landmarks, LEFT_EYE)
                right_ear = calculate_ear(face_landmarks, RIGHT_EYE)
                avg_ear = (left_ear + right_ear) / 2.0
                
                # Check if eyes are closed based on threshold
                if avg_ear < EAR_THRESHOLD:
                    closed_frames += 1
                else:
                    closed_frames = 0
                    if is_playing:
                        pygame.mixer.music.stop()
                        is_playing = False

                if closed_frames >= CLOSED_FRAMES_THRESHOLD:
                    if not is_playing:
                        pygame.mixer.music.play(-1) # Loop the sound indefinitely until eyes open again
                        is_playing = True
                    cv2.putText(image, "EYES CLOSED (Faaaahh!)", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # Show current ratio on screen
        cv2.putText(image, f"Eye Aspect Ratio: {avg_ear:.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.imshow('Faaahh Eye Tracker', image)

        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

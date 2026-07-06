import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import pyautogui
import math
import time

# Disable pyautogui failsafe if it causes issues, but normally leave it on
pyautogui.FAILSAFE = False

# --- Setup MediaPipe Hand Landmarker ---
base_options = mp_python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
detector = vision.HandLandmarker.create_from_options(options)

# Helper function
def get_distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

# Cooldown dictionary
cooldowns = {
    "pause": 0,
    "volume_up": 0,
    "screenshot": 0
}

# Cooldown delays (in seconds)
cooldown_delays = {
    "pause": 2.0,        # Don't trigger pause too fast
    "volume_up": 0.2,    # Can hold thumb up to increase volume gradually 
    "screenshot": 2.0    # Don't take 10 screenshots a second
}

def detect_gesture(landmarks):
    # Tip landmarks
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    # PIP landmarks
    index_pip = landmarks[6]
    middle_pip = landmarks[10]
    ring_pip = landmarks[14]
    pinky_pip = landmarks[18]
    
    # Are fingers extended?
    idx_ext = index_tip.y < index_pip.y
    mid_ext = middle_tip.y < middle_pip.y
    rng_ext = ring_tip.y < ring_pip.y
    pnk_ext = pinky_tip.y < pinky_pip.y
    
    # 1. OK / Circle (Screenshot): Thumb and Index close together, others extended
    if get_distance(thumb_tip, index_tip) < 0.05 and mid_ext and rng_ext and pnk_ext:
        return "screenshot"
        
    # 2. Thumb Up (Volume Up): Other fingers folded down, thumb pointing up
    if not idx_ext and not mid_ext and not rng_ext and not pnk_ext:
        # Check if thumb tip is above thumb joint AND above the folded index finger
        if thumb_tip.y < landmarks[3].y and thumb_tip.y < index_pip.y:
            return "volume_up"
            
    # 3. Open Hand (Pause/Play): All 4 fingers extended 
    if idx_ext and mid_ext and rng_ext and pnk_ext:
        # Ensure thumb is extended horizontally too (to avoid confusion with 'stop' vs 'five')
        # We can just return pause if all 4 fingers are up.
        return "pause"
        
    return "none"

# Open Webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("Hand Gesture Controller Started")
print("Press 'q' to quit.")

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to read frame.")
        break
        
    # Mirror the frame naturally
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Detect hands
    results = detector.detect(mp_image)
    
    gesture = "none"
    
    if getattr(results, 'hand_landmarks', None) and len(results.hand_landmarks) > 0:
        landmarks = results.hand_landmarks[0]
        
        # Draw some landmarks for visualization
        h, w, _ = frame.shape
        for lm in landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            
        gesture = detect_gesture(landmarks)
        
        # Execute Action
        current_time = time.time()
        if gesture != "none" and (current_time - cooldowns[gesture]) > cooldown_delays[gesture]:
            
            if gesture == "pause":
                print("Action: Play/Pause")
                pyautogui.press('playpause') # System media play/pause
                # Alternative: pyautogui.press('space') if using mainly YouTube
                
            elif gesture == "volume_up":
                print("Action: Volume Up")
                pyautogui.press('volumeup')
                
            elif gesture == "screenshot":
                print("Action: Screenshot")
                filename = f"screenshot_{int(current_time)}.png"
                pyautogui.screenshot(filename)
                print(f"Saved {filename}")
                
            # Update cooldown timer
            cooldowns[gesture] = current_time

    # UI display
    cv2.putText(frame, f"Gesture: {gesture.upper()}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.imshow("Gesture Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

import mediapipe as mp
import cv2
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

base_options = mp_python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    num_faces=1,
    output_face_blendshapes=True
)
detector = vision.FaceLandmarker.create_from_options(options)

# Need an image to get blendshapes
img = cv2.imread(r"C:\Users\darsh\code\eye_tracker\test.jpg") # Assuming we can just process an empty or random image
import numpy as np
img = np.zeros((100, 100, 3), dtype=np.uint8)
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
results = detector.detect(mp_image)
# Can't guarantee a face in a zero image...

import numpy as np

# Mediapipe Face Mesh landmarks for eyes
LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

def calculate_ear(eye_points):
    """
    Calculate the Eye Aspect Ratio (EAR)
    """
    if len(eye_points) < 6:
        return 0.0
        
    v1 = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
    v2 = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
    h = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
    
    if h == 0:
        return 0.0
        
    ear = (v1 + v2) / (2.0 * h)
    return ear

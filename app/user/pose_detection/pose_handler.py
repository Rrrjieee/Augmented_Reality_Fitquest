import numpy as np
import mediapipe as mp
from typing import Callable

def calculate_angle(a,b,c):
    a = np.array(a) # Shoulder
    b = np.array(b) # Hip
    c = np.array(c) # Knees
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle

def check_pose(image, ret_code: int, callback: Callable[[None], None], ideal_angle = 90) -> int:
    '''
    check_pose expects 1 argument for the callback parameter.
    '''
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        # Recolor image to RGB
        image.flags.writeable = False
        
        # Make detection
        results = pose.process(image)
        image.flags.writeable = True
        
        if results.pose_landmarks is None:
            return [ret_code, 0, ideal_angle]
        
        try:
            ret_code    = callback(results, ret_code)
        except:
            pass

    return [*ret_code, ideal_angle]
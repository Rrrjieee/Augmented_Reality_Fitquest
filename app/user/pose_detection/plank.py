import cv2
import mediapipe as mp
import numpy as np
from user.pose_detection.pose_handler import *
from user.pose_detection.return_code import ReturnCode

# Curl counter variables
stage = None

## Setup mediapipe instance
def check(image):
    ret_code    = ReturnCode.FAILURE
    # mp_drawing  = mp.solutions.drawing_utils
    mp_pose     = mp.solutions.pose
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        # Recolor image to RGB
        image.flags.writeable = False
        
        # Make detection
        results = pose.process(image)
        image.flags.writeable = True
        
        if results.pose_landmarks is None:
            return ret_code
        
        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            
            # Get coordinates
            shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
           
            hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            
            # Calculate angle number 1
            angle = calculate_angle(shoulder, elbow, wrist)
            # Calculate angle number 2
            angle2 = calculate_angle(hip, knee, ankle)

            # print(angle)
            # plank counter logic
            if angle < 90:
                stage = "adjust your arms"
    
                if angle2 < 170:
                    stage       ="lower your hip position"
                elif angle2 >= 170:
                    stage       ="down" 
                    ret_code    = ReturnCode.SUCCESS
                # print(counter)

        except:
            pass

    return ret_code
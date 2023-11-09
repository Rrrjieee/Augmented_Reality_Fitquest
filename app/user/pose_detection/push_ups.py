import cv2
import mediapipe as mp
import numpy as np
from user.pose_detection.pose_handler import *
from user.pose_detection.return_code import ReturnCode

# Curl counter variables
counter = 0 
stage = None
ave = 0
inside = 161

def check(image) -> int:
    ret_code    = ReturnCode.FAILURE
    mp_pose     = mp.solutions.pose
    def on_push_ups(results, ret_code):
        global counter, stage, ave, inside
        landmarks   = results.pose_landmarks.landmark
        
        # Get coordinates
        shoulder    = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow       = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wrist       = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        hip         = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        knee        = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        ankle       = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
        
        # Calculate angle
        angle       = calculate_angle(shoulder, elbow, wrist)
        
        angle2      = calculate_angle(hip, knee, ankle)
        
        # push-up counter logic
        if angle <= 70:
            stage = "down"      
        elif stage =='down' and angle >= 160:
            stage       = "up"
            if angle2 < 160 and angle2 < 180:
                stage   = "wrong"
            else: 
                ret_code    = ReturnCode.SUCCESS    
        #    print(counter)
        if stage == 'up' and angle < 160:
            ave    += inside
            inside  = 161
            stage   = "down"
    
        return [ret_code, ave]
    
    return check_pose(image, ret_code, on_push_ups, 160)
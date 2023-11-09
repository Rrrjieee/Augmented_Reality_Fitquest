import cv2
import mediapipe as mp
import numpy as np
from user.pose_detection.pose_handler import *
from user.pose_detection.return_code import ReturnCode

# Curl counter variables
stage   = None
ave     = 0
inside  = 31

## Setup mediapipe instance
def check(image):
    ret_code    = ReturnCode.FAILURE
    mp_pose     = mp.solutions.pose
    def on_bicep_curl(results, ret_code):
        global stage, ave, inside
        landmarks = results.pose_landmarks.landmark
            
        # Get coordinates
        shoulder    = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow       = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wrist       = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        
        # Calculate angle
        angle = calculate_angle(shoulder, elbow, wrist)

        # Curl counter logic
        if angle > 160:
            stage = "down"
        if angle < 30 and stage =='down':
            stage = "up"
            ret_code    = ReturnCode.SUCCESS
            if inside > angle:
                inside = angle
        if angle > 30 and stage == 'up':
            ave += inside
            inside  = 31
            stage   = "down"
            
        return [ret_code, angle]
    
    return check_pose(image, ret_code, on_bicep_curl, 30)
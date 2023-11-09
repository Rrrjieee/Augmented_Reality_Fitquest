import cv2
import mediapipe as mp
import numpy as np
from user.pose_detection.pose_handler import *
from user.pose_detection.return_code import ReturnCode

# Curl counter variables
stage       = None
inside      = 31
ave         = 0

## Setup mediapipe instance
def check(image) -> int:
    ret_code    = ReturnCode.FAILURE
    mp_pose     = mp.solutions.pose
    def on_sit_ups(results, ret_code):
        global stage, ave, inside
        landmarks   = results.pose_landmarks.landmark
        
        # Get coordinates
        shoulder    = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        hip         = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        knee        = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        
        # Calculate angle
        angle = calculate_angle(shoulder, hip, knee)
        
        # Visualize angle
        cv2.putText(image, str(angle), 
                    tuple(np.multiply(hip, [640, 480]).astype(int)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                            )
        
        #print(angle)
        # Curl counter logic
        if angle > 120:
            stage       = "down"

        if angle < 30 and stage =='down':
            stage       = "up"
            if inside > angle:
                inside  = angle
            ret_code    = ReturnCode.SUCCESS

        if angle > 30 and stage == 'up':
            ave += inside
            inside      = 31
            stage       = "down"
            print(ave)   

        return [ret_code, angle]
    
    return check_pose(image, ret_code, on_sit_ups, 30)
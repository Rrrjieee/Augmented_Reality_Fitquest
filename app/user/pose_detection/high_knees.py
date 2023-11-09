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
    mp_pose     = mp.solutions.pose
    def on_high_knees(results, ret_code):
        landmarks = results.pose_landmarks.landmark
        global stage
        # Get coordinates
        hip = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        
        # Calculate angle
        angle = calculate_angle(hip, knee, ankle)
        
        # Visualize angle
        # cv2.putText(image, str(angle), 
        #               tuple(np.multiply(hip, [640, 480]).astype(int)), 
        #               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
        #                    )
        
        #print(angle)
        # Lunge counter logic
        if angle < 120:
            stage = "up"
        if stage =='up' and angle >150:
            stage="down"
            ret_code    = ReturnCode.SUCCESS
            # print(counter)
                    
        return [ret_code, angle]
        
    return check_pose(image, ret_code, on_high_knees, 150)
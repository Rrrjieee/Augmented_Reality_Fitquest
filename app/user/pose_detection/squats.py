import cv2
import mediapipe as mp
import numpy as np
from user.pose_detection.pose_handler import *
from user.pose_detection.return_code import ReturnCode


# Curl counter variables
counter = 0
stage = None
inside = 161
ave = 0


def check(image):
    ret_code = ReturnCode.FAILURE
    mp_pose = mp.solutions.pose

    def on_squat(results, ret_code):
        global counter, stage, inside, ave

        landmarks = results.pose_landmarks.landmark

        # Get coordinates
        hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
               landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # Calculate angle
        angle = calculate_angle(hip, knee, ankle)

        # print(angle)
        # squats counter logic
        if angle <= 90:
            stage = "down"
        if angle > 160 and stage == 'down':
            stage = "up"
            ret_code = ReturnCode.SUCCESS
            if inside > angle:
                inside = angle
        if angle < 161 and stage == 'up':
            ave += inside
            inside = 161
            stage = "down"

        return [ret_code, angle]

    return check_pose(image, ret_code, on_squat, 160)

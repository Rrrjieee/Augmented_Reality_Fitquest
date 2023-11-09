import cv2
import mediapipe as mp
import numpy as np

# import setup
from setup import setup_camera
from setup import process_image
from setup import recolor_image
from setup import get_coordinates
from setup import calculate_angle
from setup import display_angle
from setup import render_counter
from setup import render_detections

# import exercises counter logic
from all_exercises import curl
from all_exercises import pushup
from all_exercises import squats
from all_exercises import lunges
from all_exercises import plank
from all_exercises import situps
from all_exercises import high_knees
from all_exercises import glute_bridges

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Main function where the video capture and processing is handled
def main():
    cap = setup_camera()
    counter = 0 
    stage = None
    ave = 0


    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            image = process_image(frame)
            results = pose.process(image)
            image = recolor_image(image)

            try:
                landmarks = results.pose_landmarks.landmark
                shoulder, elbow, wrist = get_coordinates(landmarks)
                angle = calculate_angle(shoulder, elbow, wrist)
                display_angle(image, angle, elbow)
                print(ave)
                print(angle)
                stage, ave, counter = curl(angle, ave, stage, counter)
            except:
                pass

            render_counter(image, counter, stage)
            render_detections(image, results)
            
            cv2.imshow('Mediapipe Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# Run the main function
if __name__ == "__main__":
    main()
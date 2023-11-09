import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def update_frame():
    ret, frame = cap.read()

    if ret:
        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Make detection
        results = pose.process(image)

        # Recolor back to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates
            shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)

            # Visualize angle
            cv2.putText(image, str(angle),
                        tuple(np.multiply(elbow, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Curl counter logic
            if angle > 160:
                stage = "down"
            if angle < 30 and stage == 'down':
                stage = "up"
                counter += 1
                if inside > angle:
                    inside = angle
            if angle > 30 and stage == 'up':
                ave += inside
                inside = 31
                stage = "down"
                print(ave)

        except:
            pass

        # Render curl counter
        rep_label.config(text=f"REPS: {counter}")
        stage_label.config(text=f"STAGE: {stage}")

        # Convert the frame to display in the UI
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image=image)
        camera_frame_label.config(image=image)
        camera_frame_label.image = image  # Keep reference

    # Schedule the next update
    root.after(10, update_frame)

# Create the main UI window
root = tk.Tk()
root.title("Pose Estimation Counter")

# Create the video capture
cap = cv2.VideoCapture(0)

# Curl counter variables
counter = 0
stage = None
ave = 0
inside = 31

# Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    # Create labels for counter and stage
    rep_label = ttk.Label(root, text=f"REPS: {counter}", font=("Helvetica", 24))
    stage_label = ttk.Label(root, text=f"STAGE: {stage}", font=("Helvetica", 24))

    rep_label.pack()
    stage_label.pack()

    # Create a label for the camera frame
    camera_frame_label = ttk.Label(root)
    camera_frame_label.pack()

    # Start updating the frame
    update_frame()

    # Start the Tkinter main loop
    root.mainloop()

# Release the video capture and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
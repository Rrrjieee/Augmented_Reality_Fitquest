from exercise_details import ExerciseDetails

# Pose detection scripts.
import user.pose_detection.bicep_curl_up
import user.pose_detection.sit_ups
import user.pose_detection.squats
import user.pose_detection.lunges
import user.pose_detection.high_knees
import user.pose_detection.push_ups

_check = {
    'Bicep Curl Up': user.pose_detection.bicep_curl_up.check,
    'Sit-Ups': user.pose_detection.sit_ups.check,
    'Squats': user.pose_detection.squats.check,
    'Lunges': user.pose_detection.lunges.check,
    'High Knees': user.pose_detection.high_knees.check,
    'Push Ups': user.pose_detection.push_ups.check
}


def load(exer_list: list[ExerciseDetails]):
    global _check
    for exer in exer_list:
        if not exer.name in _check:
            continue

        exer.check = _check[exer.name]

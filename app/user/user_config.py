font_name           = 'assets/fonts/Scheherazade-Bold.ttf'
home_page           = 'assets/images/fitquest_bg_home.png'
user_page           = 'assets/images/fitquest_bg_template.png'
user_icon           = 'assets/images/default_user_icon.png'
option_img_path     = 'assets/images/routine_widget.png'
default_app_size    = (1280, 720)

button_params       = {
    'bg_color'      : (1,1,1,1),
    'bg_normal'     : '',
    'dark_color'    : (32/255, 0, 67/255, 1),
    'color'         : (49/255, 0, 100/255, 1),
    'light_color'   : (201/255, 133/255, 237/255, 1)
}
back_button_params  = {
    'text'          : 'GO BACK',
    'size_hint'     : [0.18, 0.12],
    'pos_hint'      : {'x': 0.05, 'center_y': 0.12},
}
countdown_time      = 3

user_reps_count     = 12
user_reps_mult      = 5
user_sets_count     = 4

cooldown_ratings    = [
    "", # Needed to make rating indices more intuitive
    '''
    You did quite decently, though there are a lot of flaws with the
    execution. Take a moment of rest, and strive to become a healthier
    person!
    ''',
    '''
    Below Average 
    Tip: Increase your effort and consistency for better results.
    ''',
    '''
    Every set is a lesson and a prize at the same time. Treasure it,
    and strive for greater heights.
    ''',
    '''
    Nearly perfect. You have mastered this exercise. Now, it is
    time to rest for a while. You shall reach and go beyond excellence.
    ''',
    '''

    "Perfection. Wars will be fought silently, and we will win them
    with silent weapons like you."
    
    - (Dr. Hendrik Joliet Easterman)
    '''
]
toast_message       = "Congratulations! You've completed your routine."
poses               = {
    # Derived from the pose enum values.
    'nose'                  : {'value': 0, 'name': 'Nose'},
    'left_eye_inner'        : {'value': 1, 'name': 'Inner left eye'},
    'left_eye'              : {'value': 2, 'name': 'Left eye'},
    'left_eye_outer'        : {'value': 3, 'name': 'Outer left eye'},
    'right_eye_inner'       : {'value': 4, 'name': 'Inner right eye'},
    'right_eye'             : {'value': 5, 'name': 'Right eye'},
    'right_eye_outer'       : {'value': 6, 'name': 'Outer right eye'},
    'left_ear'              : {'value': 7, 'name': 'Left ear'},
    'right_ear'             : {'value': 8, 'name': 'Right ear'},
    'mouth_left'            : {'value': 9, 'name': 'Left-side mouth'},
    'mouth_right'           : {'value': 10, 'name': 'Right-side mouth'},
    'left_shoulder'         : {'value': 11, 'name': 'Left shoulder'},
    'right_shoulder'        : {'value': 12, 'name': 'Right shoulder'},
    'left_elbow'            : {'value': 13, 'name': 'Left elbow'},
    'right_elbow'           : {'value': 14, 'name': 'Right elbow'},
    'left_wrist'            : {'value': 15, 'name': 'Left wrist'},
    'right_wrist'           : {'value': 16, 'name': 'Right wrist'},
    'left_pinky'            : {'value': 17, 'name': 'Left pinky'},
    'right_pinky'           : {'value': 18, 'name': 'Right pinky'},
    'left_index'            : {'value': 19, 'name': 'Left index finger'},
    'right_index'           : {'value': 20, 'name': 'Right index finger'},
    'left_thumb'            : {'value': 21, 'name': 'Left thumb'},
    'right_thumb'           : {'value': 22, 'name': 'Right thumb'},
    'left_hip'              : {'value': 23, 'name': 'Left hip'},
    'right_hip'             : {'value': 24, 'name': 'Right hip'},
    'left_knee'             : {'value': 25, 'name': 'Left knee'},
    'right_knee'            : {'value': 26, 'name': 'Right Knee'},
    'left_ankle'            : {'value': 27, 'name': 'Left ankle'},
    'right_ankle'           : {'value': 28, 'name': 'Right ankle'},
    'left_heel'             : {'value': 29, 'name': 'Left heel'},
    'right_heel'            : {'value': 30, 'name': 'Right heel'},
    'left_foot_index'       : {'value': 31, 'name': 'Left foot index toe'},
    'right_foot_index'      : {'value': 32, 'name': 'Right foot index toe'},
}
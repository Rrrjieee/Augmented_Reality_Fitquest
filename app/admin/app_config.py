tab                 = {
    'font_size'     : 17.5,
}
path                = {
    'icons'         : {
        'delete'    : 'assets/images/icon_trash_bin.png',
        'star'      : 'assets/images/icon_star.png'
    }
}
popup               = {
    'title'         : "Confirm Deletion:",
    'exercise'      : "Are you sure you want to delete the following exercise?",
}
app                 = {
    'background'    : 'assets/images/fitquest_bg.png',
    'bg_logo'       : 'assets/images/fitquest_bg_logo.png',
    'logo'          : 'assets/images/logo-no-background.png'
}
music               = {
    'main_menu'     : [
        'assets/audio/bss_fighting.mp3',
        'assets/audio/chainsaw_man_op1.mp3',
        'assets/audio/zetsubou_billy.mp3',
        'assets/audio/ado_kura_kura.mp3',
    ],
    'play'          : False
}
json                = {
    'content'       : 'exercises.json',
    'name'          : 'exercises_names.json',
    'routines'      : 'routines.json',
    'user'          : 'users.json'
}
# Lists:
font_name = [
    "assets/fonts/gabarito.ttf",
    "assets/fonts/wonderboys.ttf",
    "assets/fonts/Times Roman Bold.ttf",
    "assets/fonts/Scheherazade-Bold.ttf"
]
font_size = [
    20,
    32,
    36,
    64,
    48,
    12,
    224
]
# Admin Pages
admin_page = {
    'exercise_manager': {
        'selection_height': 60,
        'panel_layout_size': [0.68, 1.0],
    },
    'routine_manager': {
        'bg_color_dark': [81/255, 5/255, 148/255, 1],
        'bg_color': [181/255, 148/255, 214/255, 1]
    }
}
debug_start_page = 'main_screen'
db = {
    'user_profile': 'db/user_profiles.db',
}
db_cursor = {
    'user_profile': 'db/cursor/user_profiles.sql'
}
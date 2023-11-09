from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.properties import ListProperty
from functools import partial
from kivy.metrics import dp

import user.user_config as user_config
from user.user_widgets import *

import admin.app_config as admin_config
import admin.json_handler as json_handler

from admin.admin_widgets import *
from user_details import UserDetails
from exercise_details import ExerciseDetails
# from routine_details import RoutineDetails

from admin.admin_behavior import BackButtonDispatch
from user.user_selection import UserScreen
from user.user_exercise_start import ExerciseScreen

class SummaryScreen(Screen):
    _instance   = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance   = super(SummaryScreen, cls).__new__(cls, **kwargs)
        return cls._instance

    def __init__(self, sm: ScreenManager, app: App,
                 exer_average: dict, exer_screen: ExerciseScreen,
                 user_screen: UserScreen, **kwargs):
        super().__init__(**kwargs)
        self._sm            = sm
        self._app           = app
        self.exer_average   = exer_average
        self.exer_screen    = exer_screen
        self.user_screen    = user_screen   # Exfiltrate user from user_screen via user_screen.get_choice()

        # ===============================
        #           Main layout
        # ===============================
        layout              = FloatLayout(size_hint = [1.0, 1.0], pos_hint={'x': 0, 'y': 0})
        bg                  = Image(source=admin_config.app['background'], fit_mode="fill")
        layout.add_widget(bg)
        self._layout        = layout

        self.add_widget(layout)

        # ===============================
        #       A simple toast
        # ===============================
        congratulations_label   = Label(
            size_hint           = [1, 0.30],
            pos_hint            = {'center_x': 0.5, 'center_y': 0.50},
            text                = user_config.toast_message,
            font_size           = 64,
            valign              = 'center',
            halign              = 'center'
        )
        layout.add_widget(congratulations_label)
        congratulations_label.bind(size = congratulations_label.setter('text_size'))

        # ===============================
        #       Display at right side
        # ===============================
        self.display_layout             = BGFloatLayout(
            size_hint                   = [0.60, 0.35],
            pos_hint                    = {'center_x': 0.5, 'top': 1.0}
        )
        layout.add_widget(self.display_layout)
        self.display_layout.bg_color.rgba   = app_config.admin_page['routine_manager']['bg_color_dark']

        child_layout                    = BGFloatLayout(
            size_hint                   = [1.0, 1.0],
            pos_hint                    = {'right': 1, 'top': 1}
        )
        self.display_layout.add_widget(child_layout)
        child_layout.bg_color.rgba      = app_config.admin_page['routine_manager']['bg_color']

        scroll                          = ScrollView(
            do_scroll_x                 = True,
            size_hint_x                 = None,
            size_hint_y                 = 1.0,
            pos_hint                    = {'x': 0, 'y': 0}
        )
        child_layout.add_widget(scroll)

        self.grid                       = GridLayout(
            # To achieve scrolling horizontally, this field must be set to None, not 1.
            size_hint_x                 = None,  # Set size_hint_x to 1 to fill the available space
            size_hint_y                 = 1.0,
            rows                        = 1,
            col_default_width           = 275,
            col_force_default           = True,
            spacing                     = 35
        )
        scroll.add_widget(self.grid)
        child_layout.bind(width = scroll.setter('width'))
        self.grid.bind(minimum_width = self.grid.setter('width'))

        back_btn        = Button(
            text        = 'BACK TO MAIN MENU',
            font_name   = admin_config.font_name[2],
            font_size   = admin_config.font_size[1],
            size_hint   = [0.44, 0.12],
            pos_hint    = {'center_x': 0.50, 'y': 0.24}
        )
        layout.add_widget(back_btn)
        BackButtonDispatch.on_release(back_btn, 'user_routine_selection', self._sm, 'right')

    def on_enter(self, *args):
        self.grid.clear_widgets()
        
        user: UserDetails               = self.user_screen.get_choice()
        if user is None:
            raise RuntimeError("No user specified! This screen should be unreachable!")
        
        exer_list                       = self.exer_average['exercise']
        avg_list                        = self.exer_average['average']
        json_user                       = json_handler.JSONUser()
        for i in range(len(exer_list)):
            exercise: ExerciseDetails   = exer_list[i]
            avg_score: float            = avg_list[i]
            user.add_exercise(exercise, avg_score)

        self.exer_screen.reset_average()
        json_user.update()
        
        user_exer_list                  = user.get_exercise_list()
        json_object                     = json_handler.JSONExercise()
        for exer_dict in user_exer_list:
            # Display exercise list
            # TO-DO: Render this part.
            exercise                = json_object.get_exercise(exer_dict['name'])

            outer_layout            = FloatLayout(
                size_hint           = [None, 1.0],
                pos_hint            = {'x': 0, 'y': 0},
            )
            self.grid.add_widget(outer_layout)

            # Inner layout -> Child of Outer layout
            inner_layout            = BGFloatLayout(
                size_hint           = [None, 1.0],
                pos_hint            = {'right': 1, 'top': 1}
            )
            outer_layout.add_widget(inner_layout)
            outer_layout.bind(width = inner_layout.setter('width'))
            inner_layout.bg_color.rgba  = [1,1,1,1]

            inner_image     = Image(
                size_hint   = [1.0, 0.50],
                pos_hint    = {'center_x': 0.5, 'center_y': 0.60},
                source      = exercise.img_path
            )
            inner_layout.add_widget(inner_image)

            inner_grid      = GridLayout(
                rows        = 1,
                cols        = 5,
                size_hint   = [1.0, 0.2],
                pos_hint    = {'x': 0.0,'y': 0.0},
                spacing     = [10, 0],
            )
            inner_layout.add_widget(inner_grid)
            
            # Calculate the average score for this particular exercise.
            average         = 0.0
            for value in exer_dict['score']:
                average    += value

            if len(exer_dict['score']) == 0:
                average     = 0.0
            else:
                average    /= len(exer_dict['score'])

            # Map the average score to the appropriate rating
            stars_obtained  = int(average / 0.2)
            stars_obtained  = 5 if stars_obtained >= 5 else stars_obtained
            stars_obtained  = 0 if stars_obtained <= 0 else stars_obtained

            # Change the color property of the Image widgets.
            for i in range(5):
                star            = Image(
                    size_hint   = [1.0, 1.0],
                    pos_hint    = {'x': 0.0,'y': 0.0},
                    fit_mode    = 'fill',
                    source      = admin_config.path['icons']['star']
                )
                inner_grid.add_widget(star)

                if i > stars_obtained:
                    # Color it gray
                    star.color  = [0.35, 0.35, 0.35, 1]
                else:
                    # Color it light red or something
                    star.color  = [0.95, 0.8, 0.8, 1]

        del user_exer_list

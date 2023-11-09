from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget

import user.user_config as user_config
import admin.app_config as admin_config
import admin.json_handler as json_handler
from admin.admin_widgets import *
from user.user_widgets import *
from exercise_details import ExerciseDetails
from routine_details import RoutineDetails

from admin.admin_behavior import BackButtonDispatch


class CustomRoutineScreen(Screen):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CustomRoutineScreen,
                                  cls).__new__(cls, **kwargs)
        return cls._instance

    def __init__(self, sm: ScreenManager, app: App, **kwargs):
        super().__init__(**kwargs)
        self._sm = sm
        self._app = app

        self._choice    = {
            'exercise'  : None,
            'reps'      : 0,
            'sets'      : 0,
            'finalized' : False,
            'routine'   : None,
        }
        self._widgets   = {
            'exercise'  : None,
            'reps'      : None,
            'sets'      : None
        }

        # ===============================
        #           Main layout
        # ===============================
        layout = FloatLayout(size_hint=[1.0, 1.0], pos_hint={'x': 0, 'y': 0})
        bg = Image(source=admin_config.app['background'], fit_mode="fill")
        layout.add_widget(bg)
        self._layout = layout

        # ===============================
        #   Add logo at top left area
        # ===============================
        logo            = Image(
            source      = admin_config.app['logo'],
            fit_mode    = "contain",
            size_hint   = [None, None],
            size        = [192, 192],
            pos_hint    = {'x': 0.04, 'top': 1}
        )
        layout.add_widget(logo)

        # ===============================
        #   Add cabaret at top right corner
        # ===============================
        cabaret_label   = BGLabel(
            text        = 'CUSTOMIZED ROUTINE',
            font_name   = admin_config.font_name[0],
            font_size   = admin_config.font_size[3],
            color       = user_config.button_params['color'],
            size_hint   = [0.44, 0.12],
            pos_hint    = {'right': 0.96, 'top': 0.96}
        )
        layout.add_widget(cabaret_label)

        # =======================================
        #           Back button
        # =======================================
        back_btn                = Button(
            background_normal   = user_config.button_params['bg_normal'],
            background_color    = user_config.button_params['bg_color'],
            color               = user_config.button_params['color'],
            text                = 'BACK',
            font_name           = admin_config.font_name[2],
            font_size           = admin_config.font_size[1],
            size_hint           = [0.16, 0.12],
            pos_hint            = {'x': 0.02, 'y': 0.02}
        )
        layout.add_widget(back_btn)
        BackButtonDispatch.on_release(
            back_btn, 'user_routine_selection', self._sm, 'right')
        self.add_widget(layout)

        start_btn = Button(
            background_normal=user_config.button_params['bg_normal'],
            background_color=user_config.button_params['bg_color'],
            color=user_config.button_params['color'],
            text='START',
            font_name=admin_config.font_name[2],
            font_size=admin_config.font_size[1],
            size_hint=[0.16, 0.12],
            pos_hint={'right': 0.98, 'y': 0.02},
            disabled=True
        )
        layout.add_widget(start_btn)
        self.start_button = start_btn

        def on_routine_proceed():
            self._choice['finalized'] = True
            self._app.send_routine(self._choice['routine'])
            self._choice['routine'] = None

        BackButtonDispatch.on_release(start_btn, 'exercise_pre_start', self._sm, None,
                                      pre_trans_effect=on_routine_proceed)

    def can_enable_insert_btn(self):
        return ((self._choice['exercise'] is not None) and
                (self._choice['reps'] != 0) and
                (self._choice['sets'] != 0))

    def clear_data(self):
        if (not hasattr(self, 'insert_btn')):
            return

        self._choice['exercise']    = None
        self._choice['reps']        = 0
        self._choice['sets']        = 0

        if self._widgets['exercise']:
            self._widgets['exercise'].state = "normal"
        if self._widgets['reps']:
            self._widgets['reps'].state     = "normal"
        if self._widgets['sets']:
            self._widgets['sets'].state     = "normal"
            
        self._widgets['exercise']           = None
        self._widgets['reps']               = None
        self._widgets['sets']               = None
        self.insert_btn.disabled            = not self.can_enable_insert_btn()

    def draw_options(self):
        layout = self._layout
        if hasattr(self, 'child_layout'):
            layout.remove_widget(self.child_layout)
            self.child_layout.clear_widgets()
            del self.insert_btn
            del self.exer_options
            del self.reps_options
            del self.sets_options
            del self.child_layout

        self.child_layout = FloatLayout(
            size_hint=[0.84, 0.56],
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.add_widget(self.child_layout)

        # =======================================
        #         Create selection options
        # =======================================
        self.exer_options = ScrollableOption(
            size_hint=[0.30, 1.0],
            pos_hint={'x': 0, 'y': 0},
            font_size=admin_config.font_size[2],
            cols=2,
            text='EXERCISES:',
            spacing=20,
        )
        self.child_layout.add_widget(self.exer_options)

        # =======================================
        #       Create Button Options
        # =======================================
        json_exer = json_handler.JSONExercise()
        exer_list = json_exer.extract_list()

        for exercise in exer_list:
            exercise: ExerciseDetails
            img_container = FloatLayout(
                size_hint=[1.0, None],
            )
            self.exer_options.add_grid_widget(img_container)

            img_btn         = ImageButton2(
                size_hint   = [1.0, None],
                pos_hint    = {'x': 0, 'y': 0},
                fit_mode    = 'fill',
                source      = exercise.img_path,
                group       = 'exer_options',
            )
            img_container.add_widget(img_btn)
            img_container.bind(size=img_btn.setter("size"))

            def img_factory(img_btn, exercise, self):
                def on_img_click(instance):
                    nonlocal self
                    if (self._widgets['exercise'] is not None) and (instance != self._widgets['exercise']):
                        self._widgets['exercise'].state = 'normal'
                        self._widgets['exercise'].canvas.ask_update()

                    if instance.state == 'normal':
                        self._choice['exercise']    = None
                        self._widgets['exercise']   = None
                    else:
                        self._choice['exercise']    = exercise
                        self._widgets['exercise']   = instance

                    self.insert_btn.disabled = not self.can_enable_insert_btn()

                img_btn.bind(on_release=on_img_click)

            img_factory(img_btn,
                        exercise,
                        self)

        # =======================================
        #         Create Reps options
        # =======================================
        self.reps_options   = ScrollableOption(
            size_hint       = [0.30, 0.54],
            pos_hint        = {'x': 0.33, 'y': 0.46},
            font_size       = admin_config.font_size[2],
            cols            = 3,
            text            = 'REPS:',
            spacing         = 5,
        )
        self.child_layout.add_widget(self.reps_options)

        for i in range(1, user_config.user_reps_count + 1):
            rep_btn         = ToggleButton(
                text        = str(i*user_config.user_reps_mult),
                font_name   = admin_config.font_name[0],
                font_size   = admin_config.font_size[1],
                size_hint_y = None,
                group       = 'reps',
            )
            self.reps_options.add_grid_widget(rep_btn)

            def rep_factory(rep_btn, exercise, i, self):
                def on_rep_click(instance):
                    nonlocal self
                    if instance.state == 'down':
                        self._choice['reps']    = i*user_config.user_reps_mult
                        self._widgets['reps']   = instance
                    else:
                        self._choice['reps']    = 0
                        self._widgets['reps']   = None
                    self.insert_btn.disabled    = not self.can_enable_insert_btn()

                rep_btn.bind(on_release=on_rep_click)

            rep_factory(rep_btn, exercise, i, self)

        # =======================================
        #         Create sets options
        # =======================================
        self.sets_options = ScrollableOption(
            size_hint=[0.30, 0.42],
            pos_hint={'x': 0.33, 'y': 0.0},
            font_size=admin_config.font_size[2],
            cols=3,
            text='SETS:',
            spacing=5,
        )
        self.child_layout.add_widget(self.sets_options)

        for i in range(1, user_config.user_sets_count + 1):
            set_btn         = ToggleButton(
                text        = str(i),
                font_name   = admin_config.font_name[0],
                font_size   = admin_config.font_size[1],
                size_hint_y = None,
                group       = 'sets'
            )
            self.sets_options.add_grid_widget(set_btn)

            def set_factory(set_btn, exercise, i, self):
                def on_set_click(instance):
                    nonlocal self
                    if instance.state == 'down':
                        self._choice['sets']    = i
                        self._widgets['sets']   = instance
                    else:
                        self._choice['sets']    = 0
                        self._widgets['sets']   = None
                    self.insert_btn.disabled    = not self.can_enable_insert_btn()

                set_btn.bind(on_release=on_set_click)

            set_factory(set_btn, exercise, i, self)

        # =======================================
        #         Create insert button
        # =======================================
        self.insert_btn         = Button(
            background_normal   = user_config.button_params['bg_normal'],
            background_color    = user_config.button_params['bg_color'],
            color               = user_config.button_params['color'],
            text                = 'INSERT',
            font_name           = admin_config.font_name[2],
            font_size           = admin_config.font_size[1],
            size_hint           = [0.16, 0.12],
            pos_hint            = {'right': 0.80, 'y': 0.02},
            disabled            = True
        )
        layout.add_widget(self.insert_btn)

        def on_insert_exercise(instance):
            routine = self._choice['routine']
            if routine is None:
                routine                 = RoutineDetails(
                    name                = "Custom Routine",
                    desc                = "A customized routine that grants flexibility of choice for users.",
                    exercises           = []
                )
                self._choice['routine'] = routine

            exercise: ExerciseDetails   = self._choice['exercise']

            derived_exer                = exercise.copy()
            derived_exer.reps           = self._choice['reps']
            derived_exer.sets           = self._choice['sets']
            derived_exer.duration       = int(exercise.duration * derived_exer.reps / exercise.reps)

            routine.add_exercise(derived_exer)

            self.clear_data()
            self.draw_exer_list()
            self.check_start_state()

        self.insert_btn.bind(on_release = on_insert_exercise)
        self.draw_exer_list()

    def draw_exer_list(self):
        if hasattr(self, 'exer_list_layout'):
            self.child_layout.remove_widget(self.exer_list_layout)
            del self.exer_list_layout

        self.exer_list_layout   = ScrollableOption(
            size_hint           = [0.34, 1.00],
            pos_hint            = {'x': 0.66, 'y': 0.0},
            font_size           = admin_config.font_size[2],
            cols                = 1,
            text                = 'Exercise List:',
            spacing             = 5,
        )
        self.exer_list_layout.get_grid_container().size_hint = [0.75, 0.70]
        self.child_layout.add_widget(self.exer_list_layout)

        # =======================================
        #         Create list below
        # =======================================
        if (self._choice['routine'] is None):
            # Routine hasn't been established yet.
            return

        routine: RoutineDetails = self._choice['routine']
        for exercise in iter(routine):
            # Render each option.

            exer_layout = BGFloatLayout(
                size_hint=[1.0, None],
            )
            exer_layout.bg_color.rgba = [1, 1, 1, 1]
            exer_layout.border_color.rgba = [0.8, 0.8, 0.8, 0.8]
            exer_layout.border_size = 4
            self.exer_list_layout.add_grid_widget(exer_layout)

            # =======================================
            #           Render each label
            # =======================================
            exer_label_box = GridLayout(
                size_hint=[0.4, 1.0],
                pos_hint={'x': 0, 'y': 0},
                cols=1,
            )
            exer_layout.add_widget(exer_label_box)

            exer_label_name = Label(
                text='Exercise:',
                halign='left',
                color=[0, 0, 0, 1]
            )
            exer_label_name.bind(text_size=exer_label_name.setter('size'))
            exer_label_box.add_widget(exer_label_name)

            exer_label_reps = Label(
                text        ='Reps:',
                halign      ='left',
                color=[0, 0, 0, 1]
            )
            exer_label_reps.bind(text_size=exer_label_reps.setter('size'))
            exer_label_box.add_widget(exer_label_reps)

            exer_label_sets = Label(
                text        = 'Sets:',
                halign      = 'left',
                color       = [0, 0, 0, 1]
            )
            exer_label_sets.bind(text_size=exer_label_sets.setter('size'))
            exer_label_box.add_widget(exer_label_sets)

            # =======================================
            #           Render each value
            # =======================================
            exer_value_box = GridLayout(
                size_hint=[0.45, 1.0],
                pos_hint={'x': 0.4, 'y': 0},
                cols=1,
            )
            exer_layout.add_widget(exer_value_box)

            exer_value_name = Label(
                text=exercise.name,
                halign='left',
                color=[0, 0, 0, 1]
            )
            exer_value_name.bind(text_size=exer_value_name.setter('size'))
            exer_value_box.add_widget(exer_value_name)

            exer_value_reps = Label(
                text=str(exercise.reps),
                halign='left',
                color=[0, 0, 0, 1]
            )
            exer_value_reps.bind(text_size=exer_value_reps.setter('size'))
            exer_value_box.add_widget(exer_value_reps)

            exer_value_sets = Label(
                text=str(exercise.sets),
                halign='left',
                color=[0, 0, 0, 1]
            )
            exer_value_sets.bind(text_size=exer_value_sets.setter('size'))
            exer_value_box.add_widget(exer_value_sets)

    def check_start_state(self):
        if (self._choice['routine'] is None):
            # Routine hasn't been established yet.
            self.start_button.disabled = True
            return

        routine: RoutineDetails = self._choice['routine']
        self.start_button.disabled = len(routine.exercises) < 1

    def on_pre_enter(self):
        self.draw_options()

    def on_leave(self):
        layout = self._layout

        if hasattr(self, 'exer_list_layout'):
            self.child_layout.remove_widget(self.exer_list_layout)
            del self.exer_list_layout

        if hasattr(self, 'child_layout'):
            layout.remove_widget(self.child_layout)
            self.child_layout.clear_widgets()
            del self.insert_btn
            del self.exer_options
            del self.reps_options
            del self.sets_options
            del self.child_layout

        # Clear the screen once finalized.
        if self._choice['finalized'] and hasattr(self, 'exer_list_layout'):
            self.child_layout.remove_widget(self.exer_list_layout)
            del self.exer_list_layout

        self.clear_data()

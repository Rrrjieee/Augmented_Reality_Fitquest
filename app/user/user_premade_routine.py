from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.graphics import Color, Rectangle, RoundedRectangle, Rotate, PushMatrix, PopMatrix
from kivy.animation import Animation
from kivy.metrics import dp


import user.user_config as user_config
import admin.app_config as admin_config
import admin.json_handler as json_handler
from admin.admin_widgets import *
from user.user_widgets import *
from exercise_details import ExerciseDetails

from admin.admin_behavior import BackButtonDispatch


class PremadeRoutineScreen(Screen):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PremadeRoutineScreen,
                                  cls).__new__(cls, **kwargs)
        return cls._instance

    def __init__(self, sm: ScreenManager, app: App, **kwargs):
        super().__init__(**kwargs)
        self._choice = {
            'selected': False,
            'option': -1,
            'finalized': False,
        }
        self._sm = sm
        self._app = app

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
            source      =admin_config.app['logo'],
            fit_mode    ="contain",
            size_hint   =[None, None],
            size        =[192, 192],
            pos_hint    ={'x': 0.04, 'top': 1}
        )
        layout.add_widget(logo)

        # ===============================
        #   Add cabaret at top right corner
        # ===============================
        cabaret_label   = BGLabel(
            text        ='READY-MADE ROUTINE',
            font_name   =admin_config.font_name[0],
            font_size   =admin_config.font_size[3],
            color       =user_config.button_params['color'],
            size_hint   =[0.44, 0.12],
            pos_hint    ={'right': 0.96, 'top': 0.96}
        )
        layout.add_widget(cabaret_label)

        instruction_label   = Label(
            text            ="Please choose a routine",
            size_hint       =[0.40, 0.10],
            pos_hint        ={'center_x': 0.2, 'center_y': 0.78},
            font_size       =35,
            bold            =True,
            color           =(1,1,1,1),
        )
        layout.add_widget(instruction_label)

        # =======================================
        #           Back button
        # =======================================
        back_btn                = Button(
            background_normal   =user_config.button_params['bg_normal'],
            background_color    =user_config.button_params['bg_color'],
            color               =user_config.button_params['color'],
            text                ='BACK',
            font_name           =admin_config.font_name[2],
            font_size           =admin_config.font_size[1],
            size_hint           =[0.16, 0.12],
            pos_hint            ={'x': 0.02, 'y': 0.02}
        )
        layout.add_widget(back_btn)
        BackButtonDispatch.on_release(
            back_btn, 'user_routine_selection', self._sm, 'right')
        self.add_widget(layout)

        start_btn               = Button(
            background_normal   =user_config.button_params['bg_normal'],
            background_color    =user_config.button_params['bg_color'],
            color               =user_config.button_params['color'],
            text                ='START',
            font_name           =admin_config.font_name[2],
            font_size           =admin_config.font_size[1],
            size_hint           =[0.16, 0.12],
            pos_hint            ={'right': 0.98, 'y': 0.02},
            disabled            =True
        )
        layout.add_widget(start_btn)
        self.start_button = start_btn

        def on_routine_proceed():
            self._choice['finalized'] = True
            json_routine    = json_handler.JSONRoutine()
            json_list       = json_routine.extract_list()
            self._app.send_routine(json_list[self._choice['option']].copy())

        BackButtonDispatch.on_release(start_btn, 'exercise_pre_start', self._sm, None,
                                      pre_trans_effect  =   on_routine_proceed)

    def draw_routines(self):
        layout = self._layout

        # =======================================
        #           Enclose options
        # =======================================
        option_container    = BGFloatLayout(
            size_hint       =[0.85, 0.58],
            pos_hint        ={'center_x': 0.5, 'center_y': 0.45}
        )
        layout.add_widget(option_container)
        option_container.border_size = 5
        option_container.bg_color.rgba = [1, 1, 0, 0]
        option_container.border_color.rgba = [0, 0, 0, 0]
        self.option_container = option_container

        # =======================================
        #           Scroll view
        # =======================================
        option_scroll = ScrollView(
            pos_hint={'center_x': 0.5, 'y': 0},
            size_hint=[1, None],
            do_scroll_y=True,
        )
        option_container.add_widget(option_scroll)

        def on_height_update(instance, height):
            option_scroll.height = height
        option_container.bind(height=on_height_update)

        option_grid = GridLayout(
            size_hint=[1.00, None],
            cols=1,
            spacing=5,
        )
        option_scroll.add_widget(option_grid)
        option_grid.bind(minimum_width=option_grid.setter('width'))
        option_grid.bind(minimum_height=option_grid.setter('height'))

        # =======================================
        #           Add Routines
        # =======================================
        json_routine        = json_handler.JSONRoutine()
        rout_list           = json_routine.extract_list()
        valid_rout_counter  = 0

        # Referred in on_btn_click
        self.last_layer = None
        for i in range(len(rout_list)):
            routine = rout_list[i]
            if len(routine.exercises) <= 0:
                continue
            valid_rout_counter += 1
            # =======================================
            #               Button Layout
            # =======================================
            btn_layout = BGFloatLayout(
                size_hint=[None, None],
            )
            btn_layout.size_hint_x = 1.0
            btn_layout.bg_color.rgba = [1, 1, 1, 1]
            btn_layout.height = 250
            option_grid.add_widget(btn_layout)

            btn_routine_bg = BGFloatLayout(
                size_hint=[0.2, 1.0],
                pos_hint={'x': 0, 'center_y': 0.5}
            )
            btn_layout.add_widget(btn_routine_bg)
            btn_routine_bg.bg_color.rgba = user_config.button_params['light_color']

            btn_exercise_bg = BGFloatLayout(
                size_hint=[0.8, 0.6],
                pos_hint={'x': 0.2, 'y': 0.4}
            )
            btn_layout.add_widget(btn_exercise_bg)
            btn_exercise_bg.bg_color.rgba = [0.7, 0.7, 0.7, 1]

            btn_desc_bg = FloatLayout(
                size_hint=[0.8, 0.4],
                pos_hint={'x': 0.2, 'y': 0}
            )
            btn_layout.add_widget(btn_desc_bg)

            # =======================================
            #         Backgrounds created,
            #         make labels now
            # =======================================
            btn_routine_label   = Label(
                width           =btn_routine_bg.height,
                height          =btn_routine_bg.width,
                pos_hint        ={'center_x': 0.5, 'center_y': 0.5},
                text            =routine.routine_name,
                font_size       =admin_config.font_size[2],
                font_name       =admin_config.font_name[2],
            )
            btn_routine_bg.add_widget(btn_routine_label)
            KivyPropHandler.on_text_size_change(btn_routine_label, 0.5)
            # btn_routine_label.bind(text_size=btn_routine_label.setter('size'))

            btn_desc_label  = Label(
                width       =btn_desc_bg.height,
                height      =btn_desc_bg.width,
                pos_hint    ={'center_x': 0.5, 'center_y': 0.5},
                text        =routine.routine_description,
                font_size   =admin_config.font_size[1],
                color       =[0, 0, 0, 1]
            )
            btn_desc_bg.add_widget(btn_desc_label)
            KivyPropHandler.on_text_size_change(btn_desc_label, 0.72)
            KivyPropHandler.on_font_size_change(
                btn_desc_label, 0.06, 1.1, True)
            # btn_desc_label.bind(text_size=btn_desc_label.setter('size'))

            # =======================================
            #         Backgrounds created,
            #         make labels now
            # =======================================
            btn_scroll_cont = FloatLayout(
                size_hint=[0.60, 1.0],
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
            )
            btn_exercise_bg.add_widget(btn_scroll_cont)

            btn_scroll = ScrollView(
                do_scroll_x=True,
                size_hint=[None, 1.0],
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            btn_scroll_cont.add_widget(btn_scroll)

            btn_grid = GridLayout(
                size_hint_x=None,
                rows=1,
                col_default_width=100,
            )
            btn_scroll.add_widget(btn_grid)
            btn_grid.bind(minimum_width=btn_grid.setter('width'))
            btn_grid.bind(minimum_height=btn_grid.setter('height'))

            def create_bindings(btn_scroll_cont, btn_scroll, btn_grid):
                def on_scroll_width(instance, width):
                    btn_scroll.width = width
                    btn_grid.spacing = width * 0.15
                btn_scroll_cont.bind(width=on_scroll_width)
            create_bindings(btn_scroll_cont, btn_scroll, btn_grid)

            for exercise in routine.exercises:
                exercise: ExerciseDetails
                exer_bg = FloatLayout(
                    size_hint=[None, 1.0],
                    width=150,
                )
                btn_grid.add_widget(exer_bg)

                # =================================
                #           Exercise Image
                # =================================
                exer_image = Image(
                    size_hint=[0.50, 0.60],
                    pos_hint={'center_x': 0.5, 'center_y': 0.7},
                    source=exercise.img_path,
                )
                exer_bg.add_widget(exer_image)

                # =================================
                #           Exercise Labels
                # =================================
                exer_reps = Label(
                    size_hint=[0.75, 0.20],
                    pos_hint={'center_x': 0.5, 'center_y': 0.35},
                    text=f"Reps: {exercise.reps}",
                )
                exer_bg.add_widget(exer_reps)

                exer_sets = Label(
                    size_hint=[0.75, 0.20],
                    pos_hint={'center_x': 0.5, 'center_y': 0.15},
                    text=f"Sets: {exercise.sets}",
                )
                exer_bg.add_widget(exer_sets)

            # ===================================
            #       Overlay button into the
            #       Image.
            # ===================================
            button = InvisibleButton(
                size_hint=[1.0, 1.0],
                pos_hint={'x': 0, 'y': 0},
            )
            btn_layout.add_widget(button)

            button_layer = BGFloatLayout(
                size_hint=[1.0, 1.0],
                pos_hint={'x': 0, 'y': 0},
            )
            btn_layout.add_widget(button_layer)
            button_layer.bg_color.rgba[3] = 0
            button_layer.border_color.rgba[3] = 0

            def on_btn_factory(button, i, self, button_layer):
                def on_btn_click(instance):
                    if self.last_layer is not None:
                        self.last_layer.bg_color.rgba[3] = 0

                    if i == self._choice['option']:
                        self._choice['option'] = -1
                        self._choice['selected'] = False
                        self.last_layer = None
                    else:
                        self._choice['option'] = i
                        self._choice['selected'] = True
                        self.last_layer = button_layer
                        self.last_layer.bg_color.rgba[3] = 0.35

                    self.start_button.disabled = not self._choice['selected']

                button.bind(on_release=on_btn_click)
            on_btn_factory(button, i, self, button_layer)

        if valid_rout_counter < 1:
            option_container.bg_color.rgba = [0.5, 0.5, 0.5, 1]
            option_container.border_size = 0
            option_container.clear_widgets()

            # =======================================
            #         Create a label indicating
            #         that we don't have any
            #         valid default routines.
            # =======================================
            warning_label = Label(
                size_hint=[1.0, 1.0],
                pos_hint={'x': 0, 'y': 0},
                text="Sorry, no default routines can be found.\n" +
                "Please go back and select custom routine.",
            )
            option_container.add_widget(warning_label)

    def on_pre_enter(self):
        self.draw_routines()

    def on_leave(self):
        layout = self._layout

        # Clear miscellaneous data.
        if not self._choice['finalized']:
            self._choice['option'] = -1
            self._choice['selected'] = False
        self._choice['finalized'] = False

        if self.last_layer is not None:
            self.last_layer.bg_color.rgba[3] = 0
            self.last_layer = None

        if hasattr(self, 'option_container'):
            layout.remove_widget(self.option_container)
            del self.option_container

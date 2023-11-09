from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition, FadeTransition
from kivy.properties import ListProperty
from kivy.clock import Clock

import user.user_config as user_config
import admin.app_config as admin_config
import admin.json_handler as json_handler
from admin.admin_widgets import *
from user.user_widgets import *
from exercise_details import ExerciseDetails
from routine_details import RoutineDetails
from math import ceil

class CooldownScreen(Screen):
    _instance   = None
    _score      = ListProperty([0.0, 0.3, 0.5, 0.65, 0.9])
    _stars      = NumericProperty(5)
    duration    = BoundedNumericProperty(0, min=0)

    def get_star_rating(self, score: float):
        if score > 1:
            score   = 1.0
        elif score < 0:
            score   = 0

        # Since this is a list with six items, a simple
        # linear search will work.
        for i in range(len(self._score)):
            if score < self._score[i]:
                return i
        
        return len(self._score)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance   = super(CooldownScreen, cls).__new__(cls, **kwargs)
        return cls._instance

    def __init__(self, sm: ScreenManager, app: App,
                 average_dict: dict, start_screen: Screen, **kwargs):
        super().__init__(**kwargs)
        self._sm            = sm
        self._app           = app
        self.exer_average   = average_dict
        self.start_screen   = start_screen

        # ===============================
        #           Main layout
        # ===============================
        layout              = FloatLayout(size_hint = [1.0, 1.0], pos_hint={'x': 0, 'y': 0})
        bg                  = Image(source=admin_config.app['background'], fit_mode="fill")
        layout.add_widget(bg)
        self._layout        = layout

        self.add_widget(layout)

        # ===============================
        #           Exercise Image
        # ===============================
        exer_container      = BGFloatLayout(
            size_hint       = [0.40, 0.80],
            pos_hint        = {'center_x': 0.5, 'center_y': 0.5}
        )
        exer_container.bg_color.rgba    = user_config.button_params['light_color']
        layout.add_widget(exer_container)

        exer_image          = Image(
            size_hint       = [0.75, 0.50],
            pos_hint        = {'center_x': 0.50, 'center_y': 0.70},
            source          = '',
            fit_mode        = 'contain',
        )
        exer_container.add_widget(exer_image)
        self.exer_image     = exer_image

        self.remark_label   = Label(
            size_hint       = [0.90, 0.30],
            text            = user_config.cooldown_ratings[0],
            font_size       = 24,
            pos_hint        = {'center_x': 0.50, 'y': 0},
            color           = [0.3333, 0.2824, 0.7216, 1]
        )
        self.remark_label.bind(size = self.remark_label.setter('text_size'))
        exer_container.add_widget(self.remark_label)

        # ===============================
        #       Exercise Star Rating
        # ===============================
        star_container      = GridLayout(
            cols            = self._stars,
            rows            = 1,
            size_hint       = [1.0, 0.15],
            pos_hint        = {'center_x': 0.50, 'y': 0.30}
        )
        exer_container.add_widget(star_container)

        self.star_list      = []
        for _ in range(star_container.cols):
            star            = Image(
                fit_mode    = 'cover',
                source      = admin_config.path['icons']['star']
            )
            self.star_list.append(star)
            star_container.add_widget(star)

        # ===============================
        #       Rating and remarks
        # ===============================

    def on_pre_enter(self):
        # Compute average
        exer_average                = self.exer_average

        exercise: ExerciseDetails   = exer_average['exercise'][-1]           
        average_score               = exer_average['average'][-1]

        star_count                  = self.get_star_rating(average_score)
        star_count                  = 0 if star_count < 0 else star_count
        self.remark_label.text      = user_config.cooldown_ratings[star_count]

        self.exer_image.source      = exercise.img_path

        # ==================================
        #       Store average score.
        # ==================================
        for i in range(1, self._stars + 1):
            j               = i - 1
            if star_count >= i:
                self.star_list[j].color = [1, 1, 1, 1]
            else:
                self.star_list[j].color = [0.3, 0.3, 0.3, 1]

        #   ==================================
        #       Star rating calculated,
        #       start cooldown.
        #   ==================================
        self.draw_countdown()
        self.start_cooldown()

    def on_pre_leave(self):
        if not hasattr(self, 'timer'):
            return
        self.timer.cancel()
        del self.timer

    def on_leave(self):
        self.remark_label.text  = user_config.cooldown_ratings[0]
        self.exer_image.source  = ""
        
    def draw_countdown(self):
        layout          = self._layout
        if hasattr(self, 'dur_layout'):
            layout.remove_widget(self.dur_layout)
            del self.dur_label
            del self.dur_layout

        self.dur_layout = FloatLayout(
            size_hint   = [0.40, 0.08],
            pos_hint    = {'right': 1, 'y': 0}
        )
        layout.add_widget(self.dur_layout)

        self.dur_label_text = Label(
            size_hint  = [0.8, 1.0],  # Adjust the size as needed
            pos_hint   = {'x': 0, 'y': 0},  # Position in the bottom-right with horizontal alignment
            text       = "Continuing in",
            font_size  = 50,
        )
        self.dur_layout.add_widget(self.dur_label_text)
        self.dur_label_text.bind(size = self.dur_label_text.setter('text_size'))

        self.dur_label  = Label(
            size_hint   = [0.2, 1.0],
            pos_hint    = {'x': 0.8, 'y': 0},
            text        = '0',
            font_size   = 50,
        )
        self.dur_layout.add_widget(self.dur_label)
        self.dur_label.bind(size = self.dur_label.setter('text_size'))

    def on_cooldown_update(self, dt):
        if self.duration < dt:
            self.duration   = 0
        else:
            self.duration  -= dt

    def start_cooldown(self):
        exercise: ExerciseDetails   = self.exer_average['exercise'][-1]            
        
        if exercise is None:
            calc_dur                = 5
        else:
            calc_dur                = exercise.duration * 0.5
            calc_dur                = ceil(calc_dur // 5) * 5
            if calc_dur <= 0:
                calc_dur           += 5

        self.duration       = calc_dur
        self.timer          = Clock.schedule_interval(
            self.on_cooldown_update,
            1.0,
        )

    def on_duration(self, instance, value):
        if not hasattr(self, 'dur_label'):
            return
        self.dur_label.text     = str(ceil(value))
        if value > 0:
            return
        if self._sm.current    != 'exercise_cooldown':
            return
        
        if self.start_screen.has_remaining_exercises():
            self._sm.transition     = FadeTransition(duration=0.5)
            self._sm.current        = 'exercise_start'
        else:
            self._sm.transition     = SlideTransition(direction='left')
            self._sm.current        = 'exercise_finished'
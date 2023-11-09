from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, SlideTransition, Screen, FadeTransition
from kivy.uix.camera import Camera
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp
from threading import Thread

from kivy.graphics import Color, RoundedRectangle
from kivy.graphics.texture import Texture
from typing import Callable
from user.pose_detection.return_code import ReturnCode
from kivy.uix.modalview import ModalView
from admin.admin_behavior import BackButtonDispatch

import user.user_config as user_config
import admin.app_config as admin_config
import admin.json_handler as json_handler
from admin.admin_widgets import *
from user.user_widgets import *
from exercise_details import ExerciseDetails
from routine_details import RoutineDetails

import cv2
import numpy as np
import PIL
from math import ceil

class BackButtonDispatch:
    back_button_callback = None

    @classmethod
    def on_release(cls, button, destination, sm, direction):
        def callback(instance):
            if cls.back_button_callback is not None:
                cls.back_button_callback(sm, destination, direction)
        button.bind(on_release=callback)

class ExerciseScreen(Screen):
    _instance   = None
    tick_rate   = NumericProperty(0.016)

    count       = NumericProperty(0, allownone=False)
    reps        = NumericProperty(0, allownone=False)
    exercise    = StringProperty("", allownone=False)

    def reset_average(self):
        if not hasattr(self, 'exer_average'):
            self.exer_average   = {
                'exercise'      : [],
                'average'       : [],
            }
        else:
            self.exer_average['exercise'].clear()
            self.exer_average['average'].clear()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance   = super(ExerciseScreen, cls).__new__(cls, **kwargs)
        return cls._instance

    def __init__(self, sm: ScreenManager, app: App, **kwargs):
        super().__init__(**kwargs)
        self._sm            = sm
        self._app           = app
        self.reset_average()

        # ===============================
        #           Main layout
        # ===============================
        layout              = FloatLayout(size_hint = [1.0, 1.0], pos_hint={'x': 0, 'y': 0})
        bg                  = Image(source=admin_config.app['background'], fit_mode="fill")
        layout.add_widget(bg)
        self._layout        = layout
        self._active        = False

        # ===============================
        #        Instructions widget
        # ===============================
        reminders_container             = FloatLayout(
            size_hint                   = [0.4, 0.80],
            pos_hint                    = {'center_x': 0.45, 'center_y': 0.75},
        )
        layout.add_widget(reminders_container)

        reminders_label                 = Label(
            size_hint                   = [0.20, 0.65],
            pos_hint                    = {'center_x': 0.5, 'center_y': 0.5},
            text                        = "Please position yourself within the camera frame",
            font_size                   = 25
        )
        reminders_container.add_widget(reminders_label)
        self.reminders_label            = reminders_label

        # ===============================
        #        Counter widget
        # ===============================
        count_container                 = InfoLayout(
            size_hint                   = [0.20, 0.35],
            pos_hint                    = {'x': 0.02, 'y': 0.525},
            title                       = 'Count:'
        )
        layout.add_widget(count_container)

        count_label                     = Label(
            text                        = '0',
            size_hint                   = [0.8, 0.8],
            pos_hint                    = {'center_x': 0.5, 'center_y': 0.5},
            font_name                   = admin_config.font_name[2],
            font_size                   = admin_config.font_size[3],
        )
        count_container.add_widget(count_label)
        self.count_label                = count_label

        # ===============================
        #        Exercise Icon
        # ===============================
        exer_container                  = InfoLayout(
            size_hint                   = [0.20, 0.35],
            pos_hint                    = {'x': 0.02, 'y': 0.125},
            title                       = 'Exercise:'
        )
        layout.add_widget(exer_container)

        exer_image                      = Image(
            size_hint                   = [0.8, 0.8],
            pos_hint                    = {'center_x': 0.5, 'center_y': 0.5},
            fit_mode                    = 'contain'
        )
        exer_container.add_widget(exer_image)
        self.exer_image                 = exer_image

        # ===============================
        #        Camera Display
        # ===============================
        camera                          = Image(
            size_hint                   = [0.4, 0.75],
            pos_hint                    = {'center_x': 0.45, 'center_y': 0.5},
        )
        self.camera                     = camera
        layout.add_widget(camera)

        # ===============================
        #        Info Display
        # ===============================

        info_container                  = InfoLayout(
            size_hint                   = [0.30, 0.75],
            pos_hint                    = {'right': 0.98, 'y': 0.125},
            title                       = 'Exercise Info:'
        )
        layout.add_widget(info_container)

        # ===============================
        #        Label Container
        # ===============================
        info_label_ctn                  = GridLayout(
            size_hint                   = [0.40, 0.375],
            pos_hint                    = {'x': 0.10, 'y': 0.575},
            cols                        = 1,
        )
        info_container.add_widget(info_label_ctn)
        
        info_label_exer                 = Label(
            size_hint                   = [None, None],
            font_size                   = admin_config.font_size[0],
            text                        = 'Exercise:',
            halign                      = 'left'
        )
        info_label_ctn.add_widget(info_label_exer)
        info_label_exer.bind(text_size  = info_label_exer.setter('size'))

        info_label_reps                 = Label(
            size_hint                   = [None, None],
            font_size                   = admin_config.font_size[0],
            text                        = 'Reps needed:',
            halign                      = 'left'
        )
        info_label_ctn.add_widget(info_label_reps)
        info_label_reps.bind(text_size  = info_label_reps.setter('size'))

        # ===============================
        #        Value Container
        # ===============================
        info_value_ctn                  = GridLayout(
            size_hint                   = [0.50, 0.375],
            pos_hint                    = {'x': 0.50, 'y': 0.575},
            cols                        = 1,
        )
        info_container.add_widget(info_value_ctn)
        
        info_value_exer                 = Label(
            size_hint                   = [None, None],
            font_size                   = admin_config.font_size[0],
            text                        = '',
            halign                      = 'left'
        )
        info_value_ctn.add_widget(info_value_exer)
        info_value_exer.bind(text_size  = info_value_exer.setter('size'))
        self.exer_label                 = info_value_exer

        info_value_reps                 = Label(
            size_hint                   = [None, None],
            font_size                   = 24,
            text                        = '0',
            halign                      = 'left'
        )
        info_value_ctn.add_widget(info_value_reps)
        info_value_reps.bind(text_size  = info_value_reps.setter('size'))
        self.reps_label                 = info_value_reps

        self.add_widget(layout)

        # ===============================
        #       Back button behavior
        # ===============================
        back_btn                = Button(
            background_normal   = user_config.button_params['bg_normal'],
            background_color    = user_config.button_params['bg_color'],
            color               = user_config.button_params['color'],
            text                = 'BACK',
            font_name           = admin_config.font_name[1],
            font_size           = admin_config.font_size[1],
            size_hint           = [0.16, 0.10],
            pos_hint            = {'x': 0.02, 'y': 0.005}
        )

        layout.add_widget(back_btn)
        back_btn.bind(on_press=self.show_exit_confirmation)
        BackButtonDispatch.on_release(back_btn, 'user_routine_selection', self._sm, 'right')

    # Handle the scoring process here
    def process_score(self, ret_code, angle, ideal_angle):
        score   = abs(angle - ideal_angle) / 360.0
        if ret_code == ReturnCode.SUCCESS:
            score   += 2.0
        return score

    def on_camera_update(self, tick):
        while True:
            if (not hasattr(self, '_loaded')) or (not self._loaded):
                self._loaded            = True
                break
            
            # Remove the duration check
            # if self.duration < tick:
            #     self.duration           = 0
            #     self.to_next_screen()
            #     return
            
            # Remove the duration decrement
            # self.duration              -= tick
            break

        ret_flag, frame                 = self.cam_viewer.read()
        if not ret_flag:
            return

        # Update camera feed.
        # Convert the frame to a format suitable for displaying in Kivy
        frame                           = cv2.flip(cv2.flip(frame, 0), 1)
        buffer                          = frame.tostring()
        texture1                        = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')

        # Update the Image widget with the new frame
        self.camera.texture             = texture1

        cv_texture                      = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        exercise                        = self.active_exercise
        self._cv_texture                = cv_texture
        if ((exercise is None) or (exercise.check is None)):
            self.run_instances         += 1
            return
        
        # try:
        #     # cur_exercise.check is defined
        #     ret_code            = exercise.check(cv_texture)

        #     self.run_average   += self.process_score(*ret_code)
        #     self.run_instances += 1

        #     if ret_code[0] == ReturnCode.SUCCESS:
        #         self.count  += 1
        # except:
        #     pass

    def inc_count(self, *args):
        self.count  += 1

    def request_process_feed(self):
        if not self._active:
            return
        
        self.img_proc_thread    = Thread(
            name                = "FitQuest-img-process",
            target              = self.process_feed,
            daemon              = True
        )
        self.img_proc_thread.start()

    def process_feed(self):
        while self._active:
            if not hasattr(self, '_cv_texture'):
                continue
        
            exercise            = self.active_exercise
            cv_texture          = self._cv_texture
            self._cv_texture    = None
            del self._cv_texture

            try:
                # cur_exercise.check is defined
                ret_code            = exercise.check(cv_texture)

                self.run_average   += self.process_score(*ret_code)
                self.run_instances += 1

                if ret_code[0] == ReturnCode.SUCCESS:
                    Clock.schedule_once(
                        self.inc_count,
                        0
                    )
            except:
                pass

    def load_exercise(self, deduct: bool = True) -> ExerciseDetails:
        rout_list   = self._app.post_routine()
        rout_list: RoutineDetails
        if rout_list is None:
            raise RuntimeError('''
                user/user_exercise_start.ExerciseScreen().load_exercise() >>
                    exercise_start page should be unreachable when no routines are loaded!
            ''')

        while len(rout_list.exercises) > 0:
                exercise             = rout_list.exercises[0]
                if deduct:
                    exercise.sets   -= 1

                if exercise.sets > -1:
                    return exercise
                rout_list.exercises.pop(0)

        return None

    def on_enter(self):
        self._active            = True
        self._loaded            = False

        self.run_average        = 0.0
        self.run_instances      = 0

        self.cam_viewer         = cv2.VideoCapture(0)
        self.cam_monitor        = Clock.schedule_interval(
            self.on_camera_update,
            self.tick_rate,
        )
        self.request_process_feed()

        exercise                = self.load_exercise()
        self.active_exercise    = exercise

        if exercise is None:
            return

        self.reps               = exercise.reps
        self.count              = 0
        self.exercise           = exercise.name
        # Remove the duration setting
        # self.duration           = exercise.duration
        self.exer_image.source  = exercise.img_path
        self._loaded            = False

    def on_pre_leave(self):
        self.cam_viewer.release()
        self.cam_viewer     = None
        del self.cam_viewer

        self.cam_monitor.cancel()
        del self.cam_monitor

        self.run_average        = 0.0
        self.run_instances      = 0

    def on_count(self, instance, value):
        self.count_label.text   = str(value)
        if ((value >= self.reps) and
            (self.reps > 0) and
            (self._active)):
            self.to_next_screen()

    def on_reps(self, instance, value):
        self.reps_label.text    = str(value)

    def on_exercise(self, instance, value):
        self.exer_label.text    = value

    def has_remaining_exercises(self):
        rout_list   = self._app.post_routine()
        rout_list: RoutineDetails
        return (rout_list.exercises[0].sets > 0) or (len(rout_list.exercises) > 1)
    
    def to_next_screen(self):
        self._active            = False

        self.exer_average['exercise'].append(self.active_exercise)
        try:
            self.exer_average['average'].append(self.run_average / self.run_instances)
        except ZeroDivisionError:
            self.exer_average['average'].append(0.0)

        self.active_exercise    = None
        self._sm.transition     = FadeTransition(duration=0.5)
        self._sm.current        = 'exercise_cooldown'
        self.active_exercise    = None
        self._sm.transition     = FadeTransition(duration=0.5)
        self._sm.current        = 'exercise_cooldown'

    def show_exit_confirmation(self, instance):
        # Pause camera updates and processing
        self._active = False
        self.cam_monitor.cancel()
        del self.cam_monitor

        modal_view = ModalView(size_hint=(None, None), size=(400, 200))
        content = BoxLayout(orientation='vertical', padding=10)
        text = Label(text="Do you want to exit this routine?")
        content.add_widget(text)

        buttons = BoxLayout(padding=10)
        yes_button = Button(text="Yes", on_press=self.confirm_exit)
        no_button = Button(text="No", on_press=self.dismiss_exit_confirmation)
        buttons.add_widget(yes_button)
        buttons.add_widget(no_button)
        content.add_widget(buttons)

        self.exit_confirmation_popup = Popup(
            title="Exit Confirmation",
            content=content,
            size_hint=(None, None),
            size=(400, 200),
            auto_dismiss=False  # Prevent automatic dismissal
        )
        self.exit_confirmation_popup.open()

    def confirm_exit(self, instance):
        self.dismiss_exit_confirmation(instance)
        self.redirect_to_routine_selection()

    def dismiss_exit_confirmation(self, instance):
        if self.exit_confirmation_popup is not None:
            self.exit_confirmation_popup.dismiss()
            self.active_exercise = None
           # Resume camera updates and processing
            self._active        = True
            self.cam_monitor    = Clock.schedule_interval(self.on_camera_update, self.tick_rate)
            self.exit_confirmation_popup = None  # Reset the reference to None

    def redirect_to_routine_selection(self):
        # Handle redirection to the specific screen or continue
        self.reset_average()
        self._sm.transition = SlideTransition(direction='right')
        self._sm.current    = 'user_routine_selection'
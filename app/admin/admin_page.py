from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.audio import SoundLoader
from kivy.metrics import dp

# Admin widgets and screens
from admin.admin_widgets import *
from admin.admin_dashboard import AdminDashboard

from routine_details import RoutineDetails

import admin.json_handler as json_handler
import admin.app_config as app_config

#   User config files
import user.user_config as user_config
import user.user_widgets as user_widgets

#   User pages
import user.user_selection as user_select_page
import user.user_routine_selection as user_select_routine
import user.user_premade_routine as user_premade_routine
import user.user_custom_routine as user_custom_routine
import user.user_exercise_pre_start as user_exercise_pre_start
import user.user_exercise_start as user_exercise_start
import user.user_exercise_cooldown as user_exercise_cooldown
import user.user_exercise_finished as user_exercise_finished

#   Pose detection
import user.load_pose_detection as load_pose_detection

exer_list_obj       = None
rout_list_obj       = None
user_list_obj       = None
exer_popup          = None
_app                = None
_app_data           = {
    'cur_exercise'  : None,
}


class MainScreen(Screen):
    def __init__(self, is_admin: bool = True, **kwargs):
        super().__init__(**kwargs)

        # Main layout
        layout = FloatLayout(size=(300, 300))

        # Background
        bg = Image(source=app_config.app['background'], fit_mode="cover")
        layout.add_widget(bg)

        # Logo
        logo = Image(source=app_config.app['logo'], pos_hint={
                     'center_x': 0.5, 'center_y': 0.8}, size_hint=(0.3, 0.3), fit_mode="fill")
        layout.add_widget(logo)

        # Buttons layout
        buttons = BoxLayout(orientation='vertical', spacing=10, size_hint=(
            0.50, 0.35), pos_hint={'center_x': 0.5, 'center_y': 0.4})

        user_btn = Button(
            text="User",
            height=50,
            background_normal=user_config.button_params['bg_normal'],
            background_color=user_config.button_params['bg_color'],
            color=user_config.button_params['color'],
            font_name=app_config.font_name[2],
        )
        user_btn.bind(on_press=self.user_btn_pressed)
        buttons.add_widget(user_btn)
        user_widgets.KivyPropHandler.on_font_size_change(
            user_btn, 0.1, 1.3, True)

        if (not is_admin):
            user_btn.text = "START!"

        if is_admin:
            admin_btn = Button(
                text="Admin",
                height=50,
                background_normal=user_config.button_params['bg_normal'],
                background_color=user_config.button_params['bg_color'],
                color=user_config.button_params['color'],
                font_name=app_config.font_name[2],
            )
            admin_btn.bind(on_press=self.admin_btn_pressed)
            buttons.add_widget(admin_btn)
            user_widgets.KivyPropHandler.on_font_size_change(
                admin_btn, 0.1, 1.3, True)

        layout.add_widget(buttons)

        # Add layout to screen
        self.add_widget(layout)

    def user_btn_pressed(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'user_selection'

    def admin_btn_pressed(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'admin_dashboard'


class MyApp(AppHandler):
    def __init__(self,
                 is_admin: bool = False,
                 debug_mode: bool = True,
                 override_play_music: bool = True):
        super(MyApp, self).__init__(title="FitQuest")
        global _app
        _app                = self
        self.is_admin       = is_admin
        self.debug_mode     = debug_mode
        self.play_music     = override_play_music or app_config.music['play']

    def load_user_app(self):
        # Grant access to the ScreenManager via shallow copy assignment.
        global user_list_obj
        self.user           = user_select_page.UserScreen(
            self._sm,
            name            = 'user_selection',
            user_handler    = user_list_obj,
        )
        self._sm.add_widget(self.user)

        self._sm.add_widget(
            user_select_routine.RoutineScreen(
                self._sm,
                name        = 'user_routine_selection'
            )
        )
        self._sm.add_widget(
            user_premade_routine.PremadeRoutineScreen(
                self._sm,
                self,
                name        = 'user_premade_routine'
            )
        )
        self._sm.add_widget(
            user_custom_routine.CustomRoutineScreen(
                self._sm,
                self,
                name='user_custom_routine'
            )
        )
        self._sm.add_widget(
            user_exercise_pre_start.CountdownScreen(
                self._sm,
                self,
                name='exercise_pre_start'
            )
        )

        self.exer_scr       = user_exercise_start.ExerciseScreen(
            self._sm,
            self,
            name            = 'exercise_start'
        )
        self._sm.add_widget(self.exer_scr)
        self._sm.add_widget(
            user_exercise_cooldown.CooldownScreen(
                self._sm,
                self,
                self.exer_scr.exer_average,
                self.exer_scr,
                name='exercise_cooldown'
            )
        )
        self._sm.add_widget(
            user_exercise_finished.SummaryScreen(
                self._sm,
                self,
                self.exer_scr.exer_average,
                self.exer_scr,
                self.user,
                name='exercise_finished'
            )
        )

    def load_sound(self):
        if (len(app_config.music['main_menu']) < 1):
            self.sound_active   = False
            return

        import random
        menu_index              = random.randint(0, len(app_config.music['main_menu']) - 1)
        self.sound              = SoundLoader.load(app_config.music['main_menu'][menu_index])
        self.sound_active       = True

        if (hasattr(self, 'sound') and self.sound):
            self.sound.bind(on_stop = self.on_sound_stop)
            self.sound.volume   = 0.6  # Set volume to 50%
            self.sound.play()
        else:
            print(f"FitQuest >> Unable to load the sound (path: {app_config.music['main_menu'][menu_index]})")
            app_config.music.pop(menu_index)
            self.load_sound()

    def build(self):
        sm          = ScreenManager()
        self._sm    = sm
        sm.add_widget(MainScreen(
            is_admin    = self.is_admin,
            name        = 'main_screen'
        ))

        if self.is_admin:
            global exer_list_obj, rout_list_obj, exer_popup, _app_data
            self.admin = AdminDashboard(
                name='admin_dashboard',
                app=self,
                exer_list=exer_list_obj,
                rout_list=rout_list_obj,
                popup=exer_popup,
                app_data=_app_data,
            )
            sm.add_widget(self.admin)

        self.load_user_app()
        self.exercise_list = []
        if self.is_admin and self.debug_mode:
            sm.current = app_config.debug_start_page

        # Load and play background music if requested
        if self.play_music:
            self.load_sound()

        return sm

    def on_sound_stop(self, sound):
        if self.sound_active:
            self.load_sound()

    def on_stop(self):
        # Stop the sound when the app is closed
        if (hasattr(self, 'sound') and self.sound):
            self.sound_active = False
            self.sound.stop()

    def send_routine(self, rout_data: RoutineDetails):
        self._routine = rout_data
        load_pose_detection.load(rout_data.exercises)

        if rout_data is None:
            self._routine_copy = None
            return

        self._routine_copy = []
        for elem in rout_data.exercises:
            self._routine_copy.append(elem)

    def post_routine(self, get_copy: bool = False) -> RoutineDetails:
        if not hasattr(self, '_routine'):
            return None
        if not get_copy:
            return self._routine
        try:
            return self._routine_copy
        except AttributeError:
            return None

class MyAppPreload:
    # def load_db(self):
    #     import sqlite3

    #     connection = sqlite3.connect(app_config.db['user_profile'])
    #     cursor = connection.cursor()

    #     with open(app_config.db_cursor['user_profile'], 'r') as content:
    #         user_sql = content.read()

    #     cursor.executescript(user_sql)

    #     connection.commit()
    #     connection.close()

    def __init__(self):
        # self.load_db()

        global exer_list_obj, rout_list_obj, user_list_obj, exer_popup
        user_list_obj   = json_handler.JSONUser()
        exer_list_obj   = json_handler.JSONExercise()
        rout_list_obj   = json_handler.JSONRoutine()

        exer_popup      = AdminPopup(title=app_config.popup["title"])
        exer_popup.set_body_text(app_config.popup["exercise"])

        exer_button = exer_popup.get_confirm_button()

        def on_confirm_delete(instance):
            global exer_list_obj, exer_popup, _app_data, _app
            exer_popup.popup.dismiss()
            exer_list_obj.remove_exercise(_app_data['cur_exercise'])
            _app_data['cur_exercise'] = None

            admin: AdminDashboard = _app.admin
            admin.draw_exercise_widgets()

        exer_button.bind(on_release=on_confirm_delete)

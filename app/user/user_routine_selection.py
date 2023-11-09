from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, SlideTransition, Screen
from kivy.metrics import dp


import user.user_config as user_config
import admin.app_config as admin_config
from admin.admin_widgets import *
from user.user_widgets import KivyPropHandler

from admin.admin_behavior import BackButtonDispatch

class RoutineScreen(Screen):
    _instance   = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance   = super(RoutineScreen, cls).__new__(cls, **kwargs)
        return cls._instance

    def __init__(self, sm: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self._sm    = sm

        # ===============================
        #           Main layout
        # ===============================
        layout              = FloatLayout(size=(300, 300))
        bg                  = Image(source=admin_config.app['background'], fit_mode="fill")
        layout.add_widget(bg)

        # ===============================
        #   Add logo at top left area
        # ===============================
        logo                = Image(
            source          = admin_config.app['logo'],
            fit_mode        = "contain",
            size_hint       = [None, None],
            size            = [192, 192],
            pos_hint        = {'x': 0.04, 'top': 1}
        )
        layout.add_widget(logo)

        # ===============================
        #           Select label
        # ===============================
        select_label        = Label(
            text            = 'SELECT YOUR ROUTINE',
            font_name       = admin_config.font_name[3],
            font_size       = admin_config.font_size[3],
            size_hint       = [0.48, 0.28],
            pos_hint        = {'center_x': 0.5, 'y': 0.48}
        )
        layout.add_widget(select_label)
        KivyPropHandler.on_font_size_change(select_label, 0.30, 1.8, maintain_ratio=True)

        # =======================================
        #           Option container
        # =======================================
        option_container    = GridLayout(
            cols            = 2,
            size_hint       = [0.90, 0.16],
            pos_hint        = {'center_x': 0.5, 'y': 0.37},
            spacing         = 10,
        )
        layout.add_widget(option_container)

        # =======================================
        #           Ready made routine
        # =======================================
        premade_btn             = Button(
            background_normal   = user_config.button_params['bg_normal'],
            background_color    = user_config.button_params['bg_color'],
            color               = user_config.button_params['color'],
            text                = 'READY-MADE ROUTINE',
            font_name           = admin_config.font_name[2],
            font_size           = admin_config.font_size[1],
        )
        option_container.add_widget(premade_btn)
        BackButtonDispatch.on_release(premade_btn, 'user_premade_routine', self._sm)
        KivyPropHandler.on_font_size_change(premade_btn, 0.10, 1.3, maintain_ratio=True)

        # =======================================
        #           Customized routine
        # =======================================
        custom_btn              = Button(
            background_normal   = user_config.button_params['bg_normal'],
            background_color    = user_config.button_params['bg_color'],
            color               = user_config.button_params['color'],
            text                = 'CUSTOMIZED ROUTINE',
            font_name           = admin_config.font_name[2],
            font_size           = admin_config.font_size[1],
        )
        option_container.add_widget(custom_btn)
        BackButtonDispatch.on_release(custom_btn, 'user_custom_routine', self._sm)
        KivyPropHandler.on_font_size_change(custom_btn, 0.10, 1.3, maintain_ratio=True)

        # =======================================
        #           Back button
        # =======================================
        back_btn                = Button(
            background_normal   = user_config.button_params['bg_normal'],
            background_color    = user_config.button_params['bg_color'],
            color               = user_config.button_params['color'],
            text                = 'BACK',
            font_name           = admin_config.font_name[2],
            # font_size           = admin_config.font_size[1],
            size_hint           = [0.16, 0.12],
            pos_hint            = {'x': 0.02, 'y': 0.02}
        )
        layout.add_widget(back_btn)
        BackButtonDispatch.on_release(back_btn, 'user_selection', self._sm, 'right')
        KivyPropHandler.on_font_size_change(back_btn, 0.20, 1.3, maintain_ratio=True)

        self.add_widget(layout)
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, SlideTransition, Screen
from kivy.metrics import dp

import user.user_config as user_config
import admin.app_config as admin_config
from admin.admin_widgets import *
from admin.json_handler import JSONUser
from user_details import UserDetails
from user.user_widgets import KivyPropHandler

from admin.admin_behavior import BackButtonDispatch

class UserScreen(Screen):
    '''
    This is a singleton class that displays a selection of registered
    users in the users list. Currently, that is statically fixed at 5,
    so any further changes down the line can easily be made.

    Additional user API has been provided for ease of access. These are:
    Methods:
        self.get_choice() -> UserDetails
        self.get_user_name(choice: UserDetails) -> str
        self.set_user_name(choice: UserDetails, value: str) -> str
        self.get_user_icon(choice: UserDetails) -> str
        self.set_user_icon(choice: UserDetails, img_path: str) -> str

    To refer to the singleton object, just call UserScreen().
    '''

    _instance   = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance   = super(UserScreen, cls).__new__(cls, **kwargs)
        return cls._instance

    def __init__(self, sm: ScreenManager, user_handler: JSONUser, **kwargs):
        super().__init__(**kwargs)
        self._sm            = sm
        self.user_handler   = user_handler

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
            size            = [240, 240],
            pos_hint        = {'x': 0.04, 'top': 1}
        )
        layout.add_widget(logo)

        # ===============================
        #   "WHO'S EXERCISING?" label
        # ===============================
        notice_label        = Label(
            text            = "WHO'S EXERCISING?",
            font_name       = admin_config.font_name[2],
            font_size       = admin_config.font_size[3],
            size_hint       = [0.44, 0.24],
            pos_hint        = {'center_x': 0.5, 'y': 0.56}
        )
        layout.add_widget(notice_label)

        self.add_widget(layout)

        # ===============================
        #       User Icon container:
        # ===============================
        icon_container      = GridLayout(
            cols            = user_handler.get_user_count(),
            rows            = 1,
            size_hint       = [0.80, 0.32],
            pos_hint        = {'center_x': 0.5, 'y': 0.264}
        )
        layout.add_widget(icon_container)
        self._users         = {
            'icons'         : {},
            'labels'        : {},
        }
        self._choice        = None

        for user in self.user_handler.extract_list():
            # ===============================
            #       User Icon BoxLayout:
            # ===============================
            box_container   = BoxLayout(
                size_hint   = [1.0 / icon_container.cols, 1.0],
                orientation = 'vertical',
                spacing     = 10,
            )
            icon_container.add_widget(box_container)

            # ===============================
            #       User Icons and Labels
            # ===============================
            user_icon               = ImageButton(
                size_hint           = [1.0, 0.75],
                pos_hint            = {'x': 0, 'y': 0.25},
                always_release      = True,
            )
            user_icon.set_image_source(user_config.user_icon)
            box_container.add_widget(user_icon)
            self._users['icons'][user]  = user_icon

            user_label              = Label(
                text                = user.username,
                font_name           = admin_config.font_name[0],
                font_size           = admin_config.font_size[0],
                size_hint           = [0.80, 0.25],
                pos_hint            = {'center_x': 0.5, 'y': 0}
            )
            box_container.add_widget(user_label)
            self._users['labels'][user] = user_label
            # KivyPropHandler.on_text_size_change(user_label, 0.88)
            KivyPropHandler.on_font_size_change(user_label, 0.20, 1.3, maintain_ratio=True)

            user_fg_color, user_fg  = None, None
            with box_container.canvas.after:
                user_fg_color       = Color(0.1, 0.1, 0.1, 0)
                user_fg             = Rectangle(pos=box_container.pos, size=box_container.size)

            # ===============================
            #       User Icon behavior
            # ===============================
            def bind_factory(self, user_icon, box_container, user_fg, user_fg_color, user):
                def on_icon_press(instance):
                    user_fg_color.rgba[3]       = 0.35

                def on_icon_release(instance):
                    user_fg_color.rgba[3]       = 0
                    self._choice                = user
                    self._sm.transition         = SlideTransition(direction="left")
                    self._sm.current            = 'user_routine_selection'

                def on_icon_size(instance, size):
                    user_fg.size            = size
                def on_icon_pos(instance, pos):
                    user_fg.pos             = pos

                box_container.bind(size     = on_icon_size)
                box_container.bind(pos      = on_icon_pos)
                user_icon.bind(on_press     = on_icon_press)
                user_icon.bind(on_release   = on_icon_release)

            bind_factory(self, user_icon, box_container, user_fg, user_fg_color, user)
        
        # ===============================
        #       Back button behavior
        # ===============================
        back_btn   = Button(
            text                = 'BACK',
            font_name           = admin_config.font_name[2],
            font_size           = admin_config.font_size[1],
            background_normal   = user_config.button_params['bg_normal'],
            background_color    = user_config.button_params['bg_color'],
            color               = user_config.button_params['color'],
            size_hint           = [0.16, 0.12],
            pos_hint            = {'x': 0.02, 'y': 0.02},
        )
        layout.add_widget(back_btn)
        BackButtonDispatch.on_release(back_btn, 'main_screen', self._sm, 'right')

    # =====================================================
    #                   User API
    # =====================================================
    def get_choice(self) -> UserDetails|None:
        return self._choice
    
    def get_user_name(self, choice = None):
        '''
        Gets the user name.
        '''
        choice  = ((choice is None) and self._choice) or choice
        try:
            return self._users['labels'][choice].text
        except KeyError:
            return ""
    
    def set_user_name(self, choice = None, name: str = "Regular User"):
        '''
        Sets the user name.
        '''
        choice  = ((choice is None) and self._choice) or choice
        try:
            self._users['labels'][choice].text  = name
        except KeyError:
            pass

    def get_user_icon(self, choice = None):
        '''
        Gets the image texture path of the icon button.
        '''
        choice  = ((choice is None) and self._choice) or choice
        try:
            return self._users['icons'][choice].source
        except KeyError:
            return ""
    
    def set_user_icon(self, choice = None, img_path: str = ""):
        '''
        Sets the image texture of the icon button based on the
        supplied path (img_path).
        '''
        choice  = ((choice is None) and self._choice) or choice
        try:
            self._users['icons'][choice].source = img_path
        except KeyError:
            pass

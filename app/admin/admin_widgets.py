from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ToggleButtonBehavior

from kivy.properties import OptionProperty, BooleanProperty, NumericProperty, ColorProperty

from kivy.graphics import Rectangle, Color

from kivy.core.window import Window

from kivy.clock import Clock

import admin.app_config as app_config

class IntInput(TextInput):
    def __init__(self, **kwargs):
        super(IntInput, self).__init__(**kwargs)

    def insert_text(self, substr, from_undo=False):
        # TO-DO: Solve conversion problem from str to bytes.
        try:
            int(substr)
        except ValueError:
            return ""
        
        return super(IntInput, self).insert_text(substr, from_undo=from_undo)

class LeftLabel(Label):
    def __init__(self, **kwargs):
        super(LeftLabel, self).__init__(**kwargs)
        if not 'height' in kwargs:
            self.height         = 50
            self.size_hint_y    = None
        self.halign             = 'left'
        self.valign             = 'center'

    def on_size(self, instance, size):
        self.text_size      = size

class ImageButton(Button):
    fit_mode    = OptionProperty(
        "contain", options=["scale-down", "fill", "contain", "cover"]
    )

    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)

        self.background_normal  = ""
        self.background_color   = [0,0,0,0]
        self.text               = ""
        self.emphasis           = False

        self._image             = Image(size=self.size, pos=self.pos, fit_mode=self.fit_mode)
        self._image.color       = [1,1,1,1]

        with self.canvas.after:
            self._color         = Color(0.05, 0.05, 0.05, 0)
            self._color_rect    = Rectangle(size=self.size, pos=self.pos)

        self.add_widget(self._image)

    def get_image_source(self) -> str:
        return self._image.source
    
    def set_image_source(self, image_path: str):
        self._image.source      = image_path
    
    def on_press(self):
        if not self.emphasis:
            self._color.rgba[3] = 0.50

    def on_release(self):
        if not self.emphasis:
            self._color.rgba[3] = 0

    def on_size(self, instance, size):
        if hasattr(instance, '_image'):
            instance._image.size    = size
        if hasattr(instance, '_color_rect'):
            instance._color_rect.size   = size

    def on_pos(self, instance, pos):
        if hasattr(instance, '_image'):
            instance._image.pos     = pos
        if hasattr(instance, '_color_rect'):
            instance._color_rect.pos    = pos

    def on_fit_mode(self, instance, value):
        if not hasattr(self, '_image'):
            return
        self._image.fit_mode    = value

    def set_emphasis(self, flag):
        self.emphasis           = flag
        if flag:
            self._color.rgba[3] = 0.50
        else:
            self._color.rgba[3] = 0

class ImageButton2(ToggleButtonBehavior, Image):
    hovered         = BooleanProperty(False)
    focus_counter   = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ImageButton2, self).__init__(**kwargs)
        self.always_release     = True
        self.prev_state         = self.state

        with self.canvas:
            self._color         = Color(0, 0, 0, 0)
            self._color_rect    = Rectangle(
                pos             = self.pos,
                size            = self.size,
            )

    def on_press(self, *args):
        self.focus_counter   += 1

    def on_release(self, *args):
        self.focus_counter   -= 1

    def on_focus_counter(self, instance, counter):
        if counter > 0:
            self._color.rgba[3] = 0.35
        else:
            self._color.rgba[3] = 0
        self.canvas.ask_update()

    def on_size(self, instance, size):
        if not hasattr(self, '_color_rect'):
            return
        self._color_rect.size   = size

    def on_pos(self, instance, pos):
        if not hasattr(self, '_color_rect'):
            return
        self._color_rect.pos    = pos

    def on_state(self, instance, state):
        if self.state == self.prev_state:
            return
        
        self.prev_state = self.state
        if self.state == 'down':
            self.focus_counter  += 1
        else:
            self.focus_counter  -= 1

class BGFloatLayout(FloatLayout):
    def __init__(self, **kwargs):
        self.border_size        = 0

        super(BGFloatLayout, self).__init__(**kwargs)
        with self.canvas:
            self.border_color       = Color(1,1,1,1)
            self.border_rect        = Rectangle(pos=self.pos, size=self.size)
            self.bg_color           = Color(0,0,0,1)
            self.bg_rect            = Rectangle(pos=self.pos, size=self.size)

    def on_pos(self, instance, pos):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos            = pos
        if hasattr(self, 'border_rect'):
            self.border_rect.pos        = [pos[0] - self.border_size,
                                           pos[1] - self.border_size]

    def on_size(self, instance, size):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size           = size
        if hasattr(self, 'border_rect'):
            self.border_rect.size       = [size[0] + 2*self.border_size,
                                           size[1] + 2*self.border_size]

class BGButton(Button):
    bg_color            = ColorProperty([0.5, 0.5, 0.5, 0.0])
    bg_down_color       = ColorProperty([0.4, 0.4, 0.4, 0.8])
    bg_disabled         = ColorProperty([0.4, 0.4, 0.4, 0.0])
    bg_down_disabled    = ColorProperty([0.3, 0.3, 0.3, 0.4])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color               = [1.0, 1.0, 1.0, 0.0]
        self.background_normal              = ""
        self.background_down                = ""
        self.background_disabled_normal     = ""
        self.background_disabled_down       = ""
        self.halign                         = "center"
        self.valign                         = "middle"
        self.bind(background_color          = self._request_update)
        self.bind(size                      = self.setter("text_size"))

    def on_press(self):
        if self.disabled:
            self.background_color   = self.bg_down_disabled
        else:
            self.background_color   = self.bg_down_color

    def on_release(self):
        if self.disabled:
            self.background_color   = self.bg_disabled
        else:
            self.background_color   = self.bg_color

    def _request_update(self, instance, listvalue):
        self.canvas.ask_update()

    def on_bg_color(self, instance, color):
        if (self.state == 'normal') and (not self.disabled):
            self.background_color   = self.bg_color

    def on_bg_down_color(self, instance, color):
        if (self.state == 'down') and (not self.disabled):
            self.background_color   = self.bg_down_color

    def on_bg_disabled(self, instance, color):
        if (self.state == 'normal') and (self.disabled):
            self.background_color   = self.bg_disabled

    def on_bg_down_disabled(self, instance, color):
        if (self.state == 'down') and (self.disabled):
            self.background_color   = self.bg_down_disabled

class RoutineExerWidget(BGFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bg_color.rgba  = app_config.admin_page['routine_manager']['bg_color']
        self.border_size    = 2

        self._content       = FloatLayout(
            size_hint       = [0.90, 0.90],
            pos_hint        = {'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self._content)

        # ===========================
        #       Left-side content
        # ===========================
        left_layout             = GridLayout(
            size_hint           = [0.40, 1.0],
            pos_hint            = {'x': 0, 'y': 0},
            cols                = 1,
            row_default_height  = 25,
            row_force_default   = True
        )
        self._content.add_widget(left_layout)

        exer_label              = LeftLabel(
            text                = "Exercise:",
            font_size           = 16,
            height              = 25
        )
        left_layout.add_widget(exer_label)

        self.exer_button        = ToggleButton(
            text                = "-- List --",
            font_size           = 16,
            group               = 'exercise_select_group',
        )
        left_layout.add_widget(self.exer_button)

        # ===========================
        #       Right-side content
        # ===========================
        right_layout            = GridLayout(
            size_hint           = [0.55, 0.90],
            pos_hint            = {'x': 0.45, 'center_y': 0.5},
            cols                = 2,
            row_default_height  = 25,
            row_force_default   = True,
        )
        self._content.add_widget(right_layout)
        # self._content.bind(size = self.on_content_size)

        right_layout.add_widget(LeftLabel(text = "Reps:", font_size = 16, height = 20))
        right_layout.add_widget(IntInput(text = "10", font_size = 12))
        right_layout.add_widget(LeftLabel(text = "Sets:", font_size = 16, height = 20))
        right_layout.add_widget(IntInput(text = "2", font_size = 12))

    def bind(self, **kwargs):
        click_callback      = kwargs.pop('on_click', None)
        release_callback    = kwargs.pop('on_release', None)

        if click_callback:
            self.exer_button.bind(on_click      = click_callback)
        if release_callback:
            self.exer_button.bind(on_release    = release_callback)

        super().bind(**kwargs)

    def unbind(self, **kwargs):
        click_callback      = kwargs.pop('on_click', None)
        release_callback    = kwargs.pop('on_release', None)
        
        if click_callback:
            self.exer_button.unbind(on_click  = click_callback)
        if release_callback:
            self.exer_button.unbind(on_release  = release_callback)

        super().unbind(**kwargs)

class DropdownOption(FloatLayout):
    _show_counter   = NumericProperty(1)
    _recursion      = NumericProperty(0)
    clear_when_hide = BooleanProperty(True)
    default_height  = NumericProperty(50)
    
    def __init__(self, **kwargs):
        self._selection                 = None
        self._parent                    = None

        super().__init__(**kwargs)

        self._scroll                    = ScrollView(
            size_hint                   = [1.0, None],
            pos_hint                    = {'x': 0, 'y': 0}
        )
        self.add_widget(self._scroll)

        self._grid                      = GridLayout(
            size_hint           = [1.0, None],
            pos_hint            = {'x': 0, 'y': 0},
            cols                = 1,
            row_default_height  = self.default_height
        )
        self._scroll.add_widget(self._grid)
        self._grid.bind(minimum_height  = self.on_min_height)

    def add_option(self, arg_text: str  = ""):
        option                  = ToggleButton(
            pos_hint            = {'x': 0, 'y': 0},
            group               = self,
            text                = arg_text,
        )
        self._grid.add_widget(option)
        option.bind(on_release  = self.on_select_option)

    def show(self, flag: bool = True, on_toggle_mode: bool = True):
        if on_toggle_mode:
            self._show_counter  = 1 if flag else 0
        else:
            increment           = 1 if flag else -1
            self._show_counter += increment

    def on_height(self, instance, height):
        height              = height if (self._show_counter > 0) else 0
        self._scroll.height = height

    def on_min_height(self, instance, min_height):
        min_height          = min_height if (self._show_counter > 0) else 0
        self._grid.height   = min_height

    def on_size(self, instance, size):
        if self._recursion > 0:
            return
        
        if self._show_counter <= 0:
            self._recursion    += 1
            self.size           = [0, 0]
            self._recursion    -= 1

    def on__show_counter(self, instance, counter):
        if counter == 0:
            self._saved_fields  = {
                'size_hint'     : self.size_hint,
                'size'          : self.size,
            }
            self.size_hint      = [None, None]
            self.size           = [0, 0]
            self.opacity        = 0

        elif counter == 1:
            if hasattr(self, '_saved_fields'):
                self.size       = self._saved_fields['size']
                self.size_hint  = self._saved_fields['size_hint']
                self.opacity    = 1
                del self._saved_fields

        # if self._show_counter == 1:
        #     self._scroll.height = self.height
        #     self._grid.height   = self._grid.minimum_height
        #     return

        # self._saved_fields  = {
        #     'size_hint'     : self.size_hint,
        #     'size'          : self.size,
        # }
        # self._scroll.height = 0
        # self._grid.height   = 0
        # if self.clear_when_hide:
        #     self.clear_selection()

    def on_default_height(self, instance, height):
        self._grid.row_default_height   = height

    # This one's overrideable.
    def on_select(self, instance):
        pass

    def on_select_option(self, instance, *args):
        if instance.state   == 'normal':
            self._selection = None
        else:
            self._selection = instance
            self.on_select(instance)

    def clear_selection(self):
        if self._selection is not None:
            self._selection.state   = 'normal'
        self._selection  = None

    def get_selection(self) -> ToggleButton:
        return self._selection
    
    def set_parent(self, parent):
        '''
        Sets the quasi-parent of the widget, which controls the
        position of the widget.
        '''
        if parent == self:
            return

        # For now, assume dropdown only.
        if self._parent is not None:
            self._parent.unbind(pos = self._on_parent_pos)

        self._parent            = parent
        self._parent.bind(pos   = self._on_parent_pos)

    def _on_parent_pos(self, parent, pos):
        self.pos        = [parent.pos[0], parent.pos[1] - self.height]
    
class AdminPopup:
    def __init__(self, **kwargs):
        self.popup              = Popup(**kwargs)
        self.popup.size_hint    = (None, None)
        self.popup.size         = (360, 240)

        content                 = FloatLayout(size=self.popup.size)

        # Create Label text:
        body_text               = Label(
            size_hint           = [1.0, 0.8],
            pos_hint            = {'x': 0.0, 'y': 0.2},
            valign              = 'top',
            halign              = 'left',
        )
        content.add_widget(body_text)

        def on_body_text_size(instance, size):
            instance.text_size  = size
        body_text.text_size     = body_text.size
        body_text.bind(size=on_body_text_size)

        self._body_text         = body_text

        # Create container for Confirm and Cancel buttons
        btn_container           = GridLayout(size_hint=[1.0, 0.2], cols=2, pos_hint={'x': 0, 'y': 0})
        content.add_widget(btn_container)

        # Create confirm and cancel buttons
        confirm_button          = Button(text="Confirm")
        cancel_button           = Button(text="Cancel")
        self._confirm           = confirm_button
        btn_container.add_widget(confirm_button)
        btn_container.add_widget(cancel_button)

        cancel_button.bind(on_release=self.popup.dismiss)
        self.popup.content      = content

    def get_body_text(self) -> str:
        return self._body_text.text
    
    def set_body_text(self, value: str):
        self._body_text.text    = value

    def get_confirm_button(self):
        return self._confirm

    def open(self):
        self.popup.open()

class AppHandler(App):
    aspect_ratio    = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super(AppHandler, self).__init__(**kwargs)

        self._watcher   = Clock.schedule_interval(
            self.update_aspect_ratio,
            0,
        )

    def update_aspect_ratio(self, *args):
        self.aspect_ratio       = AppHandler.get_raw_aspect_ratio()

    def get_raw_aspect_ratio():
        width, height           = Window.width, Window.height
        if height == 0:
            aspect_ratio        = 100.0
        else:
            aspect_ratio        = width / height
        return aspect_ratio
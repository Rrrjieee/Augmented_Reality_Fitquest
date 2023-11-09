from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.properties import StringProperty, NumericProperty, BoundedNumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, PushMatrix, PopMatrix, Rotate

import user.user_config as cfg
import admin.app_config as admin_config
from admin.admin_widgets import BGFloatLayout, AppHandler

class RotateLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._angle = 0
        with self.canvas.before:
            PushMatrix()
            Rotate(angle=self._angle, origin=self.center)
        with self.canvas.after:
            PopMatrix()

    def set_angle(self, angle: float):
        self._angle = angle
        self.canvas.before.clear()
        self.canvas.after.clear()
        with self.canvas.before:
            PushMatrix()
            Rotate(angle=self._angle, origin=self.center)
        with self.canvas.after:
            PopMatrix()

class BGLabel(RotateLabel):
    def __init__(self, **kwargs):
        super(BGLabel, self).__init__(**kwargs)

        self.font_name      = cfg.font_name
        self._font_scale    = -1.0
        self._font_size     = 48
        self.rect_radius    = (0, 0, 0, 0)

        with self.canvas.before:
            self.rect_color = Color(1, 1, 1, 1)
            self.rect       = RoundedRectangle(
                pos         = self.pos,
                size        = self.size,
                radius      = self.rect_radius
            )

    def on_size(self, instance, size):
        self.rect.size      = size
        if (self._font_scale < 0.0):
            instance.font_size  = self._font_size
        else:
            instance.font_size  = self._font_scale*size[0]

    def on_pos(self, instance, pos):
        self.rect.pos       = pos

    def change_color(self,
                     color: (float, float, float, float)
                     = (1, 1, 1, 1)):
        self.color          = color

    def change_bg_color(self,
                        color: (float, float, float, float)
                        = (1, 1, 1, 1)):
        self.rect_color.rgba    = color

    def set_bg_radius(self,
                      radius: (float, float, float, float)
                      = (5, 5, 5, 5)):
        self.rect_radius    = radius
        self.rect.radius    = radius

    def set_font_size(self, fixed: bool = True,
                      new_size: float = 48):
        if (fixed):
            self._font_size     = new_size
        else:
            self._font_scale    = new_size
            self.font_size      = new_size*self.size[0]

    def get_bg_radius(self) -> int:
        return self.rect_radius
    
    def get_font_size(self, fixed: bool = True) -> float:
        return ((fixed) and self._font_size) or self._font_scale

class InvisibleButton(Button):
    def __init__(self, **kwargs):
        super(InvisibleButton, self).__init__(**kwargs)

        self.opacity    = 0
        self.background_normal          = ""
        self.background_down            = ""
        self.background_disabled_normal = ""
        self.background_disabled_down   = ""

class ScrollableOption(BGFloatLayout):
    text            = StringProperty("Title")
    font_name       = StringProperty(admin_config.font_name[2])
    font_size       = NumericProperty(20)
    spacing         = NumericProperty(25)
    cols            = BoundedNumericProperty(2,    min=0, allownone=False)
    rows            = BoundedNumericProperty(None, min=0, allownone=True)

    def __init__(self, **kwargs):
        super(ScrollableOption, self).__init__(**kwargs)

        self.bg_color.rgba      = cfg.button_params['light_color']
        self.bg_color.rgba[3]   = 0.75

        self._cabaret           = BGFloatLayout(
            size_hint           = [1.0, 0.2],
            pos_hint            = {'x': 0, 'y': 0.8},
        )
        self.add_widget(self._cabaret)

        self._cabaret.bg_color.rgba     = cfg.button_params['color']
        self._cabaret.bg_color.rgba[3]  = 0.75

        # ========================================
        #           Make label
        # ========================================
        self._title             = Label(
            text                = self.text,
            font_size           = self.font_size,
            font_name           = self.font_name,
            size_hint           = [1.0, 1.0],
            pos_hint            = {'x': 0, 'y': 0}
        )
        self._cabaret.add_widget(self._title)

        # ========================================
        #       Label made, make GridLayout
        # ========================================
        self._grid_container    = FloatLayout(
            size_hint           = [0.80, 0.60],
            pos_hint            = {'center_x': 0.5, 'y': 0.05}
        )
        self.add_widget(self._grid_container)

        self._scroll            = ScrollView(
            size_hint           = [1.0, None],
            do_scroll_x         = False,
            pos_hint            = {'x': 0, 'center_y': 0.5}
        )
        self._grid_container.add_widget(self._scroll)

        self._grid              = GridLayout(
            cols                = self.cols,
            rows                = self.rows,
            size_hint           = [1.0, None],
            pos_hint            = {'center_x': 0.5, 'y': 0.1},
            spacing             = self.spacing,
        )
        self._scroll.add_widget(self._grid)

        grid                        = self._grid
        self._grid_container.bind(height    = self._scroll.setter("height"))
        grid.bind(minimum_height    = grid.setter("height"))

    def on_text(self, instance, value):
        if not hasattr(self, '_title'):
            return
        self._title.text        = value
    
    def on_font_size(self, instance, value):
        if not hasattr(self, '_title'):
            return
        self._title.font_size   = value

    def on_font_name(self, instance, name):
        if not hasattr(self, '_title'):
            return
        self._text.font_name    = name

    def on_cols(self, instance, value):
        if not hasattr(self, '_grid'):
            return
        self._grid.cols         = value

    def on_rows(self, instance, value):
        if not hasattr(self, '_grid'):
            return
        self._grid.rows         = value

    def on_spacing(self, instance, value):
        if not hasattr(self, '_grid'):
            return
        self._grid.spacing      = value

    def add_grid_widget(self, widget):
        if not hasattr(self, '_grid'):
            return
        self._grid.add_widget(widget)

    def remove_grid_widget(self, widget):
        if not hasattr(self, '_grid'):
            return
        self._grid.remove_widget(widget)

    def clear_grid_widget(self, children = None):
        if not hasattr(self, '_grid'):
            return
        self._grid.clear_widgets(children)

    def get_grid_container(self):
        if not hasattr(self, '_grid_container'):
            return None
        return self._grid_container

# Used in user_exercise_start
class InfoLayout(BGFloatLayout):
    title   = StringProperty("No Title")
    def __init__(self, **kwargs):
        super(InfoLayout, self).__init__(**kwargs)
        self.bg_color.rgba              = cfg.button_params['light_color']

        self._cabaret                   = BGFloatLayout(
            size_hint                   = [1.0, 0.35],
            pos_hint                    = {'x': 0, 'y': 0.65}
        )
        self._cabaret.bg_color.rgba     = cfg.button_params['dark_color']
        self.add_widget(self._cabaret)

        self._label                     = Label(
            text                        = self.title,
            size_hint                   = [1, 1],
            pos_hint                    = {'x': 0, 'y': 0},
            font_size                   = admin_config.font_size[4],
        )
        self._cabaret.add_widget(self._label)

        content                         = FloatLayout(
            size_hint                   = [1.0, 0.65],
            pos_hint                    = {'x': 0, 'y': 0}
        )
        self.add_widget(content)
        self._content                   = content

    def add_widget(self, widget):
        if not hasattr(self, '_content'):
            return super(InfoLayout, self).add_widget(widget)
        return self._content.add_widget(widget)
    
    def remove_widget(self, widget):
        if not hasattr(self, '_content'):
            super(InfoLayout, self).remove_widget(widget)
            return
        
        if ((widget == self._cabaret) or
            (widget == self._content)):
            return
        super(InfoLayout, self).remove_widget(widget)

    def on_title(self, instance, title):
        if not hasattr(self, "_label"):
            return
        self._label.text                = title

class KivyPropHandler:
    def on_font_size_change(widget,
                            scale_factor: float = 0.1,
                            min_ar_for_maintain: float = 1.0,
                            maintain_ratio: bool = False):
        def on_size(widget, size):
            end_scale           = scale_factor
            aspect_ratio        = AppHandler.get_raw_aspect_ratio()
            if maintain_ratio:
                end_scale      /= aspect_ratio
                if aspect_ratio < min_ar_for_maintain:
                    end_scale  *= aspect_ratio
                    end_scale  /= min_ar_for_maintain
            widget.font_size    = size[0]*end_scale

        widget.bind(size = on_size)

    def on_text_size_change(widget, scale_factor: float = 0.10, maintain_ratio: bool = False):
        def on_size(widget, size):
            widget.text_size    = [widget.size[0] * scale_factor, widget.size[1] * scale_factor]
        widget.bind(text_size   = on_size)
# =================================
#       Import Kivy Widgets
# =================================
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.metrics import dp

from kivy.clock import Clock

# =================================
#       Import local files
# =================================
import admin.app_config as app_config

from admin.json_handler import ExerciseDetails, RoutineDetails
from admin.admin_widgets import *

class ExerciseTabs:
    @staticmethod
    def add_exercise_tab(admin: Screen, tab_panel: TabbedPanel):
        if (not isinstance(admin, AdminDashboard)):
            return None
        tab                 = TabbedPanelItem(text='Add Exercises', font_size=app_config.tab['font_size'])
        
        # Content of Tab 1
        tab_content         = BoxLayout(orientation='vertical')
        tab.add_widget(tab_content)
        
        # Button to add new exercise

        def show_success_popup():
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(text="Exercise added successfully!"))

            popup = Popup(title="Success", content=content, size_hint=(None, None), size=(400, 200))
            popup.open()

        def on_exercise_defined(instance):
            if (not admin._name.text) or (int(admin._reps.text) <= 0) or (int(admin._sets.text) <= 0) or (int(admin._dur.text) <= 0):
                # Create an error label
                error_label = Label(text="Please fill in all fields.", color=(1, 0, 0, 1))

                # Check if the error layout already exists, if not, create it
                if not hasattr(admin, '_error_layout'):
                    error_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=50)
                    admin._error_layout = error_layout
                    tab_content.add_widget(error_layout)

                # Create an empty BoxLayout for spacing
                spacing_layout = BoxLayout(size_hint_y=None, height=-100)

                # Clear any previous content in the error layout
                admin._error_layout.clear_widgets()

                # Add the spacing layout and error label to the error layout
                admin._error_layout.add_widget(spacing_layout)
                admin._error_layout.add_widget(error_label)

                # Schedule a function to remove the error layout and error label after a delay
                def remove_error_layout(dt):
                    if hasattr(admin, '_error_layout'):
                        tab_content.remove_widget(admin._error_layout)
                        delattr(admin, '_error_layout')
                Clock.schedule_once(remove_error_layout, 3)  # Adjust the delay as needed (3 seconds in this example)
                return

            admin.exer_list.add_exercise(
                admin._name.text,
                int(admin._reps.text),
                int(admin._sets.text),
                int(admin._dur.text),
                admin._desc.text
            )
            Clock.schedule_once(
                admin.on_addexer_text_clear,
                0.0,
            )
            admin.draw_exercise_widgets()

            # Show the success pop-up
            show_success_popup()

        add_exercise_btn    = Button(text='Add New Exercise', size_hint_y=None, height=50)
        add_exercise_btn.bind(on_release=on_exercise_defined)
        tab_content.add_widget(add_exercise_btn)
        

        # Table (using GridLayout)
        table               = GridLayout(cols=2, row_force_default=True, row_default_height=60, spacing=[0,5])
        admin._table        = table
        admin.draw_table()
        tab_content.add_widget(table)

        return tab

    @staticmethod
    def manage_exercise_tab(admin: Screen, tab_panel: TabbedPanel):
        if (not isinstance(admin, AdminDashboard)):
            return None
        tab                         = TabbedPanelItem(text='Manage Exercises', font_size=app_config.tab['font_size'])
        base_layout                 = FloatLayout(
            size_hint               = [1.0, 1.0],
        )
        tab.add_widget(base_layout)

        bg_layout                   = BGFloatLayout(
            size_hint               = [0.72, 0.84],
            pos_hint                = {'center_x': 0.5, 'center_y': 0.5}            
        )
        base_layout.add_widget(bg_layout)

        bg_layout.border_size       = 5
        bg_layout.bg_color.rgba     = [0.16, 0.16, 0.16, 1]
        bg_layout.border_color.rgba = [0.35, 0.35, 0.35, 1]

        # =================================
        #       Create exercise manager
        # =================================

        manager_layout              = FloatLayout(
            size_hint               = [0.88, 0.88],
            pos_hint                = {'center_x' : 0.5, 'center_y': 0.5}
        )
        bg_layout.add_widget(manager_layout)

        # =================================
        #           Left Layout
        # =================================
        scroll_layout               = FloatLayout(
            size_hint               = [0.28, 1.0],
            pos_hint                = {'x' : 0, 'y': 0}
        )
        manager_layout.add_widget(scroll_layout)

        scroll                      = ScrollView(
            size_hint_x             = 1.0,
            size_hint_y             = None,
            do_scroll_y             = True,
            pos_hint                = {'center_x' : 0.5, 'center_y': 0.5}
        )
        scroll_layout.add_widget(scroll)

        box                         = GridLayout(
            cols                    = 1,
            size_hint               = [1.0, None],
            pos_hint                = {'x': 0, 'y': 0},
            row_default_height      = app_config.admin_page['exercise_manager']['selection_height'],
            row_force_default       = True,
        )
        admin._exercise_box         = box
        scroll.add_widget(box)

        scroll_layout.bind(height   = scroll.setter('height'))
        box.bind(minimum_height     = box.setter("height"))

        # =================================
        #           Right Layout
        # =================================
        panel_layout                = FloatLayout(
            size_hint               = app_config.admin_page['exercise_manager']['panel_layout_size'],
            pos_hint                = {'x': 0.32, 'y': 0}
        )
        manager_layout.add_widget(panel_layout)

        admin._exer_fields          = {}
        admin._exer_panel           = panel_layout
        admin._cur_exercise         = None

        # =================================
        #    Store Reps, Sets and Duration
        #    fields inside a GridLayout
        # =================================
        panel_grid                  = GridLayout(
            size_hint               = [1.0, 0.32],
            pos_hint                = {'x': 0, 'y': 0.68},
            cols                    = 2,
        )
        panel_layout.add_widget(panel_grid)

        # Add reps field.
        panel_grid.add_widget(LeftLabel(text    = 'Repetitions:'))
        admin._exer_fields['reps']              = IntInput()
        panel_grid.add_widget(admin._exer_fields['reps'])

        # Add sets field.
        panel_grid.add_widget(LeftLabel(text    = 'Sets:'))
        admin._exer_fields['sets']              = IntInput()
        panel_grid.add_widget(admin._exer_fields['sets'])

        # Add duration field.
        panel_grid.add_widget(LeftLabel(text    = 'Duration:'))
        admin._exer_fields['duration']          = IntInput()
        panel_grid.add_widget(admin._exer_fields['duration'])

        # Add description field.
        panel_desc_grid             = GridLayout(
            size_hint               = [1.0, 0.64],
            pos_hint                = {'x': 0, 'y': 0},
            cols                    = 1
        )
        panel_layout.add_widget(panel_desc_grid)

        desc_label                  = LeftLabel(
            text            = 'Description:',
            height          = 50,
        )
        desc_label.bind(size        = desc_label.setter('text_size'))

        panel_desc_grid.add_widget(desc_label)
        admin._exer_fields['description']       = TextInput()
        panel_desc_grid.add_widget(admin._exer_fields['description'])

        # =================================
        #       Exercise box done
        # =================================
        def on_entry_save(instance):
            exercise                = admin._cur_exercise
            if exercise is None:
                return
            
            exer_fields             = admin._exer_fields
            exercise.reps           = int(exer_fields['reps'].text)
            exercise.sets           = int(exer_fields['sets'].text)
            exercise.duration       = int(exer_fields['duration'].text)
            exercise.description    = exer_fields['description'].text

            admin.exer_list.update()

        save_btn = Button(text="Save", size_hint=[None, None], size=(100, 50), pos_hint={'right': 1, 'y': 0})
        save_btn.bind(on_press=on_entry_save)
        base_layout.add_widget(save_btn)

        admin.draw_exercise_widgets()
        # =================================
        #       Floating Delete Button
        # =================================
        del_button                  = ImageButton2(
            size_hint               = [None, None],
            size                    = [40, 40],
            pos_hint                = {'right': 1.0, 'y': 0.50},
            source                  = app_config.path['icons']['delete'],
        )
        panel_layout.add_widget(del_button)
        def on_bind_del_button(del_button: ImageButton2):
            def on_del_request(instance):
                nonlocal admin
                admin.app_data['cur_exercise'] = admin._cur_exercise.name
                admin.popup.open()
            del_button.bind(on_release=on_del_request)
            
        on_bind_del_button(del_button)
        return tab
    
class RoutineTabs:
    @staticmethod
    def add_routine_tab(admin: Screen, tab_panel: TabbedPanel):
        if (not isinstance(admin, AdminDashboard)):
            return None
        
        admin._routine_elements     = {}
        tab                         = TabbedPanelItem(text='Add Routine', font_size=app_config.tab['font_size'])

        base_layout                 = FloatLayout(
            size_hint               = [1.0, 1.0],
        )
        tab.add_widget(base_layout)

        def create_add_routine_tab_left(admin, base_layout):
            # Create left side area
            left_layout                 = GridLayout(
                size_hint               = [0.55, 0.90],
                pos_hint                = {'x': 0.05, 'y': 0.05},
                cols                    = 1,
            )
            base_layout.add_widget(left_layout)

            # Routine text layout:
            rout_name_layout            = GridLayout(
                rows                    = 1,
                cols                    = 2,
                size_hint               = [1.0, 0.08],
                pos_hint                = {'x': 0, 'y': 0}
            )
            left_layout.add_widget(rout_name_layout)

            # Routine text section:
            rout_name_label             = Label(
                text                    = 'Routine Name:',
                font_name               = app_config.font_name[0],
                font_size               = app_config.font_size[0],
                size_hint               = [0.36, 1.0],
                pos_hint                = {'x': 0, 'y': 0},
                valign                  = 'top',
            )
            rout_name_layout.add_widget(rout_name_label)

            rout_name_text              = TextInput(
                font_name               = app_config.font_name[0],
                font_size               = app_config.font_size[0],
                size_hint               = [0.64, 1.0],
                pos_hint                = {'x': 0, 'y': 0}
            )
            rout_name_layout.add_widget(rout_name_text)
            admin._routine_elements['name']  = rout_name_text

            # Routine text description layout:
            rout_desc_layout            = GridLayout(
                rows                    = 2,
                cols                    = 1,
                size_hint               = [1.0, 0.88],
                pos_hint                = {'x': 0, 'y': 0}
            )
            left_layout.add_widget(rout_desc_layout)

            # Routine text description section:
            rout_desc_label             = Label(
                text                    = 'Routine Description:',
                font_name               = app_config.font_name[0],
                font_size               = app_config.font_size[0],
                size_hint               = [1.0, 0.08],
                pos_hint                = {'x': 0, 'y': 0},
                valign                  = 'center',
                halign                  = 'left'
            )
            rout_desc_layout.add_widget(rout_desc_label)

            rout_desc_text              = TextInput(
                font_name               = app_config.font_name[0],
                font_size               = app_config.font_size[0],
                size_hint               = [1.0, 0.92],
                pos_hint                = {'x': 0, 'y': 0}
            )
            rout_desc_layout.add_widget(rout_desc_text)
            admin._routine_elements['description']   = rout_desc_text

            # Make sure rout_name_label is positioned to the left.
            # Make sure rout_desc_label is positioned to the left.
            rout_name_label.bind(size=rout_name_label.setter('text_size'))
            rout_desc_label.bind(size=rout_desc_label.setter('text_size'))
        
        def create_add_routine_tab_right(admin, base_layout):
            # Create right side area
            right_layout                = BGFloatLayout(
                size_hint               = [0.30, 0.90],
                pos_hint                = {'x': 0.65, 'y': 0.05},
            )
            right_layout.border_size        = 4
            right_layout.bg_color.rgba      = [141/255, 73/255, 209/255, 1]
            right_layout.border_color.rgba  = [0.1, 0.1, 0.1, 1]
            base_layout.add_widget(right_layout)

            # Create content layout:
            content_layout              = BGFloatLayout(
                size_hint               = [0.80, 0.72],
                pos_hint                = {'center_x': 0.5, 'y': 0.24}
            )
            content_layout.border_size          = 4
            content_layout.bg_color.rgba        = app_config.admin_page['routine_manager']['bg_color']
            content_layout.border_color.rgba    = [0.1, 0.1, 0.1, 1]
            right_layout.add_widget(content_layout)

            # Create a label showing "Exercise":
            content_label_bg                    = BGFloatLayout(
                size_hint                       = [1.00, 0.16],
                pos_hint                        = {'x': 0, 'y': 0.84}
            )
            content_label_bg.bg_color.rgba      = app_config.admin_page['routine_manager']['bg_color_dark']
            content_layout.add_widget(content_label_bg)
            content_label                       = Label(
                text                            = 'EXERCISES:',
                font_size                       = app_config.font_size[2],
                font_name                       = app_config.font_name[2],
                size_hint                       = [1.0, 1.0],
                pos_hint                        = {'x': 0, 'y': 0}
            )
            content_label_bg.add_widget(content_label)

            # ===================================
            #       Display exercise content
            # ===================================
            exercise_layout                     = FloatLayout(
                size_hint                       = [0.92, 0.76],
                pos_hint                        = {'center_x': 0.5, 'y': 0.04}
            )
            content_layout.add_widget(exercise_layout)

            exercise_scroll                     = ScrollView(
                size_hint_x                     = 1.0,
                size_hint_y                     = None,
                do_scroll_y                     = True,
                pos_hint                        = {'center_x': 0.5, 'center_y': 0.5}
            )
            exercise_layout.add_widget(exercise_scroll)

            # Note to self and others:
            #   Set the Exercise Scroll's height through the parent.
            #   The child GridLayout's height through its minimum height.
            exercise_grid                       = GridLayout(
                size_hint_x                     = 1.0,
                size_hint_y                     = None,
                pos_hint                        = {'x': 0, 'y': 0},
                cols                            = 1,
                row_default_height              = 64,
                spacing                         = [0, 10]
            )
            exercise_scroll.add_widget(exercise_grid)

            exercise_layout.bind(height         = exercise_scroll.setter('height'))
            exercise_grid.bind(minimum_height   = exercise_grid.setter('height'))

            exercise_options                    = DropdownOption(
                size_hint                       = [0.50, 0.36],
                pos_hint                        = {'x': 0, 'y': 0},
            )
            exer_list                           = admin.exer_list.extract_list()
            for exercise in exer_list:
                exercise_options.add_option(arg_text    = exercise.name)

            # content_layout.add_widget(exercise_options)
            exercise_options.show(False)

            add_exercise_btn                    = BGButton(
                text                            = 'Add New Exercise',
                size_hint_y                     = None,
                color                           = [0, 0, 0, 1]
            )
            add_exercise_btn.bg_color           = [1.0, 1.0, 1.0, 1.0]
            exercise_grid.add_widget(add_exercise_btn)
            
            def new_exer_factory(add_exercise_btn, grid):
                def on_add_exercise(instance):
                    # print("Click")
                    # ============================
                    #       Create widget
                    # ============================
                    exer_widget             = RoutineExerWidget()
                    exercise_grid.add_widget(exer_widget, 1)
                    exercise_options.set_parent(add_exercise_btn)
                    exercise_options.show(True)
                    print("Exercise options shown")
                    # exercise_options.pos    = [exer_widget.pos[0], exer_widget.pos[1] - exercise_options.height]

                add_exercise_btn.bind(on_release = on_add_exercise)

            new_exer_factory(add_exercise_btn, exercise_grid)

        create_add_routine_tab_left(admin, base_layout)
        create_add_routine_tab_right(admin, base_layout)
        return tab

    @staticmethod
    def manage_routine_tab(admin: Screen, tab_panel: TabbedPanel):
        if (not isinstance(admin, AdminDashboard)):
            return None
        tab             = TabbedPanelItem(text='Manage Routines', font_size=app_config.tab['font_size'])
        admin._tab       = tab
        admin.draw_routine_table()
        return tab
    
class AdminDashboard(Screen):
    def __init__(self, **kwargs):
        self.app            = kwargs.pop('app', None)
        self.exer_list      = kwargs.pop('exer_list', None)
        self.rout_list      = kwargs.pop('rout_list', None)
        self.popup          = kwargs.pop('popup', None)
        self.app_data       = kwargs.pop('app_data', {})

        super().__init__(**kwargs)
        
        # Main layout
        layout              = FloatLayout(size=(300, 300))
        self.add_widget(layout)

        # Background
        bg                  = Image(source=app_config.app['bg_logo'], fit_mode="fill")
        layout.add_widget(bg)
        
        # Tabbed Panel
        tab_panel           = TabbedPanel(
            pos_hint        = {'center_x': 0.5,'center_y': 0.42},
            size_hint       = (0.8, 0.72),
            do_default_tab  = False,
            tab_width       = 200
        )
        layout.add_widget(tab_panel)
        
        # Tab 1: Add Exercises
        self.create_tab(ExerciseTabs.add_exercise_tab, tab_panel)
        # Tab 2: Add Routine
        self.create_tab(RoutineTabs.add_routine_tab, tab_panel)
        # Tab 3: Manage Exercises
        self.create_tab(ExerciseTabs.manage_exercise_tab, tab_panel)
        # Tab 4: Manage Routine
        self.create_tab(RoutineTabs.manage_routine_tab, tab_panel)
        
        # Back Button
        back_btn = Button(text="Back", size_hint=(None, None), size=(100, 50), pos_hint={'right': 1, 'y': 0})
        back_btn.bind(on_press=self.back_btn_pressed)
        layout.add_widget(back_btn)
    
    def create_tab(self, fun, tab_panel: TabbedPanel):
        tab_item    = fun(self, tab_panel)
        tab_panel.add_widget(fun(self, tab_panel))
        
    def on_addexer_text_clear(self, *args):
        self._name.text = ""
        self._reps.text = ""
        self._sets.text = ""
        self._dur.text  = ""
        self._desc.text = ""

    def clear_panel_values(self):
        if not hasattr(self, '_exer_fields'):
            return
        exer_fields     = self._exer_fields
        exer_fields['reps'].text        = ""
        exer_fields['sets'].text        = ""
        exer_fields['duration'].text    = ""
        exer_fields['description'].text = ""

    def draw_exercise_widgets(self):
        if not hasattr(self, '_exercise_box'):
            return

        box                 = self._exercise_box
        box.clear_widgets()
        
        exer_list           = self.exer_list.extract_list()
        for exercise in exer_list:
            exer_btn        = ToggleButton(
                group       = 'exercises',
                text        = exercise.name
            )
            
            box.add_widget(exer_btn)
            def option_factory(exer_btn, self, exercise):
                def on_option_click(instance, *args):
                    exer_panel, exer_fields = self._exer_panel, self._exer_fields
                    if instance.state == 'normal':
                        if not exer_panel.hidden:
                            out_anim            = Animation(
                                size_hint_x     = 0,
                                opacity         = 0,
                                d               = 0.25,
                                t               = 'linear'
                            )
                            out_anim           &= Animation(
                                size_hint_y     = 0,
                                d               = 0.25,
                                t               = 'in_quart'
                            )
                            out_anim.start(exer_panel)
                            self.clear_panel_values()
                        exer_panel.hidden       = True
                        self._cur_exercise      = None
                        return
                    
                    # Option selected.
                    if exer_panel.hidden:
                        _size_hint              = app_config.admin_page['exercise_manager']['panel_layout_size']

                        in_anim                 = Animation(
                            size_hint_x         = _size_hint[0],
                            opacity             = 1,
                            d                   = 0.25,
                            t                   = 'linear'
                        )
                        in_anim                &= Animation(
                            size_hint_y         = _size_hint[1],
                            d                   = 0.25,
                            t                   = 'in_quart'
                        )
                        in_anim.start(exer_panel)
                    exer_panel.hidden           = False
                    self._cur_exercise          = exercise

                    # Update parameter values
                    exer_fields['reps'].text        = str(exercise.reps)
                    exer_fields['sets'].text        = str(exercise.sets)
                    exer_fields['duration'].text    = str(exercise.duration)
                    exer_fields['description'].text = exercise.description

                exer_btn.bind(on_release = on_option_click)
            option_factory(exer_btn, self, exercise)

        if not hasattr(self, '_exer_panel'):
            return
        exer_panel              = self._exer_panel
        exer_panel.size_hint    = [0, 0]
        exer_panel.opacity      = 0
        exer_panel.hidden       = True

    def draw_table(self):
        table               = self._table 

        # Name input.
        table.add_widget(Label(text="Name of Exercise:", height=30))
        self._name          = TextInput(multiline=False, height=30)
        table.add_widget(self._name)

        # Repetitions input.
        table.add_widget(Label(text="Reps:"))
        self._reps          = IntInput(multiline=False)
        table.add_widget(self._reps)

        # Sets input.
        table.add_widget(Label(text="Sets:"))
        self._sets          = IntInput(multiline=False)
        table.add_widget(self._sets)

        # Duration input.
        table.add_widget(Label(text="Duration:"))
        self._dur           = IntInput(multiline=False)
        table.add_widget(self._dur)

        # Description input.
        table.add_widget(Label(text="Description:"))
        self._desc          = TextInput()
        table.add_widget(self._desc)
    
    def draw_routine_table(self):
        tab             = self._tab
        tab.clear_widgets()

        rout_list       = self.rout_list.extract_list()
        if (len(rout_list) == 0):
            tab_content     = Label(text='Here, you can manage ready made routines.')  # Replace with your content
            tab.add_widget(tab_content)
            return

    def back_btn_pressed(self, instance):
        self.on_addexer_text_clear()
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current    = 'main_screen'
 
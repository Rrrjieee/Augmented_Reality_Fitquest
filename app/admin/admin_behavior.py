from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition

class BackButtonDispatch:
    def on_release(back_btn, screen_page, screen_manager,
                   trans_effect = "left",
                   pre_trans_effect = None,
                   post_trans_effect = None):
        
        def on_btn_release(instance):
            if (hasattr(pre_trans_effect, '__call__')):
                try:
                    pre_trans_effect()
                except:
                    pass

            # Apply transition effects.
            # If trans_effect is a function, call trans_effect
            if (hasattr(trans_effect, '__call__')):
                try:
                    trans_effect()
                except:
                    pass

            # If trans_effect is a string, apply SlideTransition
            elif (isinstance(trans_effect, str)):
                screen_manager.transition   = SlideTransition(direction=trans_effect)

            elif (trans_effect is None):
                screen_manager.transition   = NoTransition()

            screen_manager.current  = screen_page

            if (hasattr(post_trans_effect, '__call__')):
                try:
                    post_trans_effect()
                except:
                    pass

        back_btn.bind(on_release = on_btn_release)

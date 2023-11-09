if __name__ == "__main__":
    from admin.admin_page import MyAppPreload, MyApp
    
    MyAppPreload()
    _app    = MyApp(debug_mode = False)
    _app.run()
import flet as ft
from flet import AppView

# This is a configuration file for the Flet mobile app packaging

def main(page: ft.Page):
    # Configure the page for mobile
    page.title = "SafeWayAI"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 400
    page.window_height = 800
    page.window_resizable = False
    page.window_always_on_top = False
    
    # Import and run the main app
    from main_flet import main as app_main
    app_main(page)

# This is used by the Flet packager
ft.app(target=main, view=AppView.FLET_APP)

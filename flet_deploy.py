import flet as ft
from ui.app import SafeWayAIApp

def main(page: ft.Page):
    # Initialize the SafeWayAI app
    app = SafeWayAIApp(page)

# Start the app with a web server
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)

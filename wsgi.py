import flet as ft
from ui.app import SafeWayAIApp

def main(page: ft.Page):
    # Initialize the SafeWayAI app
    app = SafeWayAIApp(page)

# This is the WSGI application callable
app = lambda: ft.app(target=main, view=ft.AppView.WEB_BROWSER)

# For local testing
if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)

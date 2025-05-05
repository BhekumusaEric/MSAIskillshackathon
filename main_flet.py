import flet as ft
from ui.app import SafeWayAIApp
import os

def main():
    # Set environment variable to increase timeout
    os.environ["FLET_VIEW_TIMEOUT"] = "120"  # 120 seconds timeout

    # Print debug information
    print("Starting SafeWayAI application...")

    # Run the application with a specific port
    ft.app(target=SafeWayAIApp, view=ft.WEB_BROWSER, port=8576)

if __name__ == "__main__":
    main()

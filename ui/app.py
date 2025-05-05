import flet as ft
from ui.screens.home_screen import HomeScreen
from ui.screens.login_screen import LoginScreen
from ui.screens.improved_map_screen import ImprovedMapScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.chat_screen import ChatScreen
from ui.screens.navigation_screen import NavigationScreen
from services.data_manager import DataManager

class SafeWayAIApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_user = None
        self.data_manager = None

        # Initialize navigation-related variables
        self.current_route = None
        self.current_safety_analysis = None
        self.current_start_location = None
        self.current_end_location = None

        self.init_app()

    def init_app(self):
        # Configure the app
        self.page.title = "SafeWayAI"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0

        print("App: Initializing app")

        # Set up theme colors
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.BLUE,
            visual_density=ft.VisualDensity.COMFORTABLE,
        )

        print("App: Theme set")

        # Create screens
        self.screens = {
            "login": LoginScreen(self),
            "home": HomeScreen(self),
            "map": ImprovedMapScreen(self),
            "chat": ChatScreen(self),
            "settings": SettingsScreen(self),
            "navigation": NavigationScreen(self)
        }

        # Store references to specific screens for easier access
        self.map_screen = self.screens["map"]
        self.navigation_screen = self.screens["navigation"]

        print("App: Screens created")

        # Create a simple container for content
        self.content = ft.Container(expand=True)
        print("App: Content container created")

        # Create navigation rail
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=300,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="Home"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.MAP_OUTLINED,
                    selected_icon=ft.icons.MAP,
                    label="Map"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.CHAT_OUTLINED,
                    selected_icon=ft.icons.CHAT,
                    label="Emergency Chat"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
                    label="Settings"
                ),
            ],
            on_change=self.nav_change,
            visible=False  # Initially hidden for login screen
        )
        print("App: Navigation rail created")

        # Add the main layout to the page
        self.page.add(
            ft.Row(
                [
                    self.nav_rail,
                    ft.VerticalDivider(width=1),
                    self.content,
                ],
                expand=True
            )
        )
        print("App: Main layout added to page")

        # Start with login screen
        print("App: Navigating to login screen")
        self.navigate_to("login")

    # Navigation methods

    def nav_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.navigate_to("home")
        elif index == 1:
            self.navigate_to("map")
        elif index == 2:
            self.navigate_to("chat")
        elif index == 3:
            self.navigate_to("settings")

    def navigate_to(self, screen_name):
        print(f"App: Navigating to {screen_name}")

        # Check if user is logged in for protected screens
        if screen_name != "login" and not self.current_user:
            # Redirect to login if not logged in
            print(f"App: User not logged in, redirecting to login screen")
            screen_name = "login"

        try:
            # Hide navigation rail for login screen
            if screen_name == "login":
                print("App: Hiding navigation rail for login screen")
                self.nav_rail.visible = False
            else:
                print("App: Showing navigation rail")
                self.nav_rail.visible = True

            # Call will_unmount on the current screen if it exists
            if hasattr(self.content, "content") and self.content.content is not None:
                current_screen = self.content.content
                if hasattr(current_screen, "will_unmount"):
                    try:
                        current_screen.will_unmount()
                    except Exception as e:
                        print(f"App: Error calling will_unmount: {e}")

            # Update content
            print(f"App: Setting content to {screen_name} screen")
            if screen_name in self.screens:
                self.content.content = self.screens[screen_name]

                # Call did_mount on the new screen if it exists
                new_screen = self.screens[screen_name]
                if hasattr(new_screen, "did_mount"):
                    try:
                        new_screen.did_mount()
                    except Exception as e:
                        print(f"App: Error calling did_mount: {e}")

                print(f"App: Content set to {screen_name} screen")
            else:
                print(f"App: Error - screen {screen_name} not found in screens dictionary")
                print(f"App: Available screens: {list(self.screens.keys())}")

            # Update the page
            print("App: Updating page")
            self.page.update()
            print("App: Page updated")
        except Exception as e:
            print(f"App: Error navigating to {screen_name}: {e}")
            # Try to recover by going to login screen
            try:
                self.content.content = self.screens["login"]
                self.nav_rail.visible = False
                self.page.update()
            except Exception as ex:
                print(f"App: Error recovering: {ex}")

    def update_ui(self, func):
        """Execute a function in the main UI thread"""
        # This is a helper method to ensure UI updates happen in the main thread
        func()

    def logout(self):
        # Log out the user
        if self.data_manager:
            self.data_manager.logout()

        self.current_user = None
        self.navigate_to("login")

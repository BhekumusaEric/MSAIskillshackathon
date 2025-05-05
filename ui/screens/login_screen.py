import flet as ft
from services.data_manager import DataManager

class LoginScreen(ft.Container):
    def __init__(self, app):
        self.app = app
        self.data_manager = DataManager()

        # Create login form controls
        self.username = ft.TextField(
            label="Username",
            border_radius=8,
            filled=True,
            prefix_icon=ft.icons.PERSON,
            width=300,
            hint_text="Default: admin",
        )

        self.password = ft.TextField(
            label="Password",
            border_radius=8,
            filled=True,
            password=True,
            prefix_icon=ft.icons.LOCK,
            width=300,
            hint_text="Default: admin123",
        )

        self.login_button = ft.ElevatedButton(
            text="Login",
            icon=ft.icons.LOGIN,
            on_click=self.login,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.all(20),
            ),
            width=300,
        )

        # Create error text
        self.error_text = ft.Text(
            "",
            color=ft.colors.RED,
            size=14,
            visible=False,
        )

        # Create the main layout
        super().__init__(
            content=ft.Column(
                [
                    ft.Text("SafeWayAI", size=40, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                    ft.Text("Your safety companion", size=16, italic=True),
                    ft.Divider(height=40, color=ft.colors.TRANSPARENT),
                    self.username,
                    self.password,
                    self.error_text,
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    self.login_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

    def login(self, e):
        # Simple validation
        if not self.username.value or not self.password.value:
            self.error_text.value = "Please enter username and password"
            self.error_text.visible = True
            self.update()
            return

        # Show loading indicator
        self.login_button.text = "Logging in..."
        self.login_button.disabled = True
        self.error_text.visible = False
        self.update()

        # Add debug message
        print(f"Attempting to login with username: {self.username.value}")

        try:
            # Authenticate user
            login_success = self.data_manager.login(self.username.value, self.password.value)
            print(f"Login success: {login_success}")

            if login_success:
                # Set the current user in the app
                self.app.current_user = self.data_manager.get_current_user()
                print(f"Current user set: {self.app.current_user}")

                self.app.data_manager = self.data_manager
                print("Data manager set in app")

                # Navigate to home screen using the update_ui method to ensure thread safety
                print("Navigating to home screen")
                self.app.update_ui(lambda: self.app.navigate_to("home"))
                print("Navigation complete")
            else:
                # Show error message
                print("Login failed - invalid credentials")
                self.error_text.value = "Invalid username or password"
                self.error_text.visible = True
                self.login_button.text = "Login"
                self.login_button.disabled = False
                self.update()
        except Exception as ex:
            # Show error message with exception details
            print(f"Login error: {ex}")
            self.error_text.value = f"Error during login: {str(ex)}"
            self.error_text.visible = True
            self.login_button.text = "Login"
            self.login_button.disabled = False
            self.update()

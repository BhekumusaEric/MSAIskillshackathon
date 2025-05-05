import flet as ft
import threading
import time

class SafetyStatus(ft.Container):
    def __init__(self, on_panic=None):
        self.on_panic = on_panic
        self.is_safe = True
        self.safety_score = 90
        self.status_message = "You are in a safe area"

        # Create the safety indicator
        self.safety_indicator = ft.Container(
            width=20,
            height=20,
            border_radius=10,
            bgcolor=ft.colors.GREEN,
        )

        # Create the safety score progress bar
        self.safety_progress = ft.ProgressBar(
            value=0.9,  # 90%
            color=ft.colors.GREEN,
            bgcolor=ft.colors.GREY_300,
            width=200,
        )

        # Create the status message
        self.status_text = ft.Text(
            self.status_message,
            size=16,
        )

        # Create the panic button
        self.panic_button = ft.ElevatedButton(
            text="PANIC",
            icon=ft.icons.WARNING_ROUNDED,
            on_click=self.trigger_panic,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.RED,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.all(20),
            ),
        )

        # Create the main layout
        super().__init__(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self.safety_indicator,
                            ft.Text("Safety Status:", weight=ft.FontWeight.BOLD),
                            self.status_text,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    ft.Row(
                        [
                            ft.Text("Safety Score:", weight=ft.FontWeight.BOLD),
                            self.safety_progress,
                            ft.Text(f"{self.safety_score}/100"),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    ft.Row(
                        [
                            self.panic_button,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ],
                spacing=16,
            ),
            padding=20,
            border_radius=8,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLACK12,
            ),
        )

    def update_safety(self, is_safe, safety_score, status_message):
        # Update the safety status
        self.is_safe = is_safe
        self.safety_score = safety_score
        self.status_message = status_message

        # Update the UI
        self.safety_indicator.bgcolor = ft.colors.GREEN if is_safe else ft.colors.RED
        self.safety_progress.value = safety_score / 100
        self.safety_progress.color = ft.colors.GREEN if safety_score >= 70 else (
            ft.colors.ORANGE if safety_score >= 40 else ft.colors.RED
        )
        self.status_text.value = status_message

        self.update()

    def trigger_panic(self, e):
        # Show confirmation dialog
        def confirm_panic(e):
            # Close the dialog
            self.page.dialog.open = False
            self.page.update()

            # Show loading indicator
            self.panic_button.text = "Sending Alert..."
            self.panic_button.disabled = True
            self.update()

            # Simulate sending panic alert
            # For simplicity, let's just call the method directly
            # This avoids the threading issues with UI updates
            self.show_panic_sent_and_callback()

        def cancel_panic(e):
            # Close the dialog
            self.page.dialog.open = False
            self.page.update()

        # Show confirmation dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Confirm Emergency Alert"),
            content=ft.Text("Are you sure you want to send an emergency alert?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_panic),
                ft.TextButton("Send Alert", on_click=confirm_panic),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def show_panic_sent_and_callback(self):
        # Update the panic button
        self.panic_button.text = "PANIC"
        self.panic_button.disabled = False

        # Show success message
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Emergency alert sent successfully!"),
            action="OK",
        )
        self.page.snack_bar.open = True

        # Call the callback if provided
        if self.on_panic:
            self.on_panic()

        self.page.update()

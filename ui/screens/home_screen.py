import flet as ft
import threading
import time
from ui.components.safety_status import SafetyStatus

class HomeScreen(ft.Container):
    def __init__(self, app):
        self.app = app

        # Create the safety status component
        self.safety_status = SafetyStatus(on_panic=self.handle_panic)

        # Create recent incidents list
        self.incidents_list = ft.ListView(
            spacing=10,
            padding=20,
            auto_scroll=True,
        )

        # Add some sample incidents
        self.add_sample_incidents()

        # Create the main layout
        super().__init__(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Welcome to SafeWayAI", size=24, weight=ft.FontWeight.BOLD),
                                ft.Text("Your personal safety companion", size=16),
                            ],
                            spacing=4,
                        ),
                        padding=20,
                        bgcolor=ft.colors.BLUE,
                        border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                self.safety_status,
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text("Recent Incidents", size=20, weight=ft.FontWeight.BOLD),
                                            self.incidents_list,
                                        ],
                                        spacing=10,
                                    ),
                                    padding=20,
                                    border_radius=8,
                                    bgcolor=ft.colors.WHITE,
                                    shadow=ft.BoxShadow(
                                        spread_radius=1,
                                        blur_radius=15,
                                        color=ft.colors.BLACK12,
                                    ),
                                ),
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                text="Plan Route",
                                                icon=ft.icons.MAP,
                                                on_click=lambda e: self.app.navigate_to("map"),
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=8),
                                                    padding=ft.padding.all(20),
                                                ),
                                            ),
                                            ft.ElevatedButton(
                                                text="Report Incident",
                                                icon=ft.icons.REPORT_PROBLEM,
                                                on_click=self.show_report_dialog,
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=8),
                                                    padding=ft.padding.all(20),
                                                ),
                                            ),
                                            ft.ElevatedButton(
                                                text="Emergency Chat",
                                                icon=ft.icons.CHAT,
                                                on_click=lambda e: self.app.navigate_to("chat"),
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=8),
                                                    padding=ft.padding.all(20),
                                                    bgcolor=ft.colors.RED,
                                                    color=ft.colors.WHITE,
                                                ),
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    ),
                                    padding=20,
                                ),
                            ],
                            spacing=16,
                        ),
                        padding=20,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
        )

    def add_sample_incidents(self):
        # Add some sample incidents
        incidents = [
            {
                "type": "Robbery",
                "location": "Main Street, Johannesburg",
                "time": "Today, 10:30 AM",
                "severity": "High",
                "color": ft.colors.RED,
            },
            {
                "type": "Suspicious Activity",
                "location": "Park Avenue, Pretoria",
                "time": "Yesterday, 8:15 PM",
                "severity": "Medium",
                "color": ft.colors.ORANGE,
            },
            {
                "type": "Traffic Accident",
                "location": "Highway N1, Midrand",
                "time": "Yesterday, 5:45 PM",
                "severity": "Medium",
                "color": ft.colors.ORANGE,
            },
            {
                "type": "Power Outage",
                "location": "Central District, Sandton",
                "time": "2 days ago, 9:20 PM",
                "severity": "Low",
                "color": ft.colors.YELLOW,
            },
        ]

        for incident in incidents:
            self.incidents_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=incident["color"]),
                                    ft.Text(incident["type"], weight=ft.FontWeight.BOLD, size=16),
                                    ft.Container(
                                        content=ft.Text(incident["severity"], color=ft.colors.WHITE, size=12),
                                        bgcolor=incident["color"],
                                        padding=ft.padding.all(4),
                                        border_radius=4,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                spacing=10,
                            ),
                            ft.Text(incident["location"]),
                            ft.Text(incident["time"], size=12, color=ft.colors.GREY),
                        ],
                        spacing=4,
                    ),
                    padding=10,
                    border_radius=8,
                    bgcolor=ft.colors.WHITE,
                    border=ft.border.all(1, ft.colors.GREY_300),
                )
            )

    def handle_panic(self):
        # Update safety status
        self.safety_status.update_safety(
            is_safe=False,
            safety_score=30,
            status_message="Emergency alert sent to authorities",
        )

    def show_report_dialog(self, e):
        # Create the report form
        incident_type = ft.Dropdown(
            label="Incident Type",
            options=[
                ft.dropdown.Option("Robbery"),
                ft.dropdown.Option("Assault"),
                ft.dropdown.Option("Suspicious Activity"),
                ft.dropdown.Option("Traffic Accident"),
                ft.dropdown.Option("Fire"),
                ft.dropdown.Option("Medical Emergency"),
                ft.dropdown.Option("Power Outage"),
                ft.dropdown.Option("Other"),
            ],
            width=300,
        )

        # Create a dropdown for severity
        severity = ft.Dropdown(
            label="Severity",
            width=300,
            options=[
                ft.dropdown.Option("Low"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("High"),
            ],
            value="Medium",  # Default value
        )

        location = ft.TextField(
            label="Location",
            width=300,
            hint_text="Enter address or landmark",
        )

        # Add latitude and longitude fields (hidden by default)
        latitude = ft.TextField(
            label="Latitude",
            width=145,
            value="-26.2041",  # Default to Johannesburg
            visible=False,
        )

        longitude = ft.TextField(
            label="Longitude",
            width=145,
            value="28.0473",  # Default to Johannesburg
            visible=False,
        )

        # Add a button to use current location
        use_location_btn = ft.ElevatedButton(
            text="Use Current Location",
            icon=ft.icons.MY_LOCATION,
            on_click=lambda e: self.use_current_location(location, latitude, longitude),
        )

        description = ft.TextField(
            label="Description",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=300,
            hint_text="Describe what happened...",
        )

        # Add a photo upload button
        photo_btn = ft.ElevatedButton(
            text="Add Photo",
            icon=ft.icons.PHOTO_CAMERA,
            on_click=lambda e: self.show_photo_dialog(),
        )

        # Add a checkbox for anonymous reporting
        anonymous_check = ft.Checkbox(
            label="Report anonymously",
            value=False,
        )

        def submit_report(e):
            # Validate form
            if not incident_type.value or not location.value or not description.value:
                self.app.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please fill in all fields"),
                    action="OK",
                )
                self.app.page.snack_bar.open = True
                self.app.page.update()
                return

            # Close the dialog
            self.app.page.dialog.open = False
            self.app.page.update()

            # Show loading indicator
            self.app.page.snack_bar = ft.SnackBar(
                content=ft.Text("Submitting report..."),
            )
            self.app.page.snack_bar.open = True
            self.app.page.update()

            # Create incident data
            incident_data = {
                "type": incident_type.value,
                "description": description.value,
                "location": location.value,
                "latitude": float(latitude.value),
                "longitude": float(longitude.value),
                "severity": severity.value,
                "status": "active",
            }

            # If not anonymous, add the user ID
            if not anonymous_check.value and self.app.current_user:
                incident_data["reported_by"] = self.app.current_user["id"]

            # Save to database using data manager
            if self.app.data_manager:
                incident_id = self.app.data_manager.report_incident(incident_data)
                if incident_id:
                    # Show success message and add to UI
                    self.show_report_success_and_add_incident(
                        incident_type.value,
                        location.value,
                        description.value,
                        severity.value
                    )
                else:
                    # Show error message
                    self.app.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Failed to save incident. Please try again."),
                        action="OK",
                    )
                    self.app.page.snack_bar.open = True
                    self.app.page.update()
            else:
                # Fallback if data manager is not available
                self.show_report_success_and_add_incident(
                    incident_type.value,
                    location.value,
                    description.value,
                    severity.value
                )

        def cancel_report(e):
            # Close the dialog
            self.app.page.dialog.open = False
            self.app.page.update()

        # Show the dialog
        self.app.page.dialog = ft.AlertDialog(
            title=ft.Text("Report Incident"),
            content=ft.Column(
                [
                    incident_type,
                    severity,
                    location,
                    ft.Row(
                        [
                            latitude,
                            longitude,
                        ],
                        spacing=10,
                    ),
                    use_location_btn,
                    description,
                    photo_btn,
                    anonymous_check,
                ],
                spacing=10,
                width=300,
                scroll=ft.ScrollMode.AUTO,
                height=400,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_report),
                ft.TextButton("Submit", on_click=submit_report),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.app.page.dialog.open = True
        self.app.page.update()

    def use_current_location(self, location_field, lat_field, lon_field):
        """Simulate getting the user's current location"""
        # In a real app, this would use the device's GPS
        # For now, we'll just use a default location (Johannesburg)
        location_field.value = "Current Location (Johannesburg)"
        lat_field.value = "-26.2041"
        lon_field.value = "28.0473"
        self.app.page.update()

    def show_photo_dialog(self):
        """Show a dialog to upload a photo"""
        # In a real app, this would open the camera or file picker
        # For now, we'll just show a message
        self.app.page.snack_bar = ft.SnackBar(
            content=ft.Text("Photo upload not available in this version"),
            action="OK",
        )
        self.app.page.snack_bar.open = True
        self.app.page.update()

    def show_report_success_and_add_incident(self, incident_type, location, description, severity="Medium"):
        # Show success message
        self.app.page.snack_bar = ft.SnackBar(
            content=ft.Text("Incident reported successfully!"),
            action="OK",
        )
        self.app.page.snack_bar.open = True

        # Add the new incident
        self.add_new_incident(incident_type, location, description, severity)

        # Update the UI
        self.app.page.update()

    def add_new_incident(self, incident_type, location, description, severity="Medium"):
        # Determine color based on severity
        if severity == "High":
            severity_color = ft.colors.RED
            icon_color = ft.colors.RED
        elif severity == "Medium":
            severity_color = ft.colors.ORANGE
            icon_color = ft.colors.ORANGE
        else:  # Low
            severity_color = ft.colors.YELLOW
            icon_color = ft.colors.YELLOW

        # Choose icon based on incident type
        if incident_type == "Robbery" or incident_type == "Assault":
            icon_name = ft.icons.WARNING_AMBER_ROUNDED
        elif incident_type == "Traffic Accident":
            icon_name = ft.icons.CAR_CRASH
        elif incident_type == "Fire":
            icon_name = ft.icons.LOCAL_FIRE_DEPARTMENT
        elif incident_type == "Medical Emergency":
            icon_name = ft.icons.MEDICAL_SERVICES
        elif incident_type == "Power Outage":
            icon_name = ft.icons.POWER_OFF
        else:
            icon_name = ft.icons.WARNING_AMBER_ROUNDED

        # Add the new incident to the list
        self.incidents_list.controls.insert(
            0,
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(icon_name, color=icon_color),
                                ft.Text(incident_type, weight=ft.FontWeight.BOLD, size=16),
                                ft.Container(
                                    content=ft.Text(severity, color=ft.colors.WHITE, size=12),
                                    bgcolor=severity_color,
                                    padding=ft.padding.all(4),
                                    border_radius=4,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=10,
                        ),
                        ft.Text(location),
                        ft.Text(description, size=14),
                        ft.Text("Just now", size=12, color=ft.colors.GREY),
                    ],
                    spacing=4,
                ),
                padding=10,
                border_radius=8,
                bgcolor=ft.colors.WHITE,
                border=ft.border.all(1, ft.colors.GREY_300),
            )
        )
        self.update()

"""
Navigation Screen for SafeWayAI

This module provides a navigation screen with turn-by-turn directions.
"""

import flet as ft
import threading
import time
import datetime
from ui.components.map_view import MapView

class NavigationScreen(ft.Container):
    """Navigation screen with turn-by-turn directions."""

    def __init__(self, app):
        """Initialize the navigation screen."""
        self.app = app

        # Store route information
        self.route = None
        self.safety_analysis = None
        self.current_step_index = 0
        self.navigation_active = False
        self.eta = None
        self.distance_remaining = None
        self.time_remaining = None

        # Create the map view
        self.map_view = MapView()

        # Create the navigation panel
        self.navigation_panel = self.create_navigation_panel()

        # Create the main layout
        content = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        tooltip="Back to Map",
                        on_click=self.back_to_map
                    ),
                    ft.Text("Navigation", size=20, weight=ft.FontWeight.BOLD),
                ]),
                padding=10
            ),
            ft.Divider(height=1),
            ft.Container(
                content=ft.Row([
                    # Map view (2/3 of the width)
                    ft.Container(
                        content=self.map_view,
                        expand=2
                    ),
                    # Navigation panel (1/3 of the width)
                    ft.Container(
                        content=self.navigation_panel,
                        expand=1,
                        bgcolor=ft.colors.BLUE_GREY_50,
                        border_radius=10,
                        padding=10
                    )
                ]),
                expand=True
            )
        ], expand=True)

        # Initialize the container
        super().__init__(
            content=content,
            expand=True
        )

    def create_navigation_panel(self):
        """Create the navigation panel with directions."""
        # Create the ETA display
        self.eta_text = ft.Text("Calculating ETA...", size=16)

        # Create the distance and time remaining display
        self.distance_text = ft.Text("", size=14)
        self.time_text = ft.Text("", size=14)

        # Create the current instruction display
        self.current_instruction = ft.Text(
            "Preparing navigation...",
            size=18,
            weight=ft.FontWeight.BOLD
        )

        # Create the next instruction display
        self.next_instruction = ft.Text(
            "Loading next instruction...",
            size=14,
            color=ft.colors.GREY
        )

        # Create the safety info display
        self.safety_info = ft.Container(
            content=ft.Column([
                ft.Text("Safety Information", weight=ft.FontWeight.BOLD),
                ft.Text("Loading safety data...")
            ]),
            bgcolor=ft.colors.GREEN,
            padding=10,
            border_radius=5
        )

        # Create the incident alert display
        self.incident_alert = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.WARNING, color=ft.colors.WHITE),
                ft.Text("No incidents reported nearby", color=ft.colors.WHITE)
            ]),
            bgcolor=ft.colors.RED,
            padding=10,
            border_radius=5,
            visible=False
        )

        # Create the step list
        self.step_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10
        )

        # Create the navigation controls
        self.start_button = ft.ElevatedButton(
            text="Start Navigation",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.toggle_navigation
        )

        self.reroute_button = ft.ElevatedButton(
            text="Find Safer Route",
            icon=ft.icons.SHUFFLE,
            on_click=self.find_safer_route,
            disabled=True
        )

        # Create the navigation panel
        return ft.Column([
            ft.Container(
                content=ft.Column([
                    self.eta_text,
                    ft.Row([
                        self.distance_text,
                        ft.VerticalDivider(width=10),
                        self.time_text
                    ])
                ]),
                bgcolor=ft.colors.WHITE,
                padding=10,
                border_radius=5
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Current Instruction:", size=12),
                    self.current_instruction,
                    ft.Text("Next:", size=12),
                    self.next_instruction
                ]),
                bgcolor=ft.colors.WHITE,
                padding=10,
                border_radius=5,
                margin=ft.margin.only(top=10)
            ),
            self.safety_info,
            self.incident_alert,
            ft.Container(
                content=ft.Text("Turn-by-Turn Directions:", weight=ft.FontWeight.BOLD),
                margin=ft.margin.only(top=10, bottom=5)
            ),
            ft.Container(
                content=self.step_list,
                bgcolor=ft.colors.WHITE,
                border_radius=5,
                expand=True
            ),
            ft.Row([
                self.start_button,
                self.reroute_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], spacing=10, expand=True)

    def set_route(self, route, safety_analysis):
        """Set the route and safety analysis for navigation."""
        self.route = route
        self.safety_analysis = safety_analysis
        self.current_step_index = 0
        self.navigation_active = False

        # Store route information for later use
        self.start_location = self.app.map_screen.start_location
        self.end_location = self.app.map_screen.end_location
        self.route_safety_level = safety_analysis["overall_safety_level"]

        # Update the ETA and distance
        self.update_eta_and_distance()

        # Update the safety information
        self.update_safety_info()

        # Update the step list
        self.update_step_list()

        # Update the current and next instructions
        self.update_instructions()

        # Enable the start button
        self.start_button.disabled = False
        self.start_button.text = "Start Navigation"
        self.start_button.icon = ft.icons.PLAY_ARROW

        # Enable the reroute button if there are incidents
        self.reroute_button.disabled = not (safety_analysis.get("crime_count", 0) > 0)

        # Update the UI
        self.update()

    def update_eta_and_distance(self):
        """Update the ETA and distance information."""
        if not self.route:
            return

        # Get the total distance and duration
        distance = self.route.get("distance", 0)
        duration = self.route.get("duration", 0)

        # Calculate the ETA
        now = datetime.datetime.now()
        eta = now + datetime.timedelta(seconds=duration)

        # Update the displays
        self.eta_text.value = f"ETA: {eta.strftime('%I:%M %p')}"
        self.distance_text.value = f"Distance: {self._format_distance(distance)}"
        self.time_text.value = f"Time: {self._format_duration(duration)}"

        # Store for later use
        self.eta = eta
        self.distance_remaining = distance
        self.time_remaining = duration

    def update_safety_info(self):
        """Update the safety information display."""
        if not self.safety_analysis:
            return

        # Get the safety level and score
        safety_level = self.safety_analysis.get("overall_safety_level", "moderate")
        safety_score = self.safety_analysis.get("overall_safety_score", 50)

        # Determine the color based on safety level
        if safety_level == "very_safe":
            color = ft.colors.GREEN
        elif safety_level == "safe":
            color = ft.colors.LIGHT_GREEN
        elif safety_level == "moderate":
            color = ft.colors.YELLOW
        elif safety_level == "unsafe":
            color = ft.colors.ORANGE
        else:
            color = ft.colors.RED

        # Format the safety level for display
        safety_level_display = safety_level.replace("_", " ").title()

        # Create the safety info content
        content = ft.Column([
            ft.Text("Safety Information", weight=ft.FontWeight.BOLD),
            ft.Text(f"Safety Level: {safety_level_display}"),
            ft.Text(f"Safety Score: {safety_score:.0f}/100"),
            ft.Text(f"Incidents Nearby: {self.safety_analysis.get('crime_count', 0)}")
        ])

        # Update the safety info container
        self.safety_info.content = content
        self.safety_info.bgcolor = color

        # Show incident alert if there are incidents
        if self.safety_analysis.get("crime_count", 0) > 0:
            self.incident_alert.visible = True
            self.incident_alert.content = ft.Row([
                ft.Icon(ft.icons.WARNING, color=ft.colors.WHITE),
                ft.Text(f"{self.safety_analysis.get('crime_count', 0)} incidents reported nearby", color=ft.colors.WHITE)
            ])
        else:
            self.incident_alert.visible = False

    def update_step_list(self):
        """Update the step list with turn-by-turn directions."""
        if not self.route:
            return

        # Clear the step list
        self.step_list.controls.clear()

        # Get the steps
        steps = self.route.get("steps", [])

        # Add each step to the list
        for i, step in enumerate(steps):
            # Get the instruction
            instruction = step.get("instruction", f"Step {i+1}")

            # Get the distance and duration
            distance = step.get("distance", 0)
            duration = step.get("duration", 0)

            # Create the step item
            step_item = ft.Container(
                content=ft.Column([
                    ft.Text(instruction, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{self._format_distance(distance)} - {self._format_duration(duration)}")
                ]),
                bgcolor=ft.colors.WHITE if i != self.current_step_index else ft.colors.BLUE_100,
                padding=10,
                border_radius=5,
                border=ft.border.all(1, ft.colors.BLUE) if i == self.current_step_index else None
            )

            # Add to the list
            self.step_list.controls.append(step_item)

    def update_instructions(self):
        """Update the current and next instruction displays."""
        if not self.route:
            return

        # Get the steps
        steps = self.route.get("steps", [])

        if not steps:
            return

        # Get the current step
        current_step = steps[self.current_step_index] if self.current_step_index < len(steps) else None

        # Get the next step
        next_step = steps[self.current_step_index + 1] if self.current_step_index + 1 < len(steps) else None

        # Update the current instruction
        if current_step:
            instruction = current_step.get("instruction", f"Step {self.current_step_index + 1}")
            distance = current_step.get("distance", 0)
            self.current_instruction.value = f"{instruction} ({self._format_distance(distance)})"
        else:
            self.current_instruction.value = "You have arrived at your destination!"

        # Update the next instruction
        if next_step:
            instruction = next_step.get("instruction", f"Step {self.current_step_index + 2}")
            self.next_instruction.value = f"Next: {instruction}"
        else:
            self.next_instruction.value = "This is the final step"

    def toggle_navigation(self, e):
        """Toggle navigation on/off."""
        if self.navigation_active:
            # Stop navigation
            self.navigation_active = False
            self.start_button.text = "Resume Navigation"
            self.start_button.icon = ft.icons.PLAY_ARROW
        else:
            # Start navigation
            self.navigation_active = True
            self.start_button.text = "Pause Navigation"
            self.start_button.icon = ft.icons.PAUSE

            # Start the navigation thread
            threading.Thread(target=self.navigation_thread).start()

        # Update the UI
        self.update()

    def navigation_thread(self):
        """Thread for simulating navigation progress."""
        # Get the steps
        steps = self.route.get("steps", [])

        if not steps:
            return

        # Simulate navigation through each step
        while self.navigation_active and self.current_step_index < len(steps):
            # Get the current step
            current_step = steps[self.current_step_index]

            # Get the step duration
            duration = current_step.get("duration", 10)

            # Simulate travel time (1 second = 10 seconds of real travel time)
            simulation_time = duration / 10

            # Wait for the simulation time
            start_time = time.time()
            while self.navigation_active and time.time() - start_time < simulation_time:
                # Update the remaining time and distance
                progress = (time.time() - start_time) / simulation_time
                self.update_remaining_time_and_distance(progress)

                # Sleep for a short time
                time.sleep(0.5)

            # Move to the next step if navigation is still active
            if self.navigation_active:
                self.current_step_index += 1

                # Update the UI
                self.update_step_list()
                self.update_instructions()

                # Update the map to show the current position
                self.update_current_position()

        # Navigation complete
        if self.navigation_active:
            self.navigation_active = False
            self.start_button.text = "Navigation Complete"
            self.start_button.icon = ft.icons.CHECK_CIRCLE
            self.start_button.disabled = True

            # Show arrival message
            self.current_instruction.value = "You have arrived at your destination!"
            self.next_instruction.value = ""

            # Update the UI
            self.update()

    def update_remaining_time_and_distance(self, progress):
        """Update the remaining time and distance based on progress."""
        if not self.route:
            return

        # Get the current step
        steps = self.route.get("steps", [])
        if not steps or self.current_step_index >= len(steps):
            return

        current_step = steps[self.current_step_index]

        # Calculate remaining distance and time for this step
        step_distance = current_step.get("distance", 0)
        step_duration = current_step.get("duration", 0)

        step_distance_remaining = step_distance * (1 - progress)
        step_time_remaining = step_duration * (1 - progress)

        # Calculate total remaining distance and time
        total_distance_remaining = step_distance_remaining
        total_time_remaining = step_time_remaining

        for i in range(self.current_step_index + 1, len(steps)):
            total_distance_remaining += steps[i].get("distance", 0)
            total_time_remaining += steps[i].get("duration", 0)

        # Update the displays
        self.distance_text.value = f"Distance: {self._format_distance(total_distance_remaining)}"
        self.time_text.value = f"Time: {self._format_duration(total_time_remaining)}"

        # Calculate new ETA
        now = datetime.datetime.now()
        eta = now + datetime.timedelta(seconds=total_time_remaining)
        self.eta_text.value = f"ETA: {eta.strftime('%I:%M %p')}"

        # Store for later use
        self.distance_remaining = total_distance_remaining
        self.time_remaining = total_time_remaining
        self.eta = eta

        # Update the UI
        self.update()

    def update_current_position(self):
        """Update the map to show the current position."""
        if not self.route:
            return

        # Get the steps
        steps = self.route.get("steps", [])

        if not steps or self.current_step_index >= len(steps):
            return

        # Get the current step
        current_step = steps[self.current_step_index]

        # Get the end position of the current step
        end_position = current_step.get("end", {})

        # Update the map
        if end_position and "lat" in end_position and "lon" in end_position:
            self.map_view.update_map(end_position["lat"], end_position["lon"])

    def find_safer_route(self, e):
        """Find a safer route."""
        # Navigate back to the map screen
        self.app.navigate_to("map")

        # Show a message to the user
        self.app.page.snack_bar = ft.SnackBar(
            content=ft.Text("Please select a new route for safer navigation"),
            action="OK",
        )
        self.app.page.snack_bar.open = True
        self.app.page.update()

    def back_to_map(self, e):
        """Navigate back to the map screen."""
        # Stop navigation if active
        self.navigation_active = False

        # Navigate back to the map screen
        self.app.navigate_to("map")

    def _format_distance(self, distance_meters):
        """Format distance in a human-readable way."""
        if distance_meters < 1000:
            return f"{distance_meters:.0f} m"
        else:
            return f"{distance_meters/1000:.1f} km"

    def _format_duration(self, duration_seconds):
        """Format duration in a human-readable way."""
        if duration_seconds < 60:
            return f"{duration_seconds:.0f} sec"
        elif duration_seconds < 3600:
            minutes = duration_seconds / 60
            return f"{minutes:.0f} min"
        else:
            hours = duration_seconds / 3600
            minutes = (duration_seconds % 3600) / 60
            return f"{hours:.0f} hr {minutes:.0f} min"

    def did_mount(self):
        """Called when the screen is mounted to the page."""
        print("Navigation screen mounted")

        # Check if route information is available in the app
        if hasattr(self.app, 'current_route') and hasattr(self.app, 'current_safety_analysis'):
            print("Found route information in app, setting up navigation")
            # Set the route from the app's stored information
            self.route = self.app.current_route
            self.safety_analysis = self.app.current_safety_analysis
            self.current_step_index = 0
            self.navigation_active = False

            # Get start and end locations
            start_location = self.app.current_start_location
            end_location = self.app.current_end_location

            try:
                print("Showing route on navigation screen map")
                self.map_view.show_route(
                    start_location.get("lat", -26.2041),
                    start_location.get("lon", 28.0473),
                    end_location.get("lat", -26.1052),
                    end_location.get("lon", 28.0567),
                    safety_level=self.safety_analysis["overall_safety_level"]
                )
                print("Route displayed on navigation screen map")

                # Update the UI with route information
                self.update_eta_and_distance()
                self.update_safety_info()
                self.update_step_list()
                self.update_instructions()
            except Exception as e:
                print(f"Error showing route on navigation screen: {e}")
        else:
            print("No route information available in app")

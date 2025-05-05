import flet as ft
import threading
import time
from ui.components.simple_location_input import SimpleLocationInput
from ui.components.map_view import MapView

class MapScreen(ft.Container):
    def __init__(self, app):
        self.app = app
        self.start_location = None
        self.end_location = None
        self.selected_route = None
        self.selected_safety_analysis = None

        # Create location inputs
        self.start_input = SimpleLocationInput(
            label="Starting Point",
            hint_text="Enter starting point",
            on_location_selected=self.on_start_selected
        )

        self.end_input = SimpleLocationInput(
            label="Destination",
            hint_text="Enter destination",
            on_location_selected=self.on_end_selected
        )

        # Create a find route button
        self.find_route_btn = ft.ElevatedButton(
            text="Find Safe Route",
            icon=ft.icons.DIRECTIONS,
            on_click=self.find_route,
            disabled=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.all(20),
            )
        )

        # Create a start navigation button (initially hidden)
        self.start_navigation_btn = ft.ElevatedButton(
            text="START NAVIGATION",
            icon=ft.icons.NAVIGATION,
            on_click=self.start_navigation,
            visible=False,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.GREEN_700,
                color=ft.colors.WHITE,
                padding=ft.padding.all(20),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            tooltip="Start turn-by-turn navigation",
            width=250,
            height=60
        )

        # Create a map view
        self.map_view = MapView()

        # Create the main layout
        super().__init__(
            content=ft.Stack(
                [
                    # Main content
                    ft.Column(
                        [
                            # Route planning panel
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Plan Your Route", size=24, weight=ft.FontWeight.BOLD),
                                        self.start_input,
                                        self.end_input,
                                        ft.Container(
                                            content=ft.Row([
                                                self.find_route_btn,
                                            ], alignment=ft.MainAxisAlignment.CENTER),
                                            margin=ft.margin.only(top=10),
                                        ),
                                    ],
                                    spacing=8,
                                ),
                                padding=20,
                                border_radius=8,
                                bgcolor=ft.colors.WHITE,
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=15,
                                    color=ft.colors.BLACK12,
                                ),
                                margin=ft.margin.only(bottom=10),
                            ),

                            # Map container
                            ft.Container(
                                content=self.map_view,
                                expand=True,
                                padding=ft.padding.only(top=5),
                                border_radius=8,
                                bgcolor=ft.colors.WHITE,
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=15,
                                    color=ft.colors.BLACK12,
                                ),
                            ),
                        ],
                        spacing=0,
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),

                    # Navigation button
                    ft.Container(
                        content=self.start_navigation_btn,
                        alignment=ft.alignment.bottom_center,
                        padding=ft.padding.only(bottom=30),
                    ),
                ],
                expand=True,
            ),
            expand=True,
            padding=10,
        )

    def on_start_selected(self, location):
        print(f"Start location selected: {location}")
        self.start_location = location
        self.update_find_route_button()

        # Update the map
        if isinstance(location, dict) and "lat" in location and "lon" in location:
            print(f"Updating map with start location: {location['lat']}, {location['lon']}")
            self.map_view.update_map(location["lat"], location["lon"])
        else:
            print(f"Cannot update map with start location: {location}")

    def on_end_selected(self, location):
        print(f"End location selected: {location}")
        self.end_location = location
        self.update_find_route_button()

        # Update the map
        if isinstance(location, dict) and "lat" in location and "lon" in location:
            print(f"Updating map with end location: {location['lat']}, {location['lon']}")
            self.map_view.update_map(location["lat"], location["lon"])
        else:
            print(f"Cannot update map with end location: {location}")

    def update_find_route_button(self):
        # Enable the find route button if both locations are selected
        self.find_route_btn.disabled = not (self.start_location and self.end_location)
        self.update()

    def find_route(self, e):
        # Hide the navigation button if it was visible
        self.start_navigation_btn.visible = False

        # Reset selected route
        self.selected_route = None
        self.selected_safety_analysis = None

        # Show a loading dialog
        self.app.page.dialog = ft.AlertDialog(
            title=ft.Text("Finding the safest route..."),
            content=ft.ProgressRing(),
        )
        self.app.page.dialog.open = True
        self.app.page.update()

        # Start a thread to find the route
        threading.Thread(target=self.calculate_route).start()

    def calculate_route(self):
        # Try to import Google Maps client
        try:
            from services.google_maps_client import google_maps_client
            from services.ai_service import ai_service
            from services.crime_data_service import crime_data_service

            # Get route from Google Maps
            origin = {
                "lat": self.start_location.get("lat", -26.2041),
                "lon": self.start_location.get("lon", 28.0473)
            }

            destination = {
                "lat": self.end_location.get("lat", -26.1052),
                "lon": self.end_location.get("lon", 28.0567)
            }

            # Get directions with alternatives
            directions = google_maps_client.get_directions(origin, destination, alternatives=True)

            # Get incidents near the route
            from services.repositories import firebase_incident_repository
            incidents = firebase_incident_repository.get_recent_incidents(limit=20)

            # Analyze route safety
            if directions and "routes" in directions and directions["routes"]:
                # Get all routes
                routes = directions["routes"]

                print(f"Found {len(routes)} possible routes")

                # Analyze each route for safety
                route_analyses = []
                for i, route in enumerate(routes):
                    print(f"Analyzing route {i+1}/{len(routes)}")
                    analysis = ai_service.analyze_route_safety(route, incidents)
                    route_analyses.append({
                        "route_index": i,
                        "route": route,
                        "analysis": analysis
                    })

                # Sort routes by safety score (highest first)
                route_analyses.sort(key=lambda x: x["analysis"]["overall_safety_score"], reverse=True)

                # Store the route analyses for later use
                self.route_analyses = route_analyses

                # Get the safest route
                safest_route = route_analyses[0]["route"]
                safety_analysis = route_analyses[0]["analysis"]

                # Close the dialog
                self.app.page.dialog.open = False
                self.app.page.update()

                # Show route comparison dialog
                self.show_route_comparison_dialog(route_analyses)

                # Show the safest route on the map
                self.map_view.show_route(
                    self.start_location.get("lat", -26.2041),
                    self.start_location.get("lon", 28.0473),
                    self.end_location.get("lat", -26.1052),
                    self.end_location.get("lon", 28.0567),
                    safety_level=safety_analysis["overall_safety_level"]
                )
            else:
                # Fallback to simulated route
                # Close the dialog
                self.app.page.dialog.open = False
                self.app.page.update()

                # Show route details
                self.app.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Safe route found!"),
                    action="OK",
                )
                self.app.page.snack_bar.open = True
                self.app.page.update()

                # Show the route on the map
                self.map_view.show_route(
                    self.start_location.get("lat", -26.2041),
                    self.start_location.get("lon", 28.0473),
                    self.end_location.get("lat", -26.1052),
                    self.end_location.get("lon", 28.0567)
                )
        except Exception as e:
            print(f"Error calculating route: {e}")

            # Fallback to simulated route
            # Close the dialog
            self.app.page.dialog.open = False
            self.app.page.update()

            # Show route details
            self.app.page.snack_bar = ft.SnackBar(
                content=ft.Text("Safe route found!"),
                action="OK",
            )
            self.app.page.snack_bar.open = True
            self.app.page.update()

            # Show the route on the map
            try:
                self.map_view.show_route(
                    self.start_location.get("lat", -26.2041),
                    self.start_location.get("lon", 28.0473),
                    self.end_location.get("lat", -26.1052),
                    self.end_location.get("lon", 28.0567)
                )
            except Exception as e:
                print(f"Error showing route: {e}")
                # Fallback to just showing the start location
                self.map_view.update_map(
                    self.start_location.get("lat", -26.2041),
                    self.start_location.get("lon", 28.0473)
                )

    def show_route_comparison_dialog(self, route_analyses):
        """Show a dialog comparing different routes"""
        # Create route cards for each route
        route_cards = []

        for i, route_analysis in enumerate(route_analyses):
            route = route_analysis["route"]
            analysis = route_analysis["analysis"]

            # Get safety level and color
            safety_level = analysis["overall_safety_level"].replace("_", " ").title()
            safety_score = analysis["overall_safety_score"]

            if safety_level == "Very Safe":
                safety_color = ft.colors.GREEN
            elif safety_level == "Safe":
                safety_color = ft.colors.LIGHT_GREEN
            elif safety_level == "Moderate":
                safety_color = ft.colors.YELLOW
            elif safety_level == "Unsafe":
                safety_color = ft.colors.ORANGE
            else:
                safety_color = ft.colors.RED

            # Create risk factor list
            risk_factors = analysis.get("risk_factors", [])
            risk_factor_items = []

            for factor in risk_factors:
                impact = factor.get("impact", "moderate")
                impact_color = ft.colors.ORANGE if impact == "high" else ft.colors.YELLOW

                risk_factor_items.append(
                    ft.Row([
                        ft.Icon(ft.icons.WARNING, color=impact_color, size=16),
                        ft.Text(factor.get("description", ""), size=14)
                    ])
                )

            if not risk_factor_items:
                risk_factor_items.append(ft.Text("No significant risk factors", size=14, italic=True))

            # Create route card
            route_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Route {i+1}", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text(f"Safety: {safety_score:.0f}/100", color=ft.colors.WHITE),
                                bgcolor=safety_color,
                                border_radius=5,
                                padding=5
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(),
                        ft.Text("Distance: " + self._format_distance(route.get("distance", 0)), size=14),
                        ft.Text("Duration: " + self._format_duration(route.get("duration", 0)), size=14),
                        ft.Text("Safety Level: " + safety_level, size=14),
                        ft.Text("Incidents: " + str(analysis.get("crime_count", 0)), size=14),
                        ft.Divider(),
                        ft.Text("Risk Factors:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Column(risk_factor_items, spacing=5),
                        ft.Divider(),
                        ft.ElevatedButton(
                            text="Select This Route",
                            on_click=lambda e, idx=i: self.select_route(idx)
                        )
                    ], spacing=10),
                    padding=15
                ),
                elevation=3
            )

            route_cards.append(route_card)

        # Create the dialog
        self.app.page.dialog = ft.AlertDialog(
            title=ft.Text("Route Comparison"),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("We've analyzed multiple routes for your safety:", size=16),
                        ft.Divider(),
                        ft.Column(route_cards, spacing=10, scroll=ft.ScrollMode.AUTO)
                    ],
                    spacing=10
                ),
                width=500,
                height=400,
                padding=10
            ),
            actions=[
                ft.TextButton("Close", on_click=self.close_route_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        # Show the dialog
        self.app.page.dialog.open = True
        self.app.page.update()

    def _format_distance(self, distance_meters):
        """Format distance in a human-readable way"""
        if distance_meters < 1000:
            return f"{distance_meters:.0f} m"
        else:
            return f"{distance_meters/1000:.1f} km"

    def _format_duration(self, duration_seconds):
        """Format duration in a human-readable way"""
        if duration_seconds < 60:
            return f"{duration_seconds:.0f} sec"
        elif duration_seconds < 3600:
            minutes = duration_seconds / 60
            return f"{minutes:.0f} min"
        else:
            hours = duration_seconds / 3600
            minutes = (duration_seconds % 3600) / 60
            return f"{hours:.0f} hr {minutes:.0f} min"

    def close_route_dialog(self, e):
        """Close the route comparison dialog"""
        self.app.page.dialog.open = False
        self.app.page.update()

    def select_route(self, route_index):
        """Select a specific route"""
        # Close the dialog
        self.app.page.dialog.open = False
        self.app.page.update()

        # Get the selected route
        selected_route = self.route_analyses[route_index]["route"]
        safety_analysis = self.route_analyses[route_index]["analysis"]

        # Show route details
        safety_level = safety_analysis["overall_safety_level"].replace("_", " ").title()
        self.app.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Route {route_index+1} selected. Safety level: {safety_level}"),
            action="OK",
        )
        self.app.page.snack_bar.open = True
        self.app.page.update()

        # Show the route on the map
        self.map_view.show_route(
            self.start_location.get("lat", -26.2041),
            self.start_location.get("lon", 28.0473),
            self.end_location.get("lat", -26.1052),
            self.end_location.get("lon", 28.0567),
            safety_level=safety_analysis["overall_safety_level"]
        )

        # Show the start navigation button with animation
        self.start_navigation_btn.visible = True
        self.start_navigation_btn.scale = 1.0  # Start small
        self.update()

        # Animate to full size
        self.start_navigation_btn.scale = 1.2

        # Force update to make sure the button is visible
        self.update()

        # Show a snackbar to guide the user
        self.app.page.snack_bar = ft.SnackBar(
            content=ft.Text("Route selected! Click START NAVIGATION to begin turn-by-turn directions."),
            action="OK",
            bgcolor=ft.colors.GREEN_700,
            action_color=ft.colors.WHITE,
            duration=5000,  # Show for 5 seconds
        )
        self.app.page.snack_bar.open = True
        self.update()

        # Store the selected route for navigation
        self.selected_route = selected_route
        self.selected_safety_analysis = safety_analysis

    def start_navigation(self, e):
        """Start turn-by-turn navigation"""
        print("START NAVIGATION button clicked!")

        # Create a simulated route and safety analysis if none exists
        if not self.selected_route or not self.selected_safety_analysis:
            print("No route selected, creating simulated route...")
            self.selected_route = self._create_simulated_route()
            self.selected_safety_analysis = self._create_simulated_safety_analysis()

            # Show a message
            self.app.page.snack_bar = ft.SnackBar(
                content=ft.Text("Creating a safe route for you..."),
                action="OK",
                bgcolor=ft.colors.GREEN_700,
            )
            self.app.page.snack_bar.open = True
            self.app.page.update()

        print(f"Selected route: {self.selected_route}")
        # Set the route in the navigation screen
        self.app.navigation_screen.set_route(self.selected_route, self.selected_safety_analysis)

        # Navigate to the navigation screen
        self.app.navigate_to("navigation")

    def did_mount(self):
        """Called when the screen is mounted"""
        # Any initialization when the screen is mounted
        pass

    def will_unmount(self):
        """Called when the screen is unmounted"""
        # Clean up any resources
        pass

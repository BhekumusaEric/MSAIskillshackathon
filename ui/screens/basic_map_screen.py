"""
Basic Map Screen for SafeWayAI

This module provides a simplified map screen with basic inputs.
"""

import flet as ft
import threading
import time
from ui.components.map_view import MapView

class BasicMapScreen(ft.Container):
    """A simplified map screen with basic inputs."""
    
    def __init__(self, app):
        """Initialize the map screen."""
        self.app = app
        self.start_location = None
        self.end_location = None
        
        # Create basic text fields
        self.start_field = ft.TextField(
            label="Starting Point",
            hint_text="Enter starting point",
            border_radius=8,
            filled=True,
            expand=True,
            on_change=self.on_start_change,
        )
        
        self.end_field = ft.TextField(
            label="Destination",
            hint_text="Enter destination",
            border_radius=8,
            filled=True,
            expand=True,
            on_change=self.on_end_change,
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
        
        # Create a map view
        self.map_view = MapView()
        
        # Create the main layout
        super().__init__(
            content=ft.Column([
                # Header
                ft.Text("Plan Your Route", size=24, weight=ft.FontWeight.BOLD),
                
                # Input fields
                ft.Container(
                    content=ft.Column([
                        self.start_field,
                        self.end_field,
                        ft.Row([
                            self.find_route_btn,
                        ], alignment=ft.MainAxisAlignment.CENTER),
                    ]),
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
            ]),
            expand=True,
            padding=10,
        )
    
    def on_start_change(self, e):
        """Handle changes to the start field."""
        self.start_location = {"address": e.control.value, "lat": -26.2041, "lon": 28.0473}
        self.update_find_route_button()
    
    def on_end_change(self, e):
        """Handle changes to the end field."""
        self.end_location = {"address": e.control.value, "lat": -26.1052, "lon": 28.0567}
        self.update_find_route_button()
    
    def update_find_route_button(self):
        """Enable the find route button if both locations are selected."""
        self.find_route_btn.disabled = not (self.start_location and self.end_location)
        self.update()
    
    def find_route(self, e):
        """Find a route between the start and end locations."""
        # Show a snackbar
        self.app.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Finding route from {self.start_location['address']} to {self.end_location['address']}"),
            action="OK",
        )
        self.app.page.snack_bar.open = True
        self.app.page.update()
        
        # Show the route on the map
        self.map_view.show_route(
            self.start_location["lat"],
            self.start_location["lon"],
            self.end_location["lat"],
            self.end_location["lon"]
        )

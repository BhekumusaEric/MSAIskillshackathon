import flet as ft
import os
import random
from urllib.parse import quote

class MapView(ft.Container):
    def __init__(self, on_map_click=None):
        self.on_map_click = on_map_click
        self.markers = []
        self.route = None
        self.current_lat = -26.2041  # Default to Johannesburg
        self.current_lon = 28.0473
        self.zoom = 13

        # Get Google Maps API key
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')

        # Create the map iframe
        self.map_iframe = self.create_map_iframe()

        # Create a legend for the map
        self.legend = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=10, height=10, bgcolor=ft.colors.GREEN),
                        ft.Text("Safe", size=12)
                    ]),
                    padding=5,
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=10, height=10, bgcolor=ft.colors.YELLOW),
                        ft.Text("Caution", size=12)
                    ]),
                    padding=5,
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=10, height=10, bgcolor=ft.colors.RED),
                        ft.Text("Danger", size=12)
                    ]),
                    padding=5,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Create the location info text
        self.location_text = ft.Text(
            f"Location: {self.current_lat:.4f}, {self.current_lon:.4f}",
            size=12,
            text_align=ft.TextAlign.CENTER,
        )

        # Create the main layout
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text("SafeWayAI Map", size=20, weight=ft.FontWeight.BOLD),
                    self.map_iframe,
                    self.location_text,
                    self.legend,
                ],
                spacing=10,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            border_radius=8,
            expand=True,
        )

    def create_map_iframe(self):
        """Create an iframe with Google Maps"""
        # Create the Google Maps URL
        map_url = self.get_google_maps_url()

        # Create the iframe
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Loading map...", italic=True, size=14),
                    ft.Image(
                        src=f"https://maps.googleapis.com/maps/api/staticmap?center={self.current_lat},{self.current_lon}&zoom={self.zoom}&size=600x400&markers=color:red%7C{self.current_lat},{self.current_lon}&key={self.api_key}",
                        width=600,
                        height=400,
                        fit=ft.ImageFit.CONTAIN,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.WHITE,
            height=420,
            width=620,
        )

    def get_google_maps_url(self):
        """Get the Google Maps URL for the current location"""
        # Base URL
        base_url = "https://www.google.com/maps/embed/v1/view"

        # Parameters
        params = {
            "key": self.api_key,
            "center": f"{self.current_lat},{self.current_lon}",
            "zoom": self.zoom,
        }

        # Add markers if available
        if self.markers:
            markers_str = "|".join([f"{m['lat']},{m['lon']}" for m in self.markers])
            params["markers"] = markers_str

        # Add route if available
        if self.route:
            start = f"{self.route['start']['lat']},{self.route['start']['lon']}"
            end = f"{self.route['end']['lat']},{self.route['end']['lon']}"
            params["origin"] = start
            params["destination"] = end
            params["mode"] = "driving"

        # Build the URL
        url = f"{base_url}?"
        for key, value in params.items():
            url += f"{key}={quote(str(value))}&"

        return url.rstrip("&")

    def update_map(self, lat, lon, zoom=13):
        """Update the map to show a specific location"""
        print(f"Updating map to show location: {lat}, {lon}")

        # Store the current location
        self.current_lat = lat
        self.current_lon = lon
        self.zoom = zoom

        # Update the location text
        self.location_text.value = f"Location: {self.current_lat:.4f}, {self.current_lon:.4f}"

        # Update the map iframe
        self.map_iframe.content.controls[1].src = f"https://maps.googleapis.com/maps/api/staticmap?center={self.current_lat},{self.current_lon}&zoom={self.zoom}&size=600x400&markers=color:red%7C{self.current_lat},{self.current_lon}&key={self.api_key}"

        # Update the UI
        self.update()
        print("Map updated")

    def add_marker(self, lat, lon, title="Marker"):
        """Add a marker to the map"""
        print(f"Adding marker at {lat}, {lon} with title '{title}'")

        # Add the marker
        self.markers.append({"lat": lat, "lon": lon, "title": title})

        # Update the map
        self.update_map(lat, lon)

    def show_route(self, start_lat, start_lon, end_lat, end_lon, safety_level=None):
        """Show a route between two points with safety color-coding"""
        print(f"Showing route from ({start_lat}, {start_lon}) to ({end_lat}, {end_lon}) with safety level: {safety_level}")

        # Store the route
        self.route = {
            "start": {"lat": start_lat, "lon": start_lon},
            "end": {"lat": end_lat, "lon": end_lon},
            "safety_level": safety_level
        }

        # Calculate center point
        center_lat = (start_lat + end_lat) / 2
        center_lon = (start_lon + end_lon) / 2

        # Determine route color based on safety level
        route_color = "0x0000FF"  # Default blue

        if safety_level:
            if safety_level == "very_safe":
                route_color = "0x00AA00"  # Green
            elif safety_level == "safe":
                route_color = "0x88CC00"  # Light green
            elif safety_level == "moderate":
                route_color = "0xFFCC00"  # Yellow
            elif safety_level == "unsafe":
                route_color = "0xFF8800"  # Orange
            elif safety_level == "very_unsafe":
                route_color = "0xFF0000"  # Red

        # Update the map iframe with the route
        self.map_iframe.content.controls[1].src = (
            f"https://maps.googleapis.com/maps/api/staticmap"
            f"?size=600x400"
            f"&markers=color:green%7Clabel:S%7C{start_lat},{start_lon}"
            f"&markers=color:red%7Clabel:E%7C{end_lat},{end_lon}"
            f"&path=color:{route_color}|weight:5|{start_lat},{start_lon}|{end_lat},{end_lon}"
            f"&key={self.api_key}"
        )

        # Update the location text with safety information
        safety_text = ""
        if safety_level:
            safety_level_display = safety_level.replace("_", " ").title()
            safety_text = f" (Safety: {safety_level_display})"

        self.location_text.value = f"Route from ({start_lat:.4f}, {start_lon:.4f}) to ({end_lat:.4f}, {end_lon:.4f}){safety_text}"

        # Update the UI
        self.update()
        print("Route displayed on map")


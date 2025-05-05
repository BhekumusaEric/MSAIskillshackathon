import flet as ft
import threading
import time

# Use Google Maps for real geocoding
from services.google_maps_client import google_maps_client as GeocodingService
print("Using Google Maps for geocoding")

class LocationInput(ft.Column):
    def __init__(self, hint_text="Enter location", on_location_selected=None):
        self.hint_text = hint_text
        self.on_location_selected = on_location_selected
        self.selected_location = None
        self.suggestions = []
        self.is_enabled = True  # Track whether the input is enabled

        # Create the text field
        self.text_field = ft.TextField(
            hint_text=self.hint_text,
            border_radius=8,
            filled=True,
            expand=True,
            on_change=self.on_text_change,
            prefix_icon=ft.icons.LOCATION_ON_OUTLINED,
            suffix_icon=ft.icons.SEARCH,
            autofocus=False,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
            border_color=ft.colors.BLUE_GREY_300,
            bgcolor=ft.colors.WHITE,
            disabled=False,
            read_only=False,
            cursor_color=ft.colors.BLUE,
            cursor_height=20,
            cursor_width=2,
            text_size=16,
        )

        # Create the suggestions list
        self.suggestions_list = ft.ListView(
            height=200,
            visible=False,
            spacing=2,
        )

        # Create a container for the suggestions list
        self.suggestions_container = ft.Container(
            content=self.suggestions_list,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            border_radius=8,
            padding=5,
        )

        # Create the "Use Current Location" button
        self.current_location_btn = ft.TextButton(
            text="Use Current Location",
            icon=ft.icons.MY_LOCATION,
            on_click=self.use_current_location,
            style=ft.ButtonStyle(
                color=ft.colors.BLUE,
            ),
            tooltip="Use your current location as the starting point",
        )

        # Create a loading indicator
        self.progress_ring = ft.ProgressRing(
            width=20,
            height=20,
            stroke_width=2,
            visible=False
        )

        # Create the main container
        super().__init__(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self.text_field,
                            self.progress_ring
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    margin=ft.margin.only(bottom=5),
                    on_click=lambda _: self.text_field.focus(),
                ),
                ft.Container(
                    content=self.current_location_btn,
                    alignment=ft.alignment.center_right,
                ),
                ft.Container(
                    content=self.suggestions_container,
                    margin=ft.margin.only(top=2),
                    visible=self.suggestions_list.visible,
                )
            ],
            spacing=2,
            expand=True,
        )

    def on_text_change(self, e):
        text = e.control.value

        # Show loading indicator
        self.progress_ring.visible = True
        self.update()

        # Start a thread to search for suggestions
        threading.Thread(target=self.search_locations, args=(text,)).start()

    def search_locations(self, query):
        # Don't search if query is too short
        if not query or len(query) < 2:
            self.suggestions_list.visible = False
            self.progress_ring.visible = False
            self.update()
            return

        # Show loading indicator
        self.progress_ring.visible = True
        self.update()

        try:
            # Use Google Maps for real geocoding
            print(f"Searching for locations matching '{query}'")

            # First try geocoding
            location = GeocodingService.geocode(query)
            results = []

            if location:
                print(f"Found geocoded location: {location}")
                results.append(location)

            # Then try place search
            places = GeocodingService.search_places(query)
            if places:
                print(f"Found {len(places)} places")
                for place in places:
                    # Only add if not already in results
                    if not any(r.get('address') == place.get('address') for r in results):
                        results.append({
                            "address": place.get("address", place.get("name", "")),
                            "lat": place.get("lat"),
                            "lon": place.get("lon"),
                            "type": place.get("types", ["point_of_interest"])[0] if place.get("types") else "point_of_interest"
                        })

            print(f"Total results: {len(results)}")
            self.update_suggestions(results[:5])  # Limit to 5 results
        except Exception as e:
            print(f"Error searching locations: {e}")
            self.update_suggestions([])

    def update_suggestions(self, results):
        # Clear the suggestions list
        self.suggestions_list.controls.clear()

        if results:
            # Add each result to the suggestions list
            for result in results:
                address = result["address"]
                subtitle = f"{result.get('type', 'address').replace('_', ' ').title()}"
                if 'city' in result and result['city'] not in result['address']:
                    subtitle += f" • {result['city']}"

                # Create a list tile for each suggestion
                suggestion = ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.icons.LOCATION_ON, color=ft.colors.BLUE),
                        title=ft.Text(address, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(subtitle, size=12),
                        on_click=lambda e, r=result: self.select_location(r),
                    ),
                    border_radius=8,
                    margin=ft.margin.only(bottom=2),
                    ink=True,
                    hover_color=ft.colors.BLUE_50,
                )

                self.suggestions_list.controls.append(suggestion)

            # Show the suggestions list
            self.suggestions_list.visible = True
            self.controls[-1].visible = True  # Show the suggestions container
        else:
            self.suggestions_list.visible = False
            self.controls[-1].visible = False  # Hide the suggestions container

        # Hide loading indicator
        self.progress_ring.visible = False
        self.update()

    def use_current_location(self, e):
        # Show loading indicator
        self.progress_ring.visible = True
        self.update()

        # Simulate getting current location (replace with actual GPS code)
        def get_location():
            # Simulate delay
            time.sleep(1)

            # Create a location object with Johannesburg coordinates
            location = {
                "address": "Current Location",
                "lat": -26.2041,
                "lon": 28.0473,
                "type": "current_location"
            }

            # Select this location
            self.select_location(location)

        # Start a thread to get the current location
        threading.Thread(target=get_location).start()

    def select_location(self, location):
        print(f"Selecting location: {location}")

        # Update the text field
        self.text_field.value = location["address"]
        print(f"Updated text field value to: {self.text_field.value}")

        # Store the selected location
        self.selected_location = location
        print(f"Stored selected location: {self.selected_location}")

        # Hide the suggestions list
        self.suggestions_list.visible = False
        self.controls[-1].visible = False  # Hide the suggestions container

        # Hide loading indicator
        self.progress_ring.visible = False

        # Update the UI
        self.update()
        print("Updated UI after location selection")

        # Call the callback if provided
        if self.on_location_selected:
            print(f"Calling location selected callback with: {location}")
            self.on_location_selected(location)
        else:
            print("No location selected callback provided")

    def enable(self):
        """Enable the input field"""
        self.is_enabled = True
        self.text_field.disabled = False
        self.text_field.read_only = False
        self.current_location_btn.disabled = False
        self.update()

    def disable(self):
        """Disable the input field"""
        self.is_enabled = False
        self.text_field.disabled = True
        self.text_field.read_only = True
        self.current_location_btn.disabled = True
        self.update()

    def focus(self):
        """Focus the text field"""
        if self.is_enabled:
            self.text_field.focus()
            self.update()

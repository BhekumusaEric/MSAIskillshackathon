"""
Improved Location Input Component for SafeWayAI

This module provides an improved location input component with autocomplete suggestions.
"""

import flet as ft
import threading
import time

# Use Google Maps for real geocoding
from services.google_maps_client import google_maps_client as GeocodingService

class ImprovedLocationInput(ft.Container):
    """An improved location input component with autocomplete suggestions."""

    # Class variables to store locations across all instances
    recent_locations = []
    max_recent_locations = 5
    favorite_locations = []
    max_favorite_locations = 10

    def __init__(self, label="Location", hint_text="Enter location", on_location_selected=None):
        """Initialize the location input."""
        self.label = label
        self.hint_text = hint_text
        self.on_location_selected = on_location_selected
        self.selected_location = None
        self.showing_recent_locations = False
        self.current_suggestion_index = -1  # For keyboard navigation

        # Create the text field with improved interaction
        self.text_field = ft.TextField(
            label=self.label,
            hint_text=self.hint_text,
            border_radius=8,
            filled=True,
            expand=True,
            on_change=self.on_text_change,
            prefix_icon=ft.icons.LOCATION_ON_OUTLINED,
            suffix_icon=ft.icons.SEARCH,
            height=60,  # Increased height for better touch target
            # Explicitly set these properties to ensure the field is interactive
            read_only=False,
            disabled=False,
            # Add keyboard-related properties
            autofocus=False,
            can_reveal_password=False,
            multiline=False,
            # Add on_focus event handler
            on_focus=self.on_text_field_focus,
            # Add on_blur event handler
            on_blur=self.on_text_field_blur,
            # Add submit event handler
            on_submit=self.on_submit,
            # Improve text field appearance
            text_size=16,  # Larger text
            cursor_color=ft.colors.BLUE,
            cursor_width=2,
            # Improve focus appearance
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )

        # Create the suggestions list with improved appearance
        self.suggestions_list = ft.ListView(
            height=250,  # Increased height
            visible=False,
            spacing=2,
            padding=5,
        )

        # Create the "Use Current Location" button with improved appearance
        self.current_location_btn = ft.ElevatedButton(
            text="Use Current Location",
            icon=ft.icons.MY_LOCATION,
            on_click=self.use_current_location,
            style=ft.ButtonStyle(
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE,
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=3,  # Add elevation for better visibility
                animation_duration=300,  # Add animation
            ),
            tooltip="Use your current location as the starting point",
            height=45,  # Increased height for better touch target
        )

        # Create a loading indicator
        self.progress_ring = ft.ProgressRing(
            width=24,  # Increased size
            height=24,
            stroke_width=3,
            visible=False,
            color=ft.colors.BLUE,
        )

        # Create a container for the text field that can be clicked
        self.text_field_container = ft.Container(
            content=ft.Row([
                self.text_field,
                self.progress_ring
            ]),
            on_click=lambda _: self.focus_text_field(),
            # Add padding to make it easier to click
            padding=8,
            # Add hover effect
            ink=True,
            border_radius=8,
        )

        # Create the suggestions container with improved appearance
        self.suggestions_container = ft.Container(
            content=self.suggestions_list,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            border_radius=10,
            padding=8,
            margin=ft.margin.only(top=5),
            visible=False,  # Initially hidden
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
            ),
        )

        # Create the main container with improved structure
        super().__init__(
            content=ft.Column([
                # Text field container
                self.text_field_container,

                # Current location button in a container for better alignment
                ft.Container(
                    content=self.current_location_btn,
                    alignment=ft.alignment.center_right,
                    margin=ft.margin.only(top=5, bottom=5),
                ),

                # Suggestions container
                self.suggestions_container
            ],
            spacing=0,  # Reduce spacing
            tight=True,  # Make layout more compact
            ),
            padding=5,  # Reduced padding
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            # Make the entire component clickable to focus the text field
            on_click=lambda _: self.focus_text_field(),
            # Add hover effect
            ink=True,
        )

    def on_text_change(self, e):
        """Handle text changes."""
        text = e.control.value

        # Show loading indicator
        self.progress_ring.visible = True
        self.update()

        # Start a thread to search for suggestions
        threading.Thread(target=self.search_locations, args=(text,)).start()

    def search_locations(self, query):
        """Search for locations matching the query."""
        # Don't search if query is too short
        if not query or len(query) < 2:
            self.hide_suggestions()
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
            self.hide_suggestions()

    def update_suggestions(self, results):
        """Update the suggestions list."""
        # Clear the suggestions list
        self.suggestions_list.controls.clear()
        self.showing_recent_locations = False

        if results:
            # Add a header with improved visibility
            self.suggestions_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.SEARCH, color=ft.colors.BLUE, size=20),
                        ft.Text("Search Results", weight=ft.FontWeight.BOLD, size=16),
                    ], spacing=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=12),
                    bgcolor=ft.colors.BLUE_50,
                    border_radius=ft.border_radius.only(top_left=8, top_right=8),
                    margin=ft.margin.only(bottom=5),
                )
            )

            # Add each result to the suggestions list
            for result in results:
                address = result["address"]
                subtitle = f"{result.get('type', 'address').replace('_', ' ').title()}"
                if 'city' in result and result['city'] not in result['address']:
                    subtitle += f" • {result['city']}"

                # Check if this location is a favorite
                is_favorite = self.is_favorite(result)

                # Create a list tile for each suggestion with improved touch interaction
                suggestion = ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.icons.LOCATION_ON, color=ft.colors.BLUE, size=28),  # Larger icon
                        title=ft.Text(address, weight=ft.FontWeight.BOLD, size=16),  # Larger text
                        subtitle=ft.Text(subtitle, size=14),  # Larger subtitle
                        trailing=ft.IconButton(
                            icon=ft.icons.STAR if is_favorite else ft.icons.STAR_BORDER,
                            icon_color=ft.colors.AMBER if is_favorite else ft.colors.GREY,
                            icon_size=28,  # Larger icon
                            tooltip="Add to favorites" if not is_favorite else "Remove from favorites",
                            on_click=lambda e, loc=result: self.toggle_favorite(loc),
                        ),
                        on_click=lambda e, r=result: self.select_location(r),
                        selected=False,
                        selected_color=ft.colors.BLUE_100,
                        # Make the list tile taller for better touch targets
                        content_padding=ft.padding.symmetric(horizontal=10, vertical=12),
                    ),
                    border_radius=10,
                    margin=ft.margin.only(bottom=4),  # Increased margin
                    ink=True,  # Add ripple effect
                    # Add hover effect
                    on_hover=lambda e: self._handle_suggestion_hover(e, suggestion),
                )

                self.suggestions_list.controls.append(suggestion)

            # Show the suggestions list
            self.show_suggestions()
        else:
            # Show "No Results Found" message
            self.suggestions_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SEARCH_OFF, color=ft.colors.GREY, size=40),
                        ft.Text("No Results Found", weight=ft.FontWeight.BOLD, color=ft.colors.GREY),
                        ft.Text("Try a different search term", color=ft.colors.GREY),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    alignment=ft.alignment.center,
                )
            )

            # Show the suggestions list
            self.show_suggestions()

    def show_suggestions(self):
        """Show the suggestions list."""
        self.suggestions_list.visible = True
        self.suggestions_container.visible = True
        self.update()

    def hide_suggestions(self):
        """Hide the suggestions list."""
        self.suggestions_list.visible = False
        self.suggestions_container.visible = False
        self.progress_ring.visible = False
        self.update()

    def use_current_location(self, e):
        """Use the current location."""
        # Show loading indicator
        self.progress_ring.visible = True

        # Disable the button while loading
        self.current_location_btn.disabled = True
        self.current_location_btn.icon = ft.icons.LOCATION_SEARCHING
        self.current_location_btn.text = "Getting Location..."
        self.update()

        # Show a snackbar to indicate that we're getting the location
        page = self.page
        if page:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Getting your current location..."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()

        # Simulate getting current location (replace with actual GPS code)
        def get_location():
            # Simulate delay
            time.sleep(2)

            # Create a location object with Johannesburg coordinates
            location = {
                "address": "Current Location (Johannesburg)",
                "lat": -26.2041,
                "lon": 28.0473,
                "type": "current_location"
            }

            # Re-enable the button
            self.current_location_btn.disabled = False
            self.current_location_btn.icon = ft.icons.MY_LOCATION
            self.current_location_btn.text = "Use Current Location"

            # Select this location
            self.select_location(location)

            # Show a success message
            if page:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Current location set to Johannesburg"),
                    action="OK",
                    bgcolor=ft.colors.GREEN,
                )
                page.snack_bar.open = True
                page.update()

        # Start a thread to get the current location
        threading.Thread(target=get_location).start()

    def select_location(self, location):
        """Select a location."""
        print(f"Selecting location: {location}")

        # Update the text field
        self.text_field.value = location["address"]
        print(f"Updated text field value to: {self.text_field.value}")

        # Store the selected location
        self.selected_location = location
        print(f"Stored selected location: {self.selected_location}")

        # Add to recent locations
        self.add_to_recent_locations(location)
        print(f"Added to recent locations: {location}")

        # Hide the suggestions list
        if self.showing_recent_locations:
            self.hide_recent_locations()
        else:
            self.hide_suggestions()

        # Update the UI
        self.update()
        print("Updated UI after location selection")

        # Call the callback if provided
        if self.on_location_selected:
            print(f"Calling location selected callback with: {location}")
            self.on_location_selected(location)
        else:
            print("No location selected callback provided")

    def on_text_field_focus(self, e):
        """Handle text field focus."""
        print("Text field focused")
        # Show recent locations if the text field is empty
        if not self.text_field.value:
            self.show_recent_locations()

    def on_text_field_blur(self, e):
        """Handle text field blur."""
        print("Text field blurred")
        # Hide suggestions after a short delay to allow clicking on them
        def delayed_hide():
            time.sleep(0.2)
            if self.showing_recent_locations:
                self.hide_recent_locations()
            else:
                self.hide_suggestions()
        threading.Thread(target=delayed_hide).start()

    def add_to_recent_locations(self, location):
        """Add a location to the recent locations list."""
        # Check if the location is already in the list
        for i, loc in enumerate(ImprovedLocationInput.recent_locations):
            if loc.get("address") == location.get("address"):
                # Move it to the top of the list
                ImprovedLocationInput.recent_locations.pop(i)
                ImprovedLocationInput.recent_locations.insert(0, location)
                return

        # Add the location to the top of the list
        ImprovedLocationInput.recent_locations.insert(0, location)

        # Limit the number of recent locations
        if len(ImprovedLocationInput.recent_locations) > ImprovedLocationInput.max_recent_locations:
            ImprovedLocationInput.recent_locations.pop()

    def add_to_favorites(self, location):
        """Add a location to the favorites list."""
        # Check if the location is already in the list
        for i, loc in enumerate(ImprovedLocationInput.favorite_locations):
            if loc.get("address") == location.get("address"):
                # Already in favorites, no need to add again
                return

        # Add the location to the favorites list
        ImprovedLocationInput.favorite_locations.append(location)

        # Limit the number of favorite locations
        if len(ImprovedLocationInput.favorite_locations) > ImprovedLocationInput.max_favorite_locations:
            ImprovedLocationInput.favorite_locations.pop(0)

    def remove_from_favorites(self, location):
        """Remove a location from the favorites list."""
        # Find the location in the list
        for i, loc in enumerate(ImprovedLocationInput.favorite_locations):
            if loc.get("address") == location.get("address"):
                # Remove it from the list
                ImprovedLocationInput.favorite_locations.pop(i)
                return

    def is_favorite(self, location):
        """Check if a location is in the favorites list."""
        for loc in ImprovedLocationInput.favorite_locations:
            if loc.get("address") == location.get("address"):
                return True
        return False

    def show_recent_locations(self):
        """Show the recent locations and favorites list."""
        # Clear the suggestions list
        self.suggestions_list.controls.clear()

        # Show favorites section if there are any
        if ImprovedLocationInput.favorite_locations:
            # Add a header for favorites with improved visibility
            self.suggestions_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.FAVORITE, color=ft.colors.AMBER, size=20),
                        ft.Text("Favorite Locations", weight=ft.FontWeight.BOLD, size=16),
                    ], spacing=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=12),
                    bgcolor=ft.colors.AMBER_50,
                    border_radius=ft.border_radius.only(top_left=8, top_right=8),
                    margin=ft.margin.only(bottom=5, top=5),
                )
            )

            # Add each favorite location to the suggestions list
            for location in ImprovedLocationInput.favorite_locations:
                address = location.get("address", "")

                # Create a list tile for each favorite with improved touch interaction
                suggestion = ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.icons.STAR, color=ft.colors.AMBER, size=28),  # Larger icon
                        title=ft.Text(address, weight=ft.FontWeight.BOLD, size=16),  # Larger text
                        trailing=ft.IconButton(
                            icon=ft.icons.STAR,
                            icon_color=ft.colors.AMBER,
                            icon_size=28,  # Larger icon
                            tooltip="Remove from favorites",
                            on_click=lambda e, loc=location: self.toggle_favorite(loc),
                        ),
                        on_click=lambda e, loc=location: self.select_location(loc),
                        selected=False,
                        selected_color=ft.colors.AMBER_50,
                        # Make the list tile taller for better touch targets
                        content_padding=ft.padding.symmetric(horizontal=10, vertical=12),
                    ),
                    border_radius=10,
                    margin=ft.margin.only(bottom=4),  # Increased margin
                    ink=True,  # Add ripple effect
                    # Add hover effect
                    on_hover=lambda e: self._handle_suggestion_hover(e, suggestion),
                )

                self.suggestions_list.controls.append(suggestion)

        # Show recent locations section if there are any
        if ImprovedLocationInput.recent_locations:
            # Add a header for recent locations with improved visibility
            self.suggestions_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.HISTORY, color=ft.colors.BLUE, size=20),
                        ft.Text("Recent Locations", weight=ft.FontWeight.BOLD, size=16),
                    ], spacing=10),
                    padding=ft.padding.symmetric(horizontal=15, vertical=12),
                    bgcolor=ft.colors.BLUE_50,
                    border_radius=ft.border_radius.only(top_left=8, top_right=8),
                    margin=ft.margin.only(bottom=5, top=5),
                )
            )

            # Add each recent location to the suggestions list
            for location in ImprovedLocationInput.recent_locations:
                address = location.get("address", "")

                # Check if this location is a favorite
                is_favorite = self.is_favorite(location)

                # Create a list tile for each recent location with improved touch interaction
                suggestion = ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.icons.HISTORY, color=ft.colors.BLUE, size=28),  # Larger icon
                        title=ft.Text(address, weight=ft.FontWeight.BOLD, size=16),  # Larger text
                        trailing=ft.IconButton(
                            icon=ft.icons.STAR if is_favorite else ft.icons.STAR_BORDER,
                            icon_color=ft.colors.AMBER if is_favorite else ft.colors.GREY,
                            icon_size=28,  # Larger icon
                            tooltip="Add to favorites" if not is_favorite else "Remove from favorites",
                            on_click=lambda e, loc=location: self.toggle_favorite(loc),
                        ),
                        on_click=lambda e, loc=location: self.select_location(loc),
                        selected=False,
                        selected_color=ft.colors.BLUE_GREY_50,
                        # Make the list tile taller for better touch targets
                        content_padding=ft.padding.symmetric(horizontal=10, vertical=12),
                    ),
                    border_radius=10,
                    margin=ft.margin.only(bottom=4),  # Increased margin
                    ink=True,  # Add ripple effect
                    # Add hover effect
                    on_hover=lambda e: self._handle_suggestion_hover(e, suggestion),
                )

                self.suggestions_list.controls.append(suggestion)

        # Show the suggestions list if there are any items
        if ImprovedLocationInput.recent_locations or ImprovedLocationInput.favorite_locations:
            self.suggestions_list.visible = True
            self.suggestions_container.visible = True
            self.showing_recent_locations = True
            self.update()

    def hide_recent_locations(self):
        """Hide the recent locations list."""
        self.suggestions_list.visible = False
        self.suggestions_container.visible = False
        self.showing_recent_locations = False
        self.update()

    def focus_text_field(self):
        """Focus the text field."""
        print("Focusing text field")
        self.text_field.focus()
        self.update()

    def toggle_favorite(self, location):
        """Toggle a location as favorite."""
        print(f"Toggling favorite for location: {location}")

        # Check if the location is already a favorite
        if self.is_favorite(location):
            # Remove from favorites
            self.remove_from_favorites(location)

            # Show a snackbar
            page = self.page
            if page:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Removed '{location.get('address')}' from favorites"),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
        else:
            # Add to favorites
            self.add_to_favorites(location)

            # Show a snackbar
            page = self.page
            if page:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Added '{location.get('address')}' to favorites"),
                    action="OK",
                    bgcolor=ft.colors.AMBER,
                )
                page.snack_bar.open = True
                page.update()

        # Refresh the list
        if self.showing_recent_locations:
            self.show_recent_locations()

    def on_submit(self, e):
        """Handle text field submission."""
        print(f"Text field submitted: {e.control.value}")

        # If there's text, search for it
        if e.control.value:
            self.search_locations(e.control.value)

        # If suggestions are visible and there's a selected suggestion, select it
        if self.suggestions_list.visible and self.current_suggestion_index >= 0:
            self.select_current_suggestion()

    def navigate_suggestions(self, direction):
        """Navigate through suggestions with keyboard."""
        # Get the number of suggestions
        num_suggestions = len([c for c in self.suggestions_list.controls if isinstance(c.content, ft.ListTile)])

        if num_suggestions == 0:
            return

        # Update the current index
        self.current_suggestion_index += direction

        # Wrap around if needed
        if self.current_suggestion_index < 0:
            self.current_suggestion_index = num_suggestions - 1
        elif self.current_suggestion_index >= num_suggestions:
            self.current_suggestion_index = 0

        # Highlight the current suggestion
        self.highlight_current_suggestion()

    def highlight_current_suggestion(self):
        """Highlight the current suggestion."""
        # Reset all suggestions
        suggestion_index = 0

        for control in self.suggestions_list.controls:
            if isinstance(control.content, ft.ListTile):
                if suggestion_index == self.current_suggestion_index:
                    # Highlight this suggestion
                    control.bgcolor = ft.colors.BLUE_100
                else:
                    # Reset this suggestion
                    control.bgcolor = None

                suggestion_index += 1

        self.update()

    def select_current_suggestion(self):
        """Select the current highlighted suggestion."""
        # Find the current suggestion
        suggestion_index = 0

        for control in self.suggestions_list.controls:
            if isinstance(control.content, ft.ListTile):
                if suggestion_index == self.current_suggestion_index:
                    # Trigger the on_click event of this suggestion
                    if hasattr(control.content, "on_click") and control.content.on_click:
                        # Create a dummy event
                        dummy_event = type('obj', (object,), {})
                        control.content.on_click(dummy_event)
                    return

                suggestion_index += 1

    def _handle_suggestion_hover(self, e, suggestion):
        """Handle hover events for suggestions."""
        # Change background color on hover
        if e.data == "true":  # Mouse entered
            suggestion.bgcolor = ft.colors.BLUE_50
        else:  # Mouse exited
            suggestion.bgcolor = None
        self.update()

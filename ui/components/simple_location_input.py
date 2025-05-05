"""
Simple Location Input Component for SafeWayAI

This module provides a simplified location input component.
"""

import flet as ft
import threading
import time

# Use Google Maps for real geocoding
from services.google_maps_client import google_maps_client as GeocodingService

class SimpleLocationInput(ft.Container):
    """A simplified location input component."""
    
    def __init__(self, label="Location", hint_text="Enter location", on_location_selected=None):
        """Initialize the location input."""
        self.label = label
        self.hint_text = hint_text
        self.on_location_selected = on_location_selected
        self.selected_location = None
        
        # Create the text field
        self.text_field = ft.TextField(
            label=self.label,
            hint_text=self.hint_text,
            border_radius=8,
            filled=True,
            expand=True,
            on_change=self.on_text_change,
            prefix_icon=ft.icons.LOCATION_ON_OUTLINED,
            suffix_icon=ft.icons.SEARCH,
            height=50,
        )
        
        # Create the suggestions list
        self.suggestions_list = ft.ListView(
            height=200,
            visible=False,
            spacing=2,
        )
        
        # Create the "Use Current Location" button
        self.current_location_btn = ft.TextButton(
            text="Use Current Location",
            icon=ft.icons.MY_LOCATION,
            on_click=self.use_current_location,
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
            content=ft.Column([
                # Text field row
                ft.Row([
                    self.text_field,
                    self.progress_ring
                ]),
                
                # Current location button
                self.current_location_btn,
                
                # Suggestions list
                self.suggestions_list
            ]),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.WHITE,
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
        """Update the suggestions list."""
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
                suggestion = ft.ListTile(
                    leading=ft.Icon(ft.icons.LOCATION_ON),
                    title=ft.Text(address),
                    subtitle=ft.Text(subtitle, size=12),
                    on_click=lambda e, r=result: self.select_location(r),
                )
                
                self.suggestions_list.controls.append(suggestion)
            
            # Show the suggestions list
            self.suggestions_list.visible = True
        else:
            self.suggestions_list.visible = False
        
        # Hide loading indicator
        self.progress_ring.visible = False
        self.update()
    
    def use_current_location(self, e):
        """Use the current location."""
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
        """Select a location."""
        print(f"Selecting location: {location}")
        
        # Update the text field
        self.text_field.value = location["address"]
        print(f"Updated text field value to: {self.text_field.value}")
        
        # Store the selected location
        self.selected_location = location
        print(f"Stored selected location: {self.selected_location}")
        
        # Hide the suggestions list
        self.suggestions_list.visible = False
        
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

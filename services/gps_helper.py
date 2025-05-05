"""
GPS Helper for SafeWayAI

This module provides GPS functionality for getting the user's current location.
"""

import threading
import time
import random
from kivy.utils import platform
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty, StringProperty

# Default location (Johannesburg)
DEFAULT_LAT = -26.2041
DEFAULT_LON = 28.0473

class GPSHelper(EventDispatcher):
    """
    GPS Helper class for getting the user's current location.
    
    This class provides both real GPS functionality on mobile devices
    and simulated GPS for testing on desktop.
    """
    
    # Properties
    lat = NumericProperty(DEFAULT_LAT)
    lon = NumericProperty(DEFAULT_LON)
    is_available = BooleanProperty(False)
    status = StringProperty("Initializing...")
    
    def __init__(self, **kwargs):
        super(GPSHelper, self).__init__(**kwargs)
        self._gps = None
        self._running = False
        
        # Initialize GPS based on platform
        if self._init_gps():
            self.is_available = True
            self.status = "GPS Ready"
        else:
            self.status = "GPS Not Available - Using Simulated Location"
    
    def _init_gps(self):
        """Initialize the GPS based on the platform."""
        if platform == 'android':
            # On Android, use the Android GPS
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION
                ])
                
                from plyer import gps
                self._gps = gps
                return True
            except Exception as e:
                print(f"Error initializing Android GPS: {e}")
                return False
        elif platform == 'ios':
            # On iOS, use the iOS GPS
            try:
                from plyer import gps
                self._gps = gps
                return True
            except Exception as e:
                print(f"Error initializing iOS GPS: {e}")
                return False
        else:
            # On desktop, use simulated GPS
            print("Using simulated GPS for desktop")
            return False
    
    def start(self, callback=None):
        """
        Start GPS updates.
        
        Args:
            callback (callable, optional): Function to call when location is updated
        """
        if self._running:
            return
        
        self._running = True
        self.status = "Getting location..."
        
        if self._gps:
            # Real GPS
            try:
                self._gps.configure(
                    on_location=lambda **kwargs: self._on_location_update(kwargs, callback),
                    on_status=self._on_status_update
                )
                self._gps.start(minTime=1000, minDistance=1)
            except Exception as e:
                print(f"Error starting GPS: {e}")
                self.status = f"GPS Error: {e}"
                self._start_simulation(callback)
        else:
            # Simulated GPS
            self._start_simulation(callback)
    
    def _start_simulation(self, callback=None):
        """Start simulated GPS updates."""
        def simulate_location_updates():
            while self._running:
                # Simulate small movements
                self.lat += random.uniform(-0.0001, 0.0001)
                self.lon += random.uniform(-0.0001, 0.0001)
                
                # Call the callback if provided
                if callback:
                    Clock.schedule_once(
                        lambda dt: callback({"lat": self.lat, "lon": self.lon}),
                        0
                    )
                
                time.sleep(2)  # Update every 2 seconds
        
        # Start the simulation in a background thread
        thread = threading.Thread(target=simulate_location_updates)
        thread.daemon = True
        thread.start()
        
        self.status = "Using simulated location"
    
    def _on_location_update(self, location, callback=None):
        """Handle location updates from the GPS."""
        # Update properties
        self.lat = location.get('lat', DEFAULT_LAT)
        self.lon = location.get('lon', DEFAULT_LON)
        
        # Call the callback if provided
        if callback:
            callback({"lat": self.lat, "lon": self.lon})
    
    def _on_status_update(self, status):
        """Handle status updates from the GPS."""
        self.status = status
    
    def stop(self):
        """Stop GPS updates."""
        self._running = False
        if self._gps:
            try:
                self._gps.stop()
            except Exception as e:
                print(f"Error stopping GPS: {e}")
    
    def get_current_location(self, callback=None):
        """
        Get the current location.
        
        Args:
            callback (callable, optional): Function to call with the location
            
        Returns:
            dict: Current location with lat and lon keys
        """
        location = {"lat": self.lat, "lon": self.lon}
        
        if callback:
            # Start GPS updates if not already running
            if not self._running:
                self.start(callback)
            else:
                # Call the callback with the current location
                callback(location)
        
        return location

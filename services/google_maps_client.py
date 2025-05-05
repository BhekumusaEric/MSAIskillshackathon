"""
Google Maps Client for SafeWayAI

This module provides a client for Google Maps API services.
"""

import os
import json
import time
import random
import threading
import requests
import googlemaps
from dotenv import load_dotenv
from geopy.distance import geodesic

# Load environment variables
load_dotenv()

class GoogleMapsClient:
    """Client for Google Maps API services."""
    
    def __init__(self):
        """Initialize the Google Maps client."""
        # Get API key from environment variable
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        
        # Initialize client
        self.client = None
        
        # Connect if API key is available
        self._ensure_config_exists()
        self.connect()
    
    def _ensure_config_exists(self):
        """Ensure the Google Maps configuration file exists."""
        config_dir = os.path.join('config')
        config_path = os.path.join(config_dir, 'google_maps_config.json')
        
        os.makedirs(config_dir, exist_ok=True)
        
        if not os.path.exists(config_path):
            # Create a template configuration file
            default_config = {
                "api_key": "YOUR_GOOGLE_MAPS_API_KEY",
                "cache_enabled": True,
                "cache_expiration": 86400  # 24 hours in seconds
            }
            
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"Created template Google Maps config file at {config_path}")
            print("Please update this file with your actual Google Maps API key")
    
    def connect(self):
        """Connect to Google Maps API."""
        try:
            # Check if already connected
            if self.client is not None:
                return True
            
            # Check if API key is available
            if not self.api_key or self.api_key == "YOUR_GOOGLE_MAPS_API_KEY":
                print("Google Maps API key not found")
                return False
            
            # Initialize client
            self.client = googlemaps.Client(key=self.api_key)
            
            print("Connected to Google Maps API successfully")
            return True
        except Exception as e:
            print(f"Error connecting to Google Maps API: {e}")
            return False
    
    def geocode(self, address):
        """
        Geocode an address to get coordinates.
        
        Args:
            address (str): The address to geocode
            
        Returns:
            dict: The geocoding result with lat/lng coordinates
        """
        # Check if connected
        if not self.client and not self.connect():
            return self._mock_geocode(address)
        
        try:
            # Call Geocoding API
            result = self.client.geocode(address)
            
            if result and len(result) > 0:
                # Extract location data
                location = result[0]['geometry']['location']
                formatted_address = result[0]['formatted_address']
                
                return {
                    "lat": location['lat'],
                    "lon": location['lng'],
                    "address": formatted_address
                }
            else:
                return None
        except Exception as e:
            print(f"Error geocoding address: {e}")
            
            # Fall back to mock geocoding
            return self._mock_geocode(address)
    
    def reverse_geocode(self, lat, lon):
        """
        Reverse geocode coordinates to get address.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: The reverse geocoding result with address
        """
        # Check if connected
        if not self.client and not self.connect():
            return self._mock_reverse_geocode(lat, lon)
        
        try:
            # Call Reverse Geocoding API
            result = self.client.reverse_geocode((lat, lon))
            
            if result and len(result) > 0:
                # Extract address data
                formatted_address = result[0]['formatted_address']
                
                return {
                    "lat": lat,
                    "lon": lon,
                    "address": formatted_address
                }
            else:
                return None
        except Exception as e:
            print(f"Error reverse geocoding coordinates: {e}")
            
            # Fall back to mock reverse geocoding
            return self._mock_reverse_geocode(lat, lon)
    
    def get_directions(self, origin, destination, mode="driving", alternatives=True):
        """
        Get directions between two points.
        
        Args:
            origin (dict): The origin location with lat/lon
            destination (dict): The destination location with lat/lon
            mode (str): The travel mode (driving, walking, bicycling, transit)
            alternatives (bool): Whether to return alternative routes
            
        Returns:
            dict: The directions result with routes
        """
        # Check if connected
        if not self.client and not self.connect():
            return self._mock_directions(origin, destination, mode, alternatives)
        
        try:
            # Format origin and destination
            origin_str = f"{origin['lat']},{origin['lon']}"
            destination_str = f"{destination['lat']},{destination['lon']}"
            
            # Call Directions API
            result = self.client.directions(
                origin=origin_str,
                destination=destination_str,
                mode=mode,
                alternatives=alternatives
            )
            
            if result and len(result) > 0:
                # Process routes
                routes = []
                
                for route in result:
                    # Extract route data
                    distance = route['legs'][0]['distance']['value']  # meters
                    duration = route['legs'][0]['duration']['value']  # seconds
                    
                    # Extract steps
                    steps = []
                    for step in route['legs'][0]['steps']:
                        start_loc = step['start_location']
                        end_loc = step['end_location']
                        
                        steps.append({
                            "start": {"lat": start_loc['lat'], "lon": start_loc['lng']},
                            "end": {"lat": end_loc['lat'], "lon": end_loc['lng']},
                            "distance": step['distance']['value'],  # meters
                            "duration": step['duration']['value'],  # seconds
                            "instruction": step['html_instructions']
                        })
                    
                    # Calculate safety score (mock for now)
                    safety_score = self._calculate_safety_score(steps)
                    
                    routes.append({
                        "distance": distance,
                        "duration": duration,
                        "steps": steps,
                        "safety_score": safety_score
                    })
                
                return {
                    "origin": origin,
                    "destination": destination,
                    "routes": routes
                }
            else:
                return None
        except Exception as e:
            print(f"Error getting directions: {e}")
            
            # Fall back to mock directions
            return self._mock_directions(origin, destination, mode, alternatives)
    
    def search_places(self, query, location=None, radius=5000, type=None):
        """
        Search for places.
        
        Args:
            query (str): The search query
            location (dict, optional): The location to search near
            radius (int, optional): The search radius in meters
            type (str, optional): The place type
            
        Returns:
            list: The search results
        """
        # Check if connected
        if not self.client and not self.connect():
            return self._mock_search_places(query, location, radius, type)
        
        try:
            # Prepare parameters
            params = {
                'query': query
            }
            
            if location:
                params['location'] = (location['lat'], location['lon'])
            
            if radius:
                params['radius'] = radius
            
            if type:
                params['type'] = type
            
            # Call Places API
            result = self.client.places(**params)
            
            if result and 'results' in result:
                # Process results
                places = []
                
                for place in result['results']:
                    # Extract place data
                    location = place['geometry']['location']
                    
                    places.append({
                        "name": place['name'],
                        "address": place.get('formatted_address', ''),
                        "lat": location['lat'],
                        "lon": location['lng'],
                        "rating": place.get('rating', 0),
                        "types": place.get('types', [])
                    })
                
                return places
            else:
                return []
        except Exception as e:
            print(f"Error searching places: {e}")
            
            # Fall back to mock search
            return self._mock_search_places(query, location, radius, type)
    
    def _calculate_safety_score(self, steps):
        """
        Calculate a safety score for a route.
        
        Args:
            steps (list): The route steps
            
        Returns:
            int: The safety score (0-100)
        """
        # In a real implementation, this would use incident data and other factors
        # For now, we'll use a random score between 60 and 95
        return random.randint(60, 95)
    
    def _mock_geocode(self, address):
        """
        Mock geocoding for offline use.
        
        Args:
            address (str): The address to geocode
            
        Returns:
            dict: The geocoding result with lat/lng coordinates
        """
        # Load sample locations
        locations = self._load_sample_locations()
        
        # Search for matching location
        address_lower = address.lower()
        for location in locations:
            if address_lower in location['address'].lower():
                return {
                    "lat": location['lat'],
                    "lon": location['lon'],
                    "address": location['address']
                }
        
        # If no match found, return a random location
        random_location = random.choice(locations)
        return {
            "lat": random_location['lat'],
            "lon": random_location['lon'],
            "address": random_location['address']
        }
    
    def _mock_reverse_geocode(self, lat, lon):
        """
        Mock reverse geocoding for offline use.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: The reverse geocoding result with address
        """
        # Load sample locations
        locations = self._load_sample_locations()
        
        # Find closest location
        closest_location = None
        closest_distance = float('inf')
        
        for location in locations:
            distance = geodesic((lat, lon), (location['lat'], location['lon'])).kilometers
            
            if distance < closest_distance:
                closest_distance = distance
                closest_location = location
        
        # Return closest location
        return {
            "lat": lat,
            "lon": lon,
            "address": closest_location['address']
        }
    
    def _mock_directions(self, origin, destination, mode="driving", alternatives=True):
        """
        Mock directions for offline use.
        
        Args:
            origin (dict): The origin location with lat/lon
            destination (dict): The destination location with lat/lon
            mode (str): The travel mode (driving, walking, bicycling, transit)
            alternatives (bool): Whether to return alternative routes
            
        Returns:
            dict: The directions result with routes
        """
        # Calculate distance between origin and destination
        distance = geodesic(
            (origin['lat'], origin['lon']),
            (destination['lat'], destination['lon'])
        ).meters
        
        # Calculate duration based on mode
        speed_factors = {
            "driving": 13.4,  # meters per second (about 48 km/h)
            "walking": 1.4,   # meters per second (about 5 km/h)
            "bicycling": 4.2,  # meters per second (about 15 km/h)
            "transit": 8.3    # meters per second (about 30 km/h)
        }
        
        speed = speed_factors.get(mode, 13.4)
        duration = distance / speed
        
        # Generate steps
        num_steps = random.randint(3, 8)
        step_distance = distance / num_steps
        step_duration = duration / num_steps
        
        steps = []
        current_lat = origin['lat']
        current_lon = origin['lon']
        
        for i in range(num_steps):
            # Calculate progress
            progress = (i + 1) / num_steps
            
            # Calculate end point of this step
            end_lat = origin['lat'] + (destination['lat'] - origin['lat']) * progress
            end_lon = origin['lon'] + (destination['lon'] - origin['lon']) * progress
            
            # Add some randomness
            if i < num_steps - 1:  # Don't randomize the final step
                end_lat += random.uniform(-0.001, 0.001)
                end_lon += random.uniform(-0.001, 0.001)
            
            # Create step
            steps.append({
                "start": {"lat": current_lat, "lon": current_lon},
                "end": {"lat": end_lat, "lon": end_lon},
                "distance": step_distance,
                "duration": step_duration,
                "instruction": self._generate_instruction(i, num_steps)
            })
            
            # Update current position
            current_lat = end_lat
            current_lon = end_lon
        
        # Create route
        route = {
            "distance": distance,
            "duration": duration,
            "steps": steps,
            "safety_score": self._calculate_safety_score(steps)
        }
        
        # Create alternative routes if requested
        routes = [route]
        
        if alternatives:
            # Create 1-2 alternative routes
            num_alternatives = random.randint(1, 2)
            
            for _ in range(num_alternatives):
                # Vary distance and duration slightly
                alt_distance = distance * random.uniform(0.9, 1.2)
                alt_duration = alt_distance / speed
                
                # Generate steps
                alt_num_steps = random.randint(3, 8)
                alt_step_distance = alt_distance / alt_num_steps
                alt_step_duration = alt_duration / alt_num_steps
                
                alt_steps = []
                alt_current_lat = origin['lat']
                alt_current_lon = origin['lon']
                
                for i in range(alt_num_steps):
                    # Calculate progress
                    progress = (i + 1) / alt_num_steps
                    
                    # Calculate end point of this step
                    end_lat = origin['lat'] + (destination['lat'] - origin['lat']) * progress
                    end_lon = origin['lon'] + (destination['lon'] - origin['lon']) * progress
                    
                    # Add more randomness for alternative routes
                    if i < alt_num_steps - 1:  # Don't randomize the final step
                        end_lat += random.uniform(-0.003, 0.003)
                        end_lon += random.uniform(-0.003, 0.003)
                    
                    # Create step
                    alt_steps.append({
                        "start": {"lat": alt_current_lat, "lon": alt_current_lon},
                        "end": {"lat": end_lat, "lon": end_lon},
                        "distance": alt_step_distance,
                        "duration": alt_step_duration,
                        "instruction": self._generate_instruction(i, alt_num_steps)
                    })
                    
                    # Update current position
                    alt_current_lat = end_lat
                    alt_current_lon = end_lon
                
                # Create alternative route
                alt_route = {
                    "distance": alt_distance,
                    "duration": alt_duration,
                    "steps": alt_steps,
                    "safety_score": self._calculate_safety_score(alt_steps)
                }
                
                routes.append(alt_route)
        
        return {
            "origin": origin,
            "destination": destination,
            "routes": routes
        }
    
    def _mock_search_places(self, query, location=None, radius=5000, type=None):
        """
        Mock place search for offline use.
        
        Args:
            query (str): The search query
            location (dict, optional): The location to search near
            radius (int, optional): The search radius in meters
            type (str, optional): The place type
            
        Returns:
            list: The search results
        """
        # Load sample locations
        locations = self._load_sample_locations()
        
        # Filter by query
        query_lower = query.lower()
        results = []
        
        for location in locations:
            if query_lower in location['address'].lower() or (
                'type' in location and query_lower in location['type'].lower()
            ):
                # If location parameter is provided, filter by distance
                if location:
                    distance = geodesic(
                        (location['lat'], location['lon']),
                        (location['lat'], location['lon'])
                    ).meters
                    
                    if distance > radius:
                        continue
                
                # If type parameter is provided, filter by type
                if type and ('type' not in location or location['type'] != type):
                    continue
                
                # Add to results
                results.append({
                    "name": location['address'],
                    "address": location['address'],
                    "lat": location['lat'],
                    "lon": location['lon'],
                    "rating": random.uniform(3.0, 5.0),
                    "types": [location.get('type', 'point_of_interest')]
                })
        
        # Limit results
        return results[:10]
    
    def _generate_instruction(self, step_index, total_steps):
        """
        Generate a mock instruction for a route step.
        
        Args:
            step_index (int): The step index
            total_steps (int): The total number of steps
            
        Returns:
            str: The instruction
        """
        if step_index == 0:
            return "Start heading north"
        elif step_index == total_steps - 1:
            return "Arrive at your destination"
        else:
            directions = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]
            actions = ["Continue", "Turn", "Slight turn", "Sharp turn"]
            
            action = random.choice(actions)
            direction = random.choice(directions)
            
            return f"{action} {direction}"
    
    def _load_sample_locations(self):
        """
        Load sample locations for offline use.
        
        Returns:
            list: Sample locations
        """
        # Check if cache file exists
        cache_dir = os.path.join('data')
        cache_path = os.path.join(cache_dir, 'maps_cache.json')
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cache = json.load(f)
                
                if 'addresses' in cache:
                    return cache['addresses']
            except Exception as e:
                print(f"Error loading sample locations: {e}")
        
        # Default sample locations
        return [
            {
                "address": "Sandton City, Johannesburg",
                "lat": -26.1052,
                "lon": 28.0567,
                "city": "Johannesburg",
                "type": "shopping_center"
            },
            {
                "address": "University of Pretoria, Pretoria",
                "lat": -25.7545,
                "lon": 28.2314,
                "city": "Pretoria",
                "type": "university"
            },
            {
                "address": "V&A Waterfront, Cape Town",
                "lat": -33.9033,
                "lon": 18.4197,
                "city": "Cape Town",
                "type": "tourist_attraction"
            },
            {
                "address": "Moses Mabhida Stadium, Durban",
                "lat": -29.8283,
                "lon": 31.0300,
                "city": "Durban",
                "type": "stadium"
            },
            {
                "address": "Kruger National Park, Mpumalanga",
                "lat": -24.0000,
                "lon": 31.5000,
                "city": "Mpumalanga",
                "type": "national_park"
            },
            {
                "address": "Johannesburg CBD",
                "lat": -26.2041,
                "lon": 28.0473,
                "city": "Johannesburg",
                "type": "business_district"
            },
            {
                "address": "Soweto, Johannesburg",
                "lat": -26.2485,
                "lon": 27.8540,
                "city": "Johannesburg",
                "type": "township"
            },
            {
                "address": "Pretoria CBD",
                "lat": -25.7461,
                "lon": 28.1881,
                "city": "Pretoria",
                "type": "business_district"
            },
            {
                "address": "Bloemfontein CBD",
                "lat": -29.1183,
                "lon": 26.2145,
                "city": "Bloemfontein",
                "type": "business_district"
            },
            {
                "address": "Durban Beach Front",
                "lat": -29.8497,
                "lon": 31.0334,
                "city": "Durban",
                "type": "beach"
            }
        ]

# Singleton instance
google_maps_client = GoogleMapsClient()

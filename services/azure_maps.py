"""
Azure Maps Service for SafeWayAI

This module provides integration with Azure Maps for geocoding, routing,
and crime data visualization.
"""

import os
import json
import datetime
from services.azure_client import AzureClient

class AzureMaps:
    """
    Azure Maps service for geocoding, routing, and crime data visualization.
    Replaces the mock maps and geocoding services with real Azure Maps API.
    """
    
    # Path to the local cache for offline use
    CACHE_PATH = os.path.join('data', 'maps_cache.json')
    
    @classmethod
    def _ensure_cache_exists(cls):
        """Ensure the maps cache exists for offline use."""
        os.makedirs(os.path.dirname(cls.CACHE_PATH), exist_ok=True)
        
        if not os.path.exists(cls.CACHE_PATH):
            # Create an empty cache
            default_cache = {
                "addresses": [],
                "routes": [],
                "danger_zones": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(cls.CACHE_PATH, 'w') as f:
                json.dump(default_cache, f, indent=2)
    
    @classmethod
    def _get_maps_config(cls):
        """Get Azure Maps configuration."""
        config = AzureClient.load_config()
        return config["maps"]
    
    @classmethod
    def search_addresses(cls, query, limit=5, callback=None):
        """
        Search for addresses matching the query using Azure Maps Search API.
        
        Args:
            query (str): The search query
            limit (int, optional): Maximum number of results to return
            callback (callable, optional): Function to call with results
            
        Returns:
            If callback is None, this function will use the cache and return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not query or len(query) < 2:
            if callback:
                callback([])
            return []
        
        # Try to use cached data if no callback (synchronous mode)
        if not callback:
            cls._ensure_cache_exists()
            with open(cls.CACHE_PATH, 'r') as f:
                cache = json.load(f)
            
            # Filter cached addresses by query
            results = []
            for addr in cache["addresses"]:
                if query.lower() in addr["address"].lower():
                    results.append(addr)
            
            # Sort by relevance and limit
            results = sorted(
                results, 
                key=lambda x: 1 if x["address"].lower().startswith(query.lower()) else 0,
                reverse=True
            )[:limit]
            
            return results
        
        # Otherwise, make an async request to Azure Maps
        maps_config = cls._get_maps_config()
        base_url = maps_config["base_url"]
        subscription_key = maps_config["subscription_key"]
        
        # Build the search URL
        url = f"{base_url}search/fuzzy/json?api-version=1.0&query={query}&limit={limit}"
        headers = {"Subscription-Key": subscription_key}
        
        def on_success(req, result):
            # Convert Azure Maps results to our format
            addresses = []
            if "results" in result:
                for item in result["results"]:
                    address = {
                        "address": item.get("address", {}).get("freeformAddress", ""),
                        "lat": item.get("position", {}).get("lat", 0),
                        "lon": item.get("position", {}).get("lon", 0),
                        "city": item.get("address", {}).get("municipality", ""),
                        "type": item.get("type", "street_address")
                    }
                    addresses.append(address)
            
            # Cache the results
            cls._cache_addresses(addresses)
            
            # Call the callback with the results
            callback(addresses)
        
        def on_failure(req, result):
            print(f"Azure Maps search failed: {result}")
            # Fall back to cache
            cls._ensure_cache_exists()
            with open(cls.CACHE_PATH, 'r') as f:
                cache = json.load(f)
            
            # Filter cached addresses by query
            results = []
            for addr in cache["addresses"]:
                if query.lower() in addr["address"].lower():
                    results.append(addr)
            
            # Sort by relevance and limit
            results = sorted(
                results, 
                key=lambda x: 1 if x["address"].lower().startswith(query.lower()) else 0,
                reverse=True
            )[:limit]
            
            callback(results)
        
        def on_error(req, error):
            print(f"Azure Maps search error: {error}")
            # Fall back to cache
            callback(cls.search_addresses(query, limit))
        
        # Make the request
        AzureClient.make_request(
            url,
            headers=headers,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error
        )
    
    @classmethod
    def _cache_addresses(cls, addresses):
        """Cache addresses for offline use."""
        cls._ensure_cache_exists()
        
        with open(cls.CACHE_PATH, 'r') as f:
            cache = json.load(f)
        
        # Add new addresses to cache, avoiding duplicates
        existing_addresses = {addr["address"].lower() for addr in cache["addresses"]}
        for addr in addresses:
            if addr["address"].lower() not in existing_addresses:
                cache["addresses"].append(addr)
                existing_addresses.add(addr["address"].lower())
        
        cache["last_updated"] = datetime.datetime.now().isoformat()
        
        with open(cls.CACHE_PATH, 'w') as f:
            json.dump(cache, f, indent=2)
    
    @classmethod
    def geocode(cls, address, callback=None):
        """
        Convert an address to coordinates using Azure Maps.
        
        Args:
            address (str): The address to geocode
            callback (callable, optional): Function to call with result
            
        Returns:
            If callback is None, this function will use the cache and return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not callback:
            # Try to find in cache
            cls._ensure_cache_exists()
            with open(cls.CACHE_PATH, 'r') as f:
                cache = json.load(f)
            
            # Look for exact match first
            for addr in cache["addresses"]:
                if addr["address"].lower() == address.lower():
                    return addr
            
            # If no exact match, try partial match
            results = cls.search_addresses(address, limit=1)
            if results:
                return results[0]
            
            return None
        
        # Otherwise, search asynchronously
        def on_search_complete(results):
            if results:
                callback(results[0])
            else:
                callback(None)
        
        cls.search_addresses(address, limit=1, callback=on_search_complete)
    
    @classmethod
    def get_danger_zones(cls, lat, lon, radius=5000, callback=None):
        """
        Get danger zones near a location using Azure Maps and crime data.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            radius (int): Search radius in meters
            callback (callable, optional): Function to call with result
            
        Returns:
            If callback is None, this function will use the cache and return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not callback:
            # Use cached data
            cls._ensure_cache_exists()
            with open(cls.CACHE_PATH, 'r') as f:
                cache = json.load(f)
            
            # Find nearby danger zones
            nearby_zones = []
            for zone in cache["danger_zones"]:
                # Calculate distance (simplified)
                zone_lat = zone["lat"]
                zone_lon = zone["lon"]
                distance_km = cls._calculate_distance(lat, lon, zone_lat, zone_lon)
                
                if distance_km * 1000 <= radius:
                    zone_with_distance = zone.copy()
                    zone_with_distance["distance_km"] = distance_km
                    nearby_zones.append(zone_with_distance)
            
            # Determine if the location is unsafe
            is_unsafe = len(nearby_zones) > 0
            risk_level = max([zone.get("risk_level", 0) for zone in nearby_zones]) if nearby_zones else 0
            
            return {
                "is_unsafe": is_unsafe,
                "risk_level": risk_level,
                "nearby_danger_zones": nearby_zones,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Otherwise, make an async request to Azure Maps
        maps_config = cls._get_maps_config()
        base_url = maps_config["base_url"]
        subscription_key = maps_config["subscription_key"]
        
        # Build the URL for getting crime data
        # Note: This is a placeholder. Azure Maps doesn't have a direct crime data API.
        # In a real implementation, you would need to use a custom Azure Function that
        # combines Azure Maps with your crime data source.
        url = f"{base_url}spatial/geofence/json?api-version=1.0&lat={lat}&lon={lon}&radius={radius}"
        headers = {"Subscription-Key": subscription_key}
        
        def on_success(req, result):
            # Process the result (this is a placeholder)
            nearby_zones = []
            is_unsafe = False
            risk_level = 0
            
            # In a real implementation, you would process the actual crime data here
            # For now, we'll just use the cached data
            cls._ensure_cache_exists()
            with open(cls.CACHE_PATH, 'r') as f:
                cache = json.load(f)
            
            # Find nearby danger zones
            for zone in cache["danger_zones"]:
                # Calculate distance (simplified)
                zone_lat = zone["lat"]
                zone_lon = zone["lon"]
                distance_km = cls._calculate_distance(lat, lon, zone_lat, zone_lon)
                
                if distance_km * 1000 <= radius:
                    zone_with_distance = zone.copy()
                    zone_with_distance["distance_km"] = distance_km
                    nearby_zones.append(zone_with_distance)
            
            # Determine if the location is unsafe
            is_unsafe = len(nearby_zones) > 0
            risk_level = max([zone.get("risk_level", 0) for zone in nearby_zones]) if nearby_zones else 0
            
            response = {
                "is_unsafe": is_unsafe,
                "risk_level": risk_level,
                "nearby_danger_zones": nearby_zones,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            callback(response)
        
        def on_failure(req, result):
            print(f"Azure Maps danger zones request failed: {result}")
            # Fall back to cache
            callback(cls.get_danger_zones(lat, lon, radius))
        
        def on_error(req, error):
            print(f"Azure Maps danger zones request error: {error}")
            # Fall back to cache
            callback(cls.get_danger_zones(lat, lon, radius))
        
        # Make the request
        AzureClient.make_request(
            url,
            headers=headers,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error
        )
    
    @classmethod
    def plan_route(cls, start_lat, start_lon, end_lat, end_lon, callback=None):
        """
        Plan a safe route using Azure Maps and crime data.
        
        Args:
            start_lat (float): Starting latitude
            start_lon (float): Starting longitude
            end_lat (float): Ending latitude
            end_lon (float): Ending longitude
            callback (callable, optional): Function to call with result
            
        Returns:
            If callback is None, this function will use the cache and return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not callback:
            # Use cached data
            cls._ensure_cache_exists()
            with open(cls.CACHE_PATH, 'r') as f:
                cache = json.load(f)
            
            # Check if we have a cached route
            for route in cache["routes"]:
                if (abs(route["start_lat"] - start_lat) < 0.001 and
                    abs(route["start_lon"] - start_lon) < 0.001 and
                    abs(route["end_lat"] - end_lat) < 0.001 and
                    abs(route["end_lon"] - end_lon) < 0.001):
                    return route["waypoints"]
            
            # If no cached route, generate a simple one
            return cls._generate_simple_route(start_lat, start_lon, end_lat, end_lon)
        
        # Otherwise, make an async request to Azure Maps
        maps_config = cls._get_maps_config()
        base_url = maps_config["base_url"]
        subscription_key = maps_config["subscription_key"]
        
        # Build the URL for route planning
        url = (f"{base_url}route/directions/json?api-version=1.0&query={start_lat},{start_lon}:{end_lat},{end_lon}"
               f"&routeType=fastest&traffic=true&travelMode=car")
        headers = {"Subscription-Key": subscription_key}
        
        def on_success(req, result):
            # Process the route
            waypoints = []
            
            if "routes" in result and result["routes"]:
                route = result["routes"][0]
                legs = route.get("legs", [])
                
                # Process each leg of the route
                for leg_idx, leg in enumerate(legs):
                    points = leg.get("points", [])
                    
                    for point_idx, point in enumerate(points):
                        lat = point.get("latitude")
                        lon = point.get("longitude")
                        
                        # Get maneuver instruction if available
                        instruction = "Continue"
                        if "maneuvers" in leg and point_idx < len(leg["maneuvers"]):
                            instruction = leg["maneuvers"][point_idx].get("instruction", "Continue")
                        
                        # Calculate safety score (placeholder)
                        # In a real implementation, you would check crime data for each point
                        safety_score = 90  # Default high safety
                        
                        waypoint = {
                            "lat": lat,
                            "lon": lon,
                            "instruction": instruction,
                            "distance": 0,  # Will be calculated below
                            "is_safe": True,
                            "safety_score": safety_score
                        }
                        
                        # Calculate distance from previous point
                        if waypoints:
                            prev = waypoints[-1]
                            distance = cls._calculate_distance(
                                prev["lat"], prev["lon"], lat, lon
                            )
                            waypoint["distance"] = distance
                        
                        waypoints.append(waypoint)
            
            # If no route was found, generate a simple one
            if not waypoints:
                waypoints = cls._generate_simple_route(start_lat, start_lon, end_lat, end_lon)
            
            # Cache the route
            cls._cache_route(start_lat, start_lon, end_lat, end_lon, waypoints)
            
            callback(waypoints)
        
        def on_failure(req, result):
            print(f"Azure Maps route planning failed: {result}")
            # Fall back to simple route
            waypoints = cls._generate_simple_route(start_lat, start_lon, end_lat, end_lon)
            callback(waypoints)
        
        def on_error(req, error):
            print(f"Azure Maps route planning error: {error}")
            # Fall back to simple route
            waypoints = cls._generate_simple_route(start_lat, start_lon, end_lat, end_lon)
            callback(waypoints)
        
        # Make the request
        AzureClient.make_request(
            url,
            headers=headers,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error
        )
    
    @classmethod
    def _generate_simple_route(cls, start_lat, start_lon, end_lat, end_lon):
        """Generate a simple route between two points."""
        # Create a simple route with 5 waypoints
        waypoints = []
        
        # Starting point
        waypoints.append({
            "lat": start_lat,
            "lon": start_lon,
            "instruction": "Start",
            "distance": 0,
            "is_safe": True,
            "safety_score": 90
        })
        
        # Generate 3 intermediate points
        for i in range(1, 4):
            progress = i / 4
            lat = start_lat + (end_lat - start_lat) * progress
            lon = start_lon + (end_lon - start_lon) * progress
            
            waypoint = {
                "lat": lat,
                "lon": lon,
                "instruction": "Continue",
                "distance": 0,
                "is_safe": True,
                "safety_score": 90
            }
            
            # Calculate distance from previous point
            prev = waypoints[-1]
            distance = cls._calculate_distance(
                prev["lat"], prev["lon"], lat, lon
            )
            waypoint["distance"] = distance
            
            waypoints.append(waypoint)
        
        # Ending point
        waypoints.append({
            "lat": end_lat,
            "lon": end_lon,
            "instruction": "Arrive at destination",
            "distance": cls._calculate_distance(
                waypoints[-1]["lat"], waypoints[-1]["lon"], end_lat, end_lon
            ),
            "is_safe": True,
            "safety_score": 90
        })
        
        return waypoints
    
    @classmethod
    def _cache_route(cls, start_lat, start_lon, end_lat, end_lon, waypoints):
        """Cache a route for offline use."""
        cls._ensure_cache_exists()
        
        with open(cls.CACHE_PATH, 'r') as f:
            cache = json.load(f)
        
        # Add the route to cache
        route = {
            "start_lat": start_lat,
            "start_lon": start_lon,
            "end_lat": end_lat,
            "end_lon": end_lon,
            "waypoints": waypoints,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Remove any existing routes with the same start/end
        cache["routes"] = [r for r in cache["routes"] if not (
            abs(r["start_lat"] - start_lat) < 0.001 and
            abs(r["start_lon"] - start_lon) < 0.001 and
            abs(r["end_lat"] - end_lat) < 0.001 and
            abs(r["end_lon"] - end_lon) < 0.001
        )]
        
        cache["routes"].append(route)
        cache["last_updated"] = datetime.datetime.now().isoformat()
        
        with open(cls.CACHE_PATH, 'w') as f:
            json.dump(cache, f, indent=2)
    
    @classmethod
    def report_danger_zone(cls, lat, lon, risk_level, risk_factors, name=None):
        """
        Report a new danger zone or update an existing one.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            risk_level (int): Risk level from 1-10
            risk_factors (list): List of risk factors (e.g., ["theft", "assault"])
            name (str, optional): Name of the location
            
        Returns:
            dict: The created or updated danger zone
        """
        cls._ensure_cache_exists()
        
        with open(cls.CACHE_PATH, 'r') as f:
            cache = json.load(f)
        
        # Check if this zone already exists
        for zone in cache["danger_zones"]:
            if abs(zone["lat"] - lat) < 0.001 and abs(zone["lon"] - lon) < 0.001:
                # Update existing zone
                zone["risk_level"] = risk_level
                zone["risk_factors"] = risk_factors
                zone["last_updated"] = datetime.datetime.now().isoformat()
                zone["report_count"] = zone.get("report_count", 0) + 1
                
                if name:
                    zone["name"] = name
                
                with open(cls.CACHE_PATH, 'w') as f:
                    json.dump(cache, f, indent=2)
                
                return zone
        
        # Create new zone
        new_zone = {
            "lat": lat,
            "lon": lon,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "name": name or f"Reported Zone at {lat:.4f}, {lon:.4f}",
            "created": datetime.datetime.now().isoformat(),
            "last_updated": datetime.datetime.now().isoformat(),
            "report_count": 1
        }
        
        cache["danger_zones"].append(new_zone)
        cache["last_updated"] = datetime.datetime.now().isoformat()
        
        with open(cls.CACHE_PATH, 'w') as f:
            json.dump(cache, f, indent=2)
        
        return new_zone
    
    @classmethod
    def _calculate_distance(cls, lat1, lon1, lat2, lon2):
        """
        Calculate the distance between two points in kilometers.
        Uses the Haversine formula.
        """
        import math
        
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = 6371 * c  # Earth radius in kilometers
        
        return distance

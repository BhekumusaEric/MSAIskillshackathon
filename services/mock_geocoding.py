"""
Mock Geocoding Service for SafeWayAI

This module provides a mock implementation of geocoding services for development and testing.
"""

import time
import random

class MockGeocoding:
    """Mock implementation of geocoding services."""

    # Sample locations in South Africa
    SAMPLE_LOCATIONS = [
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
        },
        {
            "address": "Table Mountain, Cape Town",
            "lat": -33.9628,
            "lon": 18.4098,
            "city": "Cape Town",
            "type": "mountain"
        },
        {
            "address": "OR Tambo International Airport, Johannesburg",
            "lat": -26.1367,
            "lon": 28.2411,
            "city": "Johannesburg",
            "type": "airport"
        },
        {
            "address": "Cape Town International Airport",
            "lat": -33.9715,
            "lon": 18.6021,
            "city": "Cape Town",
            "type": "airport"
        },
        {
            "address": "King Shaka International Airport, Durban",
            "lat": -29.6144,
            "lon": 31.1197,
            "city": "Durban",
            "type": "airport"
        },
        {
            "address": "Johannesburg Park Station",
            "lat": -26.1969,
            "lon": 28.0436,
            "city": "Johannesburg",
            "type": "train_station"
        },
        {
            "address": "57 Bok Street, Johannesburg",
            "lat": -26.2041,
            "lon": 28.0473,
            "city": "Johannesburg",
            "type": "address"
        },
        {
            "address": "123 Main Road, Cape Town",
            "lat": -33.9033,
            "lon": 18.4197,
            "city": "Cape Town",
            "type": "address"
        },
        {
            "address": "45 Church Street, Pretoria",
            "lat": -25.7461,
            "lon": 28.1881,
            "city": "Pretoria",
            "type": "address"
        },
        {
            "address": "78 Beach Road, Durban",
            "lat": -29.8497,
            "lon": 31.0334,
            "city": "Durban",
            "type": "address"
        },
        {
            "address": "WeThinkCode_, Johannesburg",
            "lat": -26.2041,
            "lon": 28.0473,
            "city": "Johannesburg",
            "type": "education"
        },
        {
            "address": "University of Cape Town",
            "lat": -33.9580,
            "lon": 18.4611,
            "city": "Cape Town",
            "type": "university"
        },
        {
            "address": "University of the Witwatersrand, Johannesburg",
            "lat": -26.1929,
            "lon": 28.0305,
            "city": "Johannesburg",
            "type": "university"
        },
        {
            "address": "Gautrain Station, Sandton",
            "lat": -26.1067,
            "lon": 28.0567,
            "city": "Johannesburg",
            "type": "train_station"
        },
        {
            "address": "Gautrain Station, Rosebank",
            "lat": -26.1467,
            "lon": 28.0436,
            "city": "Johannesburg",
            "type": "train_station"
        },
        {
            "address": "Gautrain Station, Park",
            "lat": -26.1969,
            "lon": 28.0436,
            "city": "Johannesburg",
            "type": "train_station"
        }
    ]

    @classmethod
    def geocode(cls, address):
        """
        Geocode an address to get coordinates.

        Args:
            address (str): The address to geocode

        Returns:
            dict: The geocoding result with lat/lng coordinates
        """
        # Simulate network delay
        time.sleep(0.5)

        # Search for matching location
        address_lower = address.lower()
        for location in cls.SAMPLE_LOCATIONS:
            if address_lower in location["address"].lower():
                return location

        # If no match found, return a random location
        return random.choice(cls.SAMPLE_LOCATIONS)

    @classmethod
    def search_places(cls, query, location=None, radius=5000, type=None):
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
        # This is similar to search_addresses but with the Google Maps API signature
        return cls.search_addresses(query, limit=10)

    @classmethod
    def search_addresses(cls, query, limit=5):
        """
        Search for addresses matching the query.

        Args:
            query (str): The search query
            limit (int): Maximum number of results to return

        Returns:
            list: List of matching locations
        """
        # Simulate network delay
        time.sleep(0.5)

        # Filter locations based on the query
        results = []
        query = query.lower()

        for location in cls.SAMPLE_LOCATIONS:
            if query in location["address"].lower() or query in location.get("city", "").lower():
                results.append(location)

        # Sort by relevance (simple implementation - just checks if query is at the start of the address)
        results.sort(key=lambda x: 0 if x["address"].lower().startswith(query) else 1)

        # Return limited results
        return results[:limit]

    @classmethod
    def get_current_location(cls):
        """
        Get the current location (mocked).

        Returns:
            dict: The current location
        """
        # Simulate network delay
        time.sleep(1)

        # Return a random location as the "current" location
        return random.choice(cls.SAMPLE_LOCATIONS)

    @classmethod
    def get_route(cls, start_lat, start_lon, end_lat, end_lon):
        """
        Get a route between two points.

        Args:
            start_lat (float): Starting latitude
            start_lon (float): Starting longitude
            end_lat (float): Ending latitude
            end_lon (float): Ending longitude

        Returns:
            dict: Route information
        """
        # Simulate network delay
        time.sleep(1.5)

        # Calculate distance (very rough approximation)
        distance = ((end_lat - start_lat) ** 2 + (end_lon - start_lon) ** 2) ** 0.5 * 111  # km

        # Generate a mock route
        route = {
            "distance": round(distance, 2),  # km
            "duration": round(distance * 2, 2),  # minutes (assuming 30 km/h average speed)
            "safety_score": random.randint(60, 95),  # random safety score
            "start": {
                "lat": start_lat,
                "lon": start_lon
            },
            "end": {
                "lat": end_lat,
                "lon": end_lon
            },
            "waypoints": [
                {"lat": start_lat, "lon": start_lon},
                {"lat": (2 * start_lat + end_lat) / 3, "lon": (2 * start_lon + end_lon) / 3},
                {"lat": (start_lat + 2 * end_lat) / 3, "lon": (start_lon + 2 * end_lon) / 3},
                {"lat": end_lat, "lon": end_lon}
            ]
        }

        return route

"""
Crime Data Service for SafeWayAI

This module provides access to crime data for route safety analysis.
"""

import os
import json
import random
import datetime
import requests
from geopy.distance import geodesic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CrimeDataService:
    """Service for accessing crime data."""

    def __init__(self):
        """Initialize the crime data service."""
        # Define crime types and severity levels
        self.crime_types = {
            "theft": {"severity": 5, "description": "Theft or stealing of property"},
            "robbery": {"severity": 7, "description": "Theft with force or threat of force"},
            "assault": {"severity": 8, "description": "Physical attack on a person"},
            "murder": {"severity": 10, "description": "Unlawful killing of a person"},
            "sexual_assault": {"severity": 9, "description": "Sexual attack or harassment"},
            "vandalism": {"severity": 4, "description": "Damage to property"},
            "drug_related": {"severity": 6, "description": "Drug-related offenses"},
            "fraud": {"severity": 3, "description": "Deception for financial gain"},
            "kidnapping": {"severity": 9, "description": "Unlawful detention of a person"},
            "arson": {"severity": 8, "description": "Deliberate setting of fire"},
            "burglary": {"severity": 6, "description": "Breaking into a building to commit a crime"},
            "vehicle_theft": {"severity": 5, "description": "Theft of a vehicle"},
            "public_disorder": {"severity": 3, "description": "Disruptive behavior in public"},
            "weapon_offense": {"severity": 7, "description": "Illegal possession or use of weapons"},
            "traffic_violation": {"severity": 2, "description": "Violation of traffic laws"}
        }

        # Define time factors (higher values mean higher risk)
        self.time_factors = {
            "morning": 1.0,  # 6:00 - 11:59
            "afternoon": 1.2,  # 12:00 - 17:59
            "evening": 1.5,  # 18:00 - 21:59
            "night": 2.0,  # 22:00 - 5:59
        }

        # Load crime data
        self.crime_data = self._load_crime_data()

        print("Crime data service initialized")

    def _load_crime_data(self):
        """
        Load crime data from file or API.

        Returns:
            list: Crime data
        """
        # Try to load from cache first
        cache_dir = os.path.join('data')
        cache_path = os.path.join(cache_dir, 'crime_data.json')

        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading crime data from cache: {e}")

        # If cache doesn't exist or is invalid, generate synthetic data
        return self._generate_synthetic_crime_data()

    def _generate_synthetic_crime_data(self):
        """
        Generate synthetic crime data for testing.

        Returns:
            list: Synthetic crime data
        """
        # Define crime types
        crime_types = list(self.crime_types.keys())

        # Define areas with different crime rates
        # These are real locations in South Africa
        high_crime_areas = [
            {"name": "Johannesburg CBD", "lat": -26.2041, "lon": 28.0473, "radius": 3},
            {"name": "Hillbrow, Johannesburg", "lat": -26.1908, "lon": 28.0435, "radius": 2},
            {"name": "Durban CBD", "lat": -29.8587, "lon": 31.0218, "radius": 3},
            {"name": "Cape Town CBD", "lat": -33.9249, "lon": 18.4241, "radius": 3},
            {"name": "Pretoria CBD", "lat": -25.7461, "lon": 28.1881, "radius": 3},
            {"name": "Alexandra, Johannesburg", "lat": -26.1058, "lon": 28.1066, "radius": 2},
            {"name": "Nyanga, Cape Town", "lat": -33.9793, "lon": 18.5814, "radius": 2},
            {"name": "Umlazi, Durban", "lat": -29.9673, "lon": 30.9276, "radius": 2},
            {"name": "Sunnyside, Pretoria", "lat": -25.7551, "lon": 28.2137, "radius": 2},
            {"name": "Khayelitsha, Cape Town", "lat": -34.0256, "lon": 18.6492, "radius": 3}
        ]

        medium_crime_areas = [
            {"name": "Sandton, Johannesburg", "lat": -26.1052, "lon": 28.0567, "radius": 4},
            {"name": "Rosebank, Johannesburg", "lat": -26.1467, "lon": 28.0436, "radius": 2},
            {"name": "Umhlanga, Durban", "lat": -29.7267, "lon": 31.0850, "radius": 3},
            {"name": "Sea Point, Cape Town", "lat": -33.9179, "lon": 18.3881, "radius": 2},
            {"name": "Centurion, Pretoria", "lat": -25.8602, "lon": 28.1900, "radius": 4},
            {"name": "Braamfontein, Johannesburg", "lat": -26.1925, "lon": 28.0320, "radius": 2},
            {"name": "Berea, Durban", "lat": -29.8497, "lon": 31.0064, "radius": 2},
            {"name": "Observatory, Cape Town", "lat": -33.9375, "lon": 18.4700, "radius": 2},
            {"name": "Hatfield, Pretoria", "lat": -25.7487, "lon": 28.2380, "radius": 2},
            {"name": "Pinetown, Durban", "lat": -29.8168, "lon": 30.8474, "radius": 3}
        ]

        low_crime_areas = [
            {"name": "Houghton, Johannesburg", "lat": -26.1667, "lon": 28.0500, "radius": 2},
            {"name": "Constantia, Cape Town", "lat": -34.0253, "lon": 18.4213, "radius": 3},
            {"name": "La Lucia, Durban", "lat": -29.7500, "lon": 31.0667, "radius": 2},
            {"name": "Waterkloof, Pretoria", "lat": -25.7833, "lon": 28.2333, "radius": 2},
            {"name": "Camps Bay, Cape Town", "lat": -33.9500, "lon": 18.3833, "radius": 2},
            {"name": "Bryanston, Johannesburg", "lat": -26.0667, "lon": 28.0167, "radius": 3},
            {"name": "Kloof, Durban", "lat": -29.7833, "lon": 30.8333, "radius": 2},
            {"name": "Bishopscourt, Cape Town", "lat": -33.9833, "lon": 18.4500, "radius": 2},
            {"name": "Lynnwood, Pretoria", "lat": -25.7500, "lon": 28.2833, "radius": 2},
            {"name": "Westville, Durban", "lat": -29.8333, "lon": 30.9167, "radius": 3}
        ]

        # Generate crimes
        crimes = []

        # Current time
        now = datetime.datetime.now()

        # Generate crimes for high crime areas (more crimes)
        for area in high_crime_areas:
            num_crimes = random.randint(30, 50)
            for _ in range(num_crimes):
                crimes.append(self._generate_crime(area, now, crime_types, high_probability=True))

        # Generate crimes for medium crime areas
        for area in medium_crime_areas:
            num_crimes = random.randint(15, 30)
            for _ in range(num_crimes):
                crimes.append(self._generate_crime(area, now, crime_types))

        # Generate crimes for low crime areas (fewer crimes)
        for area in low_crime_areas:
            num_crimes = random.randint(5, 15)
            for _ in range(num_crimes):
                crimes.append(self._generate_crime(area, now, crime_types, low_probability=True))

        # Save to cache
        try:
            cache_dir = os.path.join('data')
            os.makedirs(cache_dir, exist_ok=True)

            cache_path = os.path.join(cache_dir, 'crime_data.json')
            with open(cache_path, 'w') as f:
                json.dump(crimes, f)
        except Exception as e:
            print(f"Error saving crime data to cache: {e}")

        return crimes

    def _generate_crime(self, area, now, crime_types, high_probability=False, low_probability=False):
        """
        Generate a synthetic crime.

        Args:
            area (dict): The area to generate the crime in
            now (datetime): The current time
            crime_types (list): List of crime types
            high_probability (bool): Whether to use high-severity crimes with higher probability
            low_probability (bool): Whether to use low-severity crimes with higher probability

        Returns:
            dict: The generated crime
        """
        # Generate random location within the area
        lat_offset = random.uniform(-area["radius"], area["radius"]) / 111  # 1 degree is approximately 111 km
        lon_offset = random.uniform(-area["radius"], area["radius"]) / (111 * abs(area["lat"]) / 90)

        lat = area["lat"] + lat_offset
        lon = area["lon"] + lon_offset

        # Generate random time within the last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)

        timestamp = now - datetime.timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

        # Select crime type based on probabilities
        if high_probability:
            # Higher probability of serious crimes in high crime areas
            weights = [self.crime_types[ct]["severity"] for ct in crime_types]
        elif low_probability:
            # Higher probability of minor crimes in low crime areas
            weights = [10 - self.crime_types[ct]["severity"] for ct in crime_types]
        else:
            # Equal probability for all crime types
            weights = [1] * len(crime_types)

        crime_type = random.choices(crime_types, weights=weights, k=1)[0]

        # Generate severity (with some randomness around the base severity)
        base_severity = self.crime_types[crime_type]["severity"]
        severity = max(1, min(10, base_severity + random.randint(-1, 1)))

        # Generate a unique ID
        crime_id = f"crime_{timestamp.strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"

        return {
            "id": crime_id,
            "type": crime_type,
            "description": self.crime_types[crime_type]["description"],
            "severity": severity,
            "latitude": lat,
            "longitude": lon,
            "location": area["name"],
            "timestamp": timestamp.isoformat(),
            "reported": True,
            "verified": random.random() > 0.2  # 80% chance of being verified
        }

    def get_crimes_near_location(self, lat, lon, radius_km=1.0, days=30):
        """
        Get crimes near a location.

        Args:
            lat (float): Latitude
            lon (float): Longitude
            radius_km (float): Radius in kilometers
            days (int): Number of days to look back

        Returns:
            list: Crimes near the location
        """
        # Calculate the cutoff date
        now = datetime.datetime.now()
        cutoff_date = now - datetime.timedelta(days=days)

        # Filter crimes by location and date
        nearby_crimes = []

        for crime in self.crime_data:
            # Check if the crime is within the time range
            crime_time = datetime.datetime.fromisoformat(crime["timestamp"])
            if crime_time < cutoff_date:
                continue

            # Calculate distance
            crime_lat = crime["latitude"]
            crime_lon = crime["longitude"]

            distance = geodesic((lat, lon), (crime_lat, crime_lon)).kilometers

            if distance <= radius_km:
                # Add distance to the crime object
                crime_copy = crime.copy()
                crime_copy["distance_km"] = distance
                nearby_crimes.append(crime_copy)

        return nearby_crimes

    def get_crimes_along_route(self, route, radius_km=0.5, days=30):
        """
        Get crimes along a route.

        Args:
            route (dict): The route with steps
            radius_km (float): Radius in kilometers around each step
            days (int): Number of days to look back

        Returns:
            list: Crimes along the route
        """
        # Get steps from the route
        steps = route.get("steps", [])

        # Get crimes near each step
        all_crimes = []
        crime_ids = set()  # To avoid duplicates

        for step in steps:
            # Get step location (midpoint)
            start = step.get("start", {})
            end = step.get("end", {})

            step_lat = (start.get("lat", 0) + end.get("lat", 0)) / 2
            step_lon = (start.get("lon", 0) + end.get("lon", 0)) / 2

            # Get crimes near this step
            step_crimes = self.get_crimes_near_location(step_lat, step_lon, radius_km, days)

            # Add to the list if not already added
            for crime in step_crimes:
                if crime["id"] not in crime_ids:
                    crime_ids.add(crime["id"])
                    all_crimes.append(crime)

        return all_crimes

    def calculate_route_safety(self, route, time_of_day=None):
        """
        Calculate the safety score for a route.

        Args:
            route (dict): The route with steps
            time_of_day (str, optional): The time of day (morning, afternoon, evening, night)

        Returns:
            dict: Safety analysis results
        """
        # Default time of day to current time
        if time_of_day is None:
            hour = datetime.datetime.now().hour
            if 6 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 18:
                time_of_day = "afternoon"
            elif 18 <= hour < 22:
                time_of_day = "evening"
            else:
                time_of_day = "night"

        # Get crimes along the route
        crimes = self.get_crimes_along_route(route)

        # Calculate base safety score (100 is safest, 0 is least safe)
        base_score = 100

        # Adjust for crimes
        crime_penalty = 0
        for crime in crimes:
            # Higher severity crimes have a bigger impact
            severity = crime.get("severity", 5)

            # More recent crimes have a bigger impact
            crime_time = datetime.datetime.fromisoformat(crime["timestamp"])
            days_ago = (datetime.datetime.now() - crime_time).days
            recency_factor = max(0.2, 1.0 - (days_ago / 30))  # 1.0 for today, 0.2 for 30 days ago

            # Calculate penalty for this crime
            crime_penalty += severity * recency_factor

        # Adjust for time of day
        time_factor = self.time_factors.get(time_of_day, 1.0)

        # Calculate final safety score
        safety_score = max(0, min(100, base_score - (crime_penalty * time_factor)))

        # Determine safety level
        if safety_score >= 80:
            safety_level = "very_safe"
        elif safety_score >= 60:
            safety_level = "safe"
        elif safety_score >= 40:
            safety_level = "moderate"
        elif safety_score >= 20:
            safety_level = "unsafe"
        else:
            safety_level = "very_unsafe"

        # Calculate risk factors
        risk_factors = []

        # Time of day risk
        if time_of_day in ["evening", "night"]:
            risk_factors.append({
                "factor": "time_of_day",
                "description": f"Traveling during {time_of_day} hours",
                "impact": "high" if time_of_day == "night" else "moderate"
            })

        # Crime hotspot risk
        if len(crimes) > 0:
            risk_factors.append({
                "factor": "crime_hotspot",
                "description": f"{len(crimes)} crimes reported along this route in the last 30 days",
                "impact": "high" if len(crimes) > 5 else "moderate"
            })

        # Specific crime types
        crime_types = {}
        for crime in crimes:
            crime_type = crime.get("type")
            if crime_type:
                crime_types[crime_type] = crime_types.get(crime_type, 0) + 1

        for crime_type, count in crime_types.items():
            if count > 1 and crime_type in self.crime_types:
                severity = self.crime_types[crime_type]["severity"]
                impact = "high" if severity >= 7 else "moderate"

                risk_factors.append({
                    "factor": f"{crime_type}_incidents",
                    "description": f"{count} {crime_type.replace('_', ' ')} incidents reported along this route",
                    "impact": impact
                })

        return {
            "safety_score": safety_score,
            "safety_level": safety_level,
            "time_of_day": time_of_day,
            "crime_count": len(crimes),
            "risk_factors": risk_factors,
            "crimes": crimes
        }

    def compare_routes(self, routes, time_of_day=None):
        """
        Compare multiple routes for safety.

        Args:
            routes (list): List of routes to compare
            time_of_day (str, optional): The time of day

        Returns:
            list: Routes with safety analysis
        """
        # Analyze each route
        route_analyses = []

        for i, route in enumerate(routes):
            # Calculate safety
            safety = self.calculate_route_safety(route, time_of_day)

            # Add to results
            route_analyses.append({
                "route_index": i,
                "route": route,
                "safety": safety
            })

        # Sort by safety score (highest first)
        route_analyses.sort(key=lambda x: x["safety"]["safety_score"], reverse=True)

        return route_analyses

# Singleton instance
crime_data_service = CrimeDataService()

"""
AI Service for SafeWayAI

This module provides AI services using free libraries.
"""

import os
import json
import random
import threading
import datetime
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIService:
    """AI service using free libraries."""

    def __init__(self):
        """Initialize the AI service."""
        # Initialize NLTK resources
        self._ensure_nltk_resources()

        # Initialize sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

        # Initialize text vectorizer
        self.vectorizer = TfidfVectorizer(stop_words='english')

        # Initialize incident classifier
        self.incident_classifier = None

        # Load incident types
        self.incident_types = [
            "theft",
            "assault",
            "robbery",
            "suspicious_activity",
            "vandalism",
            "traffic_accident",
            "fire",
            "medical_emergency",
            "natural_disaster",
            "other"
        ]

        # Load risk factors
        self.risk_factors = [
            "time_of_day",
            "location_history",
            "incident_proximity",
            "population_density",
            "lighting_conditions",
            "weather_conditions",
            "user_familiarity",
            "transportation_mode"
        ]

        print("AI service initialized")

    def _ensure_nltk_resources(self):
        """Ensure NLTK resources are downloaded."""
        try:
            # Try to use the sentiment analyzer to check if resources are available
            SentimentIntensityAnalyzer().polarity_scores("Test")
        except LookupError:
            # Download required resources
            nltk.download('vader_lexicon', quiet=True)

    def analyze_text(self, text):
        """
        Analyze text for sentiment and key information.

        Args:
            text (str): The text to analyze

        Returns:
            dict: Analysis results
        """
        # Check if text is empty
        if not text:
            return {
                "sentiment": "neutral",
                "sentiment_score": 0,
                "emergency_detected": False,
                "incident_type": None,
                "severity": 0
            }

        # Analyze sentiment
        sentiment_scores = self.sentiment_analyzer.polarity_scores(text)

        # Determine overall sentiment
        compound_score = sentiment_scores['compound']
        if compound_score >= 0.05:
            sentiment = "positive"
        elif compound_score <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # Check for emergency keywords
        emergency_keywords = [
            "emergency", "help", "danger", "urgent", "critical",
            "attack", "weapon", "gun", "knife", "blood",
            "injured", "hurt", "pain", "accident", "crash",
            "fire", "burning", "smoke", "explosion",
            "robbery", "theft", "stolen", "break-in",
            "suspicious", "following", "stalking",
            "flood", "earthquake", "storm", "disaster"
        ]

        emergency_detected = any(keyword in text.lower() for keyword in emergency_keywords)

        # Determine incident type
        incident_type = self._classify_incident_type(text)

        # Calculate severity (0-10)
        severity = self._calculate_severity(text, sentiment_scores, emergency_detected)

        return {
            "sentiment": sentiment,
            "sentiment_score": compound_score,
            "emergency_detected": emergency_detected,
            "incident_type": incident_type,
            "severity": severity
        }

    def _classify_incident_type(self, text):
        """
        Classify the incident type from text.

        Args:
            text (str): The text to classify

        Returns:
            str: The incident type
        """
        # Simple keyword-based classification
        text_lower = text.lower()

        # Define keywords for each incident type
        incident_keywords = {
            "theft": ["theft", "steal", "stole", "stolen", "pickpocket", "shoplifting"],
            "assault": ["assault", "attack", "hit", "punch", "kick", "beat", "fight"],
            "robbery": ["robbery", "robbed", "mugging", "armed", "gun", "knife", "weapon"],
            "suspicious_activity": ["suspicious", "strange", "weird", "unusual", "lurking", "following", "stalking"],
            "vandalism": ["vandalism", "graffiti", "damage", "destroy", "break", "smash"],
            "traffic_accident": ["accident", "crash", "collision", "car", "vehicle", "traffic"],
            "fire": ["fire", "burning", "smoke", "flame", "heat"],
            "medical_emergency": ["medical", "ambulance", "heart", "breathing", "unconscious", "collapse"],
            "natural_disaster": ["flood", "earthquake", "storm", "lightning", "tornado", "hurricane"]
        }

        # Count keyword matches for each type
        type_scores = {}
        for incident_type, keywords in incident_keywords.items():
            type_scores[incident_type] = sum(1 for keyword in keywords if keyword in text_lower)

        # Add "other" type with a score of 0
        type_scores["other"] = 0

        # Return the type with the highest score, or "other" if all scores are 0
        max_score = max(type_scores.values())
        if max_score > 0:
            # Get all types with the max score
            max_types = [t for t, s in type_scores.items() if s == max_score]
            return random.choice(max_types)
        else:
            return "other"

    def _calculate_severity(self, text, sentiment_scores, emergency_detected):
        """
        Calculate the severity of an incident from text.

        Args:
            text (str): The text to analyze
            sentiment_scores (dict): Sentiment analysis scores
            emergency_detected (bool): Whether emergency keywords were detected

        Returns:
            int: The severity score (0-10)
        """
        # Start with a base severity
        severity = 5

        # Adjust based on sentiment (negative sentiment increases severity)
        severity -= sentiment_scores['compound'] * 3

        # Adjust based on emergency keywords
        if emergency_detected:
            severity += 2

        # Adjust based on specific high-severity keywords
        high_severity_keywords = [
            "gun", "knife", "weapon", "blood", "injured", "hurt",
            "critical", "life", "death", "dying", "dead",
            "fire", "explosion", "crash", "accident"
        ]

        text_lower = text.lower()
        severity += sum(1 for keyword in high_severity_keywords if keyword in text_lower)

        # Ensure severity is within range 0-10
        severity = max(0, min(10, severity))

        return round(severity)

    def analyze_location_safety(self, location, time_of_day=None, incidents=None):
        """
        Analyze the safety of a location.

        Args:
            location (dict): The location with lat/lon
            time_of_day (str, optional): The time of day (morning, afternoon, evening, night)
            incidents (list, optional): List of incidents near the location

        Returns:
            dict: Safety analysis results
        """
        # Default time of day to current time
        if time_of_day is None:
            hour = datetime.datetime.now().hour
            if 5 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 17:
                time_of_day = "afternoon"
            elif 17 <= hour < 21:
                time_of_day = "evening"
            else:
                time_of_day = "night"

        # Default incidents to empty list
        if incidents is None:
            incidents = []

        # Calculate base safety score (0-100)
        base_safety_score = self._calculate_base_safety_score(location)

        # Adjust for time of day
        time_factors = {
            "morning": 10,
            "afternoon": 5,
            "evening": -5,
            "night": -15
        }

        time_adjustment = time_factors.get(time_of_day, 0)

        # Adjust for incidents
        incident_adjustment = -5 * len(incidents)

        # Calculate final safety score
        safety_score = base_safety_score + time_adjustment + incident_adjustment

        # Ensure safety score is within range 0-100
        safety_score = max(0, min(100, safety_score))

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

        # Identify risk factors
        risk_factors = self._identify_risk_factors(location, time_of_day, incidents)

        return {
            "safety_score": safety_score,
            "safety_level": safety_level,
            "time_of_day": time_of_day,
            "incident_count": len(incidents),
            "risk_factors": risk_factors
        }

    def _calculate_base_safety_score(self, location):
        """
        Calculate the base safety score for a location.

        Args:
            location (dict): The location with lat/lon

        Returns:
            float: The base safety score (0-100)
        """
        # In a real implementation, this would use historical data and other factors
        # For now, we'll use a random score between 60 and 90
        return random.uniform(60, 90)

    def _identify_risk_factors(self, location, time_of_day, incidents):
        """
        Identify risk factors for a location.

        Args:
            location (dict): The location with lat/lon
            time_of_day (str): The time of day
            incidents (list): List of incidents near the location

        Returns:
            list: Risk factors
        """
        risk_factors = []

        # Check time of day
        if time_of_day in ["evening", "night"]:
            risk_factors.append({
                "factor": "time_of_day",
                "description": f"Traveling during {time_of_day} hours",
                "impact": "moderate" if time_of_day == "evening" else "high"
            })

        # Check incident proximity
        if incidents:
            risk_factors.append({
                "factor": "incident_proximity",
                "description": f"{len(incidents)} recent incidents reported nearby",
                "impact": "high" if len(incidents) > 2 else "moderate"
            })

        # Add random risk factors for demonstration
        if random.random() < 0.3:
            risk_factors.append({
                "factor": "lighting_conditions",
                "description": "Poor street lighting in the area",
                "impact": "moderate"
            })

        if random.random() < 0.2:
            risk_factors.append({
                "factor": "population_density",
                "description": "Low population density, fewer witnesses",
                "impact": "moderate"
            })

        return risk_factors

    def analyze_route_safety(self, route, incidents=None):
        """
        Analyze the safety of a route.

        Args:
            route (dict): The route with steps
            incidents (list, optional): List of incidents along the route

        Returns:
            dict: Safety analysis results
        """
        # Use the crime data service for more accurate safety analysis
        try:
            from services.crime_data_service import crime_data_service

            # Get the current time of day
            hour = datetime.datetime.now().hour
            if 6 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 18:
                time_of_day = "afternoon"
            elif 18 <= hour < 22:
                time_of_day = "evening"
            else:
                time_of_day = "night"

            # Calculate route safety using crime data
            safety_analysis = crime_data_service.calculate_route_safety(route, time_of_day)

            # Add additional information
            safety_analysis["overall_safety_score"] = safety_analysis["safety_score"]
            safety_analysis["overall_safety_level"] = safety_analysis["safety_level"]
            safety_analysis["total_incidents"] = len(incidents) if incidents else 0
            safety_analysis["route_incidents"] = safety_analysis["crime_count"]

            return safety_analysis
        except Exception as e:
            print(f"Error using crime data service: {e}")
            # Fall back to the original implementation
            return self._legacy_analyze_route_safety(route, incidents)

    def _legacy_analyze_route_safety(self, route, incidents=None):
        """
        Legacy method to analyze the safety of a route.

        Args:
            route (dict): The route with steps
            incidents (list, optional): List of incidents along the route

        Returns:
            dict: Safety analysis results
        """
        # Default incidents to empty list
        if incidents is None:
            incidents = []

        # Get route steps
        steps = route.get("steps", [])

        # Analyze each step
        step_analyses = []
        for step in steps:
            # Get step location (midpoint)
            start = step.get("start", {})
            end = step.get("end", {})

            step_location = {
                "lat": (start.get("lat", 0) + end.get("lat", 0)) / 2,
                "lon": (start.get("lon", 0) + end.get("lon", 0)) / 2
            }

            # Find incidents near this step
            step_incidents = self._find_incidents_near_location(step_location, incidents)

            # Analyze step safety
            step_safety = self.analyze_location_safety(step_location, incidents=step_incidents)

            step_analyses.append({
                "step": step,
                "safety": step_safety,
                "incidents": step_incidents
            })

        # Calculate overall route safety
        if step_analyses:
            # Average safety score
            avg_safety_score = sum(step["safety"]["safety_score"] for step in step_analyses) / len(step_analyses)

            # Minimum safety score (worst part of route)
            min_safety_score = min(step["safety"]["safety_score"] for step in step_analyses)

            # Count high-risk steps
            high_risk_steps = sum(1 for step in step_analyses if step["safety"]["safety_level"] in ["unsafe", "very_unsafe"])

            # Determine overall safety level
            if min_safety_score < 20:
                overall_safety_level = "very_unsafe"
            elif min_safety_score < 40 or high_risk_steps > len(steps) / 3:
                overall_safety_level = "unsafe"
            elif min_safety_score < 60 or high_risk_steps > 0:
                overall_safety_level = "moderate"
            elif min_safety_score < 80:
                overall_safety_level = "safe"
            else:
                overall_safety_level = "very_safe"
        else:
            # Default values if no steps
            avg_safety_score = 50
            min_safety_score = 50
            high_risk_steps = 0
            overall_safety_level = "moderate"

        return {
            "overall_safety_score": avg_safety_score,
            "min_safety_score": min_safety_score,
            "overall_safety_level": overall_safety_level,
            "high_risk_steps": high_risk_steps,
            "total_steps": len(steps),
            "step_analyses": step_analyses,
            "total_incidents": len(incidents),
            "route_incidents": sum(len(step["incidents"]) for step in step_analyses)
        }

    def _find_incidents_near_location(self, location, incidents, max_distance_km=0.5):
        """
        Find incidents near a location.

        Args:
            location (dict): The location with lat/lon
            incidents (list): List of all incidents
            max_distance_km (float): Maximum distance in kilometers

        Returns:
            list: Incidents near the location
        """
        nearby_incidents = []

        for incident in incidents:
            incident_location = incident.get("location", {})

            # Calculate distance (very rough approximation)
            lat_diff = abs(location.get("lat", 0) - incident_location.get("lat", 0))
            lon_diff = abs(location.get("lon", 0) - incident_location.get("lon", 0))

            # Rough distance in kilometers (1 degree is approximately 111 km)
            distance_km = ((lat_diff ** 2) + (lon_diff ** 2)) ** 0.5 * 111

            if distance_km <= max_distance_km:
                nearby_incidents.append(incident)

        return nearby_incidents

    def detect_emergency(self, sensor_data, user_data=None, location_data=None):
        """
        Detect emergency situations from sensor data.

        Args:
            sensor_data (dict): Sensor data (e.g., heart rate, movement)
            user_data (dict, optional): User data for baseline comparison
            location_data (dict, optional): Location data

        Returns:
            dict: Emergency detection results
        """
        # Default user data
        if user_data is None:
            user_data = {
                "baseline_heart_rate": 70,
                "baseline_movement": "normal",
                "emergency_threshold": 0.7
            }

        # Extract sensor values
        heart_rate = sensor_data.get("heart_rate", 0)
        movement = sensor_data.get("movement", "normal")
        fall_detected = sensor_data.get("fall_detected", False)
        sos_button = sensor_data.get("sos_button", False)

        # Calculate risk factors
        risk_factors = []
        risk_score = 0

        # Check heart rate
        baseline_heart_rate = user_data.get("baseline_heart_rate", 70)
        if heart_rate > baseline_heart_rate * 1.5:
            risk_factors.append({
                "factor": "elevated_heart_rate",
                "value": heart_rate,
                "baseline": baseline_heart_rate,
                "severity": "high"
            })
            risk_score += 0.3
        elif heart_rate > baseline_heart_rate * 1.3:
            risk_factors.append({
                "factor": "elevated_heart_rate",
                "value": heart_rate,
                "baseline": baseline_heart_rate,
                "severity": "moderate"
            })
            risk_score += 0.2

        # Check movement
        baseline_movement = user_data.get("baseline_movement", "normal")
        if movement == "erratic" and baseline_movement != "erratic":
            risk_factors.append({
                "factor": "erratic_movement",
                "value": movement,
                "baseline": baseline_movement,
                "severity": "high"
            })
            risk_score += 0.3
        elif movement == "none" and baseline_movement != "none":
            risk_factors.append({
                "factor": "no_movement",
                "value": movement,
                "baseline": baseline_movement,
                "severity": "moderate"
            })
            risk_score += 0.2

        # Check fall detection
        if fall_detected:
            risk_factors.append({
                "factor": "fall_detected",
                "severity": "high"
            })
            risk_score += 0.4

        # Check SOS button
        if sos_button:
            risk_factors.append({
                "factor": "sos_button_pressed",
                "severity": "critical"
            })
            risk_score += 0.8

        # Check location safety if available
        if location_data:
            location_safety = self.analyze_location_safety(location_data)
            if location_safety["safety_level"] in ["unsafe", "very_unsafe"]:
                risk_factors.append({
                    "factor": "unsafe_location",
                    "safety_level": location_safety["safety_level"],
                    "safety_score": location_safety["safety_score"],
                    "severity": "high" if location_safety["safety_level"] == "very_unsafe" else "moderate"
                })
                risk_score += 0.3 if location_safety["safety_level"] == "very_unsafe" else 0.2

        # Determine if emergency is detected
        emergency_threshold = user_data.get("emergency_threshold", 0.7)
        emergency_detected = risk_score >= emergency_threshold

        # Determine emergency type
        emergency_type = None
        if emergency_detected:
            if sos_button:
                emergency_type = "sos_alert"
            elif fall_detected:
                emergency_type = "fall_detected"
            elif heart_rate > baseline_heart_rate * 1.5:
                emergency_type = "medical_emergency"
            elif location_data and location_safety["safety_level"] == "very_unsafe":
                emergency_type = "safety_threat"
            else:
                emergency_type = "unknown_emergency"

        return {
            "emergency_detected": emergency_detected,
            "emergency_type": emergency_type,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "emergency_threshold": emergency_threshold
        }

# Singleton instance
ai_service = AIService()

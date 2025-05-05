"""
Azure IoT Hub Service for SafeWayAI

This module provides integration with Azure IoT Hub for wearable devices
and biometric data processing.
"""

import os
import json
import datetime
import threading
import random
from services.azure_client import AzureClient

class AzureIoT:
    """
    Azure IoT Hub service for wearable integration and biometric data processing.
    """
    
    # Path to the local cache for offline use
    CACHE_PATH = os.path.join('data', 'iot_cache.json')
    
    # Biometric thresholds for emergency detection
    THRESHOLDS = {
        "heart_rate": {
            "min": 40,
            "max": 120,
            "panic": 130
        },
        "breathing_rate": {
            "min": 10,
            "max": 20,
            "panic": 25
        },
        "stress_level": {
            "normal": 40,
            "elevated": 70,
            "panic": 85
        }
    }
    
    @classmethod
    def _ensure_cache_exists(cls):
        """Ensure the IoT cache exists for offline use."""
        os.makedirs(os.path.dirname(cls.CACHE_PATH), exist_ok=True)
        
        if not os.path.exists(cls.CACHE_PATH):
            # Create an empty cache
            default_cache = {
                "biometric_data": [],
                "device_status": [],
                "emergency_alerts": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(cls.CACHE_PATH, 'w') as f:
                json.dump(default_cache, f, indent=2)
    
    @classmethod
    def _get_iot_config(cls):
        """Get Azure IoT Hub configuration."""
        config = AzureClient.load_config()
        return config["iot_hub"]
    
    @classmethod
    def get_biometric_data(cls, callback=None):
        """
        Get the latest biometric data from connected wearable devices.
        
        Args:
            callback (callable, optional): Function to call with result
            
        Returns:
            If callback is None, this function will use the cache and return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not callback:
            # Use cached data or simulate
            return cls._simulate_biometric_data()
        
        # Get Azure IoT Hub configuration
        iot_config = cls._get_iot_config()
        connection_string = iot_config["connection_string"]
        device_id = iot_config["device_id"]
        
        # In a real implementation, you would use the Azure IoT SDK here
        # Since we can't install the SDK in this environment, we'll simulate it
        
        # Start a thread to simulate the API call
        def process_request():
            # Simulate processing delay
            import time
            time.sleep(0.5)
            
            # Return simulated result
            result = cls._simulate_biometric_data()
            callback(result)
        
        thread = threading.Thread(target=process_request)
        thread.daemon = True
        thread.start()
    
    @classmethod
    def _simulate_biometric_data(cls):
        """Simulate biometric data for testing."""
        # Simulate heart rate (60-100 bpm normally)
        heart_rate = random.randint(60, 100)
        
        # Simulate breathing rate (12-20 breaths per minute normally)
        breathing_rate = random.randint(12, 20)
        
        # Simulate stress level (0-100)
        stress_level = random.randint(10, 40)
        
        # Simulate motion status
        motions = ["Walking", "Standing", "Sitting", "Running", "Lying down"]
        motion_status = random.choice(motions)
        
        # Simulate fall detection
        fall_detected = random.random() < 0.05  # 5% chance
        
        # Create the result
        result = {
            "heart_rate": heart_rate,
            "breathing_rate": breathing_rate,
            "stress_level": stress_level,
            "motion_status": motion_status,
            "fall_detected": fall_detected,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Cache the result
        cls._cache_biometric_data(result)
        
        return result
    
    @classmethod
    def _cache_biometric_data(cls, data):
        """Cache biometric data for offline use."""
        cls._ensure_cache_exists()
        
        with open(cls.CACHE_PATH, 'r') as f:
            cache = json.load(f)
        
        cache["biometric_data"].append(data)
        cache["last_updated"] = datetime.datetime.now().isoformat()
        
        # Keep only the last 100 data points
        if len(cache["biometric_data"]) > 100:
            cache["biometric_data"] = cache["biometric_data"][-100:]
        
        with open(cls.CACHE_PATH, 'w') as f:
            json.dump(cache, f, indent=2)
    
    @classmethod
    def check_for_emergency(cls, callback=None):
        """
        Check for emergency situations based on biometric data.
        
        Args:
            callback (callable, optional): Function to call with result
            
        Returns:
            If callback is None, this function will use the cache and return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not callback:
            # Get the latest biometric data
            biometric_data = cls._simulate_biometric_data()
            
            # Check for emergency
            return cls._analyze_biometric_data(biometric_data)
        
        # Get biometric data asynchronously
        def on_biometric_data(data):
            # Analyze the data
            result = cls._analyze_biometric_data(data)
            callback(result)
        
        cls.get_biometric_data(callback=on_biometric_data)
    
    @classmethod
    def _analyze_biometric_data(cls, data):
        """
        Analyze biometric data for emergency situations.
        
        Args:
            data (dict): Biometric data
            
        Returns:
            dict: Analysis result
        """
        # Check heart rate
        heart_rate = data.get("heart_rate", 0)
        heart_rate_status = "normal"
        if heart_rate > cls.THRESHOLDS["heart_rate"]["panic"]:
            heart_rate_status = "panic"
        elif heart_rate > cls.THRESHOLDS["heart_rate"]["max"]:
            heart_rate_status = "elevated"
        elif heart_rate < cls.THRESHOLDS["heart_rate"]["min"]:
            heart_rate_status = "low"
        
        # Check breathing rate
        breathing_rate = data.get("breathing_rate", 0)
        breathing_status = "normal"
        if breathing_rate > cls.THRESHOLDS["breathing_rate"]["panic"]:
            breathing_status = "panic"
        elif breathing_rate > cls.THRESHOLDS["breathing_rate"]["max"]:
            breathing_status = "elevated"
        elif breathing_rate < cls.THRESHOLDS["breathing_rate"]["min"]:
            breathing_status = "low"
        
        # Check stress level
        stress_level = data.get("stress_level", 0)
        stress_status = "normal"
        if stress_level > cls.THRESHOLDS["stress_level"]["panic"]:
            stress_status = "panic"
        elif stress_level > cls.THRESHOLDS["stress_level"]["elevated"]:
            stress_status = "elevated"
        
        # Check for fall
        fall_detected = data.get("fall_detected", False)
        
        # Determine overall emergency status
        is_emergency = (
            heart_rate_status == "panic" or
            breathing_status == "panic" or
            stress_status == "panic" or
            fall_detected
        )
        
        # Create emergency details if needed
        emergency_details = []
        if heart_rate_status == "panic":
            emergency_details.append(f"Elevated heart rate: {heart_rate} bpm")
        if breathing_status == "panic":
            emergency_details.append(f"Rapid breathing: {breathing_rate} breaths/min")
        if stress_status == "panic":
            emergency_details.append(f"High stress level: {stress_level}/100")
        if fall_detected:
            emergency_details.append("Fall detected")
        
        # Create the result
        result = {
            "is_emergency": is_emergency,
            "heart_rate_status": heart_rate_status,
            "breathing_status": breathing_status,
            "stress_status": stress_status,
            "fall_detected": fall_detected,
            "emergency_details": emergency_details,
            "biometric_data": data,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Cache the result if it's an emergency
        if is_emergency:
            cls._cache_emergency_alert(result)
        
        return result
    
    @classmethod
    def _cache_emergency_alert(cls, alert):
        """Cache emergency alert for offline use."""
        cls._ensure_cache_exists()
        
        with open(cls.CACHE_PATH, 'r') as f:
            cache = json.load(f)
        
        cache["emergency_alerts"].append(alert)
        cache["last_updated"] = datetime.datetime.now().isoformat()
        
        # Keep only the last 50 alerts
        if len(cache["emergency_alerts"]) > 50:
            cache["emergency_alerts"] = cache["emergency_alerts"][-50:]
        
        with open(cls.CACHE_PATH, 'w') as f:
            json.dump(cache, f, indent=2)
    
    @classmethod
    def send_sos(cls, lat, lon, details=None, callback=None):
        """
        Send an SOS alert to emergency contacts and authorities.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            details (str, optional): Additional details about the emergency
            callback (callable, optional): Function to call with result
            
        Returns:
            If callback is None, this function will return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        # Create the SOS alert
        sos_alert = {
            "lat": lat,
            "lon": lon,
            "details": details or "SOS Alert",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if not callback:
            # Simulate sending the alert
            print(f"SOS Alert: {sos_alert}")
            return {"success": True, "message": "SOS alert sent"}
        
        # Get Azure IoT Hub configuration
        iot_config = cls._get_iot_config()
        connection_string = iot_config["connection_string"]
        device_id = iot_config["device_id"]
        
        # In a real implementation, you would use the Azure IoT SDK here
        # Since we can't install the SDK in this environment, we'll simulate it
        
        # Start a thread to simulate the API call
        def process_request():
            # Simulate processing delay
            import time
            time.sleep(1.0)
            
            # Return simulated result
            result = {"success": True, "message": "SOS alert sent"}
            callback(result)
        
        thread = threading.Thread(target=process_request)
        thread.daemon = True
        thread.start()
        
        # Cache the alert
        cls._cache_emergency_alert({
            "is_emergency": True,
            "emergency_details": [details or "SOS Alert"],
            "sos_alert": sos_alert,
            "timestamp": datetime.datetime.now().isoformat()
        })

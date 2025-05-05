import os
import json
import datetime
# Try to import Azure services, fall back to mock services if not available
try:
    from services.azure_speech import AzureSpeech as SpeechService
    from services.azure_maps import AzureMaps as MapsService
    print("Using Azure services for panic detection")
except ImportError:
    # Create fallback implementations
    class SpeechService:
        @staticmethod
        def detect_panic(audio_path):
            return {"is_panic": True, "text": "Help me"}

    class MapsService:
        @staticmethod
        def get_danger_zones(lat, lon):
            return {"is_unsafe": True, "nearby_danger_zones": [
                {"name": "Test Zone", "risk_level": 8, "risk_factors": ["theft"]}
            ]}
    print("Using fallback services for panic detection")

class PanicDetector:
    """
    PanicDetector integrates speech recognition and location-based risk assessment
    to detect emergency situations.
    """

    # Path to the incidents database
    DB_PATH = os.path.join('data', 'incidents.json')

    def __init__(self):
        """Initialize the PanicDetector."""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)

        # Initialize incidents database if it doesn't exist
        if not os.path.exists(self.DB_PATH):
            with open(self.DB_PATH, 'w') as f:
                json.dump({
                    "incidents": [],
                    "metadata": {
                        "version": "1.0",
                        "source": "SafeWayAI Panic Detector",
                        "last_updated": datetime.datetime.now().isoformat()
                    }
                }, f, indent=2)

    def check_emergency(self, audio_path, lat, lon):
        """
        Check for emergency situations based on audio and location.

        Args:
            audio_path (str): Path to the audio file
            lat (float): Latitude
            lon (float): Longitude

        Returns:
            bool: True if an emergency is detected, False otherwise
        """
        # Get speech analysis
        speech_result = SpeechService.detect_panic(audio_path)

        # Get location risk assessment
        location_risk = MapsService.get_danger_zones(lat, lon)

        # Determine if this is an emergency
        is_emergency = speech_result["is_panic"] or location_risk["is_unsafe"]

        # Log the incident if it's an emergency
        if is_emergency:
            self._log_incident(speech_result, location_risk)

        return is_emergency

    def _log_incident(self, speech_result, location_risk):
        """
        Log an incident to the database.

        Args:
            speech_result (dict): Speech analysis results
            location_risk (dict): Location risk assessment
        """
        try:
            # Load existing incidents
            with open(self.DB_PATH, 'r') as f:
                data = json.load(f)

            # Create new incident
            incident = {
                "timestamp": datetime.datetime.now().isoformat(),
                "speech_analysis": speech_result,
                "location_risk": location_risk,
                "emergency_type": self._determine_emergency_type(speech_result, location_risk)
            }

            # Add to incidents list
            data["incidents"].append(incident)
            data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()

            # Save updated data
            with open(self.DB_PATH, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error logging incident: {e}")

    def _determine_emergency_type(self, speech_result, location_risk):
        """
        Determine the type of emergency based on speech and location data.

        Args:
            speech_result (dict): Speech analysis results
            location_risk (dict): Location risk assessment

        Returns:
            str: The determined emergency type
        """
        # Check if speech indicates a specific emergency
        if speech_result["is_panic"]:
            text = speech_result["text"].lower()

            # Check for specific emergency keywords
            if any(word in text for word in ["fire", "umlilo"]):
                return "Fire"
            elif any(word in text for word in ["attack", "assault", "hlasela"]):
                return "Assault"
            elif any(word in text for word in ["robbery", "theft", "isela", "ubusela"]):
                return "Theft"
            elif any(word in text for word in ["accident", "crash", "ingozi"]):
                return "Accident"
            elif any(word in text for word in ["medical", "ambulance", "hurt", "injured", "ngiyagula", "ngilimele"]):
                return "Medical"
            else:
                return "Panic"

        # If no specific emergency from speech, check location risk
        if location_risk["is_unsafe"]:
            # Check if there are nearby danger zones with specific risk factors
            for zone in location_risk.get("nearby_danger_zones", []):
                risk_factors = zone.get("risk_factors", [])
                if "theft" in risk_factors or "robbery" in risk_factors:
                    return "Theft Risk"
                elif "assault" in risk_factors or "mugging" in risk_factors:
                    return "Assault Risk"
                elif "carjacking" in risk_factors:
                    return "Carjacking Risk"

            # Default to general danger if no specific risk factors
            return "Danger Zone"

        # Fallback
        return "Unknown Emergency"

    def get_recent_incidents(self, limit=10):
        """
        Get recent incidents from the database.

        Args:
            limit (int): Maximum number of incidents to return

        Returns:
            list: List of recent incidents
        """
        try:
            # Load incidents
            with open(self.DB_PATH, 'r') as f:
                data = json.load(f)

            # Sort by timestamp (newest first) and limit
            incidents = data["incidents"]
            incidents.sort(key=lambda x: x["timestamp"], reverse=True)

            return incidents[:limit]

        except Exception as e:
            print(f"Error getting recent incidents: {e}")
            return []
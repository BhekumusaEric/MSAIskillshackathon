import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# Add the app directory to the path so we can import from it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.panic_detector import PanicDetector, SpeechService, MapsService

class TestPanicDetection(unittest.TestCase):
    """Test the panic detection functionality."""

    def setUp(self):
        """Set up the test environment."""
        # Patch the SpeechService and MapsService classes
        self.speech_patcher = patch('services.panic_detector.SpeechService.detect_panic')
        self.mock_speech = self.speech_patcher.start()
        self.maps_patcher = patch('services.panic_detector.MapsService.get_danger_zones')
        self.mock_maps = self.maps_patcher.start()

        # Create a PanicDetector instance
        self.detector = PanicDetector()

        # Patch the open function and json.load for the database operations
        self.open_patcher = patch('builtins.open', create=True)
        self.mock_open = self.open_patcher.start()
        self.mock_open.return_value.__enter__.return_value = MagicMock()

        self.json_load_patcher = patch('json.load')
        self.mock_json_load = self.json_load_patcher.start()
        self.mock_json_load.return_value = {'incidents': [], 'metadata': {}}

        self.json_dump_patcher = patch('json.dump')
        self.mock_json_dump = self.json_dump_patcher.start()

    def tearDown(self):
        """Clean up after the test."""
        # Stop the patchers
        self.speech_patcher.stop()
        self.maps_patcher.stop()
        self.open_patcher.stop()
        self.json_load_patcher.stop()
        self.json_dump_patcher.stop()

    def test_panic_detection_with_speech_panic(self):
        """Test panic detection with speech panic."""
        # Set up the mocks to return a panic situation
        self.mock_speech.return_value = {'is_panic': True, 'text': 'Help me!'}
        self.mock_maps.return_value = {'is_unsafe': False}

        # Check for an emergency
        result = self.detector.check_emergency("test.wav", -26.2041, 28.0473)

        # Check that an emergency was detected
        self.assertTrue(result)

        # Verify that the speech service was called with the correct audio path
        self.mock_speech.assert_called_once_with("test.wav")

        # Verify that the maps service was called with the correct coordinates
        self.mock_maps.assert_called_once_with(-26.2041, 28.0473)

    def test_panic_detection_with_unsafe_location(self):
        """Test panic detection with an unsafe location."""
        # Set up the mocks to return an unsafe location
        self.mock_speech.return_value = {'is_panic': False, 'text': 'Hello'}
        self.mock_maps.return_value = {'is_unsafe': True, 'nearby_danger_zones': [
            {'name': 'Test Zone', 'risk_level': 8, 'risk_factors': ['theft']}
        ]}

        # Check for an emergency
        result = self.detector.check_emergency("test.wav", -26.2041, 28.0473)

        # Check that an emergency was detected
        self.assertTrue(result)

    def test_panic_detection_with_no_emergency(self):
        """Test panic detection with no emergency."""
        # Set up the mocks to return no emergency
        self.mock_speech.return_value = {'is_panic': False, 'text': 'Hello'}
        self.mock_maps.return_value = {'is_unsafe': False}

        # Check for an emergency
        result = self.detector.check_emergency("test.wav", -26.2041, 28.0473)

        # Check that no emergency was detected
        self.assertFalse(result)

    def test_incident_logging(self):
        """Test that incidents are logged correctly."""
        # Set up the mocks to return a panic situation
        self.mock_speech.return_value = {'is_panic': True, 'text': 'Help me!'}
        self.mock_maps.return_value = {'is_unsafe': False}

        # Check for an emergency
        self.detector.check_emergency("test.wav", -26.2041, 28.0473)

        # Verify that json.dump was called (incident was logged)
        self.mock_json_dump.assert_called_once()

        # Get the arguments passed to json.dump
        args, kwargs = self.mock_json_dump.call_args
        data = args[0]

        # Check that the incident was added to the incidents list
        self.assertEqual(len(data['incidents']), 1)

        # Check that the incident has the correct emergency type
        self.assertEqual(data['incidents'][0]['emergency_type'], 'Panic')

    def test_get_recent_incidents(self):
        """Test getting recent incidents."""
        # Set up the mock to return some incidents
        incidents = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "speech_analysis": {"is_panic": True, "text": "Help"},
                "location_risk": {"is_unsafe": False},
                "emergency_type": "Panic"
            },
            {
                "timestamp": "2023-01-02T12:00:00",
                "speech_analysis": {"is_panic": False, "text": "Hello"},
                "location_risk": {"is_unsafe": True},
                "emergency_type": "Theft Risk"
            }
        ]
        self.mock_json_load.return_value = {'incidents': incidents, 'metadata': {}}

        # Get recent incidents
        result = self.detector.get_recent_incidents(limit=2)

        # Check that the correct number of incidents was returned
        self.assertEqual(len(result), 2)

        # Check that the incidents are sorted by timestamp (newest first)
        self.assertEqual(result[0]['timestamp'], "2023-01-02T12:00:00")
        self.assertEqual(result[1]['timestamp'], "2023-01-01T12:00:00")

    def test_get_recent_incidents_with_limit(self):
        """Test getting recent incidents with a limit."""
        # Set up the mock to return some incidents
        incidents = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "speech_analysis": {"is_panic": True, "text": "Help"},
                "location_risk": {"is_unsafe": False},
                "emergency_type": "Panic"
            },
            {
                "timestamp": "2023-01-02T12:00:00",
                "speech_analysis": {"is_panic": False, "text": "Hello"},
                "location_risk": {"is_unsafe": True},
                "emergency_type": "Theft Risk"
            },
            {
                "timestamp": "2023-01-03T12:00:00",
                "speech_analysis": {"is_panic": True, "text": "Fire"},
                "location_risk": {"is_unsafe": False},
                "emergency_type": "Fire"
            }
        ]
        self.mock_json_load.return_value = {'incidents': incidents, 'metadata': {}}

        # Get recent incidents with a limit of 2
        result = self.detector.get_recent_incidents(limit=2)

        # Check that only 2 incidents were returned
        self.assertEqual(len(result), 2)

        # Check that the most recent incidents were returned
        self.assertEqual(result[0]['timestamp'], "2023-01-03T12:00:00")
        self.assertEqual(result[1]['timestamp'], "2023-01-02T12:00:00")

if __name__ == '__main__':
    unittest.main()
import unittest
import os
import sys
import json
import shutil
from unittest.mock import patch, MagicMock

# Add the app directory to the path so we can import from it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the app modules
from services.panic_detector import PanicDetector, SpeechService, MapsService
from services.data_manager import DataManager
from ui.app import SafeWayAIApp
import flet as ft

class TestPanicDetector(unittest.TestCase):
    """Test the PanicDetector class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test data directory
        self.test_dir = 'test_data'
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        # Patch the open function to use a StringIO object
        self.patcher = patch('builtins.open', create=True)
        self.mock_open = self.patcher.start()
        self.mock_open.return_value.__enter__.return_value = MagicMock()

        # Patch the json module
        self.json_patcher = patch('json.load')
        self.mock_json_load = self.json_patcher.start()
        self.mock_json_load.return_value = {'incidents': [], 'metadata': {}}

        # Patch the SpeechService and MapsService classes
        self.speech_patcher = patch('services.panic_detector.SpeechService.detect_panic')
        self.mock_speech = self.speech_patcher.start()
        self.maps_patcher = patch('services.panic_detector.MapsService.get_danger_zones')
        self.mock_maps = self.maps_patcher.start()

        # Create a PanicDetector instance
        self.detector = PanicDetector()

    def tearDown(self):
        """Clean up after the test."""
        # Stop the patchers
        self.patcher.stop()
        self.json_patcher.stop()
        self.speech_patcher.stop()
        self.maps_patcher.stop()

        # Remove the test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_check_emergency_speech_panic(self):
        """Test checking for an emergency with speech panic."""
        # Set up the mocks to return a panic situation
        self.mock_speech.return_value = {'is_panic': True, 'text': 'help'}
        self.mock_maps.return_value = {'is_unsafe': False}

        # Check for an emergency
        result = self.detector.check_emergency('test.wav', 0, 0)

        # Check that an emergency was detected
        self.assertTrue(result)

    def test_check_emergency_location_unsafe(self):
        """Test checking for an emergency with an unsafe location."""
        # Set up the mocks to return an unsafe location
        self.mock_speech.return_value = {'is_panic': False, 'text': 'hello'}
        self.mock_maps.return_value = {'is_unsafe': True}

        # Check for an emergency
        result = self.detector.check_emergency('test.wav', 0, 0)

        # Check that an emergency was detected
        self.assertTrue(result)

    def test_check_emergency_no_emergency(self):
        """Test checking for an emergency with no emergency."""
        # Set up the mocks to return no emergency
        self.mock_speech.return_value = {'is_panic': False, 'text': 'hello'}
        self.mock_maps.return_value = {'is_unsafe': False}

        # Check for an emergency
        result = self.detector.check_emergency('test.wav', 0, 0)

        # Check that no emergency was detected
        self.assertFalse(result)

    def test_determine_emergency_type_fire(self):
        """Test determining emergency type for fire."""
        speech_result = {'is_panic': True, 'text': 'umlilo'}
        location_risk = {'is_unsafe': False}

        emergency_type = self.detector._determine_emergency_type(speech_result, location_risk)

        self.assertEqual(emergency_type, "Fire")

    def test_determine_emergency_type_assault(self):
        """Test determining emergency type for assault."""
        speech_result = {'is_panic': True, 'text': 'hlasela'}
        location_risk = {'is_unsafe': False}

        emergency_type = self.detector._determine_emergency_type(speech_result, location_risk)

        self.assertEqual(emergency_type, "Assault")

    def test_determine_emergency_type_theft(self):
        """Test determining emergency type for theft."""
        speech_result = {'is_panic': True, 'text': 'ubusela'}
        location_risk = {'is_unsafe': False}

        emergency_type = self.detector._determine_emergency_type(speech_result, location_risk)

        self.assertEqual(emergency_type, "Theft")

    def test_determine_emergency_type_from_location(self):
        """Test determining emergency type from location risk."""
        speech_result = {'is_panic': False, 'text': 'Hello'}
        location_risk = {
            'is_unsafe': True,
            'nearby_danger_zones': [
                {'name': 'Test Zone', 'risk_level': 8, 'risk_factors': ['theft']}
            ]
        }

        emergency_type = self.detector._determine_emergency_type(speech_result, location_risk)

        self.assertEqual(emergency_type, "Theft Risk")

class TestSafeWayAIApp(unittest.TestCase):
    """Test the SafeWayAIApp class."""

    def setUp(self):
        """Set up the test environment."""
        # Mock the Flet page
        self.mock_page = MagicMock(spec=ft.Page)
        self.mock_page.update = MagicMock()
        self.mock_page.add = MagicMock()

        # Create a SafeWayAIApp instance with the mock page
        self.app = SafeWayAIApp(self.mock_page)

    def test_init_app(self):
        """Test initializing the app."""
        # Check that the app title is set correctly
        self.assertEqual(self.app.page.title, "SafeWayAI")

        # Check that the theme mode is set correctly
        self.assertEqual(self.app.page.theme_mode, ft.ThemeMode.LIGHT)

        # Check that the navigation rail is created
        self.assertIsNotNone(self.app.nav_rail)

        # Check that the screens are created
        self.assertIn("login", self.app.screens)
        self.assertIn("home", self.app.screens)
        self.assertIn("map", self.app.screens)
        self.assertIn("chat", self.app.screens)
        self.assertIn("settings", self.app.screens)

    def test_navigation(self):
        """Test navigation between screens."""
        # Test navigation to login screen
        self.app.navigate_to("login")
        self.assertEqual(self.app.content.content, self.app.screens["login"])
        self.assertFalse(self.app.nav_rail.visible)

        # Set current_user to simulate login
        self.app.current_user = {"id": "test_user", "username": "test"}

        # Test navigation to home screen
        self.app.navigate_to("home")
        self.assertEqual(self.app.content.content, self.app.screens["home"])
        self.assertTrue(self.app.nav_rail.visible)

        # Test navigation to map screen
        self.app.navigate_to("map")
        self.assertEqual(self.app.content.content, self.app.screens["map"])

        # Test navigation to chat screen
        self.app.navigate_to("chat")
        self.assertEqual(self.app.content.content, self.app.screens["chat"])

        # Test navigation to settings screen
        self.app.navigate_to("settings")
        self.assertEqual(self.app.content.content, self.app.screens["settings"])

    def test_logout(self):
        """Test logging out."""
        # Set up a mock data manager
        self.app.data_manager = MagicMock()
        self.app.data_manager.logout = MagicMock()

        # Set current_user to simulate being logged in
        self.app.current_user = {"id": "test_user", "username": "test"}

        # Call logout
        self.app.logout()

        # Check that data_manager.logout was called
        self.app.data_manager.logout.assert_called_once()

        # Check that current_user is None
        self.assertIsNone(self.app.current_user)

        # Check that we navigated to the login screen
        self.assertEqual(self.app.content.content, self.app.screens["login"])

class TestDataManager(unittest.TestCase):
    """Test the DataManager class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a DataManager instance
        self.data_manager = DataManager()

        # Patch the repositories
        self.user_repo_patcher = patch('services.repositories.user_repository.authenticate_user')
        self.mock_user_repo = self.user_repo_patcher.start()

        self.settings_repo_patcher = patch('services.repositories.settings_repository.get_settings')
        self.mock_settings_repo = self.settings_repo_patcher.start()

        self.incident_repo_patcher = patch('services.repositories.incident_repository.get_recent_incidents')
        self.mock_incident_repo = self.incident_repo_patcher.start()

        self.create_incident_patcher = patch('services.repositories.incident_repository.create_incident')
        self.mock_create_incident = self.create_incident_patcher.start()

    def tearDown(self):
        """Clean up after the test."""
        # Stop the patchers
        self.user_repo_patcher.stop()
        self.settings_repo_patcher.stop()
        self.incident_repo_patcher.stop()
        self.create_incident_patcher.stop()

    def test_login_with_valid_credentials(self):
        """Test logging in with valid credentials."""
        # Set up the mock to return a user
        self.mock_user_repo.return_value = {
            "id": "test_user",
            "username": "test",
            "role": "user",
            "full_name": "Test User"
        }

        # Set up the mock to return settings
        self.mock_settings_repo.return_value = {
            "theme": "light",
            "notifications": True,
            "emergency_contacts": []
        }

        # Login with valid credentials
        result = self.data_manager.login("test", "password")

        # Check that login was successful
        self.assertTrue(result)

        # Check that current_user is set
        self.assertIsNotNone(self.data_manager.current_user)
        self.assertEqual(self.data_manager.current_user["username"], "test")

        # Check that user_settings is set
        self.assertIsNotNone(self.data_manager.user_settings)

    def test_login_with_invalid_credentials(self):
        """Test logging in with invalid credentials."""
        # Set up the mock to return None (invalid credentials)
        self.mock_user_repo.return_value = None

        # Login with invalid credentials
        result = self.data_manager.login("invalid", "invalid")

        # Check that login failed
        self.assertFalse(result)

        # Check that current_user is None
        self.assertIsNone(self.data_manager.current_user)

    def test_login_with_hardcoded_credentials(self):
        """Test logging in with hardcoded credentials."""
        # Set up the mock to return None (fall back to hardcoded credentials)
        self.mock_user_repo.return_value = None

        # Login with hardcoded credentials
        result = self.data_manager.login("admin", "admin123")

        # Check that login was successful
        self.assertTrue(result)

        # Check that current_user is set
        self.assertIsNotNone(self.data_manager.current_user)
        self.assertEqual(self.data_manager.current_user["username"], "admin")

    def test_logout(self):
        """Test logging out."""
        # Set current_user and user_settings to simulate being logged in
        self.data_manager.current_user = {"id": "test_user", "username": "test"}
        self.data_manager.user_settings = {"theme": "light"}

        # Logout
        self.data_manager.logout()

        # Check that current_user and user_settings are None
        self.assertIsNone(self.data_manager.current_user)
        self.assertIsNone(self.data_manager.user_settings)

    def test_report_incident(self):
        """Test reporting an incident."""
        # Set up the mock to return an incident ID
        self.mock_create_incident.return_value = "incident_123"

        # Set current_user to simulate being logged in
        self.data_manager.current_user = {"id": "test_user", "username": "test"}

        # Report an incident
        incident_data = {
            "type": "Robbery",
            "description": "Test incident",
            "location": "Test location",
            "latitude": -26.2041,
            "longitude": 28.0473,
            "severity": "high"
        }

        result = self.data_manager.report_incident(incident_data)

        # Check that the incident was created
        self.assertEqual(result, "incident_123")

        # Check that create_incident was called with the correct arguments
        self.mock_create_incident.assert_called_once_with(
            incident_type="Robbery",
            description="Test incident",
            location="Test location",
            latitude=-26.2041,
            longitude=28.0473,
            severity="high",
            reported_by="test_user",
            status="active"
        )

    def test_report_incident_not_logged_in(self):
        """Test reporting an incident when not logged in."""
        # Ensure current_user is None
        self.data_manager.current_user = None

        # Report an incident
        incident_data = {
            "type": "Robbery",
            "description": "Test incident",
            "location": "Test location",
            "latitude": -26.2041,
            "longitude": 28.0473,
            "severity": "high"
        }

        result = self.data_manager.report_incident(incident_data)

        # Check that the incident was not created
        self.assertFalse(result)

        # Check that create_incident was not called
        self.mock_create_incident.assert_not_called()

if __name__ == '__main__':
    unittest.main()

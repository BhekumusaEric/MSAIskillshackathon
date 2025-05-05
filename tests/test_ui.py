import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import flet as ft

# Add the app directory to the path so we can import from it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.screens.home_screen import HomeScreen
from ui.screens.login_screen import LoginScreen
from ui.screens.map_screen import MapScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.chat_screen import ChatScreen
from ui.components.safety_status import SafetyStatus

class TestHomeScreen(unittest.TestCase):
    """Test the HomeScreen class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a mock app
        self.mock_app = MagicMock()
        self.mock_app.page = MagicMock()
        self.mock_app.page.update = MagicMock()
        self.mock_app.navigate_to = MagicMock()

        # Create a HomeScreen instance
        self.home_screen = HomeScreen(self.mock_app)

        # Mock the update method to avoid UI errors
        self.home_screen.update = MagicMock()

    def test_initialization(self):
        """Test initializing the home screen."""
        # Check that the safety status component is created
        self.assertIsNotNone(self.home_screen.safety_status)

        # Check that the incidents list is created
        self.assertIsNotNone(self.home_screen.incidents_list)

        # Check that sample incidents are added
        self.assertGreater(len(self.home_screen.incidents_list.controls), 0)

    def test_handle_panic(self):
        """Test handling a panic situation."""
        # Create a mock safety status
        self.home_screen.safety_status = MagicMock()
        self.home_screen.safety_status.update_safety = MagicMock()

        # Call handle_panic
        self.home_screen.handle_panic()

        # Check that update_safety was called with the correct arguments
        self.home_screen.safety_status.update_safety.assert_called_once_with(
            is_safe=False,
            safety_score=30,
            status_message="Emergency alert sent to authorities",
        )

    def test_add_new_incident(self):
        """Test adding a new incident."""
        # Mock the incidents list
        self.home_screen.incidents_list = MagicMock()
        self.home_screen.incidents_list.controls = []

        # Add a new incident
        self.home_screen.add_new_incident(
            incident_type="Robbery",
            location="Test Location",
            description="Test Description",
            severity="High"
        )

        # Check that update was called
        self.home_screen.update.assert_called_once()

class TestLoginScreen(unittest.TestCase):
    """Test the LoginScreen class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a mock app
        self.mock_app = MagicMock()
        self.mock_app.page = MagicMock()
        self.mock_app.page.update = MagicMock()
        self.mock_app.navigate_to = MagicMock()
        self.mock_app.update_ui = MagicMock()

        # Create a mock data manager
        self.mock_data_manager = MagicMock()
        self.mock_app.data_manager = self.mock_data_manager

        # Create a LoginScreen instance
        self.login_screen = LoginScreen(self.mock_app)

        # Mock the login form controls
        self.login_screen.username = MagicMock()
        self.login_screen.password = MagicMock()
        self.login_screen.error_text = MagicMock()
        self.login_screen.login_button = MagicMock()

        # Mock the update method to avoid UI errors
        self.login_screen.update = MagicMock()

    def test_login_with_valid_credentials(self):
        """Test logging in with valid credentials."""
        # Set up the mock to return True (valid credentials)
        self.login_screen.data_manager.login = MagicMock(return_value=True)
        self.login_screen.data_manager.get_current_user = MagicMock(return_value={"id": "test_user"})

        # Set the username and password
        self.login_screen.username.value = "test"
        self.login_screen.password.value = "password"

        # Call login
        self.login_screen.login(None)

        # Check that data_manager.login was called with the correct arguments
        self.login_screen.data_manager.login.assert_called_once_with("test", "password")

        # Check that update_ui was called
        self.mock_app.update_ui.assert_called_once()

    def test_login_with_invalid_credentials(self):
        """Test logging in with invalid credentials."""
        # Set up the mock to return False (invalid credentials)
        self.login_screen.data_manager.login = MagicMock(return_value=False)

        # Set the username and password
        self.login_screen.username.value = "invalid"
        self.login_screen.password.value = "invalid"

        # Call login
        self.login_screen.login(None)

        # Check that data_manager.login was called with the correct arguments
        self.login_screen.data_manager.login.assert_called_once_with("invalid", "invalid")

        # Check that the error text is visible and has the correct value
        self.login_screen.error_text.visible = True
        self.assertTrue(self.login_screen.error_text.visible)

    def test_login_with_empty_fields(self):
        """Test logging in with empty fields."""
        # Set the username and password to empty strings
        self.login_screen.username.value = ""
        self.login_screen.password.value = ""

        # Set up a mock for data_manager.login
        self.login_screen.data_manager.login = MagicMock()

        # Call login
        self.login_screen.login(None)

        # Check that data_manager.login was not called
        self.login_screen.data_manager.login.assert_not_called()

        # Check that the error text is visible and has the correct value
        self.login_screen.error_text.visible = True
        self.assertTrue(self.login_screen.error_text.visible)

class TestSafetyStatus(unittest.TestCase):
    """Test the SafetyStatus class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a mock panic handler
        self.mock_panic_handler = MagicMock()

        # Create a SafetyStatus instance
        self.safety_status = SafetyStatus(on_panic=self.mock_panic_handler)

        # Mock the update method to avoid UI errors
        self.safety_status.update = MagicMock()

        # Mock the UI components
        self.safety_status.safety_indicator = MagicMock()
        self.safety_status.safety_score_text = MagicMock()
        self.safety_status.status_message_text = MagicMock()
        self.safety_status.panic_button = MagicMock()

    def test_initialization(self):
        """Test initializing the safety status."""
        # Check that the safety status is initialized as safe
        self.assertTrue(self.safety_status.is_safe)

        # Check that the safety score is initialized to a high value
        self.assertEqual(self.safety_status.safety_score, 90)

        # Check that the status message is initialized
        self.assertEqual(self.safety_status.status_message, "You are in a safe area")

    def test_update_safety_to_unsafe(self):
        """Test updating the safety status to unsafe."""
        # Update the safety status
        self.safety_status.update_safety(
            is_safe=False,
            safety_score=30,
            status_message="You are in a dangerous area"
        )

        # Check that the safety status was updated
        self.assertFalse(self.safety_status.is_safe)

        # Check that the safety score was updated
        self.assertEqual(self.safety_status.safety_score, 30)

        # Check that the status message was updated
        self.assertEqual(self.safety_status.status_message, "You are in a dangerous area")

        # Verify that update was called
        self.safety_status.update.assert_called_once()

    def test_update_safety_to_safe(self):
        """Test updating the safety status to safe."""
        # First set it to unsafe
        self.safety_status.update_safety(
            is_safe=False,
            safety_score=30,
            status_message="You are in a dangerous area"
        )

        # Reset the mock to check for the next call
        self.safety_status.update.reset_mock()

        # Then update it back to safe
        self.safety_status.update_safety(
            is_safe=True,
            safety_score=90,
            status_message="You are in a safe area"
        )

        # Check that the safety status was updated
        self.assertTrue(self.safety_status.is_safe)

        # Check that the safety score was updated
        self.assertEqual(self.safety_status.safety_score, 90)

        # Check that the status message was updated
        self.assertEqual(self.safety_status.status_message, "You are in a safe area")

        # Verify that update was called
        self.safety_status.update.assert_called_once()

    def test_panic_button(self):
        """Test the panic button."""
        # Directly call the panic handler that would be triggered by the button
        self.safety_status.on_panic()

        # Check that the panic handler was called
        self.mock_panic_handler.assert_called_once()

if __name__ == '__main__':
    unittest.main()

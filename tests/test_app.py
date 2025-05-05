import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import flet as ft

# Add the app directory to the path so we can import from it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.app import SafeWayAIApp
from services.data_manager import DataManager

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
        
    def test_navigation_when_not_logged_in(self):
        """Test navigation when not logged in."""
        # Ensure current_user is None
        self.app.current_user = None
        
        # Try to navigate to a protected screen
        self.app.navigate_to("home")
        
        # Check that we were redirected to the login screen
        self.assertEqual(self.app.content.content, self.app.screens["login"])
        
    def test_nav_change(self):
        """Test navigation rail change."""
        # Set current_user to simulate login
        self.app.current_user = {"id": "test_user", "username": "test"}
        
        # Create a mock event with selected_index
        mock_event = MagicMock()
        mock_event.control = MagicMock()
        
        # Test navigation to home screen
        mock_event.control.selected_index = 0
        self.app.nav_change(mock_event)
        self.assertEqual(self.app.content.content, self.app.screens["home"])
        
        # Test navigation to map screen
        mock_event.control.selected_index = 1
        self.app.nav_change(mock_event)
        self.assertEqual(self.app.content.content, self.app.screens["map"])
        
        # Test navigation to chat screen
        mock_event.control.selected_index = 2
        self.app.nav_change(mock_event)
        self.assertEqual(self.app.content.content, self.app.screens["chat"])
        
        # Test navigation to settings screen
        mock_event.control.selected_index = 3
        self.app.nav_change(mock_event)
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
        
    def test_update_ui(self):
        """Test updating the UI."""
        # Create a mock function
        mock_func = MagicMock()
        
        # Call update_ui
        self.app.update_ui(mock_func)
        
        # Check that the function was called
        mock_func.assert_called_once()

class TestIntegration(unittest.TestCase):
    """Test the integration between the app and data manager."""
    
    def setUp(self):
        """Set up the test environment."""
        # Mock the Flet page
        self.mock_page = MagicMock(spec=ft.Page)
        self.mock_page.update = MagicMock()
        self.mock_page.add = MagicMock()
        
        # Create a SafeWayAIApp instance with the mock page
        self.app = SafeWayAIApp(self.mock_page)
        
        # Create a DataManager instance
        self.data_manager = DataManager()
        
        # Patch the repositories
        self.user_repo_patcher = patch('services.repositories.user_repository.authenticate_user')
        self.mock_user_repo = self.user_repo_patcher.start()
        
        self.settings_repo_patcher = patch('services.repositories.settings_repository.get_settings')
        self.mock_settings_repo = self.settings_repo_patcher.start()
        
        # Set the data manager on the app
        self.app.data_manager = self.data_manager
        
    def tearDown(self):
        """Clean up after the test."""
        # Stop the patchers
        self.user_repo_patcher.stop()
        self.settings_repo_patcher.stop()
        
    def test_login_and_navigation(self):
        """Test logging in and navigating."""
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
        
        # Login
        result = self.data_manager.login("test", "password")
        
        # Check that login was successful
        self.assertTrue(result)
        
        # Check that current_user is set on the data manager
        self.assertIsNotNone(self.data_manager.current_user)
        
        # Set the current_user on the app
        self.app.current_user = self.data_manager.current_user
        
        # Navigate to the home screen
        self.app.navigate_to("home")
        
        # Check that we navigated to the home screen
        self.assertEqual(self.app.content.content, self.app.screens["home"])
        
        # Check that the navigation rail is visible
        self.assertTrue(self.app.nav_rail.visible)
        
    def test_logout_and_navigation(self):
        """Test logging out and navigating."""
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
        
        # Login
        result = self.data_manager.login("test", "password")
        
        # Check that login was successful
        self.assertTrue(result)
        
        # Set the current_user on the app
        self.app.current_user = self.data_manager.current_user
        
        # Navigate to the home screen
        self.app.navigate_to("home")
        
        # Check that we navigated to the home screen
        self.assertEqual(self.app.content.content, self.app.screens["home"])
        
        # Logout
        self.app.logout()
        
        # Check that current_user is None on the app
        self.assertIsNone(self.app.current_user)
        
        # Check that current_user is None on the data manager
        self.assertIsNone(self.data_manager.current_user)
        
        # Check that we navigated to the login screen
        self.assertEqual(self.app.content.content, self.app.screens["login"])
        
        # Check that the navigation rail is hidden
        self.assertFalse(self.app.nav_rail.visible)

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the app directory to the path so we can import from it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.data_manager import DataManager

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
        
        self.settings_update_patcher = patch('services.repositories.settings_repository.update_settings')
        self.mock_settings_update = self.settings_update_patcher.start()
        
        self.incident_repo_patcher = patch('services.repositories.incident_repository.get_recent_incidents')
        self.mock_incident_repo = self.incident_repo_patcher.start()
        
        self.create_incident_patcher = patch('services.repositories.incident_repository.create_incident')
        self.mock_create_incident = self.create_incident_patcher.start()
        
        self.report_repo_patcher = patch('services.repositories.report_repository.get_recent_reports')
        self.mock_report_repo = self.report_repo_patcher.start()
        
        self.create_report_patcher = patch('services.repositories.report_repository.create_report')
        self.mock_create_report = self.create_report_patcher.start()
        
    def tearDown(self):
        """Clean up after the test."""
        # Stop the patchers
        self.user_repo_patcher.stop()
        self.settings_repo_patcher.stop()
        self.settings_update_patcher.stop()
        self.incident_repo_patcher.stop()
        self.create_incident_patcher.stop()
        self.report_repo_patcher.stop()
        self.create_report_patcher.stop()
        
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
        
    def test_get_current_user(self):
        """Test getting the current user."""
        # Set current_user to simulate being logged in
        self.data_manager.current_user = {"id": "test_user", "username": "test"}
        
        # Get the current user
        user = self.data_manager.get_current_user()
        
        # Check that the correct user was returned
        self.assertEqual(user, {"id": "test_user", "username": "test"})
        
    def test_get_settings(self):
        """Test getting settings."""
        # Set current_user to simulate being logged in
        self.data_manager.current_user = {"id": "test_user", "username": "test"}
        
        # Set up the mock to return settings
        self.mock_settings_repo.return_value = {
            "theme": "light",
            "notifications": True,
            "emergency_contacts": []
        }
        
        # Get settings
        settings = self.data_manager.get_settings()
        
        # Check that the correct settings were returned
        self.assertEqual(settings, {
            "theme": "light",
            "notifications": True,
            "emergency_contacts": []
        })
        
        # Check that get_settings was called with the correct user ID
        self.mock_settings_repo.assert_called_once_with("test_user")
        
    def test_get_settings_not_logged_in(self):
        """Test getting settings when not logged in."""
        # Ensure current_user is None
        self.data_manager.current_user = None
        
        # Get settings
        settings = self.data_manager.get_settings()
        
        # Check that None was returned
        self.assertIsNone(settings)
        
        # Check that get_settings was not called
        self.mock_settings_repo.assert_not_called()
        
    def test_update_settings(self):
        """Test updating settings."""
        # Set current_user to simulate being logged in
        self.data_manager.current_user = {"id": "test_user", "username": "test"}
        
        # Set up the mock to return updated settings
        self.mock_settings_update.return_value = {
            "theme": "dark",
            "notifications": False,
            "emergency_contacts": ["123-456-7890"]
        }
        
        # Update settings
        settings_data = {
            "theme": "dark",
            "notifications": False,
            "emergency_contacts": ["123-456-7890"]
        }
        
        result = self.data_manager.update_settings(settings_data)
        
        # Check that the update was successful
        self.assertTrue(result)
        
        # Check that update_settings was called with the correct arguments
        self.mock_settings_update.assert_called_once_with("test_user", settings_data)
        
        # Check that user_settings was updated
        self.assertEqual(self.data_manager.user_settings, {
            "theme": "dark",
            "notifications": False,
            "emergency_contacts": ["123-456-7890"]
        })
        
    def test_update_settings_not_logged_in(self):
        """Test updating settings when not logged in."""
        # Ensure current_user is None
        self.data_manager.current_user = None
        
        # Update settings
        settings_data = {
            "theme": "dark",
            "notifications": False,
            "emergency_contacts": ["123-456-7890"]
        }
        
        result = self.data_manager.update_settings(settings_data)
        
        # Check that the update failed
        self.assertFalse(result)
        
        # Check that update_settings was not called
        self.mock_settings_update.assert_not_called()
        
    def test_get_recent_incidents(self):
        """Test getting recent incidents."""
        # Set up the mock to return incidents
        incidents = [
            {
                "id": "incident_1",
                "type": "Robbery",
                "location": "Test Location 1",
                "timestamp": "2023-01-01T12:00:00"
            },
            {
                "id": "incident_2",
                "type": "Assault",
                "location": "Test Location 2",
                "timestamp": "2023-01-02T12:00:00"
            }
        ]
        self.mock_incident_repo.return_value = incidents
        
        # Get recent incidents
        result = self.data_manager.get_recent_incidents(limit=2)
        
        # Check that the correct incidents were returned
        self.assertEqual(result, incidents)
        
        # Check that get_recent_incidents was called with the correct limit
        self.mock_incident_repo.assert_called_once_with(limit=2)
        
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
        
    def test_get_community_reports(self):
        """Test getting community reports."""
        # Set up the mock to return reports
        reports = [
            {
                "id": "report_1",
                "type": "Suspicious Activity",
                "location": "Test Location 1",
                "timestamp": "2023-01-01T12:00:00"
            },
            {
                "id": "report_2",
                "type": "Traffic Accident",
                "location": "Test Location 2",
                "timestamp": "2023-01-02T12:00:00"
            }
        ]
        self.mock_report_repo.return_value = reports
        
        # Get community reports
        result = self.data_manager.get_community_reports(limit=2)
        
        # Check that the correct reports were returned
        self.assertEqual(result, reports)
        
        # Check that get_recent_reports was called with the correct limit
        self.mock_report_repo.assert_called_once_with(limit=2)
        
    def test_submit_report(self):
        """Test submitting a report."""
        # Set up the mock to return a report ID
        self.mock_create_report.return_value = "report_123"
        
        # Set current_user to simulate being logged in
        self.data_manager.current_user = {"id": "test_user", "username": "test"}
        
        # Submit a report
        report_data = {
            "type": "Suspicious Activity",
            "details": "Test report",
            "location": "Test location",
            "latitude": -26.2041,
            "longitude": 28.0473,
            "severity": "medium",
            "images": []
        }
        
        result = self.data_manager.submit_report(report_data)
        
        # Check that the report was created
        self.assertEqual(result, "report_123")
        
        # Check that create_report was called with the correct arguments
        self.mock_create_report.assert_called_once_with(
            report_type="Suspicious Activity",
            details="Test report",
            location="Test location",
            latitude=-26.2041,
            longitude=28.0473,
            severity="medium",
            reported_by="test_user",
            images=[]
        )
        
    def test_submit_report_not_logged_in(self):
        """Test submitting a report when not logged in."""
        # Ensure current_user is None
        self.data_manager.current_user = None
        
        # Submit a report
        report_data = {
            "type": "Suspicious Activity",
            "details": "Test report",
            "location": "Test location",
            "latitude": -26.2041,
            "longitude": 28.0473,
            "severity": "medium",
            "images": []
        }
        
        result = self.data_manager.submit_report(report_data)
        
        # Check that the report was not created
        self.assertFalse(result)
        
        # Check that create_report was not called
        self.mock_create_report.assert_not_called()

if __name__ == '__main__':
    unittest.main()

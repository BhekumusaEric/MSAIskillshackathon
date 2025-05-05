"""
Settings Repository for Firebase/Firestore

This module provides a repository for settings operations in Firebase/Firestore.
"""

import uuid
import datetime
from services.repositories.firebase_repository import FirebaseRepository

class SettingsRepository(FirebaseRepository):
    """Repository for settings operations."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__("settings")
    
    def get_settings(self, user_id):
        """
        Get settings for a user.
        
        Args:
            user_id (str): The user ID
            
        Returns:
            dict: The settings, or default settings if not found
        """
        # Query for settings with this user_id
        settings = self.query_documents(field="user_id", operator="==", value=user_id)
        
        if settings:
            # Return the most recent settings
            settings.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            return settings[0]
        
        # Return default settings
        return self.create_default_settings(user_id)
    
    def create_default_settings(self, user_id):
        """
        Create default settings for a user.
        
        Args:
            user_id (str): The user ID
            
        Returns:
            dict: The created settings
        """
        # Default settings
        settings = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "theme": "light",
            "notifications_enabled": True,
            "sms_alerts_enabled": True,
            "authority_alerts_enabled": True,
            "check_interval": 5,
            "alert_sensitivity": 50,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        return self.create_document(settings, settings["id"])
    
    def update_settings(self, user_id, settings_data):
        """
        Update settings for a user.
        
        Args:
            user_id (str): The user ID
            settings_data (dict): The settings data to update
            
        Returns:
            dict: The updated settings
        """
        # Get current settings
        current_settings = self.get_settings(user_id)
        
        # Update with new data
        for key, value in settings_data.items():
            if key not in ["id", "user_id", "created_at"]:
                current_settings[key] = value
        
        # Update timestamp
        current_settings["updated_at"] = datetime.datetime.now().isoformat()
        
        return self.update_document(current_settings["id"], current_settings)
    
    def delete_settings(self, settings_id):
        """
        Delete settings.
        
        Args:
            settings_id (str): The settings ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        return self.delete_document(settings_id)
    
    def get_all_user_settings(self):
        """
        Get settings for all users.
        
        Returns:
            list: All settings
        """
        return self.query_documents()

# Singleton instance
get_settings = SettingsRepository().get_settings
create_default_settings = SettingsRepository().create_default_settings
update_settings = SettingsRepository().update_settings
delete_settings = SettingsRepository().delete_settings
get_all_user_settings = SettingsRepository().get_all_user_settings

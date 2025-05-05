"""
Settings Repository for Azure Cosmos DB

This module provides a repository for user settings operations in Azure Cosmos DB.
"""

import uuid
import datetime
from services.repositories.base_repository import BaseRepository

class SettingsRepository(BaseRepository):
    """Repository for user settings operations."""
    
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
        query = "SELECT * FROM c WHERE c.user_id = @user_id"
        parameters = [{"name": "@user_id", "value": user_id}]
        
        results = self.query_items(query, parameters)
        
        if results:
            # Return the most recent settings
            results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            return results[0]
        
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
        
        return self.create_item(settings)
    
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
        
        return self.update_item(current_settings)
    
    def delete_settings(self, settings_id):
        """
        Delete settings.
        
        Args:
            settings_id (str): The settings ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        return self.delete_item(settings_id)

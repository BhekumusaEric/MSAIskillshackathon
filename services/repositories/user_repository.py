"""
User Repository for Azure Cosmos DB

This module provides a repository for user operations in Azure Cosmos DB.
"""

import uuid
import datetime
import hashlib
from services.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    """Repository for user operations."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__("users")
    
    def get_user_by_id(self, user_id):
        """
        Get a user by ID.
        
        Args:
            user_id (str): The user ID
            
        Returns:
            dict: The user, or None if not found
        """
        return self.get_item(user_id)
    
    def get_user_by_username(self, username):
        """
        Get a user by username.
        
        Args:
            username (str): The username
            
        Returns:
            dict: The user, or None if not found
        """
        query = "SELECT * FROM c WHERE c.username = @username"
        parameters = [{"name": "@username", "value": username}]
        
        results = self.query_items(query, parameters)
        return results[0] if results else None
    
    def create_user(self, username, password, email=None, full_name=None, role="viewer"):
        """
        Create a new user.
        
        Args:
            username (str): The username
            password (str): The password
            email (str, optional): The email address
            full_name (str, optional): The full name
            role (str, optional): The role. Defaults to "viewer".
            
        Returns:
            dict: The created user
        """
        # Check if username already exists
        existing_user = self.get_user_by_username(username)
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")
        
        # Create the user
        user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "password_hash": self._hash_password(password),
            "email": email,
            "full_name": full_name,
            "role": role,
            "created_at": datetime.datetime.now().isoformat(),
            "last_login": None
        }
        
        return self.create_item(user)
    
    def update_user(self, user):
        """
        Update a user.
        
        Args:
            user (dict): The user to update
            
        Returns:
            dict: The updated user
        """
        return self.update_item(user)
    
    def delete_user(self, user_id):
        """
        Delete a user.
        
        Args:
            user_id (str): The user ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        return self.delete_item(user_id)
    
    def authenticate_user(self, username, password):
        """
        Authenticate a user.
        
        Args:
            username (str): The username
            password (str): The password
            
        Returns:
            dict: The user if authenticated, None otherwise
        """
        user = self.get_user_by_username(username)
        
        if user and user["password_hash"] == self._hash_password(password):
            # Update last login time
            user["last_login"] = datetime.datetime.now().isoformat()
            self.update_user(user)
            
            # Return user without password hash
            user_copy = user.copy()
            user_copy.pop("password_hash", None)
            return user_copy
        
        return None
    
    def _hash_password(self, password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_default_users(self):
        """Create default users if they don't exist."""
        default_users = [
            ("admin", "admin123", "admin@safewayai.com", "Admin User", "admin"),
            ("responder", "respond123", "responder@safewayai.com", "Emergency Responder", "responder"),
            ("viewer", "view123", "viewer@safewayai.com", "Regular User", "viewer")
        ]
        
        created_users = []
        for username, password, email, full_name, role in default_users:
            # Check if user already exists
            existing_user = self.get_user_by_username(username)
            if not existing_user:
                # Create the user
                user = self.create_user(username, password, email, full_name, role)
                created_users.append(user)
        
        return created_users

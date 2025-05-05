"""
User Repository for Firebase/Firestore

This module provides a repository for user operations in Firebase/Firestore.
"""

import uuid
import datetime
import hashlib
from services.repositories.firebase_repository import FirebaseRepository

class UserRepository(FirebaseRepository):
    """Repository for user operations."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__("users")
    
    def authenticate_user(self, username, password):
        """
        Authenticate a user.
        
        Args:
            username (str): The username
            password (str): The password
            
        Returns:
            dict: The user if authenticated, None otherwise
        """
        # Query for user with this username
        users = self.query_documents(field="username", operator="==", value=username)
        
        if users:
            user = users[0]
            
            # Check password (in a real app, use proper password hashing)
            # For simplicity, we're just comparing with password_hash directly
            if user.get("password_hash") == password:
                return user
        
        return None
    
    def get_user(self, user_id):
        """
        Get a user by ID.
        
        Args:
            user_id (str): The user ID
            
        Returns:
            dict: The user, or None if not found
        """
        return self.get_document(user_id)
    
    def create_user(self, username, password, email, first_name, last_name, phone_number=None):
        """
        Create a new user.
        
        Args:
            username (str): The username
            password (str): The password
            email (str): The email address
            first_name (str): The first name
            last_name (str): The last name
            phone_number (str, optional): The phone number
            
        Returns:
            dict: The created user
        """
        # Check if username already exists
        existing_users = self.query_documents(field="username", operator="==", value=username)
        if existing_users:
            return None
        
        # Create user object
        user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "password_hash": password,  # In a real app, hash the password
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "emergency_contacts": [],
            "created_at": datetime.datetime.now().isoformat(),
            "last_login": datetime.datetime.now().isoformat()
        }
        
        return self.create_document(user, user["id"])
    
    def update_user(self, user_id, user_data):
        """
        Update a user.
        
        Args:
            user_id (str): The user ID
            user_data (dict): The user data to update
            
        Returns:
            dict: The updated user
        """
        # Get current user
        current_user = self.get_document(user_id)
        if not current_user:
            return None
        
        # Update with new data
        for key, value in user_data.items():
            if key not in ["id", "created_at", "password_hash"]:
                current_user[key] = value
        
        # Update last login if specified
        if "last_login" in user_data:
            current_user["last_login"] = user_data["last_login"]
        
        return self.update_document(user_id, current_user)
    
    def add_emergency_contact(self, user_id, name, phone_number, relationship):
        """
        Add an emergency contact for a user.
        
        Args:
            user_id (str): The user ID
            name (str): The contact name
            phone_number (str): The contact phone number
            relationship (str): The relationship to the user
            
        Returns:
            dict: The updated user
        """
        # Get current user
        current_user = self.get_document(user_id)
        if not current_user:
            return None
        
        # Create emergency contact
        contact = {
            "name": name,
            "phone_number": phone_number,
            "relationship": relationship
        }
        
        # Add to emergency contacts
        if "emergency_contacts" not in current_user:
            current_user["emergency_contacts"] = []
        
        current_user["emergency_contacts"].append(contact)
        
        return self.update_document(user_id, current_user)
    
    def remove_emergency_contact(self, user_id, contact_index):
        """
        Remove an emergency contact for a user.
        
        Args:
            user_id (str): The user ID
            contact_index (int): The index of the contact to remove
            
        Returns:
            dict: The updated user
        """
        # Get current user
        current_user = self.get_document(user_id)
        if not current_user:
            return None
        
        # Check if emergency contacts exist
        if "emergency_contacts" not in current_user or not current_user["emergency_contacts"]:
            return current_user
        
        # Check if index is valid
        if contact_index < 0 or contact_index >= len(current_user["emergency_contacts"]):
            return current_user
        
        # Remove contact
        current_user["emergency_contacts"].pop(contact_index)
        
        return self.update_document(user_id, current_user)

# Singleton instance
authenticate_user = UserRepository().authenticate_user
get_user = UserRepository().get_user
create_user = UserRepository().create_user
update_user = UserRepository().update_user
add_emergency_contact = UserRepository().add_emergency_contact
remove_emergency_contact = UserRepository().remove_emergency_contact

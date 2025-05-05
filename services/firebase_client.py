"""
Firebase Client for SafeWayAI

This module provides a client for connecting to Firebase/Firestore.
"""

import os
import json
import datetime
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirebaseClient:
    """Base client for Firebase/Firestore."""

    def __init__(self):
        """Initialize the Firebase client."""
        # Path to service account key
        self.key_path = os.getenv('FIREBASE_KEY_PATH', 'config/firebase_key.json')
        
        # Initialize client
        self.app = None
        self.db = None
        self.collections = {}
        
        # Connect if credentials are available
        self._ensure_config_exists()
        self.connect()
    
    def _ensure_config_exists(self):
        """Ensure the Firebase configuration file exists."""
        key_dir = os.path.dirname(self.key_path)
        os.makedirs(key_dir, exist_ok=True)
        
        if not os.path.exists(self.key_path):
            # Create a template configuration file
            default_config = {
                "type": "service_account",
                "project_id": "safewayai",
                "private_key_id": "YOUR_PRIVATE_KEY_ID",
                "private_key": "YOUR_PRIVATE_KEY",
                "client_email": "YOUR_CLIENT_EMAIL",
                "client_id": "YOUR_CLIENT_ID",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "YOUR_CLIENT_CERT_URL",
                "universe_domain": "googleapis.com"
            }
            
            with open(self.key_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"Created template Firebase key file at {self.key_path}")
            print("Please update this file with your actual Firebase credentials")

    def connect(self):
        """Connect to Firebase."""
        try:
            # Check if already initialized
            if self.app is not None:
                return True
                
            # Check if key file exists
            if not os.path.exists(self.key_path):
                print(f"Firebase key file not found at {self.key_path}")
                self._use_mock_db()
                return False
                
            # Initialize Firebase app
            try:
                self.app = firebase_admin.get_app()
            except ValueError:
                # Initialize new app if not already initialized
                cred = credentials.Certificate(self.key_path)
                self.app = firebase_admin.initialize_app(cred)
            
            # Get Firestore client
            self.db = firestore.client()
            
            # Initialize collections
            self._init_collections()
            
            print("Connected to Firebase successfully")
            return True
        except Exception as e:
            print(f"Error connecting to Firebase: {e}")
            self._use_mock_db()
            return False
    
    def _use_mock_db(self):
        """Use a mock database for offline use."""
        print("Using mock database for offline use")
        self.app = "mock_app"
        self.db = "mock_db"
        
        # Create cache directory
        cache_dir = os.path.join('data', 'firebase_cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize collections
        self._init_collections()
    
    def _init_collections(self):
        """Initialize collections."""
        # Define collections
        collections_config = [
            {"id": "users", "priority": 1},
            {"id": "incidents", "priority": 2},
            {"id": "reports", "priority": 3},
            {"id": "settings", "priority": 4}
        ]
        
        # Sort collections by priority
        collections_config.sort(key=lambda x: x["priority"])
        
        # Initialize collections
        for collection_config in collections_config:
            collection_id = collection_config["id"]
            
            try:
                if self.db == "mock_db":
                    # Create mock collection
                    self._create_mock_collection(collection_id)
                else:
                    # Get collection reference
                    collection = self.db.collection(collection_id)
                    self.collections[collection_id] = collection
                    print(f"Collection {collection_id} initialized")
            except Exception as e:
                print(f"Error initializing collection {collection_id}: {e}")
                # Create mock collection as fallback
                self._create_mock_collection(collection_id)
    
    def _create_mock_collection(self, collection_id):
        """Create a mock collection for offline use."""
        # Create cache directory
        cache_dir = os.path.join('data', 'firebase_cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create cache file if it doesn't exist
        cache_path = os.path.join(cache_dir, f"{collection_id}.json")
        if not os.path.exists(cache_path):
            with open(cache_path, 'w') as f:
                json.dump({
                    "documents": [],
                    "last_updated": datetime.datetime.now().isoformat()
                }, f, indent=2)
        
        # Store the cache path
        self.collections[collection_id] = cache_path
        print(f"Created mock collection for {collection_id} using local cache")
    
    def get_collection(self, collection_id):
        """Get a collection by ID."""
        if not self.db:
            if not self.connect():
                return None
        
        if collection_id not in self.collections:
            try:
                if self.db == "mock_db":
                    # Create mock collection
                    self._create_mock_collection(collection_id)
                else:
                    # Get collection reference
                    collection = self.db.collection(collection_id)
                    self.collections[collection_id] = collection
                    print(f"Collection {collection_id} initialized")
            except Exception as e:
                print(f"Error getting collection {collection_id}: {e}")
                # Create mock collection as fallback
                self._create_mock_collection(collection_id)
        
        return self.collections[collection_id]
    
    def is_connected(self):
        """Check if connected to Firebase."""
        return self.app is not None and self.db is not None and self.db != "mock_db"
    
    def is_mock(self):
        """Check if using mock database."""
        return self.db == "mock_db"

# Singleton instance
firebase_client = FirebaseClient()

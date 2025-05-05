"""
Azure Cosmos DB Service for SafeWayAI

This module provides integration with Azure Cosmos DB for secure data storage
and retrieval, compliant with GDPR and POPIA requirements.
"""

import os
import json
import datetime
import threading
import uuid
from services.azure_client import AzureClient
from services.repositories import (
    user_repository,
    incident_repository,
    report_repository,
    settings_repository
)

class AzureCosmos:
    """
    Azure Cosmos DB service for secure data storage and retrieval.
    """

    # Path to the local cache for offline use
    CACHE_PATH = os.path.join('data', 'cosmos_cache.json')

    @classmethod
    def _ensure_cache_exists(cls):
        """Ensure the Cosmos DB cache exists for offline use."""
        os.makedirs(os.path.dirname(cls.CACHE_PATH), exist_ok=True)

        if not os.path.exists(cls.CACHE_PATH):
            # Create an empty cache
            default_cache = {
                "incidents": [],
                "reports": [],
                "users": [],
                "settings": [],
                "last_updated": datetime.datetime.now().isoformat()
            }

            with open(cls.CACHE_PATH, 'w') as f:
                json.dump(default_cache, f, indent=2)

    @classmethod
    def _get_cosmos_config(cls):
        """Get Azure Cosmos DB configuration."""
        config = AzureClient.load_config()
        return config["cosmos_db"]

    @classmethod
    def log_incident(cls, incident_type, details, location=None, latitude=None, longitude=None,
                    severity="medium", reported_by=None, callback=None):
        """
        Log an incident to Azure Cosmos DB.

        Args:
            incident_type (str): Type of incident
            details (str): Incident details
            location (dict or str, optional): Location information
            latitude (float, optional): Latitude coordinate
            longitude (float, optional): Longitude coordinate
            severity (str, optional): Incident severity
            reported_by (str, optional): User ID who reported the incident
            callback (callable, optional): Function to call with result

        Returns:
            If callback is None, this function will return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        # Extract location information
        location_str = location
        if isinstance(location, dict):
            latitude = location.get("lat", latitude)
            longitude = location.get("lon", longitude)
            location_str = f"{latitude}, {longitude}"

        if not callback:
            # Create the incident synchronously
            return incident_repository.create_incident(
                incident_type=incident_type,
                description=details,
                location=location_str,
                latitude=latitude,
                longitude=longitude,
                severity=severity,
                reported_by=reported_by
            )

        # Create the incident asynchronously
        def process_request():
            try:
                incident = incident_repository.create_incident(
                    incident_type=incident_type,
                    description=details,
                    location=location_str,
                    latitude=latitude,
                    longitude=longitude,
                    severity=severity,
                    reported_by=reported_by
                )
                callback(incident)
            except Exception as e:
                print(f"Error creating incident: {e}")
                callback({"error": str(e)})

        thread = threading.Thread(target=process_request)
        thread.daemon = True
        thread.start()

    @classmethod
    def get_incidents(cls, limit=10, callback=None):
        """
        Get recent incidents from Azure Cosmos DB.

        Args:
            limit (int): Maximum number of incidents to return
            callback (callable, optional): Function to call with result

        Returns:
            If callback is None, this function will return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not callback:
            # Get incidents synchronously
            return incident_repository.get_recent_incidents(limit=limit)

        # Get incidents asynchronously
        def process_request():
            try:
                incidents = incident_repository.get_recent_incidents(limit=limit)
                callback(incidents)
            except Exception as e:
                print(f"Error getting incidents: {e}")
                callback([])

        thread = threading.Thread(target=process_request)
        thread.daemon = True
        thread.start()

    @classmethod
    def submit_report(cls, report_type, details, location, images=None, callback=None):
        """
        Submit a community report to Azure Cosmos DB.

        Args:
            report_type (str): Type of report (e.g., "crime", "hazard")
            details (str): Report details
            location (dict or str): Location information
            images (list, optional): List of image paths
            callback (callable, optional): Function to call with result

        Returns:
            If callback is None, this function will return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        # Extract location information
        location_str = location
        latitude = None
        longitude = None

        if isinstance(location, dict):
            latitude = location.get("lat")
            longitude = location.get("lon")
            location_str = f"{latitude}, {longitude}"

        if not callback:
            # Create the report synchronously
            return report_repository.create_report(
                report_type=report_type,
                details=details,
                location=location_str,
                latitude=latitude,
                longitude=longitude,
                images=images
            )

        # Create the report asynchronously
        def process_request():
            try:
                report = report_repository.create_report(
                    report_type=report_type,
                    details=details,
                    location=location_str,
                    latitude=latitude,
                    longitude=longitude,
                    images=images
                )
                callback(report)
            except Exception as e:
                print(f"Error creating report: {e}")
                callback({"error": str(e)})

        thread = threading.Thread(target=process_request)
        thread.daemon = True
        thread.start()

    @classmethod
    def get_reports(cls, limit=10, callback=None):
        """
        Get recent community reports from Azure Cosmos DB.

        Args:
            limit (int): Maximum number of reports to return
            callback (callable, optional): Function to call with result

        Returns:
            If callback is None, this function will return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not callback:
            # Get reports synchronously
            return report_repository.get_recent_reports(limit=limit)

        # Get reports asynchronously
        def process_request():
            try:
                reports = report_repository.get_recent_reports(limit=limit)
                callback(reports)
            except Exception as e:
                print(f"Error getting reports: {e}")
                callback([])

        thread = threading.Thread(target=process_request)
        thread.daemon = True
        thread.start()

    @classmethod
    def save_user_settings(cls, user_id, settings, callback=None):
        """
        Save user settings to Azure Cosmos DB.

        Args:
            user_id (str): User ID
            settings (dict): User settings
            callback (callable, optional): Function to call with result

        Returns:
            If callback is None, this function will return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not callback:
            # Update settings synchronously
            return settings_repository.update_settings(user_id, settings)

        # Update settings asynchronously
        def process_request():
            try:
                updated_settings = settings_repository.update_settings(user_id, settings)
                callback(updated_settings)
            except Exception as e:
                print(f"Error updating settings: {e}")
                callback({"error": str(e)})

        thread = threading.Thread(target=process_request)
        thread.daemon = True
        thread.start()

    @classmethod
    def get_user_settings(cls, user_id, callback=None):
        """
        Get user settings from Azure Cosmos DB.

        Args:
            user_id (str): User ID
            callback (callable, optional): Function to call with result

        Returns:
            If callback is None, this function will return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not callback:
            # Get settings synchronously
            return settings_repository.get_settings(user_id)

        # Get settings asynchronously
        def process_request():
            try:
                settings = settings_repository.get_settings(user_id)
                callback(settings)
            except Exception as e:
                print(f"Error getting settings: {e}")
                callback({})

        thread = threading.Thread(target=process_request)
        thread.daemon = True
        thread.start()

    @classmethod
    def initialize_database(cls):
        """
        Initialize the database with default data.

        This method creates default users, incidents, and other data if they don't exist.
        """
        # Create default users
        users = user_repository.create_default_users()

        # Create sample incidents
        incidents = incident_repository.create_sample_incidents()

        return {
            "users_created": len(users),
            "incidents_created": len(incidents)
        }

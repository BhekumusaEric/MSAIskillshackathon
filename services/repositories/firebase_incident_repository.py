"""
Incident Repository for Firebase/Firestore

This module provides a repository for incident operations in Firebase/Firestore.
"""

import uuid
import datetime
from services.repositories.firebase_repository import FirebaseRepository

class IncidentRepository(FirebaseRepository):
    """Repository for incident operations."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__("incidents")
    
    def get_incident(self, incident_id):
        """
        Get an incident by ID.
        
        Args:
            incident_id (str): The incident ID
            
        Returns:
            dict: The incident, or None if not found
        """
        return self.get_document(incident_id)
    
    def get_recent_incidents(self, limit=10):
        """
        Get recent incidents.
        
        Args:
            limit (int, optional): The maximum number of incidents to return
            
        Returns:
            list: The incidents
        """
        # In a real implementation, we would query by timestamp
        # For now, we'll just get all incidents and sort them
        incidents = self.query_documents()
        
        # Sort by timestamp (newest first)
        incidents.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limit results
        return incidents[:limit]
    
    def get_incidents_by_location(self, latitude, longitude, radius_km=1):
        """
        Get incidents near a location.
        
        Args:
            latitude (float): The latitude
            longitude (float): The longitude
            radius_km (float, optional): The radius in kilometers
            
        Returns:
            list: The incidents
        """
        # In a real implementation, we would use geospatial queries
        # For now, we'll just get all incidents and filter them
        incidents = self.query_documents()
        
        # Filter by location (very rough approximation)
        nearby_incidents = []
        for incident in incidents:
            incident_lat = incident.get("latitude")
            incident_lon = incident.get("longitude")
            
            if incident_lat is not None and incident_lon is not None:
                # Calculate distance (very rough approximation)
                lat_diff = abs(latitude - incident_lat)
                lon_diff = abs(longitude - incident_lon)
                
                # Rough distance in kilometers (1 degree is approximately 111 km)
                distance_km = ((lat_diff ** 2) + (lon_diff ** 2)) ** 0.5 * 111
                
                if distance_km <= radius_km:
                    nearby_incidents.append(incident)
        
        return nearby_incidents
    
    def create_incident(self, incident_type, description, location, latitude, longitude, severity, reported_by, status="active"):
        """
        Create a new incident.
        
        Args:
            incident_type (str): The incident type
            description (str): The description
            location (str): The location description
            latitude (float): The latitude
            longitude (float): The longitude
            severity (str): The severity (low, medium, high)
            reported_by (str): The user ID who reported the incident
            status (str, optional): The status (active, investigating, resolved)
            
        Returns:
            dict: The created incident
        """
        # Create incident object
        incident = {
            "id": str(uuid.uuid4()),
            "incident_type": incident_type,
            "description": description,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "severity": severity,
            "reported_by": reported_by,
            "status": status,
            "timestamp": datetime.datetime.now().isoformat(),
            "report_count": 1
        }
        
        return self.create_document(incident, incident["id"])
    
    def update_incident(self, incident_id, incident_data):
        """
        Update an incident.
        
        Args:
            incident_id (str): The incident ID
            incident_data (dict): The incident data to update
            
        Returns:
            dict: The updated incident
        """
        # Get current incident
        current_incident = self.get_document(incident_id)
        if not current_incident:
            return None
        
        # Update with new data
        for key, value in incident_data.items():
            if key not in ["id", "timestamp"]:
                current_incident[key] = value
        
        return self.update_document(incident_id, current_incident)
    
    def resolve_incident(self, incident_id, resolution_notes=None):
        """
        Resolve an incident.
        
        Args:
            incident_id (str): The incident ID
            resolution_notes (str, optional): Notes about the resolution
            
        Returns:
            dict: The updated incident
        """
        # Get current incident
        current_incident = self.get_document(incident_id)
        if not current_incident:
            return None
        
        # Update status and add resolution notes
        current_incident["status"] = "resolved"
        current_incident["resolved_at"] = datetime.datetime.now().isoformat()
        
        if resolution_notes:
            current_incident["resolution_notes"] = resolution_notes
        
        return self.update_document(incident_id, current_incident)
    
    def increment_report_count(self, incident_id):
        """
        Increment the report count for an incident.
        
        Args:
            incident_id (str): The incident ID
            
        Returns:
            dict: The updated incident
        """
        # Get current incident
        current_incident = self.get_document(incident_id)
        if not current_incident:
            return None
        
        # Increment report count
        current_incident["report_count"] = current_incident.get("report_count", 0) + 1
        
        return self.update_document(incident_id, current_incident)

# Singleton instance
get_incident = IncidentRepository().get_incident
get_recent_incidents = IncidentRepository().get_recent_incidents
get_incidents_by_location = IncidentRepository().get_incidents_by_location
create_incident = IncidentRepository().create_incident
update_incident = IncidentRepository().update_incident
resolve_incident = IncidentRepository().resolve_incident
increment_report_count = IncidentRepository().increment_report_count

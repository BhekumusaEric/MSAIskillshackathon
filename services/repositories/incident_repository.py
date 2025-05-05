"""
Incident Repository for Azure Cosmos DB

This module provides a repository for incident operations in Azure Cosmos DB.
"""

import uuid
import datetime
from services.repositories.base_repository import BaseRepository

class IncidentRepository(BaseRepository):
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
        return self.get_item(incident_id)
    
    def create_incident(self, incident_type, description, location, latitude=None, longitude=None, 
                       severity="medium", reported_by=None, status="active"):
        """
        Create a new incident.
        
        Args:
            incident_type (str): The type of incident
            description (str): The incident description
            location (str): The location description
            latitude (float, optional): The latitude
            longitude (float, optional): The longitude
            severity (str, optional): The severity. Defaults to "medium".
            reported_by (str, optional): The user ID who reported the incident
            status (str, optional): The status. Defaults to "active".
            
        Returns:
            dict: The created incident
        """
        # Create the incident
        incident = {
            "id": str(uuid.uuid4()),
            "type": incident_type,
            "description": description,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "severity": severity,
            "reported_by": reported_by,
            "reported_at": datetime.datetime.now().isoformat(),
            "status": status
        }
        
        return self.create_item(incident)
    
    def update_incident(self, incident):
        """
        Update an incident.
        
        Args:
            incident (dict): The incident to update
            
        Returns:
            dict: The updated incident
        """
        return self.update_item(incident)
    
    def delete_incident(self, incident_id):
        """
        Delete an incident.
        
        Args:
            incident_id (str): The incident ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        return self.delete_item(incident_id)
    
    def get_recent_incidents(self, limit=50, offset=0, status="active"):
        """
        Get recent incidents.
        
        Args:
            limit (int, optional): The maximum number of incidents to return. Defaults to 50.
            offset (int, optional): The number of incidents to skip. Defaults to 0.
            status (str, optional): The status to filter by. Defaults to "active".
            
        Returns:
            list: The incidents
        """
        query = "SELECT * FROM c WHERE c.status = @status ORDER BY c.reported_at DESC OFFSET @offset LIMIT @limit"
        parameters = [
            {"name": "@status", "value": status},
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": limit}
        ]
        
        return self.query_items(query, parameters)
    
    def get_incidents_by_location(self, latitude, longitude, radius_km=5, limit=50):
        """
        Get incidents near a location.
        
        Args:
            latitude (float): The latitude
            longitude (float): The longitude
            radius_km (float, optional): The radius in kilometers. Defaults to 5.
            limit (int, optional): The maximum number of incidents to return. Defaults to 50.
            
        Returns:
            list: The incidents
        """
        # This is a simplified implementation that doesn't use geospatial queries
        # In a real implementation, you would use a geospatial index and ST_DISTANCE
        
        # For now, we'll just get all incidents and filter in memory
        incidents = self.get_recent_incidents(limit=100)
        
        # Filter by distance
        result = []
        for incident in incidents:
            if incident.get("latitude") and incident.get("longitude"):
                distance = self._calculate_distance(
                    latitude, longitude, 
                    incident["latitude"], incident["longitude"]
                )
                
                if distance <= radius_km:
                    incident["distance_km"] = distance
                    result.append(incident)
        
        # Sort by distance and limit
        result.sort(key=lambda x: x.get("distance_km", float("inf")))
        return result[:limit]
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the distance between two points in kilometers.
        This uses the Haversine formula.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Earth radius in kilometers
        radius = 6371
        
        # Distance in kilometers
        return radius * c
    
    def create_sample_incidents(self):
        """Create sample incidents if none exist."""
        # Check if there are any incidents
        incidents = self.get_recent_incidents(limit=1)
        if incidents:
            return []
        
        # Sample incidents
        sample_incidents = [
            ("Robbery", "Armed robbery at convenience store", "123 Main St", -26.2041, 28.0473, "high", None),
            ("Assault", "Physical altercation outside nightclub", "456 Club Ave", -26.1929, 28.0324, "medium", None),
            ("Suspicious Activity", "Person loitering in parking lot", "789 Market St", -26.2053, 28.0385, "low", None),
            ("Traffic Accident", "Multi-vehicle collision", "101 Highway Rd", -26.1975, 28.0568, "high", None),
            ("Fire", "Building fire reported", "202 Residential Blvd", -26.1881, 28.0412, "high", None)
        ]
        
        created_incidents = []
        for incident_type, description, location, lat, lon, severity, reported_by in sample_incidents:
            incident = self.create_incident(
                incident_type=incident_type,
                description=description,
                location=location,
                latitude=lat,
                longitude=lon,
                severity=severity,
                reported_by=reported_by
            )
            created_incidents.append(incident)
        
        return created_incidents

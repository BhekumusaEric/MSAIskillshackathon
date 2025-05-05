"""
Report Repository for Azure Cosmos DB

This module provides a repository for community report operations in Azure Cosmos DB.
"""

import uuid
import datetime
from services.repositories.base_repository import BaseRepository

class ReportRepository(BaseRepository):
    """Repository for community report operations."""
    
    def __init__(self):
        """Initialize the repository."""
        super().__init__("reports")
    
    def get_report(self, report_id):
        """
        Get a report by ID.
        
        Args:
            report_id (str): The report ID
            
        Returns:
            dict: The report, or None if not found
        """
        return self.get_item(report_id)
    
    def create_report(self, report_type, details, location, latitude=None, longitude=None, 
                     severity="medium", reported_by=None, images=None, status="pending"):
        """
        Create a new community report.
        
        Args:
            report_type (str): The type of report
            details (str): The report details
            location (str): The location description
            latitude (float, optional): The latitude
            longitude (float, optional): The longitude
            severity (str, optional): The severity. Defaults to "medium".
            reported_by (str, optional): The user ID who reported the incident
            images (list, optional): List of image paths or URLs
            status (str, optional): The status. Defaults to "pending".
            
        Returns:
            dict: The created report
        """
        # Create the report
        report = {
            "id": str(uuid.uuid4()),
            "type": report_type,
            "details": details,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "severity": severity,
            "reported_by": reported_by,
            "images": images or [],
            "reported_at": datetime.datetime.now().isoformat(),
            "status": status,
            "verified": False
        }
        
        return self.create_item(report)
    
    def update_report(self, report):
        """
        Update a report.
        
        Args:
            report (dict): The report to update
            
        Returns:
            dict: The updated report
        """
        return self.update_item(report)
    
    def delete_report(self, report_id):
        """
        Delete a report.
        
        Args:
            report_id (str): The report ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        return self.delete_item(report_id)
    
    def get_recent_reports(self, limit=50, offset=0, status=None):
        """
        Get recent reports.
        
        Args:
            limit (int, optional): The maximum number of reports to return. Defaults to 50.
            offset (int, optional): The number of reports to skip. Defaults to 0.
            status (str, optional): The status to filter by. If None, returns all reports.
            
        Returns:
            list: The reports
        """
        if status:
            query = "SELECT * FROM c WHERE c.status = @status ORDER BY c.reported_at DESC OFFSET @offset LIMIT @limit"
            parameters = [
                {"name": "@status", "value": status},
                {"name": "@offset", "value": offset},
                {"name": "@limit", "value": limit}
            ]
        else:
            query = "SELECT * FROM c ORDER BY c.reported_at DESC OFFSET @offset LIMIT @limit"
            parameters = [
                {"name": "@offset", "value": offset},
                {"name": "@limit", "value": limit}
            ]
        
        return self.query_items(query, parameters)
    
    def get_reports_by_user(self, user_id, limit=50, offset=0):
        """
        Get reports by a specific user.
        
        Args:
            user_id (str): The user ID
            limit (int, optional): The maximum number of reports to return. Defaults to 50.
            offset (int, optional): The number of reports to skip. Defaults to 0.
            
        Returns:
            list: The reports
        """
        query = "SELECT * FROM c WHERE c.reported_by = @user_id ORDER BY c.reported_at DESC OFFSET @offset LIMIT @limit"
        parameters = [
            {"name": "@user_id", "value": user_id},
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": limit}
        ]
        
        return self.query_items(query, parameters)
    
    def get_reports_by_location(self, latitude, longitude, radius_km=5, limit=50):
        """
        Get reports near a location.
        
        Args:
            latitude (float): The latitude
            longitude (float): The longitude
            radius_km (float, optional): The radius in kilometers. Defaults to 5.
            limit (int, optional): The maximum number of reports to return. Defaults to 50.
            
        Returns:
            list: The reports
        """
        # This is a simplified implementation that doesn't use geospatial queries
        # In a real implementation, you would use a geospatial index and ST_DISTANCE
        
        # For now, we'll just get all reports and filter in memory
        reports = self.get_recent_reports(limit=100)
        
        # Filter by distance
        result = []
        for report in reports:
            if report.get("latitude") and report.get("longitude"):
                distance = self._calculate_distance(
                    latitude, longitude, 
                    report["latitude"], report["longitude"]
                )
                
                if distance <= radius_km:
                    report["distance_km"] = distance
                    result.append(report)
        
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

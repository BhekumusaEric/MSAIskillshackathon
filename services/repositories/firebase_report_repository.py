"""
Report Repository for Firebase/Firestore

This module provides a repository for report operations in Firebase/Firestore.
"""

import uuid
import datetime
from services.repositories.firebase_repository import FirebaseRepository

class ReportRepository(FirebaseRepository):
    """Repository for report operations."""
    
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
        return self.get_document(report_id)
    
    def get_recent_reports(self, limit=10):
        """
        Get recent reports.
        
        Args:
            limit (int, optional): The maximum number of reports to return
            
        Returns:
            list: The reports
        """
        # In a real implementation, we would query by timestamp
        # For now, we'll just get all reports and sort them
        reports = self.query_documents()
        
        # Sort by timestamp (newest first)
        reports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limit results
        return reports[:limit]
    
    def get_reports_by_user(self, user_id, limit=10):
        """
        Get reports by a user.
        
        Args:
            user_id (str): The user ID
            limit (int, optional): The maximum number of reports to return
            
        Returns:
            list: The reports
        """
        # Query for reports with this user_id
        reports = self.query_documents(field="reported_by", operator="==", value=user_id)
        
        # Sort by timestamp (newest first)
        reports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limit results
        return reports[:limit]
    
    def create_report(self, report_type, details, location, latitude, longitude, severity, reported_by, images=None):
        """
        Create a new report.
        
        Args:
            report_type (str): The report type
            details (str): The details
            location (str): The location description
            latitude (float): The latitude
            longitude (float): The longitude
            severity (str): The severity (low, medium, high)
            reported_by (str): The user ID who reported the report
            images (list, optional): List of image URLs
            
        Returns:
            dict: The created report
        """
        # Create report object
        report = {
            "id": str(uuid.uuid4()),
            "report_type": report_type,
            "details": details,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "severity": severity,
            "reported_by": reported_by,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "pending",
            "images": images or []
        }
        
        return self.create_document(report, report["id"])
    
    def update_report(self, report_id, report_data):
        """
        Update a report.
        
        Args:
            report_id (str): The report ID
            report_data (dict): The report data to update
            
        Returns:
            dict: The updated report
        """
        # Get current report
        current_report = self.get_document(report_id)
        if not current_report:
            return None
        
        # Update with new data
        for key, value in report_data.items():
            if key not in ["id", "timestamp", "reported_by"]:
                current_report[key] = value
        
        return self.update_document(report_id, current_report)
    
    def verify_report(self, report_id, verified_by, notes=None):
        """
        Verify a report.
        
        Args:
            report_id (str): The report ID
            verified_by (str): The user ID who verified the report
            notes (str, optional): Verification notes
            
        Returns:
            dict: The updated report
        """
        # Get current report
        current_report = self.get_document(report_id)
        if not current_report:
            return None
        
        # Update status and add verification details
        current_report["status"] = "verified"
        current_report["verified_at"] = datetime.datetime.now().isoformat()
        current_report["verified_by"] = verified_by
        
        if notes:
            current_report["verification_notes"] = notes
        
        return self.update_document(report_id, current_report)
    
    def reject_report(self, report_id, rejected_by, reason=None):
        """
        Reject a report.
        
        Args:
            report_id (str): The report ID
            rejected_by (str): The user ID who rejected the report
            reason (str, optional): Rejection reason
            
        Returns:
            dict: The updated report
        """
        # Get current report
        current_report = self.get_document(report_id)
        if not current_report:
            return None
        
        # Update status and add rejection details
        current_report["status"] = "rejected"
        current_report["rejected_at"] = datetime.datetime.now().isoformat()
        current_report["rejected_by"] = rejected_by
        
        if reason:
            current_report["rejection_reason"] = reason
        
        return self.update_document(report_id, current_report)

# Singleton instance
get_report = ReportRepository().get_report
get_recent_reports = ReportRepository().get_recent_reports
get_reports_by_user = ReportRepository().get_reports_by_user
create_report = ReportRepository().create_report
update_report = ReportRepository().update_report
verify_report = ReportRepository().verify_report
reject_report = ReportRepository().reject_report

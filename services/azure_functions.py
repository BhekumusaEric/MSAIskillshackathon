"""
Azure Functions Service for SafeWayAI

This module provides integration with Azure Functions for serverless processing
of Whistle reports and communication services.
"""

import os
import json
import datetime
import threading
import uuid
from services.azure_client import AzureClient

class AzureFunctions:
    """
    Azure Functions service for serverless processing and communication.
    """
    
    # Path to the local cache for offline use
    CACHE_PATH = os.path.join('data', 'functions_cache.json')
    
    @classmethod
    def _ensure_cache_exists(cls):
        """Ensure the Functions cache exists for offline use."""
        os.makedirs(os.path.dirname(cls.CACHE_PATH), exist_ok=True)
        
        if not os.path.exists(cls.CACHE_PATH):
            # Create an empty cache
            default_cache = {
                "whistle_reports": [],
                "sms_alerts": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(cls.CACHE_PATH, 'w') as f:
                json.dump(default_cache, f, indent=2)
    
    @classmethod
    def _get_functions_config(cls):
        """Get Azure Functions configuration."""
        config = AzureClient.load_config()
        return config["functions"]
    
    @classmethod
    def submit_whistle_report(cls, report_type, details, location, images=None, callback=None):
        """
        Submit a Whistle report to Azure Functions for processing.
        
        Args:
            report_type (str): Type of report (e.g., "crime", "hazard")
            details (str): Report details
            location (dict): Location information (lat, lon)
            images (list, optional): List of image paths
            callback (callable, optional): Function to call with result
            
        Returns:
            If callback is None, this function will use the cache and return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        # Create the report
        report = {
            "id": str(uuid.uuid4()),
            "type": report_type,
            "details": details,
            "location": location,
            "images": images or [],
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "submitted"
        }
        
        if not callback:
            # Use local cache
            cls._cache_whistle_report(report)
            return report
        
        # Get Azure Functions configuration
        functions_config = cls._get_functions_config()
        base_url = functions_config["base_url"]
        api_key = functions_config["api_key"]
        
        # Build the URL for the Whistle report function
        url = f"{base_url}/api/SubmitWhistleReport?code={api_key}"
        headers = {"Content-Type": "application/json"}
        
        def on_success(req, result):
            # Update the report with the result
            report.update(result)
            
            # Cache the report
            cls._cache_whistle_report(report)
            
            # Call the callback with the result
            callback(report)
        
        def on_failure(req, result):
            print(f"Azure Functions Whistle report submission failed: {result}")
            # Update the report status
            report["status"] = "failed"
            report["error"] = str(result)
            
            # Cache the report
            cls._cache_whistle_report(report)
            
            # Call the callback with the report
            callback(report)
        
        def on_error(req, error):
            print(f"Azure Functions Whistle report submission error: {error}")
            # Update the report status
            report["status"] = "error"
            report["error"] = str(error)
            
            # Cache the report
            cls._cache_whistle_report(report)
            
            # Call the callback with the report
            callback(report)
        
        # Make the request
        AzureClient.make_request(
            url,
            method="POST",
            data=report,
            headers=headers,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error
        )
        
        return report
    
    @classmethod
    def _cache_whistle_report(cls, report):
        """Cache Whistle report for offline use."""
        cls._ensure_cache_exists()
        
        with open(cls.CACHE_PATH, 'r') as f:
            cache = json.load(f)
        
        # Check if this report already exists
        for i, r in enumerate(cache["whistle_reports"]):
            if r["id"] == report["id"]:
                # Update existing report
                cache["whistle_reports"][i] = report
                break
        else:
            # Add new report
            cache["whistle_reports"].append(report)
        
        cache["last_updated"] = datetime.datetime.now().isoformat()
        
        # Keep only the last 100 reports
        if len(cache["whistle_reports"]) > 100:
            cache["whistle_reports"] = cache["whistle_reports"][-100:]
        
        with open(cls.CACHE_PATH, 'w') as f:
            json.dump(cache, f, indent=2)
    
    @classmethod
    def get_whistle_reports(cls, limit=10, callback=None):
        """
        Get recent Whistle reports from Azure Functions.
        
        Args:
            limit (int): Maximum number of reports to return
            callback (callable, optional): Function to call with result
            
        Returns:
            If callback is None, this function will use the cache and return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        if not callback:
            # Use local cache
            cls._ensure_cache_exists()
            
            with open(cls.CACHE_PATH, 'r') as f:
                cache = json.load(f)
            
            # Sort by timestamp (newest first) and limit
            reports = cache["whistle_reports"]
            reports.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return reports[:limit]
        
        # Get Azure Functions configuration
        functions_config = cls._get_functions_config()
        base_url = functions_config["base_url"]
        api_key = functions_config["api_key"]
        
        # Build the URL for the Whistle reports function
        url = f"{base_url}/api/GetWhistleReports?code={api_key}&limit={limit}"
        
        def on_success(req, result):
            # Cache the reports
            for report in result:
                cls._cache_whistle_report(report)
            
            # Call the callback with the result
            callback(result)
        
        def on_failure(req, result):
            print(f"Azure Functions Whistle reports request failed: {result}")
            # Fall back to cache
            cls._ensure_cache_exists()
            
            with open(cls.CACHE_PATH, 'r') as f:
                cache = json.load(f)
            
            # Sort by timestamp (newest first) and limit
            reports = cache["whistle_reports"]
            reports.sort(key=lambda x: x["timestamp"], reverse=True)
            
            callback(reports[:limit])
        
        def on_error(req, error):
            print(f"Azure Functions Whistle reports request error: {error}")
            # Fall back to cache
            cls._ensure_cache_exists()
            
            with open(cls.CACHE_PATH, 'r') as f:
                cache = json.load(f)
            
            # Sort by timestamp (newest first) and limit
            reports = cache["whistle_reports"]
            reports.sort(key=lambda x: x["timestamp"], reverse=True)
            
            callback(reports[:limit])
        
        # Make the request
        AzureClient.make_request(
            url,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error
        )
    
    @classmethod
    def send_sms_alert(cls, phone_number, message, callback=None):
        """
        Send an SMS alert using Azure Communication Services via Azure Functions.
        
        Args:
            phone_number (str): Recipient phone number
            message (str): SMS message
            callback (callable, optional): Function to call with result
            
        Returns:
            If callback is None, this function will use the cache and return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        # Create the SMS alert
        sms_alert = {
            "id": str(uuid.uuid4()),
            "phone_number": phone_number,
            "message": message,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "pending"
        }
        
        if not callback:
            # Use local cache
            cls._cache_sms_alert(sms_alert)
            return sms_alert
        
        # Get Azure Functions configuration
        functions_config = cls._get_functions_config()
        base_url = functions_config["base_url"]
        api_key = functions_config["api_key"]
        
        # Build the URL for the SMS alert function
        url = f"{base_url}/api/SendSMSAlert?code={api_key}"
        headers = {"Content-Type": "application/json"}
        
        def on_success(req, result):
            # Update the alert with the result
            sms_alert.update(result)
            
            # Cache the alert
            cls._cache_sms_alert(sms_alert)
            
            # Call the callback with the result
            callback(sms_alert)
        
        def on_failure(req, result):
            print(f"Azure Functions SMS alert failed: {result}")
            # Update the alert status
            sms_alert["status"] = "failed"
            sms_alert["error"] = str(result)
            
            # Cache the alert
            cls._cache_sms_alert(sms_alert)
            
            # Call the callback with the alert
            callback(sms_alert)
        
        def on_error(req, error):
            print(f"Azure Functions SMS alert error: {error}")
            # Update the alert status
            sms_alert["status"] = "error"
            sms_alert["error"] = str(error)
            
            # Cache the alert
            cls._cache_sms_alert(sms_alert)
            
            # Call the callback with the alert
            callback(sms_alert)
        
        # Make the request
        AzureClient.make_request(
            url,
            method="POST",
            data=sms_alert,
            headers=headers,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error
        )
        
        return sms_alert
    
    @classmethod
    def _cache_sms_alert(cls, alert):
        """Cache SMS alert for offline use."""
        cls._ensure_cache_exists()
        
        with open(cls.CACHE_PATH, 'r') as f:
            cache = json.load(f)
        
        # Check if this alert already exists
        for i, a in enumerate(cache["sms_alerts"]):
            if a["id"] == alert["id"]:
                # Update existing alert
                cache["sms_alerts"][i] = alert
                break
        else:
            # Add new alert
            cache["sms_alerts"].append(alert)
        
        cache["last_updated"] = datetime.datetime.now().isoformat()
        
        # Keep only the last 100 alerts
        if len(cache["sms_alerts"]) > 100:
            cache["sms_alerts"] = cache["sms_alerts"][-100:]
        
        with open(cls.CACHE_PATH, 'w') as f:
            json.dump(cache, f, indent=2)
    
    @classmethod
    def notify_authorities(cls, emergency_type, details, location, callback=None):
        """
        Notify authorities about an emergency via Azure Functions.
        
        Args:
            emergency_type (str): Type of emergency
            details (str): Emergency details
            location (dict): Location information (lat, lon)
            callback (callable, optional): Function to call with result
            
        Returns:
            If callback is None, this function will use the cache and return immediately.
            Otherwise, it will make an async request and call the callback when done.
        """
        # Create the notification
        notification = {
            "id": str(uuid.uuid4()),
            "emergency_type": emergency_type,
            "details": details,
            "location": location,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "pending"
        }
        
        if not callback:
            # Simulate notification
            print(f"Authority Notification: {notification}")
            notification["status"] = "sent"
            return notification
        
        # Get Azure Functions configuration
        functions_config = cls._get_functions_config()
        base_url = functions_config["base_url"]
        api_key = functions_config["api_key"]
        
        # Build the URL for the authority notification function
        url = f"{base_url}/api/NotifyAuthorities?code={api_key}"
        headers = {"Content-Type": "application/json"}
        
        def on_success(req, result):
            # Update the notification with the result
            notification.update(result)
            
            # Call the callback with the result
            callback(notification)
        
        def on_failure(req, result):
            print(f"Azure Functions authority notification failed: {result}")
            # Update the notification status
            notification["status"] = "failed"
            notification["error"] = str(result)
            
            # Call the callback with the notification
            callback(notification)
        
        def on_error(req, error):
            print(f"Azure Functions authority notification error: {error}")
            # Update the notification status
            notification["status"] = "error"
            notification["error"] = str(error)
            
            # Call the callback with the notification
            callback(notification)
        
        # Make the request
        AzureClient.make_request(
            url,
            method="POST",
            data=notification,
            headers=headers,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error
        )
        
        return notification

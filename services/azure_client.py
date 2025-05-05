"""
Azure API Client for SafeWayAI

This module provides a base client for connecting to Azure services.
"""

import os
import json
import requests
import threading

class AzureClient:
    """Base client for Azure API services."""

    # Configuration file path
    CONFIG_PATH = os.path.join('config', 'azure_config.json')

    @classmethod
    def _ensure_config_exists(cls):
        """Ensure the Azure configuration file exists."""
        os.makedirs(os.path.dirname(cls.CONFIG_PATH), exist_ok=True)

        if not os.path.exists(cls.CONFIG_PATH):
            # Create a template configuration file
            default_config = {
                "subscription_key": "YOUR_SUBSCRIPTION_KEY",
                "region": "southafrica",
                "maps": {
                    "subscription_key": "YOUR_MAPS_KEY",
                    "base_url": "https://atlas.microsoft.com/",
                },
                "ai_services": {
                    "speech_key": "YOUR_SPEECH_KEY",
                    "speech_region": "southafrica",
                    "vision_key": "YOUR_VISION_KEY",
                    "vision_endpoint": "https://southafrica.api.cognitive.microsoft.com/"
                },
                "cosmos_db": {
                    "endpoint": "YOUR_COSMOS_DB_ENDPOINT",
                    "key": "YOUR_COSMOS_DB_KEY",
                    "database_id": "safewayai",
                    "container_id": "incidents"
                },
                "iot_hub": {
                    "connection_string": "YOUR_IOT_HUB_CONNECTION_STRING",
                    "device_id": "safewayai_mobile"
                },
                "functions": {
                    "base_url": "YOUR_AZURE_FUNCTIONS_URL",
                    "api_key": "YOUR_FUNCTIONS_API_KEY"
                }
            }

            with open(cls.CONFIG_PATH, 'w') as f:
                json.dump(default_config, f, indent=2)

    @classmethod
    def load_config(cls):
        """Load Azure configuration."""
        cls._ensure_config_exists()

        with open(cls.CONFIG_PATH, 'r') as f:
            return json.load(f)

    @classmethod
    def make_request(cls, url, method="GET", data=None, headers=None,
                    on_success=None, on_failure=None, on_error=None):
        """
        Make an asynchronous request to an Azure API.

        Args:
            url (str): The API endpoint URL
            method (str): HTTP method (GET, POST, etc.)
            data (dict): Request data for POST/PUT requests
            headers (dict): HTTP headers
            on_success (callable): Callback for successful response
            on_failure (callable): Callback for API failure (e.g., 404, 500)
            on_error (callable): Callback for request error (e.g., network error)

        Returns:
            Thread: The request thread
        """
        if headers is None:
            headers = {}

        # Convert data to JSON if it's a dict
        req_body = None
        if data:
            req_body = json.dumps(data)
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'

        # Define the request function to run in a thread
        def make_request_thread():
            try:
                # Make the request
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                elif method.upper() == "POST":
                    response = requests.post(url, data=req_body, headers=headers, timeout=10)
                elif method.upper() == "PUT":
                    response = requests.put(url, data=req_body, headers=headers, timeout=10)
                elif method.upper() == "DELETE":
                    response = requests.delete(url, headers=headers, timeout=10)
                else:
                    if on_error:
                        on_error(None, f"Unsupported method: {method}")
                    return

                # Check if the request was successful
                if response.status_code >= 200 and response.status_code < 300:
                    # Parse the response
                    try:
                        result = response.json()
                    except ValueError:
                        result = response.text

                    # Call the success callback
                    if on_success:
                        on_success(response, result)
                else:
                    # Call the failure callback
                    if on_failure:
                        try:
                            result = response.json()
                        except ValueError:
                            result = response.text
                        on_failure(response, result)
            except Exception as e:
                # Call the error callback
                if on_error:
                    on_error(None, str(e))

        # Start the request in a thread
        thread = threading.Thread(target=make_request_thread)
        thread.daemon = True
        thread.start()

        return thread

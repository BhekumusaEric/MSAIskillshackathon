"""
Azure Cosmos DB Client for SafeWayAI

This module provides a client for connecting to Azure Cosmos DB.
"""

import os
import json
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from services.azure_client import AzureClient

class CosmosDBClient:
    """Base client for Azure Cosmos DB."""

    def __init__(self):
        """Initialize the Cosmos DB client."""
        # Get configuration
        config = AzureClient.load_config()
        cosmos_config = config.get("cosmos_db", {})

        # Get connection details
        self.endpoint = cosmos_config.get("endpoint")
        self.key = cosmos_config.get("key")
        self.database_id = cosmos_config.get("database_id", "safewayai")

        # Initialize client
        self.client = None
        self.database = None
        self.containers = {}

        # Connect if credentials are available
        if self.endpoint and self.key:
            self.connect()

    def connect(self):
        """Connect to Azure Cosmos DB."""
        try:
            # Create the client
            self.client = CosmosClient(self.endpoint, self.key)

            # Create database if it doesn't exist
            self.database = self.client.create_database_if_not_exists(id=self.database_id)

            # Initialize containers
            self._init_containers()

            return True
        except Exception as e:
            print(f"Error connecting to Cosmos DB: {e}")
            return False

    def _init_containers(self):
        """Initialize containers."""
        # Define containers with their partition keys
        containers_config = [
            {"id": "users", "partition_key": PartitionKey(path="/id"), "priority": 1},
            {"id": "incidents", "partition_key": PartitionKey(path="/id"), "priority": 2},
            {"id": "reports", "partition_key": PartitionKey(path="/id"), "priority": 3},
            {"id": "settings", "partition_key": PartitionKey(path="/user_id"), "priority": 4}
        ]

        # Sort containers by priority (create most important ones first)
        containers_config.sort(key=lambda x: x["priority"])

        # Create containers if they don't exist
        for container_config in containers_config:
            container_id = container_config["id"]
            partition_key = container_config["partition_key"]

            try:
                # First try to get the container if it already exists
                try:
                    container = self.database.get_container_client(container_id)
                    self.containers[container_id] = container
                    print(f"Container {container_id} already exists")
                    continue
                except exceptions.CosmosResourceNotFoundError:
                    # Container doesn't exist, try to create it
                    pass

                # Use minimum throughput required by Cosmos DB
                # The free tier has a limit of 1000 RU/s total
                container = self.database.create_container_if_not_exists(
                    id=container_id,
                    partition_key=partition_key,
                    offer_throughput=400  # Minimum throughput required by Cosmos DB
                )
                self.containers[container_id] = container
                print(f"Container {container_id} created successfully")
            except exceptions.CosmosHttpResponseError as e:
                if "throughput limit" in str(e):
                    print(f"Warning: Could not create container {container_id} due to throughput limits. The application will use local cache for this container.")
                    # Create a mock container for local cache
                    self._create_mock_container(container_id)
                else:
                    print(f"Error creating container {container_id}: {e}")

    def _create_mock_container(self, container_id):
        """Create a mock container for local cache."""
        # Create cache directory if it doesn't exist
        cache_dir = os.path.join('data', 'cosmos_cache')
        os.makedirs(cache_dir, exist_ok=True)

        # Create cache file if it doesn't exist
        cache_path = os.path.join(cache_dir, f"{container_id}.json")
        if not os.path.exists(cache_path):
            with open(cache_path, 'w') as f:
                json.dump({
                    "items": [],
                    "last_updated": json.dumps({"$date": {"$numberLong": str(int(1000 * 1000))}})
                }, f, indent=2)

        print(f"Created mock container for {container_id} using local cache")

    def get_container(self, container_id):
        """Get a container by ID."""
        if not self.client or not self.database:
            if not self.connect():
                return None

        if container_id not in self.containers:
            try:
                container = self.database.get_container_client(container_id)
                self.containers[container_id] = container
                return container
            except exceptions.CosmosResourceNotFoundError:
                print(f"Container {container_id} not found")
                return None

        return self.containers[container_id]

    def is_connected(self):
        """Check if connected to Cosmos DB."""
        return self.client is not None and self.database is not None

# Singleton instance
cosmos_client = CosmosDBClient()

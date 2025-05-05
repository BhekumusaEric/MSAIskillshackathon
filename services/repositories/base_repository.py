"""
Base Repository for Azure Cosmos DB

This module provides a base repository for Azure Cosmos DB operations.
"""

import json
import datetime
import os
from azure.cosmos import exceptions
from services.cosmos_db_client import cosmos_client

class BaseRepository:
    """Base repository for Cosmos DB operations."""

    def __init__(self, container_id):
        """Initialize the repository."""
        self.container_id = container_id
        self.container = cosmos_client.get_container(container_id)

        # Path to the local cache for offline use
        self.cache_dir = os.path.join('data', 'cosmos_cache')
        self.cache_path = os.path.join(self.cache_dir, f"{container_id}.json")

        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)

        # Initialize cache if it doesn't exist
        if not os.path.exists(self.cache_path):
            with open(self.cache_path, 'w') as f:
                json.dump({
                    "items": [],
                    "last_updated": datetime.datetime.now().isoformat()
                }, f, indent=2)

        # If container is None, log a message but continue with local cache
        if self.container is None:
            print(f"Warning: Container {container_id} not available. Using local cache only.")
            # Try to create a mock container
            cosmos_client._create_mock_container(container_id)

    def get_item(self, item_id, partition_key=None):
        """
        Get an item by ID.

        Args:
            item_id (str): The ID of the item
            partition_key (str, optional): The partition key. Defaults to item_id.

        Returns:
            dict: The item, or None if not found
        """
        if partition_key is None:
            partition_key = item_id

        # Try to get from Cosmos DB
        if self.container:
            try:
                return self.container.read_item(item=item_id, partition_key=partition_key)
            except exceptions.CosmosResourceNotFoundError:
                pass
            except Exception as e:
                print(f"Error getting item {item_id}: {e}")

        # Fall back to cache
        return self._get_from_cache(item_id)

    def create_item(self, item):
        """
        Create a new item.

        Args:
            item (dict): The item to create

        Returns:
            dict: The created item
        """
        # Try to create in Cosmos DB
        if self.container:
            try:
                result = self.container.create_item(body=item)
                # Update cache
                self._update_cache(result)
                return result
            except Exception as e:
                print(f"Error creating item: {e}")

        # Fall back to cache
        self._update_cache(item)
        return item

    def update_item(self, item):
        """
        Update an existing item.

        Args:
            item (dict): The item to update

        Returns:
            dict: The updated item
        """
        # Try to update in Cosmos DB
        if self.container:
            try:
                result = self.container.replace_item(item=item["id"], body=item)
                # Update cache
                self._update_cache(result)
                return result
            except Exception as e:
                print(f"Error updating item: {e}")

        # Fall back to cache
        self._update_cache(item)
        return item

    def delete_item(self, item_id, partition_key=None):
        """
        Delete an item by ID.

        Args:
            item_id (str): The ID of the item
            partition_key (str, optional): The partition key. Defaults to item_id.

        Returns:
            bool: True if deleted, False otherwise
        """
        if partition_key is None:
            partition_key = item_id

        # Try to delete from Cosmos DB
        if self.container:
            try:
                self.container.delete_item(item=item_id, partition_key=partition_key)
                # Update cache
                self._remove_from_cache(item_id)
                return True
            except Exception as e:
                print(f"Error deleting item {item_id}: {e}")

        # Fall back to cache
        self._remove_from_cache(item_id)
        return True

    def query_items(self, query, parameters=None, partition_key=None):
        """
        Query items.

        Args:
            query (str): The query
            parameters (list, optional): Query parameters
            partition_key (str, optional): The partition key

        Returns:
            list: The query results
        """
        # Try to query Cosmos DB
        if self.container:
            try:
                if partition_key:
                    items = list(self.container.query_items(
                        query=query,
                        parameters=parameters,
                        partition_key=partition_key
                    ))
                else:
                    items = list(self.container.query_items(
                        query=query,
                        parameters=parameters,
                        enable_cross_partition_query=True
                    ))

                # Update cache with results
                for item in items:
                    self._update_cache(item)

                return items
            except Exception as e:
                print(f"Error querying items: {e}")

        # Fall back to cache
        return self._query_cache(query, parameters)

    def _get_from_cache(self, item_id):
        """Get an item from the cache."""
        try:
            with open(self.cache_path, 'r') as f:
                cache = json.load(f)

            for item in cache["items"]:
                if item.get("id") == item_id:
                    return item
        except Exception as e:
            print(f"Error reading from cache: {e}")

        return None

    def _update_cache(self, item):
        """Update an item in the cache."""
        try:
            with open(self.cache_path, 'r') as f:
                cache = json.load(f)

            # Remove existing item with same ID
            cache["items"] = [i for i in cache["items"] if i.get("id") != item.get("id")]

            # Add the new/updated item
            cache["items"].append(item)
            cache["last_updated"] = datetime.datetime.now().isoformat()

            with open(self.cache_path, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Error updating cache: {e}")

    def _remove_from_cache(self, item_id):
        """Remove an item from the cache."""
        try:
            with open(self.cache_path, 'r') as f:
                cache = json.load(f)

            # Remove item with matching ID
            cache["items"] = [i for i in cache["items"] if i.get("id") != item_id]
            cache["last_updated"] = datetime.datetime.now().isoformat()

            with open(self.cache_path, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Error removing from cache: {e}")

    def _query_cache(self, query, parameters=None):
        """
        Simple query implementation for cache.
        Note: This is a very basic implementation that only supports simple queries.
        """
        try:
            with open(self.cache_path, 'r') as f:
                cache = json.load(f)

            # Basic query parsing for simple WHERE clauses
            if "WHERE" in query.upper() and parameters:
                # Extract field and value from parameters
                filtered_items = []
                for item in cache["items"]:
                    matches = True
                    for param in parameters:
                        if param["name"].startswith("@"):
                            # Extract field name from query (very basic parsing)
                            field_parts = query.split(param["name"])
                            if len(field_parts) > 1:
                                field_expr = field_parts[0].split("WHERE")[-1].strip()
                                field_name = field_expr.split("=")[0].strip().split(".")[-1]

                                # Check if item matches the parameter
                                if field_name in item and item[field_name] != param["value"]:
                                    matches = False
                                    break

                    if matches:
                        filtered_items.append(item)

                return filtered_items

            # If no query parsing is possible, return all items
            return cache["items"]
        except Exception as e:
            print(f"Error querying cache: {e}")

        return []

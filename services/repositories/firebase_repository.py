"""
Base Repository for Firebase/Firestore

This module provides a base repository for Firebase/Firestore operations.
"""

import json
import datetime
import os
import uuid
from services.firebase_client import firebase_client

class FirebaseRepository:
    """Base repository for Firebase/Firestore operations."""
    
    def __init__(self, collection_id):
        """Initialize the repository."""
        self.collection_id = collection_id
        self.collection = firebase_client.get_collection(collection_id)
        
        # Path to the local cache for offline use
        self.cache_dir = os.path.join('data', 'firebase_cache')
        self.cache_path = os.path.join(self.cache_dir, f"{collection_id}.json")
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize cache if it doesn't exist
        if not os.path.exists(self.cache_path):
            with open(self.cache_path, 'w') as f:
                json.dump({
                    "documents": [],
                    "last_updated": datetime.datetime.now().isoformat()
                }, f, indent=2)
        
        # If using mock database, collection is the cache path
        self.is_mock = firebase_client.is_mock() or isinstance(self.collection, str)
    
    def get_document(self, doc_id):
        """
        Get a document by ID.
        
        Args:
            doc_id (str): The ID of the document
            
        Returns:
            dict: The document, or None if not found
        """
        # If using mock database, get from cache
        if self.is_mock:
            return self._get_from_cache(doc_id)
        
        # Try to get from Firestore
        try:
            doc_ref = self.collection.document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                # Get document data and add ID
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Update cache
                self._update_cache(data)
                
                return data
            else:
                return None
        except Exception as e:
            print(f"Error getting document {doc_id}: {e}")
            
            # Fall back to cache
            return self._get_from_cache(doc_id)
    
    def create_document(self, data, doc_id=None):
        """
        Create a new document.
        
        Args:
            data (dict): The document data
            doc_id (str, optional): The document ID. If not provided, a new ID will be generated.
            
        Returns:
            dict: The created document
        """
        # Generate ID if not provided
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        
        # Ensure data has ID
        data['id'] = doc_id
        
        # If using mock database, save to cache
        if self.is_mock:
            self._update_cache(data)
            return data
        
        # Try to create in Firestore
        try:
            doc_ref = self.collection.document(doc_id)
            doc_ref.set(data)
            
            # Update cache
            self._update_cache(data)
            
            return data
        except Exception as e:
            print(f"Error creating document: {e}")
            
            # Fall back to cache
            self._update_cache(data)
            return data
    
    def update_document(self, doc_id, data):
        """
        Update an existing document.
        
        Args:
            doc_id (str): The document ID
            data (dict): The document data to update
            
        Returns:
            dict: The updated document
        """
        # Ensure data has ID
        data['id'] = doc_id
        
        # If using mock database, update cache
        if self.is_mock:
            self._update_cache(data)
            return data
        
        # Try to update in Firestore
        try:
            doc_ref = self.collection.document(doc_id)
            doc_ref.update(data)
            
            # Get updated document
            updated_doc = doc_ref.get()
            updated_data = updated_doc.to_dict()
            updated_data['id'] = doc_id
            
            # Update cache
            self._update_cache(updated_data)
            
            return updated_data
        except Exception as e:
            print(f"Error updating document {doc_id}: {e}")
            
            # Fall back to cache
            self._update_cache(data)
            return data
    
    def delete_document(self, doc_id):
        """
        Delete a document by ID.
        
        Args:
            doc_id (str): The document ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        # If using mock database, remove from cache
        if self.is_mock:
            self._remove_from_cache(doc_id)
            return True
        
        # Try to delete from Firestore
        try:
            doc_ref = self.collection.document(doc_id)
            doc_ref.delete()
            
            # Remove from cache
            self._remove_from_cache(doc_id)
            
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            
            # Fall back to cache
            self._remove_from_cache(doc_id)
            return True
    
    def query_documents(self, field=None, operator=None, value=None):
        """
        Query documents.
        
        Args:
            field (str, optional): The field to query
            operator (str, optional): The operator to use (==, >, <, >=, <=, !=)
            value (any, optional): The value to compare against
            
        Returns:
            list: The query results
        """
        # If using mock database, query cache
        if self.is_mock:
            return self._query_cache(field, operator, value)
        
        # Try to query Firestore
        try:
            # Build query
            query = self.collection
            
            if field is not None and operator is not None and value is not None:
                query = query.where(field, operator, value)
            
            # Execute query
            docs = query.stream()
            
            # Process results
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
                
                # Update cache
                self._update_cache(data)
            
            return results
        except Exception as e:
            print(f"Error querying documents: {e}")
            
            # Fall back to cache
            return self._query_cache(field, operator, value)
    
    def _get_from_cache(self, doc_id):
        """Get a document from the cache."""
        try:
            with open(self.cache_path, 'r') as f:
                cache = json.load(f)
            
            for doc in cache["documents"]:
                if doc.get("id") == doc_id:
                    return doc
        except Exception as e:
            print(f"Error reading from cache: {e}")
        
        return None
    
    def _update_cache(self, data):
        """Update a document in the cache."""
        try:
            with open(self.cache_path, 'r') as f:
                cache = json.load(f)
            
            # Remove existing document with same ID
            cache["documents"] = [d for d in cache["documents"] if d.get("id") != data.get("id")]
            
            # Add the new/updated document
            cache["documents"].append(data)
            cache["last_updated"] = datetime.datetime.now().isoformat()
            
            with open(self.cache_path, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Error updating cache: {e}")
    
    def _remove_from_cache(self, doc_id):
        """Remove a document from the cache."""
        try:
            with open(self.cache_path, 'r') as f:
                cache = json.load(f)
            
            # Remove document with matching ID
            cache["documents"] = [d for d in cache["documents"] if d.get("id") != doc_id]
            cache["last_updated"] = datetime.datetime.now().isoformat()
            
            with open(self.cache_path, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Error removing from cache: {e}")
    
    def _query_cache(self, field=None, operator=None, value=None):
        """
        Query the cache.
        
        Args:
            field (str, optional): The field to query
            operator (str, optional): The operator to use (==, >, <, >=, <=, !=)
            value (any, optional): The value to compare against
            
        Returns:
            list: The query results
        """
        try:
            with open(self.cache_path, 'r') as f:
                cache = json.load(f)
            
            # If no query parameters, return all documents
            if field is None or operator is None or value is None:
                return cache["documents"]
            
            # Filter documents based on query
            results = []
            for doc in cache["documents"]:
                if field in doc:
                    doc_value = doc[field]
                    
                    # Compare based on operator
                    if operator == "==" and doc_value == value:
                        results.append(doc)
                    elif operator == ">" and doc_value > value:
                        results.append(doc)
                    elif operator == "<" and doc_value < value:
                        results.append(doc)
                    elif operator == ">=" and doc_value >= value:
                        results.append(doc)
                    elif operator == "<=" and doc_value <= value:
                        results.append(doc)
                    elif operator == "!=" and doc_value != value:
                        results.append(doc)
            
            return results
        except Exception as e:
            print(f"Error querying cache: {e}")
        
        return []

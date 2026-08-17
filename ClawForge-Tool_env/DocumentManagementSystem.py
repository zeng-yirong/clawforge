"""
Document Management System Environment API

A centralized environment for storing, organizing, and retrieving electronic documents
with access controls, versioning, and metadata management.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    # Documents
    "documents": {
        "doc_001": {
            "document_id": "doc_001",
            "title": "Q4 Financial Report",
            "content": "This is the Q4 financial report content with revenue analysis.",
            "creation_date": "2024-01-15T10:00:00",
            "last_modified_date": "2024-01-20T14:30:00",
            "version": 2,
            "status": "active",
            "owner_id": "user_001",
            "access_permission": "private"
        },
        "doc_002": {
            "document_id": "doc_002",
            "title": "Project Alpha Proposal",
            "content": "Project Alpha aims to improve customer engagement through AI.",
            "creation_date": "2024-02-01T09:00:00",
            "last_modified_date": "2024-02-05T11:00:00",
            "version": 1,
            "status": "active",
            "owner_id": "user_002",
            "access_permission": "department"
        },
        "doc_003": {
            "document_id": "doc_003",
            "title": "HR Policy Manual",
            "content": "Company HR policies and procedures for all employees.",
            "creation_date": "2023-06-10T08:00:00",
            "last_modified_date": "2023-12-01T16:00:00",
            "version": 5,
            "status": "archived",
            "owner_id": "user_003",
            "access_permission": "public"
        },
        "doc_004": {
            "document_id": "doc_004",
            "title": "Deleted Draft",
            "content": "This document was deleted.",
            "creation_date": "2024-01-01T12:00:00",
            "last_modified_date": "2024-01-02T12:00:00",
            "version": 1,
            "status": "deleted",
            "owner_id": "user_001",
            "access_permission": "private"
        }
    },
    
    # Users
    "users": {
        "user_001": {
            "_id": "user_001",
            "name": "Alice Johnson",
            "role": "manager",
            "department": "Finance"
        },
        "user_002": {
            "_id": "user_002",
            "name": "Bob Smith",
            "role": "analyst",
            "department": "Engineering"
        },
        "user_003": {
            "_id": "user_003",
            "name": "Carol Williams",
            "role": "admin",
            "department": "HR"
        },
        "user_004": {
            "_id": "user_004",
            "name": "David Brown",
            "role": "viewer",
            "department": "Marketing"
        }
    },
    
    # Access Control Entries
    "access_control": {
        "doc_001": {
            "user_001": {"read": True, "write": True, "delete": True},
            "user_002": {"read": True, "write": False, "delete": False},
            "user_003": {"read": True, "write": True, "delete": False}
        },
        "doc_002": {
            "user_002": {"read": True, "write": True, "delete": True},
            "user_001": {"read": True, "write": False, "delete": False},
            "user_004": {"read": True, "write": False, "delete": False}
        },
        "doc_003": {
            "user_003": {"read": True, "write": True, "delete": True},
            "user_001": {"read": True, "write": False, "delete": False},
            "user_002": {"read": True, "write": False, "delete": False}
        },
        "doc_004": {
            "user_001": {"read": True, "write": True, "delete": True}
        }
    },
    
    # Document Versions
    "document_versions": {
        "doc_001": [
            {
                "version_id": "ver_001_1",
                "document_id": "doc_001",
                "version_number": 1,
                "content_snapshot": "Initial Q4 financial report draft.",
                "timestamp": "2024-01-15T10:00:00",
                "modified_by": "user_001"
            },
            {
                "version_id": "ver_001_2",
                "document_id": "doc_001",
                "version_number": 2,
                "content_snapshot": "This is the Q4 financial report content with revenue analysis.",
                "timestamp": "2024-01-20T14:30:00",
                "modified_by": "user_001"
            }
        ],
        "doc_002": [
            {
                "version_id": "ver_002_1",
                "document_id": "doc_002",
                "version_number": 1,
                "content_snapshot": "Project Alpha aims to improve customer engagement through AI.",
                "timestamp": "2024-02-01T09:00:00",
                "modified_by": "user_002"
            }
        ],
        "doc_003": [
            {
                "version_id": "ver_003_1",
                "document_id": "doc_003",
                "version_number": 1,
                "content_snapshot": "Initial HR policy document.",
                "timestamp": "2023-06-10T08:00:00",
                "modified_by": "user_003"
            },
            {
                "version_id": "ver_003_5",
                "document_id": "doc_003",
                "version_number": 5,
                "content_snapshot": "Company HR policies and procedures for all employees.",
                "timestamp": "2023-12-01T16:00:00",
                "modified_by": "user_003"
            }
        ],
        "doc_004": [
            {
                "version_id": "ver_004_1",
                "document_id": "doc_004",
                "version_number": 1,
                "content_snapshot": "This document was deleted.",
                "timestamp": "2024-01-01T12:00:00",
                "modified_by": "user_001"
            }
        ]
    },
    
    # Current user context
    "current_user_id": "user_001",
    
    # ID counters
    "next_doc_id": 5,
    "next_version_id": 10
}


class DocumentManagementSystem:
    """
    A document management system environment for storing, organizing, and retrieving
    electronic documents with access controls, versioning, and metadata management.
    
    This environment supports operations like creation, retrieval, update, and deletion
    of documents in a structured and auditable manner.
    """
    
    def __init__(self) -> None:
        """
        Initialize the DocumentManagementSystem environment.
        
        Declares all state attributes with type hints and sets up the API description.
        """
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.access_control: Dict[str, Dict[str, Dict[str, bool]]] = {}
        self.document_versions: Dict[str, List[Dict[str, Any]]] = {}
        self.current_user_id: str = ""
        self.next_doc_id: int = 1
        self.next_version_id: int = 1
        
        self._api_description: str = (
            "A document management system for storing, organizing, and retrieving "
            "electronic documents with access controls and versioning."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a consistent ISO format timestamp string.
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _generate_doc_id(self) -> str:
        """
        Generate a unique document ID.
        
        Returns:
            str: A unique document identifier.
        """
        doc_id = f"doc_{self.next_doc_id:03d}"
        self.next_doc_id += 1
        return doc_id
    
    def _generate_version_id(self, doc_id: str, version_number: int) -> str:
        """
        Generate a unique version ID.
        
        Args:
            doc_id: The document ID.
            version_number: The version number.
            
        Returns:
            str: A unique version identifier.
        """
        doc_num = doc_id.split('_')[1] if '_' in doc_id else doc_id
        ver_id = f"ver_{doc_num}_{version_number}"
        self.next_version_id += 1
        return ver_id
    
    def _has_permission(self, document_id: str, user_id: str, permission: str) -> bool:
        """
        Check if a user has a specific permission on a document.
        
        Args:
            document_id: The unique identifier of the document.
            user_id: The ID of the user to check.
            permission: The permission to check (read, write, delete).
            
        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        if document_id not in self.access_control:
            return False
        
        if user_id not in self.access_control[document_id]:
            # Check if document is public
            if document_id in self.documents:
                doc = self.documents[document_id]
                if doc.get("access_permission") == "public" and permission == "read":
                    return True
            return False
        
        return self.access_control[document_id][user_id].get(permission, False)
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        If a key is not present in the scenario, falls back to DEFAULT_STATE using deepcopy.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for handling long context scenarios (not used currently).
        """
        if not scenario:
            scenario = {}
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
    
    def get_env_state(self) -> Dict[str, Any]:
        """
        Get the current state of the environment.
        
        Returns a dictionary containing all internal state variables of the
        document management system including documents, users, access control
        entries, document versions, and current user context.
        
        Returns:
            Dict[str, Any]: A dictionary with keys:
                - documents: All documents in the system
                - users: All user records
                - access_control: Access control entries for all documents
                - document_versions: Version history for all documents
                - current_user_id: The ID of the currently active user
                - next_doc_id: Counter for generating document IDs
                - next_version_id: Counter for generating version IDs
        """
        return {
            "documents": deepcopy(self.documents),
            "users": deepcopy(self.users),
            "access_control": deepcopy(self.access_control),
            "document_versions": deepcopy(self.document_versions),
            "current_user_id": self.current_user_id,
            "next_doc_id": self.next_doc_id,
            "next_version_id": self.next_version_id
        }
    
    # ==================== Query Operations ====================
    
    def get_document_by_id(
        self, 
        document_id: str, 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve a document's metadata and content by document_id.
        
        Only returns the document if status is "active" and the requester has read permission.
        
        Args:
            document_id: The unique identifier of the document to retrieve.
            user_id: The ID of the user requesting the document. 
                     Defaults to current_user_id if not provided.
        
        Returns:
            Dict[str, Any]: The document data if found and accessible, 
                           or an error dictionary if not found, not active, 
                           or user lacks read permission.
        """
        user_id = user_id or self.current_user_id
        
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        document = self.documents[document_id]
        
        if document["status"] != "active":
            return {"error": f"Document '{document_id}' is not active (status: {document['status']})"}
        
        if not self._has_permission(document_id, user_id, "read"):
            return {"error": f"User '{user_id}' does not have read permission for document '{document_id}'"}
        
        return deepcopy(document)
    
    def list_active_documents(self) -> Dict[str, Any]:
        """
        List all documents in the system with status "active".
        
        Returns:
            Dict[str, Any]: A dictionary containing a list of active documents
                           with their basic metadata.
        """
        active_docs = []
        for doc_id, doc in self.documents.items():
            if doc["status"] == "active":
                active_docs.append({
                    "document_id": doc["document_id"],
                    "title": doc["title"],
                    "owner_id": doc["owner_id"],
                    "version": doc["version"],
                    "last_modified_date": doc["last_modified_date"]
                })
        
        return {"active_documents": active_docs, "count": len(active_docs)}
    
    def check_document_status(self, document_id: str) -> Dict[str, Any]:
        """
        Return the current status of a document.
        
        Args:
            document_id: The unique identifier of the document.
        
        Returns:
            Dict[str, Any]: The document's status (active, archived, deleted)
                           or an error if document not found.
        """
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        return {
            "document_id": document_id,
            "status": self.documents[document_id]["status"]
        }
    
    def get_document_permissions(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve the list of users and their access permissions for a document.
        
        Args:
            document_id: The unique identifier of the document.
        
        Returns:
            Dict[str, Any]: A dictionary containing user permissions for the document
                           or an error if document not found.
        """
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        permissions = self.access_control.get(document_id, {})
        
        return {
            "document_id": document_id,
            "permissions": deepcopy(permissions)
        }
    
    def check_user_access(
        self, 
        document_id: str, 
        user_id: str, 
        permission: str
    ) -> Dict[str, Any]:
        """
        Determine whether a specific user has a given permission on a document.
        
        Args:
            document_id: The unique identifier of the document.
            user_id: The ID of the user to check.
            permission: The permission to check (read, write, delete).
        
        Returns:
            Dict[str, Any]: A dictionary indicating whether the user has the permission.
        """
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        if user_id not in self.users:
            return {"error": f"User with ID '{user_id}' not found"}
        
        if permission not in ["read", "write", "delete"]:
            return {"error": f"Invalid permission type: '{permission}'. Must be 'read', 'write', or 'delete'"}
        
        has_access = self._has_permission(document_id, user_id, permission)
        
        return {
            "document_id": document_id,
            "user_id": user_id,
            "permission": permission,
            "has_access": has_access
        }
    
    def get_document_version_history(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve the version history of a document.
        
        Args:
            document_id: The unique identifier of the document.
        
        Returns:
            Dict[str, Any]: The version history including version numbers, 
                           timestamps, and modifiers, or an error if not found.
        """
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        versions = self.document_versions.get(document_id, [])
        
        return {
            "document_id": document_id,
            "version_history": deepcopy(versions),
            "total_versions": len(versions)
        }
    
    def get_document_current_version(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve the current (latest) version metadata and snapshot of a document.
        
        Args:
            document_id: The unique identifier of the document.
        
        Returns:
            Dict[str, Any]: The current version data or an error if not found.
        """
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        versions = self.document_versions.get(document_id, [])
        
        if not versions:
            return {"error": f"No version history found for document '{document_id}'"}
        
        current_version = max(versions, key=lambda v: v["version_number"])
        
        return {
            "document_id": document_id,
            "current_version": deepcopy(current_version)
        }
    
    def get_document_content(
        self, 
        document_id: str, 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve only the content of a document if it is active and accessible.
        
        Args:
            document_id: The unique identifier of the document.
            user_id: The ID of the user requesting the content.
                     Defaults to current_user_id if not provided.
        
        Returns:
            Dict[str, Any]: The document content or an error dictionary.
        """
        user_id = user_id or self.current_user_id
        
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        document = self.documents[document_id]
        
        if document["status"] != "active":
            return {"error": f"Document '{document_id}' is not active (status: {document['status']})"}
        
        if not self._has_permission(document_id, user_id, "read"):
            return {"error": f"User '{user_id}' does not have read permission for document '{document_id}'"}
        
        return {
            "document_id": document_id,
            "title": document["title"],
            "content": document["content"]
        }
    
    def search_documents_by_title(self, title_query: str) -> Dict[str, Any]:
        """
        Search for documents by title with case-insensitive matching.
        
        Args:
            title_query: The search string to match against document titles.
        
        Returns:
            Dict[str, Any]: A list of matching documents with basic metadata.
        """
        if not title_query:
            return {"error": "Search query cannot be empty"}
        
        matching_docs = []
        query_lower = title_query.lower()
        
        for doc_id, doc in self.documents.items():
            if query_lower in doc["title"].lower():
                matching_docs.append({
                    "document_id": doc["document_id"],
                    "title": doc["title"],
                    "status": doc["status"],
                    "owner_id": doc["owner_id"]
                })
        
        return {
            "query": title_query,
            "results": matching_docs,
            "count": len(matching_docs)
        }
    
    def list_documents_by_owner(self, owner_id: str) -> Dict[str, Any]:
        """
        List all documents owned by a specific user.
        
        Args:
            owner_id: The ID of the document owner.
        
        Returns:
            Dict[str, Any]: A list of documents owned by the user.
        """
        if owner_id not in self.users:
            return {"error": f"User with ID '{owner_id}' not found"}
        
        owned_docs = []
        for doc_id, doc in self.documents.items():
            if doc["owner_id"] == owner_id:
                owned_docs.append({
                    "document_id": doc["document_id"],
                    "title": doc["title"],
                    "status": doc["status"],
                    "version": doc["version"],
                    "last_modified_date": doc["last_modified_date"]
                })
        
        return {
            "owner_id": owner_id,
            "documents": owned_docs,
            "count": len(owned_docs)
        }
    
    # ==================== State Change Operations ====================
    
    def create_document(
        self,
        title: str,
        content: str,
        owner_id: Optional[str] = None,
        access_permission: str = "private"
    ) -> Dict[str, Any]:
        """
        Create a new document with initial content and metadata.
        
        Assigns a unique document_id and creates its first version.
        
        Args:
            title: The title of the new document.
            content: The initial content of the document.
            owner_id: The ID of the document owner. Defaults to current_user_id.
            access_permission: The access level (private, department, public).
        
        Returns:
            Dict[str, Any]: The created document data or an error dictionary.
        """
        owner_id = owner_id or self.current_user_id
        
        if not title:
            return {"error": "Document title cannot be empty"}
        
        if not content:
            return {"error": "Document content cannot be empty"}
        
        if owner_id not in self.users:
            return {"error": f"Owner user '{owner_id}' not found"}
        
        if access_permission not in ["private", "department", "public"]:
            return {"error": f"Invalid access_permission: '{access_permission}'"}
        
        document_id = self._generate_doc_id()
        timestamp = self._timestamp()
        
        new_document = {
            "document_id": document_id,
            "title": title,
            "content": content,
            "creation_date": timestamp,
            "last_modified_date": timestamp,
            "version": 1,
            "status": "active",
            "owner_id": owner_id,
            "access_permission": access_permission
        }
        
        self.documents[document_id] = new_document
        
        # Create first version
        version_id = self._generate_version_id(document_id, 1)
        first_version = {
            "version_id": version_id,
            "document_id": document_id,
            "version_number": 1,
            "content_snapshot": content,
            "timestamp": timestamp,
            "modified_by": owner_id
        }
        
        self.document_versions[document_id] = [first_version]
        
        # Set owner permissions
        self.access_control[document_id] = {
            owner_id: {"read": True, "write": True, "delete": True}
        }
        
        return {
            "success": True,
            "message": "Document created successfully",
            "document": deepcopy(new_document)
        }
    
    def update_document(
        self,
        document_id: str,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify a document's content or metadata.
        
        Increments version number and creates a new version snapshot.
        
        Args:
            document_id: The unique identifier of the document to update.
            user_id: The ID of the user making the update. Defaults to current_user_id.
            title: The new title (optional).
            content: The new content (optional).
        
        Returns:
            Dict[str, Any]: The updated document data or an error dictionary.
        """
        user_id = user_id or self.current_user_id
        
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        document = self.documents[document_id]
        
        if document["status"] != "active":
            return {"error": f"Cannot update document with status '{document['status']}'"}
        
        if not self._has_permission(document_id, user_id, "write"):
            return {"error": f"User '{user_id}' does not have write permission for document '{document_id}'"}
        
        if title is None and content is None:
            return {"error": "At least one of 'title' or 'content' must be provided"}
        
        timestamp = self._timestamp()
        
        if title is not None:
            document["title"] = title
        
        if content is not None:
            document["content"] = content
        
        document["version"] += 1
        document["last_modified_date"] = timestamp
        
        # Create new version
        version_id = self._generate_version_id(document_id, document["version"])
        new_version = {
            "version_id": version_id,
            "document_id": document_id,
            "version_number": document["version"],
            "content_snapshot": document["content"],
            "timestamp": timestamp,
            "modified_by": user_id
        }
        
        self.document_versions[document_id].append(new_version)
        
        return {
            "success": True,
            "message": "Document updated successfully",
            "document": deepcopy(document)
        }
    
    def delete_document(
        self,
        document_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark a document as "deleted" (soft delete).
        
        After deletion, the document can no longer be retrieved in normal queries.
        
        Args:
            document_id: The unique identifier of the document to delete.
            user_id: The ID of the user performing the deletion. Defaults to current_user_id.
        
        Returns:
            Dict[str, Any]: Success confirmation or an error dictionary.
        """
        user_id = user_id or self.current_user_id
        
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        document = self.documents[document_id]
        
        if document["status"] == "deleted":
            return {"error": f"Document '{document_id}' is already deleted"}
        
        if not self._has_permission(document_id, user_id, "delete"):
            return {"error": f"User '{user_id}' does not have delete permission for document '{document_id}'"}
        
        document["status"] = "deleted"
        document["last_modified_date"] = self._timestamp()
        
        return {
            "success": True,
            "message": f"Document '{document_id}' has been deleted",
            "document_id": document_id
        }
    
    def restore_document(
        self,
        document_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Restore a deleted or archived document to "active" status.
        
        Args:
            document_id: The unique identifier of the document to restore.
            user_id: The ID of the user performing the restoration. Defaults to current_user_id.
        
        Returns:
            Dict[str, Any]: Success confirmation or an error dictionary.
        """
        user_id = user_id or self.current_user_id
        
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        document = self.documents[document_id]
        
        if document["status"] == "active":
            return {"error": f"Document '{document_id}' is already active"}
        
        if not self._has_permission(document_id, user_id, "write"):
            return {"error": f"User '{user_id}' does not have write permission for document '{document_id}'"}
        
        document["status"] = "active"
        document["last_modified_date"] = self._timestamp()
        
        return {
            "success": True,
            "message": f"Document '{document_id}' has been restored to active status",
            "document": deepcopy(document)
        }
    
    def set_document_permissions(
        self,
        document_id: str,
        target_user_id: str,
        read: bool = False,
        write: bool = False,
        delete: bool = False,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Define or update access permissions for a user on a specific document.
        
        Args:
            document_id: The unique identifier of the document.
            target_user_id: The ID of the user to grant permissions to.
            read: Whether to grant read permission.
            write: Whether to grant write permission.
            delete: Whether to grant delete permission.
            user_id: The ID of the user setting permissions. Defaults to current_user_id.
        
        Returns:
            Dict[str, Any]: Success confirmation or an error dictionary.
        """
        user_id = user_id or self.current_user_id
        
        if document_id not in self.documents:
            return {"error": f"Document with ID '{document_id}' not found"}
        
        if target_user_id not in self.users:
            return {"error": f"Target user '{target_user_id}' not found"}
        
        document = self.documents[document_id]
        if document["owner_id"] != user_id and not self._has_permission(document_id, user_id, "delete"):
            return {"error": f"User '{user_id}' is not authorized to modify permissions for document '{document_id}'"}
        
        if document_id not in self.access_control:
            self.access_control[document_id] = {}
        
        self.access_control[document_id][target_user_id] = {
            "read": read,
            "write": write,
            "delete": delete
        }
        
        return {
            "success": True,
            "message": f"Permissions updated for user '{target_user_id}' on document '{document_id}'",
            "permissions": {"read": read, "write": write, "delete": delete}
        }
    
    def revoke_user_access(
        self,
        document_id: str,
        target_user_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Remove a user's access permissions to a document.
        
        Args:
            document_id: The document identifier
            target_user_id: The user whose access is being revoked
            user_id: The user performing the action (must be owner)
            
        Returns:
            Dict containing success status and message
        """
        user_id = user_id or self.current_user_id
        
        if document_id not in self.documents:
            return {"error": f"Document '{document_id}' not found"}
        
        doc = self.documents[document_id]
        if doc["owner_id"] != user_id:
            return {"error": "Only the document owner can revoke access permissions"}
        
        if document_id not in self.access_control:
            return {"error": f"No access control entries found for document '{document_id}'"}
        
        if target_user_id not in self.access_control[document_id]:
            return {"error": f"User '{target_user_id}' has no access permissions for document '{document_id}'"}
        
        del self.access_control[document_id][target_user_id]
        
        if not self.access_control[document_id]:
            del self.access_control[document_id]
        
        return {
            "success": True,
            "message": f"Access revoked for user '{target_user_id}' on document '{document_id}'"
        }
    
    def list_document_permissions(
        self,
        document_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all access permissions for a document.
        
        Args:
            document_id: The document identifier
            user_id: The user requesting the permissions list (must be owner)
            
        Returns:
            Dict containing permissions or error
        """
        user_id = user_id or self.current_user_id
        
        if document_id not in self.documents:
            return {"error": f"Document '{document_id}' not found"}
        
        doc = self.documents[document_id]
        if doc["owner_id"] != user_id:
            return {"error": "Only the document owner can view access permissions"}
        
        permissions = self.access_control.get(document_id, {})
        
        return {
            "success": True,
            "document_id": document_id,
            "owner_id": doc["owner_id"],
            "permissions": permissions
        }
    
    def get_user_documents(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get all documents owned by or accessible to a user.
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dict containing owned and accessible documents
        """
        if user_id not in self.users:
            return {"error": f"User '{user_id}' not found"}
            
        owned = []
        accessible = []
        
        for doc_id, doc in self.documents.items():
            if doc["owner_id"] == user_id:
                owned.append({
                    "document_id": doc_id,
                    "title": doc["title"],
                    "creation_date": doc["creation_date"],
                    "last_modified_date": doc["last_modified_date"]
                })
            elif doc_id in self.access_control:
                if user_id in self.access_control[doc_id]:
                    perms = self.access_control[doc_id][user_id]
                    if perms.get("read", False):
                        accessible.append({
                            "document_id": doc_id,
                            "title": doc["title"],
                            "owner_id": doc["owner_id"],
                            "permissions": perms
                        })
        
        return {
            "success": True,
            "user_id": user_id,
            "owned_documents": owned,
            "accessible_documents": accessible
        }


__TEST_CASES__ = [
    {
        "name": "test_create_document",
        "setup": lambda: (env := DocumentManagementSystem(), env._load_scenario(DEFAULT_STATE), env)[-1],
        "action": lambda env: env.create_document("Test Doc", "Content", "user_001", "private"),
        "expected_keys": ["success", "message", "document"],
        "expected_values": {"success": True, "message": "Document created successfully"}
    },
    {
        "name": "test_revoke_user_access_error",
        "setup": lambda: (env := DocumentManagementSystem(), env._load_scenario(DEFAULT_STATE), env)[-1],
        "action": lambda env: env.revoke_user_access("doc_001", "user_002", "user_002"),
        "expected_keys": ["error"],
        "expected_values": {"error": "Only the document owner can revoke access permissions"}
    },
    {
        "name": "test_list_document_permissions_error",
        "setup": lambda: (env := DocumentManagementSystem(), env._load_scenario(DEFAULT_STATE), env)[-1],
        "action": lambda env: env.list_document_permissions("doc_001", "user_002"),
        "expected_keys": ["error"],
        "expected_values": {"error": "Only the document owner can view access permissions"}
    },
    {
        "name": "test_get_user_documents",
        "setup": lambda: (env := DocumentManagementSystem(), env._load_scenario(DEFAULT_STATE), env)[-1],
        "action": lambda env: env.get_user_documents("user_002"),
        "expected_keys": ["success", "user_id", "owned_documents", "accessible_documents"],
        "expected_values": {"success": True, "user_id": "user_002"}
    }
]
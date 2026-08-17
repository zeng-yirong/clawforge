"""
Web Content Management System (CMS) Environment API

A stateful environment for creating, managing, and delivering digital content
for websites and online platforms. Supports CRUD operations, versioning,
and publishing workflows for embeds, pages, media assets, and users.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
import uuid

DEFAULT_STATE: Dict[str, Any] = {
    "embeds": {
        "promo-banner-2024": {
            "slug": "promo-banner-2024",
            "title": "Summer Sale Banner",
            "content": "<div class='promo'>50% Off Summer Sale!</div>",
            "type": "banner",
            "status": "published",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-20T14:30:00",
            "version": 3,
            "metadata": {"theme": "summer", "priority": "high"}
        },
        "video-intro": {
            "slug": "video-intro",
            "title": "Welcome Video",
            "content": "<video src='/media/welcome.mp4'></video>",
            "type": "video",
            "status": "draft",
            "created_at": "2024-02-01T09:00:00",
            "updated_at": "2024-02-01T09:00:00",
            "version": 1,
            "metadata": {"duration": "120s", "autoplay": False}
        },
        "contact-form": {
            "slug": "contact-form",
            "title": "Contact Us Form",
            "content": "<form id='contact'>...</form>",
            "type": "form",
            "status": "published",
            "created_at": "2024-01-10T08:00:00",
            "updated_at": "2024-03-05T11:20:00",
            "version": 5,
            "metadata": {"fields": ["name", "email", "message"]}
        },
        "deleted-widget": {
            "slug": "deleted-widget",
            "title": "Old Widget",
            "content": "<div>deprecated</div>",
            "type": "widget",
            "status": "deleted",
            "created_at": "2023-06-01T10:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "version": 2,
            "metadata": {}
        }
    },
    "embed_versions": {
        "promo-banner-2024": [
            {"version": 1, "content": "<div>Initial Banner</div>", "timestamp": "2024-01-15T10:00:00"},
            {"version": 2, "content": "<div>Updated Banner</div>", "timestamp": "2024-01-18T12:00:00"},
            {"version": 3, "content": "<div class='promo'>50% Off Summer Sale!</div>", "timestamp": "2024-01-20T14:30:00"}
        ],
        "video-intro": [
            {"version": 1, "content": "<video src='/media/welcome.mp4'></video>", "timestamp": "2024-02-01T09:00:00"}
        ],
        "contact-form": [
            {"version": 1, "content": "<form>v1</form>", "timestamp": "2024-01-10T08:00:00"},
            {"version": 5, "content": "<form id='contact'>...</form>", "timestamp": "2024-03-05T11:20:00"}
        ],
        "deleted-widget": [
            {"version": 1, "content": "<div>widget v1</div>", "timestamp": "2023-06-01T10:00:00"},
            {"version": 2, "content": "<div>deprecated</div>", "timestamp": "2024-01-01T00:00:00"}
        ]
    },
    "pages": {
        "page-001": {
            "page_id": "page-001",
            "title": "Home Page",
            "slug": "home",
            "content_body": "Welcome to our site! {{embed:promo-banner-2024}} {{embed:contact-form}}",
            "status": "published",
            "author_id": "user-001",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-02-15T10:00:00",
            "categories": []
        },
        "page-002": {
            "page_id": "page-002",
            "title": "About Us",
            "slug": "about",
            "content_body": "Learn about our company. {{embed:video-intro}}",
            "status": "draft",
            "author_id": "user-001",
            "created_at": "2024-02-01T00:00:00",
            "updated_at": "2024-02-01T00:00:00",
            "categories": []
        },
        "page-003": {
            "page_id": "page-003",
            "title": "Contact",
            "slug": "contact",
            "content_body": "Get in touch with us. {{embed:contact-form}}",
            "status": "published",
            "author_id": "user-002",
            "created_at": "2024-01-20T00:00:00",
            "updated_at": "2024-03-01T00:00:00",
            "categories": []
        }
    },
    "media_assets": {
        "asset-001": {
            "asset_id": "asset-001",
            "file_name": "logo.png",
            "url": "/media/images/logo.png",
            "file_size": 25600,
            "media_type": "image/png",
            "upload_date": "2024-01-01T00:00:00",
            "uploader_id": "user-001",
            "type": "image",
            "name": "logo.png",
            "uploaded_at": "2024-01-01T00:00:00",
            "uploaded_by": "user-001",
            "metadata": {}
        },
        "asset-002": {
            "asset_id": "asset-002",
            "file_name": "welcome.mp4",
            "url": "/media/videos/welcome.mp4",
            "file_size": 15728640,
            "media_type": "video/mp4",
            "upload_date": "2024-02-01T00:00:00",
            "uploader_id": "user-002",
            "type": "video",
            "name": "welcome.mp4",
            "uploaded_at": "2024-02-01T00:00:00",
            "uploaded_by": "user-002",
            "metadata": {}
        },
        "asset-003": {
            "asset_id": "asset-003",
            "file_name": "brochure.pdf",
            "url": "/media/docs/brochure.pdf",
            "file_size": 1048576,
            "media_type": "application/pdf",
            "upload_date": "2024-01-15T00:00:00",
            "uploader_id": "user-001",
            "type": "document",
            "name": "brochure.pdf",
            "uploaded_at": "2024-01-15T00:00:00",
            "uploaded_by": "user-001",
            "metadata": {}
        }
    },
    "categories": {
        "cat-001": {
            "id": "cat-001",
            "name": "News",
            "slug": "news",
            "parent_id": None,
            "description": "News articles",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        },
        "cat-002": {
            "id": "cat-002",
            "name": "Blog",
            "slug": "blog",
            "parent_id": None,
            "description": "Blog posts",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
    },
    "users": {
        "user-001": {
            "_id": "user-001",
            "username": "admin_john",
            "role": "admin",
            "permissions": ["create_embed", "edit_embed", "publish_embed", "delete_embed", "create_page", "edit_page", "publish_page", "delete_page", "upload_media", "view_media", "delete_media", "manage_users", "manage_categories"],
            "last_login": "2024-03-10T08:00:00"
        },
        "user-002": {
            "_id": "user-002",
            "username": "editor_jane",
            "role": "editor",
            "permissions": ["create_embed", "edit_embed", "publish_embed", "create_page", "edit_page", "publish_page", "upload_media", "view_media", "manage_categories"],
            "last_login": "2024-03-09T14:30:00"
        },
        "user-003": {
            "_id": "user-003",
            "username": "viewer_bob",
            "role": "viewer",
            "permissions": ["view_content", "view_media"],
            "last_login": "2024-03-08T10:00:00"
        }
    },
    "current_user_id": "user-001"
}


class WebContentManagementSystem:
    """
    Web Content Management System (CMS) Environment API.
    
    A stateful environment for managing digital content including embeds, pages,
    media assets, and users. Supports CRUD operations, versioning, and publishing
    workflows with role-based access control.
    """
    
    def __init__(self) -> None:
        """
        Initialize the CMS environment with all state attributes.
        
        Sets up empty state containers for embeds, pages, media assets, users,
        categories, and related tracking structures. State is populated via _load_scenario.
        
        Returns:
            None
        """
        self.embeds: Dict[str, Dict[str, Any]] = {}
        self.embed_versions: Dict[str, List[Dict[str, Any]]] = {}
        self.pages: Dict[str, Dict[str, Any]] = {}
        self.media_assets: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.current_user_id: str = ""
        
        self._api_description = "A Web CMS for creating, managing, and publishing digital content including embeds, pages, and media assets."
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state data for the environment.
            long_context: Flag for extended context scenarios (unused in base implementation).
        
        Returns:
            None
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
        Return the current internal state of the CMS environment.
        
        Returns:
            Dict[str, Any]: A dictionary containing all current state variables:
                - embeds: All embed components indexed by slug
                - embed_versions: Version history for each embed
                - pages: All pages indexed by page_id
                - media_assets: All media assets indexed by asset_id
                - categories: All categories indexed by id
                - users: All users indexed by _id
                - current_user_id: The ID of the currently active user
        """
        return {
            "embeds": deepcopy(self.embeds),
            "embed_versions": deepcopy(self.embed_versions),
            "pages": deepcopy(self.pages),
            "media_assets": deepcopy(self.media_assets),
            "categories": deepcopy(self.categories),
            "users": deepcopy(self.users),
            "current_user_id": self.current_user_id
        }
    
    def _timestamp(self) -> str:
        """
        Generate a consistent ISO format timestamp string.
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _generate_id(self) -> str:
        """
        Generate a unique identifier string.
        
        Returns:
            str: A unique identifier string.
        """
        return str(uuid.uuid4())[:8]
    
    def _get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve the current user's data.
        
        Returns:
            Optional[Dict[str, Any]]: Current user data or None if not found.
        """
        return self.users.get(self.current_user_id)
    
    def _has_permission(self, permission: str) -> bool:
        """
        Check if current user has a specific permission.
        
        Args:
            permission: The permission string to check.
        
        Returns:
            bool: True if user has the permission, False otherwise.
        """
        user = self._get_current_user()
        if not user:
            return False
        return permission in user.get("permissions", [])
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_embed_by_slug(self, slug: str) -> Dict[str, Any]:
        """
        Retrieve the full details of an embed component using its unique slug.
        
        Args:
            slug: The unique identifier slug of the embed to retrieve.
        
        Returns:
            Dict[str, Any]: The embed data if found and not deleted,
                           {"error": "..."} if not found or deleted.
        """
        if slug not in self.embeds:
            return {"error": f"Embed with slug '{slug}' not found"}
        
        embed = self.embeds[slug]
        if embed.get("status") == "deleted":
            return {"error": f"Embed with slug '{slug}' has been deleted and is inaccessible"}
        
        return deepcopy(embed)
    
    def list_all_embeds(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve a list of all embeds in the system, optionally filtered by status.
        
        Args:
            status: Optional status filter (e.g., "draft", "published", "deleted").
        
        Returns:
            Dict[str, Any]: Dictionary containing "embeds" list of matching embeds.
        """
        result = []
        for embed in self.embeds.values():
            if status is None or embed.get("status") == status:
                result.append(deepcopy(embed))
        return {"embeds": result, "count": len(result)}
    
    def get_embed_version_history(self, slug: str) -> Dict[str, Any]:
        """
        Retrieve all version snapshots of a given embed by slug.
        
        Args:
            slug: The unique slug of the embed.
        
        Returns:
            Dict[str, Any]: Dictionary with "versions" list showing content evolution,
                           or {"error": "..."} if embed not found.
        """
        if slug not in self.embeds:
            return {"error": f"Embed with slug '{slug}' not found"}
        
        versions = self.embed_versions.get(slug, [])
        return {"slug": slug, "versions": deepcopy(versions)}
    
    def get_embed_status(self, slug: str) -> Dict[str, Any]:
        """
        Check the current status of an embed.
        
        Args:
            slug: The unique slug of the embed.
        
        Returns:
            Dict[str, Any]: Dictionary with "status" field or error message.
        """
        if slug not in self.embeds:
            return {"error": f"Embed with slug '{slug}' not found"}
        
        return {"slug": slug, "status": self.embeds[slug].get("status")}
    
    def get_embed_metadata(self, slug: str) -> Dict[str, Any]:
        """
        Retrieve only the metadata field of an embed for inspection.
        
        Args:
            slug: The unique slug of the embed.
        
        Returns:
            Dict[str, Any]: Dictionary with "metadata" field or error message.
        """
        if slug not in self.embeds:
            return {"error": f"Embed with slug '{slug}' not found"}
        
        embed = self.embeds[slug]
        if embed.get("status") == "deleted":
            return {"error": f"Embed with slug '{slug}' has been deleted"}
        
        return {"slug": slug, "metadata": deepcopy(embed.get("metadata", {}))}
    
    def get_page_by_id(self, page_id: str) -> Dict[str, Any]:
        """
        Retrieve a page's full information using its page_id.
        
        Args:
            page_id: The unique identifier of the page.
        
        Returns:
            Dict[str, Any]: The page data if found, or {"error": "..."} if not found.
        """
        if page_id not in self.pages:
            return {"error": f"Page with id '{page_id}' not found"}
        
        return deepcopy(self.pages[page_id])
    
    def get_page_by_slug(self, slug: str) -> Dict[str, Any]:
        """
        Retrieve a published or draft page using its URL-friendly slug.
        
        Args:
            slug: The URL-friendly slug of the page.
        
        Returns:
            Dict[str, Any]: The page data if found, or {"error": "..."} if not found.
        """
        for page in self.pages.values():
            if page.get("slug") == slug:
                return deepcopy(page)
        
        return {"error": f"Page with slug '{slug}' not found"}
    
    def list_pages_by_author(self, author_id: str) -> Dict[str, Any]:
        """
        Retrieve all pages created by a specific user.
        
        Args:
            author_id: The user ID of the author.
        
        Returns:
            Dict[str, Any]: Dictionary with "pages" list of matching pages.
        """
        result = []
        for page in self.pages.values():
            if page.get("author_id") == author_id:
                result.append(deepcopy(page))
        
        return {"author_id": author_id, "pages": result, "count": len(result)}
    
    def list_pages_containing_embed(self, embed_slug: str) -> Dict[str, Any]:
        """
        Find all pages that reference a specific embed slug in their content_body.
        
        Args:
            embed_slug: The slug of the embed to search for.
        
        Returns:
            Dict[str, Any]: Dictionary with "pages" list containing the embed reference.
        """
        embed_pattern = f"{{{{embed:{embed_slug}}}}}"
        result = []
        
        for page in self.pages.values():
            if embed_pattern in page.get("content_body", ""):
                result.append(deepcopy(page))
        
        return {"embed_slug": embed_slug, "pages": result, "count": len(result)}
    
    def get_media_asset_by_id(self, asset_id: str) -> Dict[str, Any]:
        """
        Retrieve metadata and URL of a media asset by its asset_id.
        
        Args:
            asset_id: The unique identifier of the media asset.
        
        Returns:
            Dict[str, Any]: The asset data if found, or {"error": "..."} if not found.
        """
        if asset_id not in self.media_assets:
            return {"error": f"Media asset with id '{asset_id}' not found"}
        
        return deepcopy(self.media_assets[asset_id])
    
    def list_media_assets_by_type(self, media_type: str) -> Dict[str, Any]:
        """
        Retrieve all media assets filtered by media_type.
        
        Args:
            media_type: The MIME type to filter by (e.g., "image/jpeg", "video/mp4").
        
        Returns:
            Dict[str, Any]: Dictionary with "assets" list of matching media assets.
        """
        result = []
        for asset in self.media_assets.values():
            if asset.get("media_type") == media_type:
                result.append(deepcopy(asset))
        
        return {"media_type": media_type, "assets": result, "count": len(result)}
    
    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user information including role and permissions by _id.
        
        Args:
            user_id: The unique identifier of the user.
        
        Returns:
            Dict[str, Any]: The user data if found, or {"error": "..."} if not found.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found"}
        
        return deepcopy(self.users[user_id])
    
    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """
        Retrieve user info by username.
        
        Args:
            username: The username to search for.
        
        Returns:
            Dict[str, Any]: The user data if found, or {"error": "..."} if not found.
        """
        for user in self.users.values():
            if user.get("username") == username:
                return deepcopy(user)
        
        return {"error": f"User with username '{username}' not found"}
    
    def check_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """
        Return the list of permissions assigned to a user.
        
        Args:
            user_id: The unique identifier of the user.
        
        Returns:
            Dict[str, Any]: Dictionary with "permissions" list or error message.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found"}
        
        user = self.users[user_id]
        return {
            "user_id": user_id,
            "username": user.get("username"),
            "role": user.get("role"),
            "permissions": deepcopy(user.get("permissions", []))
        }
    
    def validate_embed_reference_integrity(self, page_id: str) -> Dict[str, Any]:
        """
        Check whether all embed slugs referenced in a page's content_body exist.
        
        Args:
            page_id: The unique identifier of the page to validate.
        
        Returns:
            Dict[str, Any]: Dictionary with validation results including missing embeds.
        """
        if page_id not in self.pages:
            return {"error": f"Page with id '{page_id}' not found"}
        
        page = self.pages[page_id]
        content = page.get("content_body", "")
        
        embed_refs = re.findall(r'\{\{embed:([^}]+)\}\}', content)
        
        missing = []
        deleted = []
        valid = []
        
        for slug in embed_refs:
            if slug not in self.embeds:
                missing.append(slug)
            elif self.embeds[slug].get("status") == "deleted":
                deleted.append(slug)
            else:
                valid.append(slug)
        
        is_valid = len(missing) == 0 and len(deleted) == 0
        
        return {
            "page_id": page_id,
            "is_valid": is_valid,
            "valid_embeds": valid,
            "missing_embeds": missing,
            "deleted_embeds": deleted
        }
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def create_embed(
        self,
        slug: str,
        title: str,
        content: str,
        embed_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new embed with a unique slug, initial content, and metadata.
        
        Args:
            slug: Unique identifier for the embed.
            title: Display title of the embed.
            content: HTML/content body of the embed.
            embed_type: Type classification (e.g., "banner", "video", "form").
            metadata: Optional metadata dictionary.
        
        Returns:
            Dict[str, Any]: Created embed data or error message.
        """
        if not self._has_permission("create_embed"):
            return {"error": "User lacks permission to create embeds"}
        
        if slug in self.embeds:
            return {"error": f"Embed with slug '{slug}' already exists"}
        
        if not slug or not slug.strip():
            return {"error": "Embed slug cannot be empty"}
        
        timestamp = self._timestamp()
        
        new_embed = {
            "slug": slug,
            "title": title,
            "content": content,
            "type": embed_type,
            "status": "draft",
            "created_at": timestamp,
            "updated_at": timestamp,
            "version": 1,
            "metadata": metadata or {}
        }
        
        self.embeds[slug] = new_embed
        self.embed_versions[slug] = [
            {"version": 1, "content": content, "timestamp": timestamp}
        ]
        
        return {"success": True, "embed": deepcopy(new_embed)}
    
    def update_embed(
        self,
        slug: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Modify an existing embed's content or metadata. Increments version.
        
        Args:
            slug: The slug of the embed to update.
            content: New content body (optional).
            title: New title (optional).
            metadata: New or updated metadata (optional).
        
        Returns:
            Dict[str, Any]: Updated embed data or error message.
        """
        if not self._has_permission("edit_embed"):
            return {"error": "User lacks permission to edit embeds"}
        
        if slug not in self.embeds:
            return {"error": f"Embed with slug '{slug}' not found"}
        
        embed = self.embeds[slug]
        
        if embed.get("status") == "deleted":
            return {"error": f"Cannot update deleted embed '{slug}'"}
        
        timestamp = self._timestamp()
        
        if content is not None:
            embed["content"] = content
        if title is not None:
            embed["title"] = title
        if metadata is not None:
            embed["metadata"].update(metadata)
        
        embed["version"] += 1
        embed["updated_at"] = timestamp
        
        if slug not in self.embed_versions:
            self.embed_versions[slug] = []
        
        self.embed_versions[slug].append({
            "version": embed["version"],
            "content": embed["content"],
            "timestamp": timestamp
        })
        
        return {"success": True, "embed": deepcopy(embed)}
    
    def publish_embed(self, slug: str) -> Dict[str, Any]:
        """
        Change an embed's status from draft to published.
        
        Args:
            slug: The slug of the embed to publish.
        
        Returns:
            Dict[str, Any]: Updated embed data or error message.
        """
        if not self._has_permission("publish_embed"):
            return {"error": "User lacks permission to publish embeds"}
        
        if slug not in self.embeds:
            return {"error": f"Embed with slug '{slug}' not found"}
        
        embed = self.embeds[slug]
        
        if embed.get("status") == "deleted":
            return {"error": f"Cannot publish deleted embed '{slug}'"}
        
        if embed.get("status") == "published":
            return {"error": f"Embed '{slug}' is already published"}
        
        embed["status"] = "published"
        embed["updated_at"] = self._timestamp()
        
        return {"success": True, "embed": deepcopy(embed)}
    
    def delete_embed(self, slug: str) -> Dict[str, Any]:
        """
        Set an embed's status to "deleted", making it inaccessible.
        
        Args:
            slug: The slug of the embed to delete.
        
        Returns:
            Dict[str, Any]: Success confirmation or error message.
        """
        if not self._has_permission("delete_embed"):
            return {"error": "User lacks permission to delete embeds"}
        
        if slug not in self.embeds:
            return {"error": f"Embed with slug '{slug}' not found"}
        
        embed = self.embeds[slug]
        
        if embed.get("status") == "deleted":
            return {"error": f"Embed '{slug}' is already deleted"}
        
        embed["status"] = "deleted"
        embed["updated_at"] = self._timestamp()
        
        return {"success": True, "message": f"Embed '{slug}' has been deleted"}
    
    def restore_embed(self, slug: str) -> Dict[str, Any]:
        """
        Restore a deleted embed to draft status, preserving version history.
        
        Args:
            slug: The slug of the embed to restore.
        
        Returns:
            Dict[str, Any]: Restored embed data or error message.
        """
        if not self._has_permission("edit_embed"):
            return {"error": "User lacks permission to restore embeds"}
        
        if slug not in self.embeds:
            return {"error": f"Embed with slug '{slug}' not found"}
        
        embed = self.embeds[slug]
        
        if embed.get("status") != "deleted":
            return {"error": f"Embed '{slug}' is not deleted and cannot be restored"}
        
        embed["status"] = "draft"
        embed["updated_at"] = self._timestamp()
        
        return {"success": True, "embed": deepcopy(embed)}
    
    def create_page(
        self,
        page_id: Optional[str] = None,
        title: str = "",
        slug: str = "",
        content_body: str = "",
        content: str = "",
        author_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new page to the CMS.
        
        Args:
            page_id: Unique identifier for the page (auto-generated if not provided).
            title: Display title of the page.
            slug: URL-friendly slug for the page.
            content_body: HTML/content body potentially containing embed references.
            content: Alternative parameter for content (used if content_body is empty).
            author_id: ID of the author (defaults to current user).
        
        Returns:
            Dict[str, Any]: Created page data or error message.
        """
        if not self._has_permission("create_page"):
            return {"error": "User lacks permission to create pages"}
        
        if not title or not title.strip():
            return {"error": "Page title cannot be empty"}
        
        if not slug or not slug.strip():
            return {"error": "Page slug cannot be empty"}
        
        # Check slug uniqueness
        for existing_page in self.pages.values():
            if existing_page.get("slug") == slug.strip():
                return {"error": f"Page with slug '{slug}' already exists"}
        
        # Use content if content_body is not provided
        actual_content = content_body if content_body else content
        
        # Generate page_id if not provided
        actual_page_id = page_id if page_id else f"page_{self._generate_id()}"
        # Ensure generated page_id doesn't collide
        while actual_page_id in self.pages:
            actual_page_id = f"page_{self._generate_id()}"
        
        # Use current user as author if not specified
        actual_author_id = author_id if author_id else self.current_user_id
        
        page_data = {
            "page_id": actual_page_id,
            "title": title.strip(),
            "slug": slug.strip(),
            "content_body": actual_content or "",
            "author_id": actual_author_id,
            "status": "draft",
            "created_at": self._timestamp(),
            "updated_at": self._timestamp()
        }
        
        self.pages[actual_page_id] = page_data
        return {"success": True, "page": deepcopy(page_data)}
    
    def get_page(self, page_id: str) -> Dict[str, Any]:
        """Retrieve a page by its ID.
        
        Args:
            page_id: The unique identifier of the page.
        
        Returns:
            Dict[str, Any]: Page data or error message.
        """
        if not page_id:
            return {"error": "Page ID is required"}
        
        if page_id not in self.pages:
            return {"error": f"Page with ID '{page_id}' not found"}
        
        return {"success": True, "page": deepcopy(self.pages[page_id])}
    
    def update_page(self, page_id: str, title: str = None, content_body: str = None, content: str = None, 
                    slug: str = None, status: str = None) -> Dict[str, Any]:
        """Update an existing page.
        
        Args:
            page_id: The unique identifier of the page to update.
            title: New title for the page (optional).
            content_body: New HTML/content body for the page (optional).
            content: Alternative parameter for content (optional).
            slug: New slug for the page (optional).
            status: New status for the page (optional).
        
        Returns:
            Dict[str, Any]: Updated page data or error message.
        """
        if not self._has_permission("edit_page"):
            return {"error": "User lacks permission to edit pages"}
        
        if not page_id:
            return {"error": "Page ID is required"}
        
        if page_id not in self.pages:
            return {"error": f"Page with ID '{page_id}' not found"}
        
        page = self.pages[page_id]
        
        if title is not None:
            if not title.strip():
                return {"error": "Page title cannot be empty"}
            page["title"] = title.strip()
        
        if content_body is not None:
            page["content_body"] = content_body
        elif content is not None:
            page["content_body"] = content
        
        if slug is not None:
            if not slug.strip():
                return {"error": "Page slug cannot be empty"}
            # Check slug uniqueness (excluding current page)
            for existing_id, existing_page in self.pages.items():
                if existing_id != page_id and existing_page.get("slug") == slug.strip():
                    return {"error": f"Page with slug '{slug}' already exists"}
            page["slug"] = slug.strip()
        
        if status is not None:
            valid_statuses = ["draft", "published", "archived"]
            if status not in valid_statuses:
                return {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}
            page["status"] = status
        
        page["updated_at"] = self._timestamp()
        return {"success": True, "page": deepcopy(page)}
    
    def delete_page(self, page_id: str) -> Dict[str, Any]:
        """Delete a page by its ID.
        
        Args:
            page_id: The unique identifier of the page to delete.
        
        Returns:
            Dict[str, Any]: Success message or error.
        """
        if not self._has_permission("delete_page"):
            return {"error": "User lacks permission to delete pages"}
        
        if not page_id:
            return {"error": "Page ID is required"}
        
        if page_id not in self.pages:
            return {"error": f"Page with ID '{page_id}' not found"}
        
        deleted_page = self.pages.pop(page_id)
        return {"success": True, "message": f"Page '{deleted_page['title']}' deleted successfully"}
    
    def list_pages(self, status: str = None, author_id: str = None) -> Dict[str, Any]:
        """List all pages with optional filtering.
        
        Args:
            status: Filter by page status (optional).
            author_id: Filter by author ID (optional).
        
        Returns:
            Dict[str, Any]: List of pages matching the criteria.
        """
        pages = list(self.pages.values())
        
        if status:
            pages = [p for p in pages if p["status"] == status]
        
        if author_id:
            pages = [p for p in pages if p["author_id"] == author_id]
        
        return {"success": True, "pages": deepcopy(pages), "count": len(pages)}


__TEST_CASES__ = [
    {
        "name": "test_create_page_success",
        "input": {"title": "Test Page", "slug": "test-page", "content_body": "Hello World"},
        "expected_keys": ["success", "page"],
        "method": "create_page"
    },
    {
        "name": "test_create_page_empty_title",
        "input": {"title": "", "slug": "test-slug", "content_body": "Content"},
        "expected_error": "Page title cannot be empty",
        "method": "create_page"
    },
    {
        "name": "test_get_page_success",
        "input": {"page_id": "page-001"},
        "expected_keys": ["success", "page"],
        "method": "get_page"
    },
    {
        "name": "test_get_page_not_found",
        "input": {"page_id": "nonexistent"},
        "expected_error": "Page with ID 'nonexistent' not found",
        "method": "get_page"
    },
    {
        "name": "test_update_page_success",
        "input": {"page_id": "page-002", "title": "Updated About Us", "content": "Updated content"},
        "expected_keys": ["success", "page"],
        "method": "update_page"
    }
]
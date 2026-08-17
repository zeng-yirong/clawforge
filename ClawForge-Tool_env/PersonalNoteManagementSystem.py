"""
Personal Note Management System Environment API

A personal note management system for storing, organizing, and retrieving user-created notes
with support for categories, tags, and timestamps.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

DEFAULT_STATE: Dict[str, Any] = {
    "notes": {
        "note_001": {
            "note_id": "note_001",
            "title": "Meeting Notes",
            "content": "Discussed Q3 roadmap and budget allocation for the marketing team.",
            "category": "Work",
            "tags": ["meeting", "planning"],
            "created_at": "2024-01-15T09:30:00",
            "updated_at": "2024-01-15T10:45:00",
            "is_pinned": True
        },
        "note_002": {
            "note_id": "note_002",
            "title": "Grocery List",
            "content": "Milk, eggs, bread, butter, apples, chicken breast, rice",
            "category": "Personal",
            "tags": ["shopping", "weekly"],
            "created_at": "2024-01-16T14:00:00",
            "updated_at": "2024-01-16T14:00:00",
            "is_pinned": False
        },
        "note_003": {
            "note_id": "note_003",
            "title": "Book Recommendations",
            "content": "1. Atomic Habits by James Clear\n2. Deep Work by Cal Newport\n3. The Pragmatic Programmer",
            "category": "Personal",
            "tags": ["reading", "self-improvement"],
            "created_at": "2024-01-10T20:15:00",
            "updated_at": "2024-01-18T08:30:00",
            "is_pinned": False
        },
        "note_004": {
            "note_id": "note_004",
            "title": "Project Ideas",
            "content": "Build a personal finance tracker app with visualization features.",
            "category": "Work",
            "tags": ["ideas", "development"],
            "created_at": "2024-01-12T11:00:00",
            "updated_at": "2024-01-12T11:00:00",
            "is_pinned": True
        }
    },
    "categories": {
        "Work": {
            "category_name": "Work",
            "created_at": "2024-01-01T00:00:00"
        },
        "Personal": {
            "category_name": "Personal",
            "created_at": "2024-01-01T00:00:00"
        },
        "Ideas": {
            "category_name": "Ideas",
            "created_at": "2024-01-05T10:00:00"
        }
    },
    "tags": {
        "meeting": {"tag_name": "meeting"},
        "planning": {"tag_name": "planning"},
        "shopping": {"tag_name": "shopping"},
        "weekly": {"tag_name": "weekly"},
        "reading": {"tag_name": "reading"},
        "self-improvement": {"tag_name": "self-improvement"},
        "ideas": {"tag_name": "ideas"},
        "development": {"tag_name": "development"}
    },
    "next_note_id": 5
}


class PersonalNoteManagementSystem:
    """
    A personal note management system environment for storing, organizing, 
    and retrieving user-created notes with support for categories, tags, and timestamps.
    
    This environment provides APIs for creating, editing, searching, and organizing
    notes in a lightweight information repository for personal productivity workflows.
    """
    
    def __init__(self) -> None:
        """
        Initialize the PersonalNoteManagementSystem environment.
        
        Declares all state attributes and sets up the API description.
        
        Args:
            None
        
        Returns:
            None
        """
        self.notes: Dict[str, Dict[str, Any]] = deepcopy(DEFAULT_STATE["notes"])
        self.categories: Dict[str, Dict[str, Any]] = deepcopy(DEFAULT_STATE["categories"])
        self.tags: Dict[str, Dict[str, str]] = deepcopy(DEFAULT_STATE["tags"])
        self.next_note_id: int = DEFAULT_STATE["next_note_id"]
        
        self._api_description: str = (
            "Personal note management system for storing, organizing, and retrieving "
            "user-created notes with categories, tags, and timestamps."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state data for the environment.
            long_context: Flag for handling long context scenarios (default False).
        
        Returns:
            None
        """
        if not scenario:
            return
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
    
    def get_env_state(self) -> Dict[str, Any]:
        """
        Retrieve the current state of the environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables:
                - notes: Dictionary of all notes keyed by note_id
                - categories: Dictionary of all categories keyed by category_name
                - tags: Dictionary of all tags keyed by tag_name
                - next_note_id: Integer for the next auto-generated note ID
        """
        return {
            "notes": deepcopy(self.notes),
            "categories": deepcopy(self.categories),
            "tags": deepcopy(self.tags),
            "next_note_id": self.next_note_id
        }
    
    # ==================== Query Operations ====================
    
    def get_note_by_id(self, note_id: str) -> Dict[str, Any]:
        """
        Retrieve the full details of a note using its unique note_id.
        
        Args:
            note_id: The unique identifier of the note to retrieve.
        
        Returns:
            Dict[str, Any]: The complete note data if found, or an error dictionary
                if the note does not exist.
        """
        if note_id not in self.notes:
            return {"error": f"Note with id '{note_id}' not found."}
        return deepcopy(self.notes[note_id])
    
    def list_all_notes(self, minimal: bool = False) -> Dict[str, Any]:
        """
        Return a list of all notes, optionally with minimal metadata.
        
        Args:
            minimal: If True, return only title, note_id, and updated_at for each note.
        
        Returns:
            Dict[str, Any]: Dictionary containing a list of notes under the 'notes' key.
        """
        if minimal:
            notes_list = [
                {
                    "note_id": note["note_id"],
                    "title": note["title"],
                    "updated_at": note["updated_at"]
                }
                for note in self.notes.values()
            ]
        else:
            notes_list = [deepcopy(note) for note in self.notes.values()]
        return {"notes": notes_list, "count": len(notes_list)}
    
    def search_notes_by_title(self, keyword: str) -> Dict[str, Any]:
        """
        Find notes whose title contains the given keyword or phrase.
        
        Args:
            keyword: The keyword or phrase to search for in note titles.
        
        Returns:
            Dict[str, Any]: Dictionary containing matching notes and their count.
        """
        if not keyword:
            return {"error": "Search keyword cannot be empty."}
        
        keyword_lower = keyword.lower()
        matching_notes = [
            deepcopy(note) for note in self.notes.values()
            if keyword_lower in note["title"].lower()
        ]
        return {"notes": matching_notes, "count": len(matching_notes)}
    
    def search_notes_by_content(self, keyword: str) -> Dict[str, Any]:
        """
        Find notes whose content contains the given keyword or phrase.
        
        Args:
            keyword: The keyword or phrase to search for in note content.
        
        Returns:
            Dict[str, Any]: Dictionary containing matching notes and their count.
        """
        if not keyword:
            return {"error": "Search keyword cannot be empty."}
        
        keyword_lower = keyword.lower()
        matching_notes = [
            deepcopy(note) for note in self.notes.values()
            if keyword_lower in note["content"].lower()
        ]
        return {"notes": matching_notes, "count": len(matching_notes)}
    
    def search_notes_by_keyword(self, keyword: str) -> Dict[str, Any]:
        """
        Search across both title and content for a given keyword.
        
        Args:
            keyword: The keyword to search for in both title and content.
        
        Returns:
            Dict[str, Any]: Dictionary containing matching notes and their count.
        """
        if not keyword:
            return {"error": "Search keyword cannot be empty."}
        
        keyword_lower = keyword.lower()
        matching_notes = [
            deepcopy(note) for note in self.notes.values()
            if keyword_lower in note["title"].lower() or keyword_lower in note["content"].lower()
        ]
        return {"notes": matching_notes, "count": len(matching_notes)}
    
    def filter_notes_by_category(self, category: str) -> Dict[str, Any]:
        """
        Retrieve all notes assigned to a specific category.
        
        Args:
            category: The category name to filter notes by.
        
        Returns:
            Dict[str, Any]: Dictionary containing filtered notes and their count.
        """
        if not category:
            return {"error": "Category cannot be empty."}
        
        matching_notes = [
            deepcopy(note) for note in self.notes.values()
            if note["category"] == category
        ]
        return {"notes": matching_notes, "count": len(matching_notes)}
    
    def filter_notes_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Retrieve all notes that have a specific tag.
        
        Args:
            tag: The tag name to filter notes by.
        
        Returns:
            Dict[str, Any]: Dictionary containing filtered notes and their count.
        """
        if not tag:
            return {"error": "Tag cannot be empty."}
        
        matching_notes = [
            deepcopy(note) for note in self.notes.values()
            if tag in note["tags"]
        ]
        return {"notes": matching_notes, "count": len(matching_notes)}
    
    def get_pinned_notes(self) -> Dict[str, Any]:
        """
        List all notes currently marked as pinned.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing pinned notes and their count.
        """
        pinned_notes = [
            deepcopy(note) for note in self.notes.values()
            if note["is_pinned"]
        ]
        return {"notes": pinned_notes, "count": len(pinned_notes)}
    
    def list_all_categories(self) -> Dict[str, Any]:
        """
        Retrieve all available categories in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing all categories and their count.
        """
        categories_list = [deepcopy(cat) for cat in self.categories.values()]
        return {"categories": categories_list, "count": len(categories_list)}
    
    def list_all_tags(self) -> Dict[str, Any]:
        """
        Retrieve all existing tags used in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing all tags and their count.
        """
        tags_list = [deepcopy(tag) for tag in self.tags.values()]
        return {"tags": tags_list, "count": len(tags_list)}
    
    def get_note_metadata(self, note_id: str) -> Dict[str, Any]:
        """
        Retrieve metadata of a note without full content.
        
        Args:
            note_id: The unique identifier of the note.
        
        Returns:
            Dict[str, Any]: Dictionary containing note metadata (created_at, updated_at,
                category, tags, is_pinned) or an error if note not found.
        """
        if note_id not in self.notes:
            return {"error": f"Note with id '{note_id}' not found."}
        
        note = self.notes[note_id]
        return {
            "note_id": note["note_id"],
            "title": note["title"],
            "category": note["category"],
            "tags": list(note["tags"]),
            "created_at": note["created_at"],
            "updated_at": note["updated_at"],
            "is_pinned": note["is_pinned"]
        }
    
    # ==================== State Change Operations ====================
    
    def create_note(
        self,
        title: str = "",
        content: str = "",
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new note with title and/or content, assign category and tags.
        
        Auto-sets timestamps and generates note_id. At least one of title or content
        must be non-empty.
        
        Args:
            title: The title of the note (optional if content is provided).
            content: The content of the note (optional if title is provided).
            category: The category to assign to the note (optional).
            tags: List of tags to attach to the note (optional).
        
        Returns:
            Dict[str, Any]: The created note data or an error dictionary.
        """
        # Constraint: Every note must have a non-empty content or title
        if not title.strip() and not content.strip():
            return {"error": "Note must have a non-empty title or content."}
        
        # Validate category if provided
        if category and category not in self.categories:
            return {"error": f"Category '{category}' does not exist. Create it first or use an existing category."}
        
        # Generate note_id
        note_id = f"note_{self.next_note_id:03d}"
        self.next_note_id += 1
        
        timestamp = self._timestamp()
        
        # Process tags
        note_tags = []
        if tags:
            for tag in tags:
                if tag and tag.strip():
                    tag_name = tag.strip()
                    if tag_name not in self.tags:
                        self.tags[tag_name] = {"tag_name": tag_name}
                    note_tags.append(tag_name)
        
        new_note = {
            "note_id": note_id,
            "title": title.strip(),
            "content": content.strip(),
            "category": category if category else "",
            "tags": note_tags,
            "created_at": timestamp,
            "updated_at": timestamp,
            "is_pinned": False
        }
        
        self.notes[note_id] = new_note
        return {"success": True, "note": deepcopy(new_note)}
    
    def edit_note(
        self,
        note_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Modify the title, content, or metadata of an existing note.
        
        Auto-updates the updated_at timestamp.
        
        Args:
            note_id: The unique identifier of the note to edit.
            title: New title for the note (optional).
            content: New content for the note (optional).
            category: New category for the note (optional).
            tags: New list of tags to replace existing tags (optional).
        
        Returns:
            Dict[str, Any]: The updated note data or an error dictionary.
        """
        if note_id not in self.notes:
            return {"error": f"Note with id '{note_id}' not found."}
        
        note = self.notes[note_id]
        
        # Calculate new values
        new_title = title.strip() if title is not None else note["title"]
        new_content = content.strip() if content is not None else note["content"]
        
        # Constraint: Every note must have a non-empty content or title
        if not new_title and not new_content:
            return {"error": "Note must have a non-empty title or content."}
        
        # Validate category if provided
        if category is not None and category and category not in self.categories:
            return {"error": f"Category '{category}' does not exist."}
        
        # Apply changes
        note["title"] = new_title
        note["content"] = new_content
        
        if category is not None:
            note["category"] = category
        
        if tags is not None:
            note_tags = []
            for tag in tags:
                if tag and tag.strip():
                    tag_name = tag.strip()
                    if tag_name not in self.tags:
                        self.tags[tag_name] = {"tag_name": tag_name}
                    note_tags.append(tag_name)
            note["tags"] = note_tags
        
        note["updated_at"] = self._timestamp()
        
        return {"success": True, "note": deepcopy(note)}
    
    def delete_note(self, note_id: str) -> Dict[str, Any]:
        """
        Remove a note permanently from the system by note_id.
        
        Args:
            note_id: The unique identifier of the note to delete.
        
        Returns:
            Dict[str, Any]: Success confirmation or an error dictionary.
        """
        if note_id not in self.notes:
            return {"error": f"Note with id '{note_id}' not found."}
        
        deleted_note = self.notes.pop(note_id)
        return {"success": True, "deleted_note_id": note_id, "deleted_title": deleted_note["title"]}
    
    def pin_note(self, note_id: str) -> Dict[str, Any]:
        """
        Mark a note as pinned to keep it at the top of lists.
        
        Args:
            note_id: The unique identifier of the note to pin.
        
        Returns:
            Dict[str, Any]: Success confirmation or an error dictionary.
        """
        if note_id not in self.notes:
            return {"error": f"Note with id '{note_id}' not found."}
        
        self.notes[note_id]["is_pinned"] = True
        self.notes[note_id]["updated_at"] = self._timestamp()
        return {"success": True, "note_id": note_id, "is_pinned": True}
    
    def unpin_note(self, note_id: str) -> Dict[str, Any]:
        """
        Remove the pinned status from a note.
        
        Args:
            note_id: The unique identifier of the note to unpin.
        
        Returns:
            Dict[str, Any]: Success confirmation or an error dictionary.
        """
        if note_id not in self.notes:
            return {"error": f"Note with id '{note_id}' not found."}
        
        self.notes[note_id]["is_pinned"] = False
        self.notes[note_id]["updated_at"] = self._timestamp()
        return {"success": True, "note_id": note_id, "is_pinned": False}
    
    def create_category(self, category_name: str) -> Dict[str, Any]:
        """
        Add a new category to the system.
        
        Args:
            category_name: The name of the new category to create.
        
        Returns:
            Dict[str, Any]: The created category data or an error dictionary.
        """
        if not category_name or not category_name.strip():
            return {"error": "Category name cannot be empty."}
        
        category_name = category_name.strip()
        
        if category_name in self.categories:
            return {"error": f"Category '{category_name}' already exists."}
        
        new_category = {
            "category_name": category_name,
            "created_at": self._timestamp()
        }
        
        self.categories[category_name] = new_category
        return {"success": True, "category": deepcopy(new_category)}
    
    def create_tag(self, tag_name: str) -> Dict[str, Any]:
        """
        Add a new tag to the system if not already present.
        
        Args:
            tag_name: The name of the new tag to create.
        
        Returns:
            Dict[str, Any]: The created tag data or an error dictionary.
        """
        if not tag_name or not tag_name.strip():
            return {"error": "Tag name cannot be empty."}
        
        tag_name = tag_name.strip()
        
        if tag_name in self.tags:
            return {"error": f"Tag '{tag_name}' already exists."}
        
        new_tag = {"tag_name": tag_name}
        self.tags[tag_name] = new_tag
        return {"success": True, "tag": deepcopy(new_tag)}
    
    def add_tag_to_note(self, note_id: str, tag_name: str) -> Dict[str, Any]:
        """
        Attach an existing or new tag to a specific note.
        
        Args:
            note_id: The unique identifier of the note.
            tag_name: The name of the tag to attach.
        
        Returns:
            Dict[str, Any]: Success confirmation or an error dictionary.
        """
        if note_id not in self.notes:
            return {"error": f"Note with id '{note_id}' not found."}
        
        if not tag_name or not tag_name.strip():
            return {"error": "Tag name cannot be empty."}
        
        tag_name = tag_name.strip()
        
        # Create tag if it doesn't exist
        if tag_name not in self.tags:
            self.tags[tag_name] = {"tag_name": tag_name}
        
        note = self.notes[note_id]
        if tag_name in note["tags"]:
            return {"error": f"Tag '{tag_name}' is already attached to this note."}
        
        note["tags"].append(tag_name)
        note["updated_at"] = self._timestamp()
        
        return {"success": True, "note_id": note_id, "added_tag": tag_name, "all_tags": list(note["tags"])}
    
    def remove_tag_from_note(self, note_id: str, tag_name: str) -> Dict[str, Any]:
        """
        Remove a specific tag from a note.
        
        Args:
            note_id: The unique identifier of the note.
            tag_name: The name of the tag to remove.
        
        Returns:
            Dict[str, Any]: Success confirmation or an error dictionary.
        """
        if note_id not in self.notes:
            return {"error": f"Note with id '{note_id}' not found."}
        
        if not tag_name or not tag_name.strip():
            return {"error": "Tag name cannot be empty."}
        
        tag_name = tag_name.strip()
        note = self.notes[note_id]
        
        if tag_name not in note["tags"]:
            return {"error": f"Tag '{tag_name}' is not attached to this note."}
        
        note["tags"].remove(tag_name)
        note["updated_at"] = self._timestamp()
        
        return {"success": True, "note_id": note_id, "removed_tag": tag_name, "remaining_tags": list(note["tags"])}
    
    def update_note_category(self, note_id: str, category: str) -> Dict[str, Any]:
        """
        Change the category of an existing note, validating that the category is valid.
        
        Args:
            note_id: The unique identifier of the note.
            category: The new category name to assign.
        
        Returns:
            Dict[str, Any]: Success confirmation or an error dictionary.
        """
        if note_id not in self.notes:
            return {"error": f"Note with id '{note_id}' not found."}
        
        if not category:
            # Allow clearing category
            old_category = self.notes[note_id]["category"]
            self.notes[note_id]["category"] = ""
            self.notes[note_id]["updated_at"] = self._timestamp()
            return {"success": True, "note_id": note_id, "old_category": old_category, "new_category": ""}
        
        category = category.strip()
        
        if category and category not in self.categories:
            return {"error": f"Category '{category}' does not exist."}
        
        old_category = self.notes[note_id]["category"]
        self.notes[note_id]["category"] = category
        self.notes[note_id]["updated_at"] = self._timestamp()
        
        return {
            "success": True,
            "note_id": note_id,
            "old_category": old_category,
            "new_category": category
        }
    
    def clear_note_content(self, note_id: str) -> Dict[str, Any]:
        """
        Remove content from a note while preserving metadata.
        
        Only allowed if the note has a non-empty title (to satisfy constraints).
        
        Args:
            note_id: The unique identifier of the note.
        
        Returns:
            Dict[str, Any]: Success confirmation or an error dictionary.
        """
        if note_id not in self.notes:
            return {"error": f"Note with id '{note_id}' not found."}
        
        note = self.notes[note_id]
        
        # Constraint: Every note must have a non-empty content or title
        if not note["title"].strip():
            return {"error": "Cannot clear content when title is empty. Note must have at least a title or content."}
        
        note["content"] = ""
        note["updated_at"] = self._timestamp()
        
        return {"success": True, "note_id": note_id, "content_cleared": True}


__TEST_CASES__ = [
    {
        "name": "Create and retrieve a new note",
        "steps": [
            {"tool_call": "create_note(title='Test Note', content='This is test content', category='Work', tags=['test', 'demo'])", "expect_success": True},
            {"tool_call": "list_all_notes(minimal=True)", "expect_success": True},
            {"tool_call": "get_note_by_id(note_id='note_005')", "expect_success": True}
        ]
    },
    {
        "name": "Search and filter notes workflow",
        "steps": [
            {"tool_call": "search_notes_by_title(keyword='Meeting')", "expect_success": True},
            {"tool_call": "search_notes_by_keyword(keyword='budget')", "expect_success": True},
            {"tool_call": "filter_notes_by_category(category='Personal')", "expect_success": True},
            {"tool_call": "filter_notes_by_tag(tag='reading')", "expect_success": True}
        ]
    },
    {
        "name": "Edit and pin note workflow",
        "steps": [
            {"tool_call": "edit_note(note_id='note_002', title='Updated Grocery List', content='Milk, eggs, bread, cheese')", "expect_success": True},
            {"tool_call": "pin_note(note_id='note_002')", "expect_success": True},
            {"tool_call": "get_pinned_notes()", "expect_success": True},
            {"tool_call": "unpin_note(note_id='note_002')", "expect_success": True}
        ]
    },
    {
        "name": "Tag management workflow",
        "steps": [
            {"tool_call": "create_tag(tag_name='urgent')", "expect_success": True},
            {"tool_call": "add_tag_to_note(note_id='note_001', tag_name='urgent')", "expect_success": True},
            {"tool_call": "get_note_metadata(note_id='note_001')", "expect_success": True},
            {"tool_call": "remove_tag_from_note(note_id='note_001', tag_name='urgent')", "expect_success": True},
            {"tool_call": "list_all_tags()", "expect_success": True}
        ]
    },
    {
        "name": "Error handling - invalid operations",
        "steps": [
            {"tool_call": "get_note_by_id(note_id='note_999')", "expect_success": False},
            {"tool_call": "create_note(title='', content='')", "expect_success": False},
            {"tool_call": "update_note_category(note_id='note_001', category='NonExistentCategory')", "expect_success": False},
            {"tool_call": "delete_note(note_id='invalid_id')", "expect_success": False},
            {"tool_call": "search_notes_by_title(keyword='')", "expect_success": False},
            {"tool_call": "add_tag_to_note(note_id='note_001', tag_name='')", "expect_success": False}
        ]
    }
]
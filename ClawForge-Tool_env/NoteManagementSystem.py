import datetime
from copy import deepcopy
from typing import Dict, List, Optional, Union

DEFAULT_NOTE_STATE = {
    "users": ["alice", "bob", "charlie"],
    "current_user": None,
    "notebooks": {
        1: {"id": 1, "name": "Personal", "owner": "alice"},
        2: {"id": 2, "name": "Work Ideas", "owner": "alice"},
    },
    "notes": {
        101: {
            "id": 101,
            "notebook_id": 1,
            "title": "Grocery List",
            "content": "Milk, Eggs, Bread",
            "tags": ["shopping", "home"],
            "owner": "alice",
            "shared_with": [],
            "created_at": "2023-10-01 10:00:00",
            "updated_at": "2023-10-01 10:00:00",
            "version_history": [],
            "in_trash": False,
        }
    },
    "id_counter": 102,
    "notebook_counter": 3,
}


class SimpleNoteAPI:
    """
    A class representing the SimpleNote API for managing notebooks and rich notes.

    This environment supports creating notes within notebooks, tagging, version history
    tracking, sharing notes between users, and a trash/restore mechanism.

    Attributes:
        users (List[str]): List of registered usernames.
        current_user (Optional[str]): The currently authenticated user.
        notebooks (Dict[int, Dict]): Dictionary of notebooks keyed by notebook ID.
        notes (Dict[int, Dict]): Dictionary of notes keyed by note ID.
        id_counter (int): Counter for generating unique note IDs.
        notebook_counter (int): Counter for generating unique notebook IDs.
    """

    def __init__(self):
        self.users: List[str]
        self.current_user: Optional[str]
        self.notebooks: Dict[int, Dict[str, Union[int, str]]]
        self.notes: Dict[int, Dict[str, Union[int, str, List, bool]]]
        self.id_counter: int
        self.notebook_counter: int
        self._api_description = "This tool is an advanced note-taking application that allows users to manage notebooks, track note versions, tag content, and share notes."

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """Load a scenario into the SimpleNote API.
        
        Args:
            scenario (dict): The state dictionary to load.
            long_context (bool): Flag indicating if context is long.
            
        Returns:
            None
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_NOTE_STATE)
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])

        notebooks_raw = scenario.get("notebooks", DEFAULT_STATE_COPY["notebooks"])
        self.notebooks = {int(k) if str(k).isdigit() else k: v for k, v in notebooks_raw.items()}

        notes_raw = scenario.get("notes", DEFAULT_STATE_COPY["notes"])
        self.notes = {int(k) if str(k).isdigit() else k: v for k, v in notes_raw.items()}

        self.id_counter = scenario.get("id_counter", DEFAULT_STATE_COPY["id_counter"])
        self.notebook_counter = scenario.get("notebook_counter", DEFAULT_STATE_COPY["notebook_counter"])

    def get_env_state(self) -> Dict:
        """Get the current environment state.
        
        Returns:
            Dict: The current state of the environment.
        """
        return {
            "users": self.users,
            "current_user": self.current_user,
            "notebooks": self.notebooks,
            "notes": self.notes,
            "id_counter": self.id_counter,
            "notebook_counter": self.notebook_counter,
        }

    def _timestamp(self) -> str:
        """Get the current timestamp.
        
        Returns:
            str: The current timestamp.
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def login(self, username: str) -> Dict[str, Union[bool, str]]:
        """Log in a user to the SimpleNote system.
        
        Args:
            username (str): The username to log in.
            
        Returns:
            Dict: Success status and message, or error.
        """
        if not isinstance(username, str):
            return {"error": "Username must be a string.", "success": False}
            
        if username not in self.users:
            return {"error": f"User {username} does not exist.", "success": False}
        self.current_user = username
        return {"success": True, "message": f"Logged in as {username}"}

    def logout(self) -> Dict[str, bool]:
        """Log out the current user.
        
        Returns:
            Dict: Success status.
        """
        self.current_user = None
        return {"success": True}

    def create_notebook(self, name: str) -> Dict[str, Union[int, str]]:
        """Create a new notebook for the current user.
        
        Args:
            name (str): Name of the new notebook.
            
        Returns:
            Dict: Details of the created notebook or error.
        """
        if not isinstance(name, str):
            return {"error": "Notebook name must be a string."}
            
        if not self.current_user:
            return {"error": "Authentication required."}

        nb_id = self.notebook_counter
        self.notebooks[nb_id] = {
            "id": nb_id,
            "name": name,
            "owner": self.current_user
        }
        self.notebook_counter += 1
        return {"id": nb_id, "name": name, "status": "Notebook created successfully"}

    def create_note(self, notebook_id: int, title: str, content: str = "", tags: List[str] = None) -> Dict[str, Union[int, str]]:
        """Create a new note within a specified notebook.
        
        Args:
            notebook_id (int): The ID of the notebook.
            title (str): Title of the note.
            content (str): Content of the note.
            tags (List[str]): List of tags.
            
        Returns:
            Dict: Details of the created note or error.
        """
        if not isinstance(notebook_id, int):
            return {"error": "notebook_id must be an integer."}
        if not isinstance(title, str):
            return {"error": "title must be a string."}
        if not isinstance(content, str):
            return {"error": "content must be a string."}
        if tags is not None and not isinstance(tags, list):
            return {"error": "tags must be a list."}

        if not self.current_user:
            return {"error": "Authentication required."}
        if notebook_id not in self.notebooks:
            return {"error": f"Notebook {notebook_id} not found."}
        if self.notebooks[notebook_id]["owner"] != self.current_user:
            return {"error": "Cannot create note in a notebook you do not own."}

        note_id = self.id_counter
        timestamp = self._timestamp()

        self.notes[note_id] = {
            "id": note_id,
            "notebook_id": notebook_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "owner": self.current_user,
            "shared_with": [],
            "created_at": timestamp,
            "updated_at": timestamp,
            "version_history": [],
            "in_trash": False
        }
        self.id_counter += 1
        return {"id": note_id, "title": title, "status": "Note created successfully"}

    def update_note(self, note_id: int, content: str) -> Dict[str, str]:
        """Update note content and save the previous version to history.
        
        Args:
            note_id (int): The ID of the note.
            content (str): The new content.
            
        Returns:
            Dict: Status message and updated time, or error.
        """
        if not isinstance(note_id, int):
            return {"error": "note_id must be an integer."}
        if not isinstance(content, str):
            return {"error": "content must be a string."}

        if not self.current_user:
            return {"error": "Authentication required."}

        note = self.notes.get(note_id)
        if not note or note.get("in_trash"):
            return {"error": "Note not found or is in trash."}
        if note["owner"] != self.current_user and self.current_user not in note["shared_with"]:
            return {"error": "Permission denied."}

        # Save to version history
        note["version_history"].append({
            "content": note["content"],
            "saved_at": note["updated_at"],
            "edited_by": self.current_user
        })

        note["content"] = content
        note["updated_at"] = self._timestamp()
        return {"status": f"Note {note_id} updated successfully", "updated_at": note["updated_at"]}

    def delete_note(self, note_id: int) -> Dict[str, str]:
        """Move a note to the trash.
        
        Args:
            note_id (int): The ID of the note.
            
        Returns:
            Dict: Status message or error.
        """
        if not isinstance(note_id, int):
            return {"error": "note_id must be an integer."}
            
        if not self.current_user:
            return {"error": "Authentication required."}

        note = self.notes.get(note_id)
        if not note:
            return {"error": "Note not found."}
        if note.get("in_trash"):
            return {"error": "Note is already in trash."}
        if note["owner"] != self.current_user:
            return {"error": "Only the owner can delete the note."}

        note["in_trash"] = True
        return {"status": f"Note {note_id} moved to trash."}

    def share_note(self, note_id: int, target_user: str) -> Dict[str, str]:
        """Share a note with another registered user.
        
        Args:
            note_id (int): The ID of the note.
            target_user (str): Username to share with.
            
        Returns:
            Dict: Status message or error.
        """
        if not isinstance(note_id, int):
            return {"error": "note_id must be an integer."}
        if not isinstance(target_user, str):
            return {"error": "target_user must be a string."}

        if not self.current_user:
            return {"error": "Authentication required."}
        if target_user not in self.users:
            return {"error": "Target user does not exist."}

        note = self.notes.get(note_id)
        if not note or note.get("in_trash"):
            return {"error": "Note not found or is in trash."}
        if note["owner"] != self.current_user:
            return {"error": "Only the owner can share this note."}

        if target_user not in note["shared_with"]:
            note["shared_with"].append(target_user)

        return {"status": f"Note {note_id} shared with {target_user}."}

    def search_notes(self, keyword: str = "", tag: str = "") -> Dict[str, Union[str, List]]:
        """Search notes by keyword in title/content or by tag.
        
        Args:
            keyword (str): Keyword to search in title or content.
            tag (str): Tag to search for.
            
        Returns:
            Dict: Search results or error.
        """
        if not isinstance(keyword, str) or not isinstance(tag, str):
            return {"error": "keyword and tag must be strings."}

        if not self.current_user:
            return {"error": "Authentication required."}

        results = []
        for note in self.notes.values():
            if note.get("in_trash"):
                continue
            if note["owner"] != self.current_user and self.current_user not in note["shared_with"]:
                continue

            match_keyword = not keyword or (
                        keyword.lower() in note["title"].lower() or keyword.lower() in note["content"].lower())
            match_tag = not tag or (tag in note["tags"])

            if match_keyword and match_tag:
                # Return a summary to avoid massive payloads
                results.append({
                    "id": note["id"],
                    "title": note["title"],
                    "tags": note["tags"],
                    "updated_at": note["updated_at"]
                })
        return {"results": results}

    def read_note(self, note_id: int) -> Dict[str, Union[str, Dict]]:
        """Read the full content and metadata of a specific note.
        
        Args:
            note_id (int): The ID of the note.
            
        Returns:
            Dict: Note content and metadata or error.
        """
        if not isinstance(note_id, int):
            return {"error": "note_id must be an integer."}
        
        if not self.current_user:
            return {"error": "Authentication required."}
            
        note = self.notes.get(note_id)
        if not note:
            return {"error": "Note not found."}
            
        if note.get("in_trash"):
            return {"error": "Note is in trash."}
            
        if note["owner"] != self.current_user and self.current_user not in note["shared_with"]:
            return {"error": "Permission denied."}
            
        return {
            "note": {
                "id": note["id"],
                "notebook_id": note["notebook_id"],
                "title": note["title"],
                "content": note["content"],
                "tags": note["tags"],
                "owner": note["owner"],
                "shared_with": note["shared_with"],
                "created_at": note["created_at"],
                "updated_at": note["updated_at"]
            }
        }

    def list_notebooks(self) -> Dict[str, Union[str, List[Dict]]]:
        """List all notebooks owned by the current user.
        
        Returns:
            Dict: List of notebooks or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        results = []
        for nb in self.notebooks.values():
            if nb["owner"] == self.current_user:
                results.append({"id": nb["id"], "name": nb["name"], "owner": nb["owner"]})
        
        return {"notebooks": results}

    def get_note_history(self, note_id: int) -> Dict[str, Union[str, List[Dict]]]:
        """Get the version history of a specific note.
        
        Args:
            note_id (int): The ID of the note.
            
        Returns:
            Dict: Version history list or error.
        """
        if not isinstance(note_id, int):
            return {"error": "note_id must be an integer."}
            
        if not self.current_user:
            return {"error": "Authentication required."}
            
        note = self.notes.get(note_id)
        if not note:
            return {"error": "Note not found."}
            
        if note["owner"] != self.current_user and self.current_user not in note["shared_with"]:
            return {"error": "Permission denied."}
            
        return {"history": note["version_history"]}

    def restore_note_version(self, note_id: int, version_index: int) -> Dict[str, str]:
        """Restore a note's content to a specific historical version.
        
        Args:
            note_id (int): The ID of the note.
            version_index (int): The index of the version in the history list.
            
        Returns:
            Dict: Status message or error.
        """
        if not isinstance(note_id, int):
            return {"error": "note_id must be an integer."}
        if not isinstance(version_index, int):
            return {"error": "version_index must be an integer."}
            
        if not self.current_user:
            return {"error": "Authentication required."}
            
        note = self.notes.get(note_id)
        if not note or note.get("in_trash"):
            return {"error": "Note not found or is in trash."}
            
        if note["owner"] != self.current_user and self.current_user not in note["shared_with"]:
            return {"error": "Permission denied."}
            
        if version_index < 0 or version_index >= len(note["version_history"]):
            return {"error": "Invalid version_index."}
            
        target_version = note["version_history"][version_index]
        
        # Save current content to history before restoring
        note["version_history"].append({
            "content": note["content"],
            "saved_at": note["updated_at"],
            "edited_by": self.current_user
        })
        
        note["content"] = target_version["content"]
        note["updated_at"] = self._timestamp()
        
        return {"status": f"Note {note_id} restored to version {version_index}."}

    def restore_note(self, note_id: int) -> Dict[str, str]:
        """Restore a note from the trash.
        
        Args:
            note_id (int): The ID of the note.
            
        Returns:
            Dict: Status message or error.
        """
        if not isinstance(note_id, int):
            return {"error": "note_id must be an integer."}
            
        if not self.current_user:
            return {"error": "Authentication required."}
            
        note = self.notes.get(note_id)
        if not note:
            return {"error": "Note not found."}
            
        if not note.get("in_trash"):
            return {"error": "Note is not in trash."}
            
        if note["owner"] != self.current_user:
            return {"error": "Only the owner can restore the note."}
            
        note["in_trash"] = False
        return {"status": f"Note {note_id} restored from trash."}

    def empty_trash(self) -> Dict[str, str]:
        """Permanently delete all notes in the trash for the current user.
        
        Returns:
            Dict: Status message or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        notes_to_delete = []
        for note_id, note in self.notes.items():
            if note.get("in_trash") and note["owner"] == self.current_user:
                notes_to_delete.append(note_id)
                
        for note_id in notes_to_delete:
            del self.notes[note_id]
            
        return {"status": f"Emptied {len(notes_to_delete)} notes from trash."}

    def update_tags(self, note_id: int, tags_to_add: List[str] = None, tags_to_remove: List[str] = None) -> Dict[str, Union[str, List[str]]]:
        """Add or remove tags from an existing note.
        
        Args:
            note_id (int): The ID of the note.
            tags_to_add (List[str]): Tags to add.
            tags_to_remove (List[str]): Tags to remove.
            
        Returns:
            Dict: Status message or error.
        """
        if not isinstance(note_id, int):
            return {"error": "note_id must be an integer."}
        if tags_to_add is not None and not isinstance(tags_to_add, list):
            return {"error": "tags_to_add must be a list."}
        if tags_to_remove is not None and not isinstance(tags_to_remove, list):
            return {"error": "tags_to_remove must be a list."}
            
        if not self.current_user:
            return {"error": "Authentication required."}
            
        note = self.notes.get(note_id)
        if not note or note.get("in_trash"):
            return {"error": "Note not found or is in trash."}
            
        if note["owner"] != self.current_user and self.current_user not in note["shared_with"]:
            return {"error": "Permission denied."}
            
        tags_to_add = tags_to_add or []
        tags_to_remove = tags_to_remove or []
        
        current_tags = set(note["tags"])
        for tag in tags_to_add:
            current_tags.add(tag)
        for tag in tags_to_remove:
            current_tags.discard(tag)
            
        note["tags"] = list(current_tags)
        return {"status": f"Tags updated for note {note_id}.", "tags": note["tags"]}


__TEST_CASES__ = [
    {
        'name': 'Normal path - Create notebook, note, update, search, delete',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['notebook'].create_notebook(name='Travel')"},
            {'expect_success': True, 'tool_call': "env['notebook'].create_note(notebook_id=1, title='Paris Trip', content='Visit Eiffel Tower', tags=['travel', 'france'])"},
            {'expect_success': True, 'tool_call': "env['notebook'].update_note(note_id=102, content='Visit Eiffel Tower and Louvre')"},
            {'expect_success': True, 'tool_call': "env['notebook'].search_notes(keyword='Louvre', tag='travel')"},
            {'expect_success': True, 'tool_call': "env['notebook'].delete_note(note_id=102)"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    },
    {
        'name': 'Normal path - Share note with another user',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['notebook'].share_note(note_id=101, target_user='bob')"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"},
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='bob')"},
            {'expect_success': True, 'tool_call': "env['notebook'].search_notes(keyword='Grocery', tag='')"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    },
    {
        'name': 'Error path - Access methods without login',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"},
            {'expect_success': False, 'tool_call': "env['notebook'].create_notebook(name='Secret')"},
            {'expect_success': False, 'tool_call': "env['notebook'].create_note(notebook_id=1, title='Secret Note', content='Shh', tags=[])"},
            {'expect_success': False, 'tool_call': "env['notebook'].update_note(note_id=101, content='Hacked')"},
            {'expect_success': False, 'tool_call': "env['notebook'].delete_note(note_id=101)"},
            {'expect_success': False, 'tool_call': "env['notebook'].share_note(note_id=101, target_user='charlie')"},
            {'expect_success': False, 'tool_call': "env['notebook'].search_notes(keyword='Grocery', tag='')"}
        ]
    },
    {
        'name': 'Error path - Non-existent IDs for note and notebook operations',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': False, 'tool_call': "env['notebook'].update_note(note_id=9999, content='New')"},
            {'expect_success': False, 'tool_call': "env['notebook'].delete_note(note_id=9999)"},
            {'expect_success': False, 'tool_call': "env['notebook'].share_note(note_id=9999, target_user='bob')"},
            {'expect_success': False, 'tool_call': "env['notebook'].create_note(notebook_id=9999, title='Test', content='Test', tags=[])"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    },
    {
        'name': 'Error path - Share with non-existent user and unauthorized note access',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': False, 'tool_call': "env['notebook'].share_note(note_id=101, target_user='david')"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"},
            {'expect_success': False, 'tool_call': "env['notebook'].login(username='david')"},
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='bob')"},
            {'expect_success': False, 'tool_call': "env['notebook'].update_note(note_id=101, content='Hacked')"},
            {'expect_success': False, 'tool_call': "env['notebook'].delete_note(note_id=101)"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    },
    {
        'name': 'Boundary values - Empty strings for notebook and note creation',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['notebook'].create_notebook(name='')"},
            {'expect_success': True, 'tool_call': "env['notebook'].create_note(notebook_id=1, title='', content='', tags=[])"},
            {'expect_success': True, 'tool_call': "env['notebook'].search_notes(keyword='', tag='')"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    },
    {
        'name': 'Boundary values - Negative IDs and excessively long strings',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['notebook'].create_notebook(name='ThisIsAVeryLongNotebookNameThatMightExceedTypicalDatabaseColumnLimitsForNameFieldsInManyApplications')"},
            {'expect_success': False, 'tool_call': "env['notebook'].create_note(notebook_id=-1, title='Test', content='Test', tags=[])"},
            {'expect_success': False, 'tool_call': "env['notebook'].update_note(note_id=-1, content='Test')"},
            {'expect_success': False, 'tool_call': "env['notebook'].delete_note(note_id=-1)"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    },
    {
        'name': 'State-change verification - Update note and verify state',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['notebook'].update_note(note_id=101, content='Milk, Eggs, Bread, Butter')"},
            {'expect_success': True, 'tool_call': "env['notebook'].search_notes(keyword='Butter', tag='shopping')"},
            {'expect_success': True, 'tool_call': "env['notebook'].get_env_state()"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    },
    {
        'name': 'Cross-method workflow - Alice creates, updates, shares with Charlie',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['notebook'].create_note(notebook_id=1, title='For Charlie', content='Hi Charlie', tags=['chat'])"},
            {'expect_success': True, 'tool_call': "env['notebook'].share_note(note_id=102, target_user='charlie')"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"},
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='charlie')"},
            {'expect_success': True, 'tool_call': "env['notebook'].search_notes(keyword='Charlie', tag='chat')"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    },
    {
        'name': 'Error path - Wrong types and double delete',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': False, 'tool_call': "env['notebook'].create_notebook(name=123)"},
            {'expect_success': False, 'tool_call': "env['notebook'].create_note(notebook_id='one', title='T', content='C', tags='tag')"},
            {'expect_success': True, 'tool_call': "env['notebook'].delete_note(note_id=101)"},
            {'expect_success': False, 'tool_call': "env['notebook'].delete_note(note_id=101)"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    },
    {
        'name': 'New features - read, list_notebooks, version history, tags',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['notebook'].list_notebooks()"},
            {'expect_success': True, 'tool_call': "env['notebook'].update_note(note_id=101, content='Milk, Eggs')"},
            {'expect_success': True, 'tool_call': "env['notebook'].get_note_history(note_id=101)"},
            {'expect_success': True, 'tool_call': "env['notebook'].restore_note_version(note_id=101, version_index=0)"},
            {'expect_success': True, 'tool_call': "env['notebook'].read_note(note_id=101)"},
            {'expect_success': True, 'tool_call': "env['notebook'].update_tags(note_id=101, tags_to_add=['food'], tags_to_remove=['home'])"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    },
    {
        'name': 'New features - trash lifecycle',
        'steps': [
            {'expect_success': True, 'tool_call': "env['notebook'].login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['notebook'].delete_note(note_id=101)"},
            {'expect_success': False, 'tool_call': "env['notebook'].read_note(note_id=101)"},
            {'expect_success': True, 'tool_call': "env['notebook'].restore_note(note_id=101)"},
            {'expect_success': True, 'tool_call': "env['notebook'].read_note(note_id=101)"},
            {'expect_success': True, 'tool_call': "env['notebook'].delete_note(note_id=101)"},
            {'expect_success': True, 'tool_call': "env['notebook'].empty_trash()"},
            {'expect_success': False, 'tool_call': "env['notebook'].restore_note(note_id=101)"},
            {'expect_success': True, 'tool_call': "env['notebook'].logout()"}
        ]
    }
]
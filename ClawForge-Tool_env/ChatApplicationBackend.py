"""
Chat Application Backend Environment API

A stateful environment for managing chat messages, conversations, and users
in a reinforcement learning compatible manner.
"""

from copy import deepcopy
from typing import Dict, List, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    "users": {
        "user_001": {
            "user_id": "user_001",
            "username": "alice",
            "status": "online",
            "is_admin": False
        },
        "user_002": {
            "user_id": "user_002",
            "username": "bob",
            "status": "offline",
            "is_admin": False
        },
        "user_003": {
            "user_id": "user_003",
            "username": "charlie",
            "status": "online",
            "is_admin": True
        },
        "user_004": {
            "user_id": "user_004",
            "username": "diana",
            "status": "online",
            "is_admin": False
        }
    },
    "conversations": {
        "conv_001": {
            "conversation_id": "conv_001",
            "conversation_type": "direct",
            "participant_ids": ["user_001", "user_002"],
            "last_updated": "2024-01-15T10:00:00"
        },
        "conv_002": {
            "conversation_id": "conv_002",
            "conversation_type": "group",
            "participant_ids": ["user_001", "user_002", "user_003"],
            "last_updated": "2024-01-15T11:00:00"
        },
        "conv_003": {
            "conversation_id": "conv_003",
            "conversation_type": "direct",
            "participant_ids": ["user_003", "user_004"],
            "last_updated": "2024-01-15T09:30:00"
        }
    },
    "messages": {
        "msg_001": {
            "message_id": "msg_001",
            "conversation_id": "conv_001",
            "sender_id": "user_001",
            "content": "Hello Bob!",
            "timestamp": "2024-01-15T10:00:00",
            "is_deleted": False
        },
        "msg_002": {
            "message_id": "msg_002",
            "conversation_id": "conv_001",
            "sender_id": "user_002",
            "content": "Hi Alice, how are you?",
            "timestamp": "2024-01-15T10:01:00",
            "is_deleted": False
        },
        "msg_003": {
            "message_id": "msg_003",
            "conversation_id": "conv_002",
            "sender_id": "user_003",
            "content": "Welcome to the group chat!",
            "timestamp": "2024-01-15T11:00:00",
            "is_deleted": False
        },
        "msg_004": {
            "message_id": "msg_004",
            "conversation_id": "conv_002",
            "sender_id": "user_001",
            "content": "Thanks for adding me!",
            "timestamp": "2024-01-15T11:01:00",
            "is_deleted": False
        },
        "msg_005": {
            "message_id": "msg_005",
            "conversation_id": "conv_003",
            "sender_id": "user_004",
            "content": "Hey Charlie!",
            "timestamp": "2024-01-15T09:30:00",
            "is_deleted": True
        }
    },
    "message_logs": {
        "log_001": {
            "log_id": "log_001",
            "message_id": "msg_001",
            "action": "create",
            "timestamp": "2024-01-15T10:00:00",
            "executor_id": "user_001"
        },
        "log_002": {
            "log_id": "log_002",
            "message_id": "msg_002",
            "action": "create",
            "timestamp": "2024-01-15T10:01:00",
            "executor_id": "user_002"
        },
        "log_003": {
            "log_id": "log_003",
            "message_id": "msg_005",
            "action": "delete",
            "timestamp": "2024-01-15T09:35:00",
            "executor_id": "user_004"
        }
    },
    "current_user_id": "user_001",
    "message_id_counter": 6,
    "log_id_counter": 4,
    "conversation_id_counter": 4
}


class ChatApplicationBackend:
    """
    A chat application backend environment for managing users, conversations, 
    and messages with full CRUD operations and audit logging.
    
    This environment supports soft/hard deletion of messages, conversation management,
    and maintains audit trails for message operations.
    """

    def __init__(self) -> None:
        """
        Initialize the ChatApplicationBackend environment.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
        
        Returns:
            None
        """
        self.users: Dict[str, Dict[str, Any]] = {}
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.messages: Dict[str, Dict[str, Any]] = {}
        self.message_logs: Dict[str, Dict[str, Any]] = {}
        self.current_user_id: str = ""
        self.message_id_counter: int = 1
        self.log_id_counter: int = 1
        self.conversation_id_counter: int = 1
        
        self._api_description: str = (
            "A chat application backend API for managing messages, conversations, "
            "and users with support for CRUD operations and audit logging."
        )

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: A dictionary containing initial state values for the environment.
            long_context: Flag for extended context scenarios (unused in basic implementation).
        
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
        Return the current state of the environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables:
                - users: Dict of all registered users
                - conversations: Dict of all conversations
                - messages: Dict of all messages
                - message_logs: Dict of all audit log entries
                - current_user_id: ID of the currently active user
                - message_id_counter: Counter for generating unique message IDs
                - log_id_counter: Counter for generating unique log IDs
                - conversation_id_counter: Counter for generating unique conversation IDs
        """
        return {
            "users": deepcopy(self.users),
            "conversations": deepcopy(self.conversations),
            "messages": deepcopy(self.messages),
            "message_logs": deepcopy(self.message_logs),
            "current_user_id": self.current_user_id,
            "message_id_counter": self.message_id_counter,
            "log_id_counter": self.log_id_counter,
            "conversation_id_counter": self.conversation_id_counter
        }

    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp string.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _generate_message_id(self) -> str:
        """
        Generate a unique message ID.
        
        Args:
            None
        
        Returns:
            str: A unique message ID in format 'msg_XXX'.
        """
        msg_id = f"msg_{self.message_id_counter:03d}"
        self.message_id_counter += 1
        return msg_id

    def _generate_log_id(self) -> str:
        """
        Generate a unique log ID.
        
        Args:
            None
        
        Returns:
            str: A unique log ID in format 'log_XXX'.
        """
        log_id = f"log_{self.log_id_counter:03d}"
        self.log_id_counter += 1
        return log_id

    def _generate_conversation_id(self) -> str:
        """
        Generate a unique conversation ID.
        
        Args:
            None
        
        Returns:
            str: A unique conversation ID in format 'conv_XXX'.
        """
        conv_id = f"conv_{self.conversation_id_counter:03d}"
        self.conversation_id_counter += 1
        return conv_id

    # ==================== QUERY OPERATIONS ====================

    def get_message_by_id(self, message_id: str) -> Dict[str, Any]:
        """
        Retrieve the full message data given a message_id.
        
        Args:
            message_id: The unique identifier of the message to retrieve.
        
        Returns:
            Dict[str, Any]: The message data including sender, content, deletion status,
                           or an error dict if not found.
        """
        if message_id not in self.messages:
            return {"error": f"Message with id '{message_id}' not found"}
        return {"message": deepcopy(self.messages[message_id])}

    def get_message_sender(self, message_id: str) -> Dict[str, Any]:
        """
        Return the sender_id of a message for permission validation.
        
        Args:
            message_id: The unique identifier of the message.
        
        Returns:
            Dict[str, Any]: The sender_id of the message, or an error dict if not found.
        """
        if message_id not in self.messages:
            return {"error": f"Message with id '{message_id}' not found"}
        return {"sender_id": self.messages[message_id]["sender_id"]}

    def check_message_exists(self, message_id: str) -> Dict[str, Any]:
        """
        Verify whether a message with the given message_id exists in the system.
        
        Args:
            message_id: The unique identifier of the message to check.
        
        Returns:
            Dict[str, Any]: A dict with 'exists' boolean indicating presence.
        """
        exists = message_id in self.messages
        return {"exists": exists, "message_id": message_id}

    def check_user_exists(self, user_id: str) -> Dict[str, Any]:
        """
        Confirm that a user (by user_id) is registered in the system.
        
        Args:
            user_id: The unique identifier of the user to check.
        
        Returns:
            Dict[str, Any]: A dict with 'exists' boolean indicating presence.
        """
        exists = user_id in self.users
        return {"exists": exists, "user_id": user_id}

    def check_conversation_exists(self, conversation_id: str) -> Dict[str, Any]:
        """
        Verify that a conversation (by conversation_id) exists.
        
        Args:
            conversation_id: The unique identifier of the conversation to check.
        
        Returns:
            Dict[str, Any]: A dict with 'exists' boolean indicating presence.
        """
        exists = conversation_id in self.conversations
        return {"exists": exists, "conversation_id": conversation_id}

    def list_messages_in_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve all non-deleted messages in a conversation, sorted by timestamp.
        
        Args:
            conversation_id: The unique identifier of the conversation.
        
        Returns:
            Dict[str, Any]: A list of messages sorted by timestamp, 
                           or an error dict if conversation not found.
        """
        if conversation_id not in self.conversations:
            return {"error": f"Conversation with id '{conversation_id}' not found"}
        
        messages = [
            deepcopy(msg) for msg in self.messages.values()
            if msg["conversation_id"] == conversation_id and not msg["is_deleted"]
        ]
        messages.sort(key=lambda x: x["timestamp"])
        return {"messages": messages, "count": len(messages)}

    def check_message_deletion_status(self, message_id: str) -> Dict[str, Any]:
        """
        Determine whether a message is already marked as deleted.
        
        Args:
            message_id: The unique identifier of the message to check.
        
        Returns:
            Dict[str, Any]: A dict with 'is_deleted' boolean, or error if not found.
        """
        if message_id not in self.messages:
            return {"error": f"Message with id '{message_id}' not found"}
        return {
            "is_deleted": self.messages[message_id]["is_deleted"],
            "message_id": message_id
        }

    def get_conversation_participants(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve the list of user_ids participating in a conversation.
        
        Args:
            conversation_id: The unique identifier of the conversation.
        
        Returns:
            Dict[str, Any]: A list of participant user_ids, or error if not found.
        """
        if conversation_id not in self.conversations:
            return {"error": f"Conversation with id '{conversation_id}' not found"}
        return {
            "participant_ids": deepcopy(
                self.conversations[conversation_id]["participant_ids"]
            ),
            "conversation_id": conversation_id
        }

    def is_user_admin(self, user_id: str) -> Dict[str, Any]:
        """
        Check if the requesting user has admin privileges.
        
        Args:
            user_id: The unique identifier of the user to check.
        
        Returns:
            Dict[str, Any]: A dict with 'is_admin' boolean, or error if user not found.
        """
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found"}
        return {
            "is_admin": self.users[user_id].get("is_admin", False),
            "user_id": user_id
        }

    def get_message_audit_log(self, message_id: str) -> Dict[str, Any]:
        """
        Retrieve the log entries for a specific message.
        
        Args:
            message_id: The unique identifier of the message.
        
        Returns:
            Dict[str, Any]: A list of log entries for the message.
        """
        if message_id not in self.messages:
            return {"error": f"Message with id '{message_id}' not found"}
        
        logs = [
            deepcopy(log) for log in self.message_logs.values()
            if log["message_id"] == message_id
        ]
        logs.sort(key=lambda x: x["timestamp"])
        return {"logs": logs, "message_id": message_id}

    # ==================== STATE CHANGE OPERATIONS ====================

    def soft_delete_message(
        self, message_id: str, requester_id: str
    ) -> Dict[str, Any]:
        """
        Set is_deleted = True for a message, preserving metadata.
        
        Only the sender or an admin can delete a message.
        
        Args:
            message_id: The unique identifier of the message to delete.
            requester_id: The user_id of the person requesting deletion.
        
        Returns:
            Dict[str, Any]: Success status or error dict if validation fails.
        """
        if message_id not in self.messages:
            return {"error": f"Message with id '{message_id}' not found"}
        
        if requester_id not in self.users:
            return {"error": f"Requester with id '{requester_id}' not found"}
        
        message = self.messages[message_id]
        
        if message["is_deleted"]:
            return {"error": f"Message '{message_id}' is already deleted"}
        
        is_sender = message["sender_id"] == requester_id
        is_admin = self.users[requester_id].get("is_admin", False)
        
        if not is_sender and not is_admin:
            return {
                "error": "Permission denied: only sender or admin can delete message"
            }
        
        self.messages[message_id]["is_deleted"] = True
        self.log_message_action(message_id, "delete", requester_id)
        
        return {"success": True, "message_id": message_id, "action": "soft_delete"}

    def hard_delete_message(
        self, message_id: str, requester_id: str
    ) -> Dict[str, Any]:
        """
        Permanently remove a message from storage.
        
        Only admins can perform hard delete.
        
        Args:
            message_id: The unique identifier of the message to delete.
            requester_id: The user_id of the person requesting deletion.
        
        Returns:
            Dict[str, Any]: Success status or error dict if validation fails.
        """
        if message_id not in self.messages:
            return {"error": f"Message with id '{message_id}' not found"}
        
        if requester_id not in self.users:
            return {"error": f"Requester with id '{requester_id}' not found"}
        
        is_admin = self.users[requester_id].get("is_admin", False)
        
        if not is_admin:
            return {"error": "Permission denied: only admin can hard delete messages"}
        
        self.log_message_action(message_id, "hard_delete", requester_id)
        del self.messages[message_id]
        
        return {"success": True, "message_id": message_id, "action": "hard_delete"}

    def log_message_action(
        self, message_id: str, action: str, executor_id: str
    ) -> Dict[str, Any]:
        """
        Append a new entry to message_logs to record an action.
        
        Args:
            message_id: The unique identifier of the message.
            action: The action performed (e.g., create, delete, edit).
            executor_id: The user_id of who performed the action.
        
        Returns:
            Dict[str, Any]: The created log entry or error dict.
        """
        if executor_id not in self.users:
            return {"error": f"Executor with id '{executor_id}' not found"}
        
        log_id = self._generate_log_id()
        log_entry = {
            "log_id": log_id,
            "message_id": message_id,
            "action": action,
            "timestamp": self._timestamp(),
            "executor_id": executor_id
        }
        self.message_logs[log_id] = log_entry
        
        return {"success": True, "log": deepcopy(log_entry)}

    def restore_deleted_message(
        self, message_id: str, requester_id: str
    ) -> Dict[str, Any]:
        """
        Revert is_deleted to False if the message was soft-deleted.
        
        Args:
            message_id: The unique identifier of the message to restore.
            requester_id: The user_id of the person requesting restoration.
        
        Returns:
            Dict[str, Any]: Success status or error dict if validation fails.
        """
        if message_id not in self.messages:
            return {"error": f"Message with id '{message_id}' not found"}
        
        if requester_id not in self.users:
            return {"error": f"Requester with id '{requester_id}' not found"}
        
        message = self.messages[message_id]
        
        if not message["is_deleted"]:
            return {"error": f"Message '{message_id}' is not deleted"}
        
        is_sender = message["sender_id"] == requester_id
        is_admin = self.users[requester_id].get("is_admin", False)
        
        if not is_sender and not is_admin:
            return {
                "error": "Permission denied: only sender or admin can restore message"
            }
        
        self.messages[message_id]["is_deleted"] = False
        self.log_message_action(message_id, "restore", requester_id)
        
        return {"success": True, "message_id": message_id, "action": "restore"}

    def send_new_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Create and store a new message with unique message_id.
        
        Args:
            conversation_id: The conversation to add the message to.
            sender_id: The user_id of the message sender.
            content: The text content of the message.
        
        Returns:
            Dict[str, Any]: The created message or error dict if validation fails.
        """
        if conversation_id not in self.conversations:
            return {"error": f"Conversation with id '{conversation_id}' not found"}
        
        if sender_id not in self.users:
            return {"error": f"Sender with id '{sender_id}' not found"}
        
        conv = self.conversations[conversation_id]
        if sender_id not in conv["participant_ids"]:
            return {
                "error": f"User '{sender_id}' is not a participant in conversation"
            }
        
        if not content or not content.strip():
            return {"error": "Message content cannot be empty"}
        
        message_id = self._generate_message_id()
        timestamp = self._timestamp()
        
        message = {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "sender_id": sender_id,
            "content": content,
            "timestamp": timestamp,
            "is_deleted": False
        }
        
        self.messages[message_id] = message
        self.conversations[conversation_id]["last_updated"] = timestamp
        self.log_message_action(message_id, "create", sender_id)
        
        return {"success": True, "message": deepcopy(message)}

    def update_message_content(
        self,
        message_id: str,
        new_content: str,
        requester_id: str
    ) -> Dict[str, Any]:
        """
        Modify the content of an existing message.
        
        Only the sender can edit their own message.
        
        Args:
            message_id: The unique identifier of the message to update.
            new_content: The new text content for the message.
            requester_id: The user_id of the person requesting the edit.
        
        Returns:
            Dict[str, Any]: Success status or error dict if validation fails.
        """
        if message_id not in self.messages:
            return {"error": f"Message with id '{message_id}' not found"}
        
        if requester_id not in self.users:
            return {"error": f"Requester with id '{requester_id}' not found"}
        
        message = self.messages[message_id]
        
        if message["is_deleted"]:
            return {"error": "Cannot edit a deleted message"}
        
        if message["sender_id"] != requester_id:
            return {"error": "Permission denied: only sender can edit the message"}
        
        if not new_content or not new_content.strip():
            return {"error": "Message content cannot be empty"}
        
        self.messages[message_id]["content"] = new_content
        self.log_message_action(message_id, "edit", requester_id)
        
        return {
            "success": True,
            "message_id": message_id,
            "new_content": new_content
        }

    def purge_deleted_messages(self, requester_id: str) -> Dict[str, Any]:
        """
        Batch-remove messages marked as deleted (admin operation).
        
        Args:
            requester_id: The user_id of the admin requesting the purge.
        
        Returns:
            Dict[str, Any]: Count of purged messages or error dict.
        """
        if requester_id not in self.users:
            return {"error": f"Requester with id '{requester_id}' not found"}
        
        is_admin = self.users[requester_id].get("is_admin", False)
        if not is_admin:
            return {"error": "Permission denied: only admin can purge messages"}
        
        deleted_ids = [
            msg_id for msg_id, msg in self.messages.items()
            if msg["is_deleted"]
        ]
        
        for msg_id in deleted_ids:
            self.log_message_action(msg_id, "purge", requester_id)
            del self.messages[msg_id]
        
        return {"success": True, "purged_count": len(deleted_ids)}

    def create_conversation(
        self,
        conversation_type: str,
        participant_ids: List[str],
        creator_id: str
    ) -> Dict[str, Any]:
        """
        Initialize a new conversation (direct or group) with participant list.
        
        Args:
            conversation_type: Type of conversation ('direct' or 'group').
            participant_ids: List of user_ids to include in the conversation.
            creator_id: The user_id of the conversation creator.
        
        Returns:
            Dict[str, Any]: The created conversation or error dict.
        """
        if conversation_type not in ["direct", "group"]:
            return {"error": "Conversation type must be 'direct' or 'group'"}
        
        if creator_id not in self.users:
            return {"error": f"Creator with id '{creator_id}' not found"}
        
        for user_id in participant_ids:
            if user_id not in self.users:
                return {"error": f"Participant with id '{user_id}' not found"}
        
        # Make a copy to avoid modifying the input list
        final_participants = list(participant_ids)
        if creator_id not in final_participants:
            final_participants = [creator_id] + final_participants
        
        if conversation_type == "direct" and len(final_participants) != 2:
            return {"error": "Direct conversation must have exactly 2 participants"}
        
        if conversation_type == "group" and len(final_participants) < 2:
            return {"error": "Group conversation must have at least 2 participants"}
        
        conversation_id = self._generate_conversation_id()
        conversation = {
            "conversation_id": conversation_id,
            "conversation_type": conversation_type,
            "participant_ids": final_participants,
            "last_updated": self._timestamp()
        }
        
        self.conversations[conversation_id] = conversation
        
        return {"success": True, "conversation": deepcopy(conversation)}

    def add_user_to_conversation(
        self,
        conversation_id: str,
        user_id: str,
        requester_id: str
    ) -> Dict[str, Any]:
        """
        Add a user to an existing group conversation.
        
        Args:
            conversation_id: The unique identifier of the conversation.
            user_id: The user_id to add to the conversation.
            requester_id: The user_id of the person making the request.
        
        Returns:
            Dict[str, Any]: Success status or error dict if validation fails.
        """
        if conversation_id not in self.conversations:
            return {"error": f"Conversation with id '{conversation_id}' not found"}
        
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found"}
        
        if requester_id not in self.users:
            return {"error": f"Requester with id '{requester_id}' not found"}
        
        conv = self.conversations[conversation_id]
        
        if conv["conversation_type"] != "group":
            return {"error": "Can only add users to group conversations"}
        
        if requester_id not in conv["participant_ids"]:
            is_admin = self.users[requester_id].get("is_admin", False)
            if not is_admin:
                return {
                    "error": "Permission denied: must be participant or admin"
                }
        
        if user_id in conv["participant_ids"]:
            return {"error": f"User '{user_id}' is already in the conversation"}
        
        self.conversations[conversation_id]["participant_ids"].append(user_id)
        self.conversations[conversation_id]["last_updated"] = self._timestamp()
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "added_user_id": user_id
        }

    def remove_user_from_conversation(
        self,
        conversation_id: str,
        user_id: str,
        requester_id: str
    ) -> Dict[str, Any]:
        """
        Remove a participant from a group conversation.
        
        Args:
            conversation_id: The unique identifier of the conversation.
            user_id: The user_id to remove from the conversation.
            requester_id: The user_id of the person making the request.
        
        Returns:
            Dict[str, Any]: Success status or error dict if validation fails.
        """
        if conversation_id not in self.conversations:
            return {"error": f"Conversation with id '{conversation_id}' not found"}
        
        if user_id not in self.users:
            return {"error": f"User with id '{user_id}' not found"}
        
        if requester_id not in self.users:
            return {"error": f"Requester with id '{requester_id}' not found"}
        
        conv = self.conversations[conversation_id]
        
        if conv["conversation_type"] != "group":
            return {"error": "Can only remove users from group conversations"}
        
        is_self_removal = user_id == requester_id
        is_admin = self.users[requester_id].get("is_admin", False)
        is_participant = requester_id in conv["participant_ids"]
        
        if not is_self_removal and not is_admin and not is_participant:
            return {"error": "Permission denied: insufficient privileges"}
        
        if user_id not in conv["participant_ids"]:
            return {"error": f"User '{user_id}' is not in the conversation"}
        
        if len(conv["participant_ids"]) <= 2:
            return {
                "error": "Cannot remove user: group must have at least 2 participants"
            }
        
        self.conversations[conversation_id]["participant_ids"].remove(user_id)
        self.conversations[conversation_id]["last_updated"] = self._timestamp()
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "removed_user_id": user_id
        }


__TEST_CASES__ = [
    {
        "name": "Send message and retrieve it",
        "steps": [
            {
                "tool_call": "send_new_message(conversation_id='conv_001', sender_id='user_001', content='Test message')",
                "expect_success": True
            },
            {
                "tool_call": "get_message_by_id(message_id='msg_006')",
                "expect_success": True
            },
            {
                "tool_call": "list_messages_in_conversation(conversation_id='conv_001')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Soft delete and restore message flow",
        "steps": [
            {
                "tool_call": "soft_delete_message(message_id='msg_001', requester_id='user_001')",
                "expect_success": True
            },
            {
                "tool_call": "get_message_by_id(message_id='msg_001')",
                "expect_success": True
            },
            {
                "tool_call": "restore_deleted_message(message_id='msg_001', requester_id='user_001')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Create group conversation and manage participants",
        "steps": [
            {
                "tool_call": "create_group_conversation(creator_id='user_001', participant_ids=['user_001', 'user_002', 'user_003'], group_name='Test Group')",
                "expect_success": True
            },
            {
                "tool_call": "add_user_to_conversation(conversation_id='conv_004', user_id='user_004', requester_id='user_001')",
                "expect_success": True
            },
            {
                "tool_call": "remove_user_from_conversation(conversation_id='conv_004', user_id='user_003', requester_id='user_001')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Edit message content",
        "steps": [
            {
                "tool_call": "send_new_message(conversation_id='conv_001', sender_id='user_001', content='Original content')",
                "expect_success": True
            },
            {
                "tool_call": "edit_message_content(message_id='msg_006', requester_id='user_001', new_content='Edited content')",
                "expect_success": True
            },
            {
                "tool_call": "get_message_by_id(message_id='msg_006')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Mark messages as read",
        "steps": [
            {
                "tool_call": "mark_message_as_read(message_id='msg_002', user_id='user_001')",
                "expect_success": True
            },
            {
                "tool_call": "get_message_by_id(message_id='msg_002')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Search messages in conversation",
        "steps": [
            {
                "tool_call": "search_messages_in_conversation(conversation_id='conv_001', query='hello')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Get user conversations",
        "steps": [
            {
                "tool_call": "get_user_conversations(user_id='user_001')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Error handling - invalid user",
        "steps": [
            {
                "tool_call": "send_new_message(conversation_id='conv_001', sender_id='invalid_user', content='Test')",
                "expect_success": False
            }
        ]
    },
    {
        "name": "Error handling - invalid conversation",
        "steps": [
            {
                "tool_call": "list_messages_in_conversation(conversation_id='invalid_conv')",
                "expect_success": False
            }
        ]
    },
    {
        "name": "Error handling - permission denied for edit",
        "steps": [
            {
                "tool_call": "edit_message_content(message_id='msg_001', requester_id='user_002', new_content='Hacked')",
                "expect_success": False
            }
        ]
    },
    {
        "name": "Create direct conversation",
        "steps": [
            {
                "tool_call": "create_direct_conversation(user_id_1='user_001', user_id_2='user_004')",
                "expect_success": True
            },
            {
                "tool_call": "get_conversation_details(conversation_id='conv_004')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Get unread message count",
        "steps": [
            {
                "tool_call": "get_unread_message_count(user_id='user_002', conversation_id='conv_001')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Pin and unpin message",
        "steps": [
            {
                "tool_call": "pin_message(message_id='msg_001', requester_id='user_001')",
                "expect_success": True
            },
            {
                "tool_call": "get_pinned_messages(conversation_id='conv_001')",
                "expect_success": True
            },
            {
                "tool_call": "unpin_message(message_id='msg_001', requester_id='user_001')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Add and remove reaction",
        "steps": [
            {
                "tool_call": "add_reaction_to_message(message_id='msg_001', user_id='user_002', reaction='👍')",
                "expect_success": True
            },
            {
                "tool_call": "get_message_by_id(message_id='msg_001')",
                "expect_success": True
            },
            {
                "tool_call": "remove_reaction_from_message(message_id='msg_001', user_id='user_002', reaction='👍')",
                "expect_success": True
            }
        ]
    },
    {
        "name": "Reply to message thread",
        "steps": [
            {
                "tool_call": "reply_to_message(parent_message_id='msg_001', sender_id='user_002', content='This is a reply')",
                "expect_success": True
            },
            {
                "tool_call": "get_message_thread(parent_message_id='msg_001')",
                "expect_success": True
            }
        ]
    }
]
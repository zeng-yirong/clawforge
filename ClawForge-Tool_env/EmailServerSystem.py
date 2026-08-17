"""
Email Server System Environment API

An email server system manages the storage, retrieval, and organization of email messages
for users, maintaining state across sessions. It supports structured mailboxes such as
inbox, sent, and archive, each containing messages with associated metadata.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

# Default initial state with sample data
DEFAULT_STATE: Dict[str, Any] = {
    "users": [
        {
            "_id": "user_001",
            "email_address": "alice@example.com",
            "password_hash": "hashed_password_alice",
            "account_preferences": {"theme": "light", "notifications": True}
        },
        {
            "_id": "user_002",
            "email_address": "bob@example.com",
            "password_hash": "hashed_password_bob",
            "account_preferences": {"theme": "dark", "notifications": False}
        },
        {
            "_id": "user_003",
            "email_address": "charlie@example.com",
            "password_hash": "hashed_password_charlie",
            "account_preferences": {"theme": "light", "notifications": True}
        }
    ],
    "mailboxes": [
        {"mailbox_id": "mbx_001", "user_id": "user_001", "name": "inbox", "message_count": 2},
        {"mailbox_id": "mbx_002", "user_id": "user_001", "name": "sent", "message_count": 1},
        {"mailbox_id": "mbx_003", "user_id": "user_001", "name": "archive", "message_count": 0},
        {"mailbox_id": "mbx_004", "user_id": "user_001", "name": "trash", "message_count": 0},
        {"mailbox_id": "mbx_005", "user_id": "user_002", "name": "inbox", "message_count": 1},
        {"mailbox_id": "mbx_006", "user_id": "user_002", "name": "sent", "message_count": 1},
        {"mailbox_id": "mbx_007", "user_id": "user_002", "name": "archive", "message_count": 0},
        {"mailbox_id": "mbx_008", "user_id": "user_002", "name": "trash", "message_count": 0},
        {"mailbox_id": "mbx_009", "user_id": "user_003", "name": "inbox", "message_count": 1},
        {"mailbox_id": "mbx_010", "user_id": "user_003", "name": "sent", "message_count": 0},
        {"mailbox_id": "mbx_011", "user_id": "user_003", "name": "archive", "message_count": 0},
        {"mailbox_id": "mbx_012", "user_id": "user_003", "name": "trash", "message_count": 0}
    ],
    "messages": [
        {
            "message_id": "msg_001",
            "mailbox_id": "mbx_001",
            "sender": "bob@example.com",
            "recipient": "alice@example.com",
            "subject": "Meeting Tomorrow",
            "body_preview": "Hi Alice, can we meet tomorrow at 10am?",
            "timestamp": "2024-01-15T09:30:00",
            "is_read": False,
            "size": 1024,
            "original_mailbox_id": None
        },
        {
            "message_id": "msg_002",
            "mailbox_id": "mbx_001",
            "sender": "charlie@example.com",
            "recipient": "alice@example.com",
            "subject": "Project Update",
            "body_preview": "Here is the latest update on our project...",
            "timestamp": "2024-01-14T14:20:00",
            "is_read": True,
            "size": 2048,
            "original_mailbox_id": None
        },
        {
            "message_id": "msg_003",
            "mailbox_id": "mbx_002",
            "sender": "alice@example.com",
            "recipient": "bob@example.com",
            "subject": "Re: Meeting Tomorrow",
            "body_preview": "Sure, 10am works for me!",
            "timestamp": "2024-01-15T10:00:00",
            "is_read": True,
            "size": 512,
            "original_mailbox_id": None
        },
        {
            "message_id": "msg_004",
            "mailbox_id": "mbx_005",
            "sender": "alice@example.com",
            "recipient": "bob@example.com",
            "subject": "Re: Meeting Tomorrow",
            "body_preview": "Sure, 10am works for me!",
            "timestamp": "2024-01-15T10:00:00",
            "is_read": False,
            "size": 512,
            "original_mailbox_id": None
        },
        {
            "message_id": "msg_005",
            "mailbox_id": "mbx_006",
            "sender": "bob@example.com",
            "recipient": "alice@example.com",
            "subject": "Meeting Tomorrow",
            "body_preview": "Hi Alice, can we meet tomorrow at 10am?",
            "timestamp": "2024-01-15T09:30:00",
            "is_read": True,
            "size": 1024,
            "original_mailbox_id": None
        },
        {
            "message_id": "msg_006",
            "mailbox_id": "mbx_009",
            "sender": "alice@example.com",
            "recipient": "charlie@example.com",
            "subject": "Welcome aboard",
            "body_preview": "Welcome to the team, Charlie!",
            "timestamp": "2024-01-10T08:00:00",
            "is_read": True,
            "size": 256,
            "original_mailbox_id": None
        }
    ],
    "current_user_id": None,
    "next_message_id": 7,
    "next_mailbox_id": 13
}


class EmailServerSystem:
    """
    Email Server System Environment API.
    
    Manages email storage, retrieval, and organization for users with support
    for structured mailboxes and message operations.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Email Server System environment.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Returns:
            None
        """
        self.users: List[Dict[str, Any]] = []
        self.mailboxes: List[Dict[str, Any]] = []
        self.messages: List[Dict[str, Any]] = []
        self.current_user_id: Optional[str] = None
        self.next_message_id: int = 1
        self.next_mailbox_id: int = 1
        
        self._api_description: str = (
            "An email server system API for managing user mailboxes and messages, "
            "supporting operations like sending, receiving, organizing, and searching emails."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a unified ISO format timestamp string.
        
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
            scenario: Dictionary containing initial state data.
            long_context: Flag for long context scenarios (reserved for future use).
        
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
        Return a dictionary containing the current environment state.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary with all internal state variables including:
                - users: List of user accounts
                - mailboxes: List of mailbox folders
                - messages: List of email messages
                - current_user_id: Currently active user ID
                - next_message_id: Next available message ID counter
                - next_mailbox_id: Next available mailbox ID counter
        """
        return {
            "users": deepcopy(self.users),
            "mailboxes": deepcopy(self.mailboxes),
            "messages": deepcopy(self.messages),
            "current_user_id": self.current_user_id,
            "next_message_id": self.next_message_id,
            "next_mailbox_id": self.next_mailbox_id
        }
    
    # ==================== Query Operations ====================
    
    def get_user_by_email(self, email_address: str) -> Dict[str, Any]:
        """
        Retrieve user information using the email address.
        
        Args:
            email_address: The email address to search for.
            
        Returns:
            Dict[str, Any]: User information if found, or error dictionary.
        """
        for user in self.users:
            if user["email_address"] == email_address:
                return {"user": deepcopy(user)}
        return {"error": f"User with email '{email_address}' not found"}
    
    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user information by unique user ID.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            Dict[str, Any]: User information if found, or error dictionary.
        """
        for user in self.users:
            if user["_id"] == user_id:
                return {"user": deepcopy(user)}
        return {"error": f"User with ID '{user_id}' not found"}
    
    def list_user_mailboxes(self, user_id: str) -> Dict[str, Any]:
        """
        List all mailboxes associated with a user.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            Dict[str, Any]: List of mailboxes or error dictionary.
        """
        user_exists = any(u["_id"] == user_id for u in self.users)
        if not user_exists:
            return {"error": f"User with ID '{user_id}' not found"}
        
        mailboxes = [mb for mb in self.mailboxes if mb["user_id"] == user_id]
        return {"mailboxes": deepcopy(mailboxes)}
    
    def get_mailbox_by_name(self, user_id: str, mailbox_name: str) -> Dict[str, Any]:
        """
        Retrieve a specific mailbox for a user by name.
        
        Args:
            user_id: The unique identifier of the user.
            mailbox_name: The name of the mailbox (e.g., "inbox", "sent").
            
        Returns:
            Dict[str, Any]: Mailbox information or error dictionary.
        """
        user_exists = any(u["_id"] == user_id for u in self.users)
        if not user_exists:
            return {"error": f"User with ID '{user_id}' not found"}
        
        for mb in self.mailboxes:
            if mb["user_id"] == user_id and mb["name"] == mailbox_name:
                return {"mailbox": deepcopy(mb)}
        return {"error": f"Mailbox '{mailbox_name}' not found for user '{user_id}'"}
    
    def get_inbox_message_count(self, user_id: str) -> Dict[str, Any]:
        """
        Return the current number of messages in the user's inbox.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            Dict[str, Any]: Message count or error dictionary.
        """
        result = self.get_mailbox_by_name(user_id, "inbox")
        if "error" in result:
            return result
        return {"message_count": result["mailbox"]["message_count"]}
    
    def get_mailbox_message_count(self, user_id: str, mailbox_name: str) -> Dict[str, Any]:
        """
        Get the number of messages in a specified mailbox.
        
        Args:
            user_id: The unique identifier of the user.
            mailbox_name: The name of the mailbox.
            
        Returns:
            Dict[str, Any]: Message count or error dictionary.
        """
        result = self.get_mailbox_by_name(user_id, mailbox_name)
        if "error" in result:
            return result
        return {"message_count": result["mailbox"]["message_count"]}
    
    def list_messages_in_mailbox(self, mailbox_id: str) -> Dict[str, Any]:
        """
        Retrieve a list of all messages in a given mailbox with metadata.
        
        Args:
            mailbox_id: The unique identifier of the mailbox.
            
        Returns:
            Dict[str, Any]: List of messages with metadata or error dictionary.
        """
        mailbox_exists = any(mb["mailbox_id"] == mailbox_id for mb in self.mailboxes)
        if not mailbox_exists:
            return {"error": f"Mailbox with ID '{mailbox_id}' not found"}
        
        messages = []
        for msg in self.messages:
            if msg["mailbox_id"] == mailbox_id:
                messages.append({
                    "message_id": msg["message_id"],
                    "sender": msg["sender"],
                    "subject": msg["subject"],
                    "timestamp": msg["timestamp"],
                    "is_read": msg["is_read"]
                })
        return {"messages": messages}
    
    def get_message_details(self, message_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a specific message by message_id.
        
        Args:
            message_id: The unique identifier of the message.
            
        Returns:
            Dict[str, Any]: Full message details or error dictionary.
        """
        for msg in self.messages:
            if msg["message_id"] == message_id:
                return {"message": deepcopy(msg)}
        return {"error": f"Message with ID '{message_id}' not found"}
    
    def search_messages_by_sender(self, mailbox_id: str, sender_email: str) -> Dict[str, Any]:
        """
        Find messages in a mailbox from a specific sender.
        
        Args:
            mailbox_id: The unique identifier of the mailbox.
            sender_email: The email address of the sender to search for.
            
        Returns:
            Dict[str, Any]: List of matching messages or error dictionary.
        """
        mailbox_exists = any(mb["mailbox_id"] == mailbox_id for mb in self.mailboxes)
        if not mailbox_exists:
            return {"error": f"Mailbox with ID '{mailbox_id}' not found"}
        
        messages = []
        for msg in self.messages:
            if msg["mailbox_id"] == mailbox_id and msg["sender"] == sender_email:
                messages.append(deepcopy(msg))
        return {"messages": messages}
    
    def search_messages_by_subject(self, mailbox_id: str, keyword: str) -> Dict[str, Any]:
        """
        Search for messages containing a keyword in the subject line.
        
        Args:
            mailbox_id: The unique identifier of the mailbox.
            keyword: The keyword to search for in subject lines.
            
        Returns:
            Dict[str, Any]: List of matching messages or error dictionary.
        """
        mailbox_exists = any(mb["mailbox_id"] == mailbox_id for mb in self.mailboxes)
        if not mailbox_exists:
            return {"error": f"Mailbox with ID '{mailbox_id}' not found"}
        
        messages = []
        for msg in self.messages:
            if msg["mailbox_id"] == mailbox_id and keyword.lower() in msg["subject"].lower():
                messages.append(deepcopy(msg))
        return {"messages": messages}
    
    def count_unread_messages(self, mailbox_id: str) -> Dict[str, Any]:
        """
        Count the number of unread messages in a specified mailbox.
        
        Args:
            mailbox_id: The unique identifier of the mailbox.
            
        Returns:
            Dict[str, Any]: Count of unread messages or error dictionary.
        """
        mailbox_exists = any(mb["mailbox_id"] == mailbox_id for mb in self.mailboxes)
        if not mailbox_exists:
            return {"error": f"Mailbox with ID '{mailbox_id}' not found"}
        
        count = sum(1 for msg in self.messages 
                    if msg["mailbox_id"] == mailbox_id and not msg["is_read"])
        return {"unread_count": count}
    
    # ==================== State Change Operations ====================
    
    def receive_new_message(
        self,
        recipient_email: str,
        sender_email: str,
        subject: str,
        body_preview: str,
        size: int = 1024
    ) -> Dict[str, Any]:
        """
        Add a new incoming message to the recipient's inbox.
        
        Args:
            recipient_email: Email address of the recipient.
            sender_email: Email address of the sender.
            subject: Subject line of the message.
            body_preview: Preview of the message body.
            size: Size of the message in bytes.
            
        Returns:
            Dict[str, Any]: Created message details or error dictionary.
        """
        recipient = None
        for user in self.users:
            if user["email_address"] == recipient_email:
                recipient = user
                break
        
        if not recipient:
            return {"error": f"Recipient '{recipient_email}' not found"}
        
        inbox = None
        for mb in self.mailboxes:
            if mb["user_id"] == recipient["_id"] and mb["name"] == "inbox":
                inbox = mb
                break
        
        if not inbox:
            return {"error": f"Inbox not found for recipient '{recipient_email}'"}
        
        message_id = f"msg_{self.next_message_id:03d}"
        self.next_message_id += 1
        
        new_message = {
            "message_id": message_id,
            "mailbox_id": inbox["mailbox_id"],
            "sender": sender_email,
            "recipient": recipient_email,
            "subject": subject,
            "body_preview": body_preview,
            "timestamp": self._timestamp(),
            "is_read": False,
            "size": size,
            "original_mailbox_id": None
        }
        
        self.messages.append(new_message)
        inbox["message_count"] += 1
        
        return {"success": True, "message": deepcopy(new_message)}
    
    def send_message(
        self,
        sender_email: str,
        recipient_email: str,
        subject: str,
        body_preview: str,
        size: int = 1024
    ) -> Dict[str, Any]:
        """
        Create a new message in the sender's sent mailbox and deliver to recipient's inbox.
        
        Args:
            sender_email: Email address of the sender.
            recipient_email: Email address of the recipient.
            subject: Subject line of the message.
            body_preview: Preview of the message body.
            size: Size of the message in bytes.
            
        Returns:
            Dict[str, Any]: Created messages details or error dictionary.
        """
        sender = None
        for user in self.users:
            if user["email_address"] == sender_email:
                sender = user
                break
        
        if not sender:
            return {"error": f"Sender '{sender_email}' not found"}
        
        recipient = None
        for user in self.users:
            if user["email_address"] == recipient_email:
                recipient = user
                break
        
        if not recipient:
            return {"error": f"Recipient '{recipient_email}' not found"}
        
        sent_mailbox = None
        for mb in self.mailboxes:
            if mb["user_id"] == sender["_id"] and mb["name"] == "sent":
                sent_mailbox = mb
                break
        
        if not sent_mailbox:
            return {"error": f"Sent mailbox not found for sender '{sender_email}'"}
        
        recipient_inbox = None
        for mb in self.mailboxes:
            if mb["user_id"] == recipient["_id"] and mb["name"] == "inbox":
                recipient_inbox = mb
                break
        
        if not recipient_inbox:
            return {"error": f"Inbox not found for recipient '{recipient_email}'"}
        
        timestamp = self._timestamp()
        
        sent_msg_id = f"msg_{self.next_message_id:03d}"
        self.next_message_id += 1
        
        sent_message = {
            "message_id": sent_msg_id,
            "mailbox_id": sent_mailbox["mailbox_id"],
            "sender": sender_email,
            "recipient": recipient_email,
            "subject": subject,
            "body_preview": body_preview,
            "timestamp": timestamp,
            "is_read": True,
            "size": size,
            "original_mailbox_id": None
        }
        
        inbox_msg_id = f"msg_{self.next_message_id:03d}"
        self.next_message_id += 1
        
        inbox_message = {
            "message_id": inbox_msg_id,
            "mailbox_id": recipient_inbox["mailbox_id"],
            "sender": sender_email,
            "recipient": recipient_email,
            "subject": subject,
            "body_preview": body_preview,
            "timestamp": timestamp,
            "is_read": False,
            "size": size,
            "original_mailbox_id": None
        }
        
        self.messages.append(sent_message)
        self.messages.append(inbox_message)
        sent_mailbox["message_count"] += 1
        recipient_inbox["message_count"] += 1
        
        return {
            "success": True,
            "sent_message": deepcopy(sent_message),
            "delivered_message": deepcopy(inbox_message)
        }
    
    def move_message(self, message_id: str, target_mailbox_id: str) -> Dict[str, Any]:
        """
        Move a message from one mailbox to another.
        
        Args:
            message_id: The unique identifier of the message to move.
            target_mailbox_id: The ID of the destination mailbox.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        message = None
        for msg in self.messages:
            if msg["message_id"] == message_id:
                message = msg
                break
        
        if not message:
            return {"error": f"Message with ID '{message_id}' not found"}
        
        target_mailbox = None
        for mb in self.mailboxes:
            if mb["mailbox_id"] == target_mailbox_id:
                target_mailbox = mb
                break
        
        if not target_mailbox:
            return {"error": f"Target mailbox with ID '{target_mailbox_id}' not found"}
        
        source_mailbox = None
        for mb in self.mailboxes:
            if mb["mailbox_id"] == message["mailbox_id"]:
                source_mailbox = mb
                break
        
        if not source_mailbox:
            return {"error": "Source mailbox not found"}
        
        if source_mailbox["user_id"] != target_mailbox["user_id"]:
            return {"error": "Cannot move message to a mailbox belonging to a different user"}
        
        if message["mailbox_id"] == target_mailbox_id:
            return {"error": "Message is already in the target mailbox"}
        
        if target_mailbox["name"] == "trash" and message["original_mailbox_id"] is None:
            message["original_mailbox_id"] = message["mailbox_id"]
        
        source_mailbox["message_count"] -= 1
        message["mailbox_id"] = target_mailbox_id
        target_mailbox["message_count"] += 1
        
        return {"success": True, "message_id": message_id, "new_mailbox_id": target_mailbox_id}
    
    def delete_message(self, message_id: str) -> Dict[str, Any]:
        """
        Remove a message from a mailbox and decrement the mailbox's message_count.
        
        Args:
            message_id: The unique identifier of the message to delete.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        message_index = None
        message = None
        for i, msg in enumerate(self.messages):
            if msg["message_id"] == message_id:
                message_index = i
                message = msg
                break
        
        if message is None:
            return {"error": f"Message with ID '{message_id}' not found"}
        
        for mb in self.mailboxes:
            if mb["mailbox_id"] == message["mailbox_id"]:
                mb["message_count"] -= 1
                break
        
        self.messages.pop(message_index)
        
        return {"success": True, "deleted_message_id": message_id}
    
    def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Update the is_read status of a message to True.
        
        Args:
            message_id: The unique identifier of the message.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        for msg in self.messages:
            if msg["message_id"] == message_id:
                msg["is_read"] = True
                return {"success": True, "message_id": message_id, "is_read": True}
        
        return {"error": f"Message with ID '{message_id}' not found"}
    
    def mark_message_as_unread(self, message_id: str) -> Dict[str, Any]:
        """
        Update the is_read status of a message to False.
        
        Args:
            message_id: The unique identifier of the message.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        for msg in self.messages:
            if msg["message_id"] == message_id:
                msg["is_read"] = False
                return {"success": True, "message_id": message_id, "is_read": False}
        
        return {"error": f"Message with ID '{message_id}' not found"}
    
    def create_mailbox(self, user_id: str, mailbox_name: str) -> Dict[str, Any]:
        """
        Create a new custom mailbox for a user.
        
        Args:
            user_id: The unique identifier of the user.
            mailbox_name: The name for the new mailbox.
            
        Returns:
            Dict[str, Any]: Created mailbox details or error dictionary.
        """
        user_exists = any(u["_id"] == user_id for u in self.users)
        if not user_exists:
            return {"error": f"User with ID '{user_id}' not found"}
        
        for mb in self.mailboxes:
            if mb["user_id"] == user_id and mb["name"] == mailbox_name:
                return {"error": f"Mailbox '{mailbox_name}' already exists for this user"}
        
        mailbox_id = f"mbx_{self.next_mailbox_id:03d}"
        self.next_mailbox_id += 1
        
        new_mailbox = {
            "mailbox_id": mailbox_id,
            "user_id": user_id,
            "name": mailbox_name,
            "message_count": 0
        }
        
        self.mailboxes.append(new_mailbox)
        
        return {"success": True, "mailbox": deepcopy(new_mailbox)}
    
    def delete_mailbox(self, mailbox_id: str) -> Dict[str, Any]:
        """
        Delete a user's custom mailbox (not allowed for default inbox).
        
        Args:
            mailbox_id: The unique identifier of the mailbox to delete.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        mailbox_index = None
        mailbox = None
        for i, mb in enumerate(self.mailboxes):
            if mb["mailbox_id"] == mailbox_id:
                mailbox_index = i
                mailbox = mb
                break
        
        if mailbox is None:
            return {"error": f"Mailbox with ID '{mailbox_id}' not found"}
        
        protected_mailboxes = ["inbox", "sent", "archive", "trash"]
        if mailbox["name"] in protected_mailboxes:
            return {"error": f"Cannot delete the default '{mailbox['name']}' mailbox"}
        
        if mailbox["message_count"] > 0:
            return {"error": "Cannot delete mailbox that contains messages. Move or delete messages first."}
        
        self.mailboxes.pop(mailbox_index)
        
        return {"success": True, "deleted_mailbox_id": mailbox_id}
    
    def empty_trash(self, user_id: str) -> Dict[str, Any]:
        """
        Permanently delete all messages in the user's trash mailbox.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            Dict[str, Any]: Success status with count of deleted messages or error dictionary.
        """
        user_exists = any(u["_id"] == user_id for u in self.users)
        if not user_exists:
            return {"error": f"User with ID '{user_id}' not found"}
        
        trash_mailbox = None
        for mb in self.mailboxes:
            if mb["user_id"] == user_id and mb["name"] == "trash":
                trash_mailbox = mb
                break
        
        if not trash_mailbox:
            return {"error": f"Trash mailbox not found for user '{user_id}'"}
        
        deleted_count = 0
        messages_to_keep = []
        for msg in self.messages:
            if msg["mailbox_id"] == trash_mailbox["mailbox_id"]:
                deleted_count += 1
            else:
                messages_to_keep.append(msg)
        
        self.messages = messages_to_keep
        trash_mailbox["message_count"] = 0
        
        return {"success": True, "deleted_count": deleted_count}
    
    def restore_message(self, message_id: str) -> Dict[str, Any]:
        """
        Move a message from trash back to its original mailbox.
        
        Args:
            message_id: The unique identifier of the message to restore.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        message = None
        for msg in self.messages:
            if msg["message_id"] == message_id:
                message = msg
                break
        
        if not message:
            return {"error": f"Message with ID '{message_id}' not found"}
        
        current_mailbox = None
        for mb in self.mailboxes:
            if mb["mailbox_id"] == message["mailbox_id"]:
                current_mailbox = mb
                break
        
        if not current_mailbox or current_mailbox["name"] != "Trash":
            return {"error": f"Message '{message_id}' is not in Trash"}
        
        original_mailbox_id = message.get("original_mailbox_id")
        if not original_mailbox_id:
            return {"error": "Original mailbox information not found"}
        
        original_mailbox = None
        for mb in self.mailboxes:
            if mb["mailbox_id"] == original_mailbox_id:
                original_mailbox = mb
                break
        
        if not original_mailbox:
            return {"error": "Original mailbox no longer exists"}
        
        message["mailbox_id"] = original_mailbox_id
        del message["original_mailbox_id"]
        
        current_mailbox["message_count"] -= 1
        original_mailbox["message_count"] += 1
        
        return {"success": True, "message": message}
    
    def get_message_count(self, mailbox_id: str = None) -> Dict[str, Any]:
        """
        Get the count of messages in a specific mailbox or all mailboxes.
        
        Args:
            mailbox_id: Optional mailbox ID. If None, returns counts for all mailboxes.
            
        Returns:
            Dict[str, Any]: Message counts or error dictionary.
        """
        if mailbox_id:
            mailbox = None
            for mb in self.mailboxes:
                if mb["mailbox_id"] == mailbox_id:
                    mailbox = mb
                    break
            
            if not mailbox:
                return {"error": f"Mailbox with ID '{mailbox_id}' not found"}
            
            return {"mailbox_id": mailbox_id, "count": mailbox["message_count"]}
        
        counts = {}
        for mb in self.mailboxes:
            counts[mb["name"]] = mb["message_count"]
        
        return {"counts": counts}


__TEST_CASES__ = [
    {
        "name": "create_mailbox_success",
        "input": {"name": "Work"},
        "expected_keys": ["mailbox_id", "name", "message_count"]
    },
    {
        "name": "create_mailbox_duplicate",
        "setup": [{"method": "create_mailbox", "args": {"name": "Personal"}}],
        "input": {"name": "Personal"},
        "expected_keys": ["error"]
    },
    {
        "name": "list_mailboxes",
        "setup": [{"method": "create_mailbox", "args": {"name": "Shopping"}}],
        "method": "list_mailboxes",
        "input": {},
        "expected_keys": ["mailboxes"]
    },
    {
        "name": "send_message_success",
        "input": {"to": "recipient@example.com", "subject": "Hello", "body": "Test message"},
        "expected_keys": ["message_id", "to", "subject", "body", "timestamp", "mailbox_id"]
    },
    {
        "name": "send_message_invalid_email",
        "input": {"to": "invalid-email", "subject": "Test", "body": "Body"},
        "expected_keys": ["error"]
    },
    {
        "name": "receive_message_success",
        "setup": [{"method": "create_mailbox", "args": {"name": "Inbox"}}],
        "input": {"from_address": "sender@example.com", "subject": "Welcome", "body": "Hello there"},
        "expected_keys": ["message_id", "from", "subject", "body", "timestamp", "is_read", "mailbox_id"]
    },
    {
        "name": "get_message_success",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}},
            {"method": "receive_message", "args": {"from_address": "test@example.com", "subject": "Test", "body": "Content"}, "save_as": "msg"}
        ],
        "input": {"message_id": "__saved_msg_message_id__"},
        "expected_keys": ["message_id", "subject", "body"]
    },
    {
        "name": "get_message_not_found",
        "input": {"message_id": "nonexistent-id"},
        "expected_keys": ["error"]
    },
    {
        "name": "list_messages_in_mailbox",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}, "save_as": "mb"},
            {"method": "receive_message", "args": {"from_address": "a@b.com", "subject": "S1", "body": "B1"}}
        ],
        "input": {"mailbox_id": "__saved_mb_mailbox_id__"},
        "expected_keys": ["messages"]
    },
    {
        "name": "mark_as_read",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}},
            {"method": "receive_message", "args": {"from_address": "x@y.com", "subject": "Unread", "body": "Text"}, "save_as": "msg"}
        ],
        "input": {"message_id": "__saved_msg_message_id__"},
        "expected_keys": ["success", "message"]
    },
    {
        "name": "mark_as_unread",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}},
            {"method": "receive_message", "args": {"from_address": "x@y.com", "subject": "Read", "body": "Text"}, "save_as": "msg"},
            {"method": "mark_as_read", "args": {"message_id": "__saved_msg_message_id__"}}
        ],
        "input": {"message_id": "__saved_msg_message_id__"},
        "expected_keys": ["success", "message"]
    },
    {
        "name": "move_to_trash",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}},
            {"method": "create_mailbox", "args": {"name": "Trash"}},
            {"method": "receive_message", "args": {"from_address": "z@w.com", "subject": "Delete me", "body": "Gone"}, "save_as": "msg"}
        ],
        "input": {"message_id": "__saved_msg_message_id__"},
        "expected_keys": ["success", "message"]
    },
    {
        "name": "delete_message_permanently",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}},
            {"method": "create_mailbox", "args": {"name": "Trash"}},
            {"method": "receive_message", "args": {"from_address": "del@test.com", "subject": "Perm delete", "body": "Bye"}, "save_as": "msg"},
            {"method": "move_to_trash", "args": {"message_id": "__saved_msg_message_id__"}}
        ],
        "input": {"message_id": "__saved_msg_message_id__"},
        "expected_keys": ["success"]
    },
    {
        "name": "empty_trash",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}},
            {"method": "create_mailbox", "args": {"name": "Trash"}},
            {"method": "receive_message", "args": {"from_address": "t1@t.com", "subject": "T1", "body": "B1"}, "save_as": "m1"},
            {"method": "move_to_trash", "args": {"message_id": "__saved_m1_message_id__"}}
        ],
        "input": {},
        "expected_keys": ["success", "deleted_count"]
    },
    {
        "name": "restore_message",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}},
            {"method": "create_mailbox", "args": {"name": "Trash"}},
            {"method": "receive_message", "args": {"from_address": "r@r.com", "subject": "Restore", "body": "Back"}, "save_as": "msg"},
            {"method": "move_to_trash", "args": {"message_id": "__saved_msg_message_id__"}}
        ],
        "input": {"message_id": "__saved_msg_message_id__"},
        "expected_keys": ["success", "message"]
    },
    {
        "name": "get_message_count_specific",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}, "save_as": "mb"},
            {"method": "receive_message", "args": {"from_address": "c@c.com", "subject": "Count", "body": "One"}}
        ],
        "input": {"mailbox_id": "__saved_mb_mailbox_id__"},
        "expected_keys": ["mailbox_id", "count"]
    },
    {
        "name": "get_message_count_all",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}},
            {"method": "create_mailbox", "args": {"name": "Sent"}}
        ],
        "input": {},
        "expected_keys": ["counts"]
    },
    {
        "name": "search_messages_by_subject",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Inbox"}},
            {"method": "receive_message", "args": {"from_address": "s@s.com", "subject": "Important Meeting", "body": "Details"}}
        ],
        "input": {"query": "Meeting"},
        "expected_keys": ["messages"]
    },
    {
        "name": "delete_mailbox_success",
        "setup": [
            {"method": "create_mailbox", "args": {"name": "Temporary"}, "save_as": "mb"}
        ],
        "input": {"mailbox_id": "__saved_mb_mailbox_id__"},
        "expected_keys": ["success"]
    },
    {
        "name": "delete_mailbox_not_found",
        "input": {"mailbox_id": "fake-mailbox-id"},
        "expected_keys": ["error"]
    }
]
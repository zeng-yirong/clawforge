"""
Mobile Messaging Application Environment API

This environment simulates a mobile messaging application where users manage contacts
and send SMS or instant messages to phone numbers. It maintains conversation history,
delivery statuses, and user profiles.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# Default state containing initial data for all entities
DEFAULT_STATE: Dict[str, Any] = {
    "users": [
        {
            "_id": "user_001",
            "phone_number": "+1234567890",
            "name": "Alice Johnson",
            "profile_info": {"avatar": "alice.jpg", "status": "Available"}
        },
        {
            "_id": "user_002",
            "phone_number": "+1987654321",
            "name": "Bob Smith",
            "profile_info": {"avatar": "bob.jpg", "status": "Busy"}
        },
        {
            "_id": "user_003",
            "phone_number": "+1555123456",
            "name": "Charlie Brown",
            "profile_info": {"avatar": "charlie.jpg", "status": "Away"}
        }
    ],
    "contacts": [
        {
            "_id": "contact_001",
            "user_id": "user_001",
            "contact_id": "user_002",
            "contact_phone_number": "+1987654321",
            "contact_name": "Bob"
        },
        {
            "_id": "contact_002",
            "user_id": "user_001",
            "contact_id": "user_003",
            "contact_phone_number": "+1555123456",
            "contact_name": "Charlie"
        },
        {
            "_id": "contact_003",
            "user_id": "user_002",
            "contact_id": "user_001",
            "contact_phone_number": "+1234567890",
            "contact_name": "Alice"
        },
        {
            "_id": "contact_004",
            "user_id": "user_003",
            "contact_id": "user_001",
            "contact_phone_number": "+1234567890",
            "contact_name": "Alice J"
        }
    ],
    "messages": [
        {
            "message_id": "msg_001",
            "sender_id": "user_001",
            "receiver_id": "user_002",
            "receiver_phone_number": "+1987654321",
            "content": "Hey Bob, how are you?",
            "timestamp": "2024-01-15T10:30:00",
            "delivery_status": "delivered",
            "read_status": True
        },
        {
            "message_id": "msg_002",
            "sender_id": "user_002",
            "receiver_id": "user_001",
            "receiver_phone_number": "+1234567890",
            "content": "I'm good, thanks! How about you?",
            "timestamp": "2024-01-15T10:32:00",
            "delivery_status": "delivered",
            "read_status": True
        },
        {
            "message_id": "msg_003",
            "sender_id": "user_001",
            "receiver_id": "user_003",
            "receiver_phone_number": "+1555123456",
            "content": "Charlie, meeting at 3pm today?",
            "timestamp": "2024-01-15T11:00:00",
            "delivery_status": "sent",
            "read_status": False
        }
    ],
    "conversations": [
        {
            "conversation_id": "conv_001",
            "user_ids": ["user_001", "user_002"],
            "message_ids": ["msg_001", "msg_002"],
            "archived": False
        },
        {
            "conversation_id": "conv_002",
            "user_ids": ["user_001", "user_003"],
            "message_ids": ["msg_003"],
            "archived": False
        },
        {
            "conversation_id": "conv_003",
            "user_ids": ["user_002", "user_003"],
            "message_ids": [],
            "archived": False
        }
    ],
    "blocked_contacts": [],
    "muted_conversations": [],
    "current_user_id": "user_001",
    "message_counter": 4,
    "contact_counter": 5,
    "conversation_counter": 4
}


class MobileMessagingApplication:
    """
    A mobile messaging application environment API.
    
    This class simulates a messaging platform where users can manage contacts,
    send messages, track delivery statuses, and maintain conversation histories.
    It is designed for Agentic RL training with safe error handling.
    """

    def __init__(self) -> None:
        """
        Initialize the Mobile Messaging Application environment.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
            
        Returns:
            None
        """
        self.users: List[Dict[str, Any]] = []
        self.contacts: List[Dict[str, Any]] = []
        self.messages: List[Dict[str, Any]] = []
        self.conversations: List[Dict[str, Any]] = []
        self.blocked_contacts: List[Dict[str, Any]] = []
        self.muted_conversations: List[Dict[str, Any]] = []
        self.current_user_id: Optional[str] = None
        self.message_counter: int = 0
        self.contact_counter: int = 0
        self.conversation_counter: int = 0
        
        self._api_description = (
            "Mobile messaging application API for managing contacts, "
            "sending messages, and tracking conversations with delivery status."
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
            long_context: Flag for extended context handling (unused in base implementation).
        
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
        Retrieve the current state of the environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables:
                - users: List of registered user accounts
                - contacts: List of user contacts
                - messages: List of all messages
                - conversations: List of conversation records
                - blocked_contacts: List of blocked users
                - muted_conversations: List of muted conversations
                - current_user_id: ID of the currently active user
                - message_counter: Counter for generating message IDs
                - contact_counter: Counter for generating contact IDs
                - conversation_counter: Counter for generating conversation IDs
        """
        return {
            "users": deepcopy(self.users),
            "contacts": deepcopy(self.contacts),
            "messages": deepcopy(self.messages),
            "conversations": deepcopy(self.conversations),
            "blocked_contacts": deepcopy(self.blocked_contacts),
            "muted_conversations": deepcopy(self.muted_conversations),
            "current_user_id": self.current_user_id,
            "message_counter": self.message_counter,
            "contact_counter": self.contact_counter,
            "conversation_counter": self.conversation_counter
        }

    def _is_registered_user(self, user_id: str) -> bool:
        """
        Check if a user ID corresponds to a registered user.
        
        Args:
            user_id: The user ID to check.
            
        Returns:
            bool: True if user is registered, False otherwise.
        """
        return any(user["_id"] == user_id for user in self.users)

    def _validate_phone_format(self, phone_number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone_number: The phone number to validate.
            
        Returns:
            bool: True if format is valid, False otherwise.
        """
        pattern = r'^\+?[1-9]\d{6,14}$'
        return bool(re.match(pattern, phone_number.replace(" ", "").replace("-", "")))

    # ==================== QUERY OPERATIONS ====================

    def get_user_by_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Look up a user by their phone number.
        
        Args:
            phone_number: The phone number to search for.
            
        Returns:
            Dict[str, Any]: User information if found, or error dictionary if not found.
        """
        for user in self.users:
            if user["phone_number"] == phone_number:
                return {"user": deepcopy(user)}
        return {"error": f"No user found with phone number: {phone_number}"}

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user information by user ID.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            Dict[str, Any]: User information if found, or error dictionary if not found.
        """
        for user in self.users:
            if user["_id"] == user_id:
                return {"user": deepcopy(user)}
        return {"error": f"No user found with ID: {user_id}"}

    def list_all_users(self) -> Dict[str, Any]:
        """
        List all registered user accounts.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing list of all users.
        """
        return {"users": deepcopy(self.users), "count": len(self.users)}

    def get_contact_by_phone_number(
        self, user_id: str, contact_phone_number: str
    ) -> Dict[str, Any]:
        """
        Retrieve contact info using the contact's phone number.
        
        Args:
            user_id: The ID of the user whose contacts to search.
            contact_phone_number: The phone number of the contact.
            
        Returns:
            Dict[str, Any]: Contact information if found, or error dictionary.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        
        for contact in self.contacts:
            if (contact["user_id"] == user_id and 
                contact["contact_phone_number"] == contact_phone_number):
                return {"contact": deepcopy(contact)}
        return {"error": f"No contact found with phone number: {contact_phone_number}"}

    def get_contact_by_id(self, contact_id: str) -> Dict[str, Any]:
        """
        Look up contact info by contact ID.
        
        Args:
            contact_id: The unique identifier of the contact record.
            
        Returns:
            Dict[str, Any]: Contact information if found, or error dictionary.
        """
        for contact in self.contacts:
            if contact["_id"] == contact_id:
                return {"contact": deepcopy(contact)}
        return {"error": f"No contact found with ID: {contact_id}"}

    def list_user_contacts(self, user_id: str) -> Dict[str, Any]:
        """
        List all contacts mapped to a particular user.
        
        Args:
            user_id: The ID of the user whose contacts to list.
            
        Returns:
            Dict[str, Any]: Dictionary containing list of user's contacts.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        
        user_contacts = [
            deepcopy(c) for c in self.contacts if c["user_id"] == user_id
        ]
        return {"contacts": user_contacts, "count": len(user_contacts)}

    def validate_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Check if a phone number is valid for messaging.
        
        Args:
            phone_number: The phone number to validate.
            
        Returns:
            Dict[str, Any]: Dictionary with validation result and details, or error.
        """
        is_valid = self._validate_phone_format(phone_number)
        if not is_valid:
            return {"error": "Invalid phone number format"}
        return {
            "phone_number": phone_number,
            "is_valid": True,
            "message": "Valid phone number"
        }

    def get_messages_by_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Retrieve all messages sent or received for a specific phone number.
        
        Args:
            phone_number: The phone number to search messages for.
            
        Returns:
            Dict[str, Any]: Dictionary containing list of related messages.
        """
        user_result = self.get_user_by_phone_number(phone_number)
        if "error" in user_result:
            return {"messages": [], "count": 0, "note": "Phone number not associated with any user"}
        
        user_id = user_result["user"]["_id"]
        related_messages = [
            deepcopy(m) for m in self.messages
            if m["sender_id"] == user_id or m["receiver_id"] == user_id
        ]
        return {"messages": related_messages, "count": len(related_messages)}

    def get_conversation_by_user_and_contact(
        self, user_id: str, contact_user_id: str
    ) -> Dict[str, Any]:
        """
        Get the conversation history for a user and a given contact.
        
        Args:
            user_id: The ID of the user.
            contact_user_id: The ID of the contact user.
            
        Returns:
            Dict[str, Any]: Conversation record and messages, or error if not found.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        
        for conv in self.conversations:
            if user_id in conv["user_ids"] and contact_user_id in conv["user_ids"]:
                messages = [
                    deepcopy(m) for m in self.messages
                    if m["message_id"] in conv["message_ids"]
                ]
                return {
                    "conversation": deepcopy(conv),
                    "messages": messages,
                    "message_count": len(messages)
                }
        return {"error": f"No conversation found between {user_id} and {contact_user_id}"}

    def get_conversation_by_id(self, conversation_id: str) -> Dict[str, Any]:
        """
        Retrieve a conversation by its ID.
        
        Args:
            conversation_id: The ID of the conversation.
            
        Returns:
            Dict[str, Any]: Conversation info if found, or error dictionary.
        """
        for conv in self.conversations:
            if conv["conversation_id"] == conversation_id:
                return {"conversation": deepcopy(conv)}
        return {"error": f"No conversation found with ID: {conversation_id}"}

    def get_unread_message_count(self, user_id: str) -> Dict[str, Any]:
        """
        Get the number of unread messages for a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            Dict[str, Any]: Unread message count, or error dictionary.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        count = sum(1 for m in self.messages if m["receiver_id"] == user_id and not m["read_status"])
        return {"unread_count": count}

    def list_conversations_for_user(self, user_id: str) -> Dict[str, Any]:
        """
        List all conversations that a user is part of.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            Dict[str, Any]: List of conversations, or error dictionary.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        user_convs = [deepcopy(c) for c in self.conversations if user_id in c["user_ids"]]
        return {"conversations": user_convs, "count": len(user_convs)}

    def search_messages_by_content(self, user_id: str, search_query: str) -> Dict[str, Any]:
        """
        Search for messages containing a specific query.
        
        Args:
            user_id: The ID of the user searching.
            search_query: The text to search for.
            
        Returns:
            Dict[str, Any]: Matching messages, or error dictionary.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        matched = [
            deepcopy(m) for m in self.messages
            if (m["sender_id"] == user_id or m["receiver_id"] == user_id) and search_query.lower() in m["content"].lower()
        ]
        return {"messages": matched, "count": len(matched)}

    def get_messages_in_conversation(self, conversation_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get messages in a specific conversation.
        
        Args:
            conversation_id: The ID of the conversation.
            limit: Maximum number of messages to return.
            
        Returns:
            Dict[str, Any]: Messages in the conversation, or error dictionary.
        """
        conv = next((c for c in self.conversations if c["conversation_id"] == conversation_id), None)
        if not conv:
            return {"error": f"No conversation found with ID: {conversation_id}"}
        msgs = [deepcopy(m) for m in self.messages if m["message_id"] in conv["message_ids"]]
        if limit is not None and limit > 0:
            msgs = msgs[-limit:]
        return {"messages": msgs, "count": len(msgs)}

    def get_message_by_id(self, message_id: str) -> Dict[str, Any]:
        """
        Retrieve information on a specific message by message ID.
        
        Args:
            message_id: The unique identifier of the message.
            
        Returns:
            Dict[str, Any]: Message information if found, or error dictionary.
        """
        for message in self.messages:
            if message["message_id"] == message_id:
                return {"message": deepcopy(message)}
        return {"error": f"No message found with ID: {message_id}"}

    def get_message_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """
        Check the current delivery status of a specific message.
        
        Args:
            message_id: The unique identifier of the message.
            
        Returns:
            Dict[str, Any]: Delivery status info, or error if message not found.
        """
        for message in self.messages:
            if message["message_id"] == message_id:
                return {
                    "message_id": message_id,
                    "delivery_status": message["delivery_status"],
                    "read_status": message["read_status"]
                }
        return {"error": f"No message found with ID: {message_id}"}

    def get_blocked_contacts(self, user_id: str) -> Dict[str, Any]:
        """
        Get the list of users blocked by a specific user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            Dict[str, Any]: Blocked contacts, or error dictionary.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        blocked = [b["blocked_user_id"] for b in self.blocked_contacts if b["user_id"] == user_id]
        return {"blocked_contacts": blocked}

    def get_muted_conversations(self, user_id: str) -> Dict[str, Any]:
        """
        Get the list of conversations muted by a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            Dict[str, Any]: Muted conversations, or error dictionary.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        muted = [m["conversation_id"] for m in self.muted_conversations if m["user_id"] == user_id]
        return {"muted_conversations": muted}

    # ==================== STATE CHANGE OPERATIONS ====================

    def send_message(
        self,
        sender_id: str,
        receiver_phone_number: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Create and send a new message from a registered user to a valid phone number.
        
        Args:
            sender_id: The ID of the user sending the message.
            receiver_phone_number: The phone number of the recipient.
            content: The message content.
            
        Returns:
            Dict[str, Any]: Created message details, or error dictionary.
        """
        # Constraint: Only registered users can send messages
        if not self._is_registered_user(sender_id):
            return {"error": f"Sender {sender_id} is not a registered user"}
        
        # Constraint: Phone numbers must be valid before sending
        if not self._validate_phone_format(receiver_phone_number):
            return {"error": f"Invalid phone number format: {receiver_phone_number}"}
        
        if not content or not content.strip():
            return {"error": "Message content cannot be empty"}
        
        # Find receiver
        receiver_id = None
        for user in self.users:
            if user["phone_number"] == receiver_phone_number:
                receiver_id = user["_id"]
                break
                
        # Constraint: Check if the receiver has blocked the sender
        if receiver_id is not None:
            for b in self.blocked_contacts:
                if b["user_id"] == receiver_id and b["blocked_user_id"] == sender_id:
                    return {"error": "You are blocked by this user"}
        
        # Create message
        message_id = f"msg_{self.message_counter:03d}"
        self.message_counter += 1
        
        new_message = {
            "message_id": message_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "receiver_phone_number": receiver_phone_number,
            "content": content.strip(),
            "timestamp": self._timestamp(),
            "delivery_status": "sent",
            "read_status": False
        }
        self.messages.append(new_message)
        
        return {
            "success": True,
            "message": deepcopy(new_message),
            "status": "Message sent successfully"
        }

    def update_message_delivery_status(
        self,
        message_id: str,
        delivery_status: str
    ) -> Dict[str, Any]:
        """
        Set or update the delivery status for a message.
        
        Args:
            message_id: The unique identifier of the message.
            delivery_status: New status (sent, delivered, failed).
            
        Returns:
            Dict[str, Any]: Updated status info, or error dictionary.
        """
        valid_statuses = ["sent", "delivered", "failed"]
        if delivery_status not in valid_statuses:
            return {"error": f"Invalid status. Must be one of: {valid_statuses}"}
        
        for message in self.messages:
            if message["message_id"] == message_id:
                old_status = message["delivery_status"]
                message["delivery_status"] = delivery_status
                return {
                    "success": True,
                    "message_id": message_id,
                    "old_status": old_status,
                    "new_status": delivery_status
                }
        return {"error": f"No message found with ID: {message_id}"}

    def create_contact(
        self,
        user_id: str,
        contact_phone_number: str,
        contact_name: str
    ) -> Dict[str, Any]:
        """
        Add a new contact to the user's contact list.
        
        Args:
            user_id: The ID of the user adding the contact.
            contact_phone_number: Phone number of the new contact.
            contact_name: Display name for the contact.
            
        Returns:
            Dict[str, Any]: Created contact details, or error dictionary.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        
        if not self._validate_phone_format(contact_phone_number):
            return {"error": f"Invalid phone number format: {contact_phone_number}"}
        
        if not contact_name or not contact_name.strip():
            return {"error": "Contact name cannot be empty"}
        
        # Check for existing contact with same phone
        for contact in self.contacts:
            if (contact["user_id"] == user_id and 
                contact["contact_phone_number"] == contact_phone_number):
                return {"error": f"Contact with phone {contact_phone_number} already exists"}
        
        # Find if contact is a registered user
        contact_user_id = None
        for user in self.users:
            if user["phone_number"] == contact_phone_number:
                contact_user_id = user["_id"]
                break
        
        contact_id = f"contact_{self.contact_counter:03d}"
        self.contact_counter += 1
        
        new_contact = {
            "_id": contact_id,
            "user_id": user_id,
            "contact_id": contact_user_id,
            "contact_phone_number": contact_phone_number,
            "contact_name": contact_name.strip()
        }
        self.contacts.append(new_contact)
        
        return {
            "success": True,
            "contact": deepcopy(new_contact),
            "status": "Contact created successfully"
        }

    def add_message_to_conversation(
        self,
        conversation_id: str,
        message_id: str
    ) -> Dict[str, Any]:
        """
        Insert a new message into the conversation history.
        
        Args:
            conversation_id: The ID of the conversation to update.
            message_id: The ID of the message to add.
            
        Returns:
            Dict[str, Any]: Updated conversation info, or error dictionary.
        """
        # Validate message exists
        message_exists = any(m["message_id"] == message_id for m in self.messages)
        if not message_exists:
            return {"error": f"Message {message_id} does not exist"}
        
        for conv in self.conversations:
            if conv["conversation_id"] == conversation_id:
                if message_id in conv["message_ids"]:
                    return {"error": f"Message {message_id} already in conversation"}
                conv["message_ids"].append(message_id)
                return {
                    "success": True,
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "total_messages": len(conv["message_ids"])
                }
        return {"error": f"No conversation found with ID: {conversation_id}"}

    def create_conversation(
        self,
        user_id_1: str,
        user_id_2: str
    ) -> Dict[str, Any]:
        """
        Initiate a new conversation record between two users/contacts.
        
        Args:
            user_id_1: The ID of the first user.
            user_id_2: The ID of the second user.
            
        Returns:
            Dict[str, Any]: Created conversation details, or error dictionary.
        """
        if not self._is_registered_user(user_id_1):
            return {"error": f"User {user_id_1} is not registered"}
        
        if not self._is_registered_user(user_id_2):
            return {"error": f"User {user_id_2} is not registered"}
        
        if user_id_1 == user_id_2:
            return {"error": "Cannot create conversation with oneself"}
        
        # Check if conversation already exists
        for conv in self.conversations:
            if user_id_1 in conv["user_ids"] and user_id_2 in conv["user_ids"]:
                return {
                    "error": "Conversation already exists between these users",
                    "existing_conversation_id": conv["conversation_id"]
                }
        
        conversation_id = f"conv_{self.conversation_counter:03d}"
        self.conversation_counter += 1
        
        new_conversation = {
            "conversation_id": conversation_id,
            "user_ids": [user_id_1, user_id_2],
            "message_ids": [],
            "archived": False
        }
        self.conversations.append(new_conversation)
        
        return {
            "success": True,
            "conversation": deepcopy(new_conversation),
            "status": "Conversation created successfully"
        }

    def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Change the read status of a message when viewed.
        
        Args:
            message_id: The unique identifier of the message.
            
        Returns:
            Dict[str, Any]: Updated read status info, or error dictionary.
        """
        for message in self.messages:
            if message["message_id"] == message_id:
                if message["read_status"]:
                    return {
                        "success": True,
                        "message_id": message_id,
                        "status": "Message was already marked as read"
                    }
                message["read_status"] = True
                return {
                    "success": True,
                    "message_id": message_id,
                    "status": "Message marked as read"
                }
        return {"error": f"No message found with ID: {message_id}"}

    def delete_message(self, message_id: str) -> Dict[str, Any]:
        """
        Remove a message from the system.
        
        Args:
            message_id: The unique identifier of the message to delete.
            
        Returns:
            Dict[str, Any]: Deletion confirmation, or error dictionary.
        """
        for i, message in enumerate(self.messages):
            if message["message_id"] == message_id:
                self.messages.pop(i)
                
                # Remove from conversations
                for conv in self.conversations:
                    if message_id in conv["message_ids"]:
                        conv["message_ids"].remove(message_id)
                
                return {
                    "success": True,
                    "deleted_message_id": message_id,
                    "status": "Message deleted successfully"
                }
        return {"error": f"No message found with ID: {message_id}"}

    def delete_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Remove a contact from the user's contact list.
        
        Args:
            contact_id: The unique identifier of the contact to delete.
            
        Returns:
            Dict[str, Any]: Deletion confirmation, or error dictionary.
        """
        for i, contact in enumerate(self.contacts):
            if contact["_id"] == contact_id:
                deleted_contact = self.contacts.pop(i)
                return {
                    "success": True,
                    "deleted_contact_id": contact_id,
                    "contact_name": deleted_contact["contact_name"],
                    "status": "Contact deleted successfully"
                }
        return {"error": f"No contact found with ID: {contact_id}"}

    def archive_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Archive or hide a conversation for a user.
        
        Args:
            conversation_id: The ID of the conversation to archive.
            
        Returns:
            Dict[str, Any]: Archive confirmation, or error dictionary.
        """
        for conv in self.conversations:
            if conv["conversation_id"] == conversation_id:
                if conv.get("archived", False):
                    return {
                        "success": True,
                        "conversation_id": conversation_id,
                        "status": "Conversation was already archived"
                    }
                conv["archived"] = True
                return {
                    "success": True,
                    "conversation_id": conversation_id,
                    "status": "Conversation archived successfully"
                }
        return {"error": f"No conversation found with ID: {conversation_id}"}

    def unarchive_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Unarchive a previously archived conversation.
        
        Args:
            conversation_id: The ID of the conversation to unarchive.
            
        Returns:
            Dict[str, Any]: Unarchive confirmation, or error dictionary.
        """
        for conv in self.conversations:
            if conv["conversation_id"] == conversation_id:
                if not conv.get("archived", False):
                    return {
                        "success": True,
                        "conversation_id": conversation_id,
                        "status": "Conversation was not archived"
                    }
                conv["archived"] = False
                return {
                    "success": True,
                    "conversation_id": conversation_id,
                    "status": "Conversation unarchived successfully"
                }
        return {"error": f"No conversation found with ID: {conversation_id}"}

    def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Remove a conversation from history.
        
        Args:
            conversation_id: The ID of the conversation to delete.
            
        Returns:
            Dict[str, Any]: Deletion confirmation, or error dictionary.
        """
        for i, conv in enumerate(self.conversations):
            if conv["conversation_id"] == conversation_id:
                deleted_conv = self.conversations.pop(i)
                return {
                    "success": True,
                    "deleted_conversation_id": conversation_id,
                    "message_count_removed": len(deleted_conv["message_ids"]),
                    "status": "Conversation deleted successfully"
                }
        return {"error": f"No conversation found with ID: {conversation_id}"}

    def update_contact_name(self, contact_id: str, new_name: str) -> Dict[str, Any]:
        """
        Update the display name of an existing contact.
        
        Args:
            contact_id: The unique identifier of the contact to update.
            new_name: The new display name for the contact.
            
        Returns:
            Dict[str, Any]: Updated contact info, or error dictionary.
        """
        if not new_name or not new_name.strip():
            return {"error": "Contact name cannot be empty"}
        
        for contact in self.contacts:
            if contact["_id"] == contact_id:
                old_name = contact["contact_name"]
                contact["contact_name"] = new_name.strip()
                return {
                    "success": True,
                    "contact_id": contact_id,
                    "old_name": old_name,
                    "new_name": new_name.strip(),
                    "status": "Contact name updated successfully"
                }
        return {"error": f"No contact found with ID: {contact_id}"}

    def block_contact(self, user_id: str, blocked_user_id: str) -> Dict[str, Any]:
        """
        Block another user from sending messages.
        
        Args:
            user_id: The ID of the user performing the block.
            blocked_user_id: The ID of the user to block.
            
        Returns:
            Dict[str, Any]: Success or error dictionary.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        if not self._is_registered_user(blocked_user_id):
            return {"error": f"User {blocked_user_id} is not registered"}
        if user_id == blocked_user_id:
            return {"error": "Cannot block oneself"}
            
        for b in self.blocked_contacts:
            if b["user_id"] == user_id and b["blocked_user_id"] == blocked_user_id:
                return {"error": "User is already blocked"}
                
        self.blocked_contacts.append({"user_id": user_id, "blocked_user_id": blocked_user_id})
        return {"success": True, "message": f"User {blocked_user_id} blocked successfully"}

    def unblock_contact(self, user_id: str, blocked_user_id: str) -> Dict[str, Any]:
        """
        Unblock a previously blocked user.
        
        Args:
            user_id: The ID of the user.
            blocked_user_id: The ID of the user to unblock.
            
        Returns:
            Dict[str, Any]: Success or error dictionary.
        """
        for i, b in enumerate(self.blocked_contacts):
            if b["user_id"] == user_id and b["blocked_user_id"] == blocked_user_id:
                self.blocked_contacts.pop(i)
                return {"success": True, "message": f"User {blocked_user_id} unblocked successfully"}
        return {"error": "User is not blocked"}

    def mute_conversation(self, user_id: str, conversation_id: str) -> Dict[str, Any]:
        """
        Mute notifications for a specific conversation.
        
        Args:
            user_id: The ID of the user muting the conversation.
            conversation_id: The ID of the conversation to mute.
            
        Returns:
            Dict[str, Any]: Success or error dictionary.
        """
        if not self._is_registered_user(user_id):
            return {"error": f"User {user_id} is not registered"}
        # Verify conversation exists
        conv_exists = any(c["conversation_id"] == conversation_id for c in self.conversations)
        if not conv_exists:
            return {"error": f"No conversation found with ID: {conversation_id}"}
            
        for m in self.muted_conversations:
            if m["user_id"] == user_id and m["conversation_id"] == conversation_id:
                return {"error": "Conversation is already muted"}
                
        self.muted_conversations.append({"user_id": user_id, "conversation_id": conversation_id})
        return {"success": True, "message": "Conversation muted successfully"}

    def unmute_conversation(self, user_id: str, conversation_id: str) -> Dict[str, Any]:
        """
        Unmute notifications for a previously muted conversation.
        
        Args:
            user_id: The ID of the user.
            conversation_id: The ID of the conversation to unmute.
            
        Returns:
            Dict[str, Any]: Success or error dictionary.
        """
        for i, m in enumerate(self.muted_conversations):
            if m["user_id"] == user_id and m["conversation_id"] == conversation_id:
                self.muted_conversations.pop(i)
                return {"success": True, "message": "Conversation unmuted successfully"}
        return {"error": "Conversation is not muted"}


# Test cases for validating environment functionality
__TEST_CASES__ = [
    {
        "name": "Messaging and conversation management flow",
        "steps": [
            {"tool_call": "get_user_by_id(user_id='user_001')", "expect_success": True},
            {"tool_call": "send_message(sender_id='user_001', receiver_phone_number='+1987654321', content='Hello Bob!')", "expect_success": True},
            {"tool_call": "get_conversation_by_id(conversation_id='conv_001')", "expect_success": True},
            {"tool_call": "search_messages_by_content(user_id='user_001', search_query='Hello')", "expect_success": True},
            {"tool_call": "get_messages_in_conversation(conversation_id='conv_001', limit=5)", "expect_success": True}
        ]
    },
    {
        "name": "Contact and unread messages flow",
        "steps": [
            {"tool_call": "create_contact(user_id='user_002', contact_phone_number='+1555123456', contact_name='Charlie B')", "expect_success": True},
            {"tool_call": "list_conversations_for_user(user_id='user_002')", "expect_success": True},
            {"tool_call": "get_unread_message_count(user_id='user_002')", "expect_success": True},
            {"tool_call": "mark_message_as_read(message_id='msg_001')", "expect_success": True}
        ]
    },
    {
        "name": "Block and unblock contact flow",
        "steps": [
            {"tool_call": "block_contact(user_id='user_001', blocked_user_id='user_003')", "expect_success": True},
            {"tool_call": "get_blocked_contacts(user_id='user_001')", "expect_success": True},
            {"tool_call": "send_message(sender_id='user_003', receiver_phone_number='+1234567890', content='Hello')", "expect_success": False},
            {"tool_call": "unblock_contact(user_id='user_001', blocked_user_id='user_003')", "expect_success": True},
            {"tool_call": "send_message(sender_id='user_003', receiver_phone_number='+1234567890', content='Hello again')", "expect_success": True}
        ]
    },
    {
        "name": "Mute and unmute conversation flow",
        "steps": [
            {"tool_call": "mute_conversation(user_id='user_001', conversation_id='conv_001')", "expect_success": True},
            {"tool_call": "get_muted_conversations(user_id='user_001')", "expect_success": True},
            {"tool_call": "unmute_conversation(user_id='user_001', conversation_id='conv_001')", "expect_success": True},
            {"tool_call": "get_muted_conversations(user_id='user_001')", "expect_success": True}
        ]
    },
    {
        "name": "Error handling flow",
        "steps": [
            {"tool_call": "get_user_by_id(user_id='nonexistent_user')", "expect_success": False},
            {"tool_call": "validate_phone_number(phone_number='invalid_phone')", "expect_success": False},
            {"tool_call": "send_message(sender_id='user_001', receiver_phone_number='+0000000000', content='Test')", "expect_success": False},
            {"tool_call": "get_message_delivery_status(message_id='nonexistent_msg')", "expect_success": False},
            {"tool_call": "update_contact_name(contact_id='nonexistent_contact', new_name='Test')", "expect_success": False}
        ]
    }
]
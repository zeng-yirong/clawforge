import random
from copy import deepcopy
from typing import Dict, List, Optional, Union

DEFAULT_STATE = {
    "generated_ids": set(),
    "user_count": 4,
    "user_map": {
        "Alice": "USR001",
        "Bob": "USR002",
        "Catherine": "USR003",
        "Daniel": "USR004",
    },
    "inbox": [
        {
            "sender_id": "USR001",
            "receiver_id": "USR002",
            "message": "My name is Alice. I want to connect.",
        },
        {
            "sender_id": "USR002",
            "receiver_id": "USR003",
            "message": "Could you upload the file?",
        },
        {
            "sender_id": "USR003",
            "receiver_id": "USR004",
            "message": "Could you upload the file?",
        },
    ],
    "message_count": 3,
    "current_user": None,
}


class MessageAPI:
    """
    A class representing a Message API for managing user interactions in a workspace.

    This class provides methods for user management, messaging, and message retrieval
    within a specific workspace. It maintains user information, sent messages, and
    received messages for each user.

    Attributes:
        user_map (Dict[str, str]): A mapping of user names to user IDs.
        inbox (List[Dict[str, str]]): A list of dictionaries storing all messages.
        message_count (int): The total count of messages in the workspace.
        current_user (Optional[str]): The ID of the currently logged-in user.

    Methods:
        generate_id(): Generate a unique ID for a message.
        list_users(): List all users in the workspace.
        get_user_id(user: str): Get the user ID for a given username.
        message_login(user_id: str): Log in a user.
        message_logout(): Log out the current user.
        message_get_login_status(): Get login status of the current user.
        send_message(receiver_id: str, message: str): Send a message to another user.
        view_messages_sent(): View messages sent by the current user.
        view_messages_received(): View messages received by the current user.
        delete_message(receiver_id: str): Delete the latest message sent to a receiver.
        add_contact(user_name: str): Add a new contact to the workspace.
        remove_contact(user_id: str): Remove a contact from the workspace.
        search_messages(keyword: str): Search for messages containing a keyword.
        get_message_stats(): Get messaging statistics for the current user.
    """

    def __init__(self):
        """
        Initialize the MessageAPI with a workspace ID.
        """
        self.generated_ids: set
        self.user_count: int
        self.user_map: Dict[str, str]
        self.inbox: List[Dict[str, str]]
        self.message_count: int
        self.current_user: Optional[str]
        self._api_description = "This tool belongs to the Message API, which is used to manage user interactions in a workspace."

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load a scenario into the MessageAPI.

        Args:
            scenario (Dict): A dictionary containing message data.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self._random = random.Random((scenario.get("random_seed", 200191)))

        if isinstance(scenario.get("generated_ids", []), list):
            raw_ids = scenario.get("generated_ids", DEFAULT_STATE_COPY["generated_ids"])
            self.generated_ids = set(raw_ids)
        else:
            self.generated_ids = scenario.get(
                "generated_ids", DEFAULT_STATE_COPY["generated_ids"]
            )
        self.user_count = scenario.get("user_count", DEFAULT_STATE_COPY["user_count"])
        self.user_map = scenario.get("user_map", DEFAULT_STATE_COPY["user_map"])
        self.inbox = scenario.get("inbox", DEFAULT_STATE_COPY["inbox"])
        self.message_count = scenario.get(
            "message_count", DEFAULT_STATE_COPY["message_count"]
        )
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, MessageAPI):
            return False

        for attr_name in vars(self):
            if attr_name.startswith("_"):
                continue
            model_attr = getattr(self, attr_name)
            ground_truth_attr = getattr(value, attr_name)

            if model_attr != ground_truth_attr:
                return False

        return True

    def _generate_id(self) -> Dict[str, int]:
        """
        Generate a unique ID for a message.

        Returns:
            new_id (int): A unique ID for a message.
        """
        new_id = self._random.randint(
            10000, 99999
        )  # first 5 mapped by initial configuration.
        while new_id in self.generated_ids:
            new_id = self._random.randint(10000, 99999)
        self.generated_ids.add(new_id)
        return {"new_id": new_id}

    def get_env_state(self) -> Dict:
        return {
            "generated_ids": list(self.generated_ids),
            "user_count": self.user_count,
            "user_map": self.user_map,
            "inbox": self.inbox,
            "message_count": self.message_count,
            "current_user": self.current_user
        }

    def list_users(self) -> Dict[str, List[str]]:
        """
        List all users in the workspace.

        Returns:
          user_list (List[str]): List of all users in the workspace.
        """
        return {"user_list": list(self.user_map.keys())}

    def get_user_id(self, user: str) -> Dict[str, Optional[str]]:
        """
        Get user ID from user name.

        Args:
            user (str): User name of the user.

        Returns:
            user_id (str): User ID of the user
        """
        if not user:
            return {"error": "User name cannot be empty."}
        if user not in self.user_map:
            return {"error": f"User '{user}' not found in the workspace."}
        return {"user_id": self.user_map.get(user)}

    def message_login(self, user_id: str) -> Dict[str, Union[str, bool]]:
        """
        Log in a user with the given user ID to messeage application.

        Args:
            user_id (str): User ID of the user to log in.

        Returns:
            login_status (bool): True if login was successful, False otherwise.
            message (str): A message describing the result of the login attempt.
        """
        if user_id not in self.user_map.values():
            return {"error": f"User ID '{user_id}' not found."}
        self.current_user = user_id
        return {
            "login_status": True,
            "message": f"User '{user_id}' logged in successfully.",
        }

    def message_logout(self) -> Dict[str, Union[bool, str]]:
        """
        Log out the current user.

        Returns:
            logout_status (bool): True if logout was successful, False otherwise.
            message (str): A message describing the result of the logout attempt.
        """
        if not self.current_user:
            return {"error": "No user is currently logged in."}
            
        self.current_user = None
        return {
            "logout_status": True,
            "message": "User logged out successfully.",
        }

    def message_get_login_status(self) -> Dict[str, bool]:
        """
        Get the login status of the current user.

        Returns:
            login_status (bool): True if the current user is logged in, False otherwise.
        """
        return {"login_status": bool(self.current_user)}

    def send_message(self, receiver_id: str, message: str) -> Dict[str, Union[str, bool, int]]:
        """
        Send a message to a user.
        Args:
            receiver_id (str): User ID of the user to send the message to.
            message (str): Message to be sent.
        Returns:
            sent_status (bool): True if the message was sent successfully, False otherwise.
            message_id (int): ID of the sent message.
            message (str): A message describing the result of the send attempt.
        """
        if not self.current_user:
            return {"error": "No user is currently logged in."}
        if not message:
            return {"error": "Message cannot be empty."}
        if receiver_id not in self.user_map.values():
            return {"error": f"Receiver ID '{receiver_id}' not found."}
        
        message_id_dict = self._generate_id()
        message_id = message_id_dict["new_id"]
        
        self.inbox.append({
            "sender_id": self.current_user,
            "receiver_id": receiver_id,
            "message": message
        })
        self.message_count += 1
        return {
            "sent_status": True,
            "message_id": message_id,
            "message": f"Message sent to '{receiver_id}' successfully.",
        }

    def delete_message(self, receiver_id: str) -> Dict[str, Union[bool, str]]:
        """
        Delete the latest message sent to a receiver by the current user.
        Args:
            receiver_id (str): User ID of the user to send the message to.
        Returns:
            deleted_status (bool): True if the message was deleted successfully, False otherwise.
            message_id (str): ID of the receiver whose message was deleted.
            message (str): A message describing the result of the deletion attempt.
        """
        if not self.current_user:
            return {"error": "No user is currently logged in."}
        if not receiver_id:
            return {"error": "Receiver ID cannot be empty."}

        # Loop through the inbox in reverse order to find the latest message sent to the receiver
        for message in self.inbox[::-1]:
            if message["receiver_id"] == receiver_id and message["sender_id"] == self.current_user:
                self.inbox.remove(message)
                self.message_count -= 1
                return {
                    "deleted_status": True,
                    "message_id": receiver_id,
                    "message": f"Receiver {receiver_id}'s latest message deleted successfully.",
                }
        return {"error": f"No message sent to receiver ID '{receiver_id}' found to delete."}

    def view_messages_sent(self) -> Dict[str, Union[Dict[str, List[str]], str]]:
        """
        View all historical messages sent by the current user.

        Returns:
            messages (Dict): Dictionary of messages grouped by receiver An example of the messages dictionary is {"USR001":["Hello"],"USR002":["World"]}.
        """
        if not self.current_user:
            return {"error": "No user is currently logged in."}
        
        sent_messages = {}
        for message in self.inbox:
            if message["sender_id"] == self.current_user:
                receiver = message["receiver_id"]
                message_content = message["message"]
                if receiver not in sent_messages:
                    sent_messages[receiver] = [message_content]
                else:
                    sent_messages[receiver].append(message_content)
        return {"messages": sent_messages}

    def view_messages_received(self) -> Dict[str, Union[Dict[str, List[str]], str]]:
        """
        View all historical messages received by the current user.

        Returns:
            messages (Dict): Dictionary of messages grouped by sender. An example of the messages dictionary is {"USR001":["Hello"],"USR002":["World"]}.
        """
        if not self.current_user:
            return {"error": "No user is currently logged in."}
        
        received_messages = {}
        for message in self.inbox:
            if message["receiver_id"] == self.current_user:
                sender = message["sender_id"]
                message_content = message["message"]
                if sender not in received_messages:
                    received_messages[sender] = [message_content]
                else:
                    received_messages[sender].append(message_content)
        return {"messages": received_messages}

    def add_contact(self, user_name: str) -> Dict[str, Union[bool, str]]:
        """
        Add a contact to the workspace.
        Args:
            user_name (str): User name of contact to be added.
        Returns:
            added_status (bool): True if the contact was added successfully, False otherwise.
            user_id (str): User ID of the added contact.
            message (str): A message describing the result of the addition attempt.
        """
        if not user_name:
            return {"error": "User name cannot be empty."}
        if user_name in self.user_map:
            return {"error": f"User name '{user_name}' already exists."}
            
        self.user_count += 1
        user_id = f"USR{str(self.user_count).zfill(3)}"
        if user_id in self.user_map.values():
            return {"error": f"User ID '{user_id}' already exists."}
            
        self.user_map[user_name] = user_id
        return {
            "added_status": True,
            "user_id": user_id,
            "message": f"Contact '{user_name}' added successfully.",
        }

    def remove_contact(self, user_id: str) -> Dict[str, Union[bool, str]]:
        """
        Remove a contact from the workspace and their related message records.
        
        Args:
            user_id (str): User ID of the contact to be removed.
            
        Returns:
            removed_status (bool): True if the contact was removed successfully, False otherwise.
            message (str): A message describing the result of the removal attempt.
        """
        if not user_id:
            return {"error": "User ID cannot be empty."}
            
        user_name_to_remove = None
        for name, uid in self.user_map.items():
            if uid == user_id:
                user_name_to_remove = name
                break
                
        if not user_name_to_remove:
            return {"error": f"User ID '{user_id}' not found."}
            
        del self.user_map[user_name_to_remove]
        
        new_inbox = []
        for msg in self.inbox:
            if msg["sender_id"] != user_id and msg["receiver_id"] != user_id:
                new_inbox.append(msg)
            else:
                self.message_count -= 1
                
        self.inbox = new_inbox
        
        if self.current_user == user_id:
            self.current_user = None
            
        return {
            "removed_status": True,
            "message": f"Contact '{user_name_to_remove}' and their messages removed successfully.",
        }

    def search_messages(
        self, keyword: str
    ) -> Dict[str, Union[List[Dict[str, str]], str]]:
        """
        Search for messages containing a specific keyword that are visible to the current user.
        Args:
            keyword (str): The keyword to search for in messages.
        Returns:
            results (List[Dict]): List of dictionaries containing matching messages.
                - sender_id (str): User ID of the sender.
                - receiver_id (str): User ID of the receiver of the message.
                - message (str): The message containing the keyword.
        """
        if not self.current_user:
            return {"error": "No user is currently logged in."}
        if not keyword:
            return {"error": "Keyword cannot be empty."}
            
        keyword_lower = keyword.lower()
        results = []
        for message_data in self.inbox:
            # Only allow user to search messages they sent or received
            if message_data["sender_id"] == self.current_user or message_data["receiver_id"] == self.current_user:
                message_content = message_data["message"]
                if keyword_lower in message_content.lower():
                    results.append(
                        {
                            "sender_id": message_data["sender_id"],
                            "receiver_id": message_data["receiver_id"],
                            "message": message_content,
                        }
                    )
        return {"results": results}

    def get_message_stats(self) -> Dict[str, Union[Dict[str, int], str]]:
        """
        Get statistics about messages for the current user.
        Returns:
            stats (Dict): Dictionary containing message statistics.
                - received_count (int): Number of messages received by the current user.
                - total_contacts (int): Total number of contacts the user has interacted with.
        """
        if not self.current_user:
            return {"error": "No user is currently logged in."}
            
        received_count = 0
        contacts = set()
        
        for message_data in self.inbox:
            if message_data["receiver_id"] == self.current_user:
                received_count += 1
                contacts.add(message_data["sender_id"])
            if message_data["sender_id"] == self.current_user:
                contacts.add(message_data["receiver_id"])
                
        total_contacts = len(contacts)
        return {
            "stats": {
                "received_count": received_count,
                "total_contacts": total_contacts,
            }
        }


__TEST_CASES__ = [
    {
        'name': 'Cross-method workflow: Login, send, view, delete, and get stats',
        'steps': [
            {'expect_success': True, 'tool_call': "env['message_api'].message_login(user_id='USR001')"},
            {'expect_success': True, 'tool_call': "env['message_api'].message_get_login_status()"},
            {'expect_success': True, 'tool_call': "env['message_api'].send_message(receiver_id='USR002', message='Hello Bob')"},
            {'expect_success': True, 'tool_call': "env['message_api'].view_messages_sent()"},
            {'expect_success': True, 'tool_call': "env['message_api'].delete_message(receiver_id='USR002')"},
            {'expect_success': True, 'tool_call': "env['message_api'].get_message_stats()"}
        ]
    },
    {
        'name': 'Error path: Login with invalid user ID',
        'steps': [
            {'expect_success': False, 'tool_call': "env['message_api'].message_login(user_id='INVALID_ID')"}
        ]
    },
    {
        'name': 'Error path: Send message without login',
        'steps': [
            {'expect_success': False, 'tool_call': "env['message_api'].send_message(receiver_id='USR002', message='Hello')"}
        ]
    },
    {
        'name': 'Boundary value: Empty message and excessively long message',
        'steps': [
            {'expect_success': True, 'tool_call': "env['message_api'].message_login(user_id='USR001')"},
            {'expect_success': False, 'tool_call': "env['message_api'].send_message(receiver_id='USR002', message='')"},
            {'expect_success': True, 'tool_call': "env['message_api'].send_message(receiver_id='USR002', message='This is a very long message that exceeds normal lengths to test boundary conditions of the message sending functionality. It should be handled properly by the system without crashing.')"}
        ]
    },
    {
        'name': 'State-change verification: Add contact and verify presence',
        'steps': [
            {'expect_success': True, 'tool_call': "env['message_api'].add_contact(user_name='Eve')"},
            {'expect_success': True, 'tool_call': "env['message_api'].list_users()"},
            {'expect_success': True, 'tool_call': "env['message_api'].get_user_id(user='Eve')"}
        ]
    },
    {
        'name': 'Cross-method workflow: Search messages after sending',
        'steps': [
            {'expect_success': True, 'tool_call': "env['message_api'].message_login(user_id='USR001')"},
            {'expect_success': True, 'tool_call': "env['message_api'].send_message(receiver_id='USR003', message='Please review the document')"},
            {'expect_success': True, 'tool_call': "env['message_api'].search_messages(keyword='review')"}
        ]
    },
    {
        'name': 'Error path and boundary value: Delete message errors (unauthorized and empty)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['message_api'].message_login(user_id='USR001')"},
            {'expect_success': False, 'tool_call': "env['message_api'].delete_message(receiver_id='USR004')"},
            {'expect_success': False, 'tool_call': "env['message_api'].delete_message(receiver_id='')"}
        ]
    },
    {
        'name': 'Boundary value: Search with empty keyword',
        'steps': [
            {'expect_success': True, 'tool_call': "env['message_api'].message_login(user_id='USR001')"},
            {'expect_success': False, 'tool_call': "env['message_api'].search_messages(keyword='')"}
        ]
    },
    {
        'name': 'Error path and boundary value: Get user ID for non-existent user and add empty contact',
        'steps': [
            {'expect_success': False, 'tool_call': "env['message_api'].get_user_id(user='UnknownUser')"},
            {'expect_success': False, 'tool_call': "env['message_api'].add_contact(user_name='')"}
        ]
    },
    {
        'name': 'Normal path: Get message stats for user',
        'steps': [
            {'expect_success': True, 'tool_call': "env['message_api'].message_login(user_id='USR002')"},
            {'expect_success': True, 'tool_call': "env['message_api'].get_message_stats()"}
        ]
    },
    {
        'name': 'New methods workflow: view_messages_received, message_logout, remove_contact',
        'steps': [
            {'expect_success': True, 'tool_call': "env['message_api'].message_login(user_id='USR002')"},
            {'expect_success': True, 'tool_call': "env['message_api'].view_messages_received()"},
            {'expect_success': True, 'tool_call': "env['message_api'].message_logout()"},
            {'expect_success': False, 'tool_call': "env['message_api'].message_logout()"},
            {'expect_success': True, 'tool_call': "env['message_api'].remove_contact(user_id='USR004')"},
            {'expect_success': False, 'tool_call': "env['message_api'].remove_contact(user_id='INVALID_ID')"}
        ]
    },
    {
        'name': 'Error paths: view received without login, remove empty contact',
        'steps': [
            {'expect_success': False, 'tool_call': "env['message_api'].view_messages_received()"},
            {'expect_success': False, 'tool_call': "env['message_api'].remove_contact(user_id='')"}
        ]
    }
]
"""
SMS Notification and Messaging Service Environment API

An SMS notification and messaging service is a cloud-based platform that enables
organizations to send, receive, and manage text messages at scale.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any

DEFAULT_STATE: Dict[str, Any] = {
    "subscribers": [
        {
            "phone_number": "+1234567890",
            "subscription_status": "active",
            "subscription_date": "2024-01-15T10:30:00",
            "group": ["newsletter", "alerts"]
        },
        {
            "phone_number": "+1987654321",
            "subscription_status": "active",
            "subscription_date": "2024-02-20T14:45:00",
            "group": ["newsletter"]
        },
        {
            "phone_number": "+1555123456",
            "subscription_status": "inactive",
            "subscription_date": "2024-01-10T09:00:00",
            "group": ["alerts"]
        },
        {
            "phone_number": "+1666789012",
            "subscription_status": "active",
            "subscription_date": "2024-03-05T16:20:00",
            "group": ["newsletter", "alerts", "promotions"]
        }
    ],
    "outbound_messages": [
        {
            "message_id": "out_001",
            "recipient": "+1234567890",
            "content": "Welcome to our newsletter!",
            "status": "delivered",
            "timestamp": "2024-03-01T10:00:00",
            "message_type": "newsletter"
        },
        {
            "message_id": "out_002",
            "recipient": "+1987654321",
            "content": "System maintenance scheduled for tonight.",
            "status": "sent",
            "timestamp": "2024-03-10T08:30:00",
            "message_type": "alert"
        },
        {
            "message_id": "out_003",
            "recipient": "+1666789012",
            "content": "Your order has been shipped.",
            "status": "queued",
            "timestamp": "2024-03-15T12:00:00",
            "message_type": "notification"
        }
    ],
    "inbound_messages": [
        {
            "message_id": "in_001",
            "sender": "+1234567890",
            "content": "I have a question about my subscription.",
            "received_at": "2024-03-12T09:15:00",
            "is_read": False,
            "resolution_status": "unresolved"
        },
        {
            "message_id": "in_002",
            "sender": "+1987654321",
            "content": "Please update my phone number.",
            "received_at": "2024-03-11T14:30:00",
            "is_read": True,
            "resolution_status": "resolved"
        },
        {
            "message_id": "in_003",
            "sender": "+1666789012",
            "content": "How do I unsubscribe from promotions?",
            "received_at": "2024-03-14T11:45:00",
            "is_read": False,
            "resolution_status": "unresolved"
        }
    ],
    "message_queues": [
        {
            "queue_id": "queue_001",
            "message_type": "newsletter",
            "scheduled_time": "2024-03-20T09:00:00",
            "recipient_filter": {"group": "newsletter"},
            "status": "pending"
        },
        {
            "queue_id": "queue_002",
            "message_type": "alert",
            "scheduled_time": "2024-03-18T18:00:00",
            "recipient_filter": {"group": "alerts"},
            "status": "pending"
        },
        {
            "queue_id": "queue_003",
            "message_type": "promotion",
            "scheduled_time": "2024-03-25T10:00:00",
            "recipient_filter": {"group": "promotions"},
            "status": "cancelled"
        }
    ],
    "message_templates": [
        {
            "template_id": "tpl_001",
            "name": "welcome_message",
            "content": "Welcome to {service_name}! We're glad to have you.",
            "created_at": "2024-01-01T00:00:00"
        },
        {
            "template_id": "tpl_002",
            "name": "maintenance_alert",
            "content": "Scheduled maintenance on {date}. Service may be unavailable.",
            "created_at": "2024-01-15T00:00:00"
        },
        {
            "template_id": "tpl_003",
            "name": "subscription_confirmation",
            "content": "You have been subscribed to {group_name}. Reply STOP to unsubscribe.",
            "created_at": "2024-02-01T00:00:00"
        }
    ],
    "scheduled_messages": [],
    "webhooks": [],
    "opt_out_list": [],
    "rate_limits": {},
    "next_outbound_id": 4,
    "next_inbound_id": 4,
    "next_queue_id": 4,
    "next_template_id": 4,
    "next_scheduled_id": 1,
    "next_webhook_id": 1,
    "current_timestamp": "2024-03-15T12:00:00"
}


class SMSNotificationService:
    """
    SMS Notification and Messaging Service Environment API.
    
    This class provides a complete API for managing an SMS notification and messaging
    service, including subscriber management, message sending and receiving, queue
    management, and template handling.
    """
    
    def __init__(self) -> None:
        """
        Initialize the SMS Notification Service environment.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
        
        Returns:
            None
        """
        self.subscribers: List[Dict[str, Any]] = []
        self.outbound_messages: List[Dict[str, Any]] = []
        self.inbound_messages: List[Dict[str, Any]] = []
        self.message_queues: List[Dict[str, Any]] = []
        self.message_templates: List[Dict[str, Any]] = []
        self.scheduled_messages: List[Dict[str, Any]] = []
        self.webhooks: List[Dict[str, Any]] = []
        self.opt_out_list: List[str] = []
        self.rate_limits: Dict[str, List[str]] = {}
        self.next_outbound_id: int = 1
        self.next_inbound_id: int = 1
        self.next_queue_id: int = 1
        self.next_template_id: int = 1
        self.next_scheduled_id: int = 1
        self.next_webhook_id: int = 1
        self.current_timestamp: str = "2024-03-15T12:00:00"
        
        self._api_description = (
            "SMS Notification Service API for sending, receiving, and managing "
            "text messages at scale with subscriber management and queue handling."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a consistent timestamp for operations.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string.
        """
        return self.current_timestamp
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for long context scenarios (unused but required).
        
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
        Return the current state of all environment variables.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables:
                - subscribers: List of all subscriber records
                - outbound_messages: List of all sent messages
                - inbound_messages: List of all received messages
                - message_queues: List of all message queues
                - message_templates: List of all message templates
                - scheduled_messages: List of scheduled messages
                - webhooks: List of registered webhooks
                - opt_out_list: List of opted-out phone numbers
                - rate_limits: Rate limit tracking per phone number
                - next_outbound_id: Counter for next outbound message ID
                - next_inbound_id: Counter for next inbound message ID
                - next_queue_id: Counter for next queue ID
                - next_template_id: Counter for next template ID
                - next_scheduled_id: Counter for next scheduled message ID
                - next_webhook_id: Counter for next webhook ID
                - current_timestamp: Current system timestamp
        """
        return {
            "subscribers": deepcopy(self.subscribers),
            "outbound_messages": deepcopy(self.outbound_messages),
            "inbound_messages": deepcopy(self.inbound_messages),
            "message_queues": deepcopy(self.message_queues),
            "message_templates": deepcopy(self.message_templates),
            "scheduled_messages": deepcopy(self.scheduled_messages),
            "webhooks": deepcopy(self.webhooks),
            "opt_out_list": deepcopy(self.opt_out_list),
            "rate_limits": deepcopy(self.rate_limits),
            "next_outbound_id": self.next_outbound_id,
            "next_inbound_id": self.next_inbound_id,
            "next_queue_id": self.next_queue_id,
            "next_template_id": self.next_template_id,
            "next_scheduled_id": self.next_scheduled_id,
            "next_webhook_id": self.next_webhook_id,
            "current_timestamp": self.current_timestamp
        }
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_unresolved_inbound_messages(self) -> Dict[str, Any]:
        """
        Retrieve all inbound messages where resolution_status is "unresolved".
        
        Identifies pending user inquiries or issues that require follow-up.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - messages: List of unresolved inbound message records
                - count: Number of unresolved messages
        """
        unresolved = [
            msg for msg in self.inbound_messages 
            if msg.get("resolution_status") == "unresolved"
        ]
        return {
            "messages": deepcopy(unresolved),
            "count": len(unresolved)
        }
    
    def get_inbound_messages_by_read_status(self, is_read: bool) -> Dict[str, Any]:
        """
        List inbound messages filtered by is_read status.
        
        Allows prioritization of unread messages for processing.
        
        Args:
            is_read: Boolean flag to filter messages (True for read, False for unread).
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - messages: List of filtered inbound message records
                - count: Number of matching messages
        """
        filtered = [
            msg for msg in self.inbound_messages 
            if msg.get("is_read") == is_read
        ]
        return {
            "messages": deepcopy(filtered),
            "count": len(filtered)
        }
    
    def get_subscribers_by_group(self, group: str) -> Dict[str, Any]:
        """
        Retrieve all subscribers belonging to a specific group.
        
        Args:
            group: The group name to filter by (e.g., "newsletter", "alerts").
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - subscribers: List of subscriber records in the specified group
                - count: Number of matching subscribers
        """
        matching = [
            sub for sub in self.subscribers 
            if group in sub.get("group", [])
        ]
        return {
            "subscribers": deepcopy(matching),
            "count": len(matching)
        }
    
    def get_active_subscribers_by_group(self, group: str) -> Dict[str, Any]:
        """
        Retrieve only active subscribers in a given group.
        
        Ensures compliance with delivery rules by filtering out inactive subscribers.
        
        Args:
            group: The group name to filter by (e.g., "newsletter", "alerts").
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - subscribers: List of active subscriber records in the specified group
                - count: Number of matching subscribers
        """
        matching = [
            sub for sub in self.subscribers 
            if group in sub.get("group", []) 
            and sub.get("subscription_status") == "active"
        ]
        return {
            "subscribers": deepcopy(matching),
            "count": len(matching)
        }
    
    def list_all_subscribers(self) -> Dict[str, Any]:
        """
        Retrieve the full list of subscribers with their status and subscription details.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - subscribers: List of all subscriber records
                - count: Total number of subscribers
        """
        return {
            "subscribers": deepcopy(self.subscribers),
            "count": len(self.subscribers)
        }
    
    def get_subscriber_info(self, phone_number: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific subscriber.
        
        Args:
            phone_number: The subscriber's phone number.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - subscriber: The subscriber record if found
                - error: Error message if subscriber not found
        """
        if not phone_number:
            return {"error": "Phone number must be specified"}
        
        for sub in self.subscribers:
            if sub.get("phone_number") == phone_number:
                return {"subscriber": deepcopy(sub)}
        
        return {"error": f"Subscriber with phone number '{phone_number}' not found"}
    
    def get_message_template_by_name(self, name: str) -> Dict[str, Any]:
        """
        Retrieve a message template by its name for reuse in broadcasts or replies.
        
        Args:
            name: The name of the template to retrieve.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - template: The template record if found
                - error: Error message if template not found
        """
        for template in self.message_templates:
            if template.get("name") == name:
                return {"template": deepcopy(template)}
        return {"error": f"Template with name '{name}' not found"}
    
    def get_message_template_by_id(self, template_id: str) -> Dict[str, Any]:
        """
        Retrieve a message template using its unique template_id.
        
        Args:
            template_id: The unique identifier of the template.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - template: The template record if found
                - error: Error message if template not found
        """
        for template in self.message_templates:
            if template.get("template_id") == template_id:
                return {"template": deepcopy(template)}
        return {"error": f"Template with ID '{template_id}' not found"}
    
    def get_scheduled_message_queues(self) -> Dict[str, Any]:
        """
        List all message queues with their scheduled_time and status.
        
        Useful for monitoring or cancellation of pending message batches.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - queues: List of all message queue records
                - count: Total number of queues
        """
        return {
            "queues": deepcopy(self.message_queues),
            "count": len(self.message_queues)
        }
    
    def get_outbound_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Check the delivery status of a specific outbound message.
        
        Args:
            message_id: The unique identifier of the outbound message.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - message: The outbound message record with status
                - error: Error message if message not found
        """
        for msg in self.outbound_messages:
            if msg.get("message_id") == message_id:
                return {"message": deepcopy(msg)}
        return {"error": f"Outbound message with ID '{message_id}' not found"}
    
    def count_unresolved_inbound_messages(self) -> Dict[str, Any]:
        """
        Return the number of unresolved inbound messages.
        
        Useful to assess workload before sending broadcasts.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - count: Number of unresolved inbound messages
        """
        count = sum(
            1 for msg in self.inbound_messages 
            if msg.get("resolution_status") == "unresolved"
        )
        return {"count": count}
    
    def list_message_templates(self) -> Dict[str, Any]:
        """
        Retrieve all message templates.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - templates: List of all template records
                - count: Total number of templates
        """
        return {
            "templates": deepcopy(self.message_templates),
            "count": len(self.message_templates)
        }
    
    def list_scheduled_messages(self) -> Dict[str, Any]:
        """
        Retrieve all scheduled messages.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - scheduled_messages: List of all scheduled message records
                - count: Total number of scheduled messages
        """
        return {
            "scheduled_messages": deepcopy(self.scheduled_messages),
            "count": len(self.scheduled_messages)
        }
    
    def list_webhooks(self) -> Dict[str, Any]:
        """
        Retrieve all registered webhooks.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - webhooks: List of all webhook records
                - count: Total number of webhooks
        """
        return {
            "webhooks": deepcopy(self.webhooks),
            "count": len(self.webhooks)
        }
    
    def check_opt_out_status(self, phone_number: str) -> Dict[str, Any]:
        """
        Check if a phone number has opted out of receiving messages.
        
        Args:
            phone_number: The phone number to check.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - phone_number: The checked phone number
                - opted_out: Boolean indicating opt-out status
        """
        if not phone_number:
            return {"error": "Phone number must be specified"}
        
        return {
            "phone_number": phone_number,
            "opted_out": phone_number in self.opt_out_list
        }
    
    def check_rate_limit_status(self, phone_number: str) -> Dict[str, Any]:
        """
        Check the rate limit status for a phone number.
        
        Args:
            phone_number: The phone number to check.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - phone_number: The checked phone number
                - messages_sent: Number of messages sent in current window
                - limit: Maximum messages allowed
                - is_limited: Boolean indicating if rate limited
        """
        if not phone_number:
            return {"error": "Phone number must be specified"}
        
        messages_sent = len(self.rate_limits.get(phone_number, []))
        limit = 3
        
        return {
            "phone_number": phone_number,
            "messages_sent": messages_sent,
            "limit": limit,
            "is_limited": messages_sent >= limit
        }
    
    def get_delivery_report(self, message_id: str) -> Dict[str, Any]:
        """
        Get the delivery report for a specific outbound message.
        
        Args:
            message_id: The unique identifier of the outbound message.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - message_id: The message ID
                - status: Delivery status
                - recipient: The recipient phone number
                - timestamp: When the message was sent
                - error: Error message if message not found
        """
        if not message_id:
            return {"error": "Message ID must be specified"}
        
        for msg in self.outbound_messages:
            if msg.get("message_id") == message_id:
                return {
                    "message_id": message_id,
                    "status": msg.get("status"),
                    "recipient": msg.get("recipient"),
                    "timestamp": msg.get("timestamp")
                }
        
        return {"error": f"Message with ID '{message_id}' not found"}
    
    def get_delivery_statistics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get delivery statistics for a date range.
        
        Args:
            start_date: Start date in ISO format.
            end_date: End date in ISO format.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - total_sent: Total messages sent
                - delivered: Number delivered
                - failed: Number failed
                - queued: Number queued
                - period: The date range
        """
        if not start_date or not end_date:
            return {"error": "Both start_date and end_date must be specified"}
        
        total = 0
        delivered = 0
        failed = 0
        queued = 0
        
        for msg in self.outbound_messages:
            timestamp = msg.get("timestamp", "")
            if start_date <= timestamp <= end_date:
                total += 1
                status = msg.get("status")
                if status == "delivered":
                    delivered += 1
                elif status == "failed":
                    failed += 1
                elif status == "queued":
                    queued += 1
        
        return {
            "total_sent": total,
            "delivered": delivered,
            "failed": failed,
            "queued": queued,
            "period": {"start": start_date, "end": end_date}
        }
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def send_critical_alert(
        self, 
        content: str, 
        group: str, 
        recipient_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Immediately send a high-priority SMS to a filtered set of subscribers.
        
        Critical alerts bypass normal queue and unresolved message checks.
        
        Args:
            content: The message content to send.
            group: The subscriber group to target.
            recipient_filter: Optional additional filter criteria.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - success: Boolean indicating operation success
                - messages_sent: List of message IDs created
                - recipients_count: Number of recipients
                - error: Error message if operation failed
        """
        if not content:
            return {"error": "Message content cannot be empty"}
        
        if not group:
            return {"error": "Target group must be specified"}
        
        active_subscribers = [
            sub for sub in self.subscribers
            if group in sub.get("group", [])
            and sub.get("subscription_status") == "active"
        ]
        
        if not active_subscribers:
            return {"error": f"No active subscribers found in group '{group}'"}
        
        messages_sent = []
        timestamp = self._timestamp()
        
        for subscriber in active_subscribers:
            message_id = f"out_{self.next_outbound_id:03d}"
            self.next_outbound_id += 1
            
            outbound_msg = {
                "message_id": message_id,
                "recipient": subscriber["phone_number"],
                "content": content,
                "status": "sent",
                "timestamp": timestamp,
                "message_type": "critical_alert"
            }
            self.outbound_messages.append(outbound_msg)
            messages_sent.append(message_id)
        
        return {
            "success": True,
            "messages_sent": messages_sent,
            "recipients_count": len(active_subscribers)
        }
    
    def send_broadcast_message(
        self, 
        content: str, 
        group: str
    ) -> Dict[str, Any]:
        """
        Schedule or send a non-critical message to a subscriber group.
        
        Fails if there are unresolved inbound messages that require follow-up.
        
        Args:
            content: The message content to broadcast.
            group: The subscriber group to target.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - success: Boolean indicating operation success
                - messages_sent: List of message IDs created
                - recipients_count: Number of recipients
                - error: Error message if operation failed
        """
        if not content:
            return {"error": "Message content cannot be empty"}
        
        if not group:
            return {"error": "Target group must be specified"}
        
        unresolved_count = sum(
            1 for msg in self.inbound_messages
            if msg.get("resolution_status") == "unresolved"
        )
        
        if unresolved_count > 0:
            return {
                "error": f"Cannot send broadcast: {unresolved_count} unresolved "
                        f"inbound message(s) require follow-up first"
            }
        
        active_subscribers = [
            sub for sub in self.subscribers
            if group in sub.get("group", [])
            and sub.get("subscription_status") == "active"
        ]
        
        if not active_subscribers:
            return {"error": f"No active subscribers found in group '{group}'"}
        
        messages_sent = []
        timestamp = self._timestamp()
        
        for subscriber in active_subscribers:
            message_id = f"out_{self.next_outbound_id:03d}"
            self.next_outbound_id += 1
            
            outbound_msg = {
                "message_id": message_id,
                "recipient": subscriber["phone_number"],
                "content": content,
                "status": "queued",
                "timestamp": timestamp,
                "message_type": "broadcast"
            }
            self.outbound_messages.append(outbound_msg)
            messages_sent.append(message_id)
        
        return {
            "success": True,
            "messages_sent": messages_sent,
            "recipients_count": len(active_subscribers)
        }
    
    def send_message(self, content: str, recipient: str) -> Dict[str, Any]:
        """
        Send a single SMS message to a recipient.
        
        Subject to rate limiting and opt-out checks.
        
        Args:
            content: The message content to send.
            recipient: The recipient phone number.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - success: Boolean indicating operation success
                - message_id: The ID of the sent message
                - error: Error message if operation failed
        """
        if not content:
            return {"error": "Message content cannot be empty"}
        
        if not recipient:
            return {"error": "Recipient must be specified"}
        
        if recipient in self.opt_out_list:
            return {"error": f"Recipient '{recipient}' has opted out of messages"}
        
        if recipient not in self.rate_limits:
            self.rate_limits[recipient] = []
        
        if len(self.rate_limits[recipient]) >= 3:
            return {"error": f"Rate limit exceeded for recipient '{recipient}'"}
        
        message_id = f"out_{self.next_outbound_id:03d}"
        self.next_outbound_id += 1
        timestamp = self._timestamp()
        
        outbound_msg = {
            "message_id": message_id,
            "recipient": recipient,
            "content": content,
            "status": "sent",
            "timestamp": timestamp,
            "message_type": "direct"
        }
        self.outbound_messages.append(outbound_msg)
        self.rate_limits[recipient].append(timestamp)
        
        return {
            "success": True,
            "message_id": message_id
        }
    
    def send_template_message(
        self,
        template_name: str,
        recipient: str,
        variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send a message using a template with variable substitution.
        
        Args:
            template_name: The name of the template to use.
            recipient: The recipient phone number.
            variables: Dictionary of variables to substitute in the template.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - success: Boolean indicating operation success
                - message_id: The ID of the sent message
                - content: The rendered message content
                - error: Error message if operation failed
        """
        if not template_name:
            return {"error": "Template name must be specified"}
        
        if not recipient:
            return {"error": "Recipient must be specified"}
        
        template = None
        for tpl in self.message_templates:
            if tpl.get("name") == template_name:
                template = tpl
                break
        
        if not template:
            return {"error": f"Template with name '{template_name}' not found"}
        
        content = template.get("content", "")
        if variables:
            for key, value in variables.items():
                content = content.replace("{" + key + "}", str(value))
                content = content.replace("{{" + key + "}}", str(value))
        
        message_id = f"out_{self.next_outbound_id:03d}"
        self.next_outbound_id += 1
        timestamp = self._timestamp()
        
        outbound_msg = {
            "message_id": message_id,
            "recipient": recipient,
            "content": content,
            "status": "sent",
            "timestamp": timestamp,
            "message_type": "template"
        }
        self.outbound_messages.append(outbound_msg)
        
        return {
            "success": True,
            "message_id": message_id,
            "content": content
        }
    
    def enqueue_message_batch(
        self,
        message_type: str,
        scheduled_time: str,
        recipient_filter: Dict[str, Any],
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new message queue entry for a batch of messages.
        
        Args:
            message_type: Type of message (e.g., "newsletter", "alert").
            scheduled_time: ISO format timestamp for when to send.
            recipient_filter: Filter criteria for recipients.
            content: Optional message content for the batch.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - success: Boolean indicating operation success
                - queue_id: The ID of the created queue
                - error: Error message if operation failed
        """
        if not message_type:
            return {"error": "Message type must be specified"}
        
        if not scheduled_time:
            return {"error": "Scheduled time must be specified"}
        
        if not recipient_filter:
            return {"error": "Recipient filter must be specified"}
        
        queue_id = f"queue_{self.next_queue_id}"
        self.next_queue_id += 1
        
        queue_entry = {
            "queue_id": queue_id,
            "message_type": message_type,
            "scheduled_time": scheduled_time,
            "recipient_filter": recipient_filter,
            "content": content,
            "status": "pending",
            "created_at": self._timestamp()
        }
        
        self.message_queues.append(queue_entry)
        
        return {
            "success": True,
            "queue_id": queue_id
        }
    
    def get_queue_status(self, queue_id: str) -> Dict[str, Any]:
        """Get the status of a message queue.
        
        Args:
            queue_id: The ID of the queue to check.
        
        Returns:
            Dict[str, Any]: Queue status information.
        """
        for queue in self.message_queues:
            if queue.get("queue_id") == queue_id:
                return queue
        return {"error": f"Queue {queue_id} not found"}
    
    def cancel_scheduled_queue(self, queue_id: str) -> Dict[str, Any]:
        """Cancel a scheduled message queue.
        
        Args:
            queue_id: The ID of the queue to cancel.
        
        Returns:
            Dict[str, Any]: Result of the cancellation operation.
        """
        for queue in self.message_queues:
            if queue.get("queue_id") == queue_id:
                if queue.get("status") == "sent":
                    return {"error": "Cannot cancel a queue that has already been sent"}
                queue["status"] = "cancelled"
                return {"success": True, "queue_id": queue_id}
        return {"error": f"Queue {queue_id} not found"}


__TEST_CASES__ = [
    {
        "name": "test_schedule_message_queue_success",
        "input": {
            "message_type": "notification",
            "scheduled_time": "2024-01-15T10:00:00Z",
            "recipient_filter": {"region": "us-east"},
            "content": "Test message"
        },
        "expected": {"success": True, "queue_id": "queue_1"}
    },
    {
        "name": "test_schedule_message_queue_missing_type",
        "input": {
            "message_type": "",
            "scheduled_time": "2024-01-15T10:00:00Z",
            "recipient_filter": {"region": "us-east"}
        },
        "expected": {"error": "Message type must be specified"}
    },
    {
        "name": "test_schedule_message_queue_missing_time",
        "input": {
            "message_type": "notification",
            "scheduled_time": "",
            "recipient_filter": {"region": "us-east"}
        },
        "expected": {"error": "Scheduled time must be specified"}
    },
    {
        "name": "test_schedule_message_queue_missing_filter",
        "input": {
            "message_type": "notification",
            "scheduled_time": "2024-01-15T10:00:00Z",
            "recipient_filter": {}
        },
        "expected": {"error": "Recipient filter must be specified"}
    },
    {
        "name": "test_get_queue_status_success",
        "input": {"queue_id": "queue_1"},
        "expected": {"queue_id": "queue_1", "status": "pending"}
    },
    {
        "name": "test_get_queue_status_not_found",
        "input": {"queue_id": "queue_999"},
        "expected": {"error": "Queue queue_999 not found"}
    },
    {
        "name": "test_cancel_scheduled_queue_success",
        "input": {"queue_id": "queue_1"},
        "expected": {"success": True, "queue_id": "queue_1"}
    },
    {
        "name": "test_cancel_scheduled_queue_not_found",
        "input": {"queue_id": "queue_999"},
        "expected": {"error": "Queue queue_999 not found"}
    }
]
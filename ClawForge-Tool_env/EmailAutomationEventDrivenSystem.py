from copy import deepcopy
from typing import Dict, List, Optional, Union, Any, Tuple
import re
from datetime import datetime

DEFAULT_STATE = {
    "rules": [],
    "email_log": [],
    "action_log": [],
    "social_profiles": {},
    "brief_templates": {},
    "monitored_topics": [],
    "rule_counter": 1,
    "email_counter": 1,
    "post_counter": 1,
}

VALID_TRIGGER_TYPES = ("new_email", "email_follow_up", "schedule_reminder", "trend_alert")
VALID_CONDITION_OPS = ("eq", "neq", "gt", "lt", "gte", "lte", "contains", "matches", "in_list", "not_in_list")
VALID_PLATFORMS = ("reddit", "twitter", "linkedin", "slack", "internal_blog")
VALID_ACTION_TYPES = ("post_topic", "reply_to_thread", "update_social_profile", "schedule_content",
                     "trigger_follow_up", "archive_email", "create_brief_template")


class MailBriefSocialEnv:
    """
    A collaborative automation environment for processing emails to extract briefs
    and automatically posting/responding on social platforms.

    This environment enables agents to configure intelligent rules that monitor
    incoming emails, extract key information, and automatically create/respond to
    content on Reddit, Twitter, and other platforms based on extracted insights.

    Attributes:
        rules (List[Dict]): Configured automation rules for email→social conversion.
        email_log (List[Dict]): History of all processed emails with metadata.
        action_log (List[Dict]): History of all executed social actions.
        social_profiles (Dict): Registered social media profiles and their status.
        brief_templates (Dict): Predefined templates for extracting and formatting briefs.
        monitored_topics (List): Topics/hashtags currently being monitored.
        rule_counter (int): Auto-incrementing rule ID counter.
        email_counter (int): Auto-incrementing email ID counter.
        post_counter (int): Auto-incrementing social post ID counter.
    """

    def __init__(self):
        self.rules: List[Dict[str, Any]]
        self.email_log: List[Dict[str, Any]]
        self.action_log: List[Dict[str, Any]]
        self.social_profiles: Dict[str, Dict[str, Any]]
        self.brief_templates: Dict[str, Dict[str, Any]]
        self.monitored_topics: List[str]
        self.rule_counter: int
        self.email_counter: int
        self.post_counter: int
        self._api_description = (
            "This tool automates email-to-social workflows by extracting briefs from "
            "incoming emails and automatically posting/responding on Reddit, Twitter, "
            "and other platforms based on configured rules and templates."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load initial state from scenario dictionary.

        Args:
            scenario (dict): Initial environment configuration.
            long_context (bool): Whether to include extended context (unused in this implementation).

        Returns:
            None: Updates internal state in place.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.rules = scenario.get("rules", DEFAULT_STATE_COPY["rules"])
        self.email_log = scenario.get("email_log", DEFAULT_STATE_COPY["email_log"])
        self.action_log = scenario.get("action_log", DEFAULT_STATE_COPY["action_log"])
        self.social_profiles = scenario.get("social_profiles", DEFAULT_STATE_COPY["social_profiles"])
        self.brief_templates = scenario.get("brief_templates", DEFAULT_STATE_COPY["brief_templates"])
        self.monitored_topics = scenario.get("monitored_topics", DEFAULT_STATE_COPY["monitored_topics"])
        self.rule_counter = scenario.get("rule_counter", DEFAULT_STATE_COPY["rule_counter"])
        self.email_counter = scenario.get("email_counter", DEFAULT_STATE_COPY["email_counter"])
        self.post_counter = scenario.get("post_counter", DEFAULT_STATE_COPY["post_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including rules, email_log,
                action_log, social_profiles, brief_templates, monitored_topics,
                and counters.
        """
        return {
            "rules": self.rules,
            "email_log": self.email_log,
            "action_log": self.action_log,
            "social_profiles": self.social_profiles,
            "brief_templates": self.brief_templates,
            "monitored_topics": self.monitored_topics,
            "rule_counter": self.rule_counter,
            "email_counter": self.email_counter,
            "post_counter": self.post_counter,
        }

    # ── Social Profile Management ──────────────────────────────────────

    def register_social_profile(
        self,
        platform: str,
        profile_name: str,
        credentials: Dict[str, str],
        default_topics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Register a social media profile for automated posting.

        Args:
            platform (str): Social platform - must be one of: reddit, twitter, linkedin, slack, internal_blog.
            profile_name (str): Unique name for this profile (e.g., 'company_twitter').
            credentials (Dict[str, str]): Platform-specific authentication credentials.
            default_topics (List[str], optional): Default topics/hashtags for this profile.

        Returns:
            success (bool): Whether registration succeeded.
            profile (Dict): The registered profile metadata.
        """
        if platform not in VALID_PLATFORMS:
            return {"error": f"Invalid platform '{platform}'. Must be one of: {', '.join(VALID_PLATFORMS)}"}
        
        if profile_name in self.social_profiles:
            return {"error": f"Profile '{profile_name}' is already registered."}
        
        if not credentials.get("api_key") and not credentials.get("access_token"):
            return {"error": "Credentials must contain either 'api_key' or 'access_token'."}
        
        self.social_profiles[profile_name] = {
            "platform": platform,
            "profile_name": profile_name,
            "active": True,
            "credentials": credentials,
            "default_topics": default_topics or [],
            "post_count": 0,
            "last_post_time": None,
        }
        
        return {
            "success": True,
            "profile": self.social_profiles[profile_name]
        }

    def update_profile_topics(
        self,
        profile_name: str,
        topics: List[str],
        mode: str = "replace"
    ) -> Dict[str, Any]:
        """
        Update monitored topics for a social profile.

        Args:
            profile_name (str): Name of the registered profile.
            topics (List[str]): New topics/hashtags to monitor.
            mode (str): 'replace' to replace all topics, 'add' to append, 'remove' to delete.
                       Defaults to 'replace'.

        Returns:
            success (bool): Whether update succeeded.
            updated_topics (List[str]): Current topics after update.
        """
        if profile_name not in self.social_profiles:
            return {"error": f"Profile '{profile_name}' not found."}
        
        profile = self.social_profiles[profile_name]
        current_topics = profile["default_topics"]
        
        if mode == "replace":
            profile["default_topics"] = topics
        elif mode == "add":
            profile["default_topics"] = list(set(current_topics + topics))
        elif mode == "remove":
            profile["default_topics"] = [t for t in current_topics if t not in topics]
        else:
            return {"error": f"Invalid mode '{mode}'. Must be 'replace', 'add', or 'remove'."}
        
        return {
            "success": True,
            "updated_topics": profile["default_topics"]
        }

    def list_profiles(
        self,
        platform_filter: Optional[str] = None,
        active_only: bool = False
    ) -> Dict[str, Any]:
        """
        List registered social media profiles.

        Args:
            platform_filter (str, optional): Filter by platform name.
            active_only (bool): If True, return only active profiles. Defaults to False.

        Returns:
            profiles (List[Dict]): Matching profiles with metadata.
            total (int): Total matching count.
        """
        profiles = list(self.social_profiles.values())
        
        if platform_filter:
            profiles = [p for p in profiles if p["platform"] == platform_filter]
        
        if active_only:
            profiles = [p for p in profiles if p["active"]]
        
        return {
            "profiles": profiles,
            "total": len(profiles)
        }

    # ── Brief Template Management ──────────────────────────────────────

    def create_brief_template(
        self,
        template_name: str,
        extraction_patterns: List[Dict[str, str]],
        format_string: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Create a template for extracting briefs from emails.

        Args:
            template_name (str): Unique name for this template.
            extraction_patterns (List[Dict[str, str]]): Patterns to extract content.
                Each pattern has 'field' (email_field) and 'pattern' (regex).
            format_string (str): Format string for the final brief content.
                Use {field_name} placeholders for extracted values.
            platforms (List[str]): Target platforms for this template.

        Returns:
            success (bool): Whether creation succeeded.
            template (Dict): The created template.
        """
        if template_name in self.brief_templates:
            return {"error": f"Template '{template_name}' already exists."}
        
        for platform in platforms:
            if platform not in VALID_PLATFORMS:
                return {"error": f"Invalid platform '{platform}' in platforms list."}
        
        if not extraction_patterns:
            return {"error": "At least one extraction pattern is required."}
        
        self.brief_templates[template_name] = {
            "template_name": template_name,
            "extraction_patterns": extraction_patterns,
            "format_string": format_string,
            "platforms": platforms,
            "usage_count": 0,
        }
        
        return {
            "success": True,
            "template": self.brief_templates[template_name]
        }

    def extract_brief_from_email(
        self,
        email_content: Dict[str, Any],
        template_name: str
    ) -> Dict[str, Any]:
        """
        Extract a brief from email content using a template.

        Args:
            email_content (Dict[str, Any]): Email content with fields like subject, body, sender.
            template_name (str): Name of the template to use.

        Returns:
            success (bool): Whether extraction succeeded.
            extracted_data (Dict): Extracted fields.
            formatted_brief (str): Formatted brief text.
        """
        if template_name not in self.brief_templates:
            return {"error": f"Template '{template_name}' not found."}
        
        template = self.brief_templates[template_name]
        extracted = {}
        
        for pattern_info in template["extraction_patterns"]:
            field = pattern_info["field"]
            regex_pattern = pattern_info["pattern"]
            
            content = email_content.get(field, "")
            if not content:
                continue
            
            match = re.search(regex_pattern, content, re.IGNORECASE)
            if match:
                extracted[field] = match.group(1) if match.groups() else match.group(0)
        
        if not extracted:
            return {
                "success": False,
                "error": "No patterns matched email content.",
                "extracted_data": {}
            }
        
        try:
            formatted_brief = template["format_string"].format(**extracted)
        except KeyError as e:
            return {
                "success": False,
                "error": f"Missing field in format string: {str(e)}",
                "extracted_data": extracted
            }
        
        template["usage_count"] += 1
        
        return {
            "success": True,
            "extracted_data": extracted,
            "formatted_brief": formatted_brief
        }

    # ── Rule Management ────────────────────────────────────────────────

    def create_rule(
        self,
        name: str = None,
        trigger_type: str = None,
        condition: Dict[str, str] = None,
        actions: List[Dict[str, Any]] = None,
        template_name: Optional[str] = None,
        target_profiles: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create an automation rule for email-to-social processing.

        Args:
            name (str): Human-readable rule name.
            trigger_type (str): Event type that triggers evaluation.
            condition (Dict[str, str]): Condition specification with keys:
                field (str): Email field to evaluate.
                op (str): Comparison operator.
                value (str): Value to compare against.
            actions (List[Dict]): Ordered list of actions to execute.
                Each action has 'type' and 'params'.
            template_name (str, optional): Brief template to use for extraction.
            target_profiles (List[str], optional): Specific social profiles to target.

        Returns:
            rule_id (int): Unique rule identifier.
            rule (Dict): The created rule with all fields.
        """
        if not isinstance(name, str) or not name.strip():
            return {"error": "name must be a non-empty string."}
        if not isinstance(trigger_type, str):
            return {"error": "trigger_type must be a string."}
        if not isinstance(condition, dict):
            return {"error": "condition must be a dictionary."}
        if not isinstance(actions, list):
            return {"error": "actions must be a list."}

        if trigger_type not in VALID_TRIGGER_TYPES:
            return {"error": f"Invalid trigger_type '{trigger_type}'. Must be one of: {', '.join(VALID_TRIGGER_TYPES)}"}
        
        if "field" not in condition or "op" not in condition or "value" not in condition:
            return {"error": "Condition must contain 'field', 'op', and 'value' keys."}
        
        if condition["op"] not in VALID_CONDITION_OPS:
            return {"error": f"Invalid condition operator '{condition['op']}'. Must be one of: {', '.join(VALID_CONDITION_OPS)}"}
        
        if not actions:
            return {"error": "At least one action is required."}
        
        if template_name and template_name not in self.brief_templates:
            return {"error": f"Template '{template_name}' not found."}
        
        if target_profiles:
            for profile in target_profiles:
                if profile not in self.social_profiles:
                    return {"error": f"Target profile '{profile}' not found."}
        
        rule_id = self.rule_counter
        self.rule_counter += 1
        
        rule = {
            "rule_id": rule_id,
            "name": name,
            "enabled": True,
            "trigger_type": trigger_type,
            "condition": condition,
            "actions": actions,
            "template_name": template_name,
            "target_profiles": target_profiles or [],
            "match_count": 0,
        }
        
        self.rules.append(rule)
        return {"rule_id": rule_id, "rule": rule}

    def update_rule(self, rule_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update fields of an existing rule.

        Args:
            rule_id (int): ID of the rule to update.
            updates (Dict): Fields to change. Allowed keys:
                name, enabled, trigger_type, condition, actions, template_name, target_profiles.

        Returns:
            success (bool): Whether update succeeded.
            rule (Dict): The updated rule.
        """
        rule = self._find_rule(rule_id)
        if not rule:
            return {"error": f"Rule ID {rule_id} not found."}
        
        allowed_fields = {
            "name", "enabled", "trigger_type", "condition", "actions",
            "template_name", "target_profiles"
        }
        
        invalid = set(updates.keys()) - allowed_fields
        if invalid:
            return {"error": f"Invalid update fields: {', '.join(invalid)}"}
        
        for key, value in updates.items():
            if key == "trigger_type" and value not in VALID_TRIGGER_TYPES:
                return {"error": f"Invalid trigger_type '{value}'."}
            rule[key] = value
        
        return {"success": True, "rule": rule}

    def list_rules(
        self,
        enabled_only: bool = False,
        trigger_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List configured automation rules.

        Args:
            enabled_only (bool): If True, return only enabled rules.
            trigger_type (str, optional): Filter by trigger type.

        Returns:
            rules (List[Dict]): Matching rules.
            total (int): Total matching count.
        """
        rules = self.rules
        
        if enabled_only:
            rules = [r for r in rules if r["enabled"]]
        
        if trigger_type:
            rules = [r for r in rules if r["trigger_type"] == trigger_type]
        
        return {"rules": rules, "total": len(rules)}

    # ── Email Processing & Event Simulation ───────────────────────────

    def receive_email(
        self,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulate receiving an email and trigger rule evaluation.

        Args:
            sender (str): Sender email address.
            recipient (str): Recipient email address.
            subject (str): Email subject line.
            body (str): Email body content.
            metadata (Dict, optional): Additional email metadata.

        Returns:
            email_id (int): Unique email identifier.
            matched_rules (int): Number of rules whose conditions matched.
            executed_actions (List[Dict]): Results of executed actions.
            extracted_brief (str, optional): Extracted brief if template was used.
        """
        email_id = self.email_counter
        self.email_counter += 1
        
        email_content = {
            "sender": sender,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        
        email_record = {
            "email_id": email_id,
            **email_content,
            "processed": False,
        }
        
        self.email_log.append(email_record)
        
        matched_count = 0
        executed_actions = []
        extracted_brief = None
        
        for rule in self.rules:
            if not rule["enabled"]:
                continue
            if rule["trigger_type"] != "new_email":
                continue
            
            if not self._evaluate_condition(rule["condition"], email_content):
                continue
            
            rule["match_count"] += 1
            matched_count += 1
            
            # Extract brief if template specified
            if rule["template_name"]:
                extraction_result = self.extract_brief_from_email(
                    email_content,
                    rule["template_name"]
                )
                
                if extraction_result.get("success"):
                    extracted_brief = extraction_result["formatted_brief"]
                    email_content["extracted_brief"] = extracted_brief

            # Execute actions
            for action in rule["actions"]:
                action = deepcopy(action)
                action["params"]["email_id"] = email_id
                if extracted_brief:
                    action["params"]["extracted_brief"] = extracted_brief
                
                result = self._execute_action(action, email_content)
                executed_actions.append(result)
        
        email_record["processed"] = True
        email_record["matched_rules"] = matched_count
        
        response = {
            "email_id": email_id,
            "matched_rules": matched_count,
            "executed_actions": executed_actions,
        }
        
        if extracted_brief:
            response["extracted_brief"] = extracted_brief
        
        return response

    def search_emails(
        self,
        search_query: str,
        field: str = "all",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search through email history.

        Args:
            search_query (str): Search query string.
            field (str): Field to search in: 'sender', 'subject', 'body', or 'all'.
            limit (int): Maximum results to return.

        Returns:
            emails (List[Dict]): Matching emails.
            total (int): Total matching count.
        """
        emails = []
        query_lower = search_query.lower()
        
        for email in self.email_log:
            match = False
            
            if field == "all" or field == "sender":
                if query_lower in email["sender"].lower():
                    match = True
            
            if not match and (field == "all" or field == "subject"):
                if query_lower in email["subject"].lower():
                    match = True
            
            if not match and (field == "all" or field == "body"):
                if query_lower in email["body"].lower():
                    match = True
            
            if match:
                emails.append(email)
                if len(emails) >= limit:
                    break
        
        return {"emails": emails, "total": len(emails)}

    # ── Action Execution ──────────────────────────────────────────────

    def _execute_action(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a social media action.

        Args:
            action (Dict[str, Any]): Action specification with 'type' and 'params'.
            context (Dict[str, Any]): Context data including email content.

        Returns:
            Dict[str, Any]: Action execution result.
        """
        action_type = action.get("type", "unknown")
        params = action.get("params", {})
        
        # Generate post ID for social posts
        if action_type in ["post_topic", "reply_to_thread"]:
            post_id = self.post_counter
            self.post_counter += 1
            params["post_id"] = post_id
        
        # Update relevant profile
        profile_name = params.get("profile_name")
        if profile_name and profile_name in self.social_profiles:
            profile = self.social_profiles[profile_name]
            profile["post_count"] += 1
            profile["last_post_time"] = datetime.now().isoformat()
        
        # Simulate action execution
        result = {
            "action_type": action_type,
            "params": params,
            "context": {
                "email_sender": context.get("sender"),
                "email_subject": context.get("subject"),
            },
            "timestamp": datetime.now().isoformat(),
            "status": "executed",
            "simulated_output": self._generate_action_output(action_type, params, context),
        }
        
        self.action_log.append(result)
        return result

    def _generate_action_output(
        self,
        action_type: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate simulated output for different action types."""
        if action_type == "post_topic":
            platform = params.get("platform", "unknown")
            title = params.get("title", "No title")
            return f"Posted topic '{title}' on {platform} (simulated)"
        
        elif action_type == "reply_to_thread":
            platform = params.get("platform", "unknown")
            thread_id = params.get("thread_id", "unknown")
            return f"Replied to thread {thread_id} on {platform} (simulated)"
        
        elif action_type == "update_social_profile":
            profile = params.get("profile_name", "unknown")
            return f"Updated social profile '{profile}' (simulated)"
        
        elif action_type == "schedule_content":
            platform = params.get("platform", "unknown")
            schedule_time = params.get("schedule_time", "now")
            return f"Scheduled content for {platform} at {schedule_time} (simulated)"
        
        elif action_type == "archive_email":
            email_id = params.get("email_id", "unknown")
            return f"Archived email {email_id} (simulated)"
        
        else:
            return f"Executed {action_type} action (simulated)"

    def _evaluate_condition(
        self,
        condition: Dict[str, str],
        data: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a condition against data.

        Args:
            condition (Dict[str, str]): Condition with 'field', 'op', 'value'.
            data (Dict[str, Any]): Data to evaluate against.

        Returns:
            bool: Whether condition is satisfied.
        """
        field = condition["field"]
        op = condition["op"]
        expected = condition["value"]
        
        actual = data.get(field)
        if actual is None:
            return False
        
        actual_str = str(actual)
        expected_str = str(expected)
        
        # List operations
        if op == "in_list":
            expected_items = [item.strip() for item in expected_str.split(",")]
            return actual_str in expected_items
        
        if op == "not_in_list":
            expected_items = [item.strip() for item in expected_str.split(",")]
            return actual_str not in expected_items
        
        # String operations
        if op == "eq":
            return actual_str == expected_str
        
        if op == "neq":
            return actual_str != expected_str
        
        if op == "contains":
            return expected_str.lower() in actual_str.lower()
        
        if op == "matches":
            return bool(re.search(expected_str, actual_str, re.IGNORECASE))
        
        # Numeric operations
        try:
            actual_num = float(actual)
            expected_num = float(expected)
        except (ValueError, TypeError):
            return False
        
        if op == "gt":
            return actual_num > expected_num
        
        if op == "lt":
            return actual_num < expected_num
        
        if op == "gte":
            return actual_num >= expected_num
        
        if op == "lte":
            return actual_num <= expected_num
        
        return False

    def _find_rule(self, rule_id: int) -> Optional[Dict[str, Any]]:
        """Find a rule by ID."""
        for rule in self.rules:
            if rule["rule_id"] == rule_id:
                return rule
        return None

    # ── Analytics & Monitoring ────────────────────────────────────────

    def get_analytics(
        self,
        time_period: str = "all",
        profile_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for email-to-social automation.

        Args:
            time_period (str): Time period for analytics: 'day', 'week', 'month', or 'all'.
            profile_filter (str, optional): Filter by profile name.

        Returns:
            Dict[str, Any]: Analytics data including counts and metrics.
        """
        # Count active rules
        active_rules = len([r for r in self.rules if r["enabled"]])
        
        # Count processed emails
        processed_emails = len([e for e in self.email_log if e.get("processed")])
        
        # Count social posts by platform
        platform_counts = {}
        for profile in self.social_profiles.values():
            if profile_filter and profile["profile_name"] != profile_filter:
                continue
            
            platform = profile["platform"]
            platform_counts[platform] = platform_counts.get(platform, 0) + profile["post_count"]
        
        # Count rule matches
        rule_matches = sum(rule["match_count"] for rule in self.rules)
        
        # Template usage
        template_usage = {
            name: template["usage_count"]
            for name, template in self.brief_templates.items()
        }
        
        return {
            "active_rules": active_rules,
            "processed_emails": processed_emails,
            "total_emails": len(self.email_log),
            "social_posts_by_platform": platform_counts,
            "total_social_posts": sum(platform_counts.values()),
            "rule_matches": rule_matches,
            "template_usage": template_usage,
            "monitored_topics_count": len(self.monitored_topics),
        }

    def get_action_log(
        self,
        profile_name: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Retrieve history of executed actions.

        Args:
            profile_name (str, optional): Filter by profile name.
            platform (str, optional): Filter by platform.
            limit (int): Maximum actions to return.

        Returns:
            actions (List[Dict]): Executed actions, newest first.
            total (int): Total action count.
        """
        actions = self.action_log
        
        if profile_name:
            actions = [a for a in actions if a.get("params", {}).get("profile_name") == profile_name]
        
        if platform:
            actions = [a for a in actions if a.get("params", {}).get("platform") == platform]
        
        # Return newest first
        actions = list(reversed(actions))[:limit]
        
        return {
            "actions": actions,
            "total": len(actions),
            "filtered_total": len(self.action_log)
        }

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })
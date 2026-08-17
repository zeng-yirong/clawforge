from copy import deepcopy
from typing import Dict, List, Optional, Union, Any, Tuple
import random
import json
from datetime import datetime, timedelta

DEFAULT_STATE = {
    "platforms": {
        "reddit": {"type": "social_feed", "description": "Subreddits for topic discussion and content sharing", "active": True, "rate_limit": 30},
        "x": {"type": "microblog", "description": "X (Twitter) for real-time topic engagement", "active": True, "rate_limit": 50},
        "linkedin": {"type": "professional", "description": "LinkedIn for professional content sharing", "active": True, "rate_limit": 20},
        "discord": {"type": "community", "description": "Discord servers for community discussions", "active": True, "rate_limit": 100},
    },
    "email_accounts": {
        "work": {"address": "work@example.com", "type": "enterprise", "active": True, "unread_count": 0},
        "news": {"address": "news@example.com", "type": "newsletter", "active": True, "unread_count": 0},
        "monitoring": {"address": "monitor@example.com", "type": "alert", "active": True, "unread_count": 0},
    },
    "email_pool": [],
    "briefs": [],
    "posts": [],
    "responses": [],
    "workflow_log": [],
    "email_counter": 1,
    "brief_counter": 1,
    "post_counter": 1,
    "response_counter": 1,
}

VALID_EMAIL_TYPES = ("work_collab", "newsletter", "alert", "promotion", "discussion", "question")
VALID_BRIEF_TYPES = ("insight", "news_update", "question", "opportunity", "alert")
VALID_POST_TYPES = ("original", "curated", "question", "discussion", "announcement")
VALID_RESPONSE_TYPES = ("comment", "reply", "clarification", "support", "correction")
VALID_PLATFORMS = ("reddit", "x", "linkedin", "discord")
VALID_OUTPUT_FORMATS = ("markdown", "bullet", "json", "social", "email")


class CollaborativeBriefingEnv:
    """
    A collaborative office and email automation environment for discovering briefs
    from emails and publishing/responding on social platforms.
    
    This class models a unified pipeline: email ingestion → brief extraction → 
    platform posting/engagement. Agents can configure email accounts, ingest emails,
    extract actionable briefs from email content, publish to social platforms, 
    and respond to platform discussions.

    Attributes:
        platforms (Dict): Registry of available social platforms with metadata.
        email_accounts (Dict): Configured email accounts for monitoring.
        email_pool (List[Dict]): All ingested emails with metadata.
        briefs (List[Dict]): Extracted briefs from email analysis.
        posts (List[Dict]): Published posts on social platforms.
        responses (List[Dict]): Responses to platform discussions.
        workflow_log (List[Dict]): Audit log of all workflow operations.
        email_counter (int): Auto-incrementing email ID counter.
        brief_counter (int): Auto-incrementing brief ID counter.
        post_counter (int): Auto-incrementing post ID counter.
        response_counter (int): Auto-incrementing response ID counter.
    """

    def __init__(self):
        self.platforms: Dict[str, Dict[str, Any]]
        self.email_accounts: Dict[str, Dict[str, Any]]
        self.email_pool: List[Dict[str, Any]]
        self.briefs: List[Dict[str, Any]]
        self.posts: List[Dict[str, Any]]
        self.responses: List[Dict[str, Any]]
        self.workflow_log: List[Dict[str, Any]]
        self.email_counter: int
        self.brief_counter: int
        self.post_counter: int
        self.response_counter: int
        self._api_description = (
            "This tool provides collaborative briefing automation from email content extraction "
            "to social platform engagement, enabling workflow discovery and topic propagation."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load initial state from scenario dictionary.

        Args:
            scenario (dict): Scenario configuration with state variables.
            long_context (bool): Whether to include extended context (unused in baseline).
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.platforms = scenario.get("platforms", DEFAULT_STATE_COPY["platforms"])
        self.email_accounts = scenario.get("email_accounts", DEFAULT_STATE_COPY["email_accounts"])
        self.email_pool = scenario.get("email_pool", DEFAULT_STATE_COPY["email_pool"])
        self.briefs = scenario.get("briefs", DEFAULT_STATE_COPY["briefs"])
        self.posts = scenario.get("posts", DEFAULT_STATE_COPY["posts"])
        self.responses = scenario.get("responses", DEFAULT_STATE_COPY["responses"])
        self.workflow_log = scenario.get("workflow_log", DEFAULT_STATE_COPY["workflow_log"])
        self.email_counter = scenario.get("email_counter", DEFAULT_STATE_COPY["email_counter"])
        self.brief_counter = scenario.get("brief_counter", DEFAULT_STATE_COPY["brief_counter"])
        self.post_counter = scenario.get("post_counter", DEFAULT_STATE_COPY["post_counter"])
        self.response_counter = scenario.get("response_counter", DEFAULT_STATE_COPY["response_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including platforms, email accounts,
                  email pool, briefs, posts, responses, workflow log, and counters.
        """
        return {
            "platforms": self.platforms,
            "email_accounts": self.email_accounts,
            "email_pool": self.email_pool,
            "briefs": self.briefs,
            "posts": self.posts,
            "responses": self.responses,
            "workflow_log": self.workflow_log,
            "email_counter": self.email_counter,
            "brief_counter": self.brief_counter,
            "post_counter": self.post_counter,
            "response_counter": self.response_counter,
        }

    # ── Platform & Account Management ────────────────────────────────────

    def add_platform(self, name: str, platform_type: str, rate_limit: int = 30) -> Dict[str, Any]:
        """
        Register a new social platform for content distribution.

        Args:
            name (str): Unique platform identifier (e.g., 'reddit', 'x').
            platform_type (str): Platform category ('social_feed', 'microblog', etc.).
            rate_limit (int): Platform-specific rate limit per hour. Defaults to 30.

        Returns:
            Dict: The registered platform entry or error information.
        """
        if name in self.platforms:
            return {"error": f"Platform '{name}' already exists."}
        
        self.platforms[name] = {
            "type": platform_type,
            "description": "",
            "active": True,
            "rate_limit": rate_limit
        }
        self._log("platform_added", {"name": name, "platform_type": platform_type, "rate_limit": rate_limit})
        return {"platform": {"name": name, **self.platforms[name]}}

    def add_email_account(self, name: str, address: str, account_type: str) -> Dict[str, Any]:
        """
        Register a new email account for monitoring.

        Args:
            name (str): Unique account identifier.
            address (str): Email address.
            account_type (str): Account type ('enterprise', 'newsletter', 'alert').

        Returns:
            Dict: The registered email account or error information.
        """
        if name in self.email_accounts:
            return {"error": f"Email account '{name}' already exists."}
        
        self.email_accounts[name] = {
            "address": address,
            "type": account_type,
            "active": True,
            "unread_count": 0
        }
        self._log("email_account_added", {"name": name, "address": address, "type": account_type})
        return {"email_account": {"name": name, **self.email_accounts[name]}}

    def list_platforms(self, platform_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List registered social platforms, optionally filtered by type.

        Args:
            platform_type (str): [Optional] Filter by platform type.

        Returns:
            Dict: List of matching platform entries.
        """
        result = []
        for name, meta in self.platforms.items():
            if platform_type and meta["type"] != platform_type:
                continue
            result.append({
                "name": name,
                "type": meta["type"],
                "active": meta["active"],
                "rate_limit": meta["rate_limit"]
            })
        return {"platforms": result}

    # ── Email Ingestion ──────────────────────────────────────────────────

    def ingest_emails(self, account: str, count: int = 10, 
                     email_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest emails from a configured account into the processing pool.

        Simulates fetching emails from an email server with various content types.

        Args:
            account (str): Email account identifier (must be registered).
            count (int): Number of emails to ingest. Defaults to 10.
            email_type (str): [Optional] Filter by email type.

        Returns:
            Dict: Information about ingested emails and their IDs.
        """
        if account not in self.email_accounts:
            return {"error": f"Email account '{account}' not found. Register it first with add_email_account."}
        
        if email_type and email_type not in VALID_EMAIL_TYPES:
            return {"error": f"Invalid email_type '{email_type}'. Must be one of: {', '.join(VALID_EMAIL_TYPES)}"}
        
        ingested_ids = []
        for i in range(min(count, 50)):  # Cap at 50 emails per ingestion
            email_id = self.email_counter
            self.email_counter += 1
            
            # Simulate email content based on account type
            email_content = self._generate_email_content(account, email_type)
            
            email = {
                "email_id": email_id,
                "account": account,
                "from_address": email_content["from"],
                "subject": email_content["subject"],
                "body": email_content["body"],
                "email_type": email_content["type"],
                "timestamp": f"{(datetime.now() - timedelta(hours=i)).isoformat()}Z",
                "priority": email_content["priority"],
                "brief_relevance": email_content["brief_relevance"],
                "processed": False,
                "brief_id": None
            }
            self.email_pool.append(email)
            ingested_ids.append(email_id)
        
        # Update unread count
        self.email_accounts[account]["unread_count"] += len(ingested_ids)
        
        self._log("emails_ingested", {
            "account": account,
            "count": len(ingested_ids),
            "email_ids": ingested_ids
        })
        
        return {
            "success": True,
            "account": account,
            "ingested_count": len(ingested_ids),
            "email_ids": ingested_ids,
            "unread_count": self.email_accounts[account]["unread_count"]
        }

    def list_emails(self, account: Optional[str] = None, 
                   processed: Optional[bool] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List emails in the pool, optionally filtered by account or processing status.

        Args:
            account (str): [Optional] Filter by email account.
            processed (bool): [Optional] Filter by processed status.

        Returns:
            Dict: List of email summaries matching the filters.
        """
        filtered = self.email_pool
        
        if account:
            filtered = [e for e in filtered if e["account"] == account]
        
        if processed is not None:
            filtered = [e for e in filtered if e["processed"] == processed]
        
        summaries = [{
            "email_id": e["email_id"],
            "account": e["account"],
            "subject": e["subject"],
            "email_type": e["email_type"],
            "priority": e["priority"],
            "brief_relevance": e["brief_relevance"],
            "processed": e["processed"],
            "brief_id": e["brief_id"]
        } for e in filtered]
        
        return {"emails": summaries}

    # ── Brief Extraction ─────────────────────────────────────────────────

    def extract_briefs(self, email_ids: List[int], 
                      extraction_method: str = "auto") -> Dict[str, Any]:
        """
        Extract actionable briefs from ingested emails.

        Analyzes email content to identify key insights, news updates, or opportunities
        worth sharing on social platforms.

        Args:
            email_ids (List[int]): List of email IDs to analyze.
            extraction_method (str): Extraction approach - 'auto', 'concise', 'detailed'.

        Returns:
            Dict: Information about extracted briefs.
        """
        if not email_ids:
            return {"error": "At least one email ID is required."}
        
        extracted_briefs = []
        processed_emails = []
        
        for email_id in email_ids:
            email = self._find_email(email_id)
            if not email:
                return {"error": f"Email ID {email_id} not found."}
            
            if email["processed"]:
                continue  # Skip already processed emails
            
            # Extract brief from email content
            brief = self._extract_brief_from_email(email, extraction_method)
            if brief:
                brief_id = self.brief_counter
                self.brief_counter += 1
                
                brief_data = {
                    "brief_id": brief_id,
                    "source_email": email_id,
                    "title": brief["title"],
                    "content": brief["content"],
                    "brief_type": brief["type"],
                    "platform_relevance": brief["platform_relevance"],
                    "actionability": brief["actionability"],
                    "extracted_at": datetime.now().isoformat() + "Z",
                    "published": False,
                    "post_ids": []
                }
                
                self.briefs.append(brief_data)
                extracted_briefs.append(brief_id)
                
                # Mark email as processed
                email["processed"] = True
                email["brief_id"] = brief_id
                processed_emails.append(email_id)
        
        self._log("briefs_extracted", {
            "email_ids": processed_emails,
            "brief_ids": extracted_briefs,
            "method": extraction_method
        })
        
        return {
            "success": True,
            "extracted_count": len(extracted_briefs),
            "brief_ids": extracted_briefs,
            "processed_emails": processed_emails
        }

    def list_briefs(self, published: Optional[bool] = None,
                   brief_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List extracted briefs, optionally filtered by publication status or type.

        Args:
            published (bool): [Optional] Filter by publication status.
            brief_type (str): [Optional] Filter by brief type.

        Returns:
            Dict: List of brief summaries matching the filters.
        """
        filtered = self.briefs
        
        if published is not None:
            filtered = [b for b in filtered if b["published"] == published]
        
        if brief_type:
            filtered = [b for b in filtered if b["brief_type"] == brief_type]
        
        summaries = [{
            "brief_id": b["brief_id"],
            "source_email": b["source_email"],
            "title": b["title"],
            "brief_type": b["brief_type"],
            "platform_relevance": b["platform_relevance"],
            "actionability": b["actionability"],
            "published": b["published"],
            "post_count": len(b["post_ids"])
        } for b in filtered]
        
        return {"briefs": summaries}

    # ── Platform Publishing ──────────────────────────────────────────────

    def publish_brief(self, brief_id: int, platform: str,
                     audience: Optional[str] = "general",
                     tone: str = "professional") -> Dict[str, Any]:
        """
        Publish a brief to a social platform.

        Transforms a brief into platform-appropriate content and publishes it
        to the specified social media platform.

        Args:
            brief_id (int): Brief ID to publish.
            platform (str): Target platform identifier.
            audience (str): Target audience - 'general', 'technical', 'business'.
            tone (str): Content tone - 'professional', 'casual', 'urgent'.

        Returns:
            Dict: Information about the published post.
        """
        if platform not in self.platforms:
            return {"error": f"Platform '{platform}' not found. Register it first with add_platform."}
        
        if not self.platforms[platform]["active"]:
            return {"error": f"Platform '{platform}' is not active."}
        
        brief = self._find_brief(brief_id)
        if not brief:
            return {"error": f"Brief ID {brief_id} not found."}
        
        if brief["published"]:
            return {"error": f"Brief {brief_id} is already published."}
        
        # Check rate limiting
        recent_posts = [p for p in self.posts 
                       if p["platform"] == platform 
                       and p.get("timestamp", "").startswith(datetime.now().strftime("%Y-%m-%d"))]
        
        if len(recent_posts) >= self.platforms[platform]["rate_limit"]:
            return {"error": f"Rate limit exceeded for platform '{platform}'. Try again later."}
        
        # Create platform-specific content
        post_content = self._create_platform_content(brief, platform, audience, tone)
        
        post_id = self.post_counter
        self.post_counter += 1
        
        post = {
            "post_id": post_id,
            "brief_id": brief_id,
            "platform": platform,
            "title": post_content["title"],
            "content": post_content["content"],
            "hashtags": post_content["hashtags"],
            "audience": audience,
            "tone": tone,
            "timestamp": datetime.now().isoformat() + "Z",
            "engagement_score": 0,
            "responses": []
        }
        
        self.posts.append(post)
        
        # Update brief status
        brief["published"] = True
        brief["post_ids"].append(post_id)
        
        self._log("brief_published", {
            "brief_id": brief_id,
            "post_id": post_id,
            "platform": platform,
            "audience": audience
        })
        
        return {
            "success": True,
            "post_id": post_id,
            "platform": platform,
            "title": post["title"],
            "content_preview": post["content"][:100] + "..." if len(post["content"]) > 100 else post["content"]
        }

    def scan_platform(self, platform: str, topic: Optional[str] = None,
                     limit: int = 20) -> Dict[str, Any]:
        """
        Scan a social platform for relevant discussions.

        Simulates scanning platform content for topics matching briefs or
        opportunities for engagement.

        Args:
            platform (str): Platform to scan.
            topic (str): [Optional] Topic filter.
            limit (int): Maximum results to return. Defaults to 20.

        Returns:
            Dict: Scan results with discussions for potential engagement.
        """
        if platform not in self.platforms:
            return {"error": f"Platform '{platform}' not found."}
        
        if not self.platforms[platform]["active"]:
            return {"error": f"Platform '{platform}' is not active."}
        
        # Simulate platform scanning
        discussions = self._simulate_platform_scan(platform, topic, limit)
        
        self._log("platform_scanned", {
            "platform": platform,
            "topic": topic,
            "discussions_found": len(discussions)
        })
        
        return {
            "scan_result": {
                "platform": platform,
                "timestamp": datetime.now().isoformat() + "Z",
                "discussions": discussions,
                "total_found": len(discussions)
            }
        }

    # ── Engagement & Response ───────────────────────────────────────────

    def create_response(self, post_id: int, response_type: str,
                       content: str) -> Dict[str, Any]:
        """
        Create a response to an existing platform post/discussion.

        Args:
            post_id (int): Target post ID to respond to.
            response_type (str): Type of response - 'comment', 'reply', etc.
            content (str): Response content/text.

        Returns:
            Dict: Information about the created response.
        """
        if response_type not in VALID_RESPONSE_TYPES:
            return {"error": f"Invalid response_type '{response_type}'. Must be one of: {', '.join(VALID_RESPONSE_TYPES)}"}
        
        post = self._find_post(post_id)
        if not post:
            return {"error": f"Post ID {post_id} not found."}
        
        # Check platform rate limiting for responses
        platform = post["platform"]
        recent_responses = [r for r in self.responses 
                           if r["platform"] == platform 
                           and r.get("timestamp", "").startswith(datetime.now().strftime("%Y-%m-%d"))]
        
        if len(recent_responses) >= self.platforms[platform]["rate_limit"] * 2:
            return {"error": f"Response rate limit exceeded for platform '{platform}'. Try again later."}
        
        response_id = self.response_counter
        self.response_counter += 1
        
        response = {
            "response_id": response_id,
            "post_id": post_id,
            "platform": platform,
            "response_type": response_type,
            "content": content,
            "timestamp": datetime.now().isoformat() + "Z",
            "upvotes": 0,
            "replies": []
        }
        
        self.responses.append(response)
        
        # Link response to post
        post["responses"].append(response_id)
        post["engagement_score"] += 1  # Simple engagement metric
        
        self._log("response_created", {
            "response_id": response_id,
            "post_id": post_id,
            "platform": platform,
            "response_type": response_type
        })
        
        return {
            "success": True,
            "response_id": response_id,
            "post_id": post_id,
            "platform": platform,
            "engagement_increase": 1
        }

    def analyze_engagement(self, time_window: str = "24h") -> Dict[str, Any]:
        """
        Analyze engagement metrics across platforms.

        Args:
            time_window (str): Time window for analysis - '1h', '24h', '7d', '30d'.

        Returns:
            Dict: Engagement analysis results.
        """
        # Simulate engagement analysis
        analysis = self._simulate_engagement_analysis(time_window)
        
        self._log("engagement_analyzed", {
            "time_window": time_window,
            "platforms_analyzed": list(self.platforms.keys())
        })
        
        return {"engagement_analysis": analysis}

    # ── Output Generation ───────────────────────────────────────────────

    def generate_report(self, report_type: str = "daily",
                       output_format: str = "markdown") -> Dict[str, Any]:
        """
        Generate a workflow report.

        Args:
            report_type (str): Report type - 'daily', 'weekly', 'performance'.
            output_format (str): Output format - 'markdown', 'bullet', 'json', etc.

        Returns:
            Dict: Generated report content.
        """
        if output_format not in VALID_OUTPUT_FORMATS:
            return {"error": f"Invalid output_format '{output_format}'. Must be one of: {', '.join(VALID_OUTPUT_FORMATS)}"}
        
        # Generate report content
        report_content = self._generate_report_content(report_type, output_format)
        
        self._log("report_generated", {
            "report_type": report_type,
            "format": output_format
        })
        
        return {
            "report": {
                "type": report_type,
                "format": output_format,
                "content": report_content,
                "generated_at": datetime.now().isoformat() + "Z"
            }
        }

    # ── Helper Methods ──────────────────────────────────────────────────

    def _find_email(self, email_id: int) -> Optional[Dict[str, Any]]:
        """Find an email by ID. Returns None if not found."""
        for e in self.email_pool:
            if e["email_id"] == email_id:
                return e
        return None

    def _find_brief(self, brief_id: int) -> Optional[Dict[str, Any]]:
        """Find a brief by ID. Returns None if not found."""
        for b in self.briefs:
            if b["brief_id"] == brief_id:
                return b
        return None

    def _find_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Find a post by ID. Returns None if not found."""
        for p in self.posts:
            if p["post_id"] == post_id:
                return p
        return None

    def _log(self, event: str, detail: Dict) -> None:
        """Append an entry to the workflow audit log."""
        self.workflow_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat() + "Z"
        })

    def _generate_email_content(self, account: str, email_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate simulated email content based on account and type."""
        account_meta = self.email_accounts[account]
        
        # Determine email type if not specified
        if not email_type:
            email_type = random.choice(VALID_EMAIL_TYPES)
        
        # Email templates based on type
        templates = {
            "work_collab": {
                "from": f"colleague_{random.randint(1, 10)}@company.com",
                "subject": f"Project update: {random.choice(['Q2 Planning', 'Product Launch', 'Team Sync'])}",
                "body": f"""{random.choice(['Hi team,', 'Hello,', 'All,'])}
                
We need to discuss the {random.choice(['upcoming deadline', 'budget review', 'client feedback'])}.
Key points:
- {random.choice(['Market analysis shows growth potential', 'User feedback has been positive', 'Technical constraints identified'])}
- {random.choice(['Resources need reallocation', 'Timeline adjustment required', 'Additional stakeholders to involve'])}

{random.choice(['Please review attachments.', 'Let me know your availability.', 'Looking forward to your input.'])}

Best,
{random.choice(['Alex', 'Jamie', 'Taylor'])}""",
                "priority": random.choices([1, 2, 3], weights=[0.2, 0.3, 0.5])[0],
                "brief_relevance": round(random.uniform(0.6, 0.9), 2)
            },
            "newsletter": {
                "from": f"news@{random.choice(['techbrief.com', 'industrywatch.org', 'trends.io'])}",
                "subject": f"{random.choice(['Weekly Digest', 'Industry Insights', 'Trend Report'])}: {random.choice(['AI Developments', 'Market Shifts', 'Innovation Spotlight'])}",
                "body": f"""This week in {random.choice(['technology', 'business', 'innovation'])}:

📈 {random.choice(['New funding rounds announced', 'Market trends emerging', 'Regulatory changes impacting'])}
🤖 {random.choice(['AI tools gaining traction', 'Automation solutions scaling', 'ML models improving'])}
💡 {random.choice(['Startup spotlight: innovative approaches', 'Research breakthrough: new findings', 'Expert opinion: industry perspective'])}

Read more: {random.choice(['full article', 'detailed analysis', 'complete report'])}""",
                "priority": random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0],
                "brief_relevance": round(random.uniform(0.5, 0.85), 2)
            },
            "alert": {
                "from": "alerts@monitoring.service",
                "subject": f"ALERT: {random.choice(['Keyword trend detected', 'Competitor activity', 'Security notice', 'Service outage'])}",
                "body": f"""🚨 {random.choice(['Important notification', 'Priority alert', 'Immediate attention required'])}:

{random.choice(['Trending topic detected on social media', 'Competitor announcement made', 'System vulnerability identified', 'Service disruption reported'])}

Details:
- Severity: {random.choice(['High', 'Medium', 'Low'])}
- Impact: {random.choice(['Brand reputation', 'Service availability', 'Competitive position'])}
- Recommended action: {random.choice(['Monitor closely', 'Prepare statement', 'Investigate further', 'Take immediate action'])}

Timestamp: {datetime.now().isoformat()}""",
                "priority": random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0],
                "brief_relevance": round(random.uniform(0.7, 0.95), 2)
            }
        }
        
        # Use alert template for alert accounts, otherwise random
        if account_meta["type"] == "alert":
            template = templates["alert"]
        else:
            template = templates.get(email_type, templates["work_collab"])
        
        return {
            "from": template["from"],
            "subject": template["subject"],
            "body": template["body"],
            "type": email_type,
            "priority": template["priority"],
            "brief_relevance": template["brief_relevance"]
        }

    def _extract_brief_from_email(self, email: Dict[str, Any], 
                                 method: str) -> Optional[Dict[str, Any]]:
        """Extract a brief from email content."""
        # Simple keyword-based extraction simulation
        keywords = {
            "insight": ["report", "analysis", "finding", "discovery", "data shows"],
            "news_update": ["announced", "released", "update", "new", "launch"],
            "opportunity": ["opportunity", "potential", "growth", "investment", "partnership"],
            "question": ["question", "feedback", "input", "opinion", "perspective"],
            "alert": ["alert", "urgent", "important", "critical", "immediate"]
        }
        
        content = f"{email['subject']} {email['body']}".lower()
        brief_type = "insight"  # Default
        
        for btype, bkeywords in keywords.items():
            if any(keyword in content for keyword in bkeywords):
                brief_type = btype
                break
        
        # Generate brief content based on email
        brief_templates = {
            "insight": {
                "title": f"Insight: {email['subject'][:50]}",
                "content": f"Key insight extracted from email discussion: {email['body'][:200]}...",
                "actionability": round(random.uniform(0.6, 0.9), 2)
            },
            "news_update": {
                "title": f"Update: {email['subject'][:50]}",
                "content": f"Latest development worth sharing: {email['body'][:200]}...",
                "actionability": round(random.uniform(0.7, 0.95), 2)
            },
            "opportunity": {
                "title": f"Opportunity: {email['subject'][:50]}",
                "content": f"Identified opportunity for engagement: {email['body'][:200]}...",
                "actionability": round(random.uniform(0.8, 1.0), 2)
            }
        }
        
        template = brief_templates.get(brief_type, brief_templates["insight"])
        
        # Determine platform relevance
        platform_relevance = {}
        for platform in self.platforms:
            relevance = random.uniform(0.3, 0.95)
            if "reddit" in platform:
                relevance *= random.uniform(1.0, 1.3)  # Boost for certain platforms
            platform_relevance[platform] = round(relevance, 2)
        
        return {
            "title": template["title"],
            "content": template["content"],
            "type": brief_type,
            "actionability": template["actionability"],
            "platform_relevance": platform_relevance
        }

    def _create_platform_content(self, brief: Dict[str, Any], platform: str,
                                audience: str, tone: str) -> Dict[str, Any]:
        """Create platform-specific content from a brief."""
        platform_templates = {
            "reddit": {
                "title": f"{brief['title']} - Thoughts?",
                "prefix": random.choice(["Interesting finding", "Wanted to share", "Came across this"]),
                "hashtags": []
            },
            "x": {
                "title": "",
                "prefix": random.choice(["Sharing insights", "Update", "Interesting"]),
                "hashtags": ["#brief", "#insights", f"#{brief['brief_type']}"]
            },
            "linkedin": {
                "title": brief['title'].replace("Insight:", "Professional Insight:"),
                "prefix": random.choice(["Professional perspective", "Industry insight", "Business update"]),
                "hashtags": ["#business", "#professional", "#industry"]
            }
        }
        
        template = platform_templates.get(platform, platform_templates["x"])
        
        # Adjust tone
        tone_modifiers = {
            "professional": ["", "Analysis:", "Key finding:"],
            "casual": ["Hey everyone,", "Check this out:", "Interesting:"],
            "urgent": ["Important:", "Attention:", "Update required:"]
        }
        
        prefix = random.choice(tone_modifiers.get(tone, [""]))
        if prefix:
            prefix += " "
        
        content = f"{prefix}{template['prefix']}: {brief['content']}"
        
        # Truncate for platform constraints
        if platform == "x" and len(content) > 280:
            content = content[:275] + "..."
        
        return {
            "title": template["title"],
            "content": content,
            "hashtags": template["hashtags"]
        }

    def _simulate_platform_scan(self, platform: str, topic: Optional[str],
                               limit: int) -> List[Dict[str, Any]]:
        """Simulate scanning a platform for relevant discussions."""
        discussions = []
        
        for i in range(min(limit, 20)):
            discussion = {
                "discussion_id": f"{platform}_{random.randint(1000, 9999)}",
                "title": f"Discussion about {topic or random.choice(['AI', 'business', 'tech', 'innovation'])}",
                "content": f"User posted: '{random.choice(['Looking for opinions', 'Has anyone tried', 'What are your thoughts'])} on {random.choice(['this approach', 'the new development', 'recent trends'])}'",
                "author": f"user_{random.randint(1, 100)}",
                "upvotes": random.randint(1, 1000),
                "comments": random.randint(0, 50),
                "posted_at": f"{(datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()}Z",
                "relevance": round(random.uniform(0.3, 0.95), 2)
            }
            discussions.append(discussion)
        
        # Sort by relevance
        discussions.sort(key=lambda x: x["relevance"], reverse=True)
        return discussions

    def _simulate_engagement_analysis(self, time_window: str) -> Dict[str, Any]:
        """Simulate engagement analysis."""
        # Convert time window to hours
        hours_map = {"1h": 1, "24h": 24, "7d": 168, "30d": 720}
        hours = hours_map.get(time_window, 24)
        
        analysis = {
            "time_window": time_window,
            "platforms": {},
            "total_engagement": 0,
            "most_engaging_platform": None,
            "most_engaging_brief_type": None
        }
        
        max_engagement = 0
        brief_type_engagement = {}
        
        for platform in self.platforms:
            platform_posts = [p for p in self.posts if p["platform"] == platform]
            platform_responses = [r for r in self.responses if r["platform"] == platform]
            
            engagement = sum(p.get("engagement_score", 0) for p in platform_posts)
            engagement += len(platform_responses)
            
            analysis["platforms"][platform] = {
                "post_count": len(platform_posts),
                "response_count": len(platform_responses),
                "total_engagement": engagement,
                "engagement_per_post": round(engagement / max(len(platform_posts), 1), 2)
            }
            
            analysis["total_engagement"] += engagement
            
            if engagement > max_engagement:
                max_engagement = engagement
                analysis["most_engaging_platform"] = platform
        
        # Analyze brief type performance
        for brief in self.briefs:
            btype = brief["brief_type"]
            brief_type_engagement[btype] = brief_type_engagement.get(btype, 0) + len(brief["post_ids"])
        
        if brief_type_engagement:
            analysis["most_engaging_brief_type"] = max(brief_type_engagement.items(), key=lambda x: x[1])[0]
        
        return analysis

    def _generate_report_content(self, report_type: str, 
                                output_format: str) -> str:
        """Generate report content in requested format."""
        if output_format == "json":
            return json.dumps({
                "report_type": report_type,
                "timestamp": datetime.now().isoformat() + "Z",
                "stats": {
                    "emails_processed": len([e for e in self.email_pool if e["processed"]]),
                    "briefs_extracted": len(self.briefs),
                    "posts_published": len(self.posts),
                    "responses_created": len(self.responses),
                    "active_platforms": len([p for p in self.platforms.values() if p["active"]])
                }
            }, indent=2)
        
        elif output_format == "bullet":
            lines = [
                f"# {report_type.title()} Workflow Report",
                f"Generated: {datetime.now().isoformat()}Z",
                "",
                "## Summary",
                f"- Emails processed: {len([e for e in self.email_pool if e['processed']])}",
                f"- Briefs extracted: {len(self.briefs)}",
                f"- Posts published: {len(self.posts)}",
                f"- Responses created: {len(self.responses)}",
                "",
                "## Platform Activity"
            ]
            
            for platform, meta in self.platforms.items():
                platform_posts = len([p for p in self.posts if p["platform"] == platform])
                platform_responses = len([r for r in self.responses if r["platform"] == platform])
                lines.append(f"- {platform}: {platform_posts} posts, {platform_responses} responses")
            
            return "\n".join(lines)
        
        else:  # markdown default
            lines = [
                f"# {report_type.title()} Collaboration Briefing Report",
                "",
                f"**Report Period:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "",
                "## Overview",
                "",
                f"This report summarizes workflow activities for the {report_type} period.",
                "",
                "## Key Metrics",
                "",
                f"- **Total Emails Processed:** {len([e for e in self.email_pool if e['processed']])}",
                f"- **Briefs Extracted:** {len(self.briefs)}",
                f"- **Social Posts Published:** {len(self.posts)}",
                f"- **Platform Responses:** {len(self.responses)}",
                "",
                "## Platform Breakdown",
                ""
            ]
            
            for platform, meta in self.platforms.items():
                platform_posts = len([p for p in self.posts if p["platform"] == platform])
                platform_responses = len([r for r in self.responses if r["platform"] == platform])
                
                lines.append(f"### {platform.upper()}")
                lines.append(f"- Status: {'Active' if meta['active'] else 'Inactive'}")
                lines.append(f"- Posts: {platform_posts}")
                lines.append(f"- Responses: {platform_responses}")
                lines.append(f"- Rate Limit: {meta['rate_limit']}/hour")
                lines.append("")
            
            lines.append("---")
            lines.append("*Report generated automatically by Collaborative Briefing System*")
            
            return "\n".join(lines)
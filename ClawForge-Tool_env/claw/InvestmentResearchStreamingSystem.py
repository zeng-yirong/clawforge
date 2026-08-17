from copy import deepcopy
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import hashlib

DEFAULT_STATE = {
    "data_streams": [],
    "investor_subscriptions": [],
    "brief_history": {},
    "cross_validation_queue": [],
    "stream_counter": 1,
    "subscription_counter": 1,
    "brief_counter": 1,
    "validation_counter": 1,
    "company_registry": {},
}

VALID_DATA_TYPES = ("price", "financial", "news", "video")
VALID_BRIEF_FORMATS = ("summary", "detailed", "executive", "technical")
VALID_ALERT_LEVELS = ("info", "warning", "critical")
VALID_COMPANY_SECTORS = ("technology", "healthcare", "finance", "energy", "consumer", "industrial", "materials", "utilities")


class InvestmentResearchStreamingEnv:
    """
    A real-time cross-validation streaming environment for investment research.
    
    This environment models a multi-dimensional investment research system that 
    continuously ingests financial data streams (stock prices, financial reports, 
    news articles, executive videos) and generates comprehensive investment briefs 
    through cross-validation algorithms. Agents subscribe to specific data patterns 
    and receive asynchronously pushed investment briefs when convergence criteria 
    are met across different data dimensions.
    
    Attributes:
        data_streams (List[Dict]): Defined financial data streams with schemas.
        investor_subscriptions (List[Dict]): Active subscriptions for investment briefs.
        brief_history (Dict[str, List[Dict]]): Generated brief history keyed by brief_id.
        cross_validation_queue (List[Dict]): Pending cross-validation tasks.
        stream_counter (int): Auto-incrementing stream ID counter.
        subscription_counter (int): Auto-incrementing subscription ID counter.
        brief_counter (int): Auto-incrementing brief ID counter.
        validation_counter (int): Auto-incrementing validation task counter.
        company_registry (Dict): Registered company information.
    """

    def __init__(self):
        self.data_streams: List[Dict[str, Any]]
        self.investor_subscriptions: List[Dict[str, Any]]
        self.brief_history: Dict[str, List[Dict[str, Any]]]
        self.cross_validation_queue: List[Dict[str, Any]]
        self.stream_counter: int
        self.subscription_counter: int
        self.brief_counter: int
        self.validation_counter: int
        self.company_registry: Dict[str, Any]
        self._api_description = (
            "This tool manages real-time investment research data streams with cross-validation semantics. "
            "It continuously ingests multi-dimensional financial data (prices, financials, news, videos), "
            "performs algorithmic cross-validation, and asynchronously pushes comprehensive investment briefs "
            "to subscribers when convergence patterns are detected across data dimensions."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.data_streams = scenario.get("data_streams", DEFAULT_STATE_COPY["data_streams"])
        self.investor_subscriptions = scenario.get("investor_subscriptions", DEFAULT_STATE_COPY["investor_subscriptions"])
        self.brief_history = scenario.get("brief_history", DEFAULT_STATE_COPY["brief_history"])
        self.cross_validation_queue = scenario.get("cross_validation_queue", DEFAULT_STATE_COPY["cross_validation_queue"])
        self.stream_counter = scenario.get("stream_counter", DEFAULT_STATE_COPY["stream_counter"])
        self.subscription_counter = scenario.get("subscription_counter", DEFAULT_STATE_COPY["subscription_counter"])
        self.brief_counter = scenario.get("brief_counter", DEFAULT_STATE_COPY["brief_counter"])
        self.validation_counter = scenario.get("validation_counter", DEFAULT_STATE_COPY["validation_counter"])
        self.company_registry = scenario.get("company_registry", DEFAULT_STATE_COPY["company_registry"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the investment research environment.

        Returns:
            dict: All environment state variables including data streams,
                  subscriptions, brief history, cross-validation queue,
                  counters, and company registry.
        """
        return {
            "data_streams": self.data_streams,
            "investor_subscriptions": self.investor_subscriptions,
            "brief_history": self.brief_history,
            "cross_validation_queue": self.cross_validation_queue,
            "stream_counter": self.stream_counter,
            "subscription_counter": self.subscription_counter,
            "brief_counter": self.brief_counter,
            "validation_counter": self.validation_counter,
            "company_registry": self.company_registry,
        }

    # ── Company Registration ──────────────────────────────────────────────

    def register_company(
        self,
        symbol: str,
        name: str,
        sector: str,
        market_cap: float,
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Register a company in the investment research system.

        Args:
            symbol (str): Stock symbol/ticker (e.g., 'AAPL', 'GOOGL').
            name (str): Full company name.
            sector (str): Industry sector. Must be one of: technology, healthcare, 
                         finance, energy, consumer, industrial, materials, utilities.
            market_cap (float): Market capitalization in billions USD.
            description (str): [Optional] Company description.

        Returns:
            company_id (str): Unique company identifier (symbol hash).
            company (Dict): The registered company record.
        """
        if sector not in VALID_COMPANY_SECTORS:
            return {"error": f"Invalid sector '{sector}'. Must be one of: {', '.join(VALID_COMPANY_SECTORS)}"}
        if market_cap <= 0:
            return {"error": f"Market cap must be positive. Got: {market_cap}"}
        
        company_id = hashlib.md5(symbol.encode()).hexdigest()[:8]
        
        company = {
            "company_id": company_id,
            "symbol": symbol,
            "name": name,
            "sector": sector,
            "market_cap": market_cap,
            "description": description,
            "data_streams": [],
            "brief_count": 0,
            "registered_at": datetime.now().isoformat(),
        }
        
        self.company_registry[company_id] = company
        return {"company_id": company_id, "company": company}

    def get_company_info(self, company_id: str) -> Dict[str, Any]:
        """
        Retrieve company information by ID.

        Args:
            company_id (str): Company identifier.

        Returns:
            company (Dict): Full company record including associated streams.
        """
        if company_id not in self.company_registry:
            return {"error": f"Company ID {company_id} not found."}
        
        company = self.company_registry[company_id]
        streams = [s for s in self.data_streams if s.get("company_id") == company_id]
        return {
            "company": company,
            "associated_streams": [s["stream_id"] for s in streams],
            "total_streams": len(streams),
        }

    # ── Data Stream Management ────────────────────────────────────────────

    def create_data_stream(
        self,
        company_id: str,
        data_type: str,
        frequency_minutes: int,
        schema: Dict[str, str],
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Define a new financial data stream for a registered company.

        Args:
            company_id (str): Company identifier to associate with this stream.
            data_type (str): Type of financial data. Must be one of: 'price', 
                            'financial', 'news', 'video'.
            frequency_minutes (int): Expected data arrival frequency in minutes.
            schema (Dict[str, str]): Field name → type mapping for data points
                (e.g., {'price': 'float', 'volume': 'int', 'timestamp': 'datetime'}).
            description (str): [Optional] Stream description.

        Returns:
            stream_id (int): Unique stream identifier.
            stream (Dict): The created stream record.
        """
        if company_id not in self.company_registry:
            return {"error": f"Company ID {company_id} not found. Register company first."}
        if data_type not in VALID_DATA_TYPES:
            return {"error": f"Invalid data_type '{data_type}'. Must be one of: {', '.join(VALID_DATA_TYPES)}"}
        if frequency_minutes <= 0:
            return {"error": f"Frequency must be positive. Got: {frequency_minutes}"}
        if not schema:
            return {"error": "Schema is required. Define at least one field."}
        
        stream_id = self.stream_counter
        self.stream_counter += 1
        
        stream = {
            "stream_id": stream_id,
            "company_id": company_id,
            "data_type": data_type,
            "frequency_minutes": frequency_minutes,
            "schema": schema,
            "description": description,
            "status": "active",
            "data_point_count": 0,
            "subscriber_count": 0,
            "created_at": datetime.now().isoformat(),
        }
        
        self.data_streams.append(stream)
        self.company_registry[company_id]["data_streams"].append(stream_id)
        return {"stream_id": stream_id, "stream": stream}

    def list_data_streams(
        self, 
        company_id: Optional[str] = None,
        data_type: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List financial data streams, optionally filtered by company or data type.

        Args:
            company_id (str): [Optional] Filter by company ID.
            data_type (str): [Optional] Filter by data type.

        Returns:
            streams (List[Dict]): Stream summaries with id, company, type, and counts.
        """
        streams = self.data_streams
        
        if company_id is not None:
            streams = [s for s in streams if s.get("company_id") == company_id]
        if data_type is not None:
            streams = [s for s in streams if s.get("data_type") == data_type]
        
        summaries = [{
            "stream_id": s["stream_id"],
            "company_id": s["company_id"],
            "data_type": s["data_type"],
            "frequency_minutes": s["frequency_minutes"],
            "data_point_count": s["data_point_count"],
            "subscriber_count": s["subscriber_count"],
        } for s in streams]
        return {"streams": summaries}

    def get_stream_performance(self, stream_id: int) -> Dict[str, Any]:
        """
        Get performance metrics for a specific data stream.

        Args:
            stream_id (int): Stream ID.

        Returns:
            stream (Dict): Full stream record with performance metrics.
            recent_data (List[Dict]): Recent data points (last 20).
            cross_validations (int): Number of cross-validation tasks using this stream.
        """
        stream = self._find_stream(stream_id)
        if not stream:
            return {"error": f"Stream ID {stream_id} not found."}
        
        # Count cross-validation tasks using this stream
        cv_count = sum(1 for task in self.cross_validation_queue 
                      if stream_id in task.get("stream_ids", []))
        
        # Simulate recent data (in a real system, this would come from actual data storage)
        recent_data = [
            {
                "timestamp": f"t-{i}",
                "value": 100.0 + i * 0.5,
                "confidence": 0.85 + i * 0.01
            }
            for i in range(min(20, stream["data_point_count"]))
        ]
        
        return {
            "stream": stream,
            "recent_data": recent_data,
            "cross_validations_count": cv_count,
            "health_score": min(95.0, 70.0 + stream["data_point_count"] * 0.1),
        }

    # ── Subscription Management ───────────────────────────────────────────

    def subscribe_to_briefs(
        self,
        company_ids: List[str],
        brief_format: str = "summary",
        alert_levels: List[str] = None,
        convergence_threshold: float = 0.75,
    ) -> Dict[str, Any]:
        """
        Subscribe to receive investment briefs for specific companies.

        Args:
            company_ids (List[str]): List of company IDs to monitor.
            brief_format (str): Desired brief format. Must be one of: 
                               'summary', 'detailed', 'executive', 'technical'.
            alert_levels (List[str]): [Optional] Filter by alert levels 
                                     (info, warning, critical). If empty, all levels.
            convergence_threshold (float): Minimum cross-validation confidence 
                                          threshold (0.0 to 1.0).

        Returns:
            subscription_id (int): Unique subscription identifier.
            subscription (Dict): The created subscription record.
        """
        if not company_ids:
            return {"error": "At least one company_id is required."}
        
        # Validate all companies exist
        for cid in company_ids:
            if cid not in self.company_registry:
                return {"error": f"Company ID {cid} not found."}
        
        if brief_format not in VALID_BRIEF_FORMATS:
            return {"error": f"Invalid brief_format '{brief_format}'. Must be one of: {', '.join(VALID_BRIEF_FORMATS)}"}
        
        if alert_levels:
            for level in alert_levels:
                if level not in VALID_ALERT_LEVELS:
                    return {"error": f"Invalid alert_level '{level}'. Must be one of: {', '.join(VALID_ALERT_LEVELS)}"}
        
        if not 0.0 <= convergence_threshold <= 1.0:
            return {"error": f"convergence_threshold must be between 0.0 and 1.0. Got: {convergence_threshold}"}
        
        subscription_id = self.subscription_counter
        self.subscription_counter += 1
        
        subscription = {
            "subscription_id": subscription_id,
            "company_ids": company_ids,
            "brief_format": brief_format,
            "alert_levels": alert_levels or VALID_ALERT_LEVELS.copy(),
            "convergence_threshold": convergence_threshold,
            "status": "active",
            "briefs_received": 0,
            "briefs_acknowledged": 0,
            "pending_briefs": [],
            "created_at": datetime.now().isoformat(),
        }
        
        self.investor_subscriptions.append(subscription)
        
        # Increment subscriber counts for relevant streams
        for stream in self.data_streams:
            if stream.get("company_id") in company_ids:
                stream["subscriber_count"] += 1
        
        return {"subscription_id": subscription_id, "subscription": subscription}

    def unsubscribe_from_briefs(self, subscription_id: int) -> Dict[str, str]:
        """
        Cancel an active investment brief subscription.

        Args:
            subscription_id (int): Subscription ID to cancel.

        Returns:
            status (str): Cancellation confirmation.
        """
        sub = self._find_subscription(subscription_id)
        if not sub:
            return {"error": f"Subscription ID {subscription_id} not found."}
        if sub["status"] != "active":
            return {"error": f"Subscription {subscription_id} is already {sub['status']}."}
        
        sub["status"] = "cancelled"
        
        # Decrement subscriber counts for relevant streams
        for stream in self.data_streams:
            if stream.get("company_id") in sub["company_ids"]:
                stream["subscriber_count"] = max(0, stream["subscriber_count"] - 1)
        
        return {"status": f"Subscription {subscription_id} cancelled."}

    def list_subscriptions(
        self, 
        company_id: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List active brief subscriptions, optionally filtered by company.

        Args:
            company_id (str): [Optional] Filter by company ID.

        Returns:
            subscriptions (List[Dict]): Matching subscription records.
        """
        subs = [s for s in self.investor_subscriptions if s["status"] == "active"]
        
        if company_id is not None:
            subs = [s for s in subs if company_id in s["company_ids"]]
        
        return {"subscriptions": subs}

    def update_subscription_filters(
        self,
        subscription_id: int,
        alert_levels: Optional[List[str]] = None,
        convergence_threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Update filter criteria for an existing subscription.

        Args:
            subscription_id (int): Subscription ID to update.
            alert_levels (List[str]): [Optional] New alert levels filter.
            convergence_threshold (float): [Optional] New convergence threshold.

        Returns:
            subscription (Dict): Updated subscription record.
        """
        sub = self._find_subscription(subscription_id)
        if not sub:
            return {"error": f"Subscription ID {subscription_id} not found."}
        if sub["status"] != "active":
            return {"error": f"Cannot update {sub['status']} subscription."}
        
        if alert_levels is not None:
            for level in alert_levels:
                if level not in VALID_ALERT_LEVELS:
                    return {"error": f"Invalid alert_level '{level}'. Must be one of: {', '.join(VALID_ALERT_LEVELS)}"}
            sub["alert_levels"] = alert_levels
        
        if convergence_threshold is not None:
            if not 0.0 <= convergence_threshold <= 1.0:
                return {"error": f"convergence_threshold must be between 0.0 and 1.0. Got: {convergence_threshold}"}
            sub["convergence_threshold"] = convergence_threshold
        
        return {"subscription": sub, "updated_at": datetime.now().isoformat()}

    # ── Data Ingestion and Cross-Validation ───────────────────────────────

    def ingest_data_point(
        self,
        stream_id: int,
        data_payload: Dict[str, Any],
        source_confidence: float = 0.9,
    ) -> Dict[str, Any]:
        """
        Ingests a new data point into a financial data stream.

        This triggers cross-validation checks across different data dimensions 
        (price, financial, news, video) for the associated company.

        Args:
            stream_id (int): Target stream ID.
            data_payload (Dict[str, Any]): Data point payload matching stream schema.
            source_confidence (float): Confidence score for this data source (0.0 to 1.0).

        Returns:
            data_point_id (str): Unique data point identifier.
            validation_triggered (bool): Whether cross-validation was triggered.
            streams_affected (List[int]): Other streams involved in validation.
        """
        stream = self._find_stream(stream_id)
        if not stream:
            return {"error": f"Stream ID {stream_id} not found."}
        if stream["status"] != "active":
            return {"error": f"Stream {stream_id} is {stream['status']}. Cannot ingest data."}
        
        if not 0.0 <= source_confidence <= 1.0:
            return {"error": f"source_confidence must be between 0.0 and 1.0. Got: {source_confidence}"}
        
        stream["data_point_count"] += 1
        
        # Generate data point ID
        data_point_id = f"{stream_id}-{stream['data_point_count']}"
        
        # Check if we should trigger cross-validation
        # Rule: Trigger validation every 5th data point for this stream
        validation_triggered = stream["data_point_count"] % 5 == 0
        
        streams_affected = []
        if validation_triggered:
            # Find other streams for the same company
            company_streams = [
                s["stream_id"] for s in self.data_streams 
                if s["company_id"] == stream["company_id"] and s["stream_id"] != stream_id
            ]
            
            if company_streams:
                # Create cross-validation task
                validation_id = self.validation_counter
                self.validation_counter += 1
                
                task = {
                    "validation_id": validation_id,
                    "company_id": stream["company_id"],
                    "trigger_stream_id": stream_id,
                    "stream_ids": [stream_id] + company_streams[:2],  # Limit to 3 streams
                    "status": "pending",
                    "confidence_scores": {},
                    "created_at": datetime.now().isoformat(),
                }
                
                # Simulate confidence scores for each stream
                for sid in task["stream_ids"]:
                    s = self._find_stream(sid)
                    if s:
                        base_conf = 0.7 if s["data_type"] in ["price", "financial"] else 0.6
                        conf_adjustment = min(0.3, s["data_point_count"] * 0.01)
                        task["confidence_scores"][sid] = min(0.95, base_conf + conf_adjustment)
                
                self.cross_validation_queue.append(task)
                streams_affected = company_streams[:2]
        
        return {
            "data_point_id": data_point_id,
            "validation_triggered": validation_triggered,
            "streams_affected": streams_affected,
            "current_count": stream["data_point_count"],
        }

    def process_cross_validation(
        self,
        validation_id: int,
        manual_override: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a pending cross-validation task and generate investment briefs.

        Args:
            validation_id (int): Validation task ID.
            manual_override (bool): Force processing even if confidence low.

        Returns:
            validation_result (Dict): Cross-validation results.
            briefs_generated (int): Number of investment briefs generated.
            subscribers_notified (int): Number of subscribers notified.
        """
        task = None
        for t in self.cross_validation_queue:
            if t["validation_id"] == validation_id and t["status"] == "pending":
                task = t
                break
        
        if not task:
            return {"error": f"Pending validation task {validation_id} not found."}
        
        # Calculate overall confidence
        confidences = list(task["confidence_scores"].values())
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Check if we should generate briefs
        generate_brief = manual_override or avg_confidence >= 0.65
        
        briefs_generated = 0
        subscribers_notified = 0
        
        if generate_brief:
            # Generate investment brief
            brief_id = self.brief_counter
            self.brief_counter += 1
            
            # Determine alert level based on confidence
            if avg_confidence >= 0.85:
                alert_level = "critical"
            elif avg_confidence >= 0.75:
                alert_level = "warning"
            else:
                alert_level = "info"
            
            brief = {
                "brief_id": brief_id,
                "company_id": task["company_id"],
                "validation_id": validation_id,
                "stream_ids": task["stream_ids"],
                "overall_confidence": avg_confidence,
                "alert_level": alert_level,
                "key_insights": self._generate_insights(task),
                "recommendation": self._generate_recommendation(avg_confidence),
                "generated_at": datetime.now().isoformat(),
            }
            
            # Store in history
            self.brief_history[str(brief_id)] = brief
            
            # Find matching subscriptions and push briefs
            company = self.company_registry.get(task["company_id"])
            if company:
                company["brief_count"] += 1
            
            for sub in self.investor_subscriptions:
                if (sub["status"] == "active" and 
                    task["company_id"] in sub["company_ids"] and
                    alert_level in sub["alert_levels"] and
                    avg_confidence >= sub["convergence_threshold"]):
                    
                    sub["pending_briefs"].append(brief_id)
                    sub["briefs_received"] += 1
                    subscribers_notified += 1
            
            briefs_generated = 1
        
        task["status"] = "processed"
        task["processed_at"] = datetime.now().isoformat()
        task["result_confidence"] = avg_confidence
        
        return {
            "validation_result": task,
            "briefs_generated": briefs_generated,
            "subscribers_notified": subscribers_notified,
        }

    def get_pending_validations(self) -> Dict[str, Any]:
        """
        Get all pending cross-validation tasks.

        Returns:
            pending_tasks (List[Dict]): Pending validation tasks.
            count (int): Number of pending tasks.
            avg_confidence_estimate (float): Estimated average confidence.
        """
        pending = [t for t in self.cross_validation_queue if t["status"] == "pending"]
        
        confidence_estimates = []
        for task in pending:
            confidences = list(task.get("confidence_scores", {}).values())
            if confidences:
                confidence_estimates.append(sum(confidences) / len(confidences))
        
        avg_confidence = sum(confidence_estimates) / len(confidence_estimates) if confidence_estimates else 0.0
        
        return {
            "pending_tasks": pending,
            "count": len(pending),
            "avg_confidence_estimate": round(avg_confidence, 3),
        }

    # ── Brief Management ──────────────────────────────────────────────────

    def acknowledge_brief(
        self, 
        subscription_id: int, 
        brief_id: int
    ) -> Dict[str, Any]:
        """
        Acknowledge receipt of an investment brief.

        Args:
            subscription_id (int): Subscription ID.
            brief_id (int): Brief ID to acknowledge.

        Returns:
            subscription_id (int): The subscription ID.
            brief_acknowledged (int): The acknowledged brief ID.
            pending_briefs (int): Remaining unacknowledged briefs.
        """
        sub = self._find_subscription(subscription_id)
        if not sub:
            return {"error": f"Subscription ID {subscription_id} not found."}
        if sub["status"] != "active":
            return {"error": f"Subscription {subscription_id} is {sub['status']}."}
        if brief_id not in sub["pending_briefs"]:
            return {"error": f"Brief {brief_id} is not pending for subscription {subscription_id}."}
        
        sub["pending_briefs"].remove(brief_id)
        sub["briefs_acknowledged"] += 1
        
        return {
            "subscription_id": subscription_id,
            "brief_acknowledged": brief_id,
            "pending_briefs": len(sub["pending_briefs"]),
            "acknowledgement_rate": (
                sub["briefs_acknowledged"] / sub["briefs_received"] 
                if sub["briefs_received"] > 0 else 0.0
            ),
        }

    def get_pending_briefs(self, subscription_id: int) -> Dict[str, Any]:
        """
        Get all unacknowledged investment briefs for a subscription.

        Args:
            subscription_id (int): Subscription ID.

        Returns:
            subscription_id (int): The subscription ID.
            pending_briefs (List[int]): Brief IDs awaiting acknowledgment.
            count (int): Number of pending briefs.
            brief_details (List[Dict]): Details for pending briefs.
        """
        sub = self._find_subscription(subscription_id)
        if not sub:
            return {"error": f"Subscription ID {subscription_id} not found."}
        
        brief_details = []
        for brief_id in sub["pending_briefs"]:
            brief = self.brief_history.get(str(brief_id))
            if brief:
                brief_details.append({
                    "brief_id": brief_id,
                    "alert_level": brief.get("alert_level"),
                    "confidence": brief.get("overall_confidence"),
                    "generated_at": brief.get("generated_at"),
                })
        
        return {
            "subscription_id": subscription_id,
            "pending_briefs": sub["pending_briefs"],
            "count": len(sub["pending_briefs"]),
            "brief_details": brief_details,
        }

    def get_brief_details(self, brief_id: int) -> Dict[str, Any]:
        """
        Retrieve full details of a specific investment brief.

        Args:
            brief_id (int): Brief ID.

        Returns:
            brief (Dict): The full brief record.
            subscription_reach (int): Number of subscriptions that received this brief.
        """
        brief = self.brief_history.get(str(brief_id))
        if not brief:
            return {"error": f"Brief ID {brief_id} not found."}
        
        # Count subscriptions that have this brief pending
        subscription_reach = sum(
            1 for sub in self.investor_subscriptions 
            if brief_id in sub.get("pending_briefs", [])
        )
        
        return {
            "brief": brief,
            "subscription_reach": subscription_reach,
        }

    def get_company_brief_history(
        self,
        company_id: str,
        limit: int = 20,
        alert_level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve investment brief history for a company.

        Args:
            company_id (str): Company ID.
            limit (int): Maximum number of briefs to return. Defaults to 20.
            alert_level (str): [Optional] Filter by alert level.

        Returns:
            company_id (str): The company ID.
            briefs (List[Dict]): Matching briefs, newest first.
            statistics (Dict): Brief statistics for this company.
        """
        if company_id not in self.company_registry:
            return {"error": f"Company ID {company_id} not found."}
        
        if alert_level and alert_level not in VALID_ALERT_LEVELS:
            return {"error": f"Invalid alert_level '{alert_level}'. Must be one of: {', '.join(VALID_ALERT_LEVELS)}"}
        
        # Find all briefs for this company
        company_briefs = []
        for brief_id, brief in self.brief_history.items():
            if brief.get("company_id") == company_id:
                if alert_level is None or brief.get("alert_level") == alert_level:
                    company_briefs.append({**brief, "brief_id": int(brief_id)})
        
        # Sort by generated_at timestamp (newest first)
        company_briefs.sort(key=lambda x: x.get("generated_at", ""), reverse=True)
        
        # Calculate statistics
        total_briefs = len(company_briefs)
        if total_briefs > 0:
            confidences = [b.get("overall_confidence", 0.0) for b in company_briefs]
            alert_counts = {}
            for brief in company_briefs:
                level = brief.get("alert_level", "info")
                alert_counts[level] = alert_counts.get(level, 0) + 1
        else:
            confidences = []
            alert_counts = {}
        
        return {
            "company_id": company_id,
            "briefs": company_briefs[:limit],
            "statistics": {
                "total_briefs": total_briefs,
                "avg_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
                "alert_distribution": alert_counts,
                "briefs_per_stream_type": self._calculate_briefs_per_stream_type(company_id),
            },
        }

    # ── Helper Methods ────────────────────────────────────────────────────

    def _find_stream(self, stream_id: int) -> Optional[Dict[str, Any]]:
        """Find a stream by ID. Returns None if not found."""
        for s in self.data_streams:
            if s["stream_id"] == stream_id:
                return s
        return None

    def _find_subscription(self, subscription_id: int) -> Optional[Dict[str, Any]]:
        """Find a subscription by ID. Returns None if not found."""
        for s in self.investor_subscriptions:
            if s["subscription_id"] == subscription_id:
                return s
        return None

    def _generate_insights(self, validation_task: Dict) -> List[Dict[str, Any]]:
        """Generate simulated key insights for an investment brief."""
        streams = []
        for stream_id in validation_task.get("stream_ids", []):
            stream = self._find_stream(stream_id)
            if stream:
                streams.append(stream)
        
        insights = []
        data_types_present = {s["data_type"] for s in streams if s}
        
        if "price" in data_types_present:
            insights.append({
                "dimension": "price",
                "summary": "Price momentum shows positive trend with increasing volume",
                "confidence": validation_task.get("confidence_scores", {}).get(
                    next(s["stream_id"] for s in streams if s["data_type"] == "price"), 0.7
                ),
            })
        
        if "financial" in data_types_present:
            insights.append({
                "dimension": "financial",
                "summary": "QoQ revenue growth exceeds sector average",
                "confidence": validation_task.get("confidence_scores", {}).get(
                    next(s["stream_id"] for s in streams if s["data_type"] == "financial"), 0.75
                ),
            })
        
        if "news" in data_types_present:
            insights.append({
                "dimension": "news",
                "summary": "Positive sentiment detected in recent press coverage",
                "confidence": validation_task.get("confidence_scores", {}).get(
                    next(s["stream_id"] for s in streams if s["data_type"] == "news"), 0.65
                ),
            })
        
        if "video" in data_types_present:
            insights.append({
                "dimension": "video",
                "summary": "Management tone analysis indicates confidence in outlook",
                "confidence": validation_task.get("confidence_scores", {}).get(
                    next(s["stream_id"] for s in streams if s["data_type"] == "video"), 0.6
                ),
            })
        
        return insights

    def _generate_recommendation(self, confidence: float) -> str:
        """Generate investment recommendation based on confidence score."""
        if confidence >= 0.8:
            return "STRONG BUY - High convergence across all data dimensions"
        elif confidence >= 0.7:
            return "BUY - Positive signals with good cross-validation"
        elif confidence >= 0.6:
            return "HOLD - Mixed signals, requires monitoring"
        elif confidence >= 0.5:
            return "REDUCE - Limited positive confirmation"
        else:
            return "SELL - Negative convergence across data dimensions"

    def _calculate_briefs_per_stream_type(self, company_id: str) -> Dict[str, int]:
        """Calculate how many briefs were generated per stream type for a company."""
        stream_types = {}
        
        for brief_id, brief in self.brief_history.items():
            if brief.get("company_id") == company_id:
                for stream_id in brief.get("stream_ids", []):
                    stream = self._find_stream(stream_id)
                    if stream:
                        stream_type = stream["data_type"]
                        stream_types[stream_type] = stream_types.get(stream_type, 0) + 1
        
        return stream_types

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })
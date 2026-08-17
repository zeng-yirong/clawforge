from copy import deepcopy
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

DEFAULT_STATE = {
    "research_projects": [],
    "data_sources": [],
    "validation_rules": [],
    "briefs": [],
    "brief_log": [],
    "project_counter": 1,
    "source_counter": 1,
    "rule_counter": 1,
    "brief_counter": 1,
}

VALID_SOURCE_TYPES = ("price", "financial", "video")
VALID_BRIEF_STATUSES = ("draft", "published", "archived")


class ResearchCrossValidationEnv:
    """
    A cross-validation research environment for investment analysis.
    
    This class models a research system that integrates data from multiple dimensions
    (stock prices, financial reports/news, and management video content) to generate
    comprehensive investment briefs. The system validates consistency across data
    sources and produces multi-dimensional analysis reports.
    
    Attributes:
        research_projects (List[Dict]): Research projects with configuration.
        data_sources (List[Dict]): All data sources across different types.
        validation_rules (List[Dict]): Rules for cross-validating data sources.
        briefs (List[Dict]): Generated investment briefs.
        brief_log (List[Dict]): Audit log of all research operations.
        project_counter (int): Auto-incrementing project ID counter.
        source_counter (int): Auto-incrementing source ID counter.
        rule_counter (int): Auto-incrementing rule ID counter.
        brief_counter (int): Auto-incrementing brief ID counter.
    """

    def __init__(self):
        self.research_projects: List[Dict[str, Any]]
        self.data_sources: List[Dict[str, Any]]
        self.validation_rules: List[Dict[str, Any]]
        self.briefs: List[Dict[str, Any]]
        self.brief_log: List[Dict[str, Any]]
        self.project_counter: int
        self.source_counter: int
        self.rule_counter: int
        self.brief_counter: int
        self._api_description = (
            "This tool manages investment research cross-validation by integrating "
            "stock price data, financial reports/news, and management video content "
            "to generate multi-dimensional investment briefs with consistency checks."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """Load initial state from scenario dictionary."""
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.research_projects = scenario.get("research_projects", DEFAULT_STATE_COPY["research_projects"])
        self.data_sources = scenario.get("data_sources", DEFAULT_STATE_COPY["data_sources"])
        self.validation_rules = scenario.get("validation_rules", DEFAULT_STATE_COPY["validation_rules"])
        self.briefs = scenario.get("briefs", DEFAULT_STATE_COPY["briefs"])
        self.brief_log = scenario.get("brief_log", DEFAULT_STATE_COPY["brief_log"])
        self.project_counter = scenario.get("project_counter", DEFAULT_STATE_COPY["project_counter"])
        self.source_counter = scenario.get("source_counter", DEFAULT_STATE_COPY["source_counter"])
        self.rule_counter = scenario.get("rule_counter", DEFAULT_STATE_COPY["rule_counter"])
        self.brief_counter = scenario.get("brief_counter", DEFAULT_STATE_COPY["brief_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.
        
        Returns:
            dict: All environment state variables.
        """
        return {
            "research_projects": self.research_projects,
            "data_sources": self.data_sources,
            "validation_rules": self.validation_rules,
            "briefs": self.briefs,
            "brief_log": self.brief_log,
            "project_counter": self.project_counter,
            "source_counter": self.source_counter,
            "rule_counter": self.rule_counter,
            "brief_counter": self.brief_counter,
        }

    # ── Project management ───────────────────────────────────────────────

    def create_research_project(
        self,
        name: str,
        stock_symbol: str,
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Create a new research project for a specific stock.
        
        Args:
            name (str): Project name (e.g., 'AAPL_Q4_2024_Analysis').
            stock_symbol (str): Stock ticker symbol.
            description (str): Optional project description.
            
        Returns:
            project_id (int): Unique project identifier.
            project (Dict): The created project record.
        """
        if not name.strip():
            return {"error": "Project name is required."}
        if not stock_symbol.strip():
            return {"error": "Stock symbol is required."}
            
        project_id = self.project_counter
        self.project_counter += 1
        
        project = {
            "project_id": project_id,
            "name": name,
            "stock_symbol": stock_symbol.upper(),
            "description": description,
            "price_source_count": 0,
            "financial_source_count": 0,
            "video_source_count": 0,
            "rule_count": 0,
            "brief_count": 0,
            "status": "active",
        }
        self.research_projects.append(project)
        self._log("project_created", {
            "project_id": project_id,
            "name": name,
            "stock_symbol": stock_symbol
        })
        return {"project_id": project_id, "project": project}

    def list_projects(
        self,
        status: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all research projects.
        
        Args:
            status (str): [Optional] Filter by project status ('active', 'completed').
            
        Returns:
            projects (List[Dict]): Project summaries.
        """
        projects = self.research_projects
        if status:
            projects = [p for p in projects if p["status"] == status]
            
        summaries = [{
            "project_id": p["project_id"],
            "name": p["name"],
            "stock_symbol": p["stock_symbol"],
            "price_sources": p["price_source_count"],
            "financial_sources": p["financial_source_count"],
            "video_sources": p["video_source_count"],
            "rules": p["rule_count"],
            "briefs": p["brief_count"],
        } for p in projects]
        return {"projects": summaries}

    # ── Data source management ──────────────────────────────────────────

    def add_data_source(
        self,
        project_id: int,
        source_type: str,
        content: Dict[str, Any],
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Add a data source to a research project.
        
        Args:
            project_id (int): Target project ID.
            source_type (str): Type of source - 'price', 'financial', or 'video'.
            content (Dict[str, Any]): Source content data.
            metadata (Dict[str, Any]): Optional metadata about the source.
            
        Returns:
            source_id (int): Unique source identifier.
            source (Dict): The added source record.
        """
        project = self._find_project(project_id)
        if not project:
            return {"error": f"Project ID {project_id} not found."}
        if source_type not in VALID_SOURCE_TYPES:
            return {"error": f"Invalid source_type '{source_type}'. Must be one of: {', '.join(VALID_SOURCE_TYPES)}"}
        if not content:
            return {"error": "Source content is required."}
            
        source_id = self.source_counter
        self.source_counter += 1
        
        source = {
            "source_id": source_id,
            "project_id": project_id,
            "source_type": source_type,
            "content": content,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat(),
            "status": "active",
        }
        self.data_sources.append(source)
        
        # Update project counts
        if source_type == "price":
            project["price_source_count"] += 1
        elif source_type == "financial":
            project["financial_source_count"] += 1
        elif source_type == "video":
            project["video_source_count"] += 1
            
        self._log("source_added", {
            "source_id": source_id,
            "project_id": project_id,
            "type": source_type
        })
        return {"source_id": source_id, "source": source}

    def list_data_sources(
        self,
        project_id: Optional[int] = None,
        source_type: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List data sources, optionally filtered by project or type.
        
        Args:
            project_id (int): [Optional] Filter by project ID.
            source_type (str): [Optional] Filter by source type.
            
        Returns:
            sources (List[Dict]): Matching source summaries.
        """
        if source_type and source_type not in VALID_SOURCE_TYPES:
            return {"error": f"Invalid source_type '{source_type}'."}
            
        sources = self.data_sources
        if project_id is not None:
            sources = [s for s in sources if s["project_id"] == project_id]
        if source_type:
            sources = [s for s in sources if s["source_type"] == source_type]
            
        summaries = [{
            "source_id": s["source_id"],
            "project_id": s["project_id"],
            "source_type": s["source_type"],
            "metadata": s["metadata"],
            "added_at": s["added_at"],
        } for s in sources]
        return {"sources": summaries}

    # ── Validation rule management ──────────────────────────────────────

    def add_validation_rule(
        self,
        project_id: int,
        name: str,
        rule_type: str,
        parameters: Dict[str, Any],
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Add a validation rule for cross-validating data sources.
        
        Args:
            project_id (int): Target project ID.
            name (str): Rule name (e.g., 'Revenue_Growth_Correlation').
            rule_type (str): Type of validation rule.
            parameters (Dict[str, Any]): Rule parameters and thresholds.
            description (str): Optional rule description.
            
        Returns:
            rule_id (int): Unique rule identifier.
            rule (Dict): The added rule record.
        """
        project = self._find_project(project_id)
        if not project:
            return {"error": f"Project ID {project_id} not found."}
        if not name.strip():
            return {"error": "Rule name is required."}
        if not rule_type.strip():
            return {"error": "Rule type is required."}
            
        rule_id = self.rule_counter
        self.rule_counter += 1
        
        rule = {
            "rule_id": rule_id,
            "project_id": project_id,
            "name": name,
            "rule_type": rule_type,
            "parameters": parameters,
            "description": description,
            "status": "active",
        }
        self.validation_rules.append(rule)
        project["rule_count"] += 1
        
        self._log("rule_added", {
            "rule_id": rule_id,
            "project_id": project_id,
            "name": name,
            "type": rule_type
        })
        return {"rule_id": rule_id, "rule": rule}

    def run_validation(
        self,
        project_id: int,
        include_rules: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Run validation rules on project data sources.
        
        Args:
            project_id (int): Target project ID.
            include_rules (List[int]): [Optional] Specific rule IDs to include.
            
        Returns:
            project_id (int): The project ID.
            validation_results (List[Dict]): Results of validation checks.
            issues_found (int): Number of validation issues detected.
        """
        project = self._find_project(project_id)
        if not project:
            return {"error": f"Project ID {project_id} not found."}
            
        # Get relevant sources and rules
        sources = [s for s in self.data_sources if s["project_id"] == project_id and s["status"] == "active"]
        rules = [r for r in self.validation_rules if r["project_id"] == project_id and r["status"] == "active"]
        
        if include_rules:
            rules = [r for r in rules if r["rule_id"] in include_rules]
            
        if not sources:
            return {"error": "No active data sources in this project."}
        if not rules:
            return {"error": "No active validation rules in this project."}
            
        # Run validations
        results = []
        issues_count = 0
        
        for rule in rules:
            rule_result = self._apply_validation_rule(rule, sources)
            results.append(rule_result)
            if not rule_result.get("passed", True):
                issues_count += 1
                
        self._log("validation_run", {
            "project_id": project_id,
            "rules_executed": len(rules),
            "issues_found": issues_count
        })
        
        return {
            "project_id": project_id,
            "validation_results": results,
            "issues_found": issues_count,
        }

    def _apply_validation_rule(self, rule: Dict, sources: List[Dict]) -> Dict[str, Any]:
        """Apply a single validation rule to data sources."""
        rule_type = rule["rule_type"]
        parameters = rule["parameters"]
        
        # Extract relevant sources by type
        price_sources = [s for s in sources if s["source_type"] == "price"]
        financial_sources = [s for s in sources if s["source_type"] == "financial"]
        video_sources = [s for s in sources if s["source_type"] == "video"]
        
        if rule_type == "price_momentum_check":
            # Check if price trend aligns with financial sentiment
            return self._validate_price_momentum(price_sources, financial_sources, parameters)
        elif rule_type == "sentiment_consistency":
            # Check consistency between financial news and video sentiment
            return self._validate_sentiment_consistency(financial_sources, video_sources, parameters)
        elif rule_type == "data_recency":
            # Check if data sources are recent enough
            return self._validate_data_recency(price_sources + financial_sources + video_sources, parameters)
        else:
            return {
                "rule_id": rule["rule_id"],
                "rule_name": rule["name"],
                "passed": False,
                "message": f"Unknown rule type: {rule_type}",
                "details": {}
            }

    def _validate_price_momentum(self, price_sources: List, financial_sources: List, params: Dict) -> Dict[str, Any]:
        """Validate if price momentum aligns with financial sentiment."""
        if not price_sources or not financial_sources:
            return {
                "passed": False,
                "message": "Insufficient data for validation",
                "details": {"price_sources": len(price_sources), "financial_sources": len(financial_sources)}
            }

        price_direction = None
        for ps in price_sources:
            content = ps.get("content", {})
            price_direction = content.get("direction") or content.get("trend")
            if price_direction:
                break

        fin_sentiment = None
        for fs in financial_sources:
            content = fs.get("content", {})
            fin_sentiment = content.get("sentiment") or content.get("outlook")
            if fin_sentiment:
                break

        if price_direction is None or fin_sentiment is None:
            return {
                "passed": True,
                "message": "Insufficient directional labels for comparison, skipping check",
                "details": {"has_price_direction": price_direction is not None, "has_fin_sentiment": fin_sentiment is not None}
            }

        bullish_terms = {"up", "positive", "bullish", "growth", "increase", "rising", "outperform"}
        bearish_terms = {"down", "negative", "bearish", "decline", "decrease", "falling", "underperform"}

        p_dir = str(price_direction).lower()
        f_sen = str(fin_sentiment).lower()
        price_up = any(t in p_dir for t in bullish_terms)
        price_down = any(t in p_dir for t in bearish_terms)
        fin_up = any(t in f_sen for t in bullish_terms)
        fin_down = any(t in f_sen for t in bearish_terms)

        if (price_up and fin_down) or (price_down and fin_up):
            passed = False
            message = f"Price direction '{price_direction}' contradicts financial sentiment '{fin_sentiment}'"
        else:
            passed = True
            message = "Price momentum aligns with financial sentiment"

        return {
            "passed": passed,
            "message": message,
            "details": {
                "price_direction": price_direction,
                "financial_sentiment": fin_sentiment,
                "checked_sources": len(price_sources) + len(financial_sources),
            }
        }

    def _validate_sentiment_consistency(self, financial_sources: List, video_sources: List, params: Dict) -> Dict[str, Any]:
        """Validate consistency between financial news and video sentiment."""
        if not financial_sources or not video_sources:
            return {
                "passed": False,
                "message": "Insufficient data for validation",
                "details": {"financial_sources": len(financial_sources), "video_sources": len(video_sources)}
            }

        pos_terms = {"positive", "bullish", "optimistic", "up", "growth", "strong"}
        neg_terms = {"negative", "bearish", "pessimistic", "down", "decline", "weak"}

        def classify_sentiment(sentiments):
            pos = sum(1 for s in sentiments if any(t in s for t in pos_terms))
            neg = sum(1 for s in sentiments if any(t in s for t in neg_terms))
            if pos > neg:
                return "positive"
            elif neg > pos:
                return "negative"
            return "neutral"

        fin_sentiments = []
        for fs in financial_sources:
            content = fs.get("content", {})
            s = content.get("sentiment") or content.get("tone")
            if s:
                fin_sentiments.append(str(s).lower())

        vid_sentiments = []
        for vs in video_sources:
            content = vs.get("content", {})
            s = content.get("sentiment") or content.get("tone")
            if s:
                vid_sentiments.append(str(s).lower())

        if not fin_sentiments or not vid_sentiments:
            return {
                "passed": True,
                "message": "Insufficient sentiment labels for consistency check, skipping",
                "details": {"fin_labeled": len(fin_sentiments), "vid_labeled": len(vid_sentiments)}
            }

        fin_class = classify_sentiment(fin_sentiments)
        vid_class = classify_sentiment(vid_sentiments)

        passed = fin_class == vid_class
        return {
            "passed": passed,
            "message": "Sentiment is consistent across sources" if passed else f"Sentiment mismatch: financial={fin_class}, video={vid_class}",
            "details": {
                "financial_dominant_sentiment": fin_class,
                "video_dominant_sentiment": vid_class,
                "checked_sources": len(financial_sources) + len(video_sources),
            }
        }

    def _validate_data_recency(self, sources: List, params: Dict) -> Dict[str, Any]:
        """Validate that data sources are recent enough."""
        if not sources:
            return {
                "passed": False,
                "message": "No data sources to validate",
                "details": {}
            }
            
        max_age_days = params.get("max_age_days", 90)
        current_time = datetime.now()
        
        outdated_sources = []
        for source in sources:
            added_time = datetime.fromisoformat(source["added_at"])
            age_days = (current_time - added_time).days
            if age_days > max_age_days:
                outdated_sources.append({
                    "source_id": source["source_id"],
                    "age_days": age_days,
                    "source_type": source["source_type"]
                })
                
        passed = len(outdated_sources) == 0
        message = "Data recency check passed" if passed else f"Found {len(outdated_sources)} outdated sources"
        
        return {
            "passed": passed,
            "message": message,
            "details": {"outdated_sources": outdated_sources, "max_age_days": max_age_days}
        }

    # ── Investment brief generation ────────────────────────────────────

    def generate_brief(
        self,
        project_id: int,
        template: str = "comprehensive",
        include_validation: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate an investment brief for a project.
        
        Args:
            project_id (int): Target project ID.
            template (str): Brief template type.
            include_validation (bool): Whether to include validation results.
            
        Returns:
            brief_id (int): Unique brief identifier.
            brief (Dict): The generated brief.
            confidence_score (int): Overall confidence score (0-100).
        """
        project = self._find_project(project_id)
        if not project:
            return {"error": f"Project ID {project_id} not found."}
            
        # Get relevant data
        sources = [s for s in self.data_sources if s["project_id"] == project_id and s["status"] == "active"]
        price_sources = [s for s in sources if s["source_type"] == "price"]
        financial_sources = [s for s in sources if s["source_type"] == "financial"]
        video_sources = [s for s in sources if s["source_type"] == "video"]
        
        if not sources:
            return {"error": "No active data sources available for this project."}
            
        # Run validation if requested
        validation_results = None
        if include_validation:
            rules = [r for r in self.validation_rules if r["project_id"] == project_id and r["status"] == "active"]
            if rules:
                validation_results = []
                for rule in rules:
                    result = self._apply_validation_rule(rule, sources)
                    validation_results.append({
                        "rule_name": rule["name"],
                        "passed": result["passed"],
                        "message": result["message"],
                        "details": result.get("details", {})
                    })
        
        # Generate brief content
        content = self._generate_brief_content(
            project, price_sources, financial_sources, video_sources,
            template, validation_results
        )
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(
            len(price_sources), len(financial_sources), len(video_sources),
            validation_results
        )
        
        brief_id = self.brief_counter
        self.brief_counter += 1
        
        brief = {
            "brief_id": brief_id,
            "project_id": project_id,
            "stock_symbol": project["stock_symbol"],
            "template": template,
            "content": content,
            "confidence_score": confidence,
            "validation_included": include_validation,
            "generated_at": datetime.now().isoformat(),
            "status": "draft",
            "source_counts": {
                "price": len(price_sources),
                "financial": len(financial_sources),
                "video": len(video_sources)
            }
        }
        self.briefs.append(brief)
        project["brief_count"] += 1
        
        self._log("brief_generated", {
            "brief_id": brief_id,
            "project_id": project_id,
            "confidence_score": confidence,
            "template": template
        })
        
        return {
            "brief_id": brief_id,
            "brief": brief,
            "confidence_score": confidence,
        }

    def _generate_brief_content(self, project: Dict, price_sources: List,
                               financial_sources: List, video_sources: List,
                               template: str, validation_results: Optional[List]) -> Dict[str, Any]:
        """Generate the content structure for the investment brief."""
        # Simplified content generation
        # In a real implementation, this would involve NLP analysis and data synthesis
        
        sections = []
        
        # Executive Summary section
        sections.append({
            "section_name": "Executive Summary",
            "content": f"Analysis of {project['stock_symbol']} based on multi-dimensional data sources.",
            "data_sources": len(price_sources) + len(financial_sources) + len(video_sources)
        })
        
        # Price Analysis section
        if price_sources:
            sections.append({
                "section_name": "Price Analysis",
                "content": f"Analyzed {len(price_sources)} price data source(s).",
                "key_insights": ["Price trend analysis", "Volatility assessment", "Support/resistance levels"]
            })
        
        # Financial Analysis section
        if financial_sources:
            sections.append({
                "section_name": "Financial Analysis",
                "content": f"Analyzed {len(financial_sources)} financial data source(s).",
                "key_insights": ["Revenue trends", "Profitability metrics", "Financial health indicators"]
            })
        
        # Management Sentiment section
        if video_sources:
            sections.append({
                "section_name": "Management Sentiment Analysis",
                "content": f"Analyzed {len(video_sources)} management video(s).",
                "key_insights": ["Leadership confidence", "Strategic direction", "Communication tone"]
            })
        
        # Validation Results section
        if validation_results:
            passed_rules = [r for r in validation_results if r["passed"]]
            failed_rules = [r for r in validation_results if not r["passed"]]
            
            sections.append({
                "section_name": "Cross-Validation Results",
                "content": f"{len(passed_rules)} validation rules passed, {len(failed_rules)} failed.",
                "passed_rules": [r["rule_name"] for r in passed_rules],
                "failed_rules": [{"rule": r["rule_name"], "issue": r["message"]} for r in failed_rules]
            })
        
        # Recommendations section
        sections.append({
            "section_name": "Investment Recommendations",
            "content": "Based on multi-dimensional analysis, the following investment perspectives are provided.",
            "perspectives": ["Short-term outlook", "Medium-term strategy", "Long-term positioning"]
        })
        
        return {
            "sections": sections,
            "total_sections": len(sections),
            "generation_method": template,
        }

    def _calculate_confidence_score(self, price_count: int, financial_count: int,
                                   video_count: int, validation_results: Optional[List]) -> int:
        """Calculate overall confidence score (0-100)."""
        # Base score from data availability
        data_score = min(100, price_count * 15 + financial_count * 20 + video_count * 10)
        
        # Adjust based on validation results
        validation_score = 50  # Default mid-range
        if validation_results:
            passed = sum(1 for r in validation_results if r["passed"])
            total = len(validation_results)
            if total > 0:
                validation_score = (passed / total) * 100
        
        # Weighted combination
        confidence = int((data_score * 0.6 + validation_score * 0.4))
        return min(100, max(0, confidence))

    def publish_brief(self, brief_id: int) -> Dict[str, Any]:
        """
        Publish a draft brief, making it available for review.
        
        Args:
            brief_id (int): Brief ID to publish.
            
        Returns:
            brief_id (int): The published brief ID.
            status (str): New status — 'published'.
        """
        brief = self._find_brief(brief_id)
        if not brief:
            return {"error": f"Brief ID {brief_id} not found."}
        if brief["status"] != "draft":
            return {"error": f"Brief {brief_id} is {brief['status']}, not draft."}
            
        brief["status"] = "published"
        brief["published_at"] = datetime.now().isoformat()
        
        self._log("brief_published", {"brief_id": brief_id})
        return {"brief_id": brief_id, "status": "published"}

    def archive_brief(self, brief_id: int) -> Dict[str, Any]:
        """
        Archive a published brief.
        
        Args:
            brief_id (int): Brief ID to archive.
            
        Returns:
            brief_id (int): The archived brief ID.
            status (str): New status — 'archived'.
        """
        brief = self._find_brief(brief_id)
        if not brief:
            return {"error": f"Brief ID {brief_id} not found."}
        if brief["status"] != "published":
            return {"error": f"Brief {brief_id} is {brief['status']}, not published."}
            
        brief["status"] = "archived"
        brief["archived_at"] = datetime.now().isoformat()
        
        self._log("brief_archived", {"brief_id": brief_id})
        return {"brief_id": brief_id, "status": "archived"}

    def list_briefs(
        self,
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        min_confidence: Optional[int] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List investment briefs with optional filtering.
        
        Args:
            project_id (int): [Optional] Filter by project ID.
            status (str): [Optional] Filter by brief status.
            min_confidence (int): [Optional] Minimum confidence score threshold.
            
        Returns:
            briefs (List[Dict]): Matching brief summaries.
        """
        if status and status not in VALID_BRIEF_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_BRIEF_STATUSES)}"}
            
        briefs = self.briefs
        if project_id is not None:
            briefs = [b for b in briefs if b["project_id"] == project_id]
        if status:
            briefs = [b for b in briefs if b["status"] == status]
        if min_confidence is not None:
            briefs = [b for b in briefs if b["confidence_score"] >= min_confidence]
            
        return {"briefs": briefs}

    # ── Helpers ────────────────────────────────────────────────────────

    def _find_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        for p in self.research_projects:
            if p["project_id"] == project_id:
                return p
        return None

    def _find_brief(self, brief_id: int) -> Optional[Dict[str, Any]]:
        for b in self.briefs:
            if b["brief_id"] == brief_id:
                return b
        return None

    def _log(self, event: str, detail: Dict) -> None:
        self.brief_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })
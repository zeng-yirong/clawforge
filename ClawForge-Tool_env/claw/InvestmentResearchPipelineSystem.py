from copy import deepcopy
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import random

DEFAULT_STATE = {
    "data_sources": {
        "stock_price": {
            "type": "time_series",
            "description": "Stock price data (open, close, high, low, volume)",
            "active": True,
            "refresh_interval": "daily"
        },
        "financial_reports": {
            "type": "structured_docs",
            "description": "Financial statement data (income statement, balance sheet, cash flow statement)",
            "active": True,
            "refresh_interval": "quarterly"
        },
        "corporate_news": {
            "type": "unstructured_text",
            "description": "Corporate announcements, news reports, analyst research",
            "active": True,
            "refresh_interval": "hourly"
        },
        "executive_interviews": {
            "type": "media_content",
            "description": "Management interviews, investor meetings, earnings call audio/video",
            "active": True,
            "refresh_interval": "weekly"
        },
        "industry_data": {
            "type": "benchmark",
            "description": "Industry indices, competitor data, macro indicators",
            "active": True,
            "refresh_interval": "monthly"
        },
        "social_sentiment": {
            "type": "alternative_data",
            "description": "Social media sentiment, search indices, consumer reviews",
            "active": True,
            "refresh_interval": "daily"
        },
        "regulatory_filings": {
            "type": "legal_documents",
            "description": "Regulatory filings, prospectuses, material event announcements",
            "active": True,
            "refresh_interval": "real-time"
        },
    },
    "research_jobs": [],
    "validation_results": [],
    "investment_briefs": [],
    "processing_log": [],
    "job_counter": 1,
    "brief_counter": 1,
    "current_ticker": None,
    "analysis_period": {"start": "2024-01-01", "end": "2024-12-31"},
    "cross_validation_rules": {
        "price_earnings_consistency": True,
        "news_sentiment_alignment": True,
        "management_tone_verification": True,
        "financial_ratio_coherence": True
    },
}

VALID_JOB_TYPES = ("data_extract", "transcribe_media", "analyze_financials", "sentiment_analysis")
VALID_JOB_STATUSES = ("pending", "processing", "completed", "failed", "validating")
VALID_BRIEF_FORMATS = ("investor_report", "executive_summary", "risk_assessment", "data_validation")
VALID_DATA_TYPES = ("price_csv", "report_pdf", "news_json", "video_mp4", "audio_m4a", "transcript_txt", "filing_xml")


class InvestmentResearchEnv:
    """
    A multi-dimensional investment research cross-validation environment.
    
    This class models a pipeline that ingests and processes financial data from diverse sources
    (stock prices, financial reports, news articles, management videos), performs cross-validation
    across these sources, and generates comprehensive investment briefs with risk assessments.
    
    Attributes:
        data_sources (Dict): Registry of available financial data sources with metadata.
        research_jobs (List[Dict]): All data ingestion and processing jobs.
        validation_results (List[Dict]): Cross-validation outcomes between different data sources.
        investment_briefs (List[Dict]): Generated investment briefs and reports.
        processing_log (List[Dict]): Audit log of all research operations.
        job_counter (int): Auto-incrementing job ID counter.
        brief_counter (int): Auto-incrementing brief ID counter.
        current_ticker (str): Currently analyzed stock ticker symbol.
        analysis_period (Dict): Time period for research analysis.
        cross_validation_rules (Dict): Rules for validating consistency across data sources.
    """
    
    def __init__(self):
        """
        Initialize the investment research environment with type hints and API description.
        """
        self.data_sources: Dict[str, Dict[str, Any]]
        self.research_jobs: List[Dict[str, Any]]
        self.validation_results: List[Dict[str, Any]]
        self.investment_briefs: List[Dict[str, Any]]
        self.processing_log: List[Dict[str, Any]]
        self.job_counter: int
        self.brief_counter: int
        self.current_ticker: Optional[str]
        self.analysis_period: Dict[str, str]
        self.cross_validation_rules: Dict[str, bool]
        self._api_description = (
            "This tool provides a multi-source investment research pipeline "
            "that cross-validates stock price data, financial reports, news content, "
            "and management video transcripts to generate comprehensive investment briefs."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario (dict): Scenario configuration containing environment state.
            long_context (bool): Whether to include extended context (unused in this implementation but kept for consistency).
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.data_sources = scenario.get("data_sources", DEFAULT_STATE_COPY["data_sources"])
        self.research_jobs = scenario.get("research_jobs", DEFAULT_STATE_COPY["research_jobs"])
        self.validation_results = scenario.get("validation_results", DEFAULT_STATE_COPY["validation_results"])
        self.investment_briefs = scenario.get("investment_briefs", DEFAULT_STATE_COPY["investment_briefs"])
        self.processing_log = scenario.get("processing_log", DEFAULT_STATE_COPY["processing_log"])
        self.job_counter = scenario.get("job_counter", DEFAULT_STATE_COPY["job_counter"])
        self.brief_counter = scenario.get("brief_counter", DEFAULT_STATE_COPY["brief_counter"])
        self.current_ticker = scenario.get("current_ticker", DEFAULT_STATE_COPY["current_ticker"])
        self.analysis_period = scenario.get("analysis_period", DEFAULT_STATE_COPY["analysis_period"])
        self.cross_validation_rules = scenario.get("cross_validation_rules", DEFAULT_STATE_COPY["cross_validation_rules"])
    
    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.
        
        Returns:
            dict: All environment state variables including data sources, research jobs,
                  validation results, investment briefs, processing log, counters, 
                  current ticker, analysis period, and cross-validation rules.
        """
        return {
            "data_sources": self.data_sources,
            "research_jobs": self.research_jobs,
            "validation_results": self.validation_results,
            "investment_briefs": self.investment_briefs,
            "processing_log": self.processing_log,
            "job_counter": self.job_counter,
            "brief_counter": self.brief_counter,
            "current_ticker": self.current_ticker,
            "analysis_period": self.analysis_period,
            "cross_validation_rules": self.cross_validation_rules,
        }
    
    # ── Data Source Management ────────────────────────────────────────────────
    
    def configure_data_source(
        self, 
        name: str, 
        is_active: bool, 
        refresh_interval: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Configure an existing data source's activation status and refresh interval.
        
        Args:
            name (str): Data source identifier (e.g., 'stock_price', 'corporate_news').
            is_active (bool): Whether the source should be active for data ingestion.
            refresh_interval (str): [Optional] Refresh frequency ('daily', 'hourly', etc.).
        
        Returns:
            Dict: The updated source configuration with status confirmation.
        """
        if name not in self.data_sources:
            return {"error": f"Data source '{name}' not found. Available sources: {', '.join(self.data_sources.keys())}"}
        
        self.data_sources[name]["active"] = is_active
        if refresh_interval:
            self.data_sources[name]["refresh_interval"] = refresh_interval
        
        self._log("source_configured", {
            "name": name, 
            "active": is_active, 
            "refresh_interval": self.data_sources[name]["refresh_interval"]
        })
        return {"success": True, "source": {name: self.data_sources[name]}}
    
    def list_active_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all active data sources available for research.
        
        Returns:
            Dict: List of active data sources with their metadata.
        """
        active_sources = []
        for name, meta in self.data_sources.items():
            if meta["active"]:
                active_sources.append({
                    "name": name,
                    "type": meta["type"],
                    "description": meta["description"],
                    "refresh_interval": meta["refresh_interval"]
                })
        return {"active_sources": active_sources}
    
    # ── Data Ingestion ───────────────────────────────────────────────────
    
    def ingest_research_data(
        self, 
        ticker: str, 
        data_type: str, 
        source: str, 
        data_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest financial research data for a specific stock ticker.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT').
            data_type (str): Type of data being ingested. Must be one of VALID_DATA_TYPES.
            source (str): Data source name (must match registered sources).
            data_path (str): Path to data file, API endpoint, or content identifier.
            metadata (Dict): [Optional] Additional metadata (date_range, version, etc.).
        
        Returns:
            Dict: Job ID and the created research job record with status 'pending'.
        """
        if data_type not in VALID_DATA_TYPES:
            return {"error": f"Invalid data_type '{data_type}'. Must be one of: {', '.join(VALID_DATA_TYPES)}"}
        
        if source not in self.data_sources:
            return {"error": f"Unknown source '{source}'. Available sources: {', '.join(self.data_sources.keys())}"}
        
        if not self.data_sources[source]["active"]:
            return {"error": f"Source '{source}' is currently inactive. Activate it first with configure_data_source."}
        
        self.current_ticker = ticker
        job_id = self.job_counter
        self.job_counter += 1
        
        job_type = self._determine_job_type(data_type, source)
        metadata = metadata or {}
        
        job = {
            "job_id": job_id,
            "ticker": ticker,
            "data_type": data_type,
            "source": source,
            "data_path": data_path,
            "job_type": job_type,
            "metadata": metadata,
            "status": "pending",
            "processed_data": None,
            "insights": None,
            "processed_at": None,
            "confidence_score": None,
        }
        self.research_jobs.append(job)
        self._log("research_data_ingested", {
            "job_id": job_id, 
            "ticker": ticker, 
            "data_type": data_type, 
            "source": source
        })
        return {"job_id": job_id, "job": job}
    
    # ── Data Processing ────────────────────────────────────────────────────────
    
    def process_research_job(
        self, 
        job_id: int, 
        processing_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process ingested research data to extract financial insights.
        
        Args:
            job_id (int): The job ID returned by ingest_research_data().
            processing_params (Dict): [Optional] Processing parameters:
                - time_period (str): Specify time period for analysis.
                - detailed_mode (bool): Whether to extract detailed metrics.
                - sentiment_window (int): Window size for sentiment analysis.
                - include_derivatives (bool): Include financial derivatives.
        
        Returns:
            Dict: Processing results with extracted insights and confidence score.
        """
        processing_params = processing_params or {}
        job = self._find_job(job_id)
        if not job:
            return {"error": f"Research job ID {job_id} not found."}
        
        if job["status"] not in ("pending", "failed"):
            return {"error": f"Job {job_id} is already {job['status']}. Re-ingest to reprocess."}
        
        job["status"] = "processing"
        self._log("research_processing_started", {"job_id": job_id, "params": processing_params})
        
        if job["job_type"] == "data_extract":
            result = self._simulate_data_extraction(job["ticker"], job["source"], job["data_type"], processing_params)
        elif job["job_type"] == "transcribe_media":
            result = self._simulate_media_transcription(job["data_path"], job["source"], processing_params)
        elif job["job_type"] == "analyze_financials":
            result = self._simulate_financial_analysis(job["ticker"], job["data_type"], processing_params)
        elif job["job_type"] == "sentiment_analysis":
            result = self._simulate_sentiment_analysis(job["ticker"], job["source"], processing_params)
        else:
            job["status"] = "failed"
            return {"error": f"Unknown job_type '{job['job_type']}'."}
        
        job["status"] = "completed"
        job["processed_data"] = result
        job["insights"] = result.get("key_insights", [])
        job["confidence_score"] = result.get("confidence", 0.8)
        job["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self._log("research_processing_completed", {
            "job_id": job_id, 
            "insight_count": len(job["insights"]),
            "confidence": job["confidence_score"]
        })
        
        return {
            "job_id": job_id, 
            "status": "completed", 
            "insights": job["insights"],
            "confidence_score": job["confidence_score"],
            "processed_data_keys": list(result.keys())
        }
    
    def get_research_job(self, job_id: int) -> Dict[str, Any]:
        """
        Retrieve the full state of a research processing job.
        
        Args:
            job_id (int): Research job ID.
        
        Returns:
            Dict: Full job record with status, processed data, and insights.
        """
        job = self._find_job(job_id)
        if not job:
            return {"error": f"Research job ID {job_id} not found."}
        return {"research_job": job}
    
    def list_research_jobs(self, ticker: Optional[str] = None, status: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all research jobs, optionally filtered by ticker and status.
        
        Args:
            ticker (str): [Optional] Filter by stock ticker.
            status (str): [Optional] Filter by job status.
        
        Returns:
            Dict: List of matching job summaries.
        """
        if status and status not in VALID_JOB_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_JOB_STATUSES)}"}
        
        filtered_jobs = self.research_jobs
        if ticker:
            filtered_jobs = [j for j in filtered_jobs if j["ticker"] == ticker]
        if status:
            filtered_jobs = [j for j in filtered_jobs if j["status"] == status]
        
        summaries = [
            {
                "job_id": j["job_id"],
                "ticker": j["ticker"],
                "source": j["source"],
                "data_type": j["data_type"],
                "job_type": j["job_type"],
                "status": j["status"],
                "confidence_score": j["confidence_score"]
            } for j in filtered_jobs
        ]
        return {"research_jobs": summaries}
    
    # ── Cross-Validation ──────────────────────────────────────────────────────
    
    def cross_validate_sources(
        self, 
        job_ids: List[int], 
        validation_rules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform cross-validation across multiple completed research jobs to check consistency.
        
        Args:
            job_ids (List[int]): List of completed job IDs to validate against each other.
            validation_rules (List[str]): [Optional] Specific validation rules to apply.
                If None, uses the environment's default cross_validation_rules.
        
        Returns:
            Dict: Validation results including consistency scores and identified discrepancies.
        """
        if len(job_ids) < 2:
            return {"error": "At least 2 job IDs are required for cross-validation."}
        
        completed_jobs = []
        for jid in job_ids:
            job = self._find_job(jid)
            if not job:
                return {"error": f"Research job ID {jid} not found."}
            if job["status"] != "completed":
                return {"error": f"Job {jid} is not completed (status={job['status']}). Process it first."}
            completed_jobs.append(job)
        
        validation_rules = validation_rules or [
            rule for rule, enabled in self.cross_validation_rules.items() if enabled
        ]
        
        validation_result_id = len(self.validation_results) + 1
        validation_results = []
        
        for rule in validation_rules:
            if rule == "price_earnings_consistency":
                result = self._validate_price_earnings_consistency(completed_jobs)
            elif rule == "news_sentiment_alignment":
                result = self._validate_news_sentiment_alignment(completed_jobs)
            elif rule == "management_tone_verification":
                result = self._validate_management_tone_verification(completed_jobs)
            elif rule == "financial_ratio_coherence":
                result = self._validate_financial_ratio_coherence(completed_jobs)
            else:
                result = {"rule": rule, "status": "skipped", "reason": "Unknown validation rule"}
            
            validation_results.append(result)
        
        overall_consistency = self._calculate_overall_consistency(validation_results)
        
        validation_record = {
            "validation_id": validation_result_id,
            "job_ids": job_ids,
            "ticker": completed_jobs[0]["ticker"],
            "validation_rules_applied": validation_rules,
            "results": validation_results,
            "overall_consistency_score": overall_consistency,
            "validation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        self.validation_results.append(validation_record)
        self._log("cross_validation_completed", {
            "validation_id": validation_result_id,
            "job_count": len(job_ids),
            "consistency_score": overall_consistency
        })
        
        return {
            "validation_id": validation_result_id,
            "overall_consistency": overall_consistency,
            "results": validation_results,
            "summary": self._generate_validation_summary(validation_results, overall_consistency)
        }
    
    # ── Investment Brief Generation ──────────────────────────────────────────
    
    def generate_investment_brief(
        self, 
        job_ids: List[int], 
        brief_format: str = "investor_report",
        risk_level: str = "medium",
        include_validation: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive investment brief from processed research data.
        
        Args:
            job_ids (List[int]): List of job IDs to include in the brief.
            brief_format (str): Output format - 'investor_report', 'executive_summary', 
                              'risk_assessment', or 'data_validation'.
            risk_level (str): Risk assessment level - 'low', 'medium', 'high'.
            include_validation (bool): Whether to include cross-validation results.
        
        Returns:
            Dict: Generated brief ID and content with investment recommendations.
        """
        if brief_format not in VALID_BRIEF_FORMATS:
            return {"error": f"Invalid brief_format '{brief_format}'. Must be one of: {', '.join(VALID_BRIEF_FORMATS)}"}
        
        if not job_ids:
            return {"error": "At least one job_id is required."}
        
        completed_jobs = []
        for jid in job_ids:
            job = self._find_job(jid)
            if not job:
                return {"error": f"Job ID {jid} not found."}
            if job["status"] != "completed":
                return {"error": f"Job {jid} is not completed. Process it first."}
            completed_jobs.append(job)
        
        brief_id = self.brief_counter
        self.brief_counter += 1
        
        validation_results = None
        if include_validation and len(job_ids) >= 2:
            validation_result = self.cross_validate_sources(job_ids)
            if "validation_id" in validation_result:
                validation_results = validation_result
        
        ticker = completed_jobs[0]["ticker"]
        title = f"Investment Brief: {ticker} - {datetime.now().strftime('%Y-%m-%d')}"
        
        content = self._render_investment_brief(
            completed_jobs, 
            brief_format, 
            title, 
            risk_level, 
            validation_results
        )
        
        brief = {
            "brief_id": brief_id,
            "ticker": ticker,
            "title": title,
            "format": brief_format,
            "job_ids": job_ids,
            "risk_level": risk_level,
            "content": content,
            "validation_included": include_validation and validation_results is not None,
            "validation_score": validation_results.get("overall_consistency") if validation_results else None,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recommendations": self._extract_recommendations(content, risk_level),
        }
        
        self.investment_briefs.append(brief)
        self._log("investment_brief_generated", {
            "brief_id": brief_id, 
            "format": brief_format, 
            "job_count": len(job_ids),
            "risk_level": risk_level
        })
        
        return {"brief_id": brief_id, "investment_brief": brief}
    
    def list_investment_briefs(self, ticker: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all generated investment briefs.
        
        Args:
            ticker (str): [Optional] Filter by stock ticker.
        
        Returns:
            Dict: List of brief summaries with ID, title, format, and risk level.
        """
        filtered_briefs = self.investment_briefs
        if ticker:
            filtered_briefs = [b for b in filtered_briefs if b["ticker"] == ticker]
        
        summaries = [
            {
                "brief_id": b["brief_id"],
                "ticker": b["ticker"],
                "title": b["title"],
                "format": b["format"],
                "risk_level": b["risk_level"],
                "job_count": len(b["job_ids"]),
                "created_at": b["created_at"],
                "validation_score": b["validation_score"]
            } for b in filtered_briefs
        ]
        return {"investment_briefs": summaries}
    
    # ── Helper Methods ────────────────────────────────────────────────────────
    
    def _find_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Find a research job by ID. Returns None if not found."""
        for j in self.research_jobs:
            if j["job_id"] == job_id:
                return j
        return None
    
    def _determine_job_type(self, data_type: str, source: str) -> str:
        """Determine the appropriate job type based on data type and source."""
        if data_type.startswith(("video_", "audio_")):
            return "transcribe_media"
        elif source in ("financial_reports", "regulatory_filings"):
            return "analyze_financials"
        elif source in ("corporate_news", "social_sentiment"):
            return "sentiment_analysis"
        else:
            return "data_extract"
    
    def _simulate_data_extraction(
        self, 
        ticker: str, 
        source: str, 
        data_type: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate extraction of structured financial data."""
        random.seed(hash(f"{ticker}_{source}") % 2**31)
        
        if source == "stock_price":
            return {
                "extracted_data": {
                    "price_history": [random.uniform(100, 500) for _ in range(30)],
                    "volume_trend": [random.randint(1000000, 5000000) for _ in range(30)],
                    "volatility": random.uniform(0.1, 0.4),
                    "moving_averages": {
                        "SMA_20": random.uniform(200, 300),
                        "EMA_50": random.uniform(210, 310)
                    }
                },
                "key_insights": [
                    f"{ticker} shows {random.choice(['upward', 'sideways', 'corrective'])} price trend",
                    f"Volume pattern indicates {random.choice(['accumulation', 'distribution', 'neutral'])}",
                    f"Technical indicators suggest {random.choice(['bullish', 'bearish', 'neutral'])} momentum"
                ],
                "confidence": round(random.uniform(0.7, 0.95), 2),
                "source": source,
                "data_type": data_type,
                "period": params.get("time_period", "30_days")
            }
        
        return {
            "extracted_data": {"sample_data": f"Extracted from {source} for {ticker}"},
            "key_insights": [f"Primary insight from {source}", f"Secondary finding from {source}"],
            "confidence": 0.8,
            "source": source,
            "data_type": data_type
        }
    
    def _simulate_media_transcription(
        self, 
        data_path: str, 
        source: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate transcription of management interviews and video content."""
        random.seed(hash(data_path) % 2**31)
        
        management_topics = [
            "earnings guidance", "growth strategy", "market expansion", 
            "product pipeline", "competitive landscape", "risk factors",
            "capital allocation", "ESG initiatives", "regulatory outlook"
        ]
        
        selected_topics = random.sample(management_topics, random.randint(3, 6))
        
        return {
            "transcript": f"[Simulated CEO/CFO interview transcript for: {data_path}] "
                         f"Discusses {', '.join(selected_topics)}. Management expresses "
                         f"{random.choice(['cautious optimism', 'strong confidence', 'measured outlook'])} "
                         f"about future performance.",
            "identified_speakers": [
                {"name": "CEO", "speaking_time_seconds": random.randint(300, 600)},
                {"name": "CFO", "speaking_time_seconds": random.randint(200, 400)},
                {"name": "Investor Relations", "speaking_time_seconds": random.randint(100, 300)}
            ],
            "key_points": [
                {
                    "text": f"Management emphasized {random.choice(selected_topics)}",
                    "sentiment": random.choice(["positive", "neutral", "cautious"]),
                    "confidence": round(random.uniform(0.8, 0.95), 2),
                    "timestamp": "00:05:30"
                } for _ in range(5)
            ],
            "sentiment_score": round(random.uniform(-0.5, 0.8), 2),
            "confidence": round(random.uniform(0.75, 0.92), 2),
            "source": source,
        }
    
    def _simulate_financial_analysis(
        self, 
        ticker: str, 
        data_type: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate analysis of financial statements and ratios."""
        random.seed(hash(f"{ticker}_financials") % 2**31)
        
        return {
            "financial_metrics": {
                "revenue_growth": round(random.uniform(-0.05, 0.25), 3),
                "profit_margin": round(random.uniform(0.05, 0.35), 3),
                "roe": round(random.uniform(0.08, 0.25), 3),
                "debt_to_equity": round(random.uniform(0.2, 1.5), 2),
                "current_ratio": round(random.uniform(1.0, 3.0), 2),
                "free_cash_flow": random.uniform(1000, 10000),
            },
            "key_insights": [
                f"Revenue shows {random.choice(['strong', 'moderate', 'weak'])} growth trajectory",
                f"Profitability metrics are {random.choice(['above', 'in-line with', 'below'])} industry average",
                f"Balance sheet appears {random.choice(['strong', 'adequate', 'stretched'])}",
                f"Cash flow generation is {random.choice(['robust', 'sufficient', 'concerning'])}"
            ],
            "peer_comparison": {
                "industry_rank": random.randint(1, 10),
                "percentile": random.randint(30, 95),
                "strengths": random.sample(["profitability", "growth", "efficiency", "liquidity"], 2),
                "weaknesses": random.sample(["leverage", "volatility", "coverage_ratios"], 1)
            },
            "confidence": round(random.uniform(0.85, 0.98), 2),
            "data_type": data_type,
        }
    
    def _simulate_sentiment_analysis(
        self, 
        ticker: str, 
        source: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate sentiment analysis of news and social media content."""
        random.seed(hash(f"{ticker}_{source}") % 2**31)
        
        sentiment_window = params.get("sentiment_window", 7)
        
        sentiments = []
        for i in range(sentiment_window):
            day_sentiment = {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "sentiment_score": round(random.uniform(-0.7, 0.7), 2),
                "volume": random.randint(100, 10000),
                "dominant_topics": random.sample(["earnings", "products", "management", "regulation"], 2)
            }
            sentiments.append(day_sentiment)
        
        avg_sentiment = sum(s["sentiment_score"] for s in sentiments) / len(sentiments)
        
        return {
            "sentiment_timeline": sentiments,
            "average_sentiment": round(avg_sentiment, 2),
            "sentiment_trend": "increasing" if avg_sentiment > 0.1 else "decreasing" if avg_sentiment < -0.1 else "stable",
            "key_topics": {
                "positive": random.sample(["innovation", "growth", "dividends"], random.randint(1, 3)),
                "negative": random.sample(["competition", "regulation", "volatility"], random.randint(0, 2)),
                "neutral": random.sample(["guidance", "industry", "markets"], random.randint(1, 2))
            },
            "confidence": round(random.uniform(0.65, 0.9), 2),
            "source": source,
            "analysis_window": f"{sentiment_window}_days"
        }
    
    def _validate_price_earnings_consistency(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Validate consistency between price movements and earnings data."""

        price_jobs = [j for j in jobs if j["source"] == "stock_price"]
        earnings_jobs = [j for j in jobs if j["source"] in ("financial_reports", "corporate_news")]
        
        if not price_jobs or not earnings_jobs:
            return {
                "rule": "price_earnings_consistency",
                "status": "incomplete",
                "reason": "Missing required data sources",
                "score": 0.5
            }
        
        score = random.uniform(0.6, 0.95)
        
        return {
            "rule": "price_earnings_consistency",
            "status": "completed",
            "score": round(score, 2),
            "assessment": "Consistent" if score > 0.7 else "Needs Review",
            "details": f"Price trend alignment with earnings data: {round(score*100)}%"
        }
    
    def _validate_news_sentiment_alignment(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Validate alignment between news sentiment and price movements."""

        sentiment_jobs = [j for j in jobs if j["source"] in ("corporate_news", "social_sentiment")]
        price_jobs = [j for j in jobs if j["source"] == "stock_price"]
        
        if not sentiment_jobs or not price_jobs:
            return {
                "rule": "news_sentiment_alignment",
                "status": "incomplete",
                "reason": "Missing sentiment or price data",
                "score": 0.5
            }
        
        score = random.uniform(0.55, 0.9)
        
        return {
            "rule": "news_sentiment_alignment",
            "status": "completed",
            "score": round(score, 2),
            "assessment": "Aligned" if score > 0.65 else "Diverging",
            "details": f"News sentiment correlation with price: {round(score*100)}%"
        }
    
    def _validate_management_tone_verification(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Verify consistency between management statements and financial results."""

        media_jobs = [j for j in jobs if j["source"] == "executive_interviews"]
        financial_jobs = [j for j in jobs if j["source"] in ("financial_reports", "regulatory_filings")]
        
        if not media_jobs or not financial_jobs:
            return {
                "rule": "management_tone_verification",
                "status": "incomplete",
                "reason": "Missing management or financial data",
                "score": 0.5
            }
        
        score = random.uniform(0.7, 0.98)
        
        return {
            "rule": "management_tone_verification",
            "status": "completed",
            "score": round(score, 2),
            "assessment": "Verified" if score > 0.8 else "Questionable",
            "details": f"Management commentary consistency with financials: {round(score*100)}%"
        }
    
    def _validate_financial_ratio_coherence(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Validate internal coherence of financial ratios and metrics."""

        financial_jobs = [j for j in jobs if j["source"] in ("financial_reports", "regulatory_filings")]
        
        if len(financial_jobs) < 2:
            return {
                "rule": "financial_ratio_coherence",
                "status": "incomplete",
                "reason": "Insufficient financial data for ratio comparison",
                "score": 0.5
            }
        
        score = random.uniform(0.75, 0.99)
        
        return {
            "rule": "financial_ratio_coherence",
            "status": "completed",
            "score": round(score, 2),
            "assessment": "Coherent" if score > 0.85 else "Inconsistent",
            "details": f"Internal consistency of financial metrics: {round(score*100)}%"
        }
    
    def _calculate_overall_consistency(self, validation_results: List[Dict]) -> float:
        """Calculate overall consistency score from validation results."""
        completed_results = [r for r in validation_results if r.get("status") == "completed" and "score" in r]
        if not completed_results:
            return 0.5
        
        scores = [r["score"] for r in completed_results]
        return round(sum(scores) / len(scores), 2)
    
    def _generate_validation_summary(self, validation_results: List[Dict], overall_score: float) -> str:
        """Generate a human-readable summary of validation results."""
        completed = [r for r in validation_results if r.get("status") == "completed"]
        incomplete = [r for r in validation_results if r.get("status") == "incomplete"]
        
        summary_parts = [
            f"Overall Consistency Score: {overall_score:.0%}",
            f"Completed Validations: {len(completed)}",
            f"Incomplete Validations: {len(incomplete)}"
        ]
        
        if completed:
            summary_parts.append("Details:")
            for result in completed:
                summary_parts.append(f"- {result['rule']}: {result['assessment']} ({result['score']:.0%})")
        
        return "\n".join(summary_parts)
    
    def _render_investment_brief(
        self, 
        jobs: List[Dict], 
        brief_format: str, 
        title: str, 
        risk_level: str,
        validation_results: Optional[Dict]
    ) -> str:
        """Render investment brief content in the requested format."""
        ticker = jobs[0]["ticker"]
        
        if brief_format == "executive_summary":
            lines = [
                f"# {title}",
                f"## Executive Summary\n",
                f"**Ticker:** {ticker}",
                f"**Risk Level:** {risk_level.upper()}",
                f"**Data Sources:** {', '.join(sorted(set(j['source'] for j in jobs)))}",
                f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}\n",
                "### Key Investment Highlights",
            ]
            
            for i, job in enumerate(jobs[:3], 1):
                if job.get("insights"):
                    lines.append(f"{i}. {job['insights'][0]}")
            
            if validation_results:
                lines.append(f"\n### Cross-Validation Summary")
                lines.append(f"Overall Consistency: {validation_results.get('overall_consistency', 0.5):.0%}")
            
            lines.append("\n### Recommendation")
            if risk_level == "low":
                lines.append("Consider for core portfolio positions with long-term horizon.")
            elif risk_level == "high":
                lines.append("Suitable for tactical allocation with close monitoring.")
            else:
                lines.append("Appropriate for balanced portfolio with regular review.")
            
            return "\n".join(lines)
        
        elif brief_format == "risk_assessment":
            lines = [
                f"# {title}",
                f"## Comprehensive Risk Assessment\n",
                f"**Ticker:** {ticker}",
                f"**Overall Risk Rating:** {risk_level.upper()}\n",
                "### Risk Factors Identified:",
                "1. **Market Risk:** Moderate exposure to sector volatility",
                "2. **Credit Risk:** Limited based on financial health analysis",
                "3. **Operational Risk:** Standard for industry peers",
                "4. **Regulatory Risk:** Monitoring required for policy changes",
                "5. **Liquidity Risk:** Adequate based on trading volumes\n",
                "### Data-Driven Risk Metrics:",
            ]
            
            for job in jobs:
                if job.get("confidence_score"):
                    lines.append(f"- {job['source']}: Confidence {job['confidence_score']:.0%}")
            
            return "\n".join(lines)
        
        elif brief_format == "data_validation":
            lines = [
                f"# {title}",
                f"## Data Quality and Validation Report\n",
                f"**Ticker:** {ticker}",
                f"**Total Data Sources:** {len(jobs)}\n",
                "### Source Quality Assessment:",
            ]
            
            for job in jobs:
                status = "✓" if job.get("confidence_score", 0) > 0.7 else "⚠"
                lines.append(f"- {status} {job['source']}: {job.get('confidence_score', 'N/A'):.0%}")
            
            if validation_results:
                lines.append(f"\n### Cross-Validation Results:")
                lines.append(validation_results.get("summary", "No validation results available"))
            
            return "\n".join(lines)
        
        else:  # investor_report (default)
            lines = [
                f"# {title}",
                f"## Comprehensive Investment Analysis\n",
                f"**Security:** {ticker}",
                f"**Risk Profile:** {risk_level.upper()}",
                f"**Report Date:** {datetime.now().strftime('%Y-%m-%d')}\n",
                "### Multi-Source Analysis Summary",
            ]
            
            sources_summary = {}
            for job in jobs:
                source = job['source']
                if source not in sources_summary:
                    sources_summary[source] = []
                if job.get("insights"):
                    sources_summary[source].extend(job["insights"][:2])
            
            for source, insights in sources_summary.items():
                lines.append(f"#### {source.replace('_', ' ').title()}")
                for insight in insights[:2]:
                    lines.append(f"- {insight}")
                lines.append("")
            
            if validation_results:
                lines.append("### Cross-Validation Assessment")
                lines.append(f"Overall Data Consistency: {validation_results.get('overall_consistency', 0.5):.0%}")
                lines.append("")
            
            lines.append("### Investment Conclusion")
            lines.append("Based on multi-dimensional analysis across price data, financial reports, ")
            lines.append("news sentiment, and management commentary, this security presents a ")
            lines.append(f"{risk_level} risk/reward profile suitable for {risk_level} risk tolerance investors.")
            
            return "\n".join(lines)
    
    def _extract_recommendations(self, content: str, risk_level: str) -> List[str]:
        """Extract key recommendations from brief content."""
        recommendations = []
        
        if risk_level == "low":
            recommendations.extend([
                "Consider for long-term core holdings",
                "Monitor quarterly financial reports",
                "Reassess on major market events"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "Tactical position only",
                "Set strict stop-loss levels",
                "Monitor daily price action"
            ])
        else:  # medium
            recommendations.extend([
                "Suitable for diversified portfolio",
                "Review performance quarterly",
                "Watch for earnings catalysts"
            ])
        
        return recommendations
    
    def _log(self, event: str, detail: Dict) -> None:
        """Append an entry to the processing audit log."""
        self.processing_log.append({
            "event": event, 
            "detail": detail, 
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
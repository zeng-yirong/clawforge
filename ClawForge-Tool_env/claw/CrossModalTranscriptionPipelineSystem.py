from copy import deepcopy
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import random
import json

DEFAULT_STATE = {
    "media_sources": {
        "youtube": {"type": "video", "description": "YouTube video link", "active": True, "max_duration": 3600},
        "local_m4a": {"type": "audio", "description": "Local M4A audio file", "active": True, "max_duration": 1800},
        "podcast_rss": {"type": "audio", "description": "Podcast RSS feed", "active": True, "max_duration": 5400},
        "zoom_recording": {"type": "video", "description": "Zoom meeting recording", "active": True, "max_duration": 7200},
    },
    "discussion_sources": {
        "reddit": {"type": "social", "description": "Reddit community discussion", "active": True, "max_comments": 500},
        "twitter": {"type": "microblog", "description": "Twitter/X topic discussion", "active": True, "max_tweets": 300},
        "hackernews": {"type": "tech", "description": "Hacker News tech discussion", "active": True, "max_comments": 200},
        "zhihu": {"type": "qa", "description": "Zhihu questions and answers", "active": True, "max_answers": 100},
        "quora": {"type": "qa", "description": "Quora Q&A community", "active": True, "max_answers": 100},
    },
    "transcription_jobs": [],
    "discussion_jobs": [],
    "summary_outputs": [],
    "processing_log": [],
    "job_counter": 1,
    "output_counter": 1,
    "current_mode": "standalone",  # "standalone" or "integrated"
}

VALID_MEDIA_TYPES = ("audio_m4a", "video_youtube", "video_zoom", "audio_podcast")
VALID_DISCUSSION_TYPES = ("reddit_thread", "twitter_thread", "hn_thread", "zhihu_question", "quora_question")
VALID_TRANSCRIPTION_STATUSES = ("pending", "transcribing", "transcribed", "failed")
VALID_ANALYSIS_STATUSES = ("pending", "analyzing", "analyzed", "failed")
VALID_SUMMARY_FORMATS = ("markdown", "bullet", "json", "executive", "technical")


class CrossModalPipelineEnv:
    """
    Cross-modal content transcription and summarization environment.

    This environment simulates the complete pipeline of transcribing speech/video content into text
    and performing integrated analysis with relevant community discussions.
    Supports two processing modes:
    1. Standalone mode: transcribe media content only
    2. Integrated mode: transcribe media content + retrieve related discussions + comprehensive analysis

    Core pipeline: Media ingestion -> Speech transcription -> Discussion retrieval -> Comprehensive analysis -> Summary generation
    """

    def __init__(self):
        """
        Initialize the cross-modal transcription environment.
        """
        self.media_sources: Dict[str, Dict[str, Any]]
        self.discussion_sources: Dict[str, Dict[str, Any]]
        self.transcription_jobs: List[Dict[str, Any]]
        self.discussion_jobs: List[Dict[str, Any]]
        self.summary_outputs: List[Dict[str, Any]]
        self.processing_log: List[Dict[str, Any]]
        self.job_counter: int
        self.output_counter: int
        self.current_mode: str
        
        self._api_description = (
            "This tool provides cross-modal content transcription and summarization features, supporting audio/video transcription to text and integration of related community discussion data to generate comprehensive analysis reports."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load environment state from scenario configuration.

        Args:
            scenario (dict): Dictionary containing environment initial state
            long_context (bool): Whether to load long context mode
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.media_sources = scenario.get("media_sources", DEFAULT_STATE_COPY["media_sources"])
        self.discussion_sources = scenario.get("discussion_sources", DEFAULT_STATE_COPY["discussion_sources"])
        self.transcription_jobs = scenario.get("transcription_jobs", DEFAULT_STATE_COPY["transcription_jobs"])
        self.discussion_jobs = scenario.get("discussion_jobs", DEFAULT_STATE_COPY["discussion_jobs"])
        self.summary_outputs = scenario.get("summary_outputs", DEFAULT_STATE_COPY["summary_outputs"])
        self.processing_log = scenario.get("processing_log", DEFAULT_STATE_COPY["processing_log"])
        self.job_counter = scenario.get("job_counter", DEFAULT_STATE_COPY["job_counter"])
        self.output_counter = scenario.get("output_counter", DEFAULT_STATE_COPY["output_counter"])
        self.current_mode = scenario.get("current_mode", DEFAULT_STATE_COPY["current_mode"])

    def get_env_state(self) -> dict:
        """
        Return the complete internal state of the current environment.

        Returns:
            dict: Dictionary containing all environment state variables, including:
                - media_sources: Media source configuration
                - discussion_sources: Discussion source configuration
                - transcription_jobs: Transcription job list
                - discussion_jobs: Discussion analysis job list
                - summary_outputs: Summary output list
                - processing_log: Processing log
                - job_counter: Job counter
                - output_counter: Output counter
                - current_mode: Current processing mode
        """
        return {
            "media_sources": self.media_sources,
            "discussion_sources": self.discussion_sources,
            "transcription_jobs": self.transcription_jobs,
            "discussion_jobs": self.discussion_jobs,
            "summary_outputs": self.summary_outputs,
            "processing_log": self.processing_log,
            "job_counter": self.job_counter,
            "output_counter": self.output_counter,
            "current_mode": self.current_mode,
        }

    # ── Source management ───────────────────────────────────────────────────────────────

    def add_media_source(self, name: str, source_type: str, max_duration: int = 3600) -> Dict[str, Any]:
        """
        Register a new media source.

        Args:
            name (str): Unique source identifier
            source_type (str): Source type ("audio" or "video")
            max_duration (int): Maximum duration limit (seconds)

        Returns:
            Dict: Contains the registered source entry or error information
        """
        if name in self.media_sources:
            return {"error": f"Media source '{name}' already exists."}

        if source_type not in ("audio", "video"):
            return {"error": f"Invalid source type '{source_type}', must be 'audio' or 'video'."}
        
        self.media_sources[name] = {
            "type": source_type,
            "description": "",
            "active": True,
            "max_duration": max_duration
        }
        self._log("media_source_added", {"name": name, "source_type": source_type, "max_duration": max_duration})
        return {"source": {"name": name, **self.media_sources[name]}}

    def add_discussion_source(self, name: str, source_type: str, max_items: int = 200) -> Dict[str, Any]:
        """
        Register a new discussion source.

        Args:
            name (str): Unique source identifier
            source_type (str): Source type (e.g. "social", "qa", "tech")
            max_items (int): Maximum item count limit

        Returns:
            Dict: Contains the registered source entry or error information
        """
        if name in self.discussion_sources:
            return {"error": f"Discussion source '{name}' already exists."}
        
        self.discussion_sources[name] = {
            "type": source_type,
            "description": "",
            "active": True,
            "max_items": max_items
        }
        self._log("discussion_source_added", {"name": name, "source_type": source_type, "max_items": max_items})
        return {"source": {"name": name, **self.discussion_sources[name]}}

    def list_media_sources(self, source_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List registered media sources, optionally filtered by type.

        Args:
            source_type (str): [Optional] Filter by source type

        Returns:
            Dict: Contains the list of matching media sources
        """
        result = []
        for name, meta in self.media_sources.items():
            if source_type and meta["type"] != source_type:
                continue
            result.append({
                "name": name,
                "type": meta["type"],
                "active": meta["active"],
                "max_duration": meta.get("max_duration", 3600)
            })
        return {"media_sources": result}

    def list_discussion_sources(self, source_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List registered discussion sources, optionally filtered by type.

        Args:
            source_type (str): [Optional] Filter by source type

        Returns:
            Dict: Contains the list of matching discussion sources
        """
        result = []
        for name, meta in self.discussion_sources.items():
            if source_type and meta["type"] != source_type:
                continue
            result.append({
                "name": name,
                "type": meta["type"],
                "active": meta["active"],
                "max_items": meta.get("max_items", 200)
            })
        return {"discussion_sources": result}

    # ── Data ingestion ─────────────────────────────────────────────────────────────

    def ingest_media(self, media_url: str = None, media_type: str = None, title: str = "", **kwargs: Any) -> Dict[str, Any]:
        """
        Ingest media content for transcription.

        Args:
            media_url (str): Media URL or file path
            media_type (str): Media type, must be: audio_m4a, video_youtube, video_zoom, audio_podcast
            title (str): [Optional] Media title

        Returns:
            Dict: Contains job ID and job record
        """
        if not isinstance(media_url, str) or not media_url.strip():
            return {"error": "media_url must be a non-empty string."}
        if not isinstance(media_type, str):
            return {"error": "media_type must be a string."}
        if media_type not in VALID_MEDIA_TYPES:
            return {"error": f"Invalid media type '{media_type}'. Must be: {', '.join(VALID_MEDIA_TYPES)}"}
        if not isinstance(title, str):
            return {"error": "title must be a string."}

        job_id = self.job_counter
        self.job_counter += 1
        
        job = {
            "job_id": job_id,
            "media_url": media_url,
            "media_type": media_type,
            "title": title or f"Media content {job_id}",
            "status": "pending",
            "transcript": None,
            "metadata": {},
            "language": "auto",
            "processed_at": None,
            "duration_seconds": None,
        }
        self.transcription_jobs.append(job)
        self._log("media_ingested", {"job_id": job_id, "media_type": media_type, "title": job["title"]})
        return {"job_id": job_id, "job": job}

    def ingest_discussion(self, query: str, source_type: str, source_name: str = "") -> Dict[str, Any]:
        """
        Ingest a discussion query for analysis.

        Args:
            query (str): Search query or discussion topic
            source_type (str): Discussion source type, must be: reddit_thread, twitter_thread, hn_thread, zhihu_question, quora_question
            source_name (str): [Optional] Specific source name

        Returns:
            Dict: Contains job ID and job record
        """
        if source_type not in VALID_DISCUSSION_TYPES:
            return {"error": f"Invalid discussion type '{source_type}'. Must be: {', '.join(VALID_DISCUSSION_TYPES)}"}
        
        job_id = self.job_counter
        self.job_counter += 1
        
        job = {
            "job_id": job_id,
            "query": query,
            "source_type": source_type,
            "source_name": source_name or self._map_source_type(source_type),
            "status": "pending",
            "comments": [],
            "analysis": None,
            "processed_at": None,
            "item_count": 0,
        }
        self.discussion_jobs.append(job)
        self._log("discussion_ingested", {"job_id": job_id, "source_type": source_type, "query": query})
        return {"job_id": job_id, "job": job}

    # ── Processing ────────────────────────────────────────────────────────────────

    def transcribe(self, job_id: int = None, language: str = "auto", **kwargs: Any) -> Dict[str, Any]:
        """
        Execute media content transcription.

        Args:
            job_id (int): Transcription job ID
            language (str): Target language, defaults to "auto" for automatic detection

        Returns:
            Dict: Contains transcription status and result
        """
        if not isinstance(job_id, int):
            return {"error": "job_id must be an integer."}
        if not isinstance(language, str):
            return {"error": "language must be a string."}

        job = self._find_transcription_job(job_id)
        if not job:
            return {"error": f"Transcription job ID {job_id} not found."}

        if job["status"] not in ("pending", "failed"):
            return {"error": f"Transcription job {job_id} is already in {job['status']} status."}

        job["status"] = "transcribing"
        job["language"] = language
        self._log("transcription_started", {"job_id": job_id, "language": language})

        # Simulate transcription process
        result = self._simulate_transcription(job["media_url"], job["media_type"], language)
        
        job["status"] = "transcribed"
        job["transcript"] = result["transcript"]
        job["metadata"] = result["metadata"]
        job["duration_seconds"] = result["duration_seconds"]
        job["processed_at"] = self._current_timestamp()
        
        self._log("transcription_completed", {"job_id": job_id, "duration": result["duration_seconds"], "word_count": result["word_count"]})
        return {"job_id": job_id, "status": "transcribed", "result": result}

    def analyze_discussion(self, job_id: int, max_items: int = 100) -> Dict[str, Any]:
        """
        Analyze discussion content.

        Args:
            job_id (int): Discussion analysis job ID
            max_items (int): Maximum number of items to analyze

        Returns:
            Dict: Contains analysis status and result
        """
        job = self._find_discussion_job(job_id)
        if not job:
            return {"error": f"Discussion analysis job ID {job_id} not found."}

        if job["status"] not in ("pending", "failed"):
            return {"error": f"Discussion analysis job {job_id} is already in {job['status']} status."}

        job["status"] = "analyzing"
        self._log("analysis_started", {"job_id": job_id, "max_items": max_items})

        # Simulate discussion analysis
        result = self._simulate_discussion_analysis(job["query"], job["source_type"], max_items)
        
        job["status"] = "analyzed"
        job["comments"] = result["comments"]
        job["analysis"] = result["analysis"]
        job["item_count"] = result["item_count"]
        job["processed_at"] = self._current_timestamp()
        
        self._log("analysis_completed", {"job_id": job_id, "item_count": result["item_count"]})
        return {"job_id": job_id, "status": "analyzed", "result": result}

    # ── Integrated processing ────────────────────────────────────────────────────────────

    def process_integrated(self, media_job_id: int, discussion_query: str = "") -> Dict[str, Any]:
        """
        Execute integrated processing: transcribe media content and analyze related discussions.

        Args:
            media_job_id (int): Media transcription job ID
            discussion_query (str): [Optional] Discussion query; if empty, keywords extracted from transcript

        Returns:
            Dict: Contains IDs and processing results for both jobs
        """
        media_job = self._find_transcription_job(media_job_id)
        if not media_job:
            return {"error": f"Media transcription job ID {media_job_id} not found."}

        if media_job["status"] != "transcribed":
            return {"error": f"Media transcription job {media_job_id} has not been transcribed yet. Current status: {media_job['status']}"}

        # If no query provided, generate query from transcript
        if not discussion_query and media_job.get("transcript"):
            discussion_query = self._extract_keywords_from_transcript(media_job["transcript"])

        # Create discussion analysis task
        discussion_result = self.ingest_discussion(
            query=discussion_query,
            source_type="reddit_thread",  # Default to Reddit
            source_name="reddit"
        )

        if "error" in discussion_result:
            return discussion_result

        discussion_job_id = discussion_result["job_id"]

        # Analyze discussion
        analysis_result = self.analyze_discussion(discussion_job_id)
        
        self._log("integrated_processing", {
            "media_job_id": media_job_id,
            "discussion_job_id": discussion_job_id,
            "query": discussion_query
        })
        
        return {
            "media_job_id": media_job_id,
            "discussion_job_id": discussion_job_id,
            "transcript_available": media_job["status"] == "transcribed",
            "discussion_available": "analysis" in analysis_result,
        }

    # ── Aggregation and analysis ─────────────────────────────────────────────────────────

    def cross_analyze(self, media_job_ids: List[int], discussion_job_ids: List[int]) -> Dict[str, Any]:
        """
        Cross-modal analysis: integrate transcription content and discussion analysis.

        Args:
            media_job_ids (List[int]): List of media transcription job IDs
            discussion_job_ids (List[int]): List of discussion analysis job IDs

        Returns:
            Dict: Contains comprehensive analysis results
        """
        if not media_job_ids and not discussion_job_ids:
            return {"error": "At least one media job ID or discussion job ID is required."}

        media_data = []
        discussion_data = []

        # Collect media transcription data
        for job_id in media_job_ids:
            job = self._find_transcription_job(job_id)
            if not job:
                return {"error": f"Media transcription job ID {job_id} not found."}
            if job["status"] != "transcribed":
                return {"error": f"Media transcription job {job_id} has not been transcribed yet."}
            media_data.append({
                "job_id": job_id,
                "title": job["title"],
                "transcript": job["transcript"],
                "duration": job["duration_seconds"],
                "language": job["language"],
            })

        # Collect discussion analysis data
        for job_id in discussion_job_ids:
            job = self._find_discussion_job(job_id)
            if not job:
                return {"error": f"Discussion analysis job ID {job_id} not found."}
            if job["status"] != "analyzed":
                return {"error": f"Discussion analysis job {job_id} has not been analyzed yet."}
            discussion_data.append({
                "job_id": job_id,
                "query": job["query"],
                "source": job["source_name"],
                "comments": job["comments"],
                "analysis": job["analysis"],
            })

        # Execute comprehensive analysis
        cross_analysis = self._perform_cross_analysis(media_data, discussion_data)
        
        self._log("cross_analysis_completed", {
            "media_jobs": len(media_data),
            "discussion_jobs": len(discussion_data),
            "key_insights": len(cross_analysis.get("key_insights", []))
        })
        
        return {"cross_analysis": cross_analysis}

    # ── Output generation ───────────────────────────────────────────────────────────

    def generate_summary(
        self,
        media_job_ids: List[int],
        discussion_job_ids: List[int],
        summary_format: str = "markdown",
        title: str = "",
        audience: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis summary.

        Args:
            media_job_ids (List[int]): List of media transcription job IDs
            discussion_job_ids (List[int]): List of discussion analysis job IDs
            summary_format (str): Output format: markdown, bullet, json, executive, technical
            title (str): Summary title
            audience (str): Target audience: general, executive, technical

        Returns:
            Dict: Contains output ID and summary content
        """
        if summary_format not in VALID_SUMMARY_FORMATS:
            return {"error": f"Invalid summary format '{summary_format}'. Must be: {', '.join(VALID_SUMMARY_FORMATS)}"}

        if not media_job_ids and not discussion_job_ids:
            return {"error": "At least one media job ID or discussion job ID is required."}

        # Validate all jobs
        all_jobs = []
        for job_id in media_job_ids:
            job = self._find_transcription_job(job_id)
            if not job:
                return {"error": f"Media transcription job ID {job_id} not found."}
            if job["status"] != "transcribed":
                return {"error": f"Media transcription job {job_id} has not been transcribed yet."}
            all_jobs.append(job)

        for job_id in discussion_job_ids:
            job = self._find_discussion_job(job_id)
            if not job:
                return {"error": f"Discussion analysis job ID {job_id} not found."}
            if job["status"] != "analyzed":
                return {"error": f"Discussion analysis job {job_id} has not been analyzed yet."}
            all_jobs.append(job)

        # Generate output ID
        output_id = self.output_counter
        self.output_counter += 1

        # Generate title
        title = title or f"Cross-modal analysis summary #{output_id}"

        # Generate summary content
        content = self._render_summary(
            media_job_ids,
            discussion_job_ids,
            summary_format,
            title,
            audience
        )
        
        output = {
            "output_id": output_id,
            "title": title,
            "format": summary_format,
            "audience": audience,
            "media_job_ids": media_job_ids,
            "discussion_job_ids": discussion_job_ids,
            "content": content,
            "created_at": self._current_timestamp(),
            "word_count": len(content.split()),
        }
        
        self.summary_outputs.append(output)
        self._log("summary_generated", {
            "output_id": output_id,
            "format": summary_format,
            "media_count": len(media_job_ids),
            "discussion_count": len(discussion_job_ids)
        })
        
        return {"output_id": output_id, "output": output}

    def get_job_status(self, job_id: int) -> Dict[str, Any]:
        """
        Get job status.

        Args:
            job_id (int): Job ID

        Returns:
            Dict: Contains job status information
        """
        # Check transcription jobs first
        job = self._find_transcription_job(job_id)
        if job:
            return {
                "job_type": "transcription",
                "job_id": job_id,
                "status": job["status"],
                "title": job.get("title", ""),
                "processed_at": job.get("processed_at"),
            }

        # Then check discussion jobs
        job = self._find_discussion_job(job_id)
        if job:
            return {
                "job_type": "discussion",
                "job_id": job_id,
                "status": job["status"],
                "query": job.get("query", ""),
                "processed_at": job.get("processed_at"),
            }

        return {"error": f"Job ID {job_id} not found."}

    def list_summaries(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all generated summaries.

        Returns:
            Dict: Contains list of summary abstracts
        """
        summaries = []
        for output in self.summary_outputs:
            summaries.append({
                "output_id": output["output_id"],
                "title": output["title"],
                "format": output["format"],
                "audience": output["audience"],
                "media_count": len(output["media_job_ids"]),
                "discussion_count": len(output["discussion_job_ids"]),
                "created_at": output["created_at"],
                "word_count": output.get("word_count", 0),
            })
        return {"summaries": summaries}

    # ── Helper methods ───────────────────────────────────────────────────────────

    def _find_transcription_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Find transcription job by ID"""
        for job in self.transcription_jobs:
            if job["job_id"] == job_id:
                return job
        return None

    def _find_discussion_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Find discussion job by ID"""
        for job in self.discussion_jobs:
            if job["job_id"] == job_id:
                return job
        return None

    def _simulate_transcription(self, media_url: str, media_type: str, language: str) -> Dict[str, Any]:
        """Simulate speech/video transcription process"""
        random.seed(hash(media_url) % 2**31)

        media_type_map = {
            "audio_m4a": "audio",
            "video_youtube": "YouTube video",
            "video_zoom": "Zoom video",
            "audio_podcast": "podcast audio"
        }

        media_desc = media_type_map.get(media_type, "media content")

        # Simulate generating transcription text
        base_text = f"This is a simulated transcript of {media_desc}. Original content located at: {media_url}"

        # Generate more realistic transcription content
        paragraphs = [
            f"{base_text} This is the first segment, discussing the application of artificial intelligence in media transcription.",
            f"The second segment explores how natural language processing techniques improve transcription accuracy.",
            f"The final segment summarizes the importance of cross-modal analysis and how integrating community discussions enhances depth of understanding.",
        ]

        transcript = "\n\n".join(paragraphs)

        # Simulate metadata
        duration = random.randint(120, 1800)  # 2-30 minutes
        word_count = len(transcript.split())

        return {
            "transcript": transcript,
            "metadata": {
                "media_type": media_type,
                "source_url": media_url,
                "language": language if language != "auto" else "en-US",
                "confidence_score": round(random.uniform(0.85, 0.97), 2),
                "speaker_count": random.randint(1, 5),
                "has_background_noise": random.choice([True, False]),
            },
            "duration_seconds": duration,
            "word_count": word_count,
            "key_phrases": ["artificial intelligence", "speech transcription", "natural language processing", "cross-modal analysis"],
        }

    def _simulate_discussion_analysis(self, query: str, source_type: str, max_items: int) -> Dict[str, Any]:
        """Simulate discussion analysis process"""
        random.seed(hash(query) % 2**31)

        source_map = {
            "reddit_thread": "Reddit",
            "twitter_thread": "Twitter",
            "hn_thread": "Hacker News",
            "zhihu_question": "Zhihu",
            "quora_question": "Quora"
        }

        source_name = source_map.get(source_type, "Community")

        # Simulate generating comments
        comments = []
        item_count = min(max_items, random.randint(10, 50))

        for i in range(item_count):
            comments.append({
                "id": i + 1,
                "author": f"user_{random.randint(1000, 9999)}",
                "text": f"Simulated comment {i+1} about '{query}': This is a simulated reply on {source_name}, discussing related topics.",
                "upvotes": random.randint(0, 1000),
                "timestamp": f"2024-0{random.randint(1,9)}-{random.randint(10,28)}",
                "sentiment": random.choice(["positive", "neutral", "negative"]),
            })

        # Simulate analysis results
        analysis = {
            "query": query,
            "source": source_name,
            "total_comments": item_count,
            "sentiment_distribution": {
                "positive": random.randint(30, 60),
                "neutral": random.randint(20, 50),
                "negative": random.randint(5, 20),
            },
            "top_topics": [
                {"topic": "AI transcription technology", "frequency": random.randint(20, 40)},
                {"topic": "Community feedback", "frequency": random.randint(15, 30)},
                {"topic": "User experience", "frequency": random.randint(10, 25)},
            ],
            "key_insights": [
                f"Community attention to '{query}' topic is relatively high",
                "Users generally focus on transcription accuracy and real-time performance",
                "Cross-platform integration is a major user expectation",
            ],
        }

        return {
            "comments": comments,
            "analysis": analysis,
            "item_count": item_count,
            "query": query,
            "source_type": source_type,
        }

    def _perform_cross_analysis(self, media_data: List[Dict], discussion_data: List[Dict]) -> Dict[str, Any]:
        """Execute cross-modal comprehensive analysis"""

        total_media_duration = sum(m.get("duration", 0) for m in media_data)
        total_discussion_items = sum(d.get("item_count", 0) for d in discussion_data if isinstance(d, dict) and "item_count" in d)

        # Extract all transcription texts
        all_transcripts = [m.get("transcript", "") for m in media_data]
        combined_transcript = "\n\n".join(all_transcripts)

        # Extract all comments
        all_comments = []
        for d in discussion_data:
            if isinstance(d, dict) and "comments" in d:
                all_comments.extend(d["comments"])

        # Generate comprehensive analysis
        cross_analysis = {
            "summary": f"Comprehensive analysis covers {len(media_data)} media sources and {len(discussion_data)} discussion sources",
            "total_media_duration": total_media_duration,
            "total_discussion_items": total_discussion_items,
            "transcript_word_count": len(combined_transcript.split()),
            "key_insights": [
                {
                    "insight": "Significant correlation exists between media content and community discussions",
                    "confidence": 0.88,
                    "supporting_evidence": ["High co-occurrence frequency of keywords", "Consistent sentiment tendencies"]
                },
                {
                    "insight": "Technical topics are discussed more in-depth in professional communities",
                    "confidence": 0.82,
                    "supporting_evidence": ["Hacker News comments have more technical depth", "Reddit discussions focus more on practicality"]
                },
                {
                    "insight": "Cross-modal analysis can reveal information not apparent from single sources",
                    "confidence": 0.91,
                    "supporting_evidence": ["Media transcription reveals details", "Community discussions provide context"]
                }
            ],
            "emerging_themes": [
                "Improvement in AI-assisted transcription accuracy",
                "Growing demand for real-time transcription technology",
                "Importance of multi-language support"
            ],
            "recommendations": [
                "Consider further optimizing transcription accuracy in noisy environments",
                "Consider adding real-time analysis for more community sources",
                "Explore deeper integration of video content and text discussions"
            ],
            "analysis_timestamp": self._current_timestamp(),
        }

        return cross_analysis

    def _render_summary(
        self,
        media_job_ids: List[int],
        discussion_job_ids: List[int],
        fmt: str,
        title: str,
        audience: str
    ) -> str:
        """Render summary content according to the specified format"""
        if fmt == "bullet":
            lines = [f"# {title}", f"Target audience: {audience}", ""]
            lines.append("## Included tasks:")
            for job_id in media_job_ids:
                job = self._find_transcription_job(job_id)
                if job:
                    lines.append(f"- Media transcription task {job_id}: {job.get('title', '')}")
            for job_id in discussion_job_ids:
                job = self._find_discussion_job(job_id)
                if job:
                    lines.append(f"- Discussion analysis task {job_id}: {job.get('query', '')}")
            lines.append("")
            lines.append("## Key findings:")
            lines.append("- Media content is highly correlated with community discussions")
            lines.append("- Cross-modal analysis provides a more comprehensive perspective")
            lines.append("- Technical topics are discussed in greater depth in professional communities")
            return "\n".join(lines)

        elif fmt == "json":
            data = {
                "title": title,
                "audience": audience,
                "media_jobs": media_job_ids,
                "discussion_jobs": discussion_job_ids,
                "generated_at": self._current_timestamp(),
                "summary": "Cross-modal analysis summary report"
            }
            return json.dumps(data, ensure_ascii=False, indent=2)

        elif fmt == "executive":
            lines = [
                f"# Executive summary: {title}",
                "",
                "## Overview",
                f"This report integrates analysis results from {len(media_job_ids)} media sources and {len(discussion_job_ids)} community discussion sources.",
                "",
                "## Key insights",
                "1. Media content is highly consistent with community feedback, validating broad acceptance of main viewpoints",
                "2. Technical implementation details receive more in-depth discussion in professional communities",
                "3. Users expect more intelligent cross-platform integration features",
                "",
                "## Recommended actions",
                "- Prioritize improving audio quality detection algorithms",
                "- Expand community monitoring scope to emerging platforms",
                "- Develop a real-time analytics dashboard",
            ]
            return "\n".join(lines)

        elif fmt == "technical":
            lines = [
                f"# Technical analysis report: {title}",
                "",
                "## Data source statistics",
                f"- Media transcription tasks: {len(media_job_ids)}",
                f"- Discussion analysis tasks: {len(discussion_job_ids)}",
                "",
                "## Analysis methods",
                "- Natural language processing: text transcription and keyword extraction",
                "- Sentiment analysis: positive/negative community feedback statistics",
                "- Topic modeling: identifying trending discussion topics",
                "",
                "## Technical findings",
                "- Average transcription accuracy: 92.5%",
                "- Sentiment distribution: Positive 65%, Neutral 25%, Negative 10%",
                "- Main technical topics: AI transcription, real-time processing, multi-language support",
            ]
            return "\n".join(lines)

        else:  # markdown default format
            lines = [
                f"# {title}",
                "",
                "## Report information",
                f"- **Generated at**: {self._current_timestamp()}",
                f"- **Target audience**: {audience}",
                f"- **Format**: {fmt}",
                "",
                "## Data sources",
                f"- **Media transcription tasks**: {len(media_job_ids)}",
                f"- **Discussion analysis tasks**: {len(discussion_job_ids)}",
                "",
                "## Comprehensive analysis",
                "This report integrates speech/video transcription content with relevant community discussion data through cross-modal analysis methods.",
                "",
                "### Key findings",
                "1. Core viewpoints from media content are validated and extended in community discussions",
                "2. Technical implementation details are the primary focus of professional communities",
                "3. User demand for real-time performance and accuracy continues to grow",
                "",
                "### Recommendations",
                "- Optimize transcription algorithms to accommodate different audio environments",
                "- Establish a more comprehensive community feedback monitoring mechanism",
                "- Explore AI-assisted content quality assessment",
                "",
                "---",
                "*End of report*",
            ]
            return "\n".join(lines)

    def _extract_keywords_from_transcript(self, transcript: str) -> str:
        """Extract keywords from transcript text as query"""

        # Simulate keyword extraction
        keywords_pool = [
            "artificial intelligence", "speech transcription", "video analysis", "natural language processing",
            "machine learning", "deep learning", "community discussion", "user experience",
            "real-time processing", "multimodal analysis", "technology trends", "industry applications"
        ]
        
        selected = random.sample(keywords_pool, min(3, len(keywords_pool)))
        return " ".join(selected)

    def _map_source_type(self, source_type: str) -> str:
        """Map source type to source name"""
        mapping = {
            "reddit_thread": "reddit",
            "twitter_thread": "twitter",
            "hn_thread": "hackernews",
            "zhihu_question": "zhihu",
            "quora_question": "quora"
        }
        return mapping.get(source_type, "general")

    def _current_timestamp(self) -> str:
        """Generate current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log(self, event: str, detail: Dict) -> None:
        """Record processing log entry"""
        self.processing_log.append({
            "event": event,
            "detail": detail,
            "timestamp": self._current_timestamp()
        })
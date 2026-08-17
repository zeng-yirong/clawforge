from copy import deepcopy
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from collections import Counter
import json

DEFAULT_STATE = {
    "transcription_tasks": [],
    "summarization_jobs": [],
    "source_files": {},
    "transcription_results": {},
    "summarization_results": {},
    "task_counter": 1,
    "job_counter": 1,
    "community_discussions": {},
    "knowledge_base": {
        "extracted_entities": [],
        "key_topics": [],
        "action_items": []
    }
}

VALID_TASK_STATUSES = ("pending", "transcribing", "completed", "failed", "cancelled")
VALID_JOB_STATUSES = ("pending", "analyzing", "summarizing", "completed", "failed")
VALID_SOURCE_TYPES = ("audio_m4a", "video_youtube", "audio_mp3", "video_mp4")
VALID_SUMMARY_FORMATS = ("bulleted", "paragraph", "executive", "detailed")
VALID_ENTITY_TYPES = ("person", "organization", "location", "date", "topic", "action_item")


class CrossModalConversationalEnv:
    """
    A cross-modal transcription and summarization environment.
    
    This environment handles audio/video transcription combined with community
    discussion analysis to extract core information. It manages the full pipeline:
    source ingestion → transcription → community context integration → 
    summarization with entity extraction and key point identification.
    
    Attributes:
        transcription_tasks (List[Dict]): All transcription tasks with status.
        summarization_jobs (List[Dict]): All summarization jobs with status.
        source_files (Dict[str, Dict]): Source metadata keyed by source_id.
        transcription_results (Dict[str, Dict]): Transcription results keyed by task_id.
        summarization_results (Dict[str, Dict]): Summarization results keyed by job_id.
        task_counter (int): Auto-incrementing task ID counter.
        job_counter (int): Auto-incrementing job ID counter.
        community_discussions (Dict[str, List]): Community discussions by topic.
        knowledge_base (Dict[str, Any]): Extracted knowledge across all jobs.
    """

    def __init__(self):
        
        self.transcription_tasks: List[Dict[str, Any]]
        self.summarization_jobs: List[Dict[str, Any]]
        self.source_files: Dict[str, Dict[str, Any]]
        self.transcription_results: Dict[str, Dict[str, Any]]
        self.summarization_results: Dict[str, Dict[str, Any]]
        self.task_counter: int
        self.job_counter: int
        self.community_discussions: Dict[str, List]
        self.knowledge_base: Dict[str, Any]
        self._api_description = (
            "This tool manages cross-modal transcription pipelines from audio/video to text, "
            "integrates community discussions for context, and produces structured summaries "
            "with entity extraction and key information identification."
        )
        self._load_scenario({})

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.transcription_tasks = scenario.get("transcription_tasks", DEFAULT_STATE_COPY["transcription_tasks"])
        self.summarization_jobs = scenario.get("summarization_jobs", DEFAULT_STATE_COPY["summarization_jobs"])
        self.source_files = scenario.get("source_files", DEFAULT_STATE_COPY["source_files"])
        self.transcription_results = scenario.get("transcription_results", DEFAULT_STATE_COPY["transcription_results"])
        self.summarization_results = scenario.get("summarization_results", DEFAULT_STATE_COPY["summarization_results"])
        self.task_counter = scenario.get("task_counter", DEFAULT_STATE_COPY["task_counter"])
        self.job_counter = scenario.get("job_counter", DEFAULT_STATE_COPY["job_counter"])
        self.community_discussions = scenario.get("community_discussions", DEFAULT_STATE_COPY["community_discussions"])
        self.knowledge_base = scenario.get("knowledge_base", DEFAULT_STATE_COPY["knowledge_base"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including transcription tasks,
                  summarization jobs, source files, results, counters, and knowledge base.
        """
        return {
            "transcription_tasks": self.transcription_tasks,
            "summarization_jobs": self.summarization_jobs,
            "source_files": self.source_files,
            "transcription_results": self.transcription_results,
            "summarization_results": self.summarization_results,
            "task_counter": self.task_counter,
            "job_counter": self.job_counter,
            "community_discussions": self.community_discussions,
            "knowledge_base": self.knowledge_base,
        }

    # ── Source Management ─────────────────────────────────────────────────

    def add_source(
        self,
        source_url: str,
        source_type: str,
        title: str,
        duration: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a new audio/video source for processing.

        Args:
            source_url (str): URL or path to the source file (YouTube URL or .m4a path).
            source_type (str): Type of source - "audio_m4a", "video_youtube", etc.
            title (str): Display title for the source.
            duration (int): [Optional] Duration in seconds.
            metadata (Dict): [Optional] Additional metadata:
                - language (str): Primary language code.
                - speakers (List[str]): Names of known speakers.
                - topics (List[str]): Expected topic tags.
                - quality (str): "low", "medium", or "high".

        Returns:
            source_id (str): Unique source identifier.
            source_info (Dict): The registered source record.
        """
        if not source_url.strip():
            return {"error": "Source URL cannot be empty."}
        if source_type not in VALID_SOURCE_TYPES:
            return {"error": f"Invalid source type '{source_type}'. Must be one of: {', '.join(VALID_SOURCE_TYPES)}"}
        if not title.strip():
            return {"error": "Title cannot be empty."}

        source_id = f"src_{self.task_counter}"
        self.task_counter += 1

        metadata = metadata or {}
        source_info = {
            "source_id": source_id,
            "source_url": source_url,
            "source_type": source_type,
            "title": title,
            "duration": duration,
            "metadata": {
                "language": metadata.get("language", "en"),
                "speakers": metadata.get("speakers", []),
                "topics": metadata.get("topics", []),
                "quality": metadata.get("quality", "medium"),
                "added_at": datetime.now().isoformat(),
            },
            "status": "registered",
            "transcription_task_id": None,
            "summarization_job_id": None,
        }
        self.source_files[source_id] = source_info
        return {"source_id": source_id, "source_info": source_info}

    def list_sources(self, status: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all registered sources, optionally filtered by status.

        Args:
            status (str): [Optional] Filter by source status.

        Returns:
            sources (List[Dict]): Matching source summaries.
        """
        sources = list(self.source_files.values())
        if status:
            sources = [s for s in sources if s.get("status") == status]
        summaries = [{
            "source_id": s["source_id"],
            "title": s["title"],
            "source_type": s["source_type"],
            "status": s.get("status", "unknown"),
            "duration": s.get("duration"),
            "language": s.get("metadata", {}).get("language", "unknown"),
        } for s in sources]
        return {"sources": summaries}

    # ── Transcription Pipeline ────────────────────────────────────────────

    def start_transcription(
        self,
        source_id: str,
        language: Optional[str] = None,
        speaker_diarization: bool = True,
        timestamping: bool = True,
    ) -> Dict[str, Any]:
        """
        Start a transcription task for a registered source.

        Args:
            source_id (str): The source to transcribe.
            language (str): [Optional] Override language for transcription.
            speaker_diarization (bool): Whether to identify different speakers.
            timestamping (bool): Whether to generate word-level timestamps.

        Returns:
            task_id (str): Unique transcription task identifier.
            task_info (Dict): The created task record.
        """
        if source_id not in self.source_files:
            return {"error": f"Source '{source_id}' not found."}
        
        source = self.source_files[source_id]
        if source.get("transcription_task_id"):
            return {"error": f"Source '{source_id}' already has transcription task {source['transcription_task_id']}."}

        task_id = f"trans_{self.task_counter}"
        self.task_counter += 1

        task = {
            "task_id": task_id,
            "source_id": source_id,
            "language": language or source.get("metadata", {}).get("language", "en"),
            "speaker_diarization": speaker_diarization,
            "timestamping": timestamping,
            "status": "pending",
            "progress": 0.0,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error_message": None,
        }
        self.transcription_tasks.append(task)
        source["transcription_task_id"] = task_id
        source["status"] = "transcribing"
        
        return {"task_id": task_id, "task_info": task}

    def update_transcription_status(
        self,
        task_id: str,
        status: str,
        progress: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update the status of a transcription task.

        Args:
            task_id (str): The transcription task to update.
            status (str): New status - must be valid.
            progress (float): [Optional] Progress percentage (0-100).
            error_message (str): [Optional] Error details if failed.

        Returns:
            task_info (Dict): Updated task information.
        """
        task = self._find_transcription_task(task_id)
        if not task:
            return {"error": f"Transcription task '{task_id}' not found."}
        if status not in VALID_TASK_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_TASK_STATUSES)}"}

        task["status"] = status
        if progress is not None:
            task["progress"] = max(0.0, min(100.0, progress))
        
        if status == "transcribing" and not task["started_at"]:
            task["started_at"] = datetime.now().isoformat()
        elif status in ["completed", "failed", "cancelled"]:
            task["completed_at"] = datetime.now().isoformat()
            if error_message:
                task["error_message"] = error_message

        return {"task_info": task}

    def submit_transcription_result(
        self,
        task_id: str,
        transcript_text: str,
        segments: Optional[List[Dict]] = None,
        word_timestamps: Optional[List[Dict]] = None,
        speaker_labels: Optional[Dict] = None,
        confidence_scores: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Submit the completed transcription result.

        Args:
            task_id (str): The completed transcription task.
            transcript_text (str): Full transcript text.
            segments (List[Dict]): [Optional] Timestamped segments.
            word_timestamps (List[Dict]): [Optional] Word-level timestamps.
            speaker_labels (Dict): [Optional] Speaker identification data.
            confidence_scores (Dict): [Optional] Confidence metrics.

        Returns:
            result_id (str): Unique result identifier.
            transcript_summary (Dict): Summary of the transcription.
        """
        task = self._find_transcription_task(task_id)
        if not task:
            return {"error": f"Transcription task '{task_id}' not found."}
        if task["status"] != "completed":
            return {"error": f"Task '{task_id}' is {task['status']}, must be 'completed' to submit results."}
        if not transcript_text.strip():
            return {"error": "Transcript text cannot be empty."}

        source_id = task["source_id"]
        source = self.source_files.get(source_id)
        if not source:
            return {"error": f"Source '{source_id}' not found."}

        # Auto-extract some metadata
        word_count = len(transcript_text.split())
        estimated_duration = source.get("duration") or int(word_count / 2.5)  # approximate

        result = {
            "result_id": f"trans_result_{self.job_counter}",
            "task_id": task_id,
            "source_id": source_id,
            "transcript_text": transcript_text,
            "segments": segments or [],
            "word_timestamps": word_timestamps or [],
            "speaker_labels": speaker_labels or {},
            "confidence_scores": confidence_scores or {"overall": 0.85, "segments": []},
            "metadata": {
                "word_count": word_count,
                "character_count": len(transcript_text),
                "estimated_duration": estimated_duration,
                "language": task["language"],
                "has_speakers": bool(speaker_labels),
                "has_timestamps": bool(word_timestamps),
                "generated_at": datetime.now().isoformat(),
            }
        }
        self.job_counter += 1

        self.transcription_results[task_id] = result
        source["status"] = "transcribed"

        summary = {
            "result_id": result["result_id"],
            "source_title": source["title"],
            "word_count": word_count,
            "language": task["language"],
            "speaker_count": len(speaker_labels) if speaker_labels else 0,
            "segment_count": len(segments) if segments else 0,
        }
        
        return {"result_id": result["result_id"], "transcript_summary": summary}

    def get_transcription_result(self, task_id: str) -> Dict[str, Any]:
        """
        Retrieve transcription result by task ID.

        Args:
            task_id (str): The transcription task ID.

        Returns:
            result (Dict): Full transcription result including text and metadata.
        """
        if task_id not in self.transcription_results:
            return {"error": f"Transcription result for task '{task_id}' not found."}
        
        result = self.transcription_results[task_id]
        # Don't return full text for large transcripts in basic result
        truncated_text = result["transcript_text"]
        if len(truncated_text) > 1000:
            truncated_text = truncated_text[:1000] + "... [truncated]"
        
        return {
            "result": {
                **result,
                "transcript_text": truncated_text,
            },
            "full_text_length": len(result["transcript_text"])
        }

    # ── Community Discussion Integration ──────────────────────────────────

    def add_community_discussions(
        self,
        topic: str,
        discussions: List[Dict[str, Any]],
        source_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Add community discussions related to topics from transcribed sources.

        Args:
            topic (str): Main topic of the discussions.
            discussions (List[Dict]): List of discussion entries, each with:
                - content (str): Discussion text.
                - source (str): Where it came from.
                - relevance_score (float): 0-1 relevance to topic.
                - sentiment (str): "positive", "negative", or "neutral".
            source_ids (List[str]): [Optional] Source IDs this relates to.

        Returns:
            topic (str): The discussion topic.
            added_count (int): Number of discussions added.
            related_sources (List[str]): Sources linked to this discussion.
        """
        if not topic.strip():
            return {"error": "Topic cannot be empty."}
        if not discussions:
            return {"error": "Discussions list cannot be empty."}

        if topic not in self.community_discussions:
            self.community_discussions[topic] = []

        valid_discussions = []
        for i, disc in enumerate(discussions):
            if not isinstance(disc, dict):
                continue
            if not disc.get("content", "").strip():
                continue
            disc_entry = {
                "discussion_id": f"disc_{len(self.community_discussions[topic]) + i + 1}",
                "content": disc.get("content", ""),
                "source": disc.get("source", "unknown"),
                "relevance_score": min(1.0, max(0.0, disc.get("relevance_score", 0.5))),
                "sentiment": disc.get("sentiment", "neutral"),
                "added_at": datetime.now().isoformat(),
                "related_sources": source_ids or [],
            }
            valid_discussions.append(disc_entry)

        self.community_discussions[topic].extend(valid_discussions)
        
        return {
            "topic": topic,
            "added_count": len(valid_discussions),
            "related_sources": source_ids or [],
            "total_discussions": len(self.community_discussions[topic]),
        }

    def get_community_context(
        self,
        topic: str,
        min_relevance: float = 0.3,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Retrieve community discussions for a topic with relevance filtering.

        Args:
            topic (str): Topic to get discussions for.
            min_relevance (float): Minimum relevance score (0-1).
            limit (int): Maximum number of discussions to return.

        Returns:
            topic (str): The requested topic.
            discussions (List[Dict]): Filtered and sorted discussions.
            relevance_stats (Dict): Statistics about relevance scores.
        """
        if topic not in self.community_discussions:
            return {"error": f"No discussions found for topic '{topic}'."}

        all_discussions = self.community_discussions[topic]
        filtered = [d for d in all_discussions if d["relevance_score"] >= min_relevance]
        filtered.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        if limit > 0:
            filtered = filtered[:limit]

        if not filtered:
            return {
                "topic": topic,
                "discussions": [],
                "relevance_stats": {
                    "total": len(all_discussions),
                    "filtered": 0,
                    "min_relevance": min_relevance,
                    "average_relevance": 0.0,
                }
            }

        avg_relevance = sum(d["relevance_score"] for d in filtered) / len(filtered)
        sentiment_counts = {}
        for d in filtered:
            sentiment_counts[d["sentiment"]] = sentiment_counts.get(d["sentiment"], 0) + 1

        return {
            "topic": topic,
            "discussions": filtered,
            "relevance_stats": {
                "total": len(all_discussions),
                "filtered": len(filtered),
                "min_relevance": min_relevance,
                "average_relevance": round(avg_relevance, 3),
                "sentiment_distribution": sentiment_counts,
            }
        }

    # ── Summarization Pipeline ────────────────────────────────────────────

    def start_summarization_job(
        self,
        task_id: str,
        summary_format: str = "bulleted",
        include_community_context: bool = True,
        extract_entities: bool = True,
        max_length: Optional[int] = None,
        custom_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Start a summarization job for a transcribed source with community context.

        Args:
            task_id (str): Transcription task to summarize.
            summary_format (str): Output format - "bulleted", "paragraph", etc.
            include_community_context (bool): Whether to incorporate community discussions.
            extract_entities (bool): Whether to extract named entities.
            max_length (int): [Optional] Maximum summary length in words.
            custom_prompt (str): [Optional] Custom instructions for summarization.

        Returns:
            job_id (str): Unique summarization job identifier.
            job_info (Dict): The created job record.
        """
        if task_id not in self.transcription_results:
            return {"error": f"No transcription result found for task '{task_id}'."}
        if summary_format not in VALID_SUMMARY_FORMATS:
            return {"error": f"Invalid summary format '{summary_format}'. Must be one of: {', '.join(VALID_SUMMARY_FORMATS)}"}

        job_id = f"summ_{self.job_counter}"
        self.job_counter += 1

        transcript_result = self.transcription_results[task_id]
        source_id = transcript_result["source_id"]
        source = self.source_files.get(source_id, {})

        # Identify topics from transcription and source metadata
        topics = source.get("metadata", {}).get("topics", [])
        if not topics:
            transcript_text = transcript_result["transcript_text"][:500]
            topics = self._extract_topics_from_text(transcript_text)

        job = {
            "job_id": job_id,
            "task_id": task_id,
            "source_id": source_id,
            "summary_format": summary_format,
            "include_community_context": include_community_context,
            "extract_entities": extract_entities,
            "max_length": max_length,
            "custom_prompt": custom_prompt,
            "topics": topics,
            "status": "pending",
            "progress": 0.0,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error_message": None,
        }
        self.summarization_jobs.append(job)
        
        if source_id in self.source_files:
            self.source_files[source_id]["summarization_job_id"] = job_id
            self.source_files[source_id]["status"] = "summarizing"

        return {"job_id": job_id, "job_info": job}

    def update_summarization_status(
        self,
        job_id: str,
        status: str,
        progress: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update the status of a summarization job.

        Args:
            job_id (str): The summarization job to update.
            status (str): New status - must be valid.
            progress (float): [Optional] Progress percentage (0-100).
            error_message (str): [Optional] Error details if failed.

        Returns:
            job_info (Dict): Updated job information.
        """
        job = self._find_summarization_job(job_id)
        if not job:
            return {"error": f"Summarization job '{job_id}' not found."}
        if status not in VALID_JOB_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_JOB_STATUSES)}"}

        job["status"] = status
        if progress is not None:
            job["progress"] = max(0.0, min(100.0, progress))
        
        if status == "analyzing" and not job["started_at"]:
            job["started_at"] = datetime.now().isoformat()
        elif status in ["completed", "failed"]:
            job["completed_at"] = datetime.now().isoformat()
            if error_message:
                job["error_message"] = error_message

        return {"job_info": job}

    def submit_summarization_result(
        self,
        job_id: str,
        summary_text: str,
        key_points: List[str],
        entities: Optional[List[Dict]] = None,
        community_insights: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Submit the completed summarization result.

        Args:
            job_id (str): The completed summarization job.
            summary_text (str): Generated summary text.
            key_points (List[str]): Key points extracted.
            entities (List[Dict]): [Optional] Extracted named entities.
            community_insights (List[str]): [Optional] Insights from community discussions.
            metadata (Dict): [Optional] Additional metadata about the summarization.

        Returns:
            result_id (str): Unique result identifier.
            summary_overview (Dict): Overview of the summary.
        """
        job = self._find_summarization_job(job_id)
        if not job:
            return {"error": f"Summarization job '{job_id}' not found."}
        if job["status"] != "completed":
            return {"error": f"Job '{job_id}' is {job['status']}, must be 'completed' to submit results."}
        if not summary_text.strip():
            return {"error": "Summary text cannot be empty."}
        if not key_points:
            return {"error": "At least one key point is required."}

        task_id = job["task_id"]
        transcript_result = self.transcription_results.get(task_id, {})
        source_id = job["source_id"]
        source = self.source_files.get(source_id, {})

        # Update knowledge base with extracted entities
        if entities:
            for entity in entities:
                if not isinstance(entity, dict):
                    continue
                if entity.get("type") not in VALID_ENTITY_TYPES:
                    continue
                entity_entry = {
                    **entity,
                    "source_job_id": job_id,
                    "source_title": source.get("title", "Unknown"),
                    "extracted_at": datetime.now().isoformat(),
                }
                self.knowledge_base["extracted_entities"].append(entity_entry)

        # Update key topics
        for topic in job.get("topics", []):
            if topic not in self.knowledge_base["key_topics"]:
                self.knowledge_base["key_topics"].append(topic)

        # Find action items
        action_items = self._extract_action_items(summary_text, key_points)
        for action in action_items:
            self.knowledge_base["action_items"].append({
                "action": action,
                "source_job_id": job_id,
                "source_title": source.get("title", "Unknown"),
                "priority": "medium",
            })

        result = {
            "result_id": f"summ_result_{self.job_counter}",
            "job_id": job_id,
            "task_id": task_id,
            "source_id": source_id,
            "summary_text": summary_text,
            "key_points": key_points,
            "entities": entities or [],
            "community_insights": community_insights or [],
            "action_items": action_items,
            "metadata": metadata or {
                "summary_format": job["summary_format"],
                "word_count": len(summary_text.split()),
                "key_points_count": len(key_points),
                "entities_count": len(entities) if entities else 0,
                "has_community_context": job["include_community_context"],
                "generated_at": datetime.now().isoformat(),
            }
        }
        self.job_counter += 1

        self.summarization_results[job_id] = result
        
        if source_id in self.source_files:
            self.source_files[source_id]["status"] = "summarized"

        overview = {
            "result_id": result["result_id"],
            "source_title": source.get("title", "Unknown"),
            "summary_length": len(summary_text),
            "key_points_count": len(key_points),
            "entities_count": len(entities) if entities else 0,
            "action_items": action_items,
        }
        
        return {"result_id": result["result_id"], "summary_overview": overview}

    def get_summarization_result(self, job_id: str) -> Dict[str, Any]:
        """
        Retrieve summarization result by job ID.

        Args:
            job_id (str): The summarization job ID.

        Returns:
            result (Dict): Full summarization result.
        """
        if job_id not in self.summarization_results:
            return {"error": f"Summarization result for job '{job_id}' not found."}
        
        return {"result": self.summarization_results[job_id]}

    def get_comprehensive_report(self, source_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive report for a source including transcription and summary.

        Args:
            source_id (str): The source to report on.

        Returns:
            report (Dict): Integrated report with all available information.
        """
        if source_id not in self.source_files:
            return {"error": f"Source '{source_id}' not found."}

        source = self.source_files[source_id]
        task_id = source.get("transcription_task_id")
        job_id = source.get("summarization_job_id")

        transcription_result = self.transcription_results.get(task_id) if task_id else None
        summarization_result = self.summarization_results.get(job_id) if job_id else None

        # Gather community discussions for relevant topics
        community_context = {}
        topics = source.get("metadata", {}).get("topics", [])
        if topics:
            for topic in topics[:3]:  # Limit to top 3 topics
                if topic in self.community_discussions:
                    discussions = self.community_discussions[topic][:5]
                    community_context[topic] = {
                        "discussion_count": len(discussions),
                        "sample_discussions": discussions,
                    }

        report = {
            "source_info": {
                "title": source.get("title", "Unknown"),
                "type": source.get("source_type", "unknown"),
                "status": source.get("status", "unknown"),
                "language": source.get("metadata", {}).get("language", "unknown"),
            },
            "transcription": {
                "has_transcription": transcription_result is not None,
                "word_count": transcription_result.get("metadata", {}).get("word_count", 0) if transcription_result else 0,
                "language": transcription_result.get("metadata", {}).get("language", "unknown") if transcription_result else "unknown",
            } if transcription_result else {"has_transcription": False},
            "summarization": {
                "has_summary": summarization_result is not None,
                "format": summarization_result.get("metadata", {}).get("summary_format") if summarization_result else None,
                "key_points_count": len(summarization_result.get("key_points", [])) if summarization_result else 0,
                "action_items": summarization_result.get("action_items", []) if summarization_result else [],
            } if summarization_result else {"has_summary": False},
            "community_context": {
                "topics_covered": list(community_context.keys()),
                "total_discussions": sum(ctx["discussion_count"] for ctx in community_context.values()),
                "by_topic": community_context,
            } if community_context else {"has_community_context": False},
            "knowledge_extraction": {
                "entities_extracted": len([e for e in self.knowledge_base["extracted_entities"] 
                                         if e.get("source_job_id") == job_id]) if job_id else 0,
                "related_topics": [t for t in topics if t in self.knowledge_base["key_topics"]],
            },
            "pipeline_status": {
                "source_registered": True,
                "transcription_completed": transcription_result is not None,
                "summarization_completed": summarization_result is not None,
                "community_context_integrated": bool(community_context),
            }
        }

        return {"report": report}

    # ── Knowledge Base Operations ─────────────────────────────────────────

    def query_knowledge_base(
        self,
        query: str,
        entity_type: Optional[str] = None,
        min_confidence: float = 0.5,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Query the accumulated knowledge base for information.

        Args:
            query (str): Search query string.
            entity_type (str): [Optional] Filter by entity type.
            min_confidence (float): [Optional] Minimum confidence for entities.
            limit (int): [Optional] Maximum results to return.

        Returns:
            query_results (Dict): Search results from knowledge base.
        """
        query_lower = query.lower()
        results = {
            "entities": [],
            "topics": [],
            "action_items": [],
        }

        # Search entities
        for entity in self.knowledge_base["extracted_entities"]:
            if not isinstance(entity, dict):
                continue
            if entity_type and entity.get("type") != entity_type:
                continue
            if entity.get("confidence", 1.0) < min_confidence:
                continue
            
            entity_text = entity.get("text", "").lower()
            entity_type_str = entity.get("type", "").lower()
            
            if (query_lower in entity_text or 
                query_lower in entity_type_str or
                (entity.get("source_title") and query_lower in entity.get("source_title", "").lower())):
                
                results["entities"].append(entity)
                if len(results["entities"]) >= limit:
                    break

        # Search topics
        for topic in self.knowledge_base["key_topics"]:
            if query_lower in topic.lower():
                results["topics"].append({
                    "topic": topic,
                    "occurrences": sum(1 for j in self.summarization_jobs if query_lower in str(j.get("topics", [])).lower()),
                })
                if len(results["topics"]) >= limit:
                    break

        # Search action items
        for action in self.knowledge_base["action_items"]:
            if not isinstance(action, dict):
                continue
            action_text = action.get("action", "").lower()
            if query_lower in action_text:
                results["action_items"].append(action)
                if len(results["action_items"]) >= limit:
                    break

        return {
            "query": query,
            "entity_type_filter": entity_type,
            "results": results,
            "counts": {
                "entities": len(results["entities"]),
                "topics": len(results["topics"]),
                "action_items": len(results["action_items"]),
            }
        }

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the accumulated knowledge base.

        Returns:
            stats (Dict): Knowledge base statistics.
        """
        entities_by_type = {}
        for entity in self.knowledge_base["extracted_entities"]:
            if not isinstance(entity, dict):
                continue
            etype = entity.get("type", "unknown")
            entities_by_type[etype] = entities_by_type.get(etype, 0) + 1

        action_items_by_priority = {}
        for action in self.knowledge_base["action_items"]:
            if not isinstance(action, dict):
                continue
            priority = action.get("priority", "medium")
            action_items_by_priority[priority] = action_items_by_priority.get(priority, 0) + 1

        sources_processed = len([s for s in self.source_files.values() 
                                if s.get("status") == "summarized"])

        return {
            "knowledge_base_stats": {
                "total_entities": len(self.knowledge_base["extracted_entities"]),
                "entities_by_type": entities_by_type,
                "total_topics": len(self.knowledge_base["key_topics"]),
                "top_topics": self.knowledge_base["key_topics"][:10],
                "total_action_items": len(self.knowledge_base["action_items"]),
                "action_items_by_priority": action_items_by_priority,
                "sources_processed": sources_processed,
                "total_summarization_jobs": len([j for j in self.summarization_jobs 
                                               if j.get("status") == "completed"]),
                "community_discussion_topics": len(self.community_discussions),
                "total_discussions": sum(len(d) for d in self.community_discussions.values()),
            }
        }

    # ── Helper Methods ────────────────────────────────────────────────────

    def _find_transcription_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Find a transcription task by ID. Returns None if not found."""
        for task in self.transcription_tasks:
            if task["task_id"] == task_id:
                return task
        return None

    def _find_summarization_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Find a summarization job by ID. Returns None if not found."""
        for job in self.summarization_jobs:
            if job["job_id"] == job_id:
                return job
        return None

    def _extract_topics_from_text(self, text: str, max_topics: int = 5) -> List[str]:
        """Simple topic extraction from text (simplified for demo)."""
        _STOP_WORDS = {
            "the", "and", "for", "with", "that", "this", "have", "from",
            "about", "after", "also", "been", "being", "can", "could",
            "does", "each", "even", "first", "going", "into", "its",
            "just", "like", "make", "many", "more", "most", "much",
            "must", "need", "only", "other", "over", "part", "same",
            "said", "should", "some", "such", "than", "then", "their",
            "them", "they", "there", "these", "thing", "things",
            "through", "very", "well", "were", "what", "when",
            "which", "will", "would",
        }
        words = [
            w.lower() for w in text.split()
            if len(w) > 4 and w.lower() not in _STOP_WORDS and w.isalpha()
        ]

        word_counts = Counter(words)
        # Require at least 2 occurrences to filter noise
        candidates = [(w, c) for w, c in word_counts.most_common() if c >= 2]
        topics = [word for word, _ in candidates[:max_topics]]

        return topics

    def _extract_action_items(self, summary_text: str, key_points: List[str]) -> List[str]:
        """Extract potential action items from summary and key points."""
        action_keywords = ["should", "must", "need to", "requires", "action", "next step", "follow up", "implement"]
        combined_text = summary_text.lower() + " " + " ".join(kp.lower() for kp in key_points)
        
        sentences = combined_text.split('. ')
        action_items = []
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in action_keywords):
                # Clean up the sentence for display
                clean_sentence = sentence.strip().capitalize()
                if len(clean_sentence) > 0:
                    action_items.append(clean_sentence)
        
        return list(set(action_items))[:5]  # Deduplicate and limit

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })
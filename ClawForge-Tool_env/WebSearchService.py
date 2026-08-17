import random
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

DEFAULT_STATE: Dict[str, Any] = {
    "show_snippet": True,
}

_SIMULATED_SITES = [
    ("Wikipedia", "https://en.wikipedia.org/wiki/{keyword}"),
    ("GitHub", "https://github.com/topics/{keyword}"),
    ("Stack Overflow", "https://stackoverflow.com/questions/tagged/{keyword}"),
    ("arXiv", "https://arxiv.org/search/?query={keyword}"),
    ("Medium", "https://medium.com/tag/{keyword}"),
    ("Reddit", "https://www.reddit.com/r/{keyword}/"),
    ("Hacker News", "https://news.ycombinator.com/item?id={id}"),
    ("Google Scholar", "https://scholar.google.com/scholar?q={keyword}"),
    ("PyPI", "https://pypi.org/search/?q={keyword}"),
    ("npm", "https://www.npmjs.com/search?q={keyword}"),
    ("IEEE Xplore", "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={keyword}"),
    ("PubMed", "https://pubmed.ncbi.nlm.nih.gov/?term={keyword}"),
]


class WebSearchAPI:
    def __init__(self):
        self.show_snippet: bool
        self._search_history: List[Dict[str, Any]]
        self._bookmarks: List[Dict[str, Any]]
        self._filters: List[Dict[str, str]]
        self._config: Dict[str, Any]
        self._api_description = "This tool belongs to the Web Search API category. It provides functions to search the web and browse search results."
        self._random = random.Random(337)
        self._rng = random.Random(1053)
        self._search_history = []
        self._bookmarks = []
        self._filters = []
        self._config = deepcopy(DEFAULT_STATE)
        self._load_scenario({})

    def _load_scenario(self, initial_config: dict, long_context: bool = False):
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.show_snippet = initial_config.get("show_snippet", DEFAULT_STATE_COPY["show_snippet"])

    def _timestamp(self) -> str:
        return datetime.now().isoformat()

    # ==================== Core Methods ====================

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables.
        """
        return {
            "show_snippet": self.show_snippet,
            "search_history": self._search_history,
            "bookmarks": self._bookmarks,
            "filters": self._filters,
            "config": self._config,
        }

    def search_engine_query(
        self,
        keywords: str,
        max_results: Optional[int] = 10,
        region: Optional[str] = "wt-wt",
    ) -> list:
        """
        Query the search engine for the provided keywords and region.
        Returns simulated search results for offline RL training.

        Args:
            keywords (str): The keywords to search for.
            max_results (int, optional): Maximum number of results. Default 10.
            region (str, optional): Region code (e.g. "us-en", "cn-zh"). Default "wt-wt".

        Returns:
            list: Search result dicts with 'title', 'href', and optional 'body'.
        """
        if not keywords or not keywords.strip():
            return {"error": "Keywords must not be empty."}

        kw_clean = keywords.strip().lower().replace(" ", "_")
        seed = hash(kw_clean + region)
        rng = random.Random(seed)

        n = min(max(max_results, 1), 20)
        results: List[Dict[str, str]] = []
        for i in range(n):
            site_name, url_tmpl = _SIMULATED_SITES[i % len(_SIMULATED_SITES)]
            kw_slug = kw_clean.replace("_", "-")
            href = url_tmpl.format(keyword=kw_slug, id=rng.randint(10000000, 99999999))
            title = f"{keywords} — {site_name} (page {i + 1})"
            entry: Dict[str, str] = {"title": title, "href": href}
            if self.show_snippet:
                entry["body"] = (
                    f"Simulated snippet about '{keywords}' "
                    f"from {site_name}. This is offline content for RL training."
                )
            results.append(entry)

        self._search_history.append({
            "keywords": keywords,
            "max_results": max_results,
            "region": region,
            "timestamp": self._timestamp(),
            "results_count": len(results),
        })

        return results

    def fetch_url_content(self, url: str, mode: str = "raw") -> Dict[str, str]:
        """
        Retrieve simulated page content from the given URL.
        All content is generated offline — no real HTTP requests.

        Args:
            url (str): The URL to fetch. Must start with http:// or https://.
            mode (str, optional): "raw" (HTML), "markdown", or "truncate" (plain text). Default "raw".

        Returns:
            dict with "content" key, or "error" key on failure.
        """
        if not url.startswith(("http://", "https://")):
            return {"error": f"Invalid URL: {url}"}

        parsed = urlparse(url)
        host = parsed.hostname or "example.com"
        path = parsed.path or "/"

        html = (
            "<!DOCTYPE html>\n"
            f"<html>\n<head><title>{host}{path}</title></head>\n"
            "<body>\n"
            f"<h1>Simulated Page: {host}{path}</h1>\n"
            f"<p>This is offline-simulated content for <code>{url}</code>.</p>\n"
            "<p>All content is generated locally for RL training purposes.</p>\n"
            "</body>\n</html>"
        )

        if mode == "raw":
            return {"content": html}
        elif mode == "markdown":
            md = (
                f"# Simulated Page: {host}{path}\n\n"
                f"This is offline-simulated content for `{url}`.\n\n"
                "All content is generated locally for RL training purposes.\n"
            )
            return {"content": md}
        elif mode == "truncate":
            text = (
                f"Simulated Page: {host}{path} "
                f"This is offline-simulated content for {url}. "
                "All content is generated locally for RL training purposes."
            )
            return {"content": text}
        else:
            return {"error": f"Unsupported mode: {mode}"}

    # ==================== Query / Retrieval ====================

    def search_history(
        self,
        keyword_filter: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_results: int = 10,
        sort_by: str = "timestamp",
        ascending: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieve search history with optional filtering, sorting and pagination.

        Args:
            keyword_filter (str, optional): Filter by keyword (case-insensitive).
            start_time (str, optional): ISO format start time.
            end_time (str, optional): ISO format end time.
            max_results (int): Maximum records. Default 10.
            sort_by (str): Field to sort by — "timestamp" or "keywords". Default "timestamp".
            ascending (bool): Sort ascending or descending. Default False.

        Returns:
            dict: "history" list and "total_count".
        """
        history = self._search_history[:]

        if keyword_filter:
            kw_lower = keyword_filter.lower()
            history = [h for h in history if kw_lower in h["keywords"].lower()]

        if start_time:
            history = [h for h in history if h["timestamp"] >= start_time]
        if end_time:
            history = [h for h in history if h["timestamp"] <= end_time]

        if sort_by not in ("timestamp", "keywords"):
            return {"error": f"Unsupported sort_by field: {sort_by}. Must be 'timestamp' or 'keywords'."}

        history.sort(key=lambda x: x.get(sort_by, ""), reverse=not ascending)

        total = len(history)
        history = history[:max_results]
        return {"history": history, "total_count": total}

    def clear_search_history(self) -> Dict[str, Any]:
        """
        Clear all search history records.

        Returns:
            dict: Confirmation with count of cleared records.
        """
        count = len(self._search_history)
        self._search_history.clear()
        return {"status": "success", "cleared_count": count}

    # ==================== State Flow / Management ====================

    def bookmark_result(self, title: str, url: str, snippet: str = "") -> Dict[str, Any]:
        """
        Bookmark a search result for later reference.

        Args:
            title (str): Title of the result.
            url (str): URL of the result.
            snippet (str, optional): Optional snippet/description.

        Returns:
            dict: Contains the bookmark object or error.
        """
        if not url or not title:
            return {"error": "Both 'title' and 'url' must be provided."}

        for bm in self._bookmarks:
            if bm["url"] == url:
                return {"error": f"Bookmark already exists for URL: {url}"}

        bookmark = {
            "id": len(self._bookmarks) + 1,
            "title": title,
            "url": url,
            "snippet": snippet,
            "created_at": self._timestamp(),
        }
        self._bookmarks.append(bookmark)
        return {"status": "success", "bookmark": bookmark}

    def unbookmark_result(self, bookmark_id: int) -> Dict[str, Any]:
        """
        Remove a bookmark by its id.

        Args:
            bookmark_id (int): The id of the bookmark to remove.

        Returns:
            dict: Confirmation or error.
        """
        for i, bm in enumerate(self._bookmarks):
            if bm["id"] == bookmark_id:
                removed = self._bookmarks.pop(i)
                return {"status": "success", "removed_bookmark": removed}
        return {"error": f"Bookmark with id {bookmark_id} not found."}

    def list_bookmarks(
        self,
        sort_by: str = "created_at",
        ascending: bool = False,
        max_results: int = 20,
    ) -> Dict[str, Any]:
        """
        List all bookmarks with sorting and pagination.

        Args:
            sort_by (str): Field — "id", "title", or "created_at". Default "created_at".
            ascending (bool): Sort direction. Default False.
            max_results (int): Max items. Default 20.

        Returns:
            dict: "bookmarks" list and "total_count".
        """
        if sort_by not in ("id", "title", "created_at"):
            return {"error": f"Unsupported sort_by field: {sort_by}. Must be 'id', 'title', or 'created_at'."}

        bookmarks = sorted(
            self._bookmarks,
            key=lambda x: x.get(sort_by, ""),
            reverse=not ascending,
        )
        total = len(bookmarks)
        bookmarks = bookmarks[:max_results]
        return {"bookmarks": bookmarks, "total_count": total}

    def clear_bookmarks(self) -> Dict[str, Any]:
        """
        Remove all bookmarks.

        Returns:
            dict: Confirmation with count of cleared bookmarks.
        """
        count = len(self._bookmarks)
        self._bookmarks.clear()
        return {"status": "success", "cleared_count": count}

    # ==================== Association & Aggregation ====================

    def add_search_filter(self, domain: str, filter_type: str = "include") -> Dict[str, Any]:
        """
        Add a domain filter for future search results.

        Args:
            domain (str): Domain to filter (e.g. "wikipedia.org").
            filter_type (str): "include" or "exclude". Default "include".

        Returns:
            dict: Contains the filter object or error.
        """
        if filter_type not in ("include", "exclude"):
            return {"error": f"filter_type must be 'include' or 'exclude', got '{filter_type}'."}
        if not domain:
            return {"error": "Domain must be provided."}

        for f in self._filters:
            if f["domain"] == domain and f["type"] == filter_type:
                return {"error": f"Filter already exists: {domain} ({filter_type})."}

        new_filter = {
            "id": len(self._filters) + 1,
            "domain": domain,
            "type": filter_type,
            "created_at": self._timestamp(),
        }
        self._filters.append(new_filter)
        return {"status": "success", "filter": new_filter}

    def remove_search_filter(self, filter_id: int) -> Dict[str, Any]:
        """
        Remove a search filter by its id.

        Args:
            filter_id (int): The id of the filter to remove.

        Returns:
            dict: Confirmation or error.
        """
        for i, f in enumerate(self._filters):
            if f["id"] == filter_id:
                removed = self._filters.pop(i)
                return {"status": "success", "removed_filter": removed}
        return {"error": f"Filter with id {filter_id} not found."}

    def list_filters(self) -> Dict[str, Any]:
        """
        List all active search filters.

        Returns:
            dict: "filters" list and "count".
        """
        return {"filters": self._filters, "count": len(self._filters)}

    # ==================== Statistics & Analysis ====================

    def get_search_stats(self) -> Dict[str, Any]:
        """
        Get aggregated statistics about search activities.

        Returns:
            dict: total_searches, unique_keywords, latest_search_time, average_results_per_search.
        """
        total = len(self._search_history)
        if total == 0:
            return {
                "total_searches": 0,
                "unique_keywords": 0,
                "latest_search_time": None,
                "average_results_per_search": 0.0,
            }

        keywords_set = set(h["keywords"] for h in self._search_history)
        latest = max(self._search_history, key=lambda x: x["timestamp"])
        avg_results = sum(h["results_count"] for h in self._search_history) / total

        return {
            "total_searches": total,
            "unique_keywords": len(keywords_set),
            "latest_search_time": latest["timestamp"],
            "average_results_per_search": round(avg_results, 2),
        }

    def set_config(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Update a configuration parameter.

        Args:
            key (str): Configuration key (e.g. "show_snippet").
            value (Any): New value.

        Returns:
            dict: Updated config or error.
        """
        allowed_keys = ["show_snippet"]
        if key not in allowed_keys:
            return {"error": f"Unknown config key '{key}'. Allowed: {allowed_keys}"}

        self._config[key] = value
        if key == "show_snippet":
            self.show_snippet = value
        return {"status": "success", "config": {key: self._config[key]}}

    def get_config(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve configuration. If key is None, return all.

        Args:
            key (str, optional): Specific config key.

        Returns:
            dict: Config value(s) or error.
        """
        if key is None:
            return {"config": deepcopy(self._config)}
        if key not in self._config:
            return {"error": f"Unknown config key '{key}'."}
        return {"config": {key: self._config[key]}}


__TEST_CASES__ = [
    {"name": "Normal — search keywords", "method": "search_engine_query", "input": {"keywords": "quantum computing", "max_results": 3}, "expected_contains": ["title", "href"]},
    {"name": "Boundary — empty keywords", "method": "search_engine_query", "input": {"keywords": ""}, "expected": {"error": "Keywords must not be empty."}},
    {"name": "Normal — fetch URL raw content", "method": "fetch_url_content", "input": {"url": "https://example.com/page"}, "expected_contains": ["content"]},
    {"name": "Normal — fetch URL markdown", "method": "fetch_url_content", "input": {"url": "https://example.com/page", "mode": "markdown"}, "expected_contains": ["content"]},
    {"name": "Normal — fetch URL truncated text", "method": "fetch_url_content", "input": {"url": "https://example.com/page", "mode": "truncate"}, "expected_contains": ["content"]},
    {"name": "Error — invalid URL", "method": "fetch_url_content", "input": {"url": "ftp://invalid"}, "expected": {"error": "Invalid URL: ftp://invalid"}},
    {"name": "Error — unsupported mode", "method": "fetch_url_content", "input": {"url": "https://x.com", "mode": "xml"}, "expected": {"error": "Unsupported mode: xml"}},
    {"name": "Normal — view search history (empty)", "method": "search_history", "input": {}, "expected": {"history": [], "total_count": 0}},
    {"name": "Error — invalid sort_by", "method": "search_history", "input": {"sort_by": "invalid"}, "expected": {"error": "Unsupported sort_by field: invalid. Must be 'timestamp' or 'keywords'."}},
    {"name": "Normal — add bookmark", "method": "bookmark_result", "input": {"title": "Example", "url": "https://example.com", "snippet": "test"}, "expected_contains": ["status", "bookmark"]},
    {"name": "Error — bookmark missing URL", "method": "bookmark_result", "input": {"title": "No URL", "url": ""}, "expected": {"error": "Both 'title' and 'url' must be provided."}},
    {"name": "Error — duplicate bookmark", "steps": [
        {"tool_call": "bookmark_result(title='Example', url='https://example.com')", "expect_success": True},
        {"tool_call": "bookmark_result(title='Example', url='https://example.com')", "expect_success": False},
    ]},
    {"name": "Error — remove nonexistent bookmark", "method": "unbookmark_result", "input": {"bookmark_id": 999}, "expected": {"error": "Bookmark with id 999 not found."}},
    {"name": "Normal — list bookmarks", "method": "list_bookmarks", "input": {}, "expected_contains": ["bookmarks", "total_count"]},
    {"name": "Normal — add search filter", "method": "add_search_filter", "input": {"domain": "example.com", "filter_type": "include"}, "expected_contains": ["status", "filter"]},
    {"name": "Error — invalid filter_type", "method": "add_search_filter", "input": {"domain": "test.com", "filter_type": "block"}, "expected": {"error": "filter_type must be 'include' or 'exclude', got 'block'."}},
    {"name": "Error — empty domain", "method": "add_search_filter", "input": {"domain": ""}, "expected": {"error": "Domain must be provided."}},
    {"name": "Normal — list filters", "method": "list_filters", "input": {}, "expected_contains": ["filters", "count"]},
    {"name": "Normal — search stats (empty history)", "method": "get_search_stats", "input": {}, "expected_contains": ["total_searches", "unique_keywords"]},
    {"name": "Normal — set config", "method": "set_config", "input": {"key": "show_snippet", "value": False}, "expected": {"status": "success", "config": {"show_snippet": False}}},
    {"name": "Error — unknown config key", "method": "set_config", "input": {"key": "nonexistent", "value": True}, "expected": {"error": "Unknown config key 'nonexistent'. Allowed: ['show_snippet']"}},
    {"name": "Normal — get config", "method": "get_config", "input": {}, "expected_contains": ["config"]},
    {"name": "Normal — clear search history", "method": "clear_search_history", "input": {}, "expected_contains": ["status", "cleared_count"]},
    {"name": "Normal — clear bookmarks", "method": "clear_bookmarks", "input": {}, "expected_contains": ["status", "cleared_count"]},
    {"name": "State-change — history updated after search", "steps": [
        {"tool_call": "search_engine_query(keywords='AI', max_results=2)", "expect_success": True},
        {"tool_call": "search_history(max_results=5)", "expect_success": True},
    ]},
    {"name": "Workflow — search→bookmark→list→unbookmark", "steps": [
        {"tool_call": "search_engine_query(keywords='machine learning', max_results=3)", "expect_success": True},
        {"tool_call": "bookmark_result(title='ML Wiki', url='https://en.wikipedia.org/wiki/ML', snippet='desc')", "expect_success": True},
        {"tool_call": "list_bookmarks(sort_by='created_at')", "expect_success": True},
        {"tool_call": "unbookmark_result(bookmark_id=1)", "expect_success": True},
        {"tool_call": "list_bookmarks()", "expect_success": True},
    ]},
]

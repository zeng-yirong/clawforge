import json
import re
import time
from copy import deepcopy
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from rank_bm25 import BM25Plus

DEFAULT_STATE = {
    "core_memory": {
        "example_user_profile": {
            "value": "John Doe",
            "created_at": 1234567890.0,
            "access_count": 0
        }
    },
    "archival_memory": {
        "example_system_config": {
            "value": "dark_mode=true",
            "created_at": 1234567890.0,
            "access_count": 0
        }
    }
}


class MemoryAPI:
    """Base class for memory environments. Provides abstract interface for memory management."""

    def __init__(self):
        self.core_memory = {}
        self.archival_memory = {}
        self._api_description = ""

    def _load_scenario(self, initial_config: dict, long_context: bool = False):
        raise NotImplementedError

    def _flush_memory_to_local_file(self):
        raise NotImplementedError

    def _dump_core_memory_to_context(self) -> str:
        raise NotImplementedError

    def get_env_state(self):
        raise NotImplementedError


MAX_CORE_MEMORY_SIZE = 7
MAX_CORE_MEMORY_ENTRY_LENGTH = 300
MAX_ARCHIVAL_MEMORY_SIZE = 50
MAX_ARCHIVAL_MEMORY_ENTRY_LENGTH = 2000


class MemoryAPI_kv(MemoryAPI):
    """
    A class that provides APIs to manage short-term and long-term memory data in a key-value format.
    """

    def __init__(self, snapshot_folder: Optional[str] = None, test_id: Optional[str] = None):
        self.core_memory = {}
        self.archival_memory = {}
        self._api_description = """This tool belongs to the memory suite, which provides APIs to interact with a key-value based memory system."""
        self.snapshot_folder = Path(snapshot_folder) if snapshot_folder else None
        self.test_id = test_id
        self.latest_snapshot_file = None

    def _load_scenario(self, initial_config: dict, long_context: bool = False):
        if not initial_config:
            return
        if not isinstance(initial_config, dict):
            return
        core = initial_config.get("core_memory", {})
        archival = initial_config.get("archival_memory", {})
        self.core_memory = deepcopy(core) if isinstance(core, dict) else {}
        self.archival_memory = deepcopy(archival) if isinstance(archival, dict) else {}

    def get_env_state(self):
        return {
            "core_memory": deepcopy(self.core_memory),
            "archival_memory": deepcopy(self.archival_memory)
        }

    def _flush_memory_to_local_file(self):
        """Flush current memory to local JSON file if paths are configured."""
        if not self.snapshot_folder or not self.test_id:
            return
        self.snapshot_folder.mkdir(parents=True, exist_ok=True)
        snapshot_path = self.snapshot_folder / f"{self.test_id}.json"
        with open(snapshot_path, "w") as f:
            json.dump(
                {
                    "core_memory": self._strip_metadata(self.core_memory),
                    "archival_memory": self._strip_metadata(self.archival_memory),
                },
                f,
                indent=4,
            )
        if self.latest_snapshot_file:
            with open(self.latest_snapshot_file, "w") as f:
                json.dump(
                    {
                        "core_memory": self._strip_metadata(self.core_memory),
                        "archival_memory": self._strip_metadata(self.archival_memory),
                    },
                    f,
                    indent=4,
                )

    def _dump_core_memory_to_context(self) -> str:
        if not self.core_memory:
            return "There is no content in the core memory at this point."
        stripped = self._strip_metadata(self.core_memory)
        return json.dumps(stripped, indent=4)

    @staticmethod
    def _strip_metadata(memory: dict) -> dict:
        """Remove internal metadata from memory entries, keeping only raw value strings."""
        stripped = {}
        for key, entry in memory.items():
            if isinstance(entry, dict) and "value" in entry:
                stripped[key] = entry["value"]
            else:
                stripped[key] = entry
        return stripped

    @staticmethod
    def _wrap_value(value: str) -> dict:
        """Wrap a raw value with metadata."""
        return {
            "value": value,
            "created_at": time.time(),
            "access_count": 0
        }

    @staticmethod
    def _extract_value(entry) -> str:
        """Extract the raw value from an entry (may be dict with metadata or plain string)."""
        if isinstance(entry, dict) and "value" in entry:
            return entry["value"]
        return entry

    @staticmethod
    def _similarity_search(query: str, corpus: list[str], k: int = 5) -> Dict:
        """
        Search for the most similar text in the corpus to the query using BM25+ algorithm.

        Args:
            query (str): The query text to search for.
            corpus (list[str]): A list of text strings to search in.
            k (int): The number of results to return.

        Returns:
            dict with keys:
                - success: bool
                - data: list of {"score": float, "text": str} (top k results)
        """
        if not corpus:
            return {"success": True, "data": []}
        tokenized_corpus = [text.replace("_", " ").lower().split() for text in corpus]
        bm25 = BM25Plus(tokenized_corpus)
        tokenized_query = query.replace("_", " ").lower().split()
        scores = bm25.get_scores(tokenized_query)
        ranked_results = sorted(zip(scores, corpus), key=lambda x: x[0], reverse=True)
        top_k = [{"score": round(float(score), 4), "text": text} for score, text in ranked_results[:k]]
        return {"success": True, "data": top_k}

    @staticmethod
    def _is_valid_key_format(s: str) -> bool:
        """
        Check if the key contains only alphanumeric characters and underscores, and no spaces or special characters.
        """
        if not s:
            return False
        # Allow letters, digits, underscores; reject spaces and special characters
        pattern = r"^[a-zA-Z0-9_]+$"
        return bool(re.match(pattern, s)) and " " not in s

    def _evict_oldest_from_core(self):
        """Evict the oldest entry (by creation time) from core memory to make room."""
        if not self.core_memory:
            return
        # Find the oldest entry (smallest created_at)
        oldest_key = min(
            self.core_memory.keys(),
            key=lambda k: self.core_memory[k].get("created_at", 0) if isinstance(self.core_memory[k], dict) else 0
        )
        self._archive_entry(oldest_key)

    def _evict_oldest_from_archival(self):
        """Evict the oldest entry from archival memory to make room."""
        if not self.archival_memory:
            return
        oldest_key = min(
            self.archival_memory.keys(),
            key=lambda k: self.archival_memory[k].get("created_at", 0) if isinstance(self.archival_memory[k], dict) else 0
        )
        del self.archival_memory[oldest_key]

    def _archive_entry(self, key: str):
        """Move an entry from core to archival memory, evicting from archival if needed."""
        entry = self.core_memory.pop(key)
        raw_value = self._extract_value(entry)
        # If archival is full, evict oldest first
        if len(self.archival_memory) >= MAX_ARCHIVAL_MEMORY_SIZE:
            self._evict_oldest_from_archival()
        self.archival_memory[key] = self._wrap_value(raw_value)

    # ========== Core Memory APIs ==========

    def core_memory_add(self, key: str, value: str) -> Dict[str, str]:
        """
        Add a key-value pair to the short-term memory. Make sure to use meaningful keys for easy retrieval later.

        Args:
            key (str): The key under which the value is stored. The key should be unique and case-sensitive. Keys must be snake_case and cannot contain spaces.
            value (str): The value to store in the short-term memory.

        Returns:
            status (str): Status of the operation.
        """
        if not isinstance(key, str) or not isinstance(value, str):
            return {"error": "Both key and value must be strings."}
        key, value = str(key), str(value)
        if not self._is_valid_key_format(key):
            return {"error": "Key must contain only alphanumeric characters and underscores, and cannot contain spaces."}
        if key in self.core_memory:
            return {"error": "Key name must be unique."}
        if len(value) > MAX_CORE_MEMORY_ENTRY_LENGTH:
            return {
                "error": f"Entry is too long. Please shorten the entry to less than {MAX_CORE_MEMORY_ENTRY_LENGTH} characters."
            }

        # If core is full, automatically archive oldest entry
        if len(self.core_memory) >= MAX_CORE_MEMORY_SIZE:
            self._evict_oldest_from_core()

        self.core_memory[key] = self._wrap_value(value)
        return {"status": "Key-value pair added."}

    def core_memory_remove(self, key: str) -> Dict[str, str]:
        """
        Remove a key-value pair from the short-term memory.

        Args:
            key (str): The key to remove from the short-term memory. Case-sensitive.

        Returns:
            status (str): Status of the operation.
        """
        if key not in self.core_memory:
            return {"error": "Key not found."}
        del self.core_memory[key]
        return {"status": "Key removed."}

    def core_memory_replace(self, key: str, value: str) -> Dict[str, str]:
        """
        Replace a key-value pair in the short-term memory with a new value.

        Args:
            key (str): The key to replace in the short-term memory. Case-sensitive.
            value (str): The new value associated with the key.

        Returns:
            status (str): Status of the operation.
        """
        if not isinstance(key, str) or not isinstance(value, str):
            return {"error": "Both key and value must be strings."}
        key, value = str(key), str(value)
        if key not in self.core_memory:
            return {"error": "Key not found."}
        if len(value) > MAX_CORE_MEMORY_ENTRY_LENGTH:
            return {
                "error": f"Entry is too long. Please shorten the entry to less than {MAX_CORE_MEMORY_ENTRY_LENGTH} characters."
            }
        # Preserve metadata but update value
        old_entry = self.core_memory[key]
        if isinstance(old_entry, dict):
            old_entry["value"] = value
            old_entry["access_count"] = 0  # reset?
        else:
            self.core_memory[key] = self._wrap_value(value)
        return {"status": "Key replaced."}

    def core_memory_clear(self) -> Dict[str, str]:
        """
        Clear all key-value pairs from the short-term memory, including those from previous interactions. This operation is irreversible.

        Returns:
            status (str): Status of the operation.
        """
        self.core_memory = {}
        return {"status": "Short term memory cleared."}

    def core_memory_retrieve(self, key: str) -> Dict[str, str]:
        """
        Retrieve the value associated with a key from the short-term memory. This function does not support partial key matching or similarity search.

        Args:
            key (str): The key to retrieve. Case-sensitive. The key must match exactly with the key stored in the memory.

        Returns:
            value (str): The value associated with the key.
        """
        if key not in self.core_memory:
            return {"error": "Key not found."}
        entry = self.core_memory[key]
        # Update access count if metadata present
        if isinstance(entry, dict):
            entry["access_count"] = entry.get("access_count", 0) + 1
        return {"value": self._extract_value(entry)}

    def core_memory_list_keys(self) -> Dict[str, List[str]]:
        """
        List all keys currently in the short-term memory.

        Returns:
            keys (List[str]): A list of all keys in the short-term memory.
        """
        return {"keys": list(self.core_memory.keys())}

    def core_memory_key_search(
        self, query: str, k: int = 5
    ) -> Dict:
        """
        Search for key names in the short-term memory that are similar to the query using BM25+ algorithm.

        Args:
            query (str): The query text to search for.
            k (int): [Optional] The number of results to return.

        Returns:
            dict with keys:
                - success: bool
                - data: list of {"score": float, "text": str} (top k results)
                (also backward compatible: ranked_results key)
        """
        if not isinstance(query, str) or not isinstance(k, int) or k <= 0:
            return {"error": "Query must be a string and k must be a positive integer."}
        keys = list(self.core_memory.keys())
        result = self._similarity_search(query, keys, k)
        # For backward compatibility, also include ranked_results
        result["ranked_results"] = [item["text"] for item in result["data"]]
        return result

    def core_memory_retrieve_all(self) -> Dict:
        """
        Retrieve all key-value pairs from the short-term memory.

        Returns:
            dict with success and data keys
        """
        stripped = self._strip_metadata(self.core_memory)
        return {"success": True, "data": stripped}

    # ========== Archival Memory APIs ==========

    def archival_memory_add(self, key: str, value: str) -> Dict[str, str]:
        """
        Add a key-value pair to the long-term memory. Make sure to use meaningful keys for easy retrieval later.

        Args:
            key (str): The key under which the value is stored. The key should be unique and case-sensitive. Keys must be snake_case and cannot contain spaces.
            value (str): The value to store in the long-term memory.

        Returns:
            status (str): Status of the operation.
        """
        if not isinstance(key, str) or not isinstance(value, str):
            return {"error": "Both key and value must be strings."}
        key, value = str(key), str(value)
        if not self._is_valid_key_format(key):
            return {"error": "Key must contain only alphanumeric characters and underscores, and cannot contain spaces."}
        if key in self.archival_memory:
            return {"error": "Key name must be unique."}
        if len(value) > MAX_ARCHIVAL_MEMORY_ENTRY_LENGTH:
            return {
                "error": f"Entry is too long. Please shorten the entry to less than {MAX_ARCHIVAL_MEMORY_ENTRY_LENGTH} characters."
            }

        # If archival is full, evict oldest entry
        if len(self.archival_memory) >= MAX_ARCHIVAL_MEMORY_SIZE:
            self._evict_oldest_from_archival()

        self.archival_memory[key] = self._wrap_value(value)
        return {"status": "Key added."}

    def archival_memory_remove(self, key: str) -> Dict[str, str]:
        """
        Remove a key-value pair from the long-term memory.

        Args:
            key (str): The key to remove from the long-term memory. Case-sensitive.

        Returns:
            status (str): Status of the operation.
        """
        if key not in self.archival_memory:
            return {"error": "Key not found."}
        del self.archival_memory[key]
        return {"status": "Key removed."}

    def archival_memory_replace(self, key: str, value: str) -> Dict[str, str]:
        """
        Replace a key-value pair in the long-term memory with a new value.

        Args:
            key (str): The key to replace in the long-term memory. Case-sensitive.
            value (str): The new value associated with the key.

        Returns:
            status (str): Status of the operation.
        """
        if not isinstance(key, str) or not isinstance(value, str):
            return {"error": "Both key and value must be strings."}
        key, value = str(key), str(value)
        if key not in self.archival_memory:
            return {"error": "Key not found."}
        if len(value) > MAX_ARCHIVAL_MEMORY_ENTRY_LENGTH:
            return {
                "error": f"Entry is too long. Please shorten the entry to less than {MAX_ARCHIVAL_MEMORY_ENTRY_LENGTH} characters."
            }
        old_entry = self.archival_memory[key]
        if isinstance(old_entry, dict):
            old_entry["value"] = value
            old_entry["access_count"] = 0
        else:
            self.archival_memory[key] = self._wrap_value(value)
        return {"status": "Key replaced."}

    def archival_memory_clear(self) -> Dict[str, str]:
        """
        Clear all key-value pairs from the long-term memory, including those from previous interactions. This operation is irreversible.

        Returns:
            status (str): Status of the operation.
        """
        self.archival_memory = {}
        return {"status": "Long term memory cleared."}

    def archival_memory_retrieve(self, key: str) -> Dict[str, str]:
        """
        Retrieve the value associated with a key from the long-term memory. This function does not support partial key matching or similarity search.

        Args:
            key (str): The key to retrieve. Case-sensitive. The key must match exactly with the key stored in the memory.

        Returns:
            value (str): The value associated with the key.
        """
        if key not in self.archival_memory:
            return {"error": "Key not found."}
        entry = self.archival_memory[key]
        if isinstance(entry, dict):
            entry["access_count"] = entry.get("access_count", 0) + 1
        return {"value": self._extract_value(entry)}

    def archival_memory_list_keys(self) -> Dict[str, List[str]]:
        """
        List all keys currently in the long-term memory.

        Returns:
            keys (List[str]): A list of all keys in the long-term memory.
        """
        return {"keys": list(self.archival_memory.keys())}

    def archival_memory_key_search(
        self, query: str, k: int = 5
    ) -> Dict:
        """
        Search for key names in the long-term memory that are similar to the query using BM25+ algorithm.

        Args:
            query (str): The query text to search for.
            k (int): [Optional] The number of results to return.

        Returns:
            dict with keys:
                - success: bool
                - data: list of {"score": float, "text": str}
                (also backward compatible: ranked_results)
        """
        if not isinstance(query, str) or not isinstance(k, int) or k <= 0:
            return {"error": "Query must be a string and k must be a positive integer."}
        keys = list(self.archival_memory.keys())
        result = self._similarity_search(query, keys, k)
        result["ranked_results"] = [item["text"] for item in result["data"]]
        return result

    def archival_memory_content_search(self, query: str, k: int = 5) -> Dict:
        """
        Search for values in the long-term memory that are semantically similar to the query using BM25+ algorithm.

        Args:
            query (str): The query text to search for.
            k (int): [Optional] The number of results to return.

        Returns:
            dict with keys:
                - success: bool
                - data: list of {"score": float, "key": str, "value": str}
        """
        if not isinstance(query, str) or not isinstance(k, int) or k <= 0:
            return {"error": "Query must be a string and k must be a positive integer."}
        # Build list of values (raw strings)
        values = [self._extract_value(entry) for entry in self.archival_memory.values()]
        keys = list(self.archival_memory.keys())
        tokenized_corpus = [v.replace("_", " ").lower().split() for v in values]
        if not tokenized_corpus:
            return {"success": True, "data": []}
        bm25 = BM25Plus(tokenized_corpus)
        tokenized_query = query.replace("_", " ").lower().split()
        scores = bm25.get_scores(tokenized_query)
        ranked = sorted(zip(scores, keys, values), key=lambda x: x[0], reverse=True)
        top_k = [{"score": round(float(score), 4), "key": key, "value": value} for score, key, value in ranked[:k]]
        return {"success": True, "data": top_k}

    # ========== Cross-memory operations ==========

    def core_memory_archive_to_archival(self, key: str) -> Dict[str, str]:
        """
        Move a specific entry from core memory to archival memory.
        Args:
            key (str): The key to move.
        Returns:
            status (str): Status of the operation.
        """
        if key not in self.core_memory:
            return {"error": "Key not found in core memory."}
        self._archive_entry(key)
        return {"status": f"Key '{key}' moved to archival memory."}

    def archival_memory_recall_to_core(self, key: str) -> Dict[str, str]:
        """
        Recall a specific entry from archival memory to core memory.
        If core memory is full, the oldest entry will be archived automatically.
        Args:
            key (str): The key to recall.
        Returns:
            status (str): Status of the operation.
        """
        if key not in self.archival_memory:
            return {"error": "Key not found in archival memory."}
        entry = self.archival_memory.pop(key)
        raw_value = self._extract_value(entry)
        # If core is full, archive oldest core entry first
        if len(self.core_memory) >= MAX_CORE_MEMORY_SIZE:
            self._evict_oldest_from_core()
        self.core_memory[key] = self._wrap_value(raw_value)
        return {"status": f"Key '{key}' recalled to core memory."}


__TEST_CASES__ = [
    {
        'name': 'Normal path & State-change verification (Core Memory)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_add(key='user_profile', value='John Doe')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_retrieve(key='user_profile')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_list_keys()"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_retrieve_all()"}
        ]
    },
    {
        'name': 'Normal path & State-change verification (Archival Memory)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_add(key='system_config', value='dark_mode=true')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_retrieve(key='system_config')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_list_keys()"}
        ]
    },
    {
        'name': 'Cross-method workflow (Core Memory CRUD)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_add(key='session_token', value='abc123init')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_replace(key='session_token', value='xyz789new')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_retrieve(key='session_token')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_remove(key='session_token')"},
            {'expect_success': False, 'tool_call': "env['memory_kv'].core_memory_retrieve(key='session_token')"}
        ]
    },
    {
        'name': 'Cross-method workflow (Archival Memory CRUD)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_add(key='historical_data', value='2023_records')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_replace(key='historical_data', value='2024_records')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_retrieve(key='historical_data')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_remove(key='historical_data')"},
            {'expect_success': False, 'tool_call': "env['memory_kv'].archival_memory_retrieve(key='historical_data')"}
        ]
    },
    {
        'name': 'Boundary values (Empty strings and long inputs)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_add(key='empty_value_key', value='')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_add(key='long_value_key', value='A_VERY_LONG_STRING_THAT_EXCEEDS_NORMAL_LENGTH_LIMITS_1234567890')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_retrieve(key='empty_value_key')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_retrieve(key='long_value_key')"}
        ]
    },
    {
        'name': 'Error paths (Invalid keys, non-existent keys)',
        'steps': [
            {'expect_success': False, 'tool_call': "env['memory_kv'].core_memory_retrieve(key='non_existent_key')"},
            {'expect_success': False, 'tool_call': "env['memory_kv'].core_memory_remove(key='non_existent_key')"},
            {'expect_success': False, 'tool_call': "env['memory_kv'].core_memory_replace(key='non_existent_key', value='val')"},
            {'expect_success': False, 'tool_call': "env['memory_kv'].core_memory_add(key='invalid key with spaces', value='val')"}
        ]
    },
    {
        'name': 'Error paths (Missing fields, wrong types, negative numbers)',
        'steps': [
            {'expect_success': False, 'tool_call': "env['memory_kv'].core_memory_add(key='missing_value')"},
            {'expect_success': False, 'tool_call': "env['memory_kv'].core_memory_key_search(query='test', k=-5)"},
            {'expect_success': False, 'tool_call': "env['memory_kv'].archival_memory_add(key='wrong_type_key', value=123)"}
        ]
    },
    {
        'name': 'Search functionality (BM25+ algorithm)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_add(key='search_target_alpha', value='data1')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_add(key='search_target_beta', value='data2')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_key_search(query='target', k=2)"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_add(key='archival_target_gamma', value='data3')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_key_search(query='gamma', k=1)"}
        ]
    },
    {
        'name': 'Clear functionality (Core Memory)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_add(key='temp_data_one', value='val1')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_add(key='temp_data_two', value='val2')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_clear()"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].core_memory_list_keys()"},
            {'expect_success': False, 'tool_call': "env['memory_kv'].core_memory_retrieve(key='temp_data_one')"}
        ]
    },
    {
        'name': 'Clear functionality (Archival Memory)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_add(key='old_log_one', value='log1')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_add(key='old_log_two', value='log2')"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_clear()"},
            {'expect_success': True, 'tool_call': "env['memory_kv'].archival_memory_list_keys()"},
            {'expect_success': False, 'tool_call': "env['memory_kv'].archival_memory_retrieve(key='old_log_one')"}
        ]
    }
]
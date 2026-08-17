import json
from copy import deepcopy
from typing import Any, Dict, List, Optional

DEFAULT_STATE: Dict[str, Any] = {
    "memory": "This is the initial memory content. It contains some information.",
    "archival_memory": {
        "0": "Archived text from previous session.",
        "1": "Another archival entry with additional details."
    },
}

class MemoryAPI:
    """Base class for memory environments. Provides abstract interface for memory management."""

    def __init__(self):
        self.core_memory = {}
        self.archival_memory = {}
        self.memory = ""
        self._api_description = ""

    def _load_scenario(self, initial_config: dict, long_context: bool = False):
        return {"error": "Not implemented"}

    def _flush_memory_to_local_file(self):
        pass

    def _dump_core_memory_to_context(self) -> str:
        return ""

    def get_env_state(self):
        return {}


MAX_MEMORY_ENTRY_LENGTH = 10000  # 10k characters


class MemoryAPI_rec_sum(MemoryAPI):
    """
    A class that provides APIs to manage memory data via recursive summarization.
    Supports archival memory with retrieval, search, and automatic capacity management.
    """

    def __init__(
        self,
        snapshot_folder: Optional[str] = None,
        test_id: Optional[str] = None,
        latest_snapshot_file: Optional[str] = None,
    ):
        super().__init__()
        self.memory = ""
        self.archival_memory: Dict[str, str] = {}
        self._api_description = """This tool belongs to the memory suite, which provides APIs to manage memory data via recursive summarization."""
        self.snapshot_folder = snapshot_folder
        self.test_id = test_id
        self.latest_snapshot_file = latest_snapshot_file

    def _auto_manage_capacity(self) -> None:
        """
        Automatically archive oldest content if memory exceeds MAX_MEMORY_ENTRY_LENGTH.
        """
        while len(self.memory) > MAX_MEMORY_ENTRY_LENGTH:
            # Archive enough characters to bring memory back within bounds
            excess = len(self.memory) - MAX_MEMORY_ENTRY_LENGTH
            chunk_size = min(MAX_MEMORY_ENTRY_LENGTH // 2, excess + 100)  # archive at least some
            actual_chunk = min(chunk_size, len(self.memory))
            archived_text = self.memory[:actual_chunk]
            self.memory = self.memory[actual_chunk:]
            archive_id = str(len(self.archival_memory))
            self.archival_memory[archive_id] = archived_text

    def _load_scenario(self, initial_config: dict, long_context: bool = False):
        if not initial_config:
            return
        if not isinstance(initial_config, dict):
            return

        self.memory = deepcopy(initial_config.get("memory", ""))
        if not isinstance(self.memory, str):
            self.memory = str(self.memory)

        archival = initial_config.get("archival_memory", {})
        if isinstance(archival, dict):
            self.archival_memory = deepcopy(archival)

    def _flush_memory_to_local_file(self):
        """
        Flush (save) current memory and archival memory to a local JSON file.
        """
        if not self.snapshot_folder or not self.test_id or not self.latest_snapshot_file:
            return

        try:
            # Write the snapshot file for the current test entry
            with open(self.snapshot_folder / f"{self.test_id}.json", "w") as f:
                json.dump(
                    {
                        "memory": self.memory,
                        "archival_memory": self.archival_memory,
                    },
                    f,
                    indent=4,
                )

            # Update the latest snapshot file content
            with open(self.latest_snapshot_file, "w") as f:
                json.dump(
                    {
                        "memory": self.memory,
                        "archival_memory": self.archival_memory,
                    },
                    f,
                    indent=4,
                )
        except Exception:
            pass

    def _dump_core_memory_to_context(self) -> str:
        if not self.memory:
            return "There is no content in the memory at this point."
        return str(self.memory)

    def get_env_state(self):
        return {
            "memory": self.memory,
            "archival_memory": self.archival_memory,
        }

    # -------------------------------------------------------------------------
    # Archival memory retrieval and search (new)
    # -------------------------------------------------------------------------
    def archival_retrieve(self, archive_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific archived text by its ID.

        Args:
            archive_id (str): The ID of the archived entry.

        Returns:
            Dict with 'archived_text' on success, or 'error' if not found.
        """
        if not isinstance(archive_id, str):
            return {"success": False, "error": "Parameter 'archive_id' must be a string."}
        if archive_id not in self.archival_memory:
            return {"success": False, "error": f"Archive ID '{archive_id}' not found."}
        return {"success": True, "archived_text": self.archival_memory[archive_id]}

    def archival_search(self, query: str) -> Dict[str, Any]:
        """
        Search for a keyword in all archived entries.

        Args:
            query (str): The keyword or phrase to search for.

        Returns:
            Dict with 'results' (list of {id, snippet}) or 'error'.
        """
        if not isinstance(query, str) or not query:
            return {"success": False, "error": "Parameter 'query' must be a non-empty string."}
        results = []
        for aid, text in self.archival_memory.items():
            if query in text:
                # Provide a snippet around the match
                idx = text.find(query)
                start = max(0, idx - 50)
                end = min(len(text), idx + len(query) + 50)
                snippet = text[start:end]
                results.append({"id": aid, "snippet": snippet})
        return {"success": True, "results": results, "count": len(results)}

    def archival_list(self) -> Dict[str, Any]:
        """
        List all archived entries with their IDs and first 100 characters preview.

        Returns:
            Dict with 'entries' list.
        """
        entries = []
        for aid, text in self.archival_memory.items():
            preview = text[:100] + ("..." if len(text) > 100 else "")
            entries.append({"id": aid, "preview": preview})
        return {"success": True, "entries": entries, "total": len(entries)}

    # -------------------------------------------------------------------------
    # Core memory operations (with unified success field and auto capacity)
    # -------------------------------------------------------------------------
    def memory_append(self, text: str) -> Dict[str, str]:
        """
        Append a new text to the end of the memory.

        Args:
            text (str): The text to append to the memory.

        Returns:
            Dict with success status.
        """
        if not isinstance(text, str):
            return {"success": False, "error": "Parameter 'text' must be a string."}

        self.memory += text
        self._auto_manage_capacity()
        return {"success": True, "status": "Memory appended."}

    def memory_update(self, text: str) -> Dict[str, str]:
        """
        Update the memory with new text. This will replace the existing memory content.

        Args:
            text (str): The new text to set as the memory.

        Returns:
            Dict with success status.
        """
        if not isinstance(text, str):
            return {"success": False, "error": "Parameter 'text' must be a string."}

        self.memory = text
        self._auto_manage_capacity()
        return {"success": True, "status": "Memory updated."}

    def memory_clear(self) -> Dict[str, str]:
        """
        Clear all content in the memory, including any from previous interactions. This operation is irreversible.

        Returns:
            Dict with success status.
        """
        self.memory = ""
        return {"success": True, "status": "Short term memory cleared."}

    def memory_replace(self, old_text: str, new_text: str) -> Dict[str, str]:
        """
        Replace a specific text in the memory with new text.
        Args:
            old_text (str): The text to be replaced in the memory.
            new_text (str): The new text to replace the old text.
        Returns:
            Dict with success status.
        """
        if not isinstance(old_text, str) or not isinstance(new_text, str):
            return {"success": False, "error": "Parameters 'old_text' and 'new_text' must be strings."}

        if old_text not in self.memory:
            return {"success": False, "error": f"Text '{old_text}' not found in memory."}

        replaced_memory = self.memory.replace(old_text, new_text)
        self.memory = replaced_memory
        self._auto_manage_capacity()
        return {"success": True, "status": "Memory updated."}

    def memory_retrieve(self) -> Dict[str, str]:
        """
        Retrieve the current content of the memory.

        Returns:
            Dict with memory_content.
        """
        return {"success": True, "memory_content": self.memory}

    def memory_summarize(self, instruction: str) -> Dict[str, str]:
        """
        Simulate calling an internal model to compress and rewrite the current memory based on an instruction.

        Args:
            instruction (str): The summarization instruction (e.g., 'extract key conclusions').

        Returns:
            Dict with success status.
        """
        if not isinstance(instruction, str):
            return {"success": False, "error": "Parameter 'instruction' must be a string."}

        if not self.memory:
            return {"success": False, "error": "Memory is empty, nothing to summarize."}

        # Simulate a more realistic summarization: keep first 300 chars and last 200 chars, mark with instruction
        original = self.memory
        if len(original) > 500:
            head = original[:300]
            tail = original[-200:]
            summary = f"[Summary based on '{instruction}']\n{head}\n...(skipped {len(original)-500} chars)...\n{tail}"
        else:
            summary = f"[Summary based on '{instruction}']\n{original}"

        self.memory = summary
        self._auto_manage_capacity()
        return {"success": True, "status": "Memory summarized."}

    def memory_archive_oldest(self, chunk_size: int) -> Dict[str, str]:
        """
        Truncate the oldest (front) part of the memory and move it to the archival memory.

        Args:
            chunk_size (int): The number of characters to archive from the beginning.

        Returns:
            Dict with success status.
        """
        if not isinstance(chunk_size, int):
            return {"success": False, "error": "Parameter 'chunk_size' must be an integer."}
        if chunk_size <= 0:
            return {"success": False, "error": "Parameter 'chunk_size' must be greater than 0."}

        if not self.memory:
            return {"success": False, "error": "Memory is empty, nothing to archive."}

        actual_chunk = min(chunk_size, len(self.memory))
        archived_text = self.memory[:actual_chunk]
        self.memory = self.memory[actual_chunk:]

        archive_id = str(len(self.archival_memory))
        self.archival_memory[archive_id] = archived_text

        return {"success": True, "status": f"Successfully archived {actual_chunk} characters."}

    def memory_search(self, query: str) -> Dict[str, Any]:
        """
        Search for a specific keyword in the memory, returning whether it exists and its frequency.

        Args:
            query (str): The keyword or phrase to search for.

        Returns:
            A dictionary containing 'found' (bool) and 'count' (int) or 'error' message.
        """
        if not isinstance(query, str):
            return {"success": False, "error": "Parameter 'query' must be a string."}
        if not query:
            return {"success": False, "error": "Parameter 'query' cannot be empty."}

        count = self.memory.count(query)
        return {
            "success": True,
            "found": count > 0,
            "count": count
        }

    def memory_extract_context(self, target_text: str, window_size: int) -> Dict[str, str]:
        """
        Find a target text and return it along with its surrounding context.

        Args:
            target_text (str): The text to search for.
            window_size (int): The number of characters to include before and after the target text.

        Returns:
            Dict with 'context' on success, or 'error'.
        """
        if not isinstance(target_text, str) or not target_text:
            return {"success": False, "error": "Parameter 'target_text' must be a non-empty string."}
        if not isinstance(window_size, int) or window_size < 0:
            return {"success": False, "error": "Parameter 'window_size' must be a non-negative integer."}

        idx = self.memory.find(target_text)
        if idx == -1:
            return {"success": False, "error": f"Target text '{target_text}' not found in memory."}

        start_idx = max(0, idx - window_size)
        end_idx = min(len(self.memory), idx + len(target_text) + window_size)

        context = self.memory[start_idx:end_idx]
        return {"success": True, "context": context}

    def memory_get_capacity(self) -> Dict[str, int]:
        """
        Return the current memory length, maximum capacity, and remaining available characters.

        Returns:
            Dict containing 'current_length', 'max_capacity', and 'remaining_space'.
        """
        current_length = len(self.memory)
        return {
            "success": True,
            "current_length": current_length,
            "max_capacity": MAX_MEMORY_ENTRY_LENGTH,
            "remaining_space": MAX_MEMORY_ENTRY_LENGTH - current_length
        }

    def memory_prepend(self, text: str) -> Dict[str, str]:
        """
        Insert text at the very beginning of the memory.

        Args:
            text (str): The text to prepend.

        Returns:
            Dict with success status.
        """
        if not isinstance(text, str):
            return {"success": False, "error": "Parameter 'text' must be a string."}

        self.memory = text + self.memory
        self._auto_manage_capacity()
        return {"success": True, "status": "Memory prepended."}

    def memory_delete(self, target_text: str) -> Dict[str, str]:
        """
        Precisely delete all occurrences of a specified substring from the memory.

        Args:
            target_text (str): The text to delete from memory.

        Returns:
            Dict with success status.
        """
        if not isinstance(target_text, str) or not target_text:
            return {"success": False, "error": "Parameter 'target_text' must be a non-empty string."}

        if target_text not in self.memory:
            return {"success": False, "error": f"Text '{target_text}' not found in memory."}

        self.memory = self.memory.replace(target_text, "")
        return {"success": True, "status": f"Deleted '{target_text}' from memory."}

    def memory_insert_after(self, anchor_text: str, new_text: str) -> Dict[str, str]:
        """
        Find an anchor text in memory and insert new text immediately after it.

        Args:
            anchor_text (str): The existing text in memory to act as an anchor.
            new_text (str): The new text to insert after the anchor.

        Returns:
            Dict with success status.
        """
        if not isinstance(anchor_text, str) or not anchor_text:
            return {"success": False, "error": "Parameter 'anchor_text' must be a non-empty string."}
        if not isinstance(new_text, str):
            return {"success": False, "error": "Parameter 'new_text' must be a string."}

        idx = self.memory.find(anchor_text)
        if idx == -1:
            return {"success": False, "error": f"Anchor text '{anchor_text}' not found in memory."}

        insert_pos = idx + len(anchor_text)
        combined_text = self.memory[:insert_pos] + new_text + self.memory[insert_pos:]
        self.memory = combined_text
        self._auto_manage_capacity()
        return {"success": True, "status": "Memory updated successfully."}


__TEST_CASES__ = [
    {
        'name': 'Normal path: append and retrieve memory',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_append(text='Hello World')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_retrieve()"}
        ]
    },
    {
        'name': 'Normal path: update memory',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_update(text='New Memory')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_retrieve()"}
        ]
    },
    {
        'name': 'Normal path: replace text in memory',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_update(text='Replace this text.')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_replace(old_text='this', new_text='that')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_retrieve()"}
        ]
    },
    {
        'name': 'Normal path: clear memory',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_update(text='To be cleared')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_clear()"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_retrieve()"}
        ]
    },
    {
        'name': 'Boundary values: empty strings',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_update(text='')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_append(text='')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_replace(old_text='', new_text='')"}
        ]
    },
    {
        'name': 'Boundary values: excessively long string',
        'steps': [
            {
                'expect_success': True,
                'tool_call': "env['memory_rec_sum'].memory_update(text='A very long string that goes on and "
                             'on and on and on and on and on and on and on and on and on and on and on and on '
                             'and on and on and on and on and on and on and on and on and on and on and on '
                             'and on and on and on and on and on and on and on and on and on and on and on '
                             'and on and on and on and on and on and on and on and on and on and on and on '
                             'and on and on and on and on and on and on and on and on and on and on and on '
                             'and on and on and on and on and on and on and on and on and on and on and on '
                             'and on and on and on and on and on and on and on and on and on and on and on '
                             "and on and on and on and on and on and on and on and on and on and on')"
            },
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_retrieve()"}
        ]
    },
    {
        'name': 'Error path: missing required fields',
        'steps': [
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_append()"},
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_update()"},
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_replace(old_text='old')"}
        ]
    },
    {
        'name': 'Error path: wrong parameter types',
        'steps': [
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_append(text=123)"},
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_update(text=['array'])"},
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_replace(old_text=True, new_text=False)"}
        ]
    },
    {
        'name': 'State-change verification: modify state then query to confirm',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_update(text='Initial state')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].get_env_state()"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_append(text=' appended')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].get_env_state()"}
        ]
    },
    {
        'name': 'Cross-method workflows: clear, append, replace, retrieve, update',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_clear()"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_append(text='First sentence.')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_append(text=' Second sentence.')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_replace(old_text='Second', new_text='Third')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_retrieve()"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_update(text='Completely new text.')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_retrieve()"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_clear()"}
        ]
    },
    {
        'name': 'New methods: summarize and archive',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_update(text='Long text to summarize and archive')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_archive_oldest(chunk_size=5)"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_summarize(instruction='keep it short')"}
        ]
    },
    {
        'name': 'New methods: search and context extraction',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_update(text='The quick brown fox jumps over the lazy dog')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_search(query='fox')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_extract_context(target_text='jumps', window_size=5)"}
        ]
    },
    {
        'name': 'New methods: capacity and prepend',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_clear()"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_get_capacity()"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_prepend(text='System prompt: be helpful. ')"}
        ]
    },
    {
        'name': 'New methods: delete and insert_after',
        'steps': [
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_update(text='123456789')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_delete(target_text='456')"},
            {'expect_success': True, 'tool_call': "env['memory_rec_sum'].memory_insert_after(anchor_text='123', new_text='abc')"}
        ]
    },
    {
        'name': 'New methods: error paths',
        'steps': [
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_summarize(instruction=123)"},
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_archive_oldest(chunk_size=-5)"},
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_search(query='')"},
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_extract_context(target_text='', window_size=5)"},
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_delete(target_text='')"},
            {'expect_success': False, 'tool_call': "env['memory_rec_sum'].memory_insert_after(anchor_text='', new_text='abc')"}
        ]
    }
]
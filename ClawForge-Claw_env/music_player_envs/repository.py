from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MusicRepository:
    def __init__(self, data_root: Path | str):
        self.data_root = Path(data_root)

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        full_path = self.data_root / relative_path
        with open(full_path, encoding="utf-8") as f:
            return json.load(f)

    def get_account(self, account_id: str) -> dict[str, Any] | None:
        accounts = self._load_json("accounts.json")
        if isinstance(accounts, list):
            for acc in accounts:
                if acc.get("account_id") == account_id:
                    return acc
        elif isinstance(accounts, dict) and accounts.get("account_id") == account_id:
            return accounts
        return None

    def list_accounts(self) -> list[dict[str, Any]]:
        accounts = self._load_json("accounts.json")
        if isinstance(accounts, list):
            return accounts
        return [accounts]

    def get_song(self, song_id: str) -> dict[str, Any] | None:
        data = self._load_json("songs/songs.json")
        for song in data.get("songs", []):
            if song.get("song_id") == song_id:
                return song
        return None

    def list_songs(self) -> list[dict[str, Any]]:
        data = self._load_json("songs/songs.json")
        return data.get("songs", [])

    def search_songs(
        self,
        title: str | None = None,
        artist: str | None = None,
        album: str | None = None,
        brand: str | None = None,
        tag: str | None = None,
        scene: str | None = None,
        style: str | None = None,
        language: str | None = None,
        era: str | None = None,
        crowd: str | None = None,
    ) -> list[dict[str, Any]]:
        songs = self.list_songs()
        results = []

        for song in songs:
            if title and title.lower() in song.get("title", "").lower():
                results.append(song)
                continue
            if artist and artist.lower() in song.get("artist", "").lower():
                results.append(song)
                continue
            if album and album.lower() in song.get("album", "").lower():
                results.append(song)
                continue
            if brand and song.get("brand_theme") and brand.lower() in song.get("brand_theme", "").lower():
                results.append(song)
                continue
            if tag and tag in song.get("tags", []):
                results.append(song)
                continue
            if scene and scene in song.get("scene_tags", []):
                results.append(song)
                continue
            if style and style.lower() in song.get("style", "").lower():
                results.append(song)
                continue
            if language and language == song.get("language"):
                results.append(song)
                continue
            if era and era == song.get("era"):
                results.append(song)
                continue
            if crowd and crowd in song.get("crowd_tags", []):
                results.append(song)
                continue

        return results

    def get_similar_songs(self, song_id: str, limit: int = 5) -> list[dict[str, Any]]:
        song = self.get_song(song_id)
        if not song:
            return []

        songs = self.list_songs()
        scored = []

        for other in songs:
            if other["song_id"] == song_id:
                continue
            score = 0
            common_tags = set(song.get("tags", [])) & set(other.get("tags", []))
            score += len(common_tags) * 2
            if song.get("artist") == other.get("artist"):
                score += 5
            if song.get("genre") == other.get("genre"):
                score += 3
            if song.get("style") == other.get("style"):
                score += 3
            if song.get("language") == other.get("language"):
                score += 2
            scored.append((score, other))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:limit]]

    def get_playlist(self, playlist_id: str) -> dict[str, Any] | None:
        data = self._load_json("playlists/playlists.json")
        for pl in data.get("playlists", []):
            if pl.get("playlist_id") == playlist_id:
                return pl
        return None

    def list_playlists(self) -> list[dict[str, Any]]:
        data = self._load_json("playlists/playlists.json")
        return data.get("playlists", [])

    def get_scenario(self, scenario_id: str) -> dict[str, Any] | None:
        scenario_path = self.data_root / "scenarios" / f"{scenario_id}.json"
        if not scenario_path.exists():
            return None
        with open(scenario_path, encoding="utf-8") as f:
            return json.load(f)

    def list_scenarios(self) -> list[dict[str, Any]]:
        scenarios_dir = self.data_root / "scenarios"
        if not scenarios_dir.exists():
            return []
        scenarios = []
        for f in scenarios_dir.glob("*.json"):
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
                scenarios.append({
                    "scenario_id": data.get("scenario_id", f.stem),
                    "title": data.get("title", ""),
                    "task_prompt": data.get("task_prompt", ""),
                })
        return scenarios

    def get_tag_definitions(self) -> dict[str, Any]:
        return self._load_json("tags/tag_definitions.json")

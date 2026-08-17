from __future__ import annotations

from typing import Any

if False:
    from .repository import DatasetRepository


class SearchEngine:
    def __init__(self, repo: DatasetRepository):
        self._repo = repo


def search_songs(
    eng: SearchEngine,
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
    similar_to: str | None = None,
) -> dict[str, Any]:
    if similar_to:
        songs = eng._repo.get_similar_songs(similar_to, limit=10)
        return {"status": "ok", "data": songs, "count": len(songs)}

    songs = eng._repo.search_songs(
        title=title,
        artist=artist,
        album=album,
        brand=brand,
        tag=tag,
        scene=scene,
        style=style,
        language=language,
        era=era,
        crowd=crowd,
    )
    return {"status": "ok", "data": songs, "count": len(songs)}


def list_songs(eng: SearchEngine) -> dict[str, Any]:
    songs = eng._repo.list_songs()
    return {"status": "ok", "data": songs, "count": len(songs)}


def list_playlists(eng: SearchEngine) -> dict[str, Any]:
    playlists = eng._repo.list_playlists()
    return {"status": "ok", "data": playlists, "count": len(playlists)}

from copy import deepcopy
from typing import Dict, List, Optional, Union, Any

DEFAULT_MUSIC_STATE = {
    "current_user": None,
    "users": {
        "alice": {"subscription": "free", "liked_songs": [101], "play_count": 0},
        "bob": {"subscription": "premium", "liked_songs": [], "play_count": 500},
    },
    "songs": {
        101: {"id": 101, "title": "Bohemian Rhapsody", "artist": "Queen", "is_premium": False, "streams": 1500000},
        102: {"id": 102, "title": "Shape of You", "artist": "Ed Sheeran", "is_premium": False, "streams": 2000000},
        103: {"id": 103, "title": "Symphony No. 9", "artist": "Beethoven", "is_premium": True, "streams": 50000},
    },
    "playlists": {
        1: {"id": 1, "owner": "alice", "name": "My Favorites", "songs": [101]},
    },
    "playing_queue": [],
    "playlist_counter": 2,
}


class MusicPlayerAPI:
    """
    A complex Music Player API that handles subscriptions, playlists, and playing queues.
    Premium songs require a premium subscription to be added to the queue or played.
    """

    def __init__(self):
        self.current_user: Optional[str] = None
        self.users: Dict[str, Dict[str, Union[str, List[int], int]]] = {}
        self.songs: Dict[int, Dict[str, Union[int, str, bool]]] = {}
        self.playlists: Dict[int, Dict[str, Union[int, str, List[int]]]] = {}
        self.playing_queue: List[int] = []
        self.playlist_counter: int = 2
        self._api_description = "A music streaming platform that manages songs, user subscriptions, playlists, and playback queues."

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_MUSIC_STATE)
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.users = scenario.get("users", DEFAULT_STATE_COPY["users"])
        self.songs = {int(k) if str(k).isdigit() else k: v for k, v in
                      scenario.get("songs", DEFAULT_STATE_COPY["songs"]).items()}
        self.playlists = {int(k) if str(k).isdigit() else k: v for k, v in
                          scenario.get("playlists", DEFAULT_STATE_COPY["playlists"]).items()}
        self.playing_queue = scenario.get("playing_queue", DEFAULT_STATE_COPY["playing_queue"])
        self.playlist_counter = scenario.get("playlist_counter", DEFAULT_STATE_COPY["playlist_counter"])

    def get_env_state(self):
        return {
            "current_user": self.current_user,
            "users": self.users,
            "songs": self.songs,
            "playlists": self.playlists,
            "playing_queue": self.playing_queue,
            "playlist_counter": self.playlist_counter,
        }

    def login(self, username: str) -> Dict[str, Union[bool, str]]:
        if username not in self.users:
            return {"success": False, "error": "User not found."}
        self.current_user = username
        return {"success": True, "message": f"Logged in as {username}. Tier: {self.users[username]['subscription']}"}

    def upgrade_subscription(self) -> Dict[str, str]:
        if not self.current_user:
            return {"error": "Authentication required."}
        if self.users[self.current_user]["subscription"] == "premium":
            return {"status": "Already a premium member."}
        self.users[self.current_user]["subscription"] = "premium"
        return {"status": "Successfully upgraded to premium."}

    def create_playlist(self, name: str) -> Dict[str, Union[int, str]]:
        if not self.current_user:
            return {"error": "Authentication required."}
        p_id = self.playlist_counter
        self.playlists[p_id] = {"id": p_id, "owner": self.current_user, "name": name, "songs": []}
        self.playlist_counter += 1
        return {"id": p_id, "status": f"Playlist '{name}' created."}

    def play_song(self, song_id: int) -> Dict[str, str]:
        """Plays a song. Checks premium constraints."""
        if not self.current_user:
            return {"error": "Authentication required."}
        if song_id not in self.songs:
            return {"error": "Song not found."}

        song = self.songs[song_id]
        user_tier = self.users[self.current_user]["subscription"]

        if song["is_premium"] and user_tier != "premium":
            return {"error": f"Cannot play '{song['title']}'. Premium subscription required."}

        # Simulate playing
        self.songs[song_id]["streams"] += 1
        self.users[self.current_user]["play_count"] += 1
        self.playing_queue = [song_id] + self.playing_queue  # Add to front of queue
        return {"status": f"Now playing: {song['title']} by {song['artist']}"}

    def toggle_like(self, song_id: int) -> Dict[str, str]:
        if not self.current_user:
            return {"error": "Authentication required."}
        if song_id not in self.songs:
            return {"error": "Song not found."}

        liked_list = self.users[self.current_user]["liked_songs"]
        if song_id in liked_list:
            liked_list.remove(song_id)
            return {"status": f"Removed song {song_id} from liked songs."}
        else:
            liked_list.append(song_id)
            return {"status": f"Added song {song_id} to liked songs."}

    def add_song_to_playlist(self, playlist_id: int, song_id: int) -> Dict[str, str]:
        """Adds a specific song to a playlist owned by the current user."""
        if not self.current_user:
            return {"error": "Authentication required."}
        if playlist_id not in self.playlists:
            return {"error": "Playlist not found."}
        if self.playlists[playlist_id]["owner"] != self.current_user:
            return {"error": "Not authorized to modify this playlist."}
        if song_id not in self.songs:
            return {"error": "Song not found."}
        
        songs_list = self.playlists[playlist_id]["songs"]
        if song_id in songs_list:
            return {"error": "Song already in the playlist."}
            
        songs_list.append(song_id)
        return {"status": f"Song {song_id} successfully added to playlist {playlist_id}."}

    def remove_song_from_playlist(self, playlist_id: int, song_id: int) -> Dict[str, str]:
        """Removes a specific song from a playlist owned by the current user."""
        if not self.current_user:
            return {"error": "Authentication required."}
        if playlist_id not in self.playlists:
            return {"error": "Playlist not found."}
        if self.playlists[playlist_id]["owner"] != self.current_user:
            return {"error": "Not authorized to modify this playlist."}
            
        songs_list = self.playlists[playlist_id]["songs"]
        if song_id not in songs_list:
            return {"error": "Song is not in the playlist."}
            
        songs_list.remove(song_id)
        return {"status": f"Song {song_id} removed from playlist {playlist_id}."}

    def search_songs(self, query: str) -> Dict[str, Any]:
        """Searches for songs by title or artist matching the query string."""
        query_lower = query.lower()
        results = []
        for s_id, song in self.songs.items():
            if query_lower in str(song["title"]).lower() or query_lower in str(song["artist"]).lower():
                results.append({
                    "id": s_id, 
                    "title": song["title"], 
                    "artist": song["artist"], 
                    "is_premium": song["is_premium"]
                })
        return {"status": f"Found {len(results)} songs.", "results": results}

    def add_to_queue(self, song_id: int) -> Dict[str, str]:
        """Adds a song to the end of the playing queue. Verifies premium constraints."""
        if not self.current_user:
            return {"error": "Authentication required."}
        if song_id not in self.songs:
            return {"error": "Song not found."}
            
        song = self.songs[song_id]
        user_tier = self.users[self.current_user]["subscription"]
        
        if song["is_premium"] and user_tier != "premium":
            return {"error": f"Cannot add '{song['title']}' to queue. Premium subscription required."}
            
        self.playing_queue.append(song_id)
        return {"status": f"Added {song['title']} to the end of the queue."}

    def play_next(self) -> Dict[str, str]:
        """Plays the next song from the playing queue and simulates a stream count update."""
        if not self.current_user:
            return {"error": "Authentication required."}
        if not self.playing_queue:
            return {"error": "Playing queue is empty."}
            
        next_song_id = self.playing_queue.pop(0)
        
        if next_song_id not in self.songs:
            return {"error": f"Queued song with ID {next_song_id} no longer exists."}
            
        song = self.songs[next_song_id]
        self.songs[next_song_id]["streams"] += 1
        self.users[self.current_user]["play_count"] += 1
        
        return {"status": f"Now playing from queue: {song['title']} by {song['artist']}"}

    def delete_playlist(self, playlist_id: int) -> Dict[str, str]:
        """Deletes a playlist owned by the current user."""
        if not self.current_user:
            return {"error": "Authentication required."}
        if playlist_id not in self.playlists:
            return {"error": "Playlist not found."}
        if self.playlists[playlist_id]["owner"] != self.current_user:
            return {"error": "Not authorized to delete this playlist."}
            
        del self.playlists[playlist_id]
        return {"status": f"Playlist {playlist_id} deleted successfully."}

    def clear_queue(self) -> Dict[str, str]:
        """Clears all songs currently in the playing queue."""
        if not self.current_user:
            return {"error": "Authentication required."}
        self.playing_queue.clear()
        return {"status": "Playing queue cleared."}

    def get_playlist_details(self, playlist_id: int) -> Dict[str, Any]:
        """Returns detailed information and complete metadata of all songs in a playlist."""
        if not self.current_user:
            return {"error": "Authentication required."}
        if playlist_id not in self.playlists:
            return {"error": "Playlist not found."}
            
        playlist = self.playlists[playlist_id]
        song_details = []
        for s_id in playlist["songs"]:
            if s_id in self.songs:
                song_details.append(self.songs[s_id])
                
        return {
            "id": playlist["id"],
            "name": playlist["name"],
            "owner": playlist["owner"],
            "song_count": len(song_details),
            "songs": song_details
        }

__TEST_CASES__ = [
    {   'name': 'Normal Path - Login and Play Free Song',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].login(username='alice')"},
                     {'expect_success': True, 'tool_call': "env['music'].play_song(song_id=101)"},
                     {'expect_success': True, 'tool_call': "env['music'].get_env_state()"}]},
    {   'name': 'Error Path - Play Premium Song as Free User',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].login(username='alice')"},
                     {'expect_success': False, 'tool_call': "env['music'].play_song(song_id=103)"}]},
    {   'name': 'Normal Path - Premium User Plays Premium Song',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].login(username='bob')"},
                     {'expect_success': True, 'tool_call': "env['music'].play_song(song_id=103)"},
                     {'expect_success': True, 'tool_call': "env['music'].get_env_state()"}]},
    {   'name': 'Cross-method Workflow - Upgrade Subscription and Play Premium Song',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].login(username='alice')"},
                     {'expect_success': True, 'tool_call': "env['music'].upgrade_subscription()"},
                     {'expect_success': True, 'tool_call': "env['music'].play_song(song_id=103)"},
                     {'expect_success': True, 'tool_call': "env['music'].get_env_state()"}]},
    {   'name': 'State-change Verification - Toggle Like',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].login(username='alice')"},
                     {'expect_success': True, 'tool_call': "env['music'].toggle_like(song_id=102)"},
                     {'expect_success': True, 'tool_call': "env['music'].get_env_state()"},
                     {'expect_success': True, 'tool_call': "env['music'].toggle_like(song_id=102)"},
                     {'expect_success': True, 'tool_call': "env['music'].get_env_state()"}]},
    {   'name': 'Boundary Values - Create Playlist with Empty Name and Excessively Long Name',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].login(username='bob')"},
                     {'expect_success': True, 'tool_call': "env['music'].create_playlist(name='')"},
                     {   'expect_success': True,
                         'tool_call': "env['music'].create_playlist(name='ThisIsAVeryLongPlaylistNameThatMightExceedSomeLimitsOrMaybeNotButItIsGoodToTest')"}]},
    {   'name': 'Error Path - Non-existent Song ID and Invalid Username',
        'steps': [   {'expect_success': False, 'tool_call': "env['music'].login(username='charlie')"},
                     {'expect_success': True, 'tool_call': "env['music'].login(username='bob')"},
                     {'expect_success': False, 'tool_call': "env['music'].play_song(song_id=999)"},
                     {'expect_success': False, 'tool_call': "env['music'].toggle_like(song_id=-1)"}]},
    {   'name': 'Error Path - Operations Without Login',
        'steps': [   {'expect_success': False, 'tool_call': "env['music'].play_song(song_id=101)"},
                     {'expect_success': False, 'tool_call': "env['music'].create_playlist(name='My Playlist')"},
                     {'expect_success': False, 'tool_call': "env['music'].toggle_like(song_id=101)"},
                     {'expect_success': False, 'tool_call': "env['music'].upgrade_subscription()"}]},
    {   'name': 'Normal Path - Create Playlist and Verify State',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].login(username='alice')"},
                     {'expect_success': True, 'tool_call': "env['music'].create_playlist(name='Workout Mix')"},
                     {'expect_success': True, 'tool_call': "env['music'].get_env_state()"}]},
    {   'name': 'Boundary Values - Play Song ID 0',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].login(username='bob')"},
                     {'expect_success': False, 'tool_call': "env['music'].play_song(song_id=0)"}]},
    {   'name': 'New Feature - Playlist Lifecycle Management',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].login(username='alice')"},
                     {'expect_success': True, 'tool_call': "env['music'].create_playlist(name='Road Trip')"},
                     {'expect_success': True, 'tool_call': "env['music'].add_song_to_playlist(playlist_id=2, song_id=102)"},
                     {'expect_success': True, 'tool_call': "env['music'].get_playlist_details(playlist_id=2)"},
                     {'expect_success': True, 'tool_call': "env['music'].remove_song_from_playlist(playlist_id=2, song_id=102)"},
                     {'expect_success': True, 'tool_call': "env['music'].delete_playlist(playlist_id=2)"},
                     {'expect_success': False, 'tool_call': "env['music'].get_playlist_details(playlist_id=2)"}]},
    {   'name': 'New Feature - Search and Queue Management',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].search_songs(query='queen')"},
                     {'expect_success': True, 'tool_call': "env['music'].login(username='bob')"},
                     {'expect_success': True, 'tool_call': "env['music'].add_to_queue(song_id=101)"},
                     {'expect_success': True, 'tool_call': "env['music'].add_to_queue(song_id=103)"},
                     {'expect_success': True, 'tool_call': "env['music'].play_next()"},
                     {'expect_success': True, 'tool_call': "env['music'].clear_queue()"},
                     {'expect_success': False, 'tool_call': "env['music'].play_next()"}]},
    {   'name': 'New Feature - Error Paths for Playlist and Queue',
        'steps': [   {'expect_success': True, 'tool_call': "env['music'].login(username='alice')"},
                     {'expect_success': False, 'tool_call': "env['music'].add_song_to_playlist(playlist_id=99, song_id=101)"},
                     {'expect_success': False, 'tool_call': "env['music'].add_to_queue(song_id=103)"},
                     {'expect_success': False, 'tool_call': "env['music'].play_next()"}]}
]
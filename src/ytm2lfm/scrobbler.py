import time
from typing import Any, Dict, List

from ytm2lfm.database import SQLite
from ytm2lfm.lastfm import LastFMClient
from ytm2lfm.logger import get_logger
from ytm2lfm.utils import find_overlap_start_index
from ytm2lfm.ytmusic import YTMusicClient

logger = get_logger(__name__)


class Scrobbler:
    def __init__(
        self, lastfm_client: LastFMClient, ytmusic_client: YTMusicClient, database: SQLite, min_overlap_length: int = 50
    ):
        """
        Initialize the Scrobbler with necessary clients and configuration.

        Args:
            lastfm_client: Authenticated Last.fm client
            ytmusic_client: Authenticated YouTube Music client
            database: SQLite database instance
            min_overlap_length: Minimum number of matching tracks required to detect an overlap
        """
        self.lastfm = lastfm_client
        self.ytmusic = ytmusic_client
        self.db = database
        self.min_overlap_length = min_overlap_length

    def get_tracks_to_scrobble(self) -> List[Dict[str, Any]]:
        """
        Determine which tracks need to be scrobbled by comparing YouTube Music history
        with previously scrobbled tracks.

        Returns:
            List of tracks that need to be scrobbled (the new tracks not previously scrobbled)
        """
        # Get recent tracks from YT Music
        tracks_history = self._get_recently_played()

        # Ensure we have enough history for overlap detection
        if len(tracks_history) < self.min_overlap_length:
            logger.warning(
                f"Not enough YT Music history. Found {len(tracks_history)} entries "
                f"but need at least {self.min_overlap_length}"
            )
            return []

        # Get already scrobbled tracks from database
        tracks_scrobbled = self.db.fetch_latest_scrobbles()

        # Find where the history starts to overlap with already scrobbled tracks
        overlap_idx = find_overlap_start_index(
            [track["video_id"] for track in tracks_history],
            [track["video_id"] for track in tracks_scrobbled],
            self.min_overlap_length,
        )

        # If we found an overlap, everything before that index is new and needs scrobbling
        if overlap_idx is not None:
            tracks_to_scrobble = tracks_history[:overlap_idx]
            logger.info(f"Found {len(tracks_to_scrobble)} new tracks to scrobble (overlap at index {overlap_idx})")
        else:
            # No overlap found - all tracks are new
            tracks_to_scrobble = tracks_history
            logger.info(f"No overlap found with existing scrobbles.")

        return tracks_to_scrobble

    def scrobble_tracks(self, tracks: List[Dict[str, Any]], batch_size: int = 50, store=False, dry_run=False) -> int:
        """
        Scrobble tracks to Last.fm and save them to the database.

        Args:
            tracks: List of tracks to scrobble
            batch_size: Number of tracks to process in each batch
            store: Populates database without scrobbling
            dry_run: Run without side effects

        Returns:
            Number of tracks successfully scrobbled
        """
        if not tracks:
            logger.info("No new tracks to scrobble")
            return 0

        # Add timestamp and reverse to process oldest first
        epoch_time = int(time.time())
        tracks_to_scrobble = [track | {"timestamp": epoch_time} for track in tracks]
        tracks_to_scrobble.reverse()

        scrobbled_count = 0
        for i in range(0, len(tracks_to_scrobble), batch_size):
            try:
                tracks_batch = tracks_to_scrobble[i : i + batch_size]
                if not store or dry_run:
                    self.lastfm.scrobble_many(tracks_batch)
                    scrobbled_count += len(tracks_batch)

                if dry_run:
                    logger.info("Dry-run: Skip inserting tracks in database.")
                else:
                    self.db.insert_tracks(tracks_batch)
                    time.sleep(0.5)  # Avoid rate limiting
            except Exception as e:
                logger.error(f"Failed to scrobble batch starting at index {i}: {str(e)}", exc_info=True)
                raise

        return scrobbled_count

    def cleanup_database(self, dry_run=False, keep_latest: int = 200):
        """
        Clean up the database by keeping only the most recent entries.

        Args:
            dry_run: Run without side effects
            keep_latest: Number of most recent entries to keep
        """
        if dry_run:
            logger.info(f"Dry-run: skipped cleaning database to keep only {keep_latest} entries")
        else:
            self.db.delete_except_latest_n(keep_latest)
            logger.info(f"Database cleaned up, keeping latest {keep_latest} entries")
            

    def _get_recently_played(self) -> List[Dict[str, Any]]:
        """Get recently played tracks from YouTube Music"""
        try:
            history = self.ytmusic.get_history()
            logger.info(f"Fetched {len(history)} recent tracks from YouTube Music")

            processed = []
            for track in history:
                # Skip keys with None values
                for k in list(track.keys()):
                    if track[k] is None:
                        track.pop(k)

                if "title" not in track or "artists" not in track:
                    continue

                processed.append(
                    {
                        "video_id": track["videoId"],
                        "title": track["title"],
                        "artist": ", ".join(
                            [artist["name"] for artist in track["artists"] if not artist["name"].endswith(" views")]
                        ),
                        "album": track.get("album", {}).get("name", ""),
                        "played": track["played"],
                    }
                )

            return processed
        except Exception as e:
            logger.error(f"Failed to process YouTube Music history: {str(e)}")
            raise

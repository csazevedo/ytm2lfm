from typing import Any, Dict, List

from ytmusicapi import OAuthCredentials, YTMusic

from ytm2lfm.logger import get_logger

logger = get_logger(__name__)


class YTMusicClient(YTMusic):
    def __init__(self, auth_file: str, client_id: str, client_secret: str):
        """
        Initialize YouTube Music client with OAuth credentials.

        Args:
            auth_file: Path to OAuth credentials file
            client_id: Google API client ID
            client_secret: Google API client secret
        """
        try:
            super().__init__(
                auth_file,
                oauth_credentials=OAuthCredentials(client_id=client_id, client_secret=client_secret),
            )
            logger.info("YouTube Music client initialized")
        except Exception as e:
            logger.error(f"YouTube Music authentication failed: {e}")
            raise

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get and process the user's YouTube Music listening history.

        Returns:
            List of processed track dictionaries
        """
        try:
            # Call the parent class method to get raw history
            history = super().get_history()
            return history

        except Exception as e:
            logger.error(f"Failed to fetch YouTube Music history: {e}")
            raise

    def _is_valid_track(self, track: Dict[str, Any]) -> bool:
        """
        Check if a track has the required fields.

        Args:
            track: Track data from YTMusic API

        Returns:
            True if the track is valid, False otherwise
        """
        # Remove None values
        for k in list(track.keys()):
            if track[k] is None:
                track.pop(k)

        return "title" in track and "artists" in track and "videoId" in track

    def _format_artists(self, artists: List[Dict[str, Any]]) -> str:
        """
        Format the artists list into a comma-separated string.

        Args:
            artists: List of artist dictionaries

        Returns:
            Comma-separated string of artist names
        """
        return ", ".join([artist["name"] for artist in artists if not artist["name"].endswith(" views")])

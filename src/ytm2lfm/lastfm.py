import pylast

from ytm2lfm.logger import get_logger

logger = get_logger(__name__)


class LastFMClient(pylast.LastFMNetwork):
    """Client for interacting with Last.fm API."""

    def __init__(self, api_key: str, api_secret: str, username: str, password: str):
        """
        Initialize and authenticate with Last.fm API.

        Args:
            api_key: Last.fm API key
            api_secret: Last.fm API secret
            username: Last.fm username
            password: Last.fm password (will be hashed)

        Raises:
            pylast.WSError: If authentication fails
        """
        try:
            super().__init__(
                api_key=api_key,
                api_secret=api_secret,
                username=username,
                password_hash=pylast.md5(password),
            )

            # Verify authentication
            self.get_authenticated_user()
            logger.info("Successfully authenticated with Last.fm")
        except pylast.WSError as e:
            logger.error("Last.fm authentication failed: %s", e)
            raise

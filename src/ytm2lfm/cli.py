import argparse
import sys

from ytm2lfm.config import settings
from ytm2lfm.database import SQLite
from ytm2lfm.lastfm import LastFMClient
from ytm2lfm.logger import get_logger
from ytm2lfm.scrobbler import Scrobbler
from ytm2lfm.ytmusic import YTMusicClient

logger = get_logger(__name__)


def run_scrobble(dry_run=False):
    # Initialize components
    db = SQLite(settings.sqlite.db_path)

    lastfm = LastFMClient(
        api_key=settings.lastfm.api_key,
        api_secret=settings.lastfm.shared_secret,
        username=settings.lastfm.registered_to,
        password=settings.lastfm.password,
    )

    ytmusic = YTMusicClient(
        auth_file=settings.ytmusic.auth_file,
        client_id=settings.ytmusic.client_id,
        client_secret=settings.ytmusic.client_secret,
    )

    # Create and run the scrobbler
    scrobbler = Scrobbler(lastfm, ytmusic, db)

    try:
        # Get tracks that need to be scrobbled
        tracks_to_scrobble = scrobbler.get_tracks_to_scrobble()

        # Scrobble the tracks
        scrobbler.scrobble_tracks(tracks_to_scrobble, dry_run=dry_run)

        # Clean up database to keep it from growing too large
        scrobbler.cleanup_database()

        logger.info("Scrobbling process completed successfully")
    except Exception as e:
        logger.error(f"Scrobbling process failed: {str(e)}", exc_info=True)
        raise


def setup_cli():
    """Set up the command-line interface."""
    parser = argparse.ArgumentParser(
        description="YTMusic to Last.fm Scrobbler CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py scrobble    # Normal scrobbling operation
  python cli.py store       # Store tracks without scrobbling
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scrobble command
    subparsers.add_parser("scrobble", help="Scrobble tracks from YTMusic to Last.fm")

    # Store command
    subparsers.add_parser("store", help="Store tracks in database without scrobbling")

    return parser


def main():
    parser = setup_cli()
    args = parser.parse_args()

    if args.command == "scrobble":
        tracks = run_scrobble(dry_run=False)
        print(f"Scrobbled {len(tracks) if tracks else 0} tracks to Last.fm")

    elif args.command == "store":
        tracks = run_scrobble(dry_run=True)
        print(f"Stored {len(tracks) if tracks else 0} tracks in database without scrobbling")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

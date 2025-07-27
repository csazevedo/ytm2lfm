import argparse
import logging
import os
import sys
import textwrap

from ytm2lfm.config import settings
from ytm2lfm.database import SQLite
from ytm2lfm.lastfm import LastFMClient
from ytm2lfm.logger import setup_logging
from ytm2lfm.scrobbler import Scrobbler
from ytm2lfm.ytmusic import YTMusicClient

setup_logging()
logger = logging.getLogger(__name__)


def run_scrobble(sync=False, dry_run=False):
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
        scrobbler.scrobble_tracks(tracks_to_scrobble, sync=sync, dry_run=dry_run)

        # Clean up database to keep it from growing too large
        scrobbler.cleanup_database(dry_run=dry_run)

        logger.info("Scrobbling process completed successfully")

        return tracks_to_scrobble
    except Exception as e:
        logger.error(f"Scrobbling process failed: {str(e)}", exc_info=True)
        raise


def setup_cli():
    """Set up the command-line interface."""
    cli_relative_path = os.path.relpath(sys.argv[0])
    epilog = textwrap.dedent(
        f"""
            Examples:
                python {cli_relative_path} scrobble    # Normal scrobbling operation
                python {cli_relative_path} sync        # Sync tracks without scrobbling
                python {cli_relative_path} dry-run     # Dry-run
        """
    )
    parser = argparse.ArgumentParser(
        description="YTMusic to Last.fm Scrobbler CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scrobble command
    subparsers.add_parser("scrobble", help="Scrobble tracks from YTMusic to Last.fm")

    # Sync command
    subparsers.add_parser("sync", help="Sync tracks in database without scrobbling")

    # Dry-run command
    subparsers.add_parser("dry-run", help="Dry-run")

    return parser


def main():
    parser = setup_cli()
    args = parser.parse_args()

    if args.command == "scrobble":
        tracks = run_scrobble(sync=False, dry_run=False)
        logger.info(f"Scrobbled {len(tracks) if tracks else 0} tracks to Last.fm")

    elif args.command == "sync":
        tracks = run_scrobble(sync=True, dry_run=False)
        logger.info(f"Synced {len(tracks) if tracks else 0} tracks in database without scrobbling")

    elif args.command == "dry-run":
        tracks = run_scrobble(sync=False, dry_run=True)
        logger.info(f"Dry-run finished. Would scrobble {len(tracks) if tracks else 0} tracks to Last.fm")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

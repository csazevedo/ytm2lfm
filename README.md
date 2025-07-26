# YTM2LFM - YouTube Music to Last.fm Scrobbler

[![CI](https://github.com/csazevedo/ytm2lfm/actions/workflows/ci.yaml/badge.svg)](https://github.com/csazevedo/ytm2lfm/actions/workflows/ci.yaml)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Introduction

A simple tool to scrobble your YouTube Music listening history to Last.fm.

## How It Works

The scrobbler works by:
1. Fetching your YouTube Music listening history
2. Comparing it with previously scrobbled tracks in the database
3. Identifying new tracks that need to be scrobbled
4. Sending those tracks to Last.fm and storing them in the database

## Features

- Automatically scrobbles tracks from your YouTube Music history to Last.fm
- Keeps track of what has already been scrobbled to avoid duplicates
- Simple CLI interface
- Uses [ytmusicapi](https://github.com/sigma67/ytmusicapi) to fetch the most recent YouTube Music play history
- Uses [pylast](https://github.com/pylast/pylast) to scrobble new tracks to Last.fm
- Uses SQLite to sync/store scrobbled tracks and detect new ones

## Limitations

- YouTube Music history is limited to the last 200 tracks by the YouTube Music API
- If you run this tool regularly (e.g., daily), this limitation shouldn't be a problem
- When the same track is played multiple times, YouTube Music moves it to the top of history rather than creating duplicate entries - this means repeated plays may not be scrobbled separately

## Installation

The easiest way to use YTM2LFM is with Docker:

1. Clone this repository
2. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the required credentials:
     - Get Last.fm API credentials from [Last.fm API](https://www.last.fm/api/account/create)
     - Set up Google OAuth credentials at [Google Developer Console](https://console.developers.google.com) and make sure you get the oatuh.json file that looks like:
     ```
      {
         "scope": "https://www.googleapis.com/auth/youtube",
         "token_type": "Bearer",
         "access_token": ?,
         "refresh_token": ?,
         "expires_at": ?,
         "expires_in": ?
      }
     ```

## Usage

### Configuration

All configuration is handled through environment variables.

Copy `.env.example` into `.env` or create a new `.env` file with the following variables:

```
# Last.fm API Credentials
LASTFM__API_KEY=your_lastfm_api_key
LASTFM__SHARED_SECRET=your_lastfm_shared_secret
LASTFM__REGISTERED_TO=your_lastfm_username
LASTFM__PASSWORD=your_lastfm_password

# YouTube Music Credentials
YTMUSIC__AUTH_FILE=path/to/oauth.json
YTMUSIC__CLIENT_ID=your_google_client_id
YTMUSIC__CLIENT_SECRET=your_google_client_secret

# Database Configuration
SQLITE__DB_PATH=path/to/database.sqlite

# Scrobbler Configuration (Optional)
# with the following default values you just need to make sure to not play more than 150 tracks between 2 consecutive runs of ytm2lfm
SCROBBLER__SEQUENCE_MATCH_LENGTH = 50
SCROBBLER__BATCH_SIZE = 50
SCROBBLER__MAX_SYNCED_TRACKS = 200
```

#### Last.fm Authentication

1. Create a Last.fm API account at [Last.fm API](https://www.last.fm/api/account/create)
2. Get your API key and shared secret
3. Add them to your `.env` file

#### YouTube Music Authentication

1. Set up a project in [Google Developer Console](https://console.developers.google.com)
2. Enable the YouTube Data API
3. Create OAuth credentials (Desktop application)
4. Download OAuth credentials JSON file and save it to the location specified in your `.env` file

### Run locally for development

#### Scrobble your YouTube Music history to Last.fm:

```bash
make docker-scrobble
```

On first run, these commands will fetch your YouTube Music history (last 200 plays) and scrobble it to Last.fm. On subsequent runs, only new tracks will be scrobbled.

#### Sync tracks without scrobbling:

If you don't want to scrobble your entire history on the first run, you can use these commands to sync the history without scrobbling:

```bash
make docker-sync
```

This will populate the database with your current history, so the next time you run scrobble, it will only scrobble new tracks after the `sync` run.

#### Dry-run

This allows to test the run without any side-effects (no syncing or scrobbling).

```bash
make docker-dry-run
```

## Scheduling runs

### General

While there are many ways to schedule periodic runs, here is the simplest one that doesn't require any extra configuration besides running `docker compose up`:
```
services:
ytm2lfm:
   image: csazev/ytm2lfm:latest  # you might want to pin a specific version here
   container_name: ytm2lfm
   command: ["python", "/app/src/cli.py", "scrobble"]
   volumes:
   - ./oauth.json:/app/oauth.json  # should match the path of env var YTMUSIC__AUTH_FILE
   - ./sqlite:/app/sqlite  # should match the path of env var SQLITE__DB_PATH
   env_file:
   - .env
   labels:
   - "net.reddec.scheduler.cron=0 0 * * *"  # runs every day at midnight
scheduler:
   image: ghcr.io/reddec/compose-scheduler:1.0.0
   container_name: ytm2lfm-scheduler
   restart: unless-stopped
   volumes:
   - /var/run/docker.sock:/var/run/docker.sock:ro
```

### Synology NAS

1. Create new folder /docker/ytm2lfm
2. Use Text Editor (or any other editor) to create a file in /docker/ytm2lfm with the environment variables and call it `.env`:
```
  # Last.fm API Credentials
  LASTFM__API_KEY=
  LASTFM__SHARED_SECRET=
  LASTFM__REGISTERED_TO=
  LASTFM__PASSWORD=

  # YouTube Music Credentials
  YTMUSIC__AUTH_FILE=./oauth.json
  YTMUSIC__CLIENT_ID=
  YTMUSIC__CLIENT_SECRET=

  # Database Configuration
  SQLITE__DB_PATH=./sqlite/scrobbles.db
```
3. Add the file oauth.json to /docker/ytm2lfm
4. Open container manager and create a new Project.
  4.1. Set project name to `ytm2lfm`
  4.2. Set path to /docker/ytm2lfm
  4.3. Set source to create new docker-compose.yml and paste the following:
  ```
   services:
   ytm2lfm:
      image: csazev/ytm2lfm:latest  # you might want to pin a specific version here
      container_name: ytm2lfm
      command: ["python", "/app/src/cli.py", "scrobble"]
      volumes:
      - ./oauth.json:/app/oauth.json  # should match the path of env var YTMUSIC__AUTH_FILE
      - ./sqlite:/app/sqlite  # should match the path of env var SQLITE__DB_PATH
      env_file:
      - .env
      labels:
      - "net.reddec.scheduler.cron=0 0 * * *"  # runs every day at midnight
   scheduler:
      image: ghcr.io/reddec/compose-scheduler:1.0.0
      container_name: ytm2lfm-scheduler
      restart: unless-stopped
      volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request if you’d like to help improve this project.

## License

MIT

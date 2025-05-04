# YTM2LFM - YouTube Music to Last.fm Scrobbler

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
- Uses SQLite to store scrobbled tracks and detect new ones

## Limitations

- YouTube Music history is limited to the last 200 tracks by the YouTube Music API
- If you run this tool regularly (e.g., daily), this limitation shouldn't be a problem
- When the same track is played multiple times, YouTube Music moves it to the top of history rather than creating duplicate entries - this means repeated plays may not be scrobbled separately

## Installation

### Option 1: Docker (Recommended)

The easiest way to use YTM2LFM is with Docker:

1. Clone this repository
2. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the required credentials:
     - Get Last.fm API credentials from [Last.fm API](https://www.last.fm/api/account/create)
     - Set up Google OAuth credentials at [Google Developer Console](https://console.developers.google.com)

### Option 2: Local installation

Necessary for local development or if you don't want to use Docker:

1. Clone this repository
2. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the required credentials:
     - Get Last.fm API credentials from [Last.fm API](https://www.last.fm/api/account/create)
     - Set up Google OAuth credentials at [Google Developer Console](https://console.developers.google.com)
3. Install dependencies
   ```bash
   make sync
   ```

## Usage

### Configuration

All configuration is handled through environment variables.

Copy `.env.example` into `.env` or create a new `.env` file with the following variables:

```
LASTFM__API_KEY=your_lastfm_api_key
LASTFM__SHARED_SECRET=your_lastfm_shared_secret
LASTFM__REGISTERED_TO=your_lastfm_username
LASTFM__PASSWORD=your_lastfm_password

YTMUSIC__AUTH_FILE=path/to/oauth.json
YTMUSIC__CLIENT_ID=your_google_client_id
YTMUSIC__CLIENT_SECRET=your_google_client_secret

SQLITE__DB_PATH=path/to/database.sqlite
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

### Scrobble your YouTube Music history to Last.fm:

```bash
# Option 1: Run in a docker container
make docker-scrobble

# Option 2: Run directly in the host machine
make scrobble
```

On first run, these commands will fetch your YouTube Music history (last 200 plays) and scrobble it to Last.fm. On subsequent runs, only new tracks will be scrobbled.

### Store tracks without scrobbling:

If you don't want to scrobble your entire history on the first run, you can use these commands to store the history without scrobbling:

```bash
# Option 1: Run in a docker container
make docker-store

# Option 2: Run directly in the host machine
make store
```

This will populate the database with your current history, so the next time you run scrobble, it will only scrobble new tracks.

## Scheduling

For best results, set up a scheduled task (cron job) to run the scrobbler regularly:

```bash
# Option 1: Example cron job to run every hour with Docker
0 * * * * cd /path/to/ytm2lfm && make docker-scrobble >> /path/to/logfile.log 2>&1

# Option 2: Example cron job to run every hour
0 * * * * cd /path/to/ytm2lfm && make scrobble >> /path/to/logfile.log 2>&1
```

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request if you’d like to help improve this project.

## License

MIT

import os
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SQLiteSettings(BaseModel):
    db_path: str = Field(..., description="Path to the SQLite database file")


class LastFMSettings(BaseModel):
    api_key: str = Field(..., description="Last.fm API key")
    shared_secret: str = Field(..., description="Last.fm API shared secret")
    registered_to: str = Field(..., description="Last.fm username")
    password: str = Field(..., description="Last.fm password")


class YTMusicSettings(BaseModel):
    auth_file: str = Field(..., description="Path to YTMusic OAuth credentials file")
    client_id: str = Field(..., description="Google API client ID")
    client_secret: str = Field(..., description="Google API client secret")

    @field_validator("auth_file")
    def validate_file_exists(cls, v):
        if not os.path.isfile(v):
            raise ValueError(f"Auth file not found: {v}")
        return v


class ScrobblerSettings(BaseModel):
    sequence_match_length: int = Field(50, description="Length of sequence to match for finding new tracks")
    batch_size: int = Field(50, description="Number of tracks to scrobble in each batch")
    max_stored_tracks: int = Field(200, description="Maximum number of tracks to keep in the database.")


class Settings(BaseSettings):
    lastfm: LastFMSettings
    ytmusic: YTMusicSettings
    sqlite: SQLiteSettings
    scrobbler: Optional[ScrobblerSettings] = Field(default_factory=ScrobblerSettings)

    # if both a .env file and environment variables are present, environment variables take precedence
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",  # Enables nested loading from env
    )


settings = Settings()

"""Configuration loader for reading environment variables."""

import os
from pydantic import BaseSettings

def get_env_path(filename: str = ".env") -> str:
    """Return the absolute path to the environment file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

class ConfigSettings(BaseSettings):
    """Project configuration settings managed with Pydantic."""
    alpha_key: str
    database_name: str
    model_path: str

    class Config:
        env_file = get_env_path(".env")

# Initialize settings instance to be imported by other modules
config = ConfigSettings()

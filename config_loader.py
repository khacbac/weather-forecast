"""
Configuration loader for the weather prediction project.
Loads configuration from config.json file with fallback to environment variables.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the project."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to config.json file. If None, looks for config.json in script directory.
        """
        if config_file is None:
            current_dir = Path(__file__).parent
            config_file = current_dir / "config.json"
        else:
            config_file = Path(config_file)
        
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or use defaults with environment variable overrides."""
        # Default configuration
        defaults = {
            "gcp": {
                "project_id": "ai-realtime-project",
                "dataset_id": "sensor_data_stream",
                "table_id": "real-weather",
                "credentials_file": "ai-realtime-project-4de709b969f4.json"
            },
            "api": {
                "predict_api_url": "http://localhost:8000",
                "timeout": 5
            },
            "weather": {
                "latitude": 16.047079,
                "longitude": 108.206230,
                "city": "Danang"
            },
            "model": {
                "model_file": "weather_model.pkl"
            },
            "app": {
                "show_debug_info": False
            }
        }
        
        # Try to load from config file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    # Merge with defaults (file config takes precedence)
                    self._config = self._deep_merge(defaults, file_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
                print("Using defaults with environment variable overrides.")
                self._config = defaults
        else:
            print(f"Config file not found: {self.config_file}")
            print("Using defaults with environment variable overrides.")
            self._config = defaults
        
        # Apply environment variable overrides
        self._apply_env_overrides()
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        # GCP settings
        if os.getenv("GCP_PROJECT_ID"):
            self._config["gcp"]["project_id"] = os.getenv("GCP_PROJECT_ID")
        if os.getenv("BIGQUERY_DATASET"):
            self._config["gcp"]["dataset_id"] = os.getenv("BIGQUERY_DATASET")
        if os.getenv("BIGQUERY_TABLE"):
            self._config["gcp"]["table_id"] = os.getenv("BIGQUERY_TABLE")
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            self._config["gcp"]["credentials_file"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        # API settings
        if os.getenv("PREDICT_API_URL"):
            self._config["api"]["predict_api_url"] = os.getenv("PREDICT_API_URL")
        
        # Weather settings
        if os.getenv("WEATHER_LAT"):
            self._config["weather"]["latitude"] = float(os.getenv("WEATHER_LAT"))
        if os.getenv("WEATHER_LON"):
            self._config["weather"]["longitude"] = float(os.getenv("WEATHER_LON"))
        if os.getenv("WEATHER_CITY"):
            self._config["weather"]["city"] = os.getenv("WEATHER_CITY")
    
    def get(self, *keys, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            *keys: Keys to navigate the config dictionary (e.g., 'gcp', 'project_id')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value
    
    @property
    def gcp_project_id(self) -> str:
        """Get GCP project ID."""
        return self.get("gcp", "project_id")
    
    @property
    def gcp_dataset_id(self) -> str:
        """Get BigQuery dataset ID."""
        return self.get("gcp", "dataset_id")
    
    @property
    def gcp_table_id(self) -> str:
        """Get BigQuery table ID."""
        return self.get("gcp", "table_id")
    
    @property
    def gcp_full_table_path(self) -> str:
        """Get full BigQuery table path."""
        return f"{self.gcp_project_id}.{self.gcp_dataset_id}.{self.gcp_table_id}"
    
    @property
    def gcp_credentials_file(self) -> str:
        """Get GCP credentials file path."""
        cred_file = self.get("gcp", "credentials_file")
        # If it's a relative path, make it relative to the config file's directory
        if not os.path.isabs(cred_file):
            cred_file = str(self.config_file.parent / cred_file)
        return cred_file
    
    @property
    def api_base_url(self) -> str:
        """Get API base URL."""
        return self.get("api", "predict_api_url")
    
    @property
    def api_timeout(self) -> int:
        """Get API timeout in seconds."""
        return self.get("api", "timeout", default=5)
    
    @property
    def weather_latitude(self) -> float:
        """Get weather location latitude."""
        return self.get("weather", "latitude")
    
    @property
    def weather_longitude(self) -> float:
        """Get weather location longitude."""
        return self.get("weather", "longitude")
    
    @property
    def weather_city(self) -> str:
        """Get weather city name."""
        return self.get("weather", "city")
    
    @property
    def model_file(self) -> str:
        """Get model file path."""
        model_file = self.get("model", "model_file")
        # If it's a relative path, make it relative to the config file's directory
        if not os.path.isabs(model_file):
            model_file = str(self.config_file.parent / model_file)
        return model_file
    
    @property
    def show_debug_info(self) -> bool:
        """Get whether to show debug info in the app."""
        return self.get("app", "show_debug_info", default=False)


# Global config instance
_config_instance: Optional[Config] = None


def get_config(config_file: Optional[str] = None) -> Config:
    """
    Get the global configuration instance.
    
    Args:
        config_file: Optional path to config file. Only used on first call.
        
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_file)
    return _config_instance


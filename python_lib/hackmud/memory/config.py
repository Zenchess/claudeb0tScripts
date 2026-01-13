"""Configuration management for hackmud memory scanner

Handles platform-specific paths, auto-detection, and config file creation.
"""

import json
import hashlib
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


# Default installation paths by platform
DEFAULT_GAME_PATHS = {
    'Linux': Path.home() / ".local/share/Steam/steamapps/common/hackmud",
    'Windows': Path("C:/Program Files (x86)/Steam/steamapps/common/hackmud"),
    'Darwin': Path.home() / "Library/Application Support/Steam/steamapps/common/hackmud"
}

DEFAULT_SETTINGS_PATHS = {
    'Linux': Path.home() / ".config/unity3d/Drizzly Bear/hackmud",
    'Windows': Path.home() / "AppData/LocalLow/Drizzly Bear/hackmud",
    'Darwin': Path.home() / "Library/Application Support/Drizzly Bear/hackmud"
}


def get_platform() -> str:
    """Get current platform name"""
    return platform.system()


def get_core_dll_path(game_path: Path, plat: str) -> Path:
    """Generate Core.dll path from game base path and platform

    Args:
        game_path: Base hackmud installation directory
        plat: Platform name (Linux, Windows, Darwin)

    Returns:
        Path to Core.dll

    Raises:
        ValueError: If platform is unsupported
    """
    if plat == 'Linux':
        return game_path / "hackmud_lin_Data/Managed/Core.dll"
    elif plat == 'Windows':
        return game_path / "hackmud_Data/Managed/Core.dll"
    elif plat == 'Darwin':
        return game_path / "hackmud.app/Contents/Resources/Data/Managed/Core.dll"
    else:
        raise ValueError(f"Unsupported platform: {plat}")


def detect_game_path(plat: Optional[str] = None) -> Optional[Path]:
    """Try to auto-detect game installation path

    Args:
        plat: Platform name (defaults to current platform)

    Returns:
        Path to game installation, or None if not found
    """
    if plat is None:
        plat = get_platform()

    # Try default location first
    default_path = DEFAULT_GAME_PATHS.get(plat)
    if default_path and default_path.exists():
        core_dll = get_core_dll_path(default_path, plat)
        if core_dll.exists():
            return default_path

    # Try alternative Steam locations
    if plat == 'Linux':
        search_paths = [
            Path.home() / ".local/share/Steam/steamapps/common/hackmud",
            Path.home() / ".steam/steam/steamapps/common/hackmud",
        ]
    elif plat == 'Windows':
        search_paths = [
            Path("C:/Program Files (x86)/Steam/steamapps/common/hackmud"),
            Path("C:/Program Files/Steam/steamapps/common/hackmud"),
        ]
    else:
        search_paths = []

    for path in search_paths:
        if path.exists():
            core_dll = get_core_dll_path(path, plat)
            if core_dll.exists():
                return path

    return None


def detect_settings_path(plat: Optional[str] = None) -> Optional[Path]:
    """Try to auto-detect settings path

    Args:
        plat: Platform name (defaults to current platform)

    Returns:
        Path to settings directory, or None if not found
    """
    if plat is None:
        plat = get_platform()

    default_path = DEFAULT_SETTINGS_PATHS.get(plat)
    if default_path and default_path.exists():
        return default_path

    return None


def compute_dll_hash(dll_path: Path) -> str:
    """Compute SHA256 hash of Core.dll

    Args:
        dll_path: Path to Core.dll

    Returns:
        Hexadecimal SHA256 hash string
    """
    sha256 = hashlib.sha256()
    with open(dll_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def create_config(
    game_path: Optional[Path] = None,
    settings_path: Optional[Path] = None,
    plat: Optional[str] = None
) -> Dict[str, str]:
    """Create configuration dictionary

    Args:
        game_path: Path to game installation (auto-detects if None)
        settings_path: Path to settings directory (auto-detects if None)
        plat: Platform name (defaults to current platform)

    Returns:
        Configuration dictionary

    Raises:
        ValueError: If game path cannot be found
    """
    if plat is None:
        plat = get_platform()

    # Auto-detect game path if not provided
    if game_path is None:
        game_path = detect_game_path(plat)
        if game_path is None:
            raise ValueError(
                "Could not detect game installation path. "
                "Please provide game_path argument."
            )

    # Auto-detect settings path if not provided
    if settings_path is None:
        settings_path = detect_settings_path(plat)

    # Get Core.dll path and compute hash
    core_dll = get_core_dll_path(game_path, plat)
    if not core_dll.exists():
        raise ValueError(f"Core.dll not found at {core_dll}")

    dll_hash = compute_dll_hash(core_dll)

    # Build config
    config = {
        'platform': plat,
        'game_path': str(game_path),
        'core_dll_hash': dll_hash,
        'date_last': datetime.now().isoformat()
    }

    if settings_path:
        config['settings_path'] = str(settings_path)

    return config


def save_config(config: Dict[str, str], config_file: Path) -> None:
    """Save configuration to JSON file

    Args:
        config: Configuration dictionary
        config_file: Path to save config.json
    """
    # Update date_last on every save
    config['date_last'] = datetime.now().isoformat()

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


def load_config(config_file: Path) -> Dict[str, str]:
    """Load configuration from JSON file

    Args:
        config_file: Path to config.json

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid
    """
    with open(config_file, 'r') as f:
        return json.load(f)

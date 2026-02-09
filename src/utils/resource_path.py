"""
Resource path utility for PyInstaller bundled applications.

Provides a helper function to locate resource files correctly whether running
from source or from a PyInstaller-bundled executable.
"""

import sys
import os


def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for PyInstaller bundled apps.
    
    When running as a PyInstaller-packed executable, files are temporarily unpacked into a folder
    defined by sys._MEIPASS. When running without PyInstaller, it defaults to the current working directory.
    
    Args:
        relative_path: Path to the resource, relative to the root directory of the script.
        
    Returns:
        The absolute path to the resource.
    """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # If not running as PyInstaller exe, assume script dir as base path
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

"""
Main entry point for Ghosty Toolz Evolved.

This module initializes the application and starts the main GUI.
"""

import sys
import os
from pathlib import Path

# Add src to path if running from repository root
if __name__ == "__main__":
    root_dir = Path(__file__).parent.parent
    if root_dir not in sys.path:
        sys.path.insert(0, str(root_dir))

from src.utils.logger import get_logger, Logger
from src.utils.config import get_config
from src.gui.main_window import MainWindow

logger = get_logger("main")


def setup_logging() -> None:
    """Set up application logging."""
    logger_instance = Logger()

    # Get configuration
    config = get_config()
    log_level = config.get("logging.level", "INFO")

    # Map string to logging level
    import logging

    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    level = level_map.get(log_level.upper(), logging.INFO)

    # Configure main logger
    main_logger = logger_instance.get_logger(
        "ghosty_tools", log_file="ghosty_tools.log", level=level
    )

    logger.info("Logging initialized")


def check_requirements() -> bool:
    """
    Check if all requirements are met.

    Returns:
        True if requirements are met
    """
    logger.info("Checking requirements...")

    # Check Python version
    if sys.version_info < (3, 8):
        logger.error(f"Python 3.8+ required, got {sys.version_info.major}.{sys.version_info.minor}")
        return False

    # Check platform
    if sys.platform != "win32":
        logger.error(f"Windows platform required, got {sys.platform}")
        return False

    logger.info("Requirements check passed")
    return True


def show_welcome_message() -> None:
    """Show welcome message in console."""
    config = get_config()
    app_name = config.get("app.name", "Ghosty Toolz Evolved")
    app_version = config.get("app.version", "2.0.0")

    welcome_msg = f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              {app_name}                  ║
║                    Version {app_version}                       ║
║                                                           ║
║     Professional Windows System Maintenance Tool         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Starting application...
"""

    print(welcome_msg)
    logger.info(f"{app_name} v{app_version} starting")


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Exit code (0 for success)
    """
    try:
        # Set up logging
        setup_logging()

        # Show welcome message
        show_welcome_message()

        # Check requirements
        if not check_requirements():
            logger.error("Requirements check failed")
            return 1

        # Load configuration
        config = get_config()
        logger.info("Configuration loaded")

        # Create and run main window
        logger.info("Creating main window...")
        app = MainWindow()

        logger.info("Application started successfully")
        app.mainloop()

        logger.info("Application closed normally")
        return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

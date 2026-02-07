"""
Logging utility for Ghosty Toolz Evolved.

Provides centralized logging functionality with file and console output,
color-coded console messages, and audit trail support.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
import colorlog


class Logger:
    """Centralized logging manager for the application."""

    _instance: Optional["Logger"] = None
    _initialized: bool = False

    def __new__(cls) -> "Logger":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the logger."""
        if not self._initialized:
            self._initialized = True
            self.loggers = {}
            self.log_dir = Path("logs")
            self.log_dir.mkdir(exist_ok=True)

    def get_logger(
        self,
        name: str,
        log_file: Optional[str] = None,
        level: int = logging.INFO,
        max_bytes: int = 10485760,
        backup_count: int = 5,
    ) -> logging.Logger:
        """
        Get or create a logger instance.

        Args:
            name: Logger name
            log_file: Optional log file name (relative to logs/)
            level: Logging level
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup files to keep

        Returns:
            Configured logger instance
        """
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False

        # Console handler with colors
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler with rotation
        if log_file:
            log_path = self.log_dir / log_file
            file_handler = RotatingFileHandler(
                log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
            )
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        self.loggers[name] = logger
        return logger

    def get_audit_logger(self, log_file: str = "audit.log") -> logging.Logger:
        """
        Get dedicated audit logger for security and operation tracking.

        Args:
            log_file: Audit log file name

        Returns:
            Audit logger instance
        """
        return self.get_logger(
            "audit", log_file=log_file, level=logging.INFO, max_bytes=52428800, backup_count=10
        )


# Global logger instance
_logger_instance = Logger()


def get_logger(name: str = "ghosty_tools") -> logging.Logger:
    """
    Get a logger instance (convenience function).

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return _logger_instance.get_logger(name, log_file="ghosty_tools.log")


def get_audit_logger() -> logging.Logger:
    """
    Get audit logger instance (convenience function).

    Returns:
        Audit logger instance
    """
    return _logger_instance.get_audit_logger()


# Example usage
if __name__ == "__main__":
    # Test logger
    logger = get_logger("test")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Test audit logger
    audit = get_audit_logger()
    audit.info("User performed system cleanup")
    audit.warning("Attempted registry modification")

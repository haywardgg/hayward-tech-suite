"""
Global admin state management for the application.

Tracks whether the application has admin privileges and whether the user
declined admin elevation.
"""


class AdminState:
    """Global admin state singleton."""
    
    _is_admin = False
    _user_declined = False
    
    @classmethod
    def set_admin_mode(cls, is_admin: bool, declined: bool = False) -> None:
        """
        Set admin mode state.
        
        Args:
            is_admin: Whether the application has admin privileges
            declined: Whether the user declined admin elevation
        """
        cls._is_admin = is_admin
        cls._user_declined = declined
    
    @classmethod
    def is_admin(cls) -> bool:
        """
        Check if application has admin privileges.
        
        Returns:
            True if running as admin
        """
        return cls._is_admin
    
    @classmethod
    def user_declined_admin(cls) -> bool:
        """
        Check if user declined admin elevation.
        
        Returns:
            True if user declined admin elevation
        """
        return cls._user_declined

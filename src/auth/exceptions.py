class GoogleOAuthError(Exception):
    def __init__(self, message: str = 'An error occurred while interacting with Google OAuth.'):
        super().__init__(message)
        self.message = message


class GoogleOAuthUrlGenerationError(Exception):
    """Custom exception for errors occurring during the Google OAuth URL generation."""

    def __init__(self, message: str = 'Failed to generate Google OAuth URL'):
        super().__init__(message)
        self.message = message

class GoogleOAuthError(Exception):
    """Base error for all Google OAuth-related issues."""

    def __init__(self, message: str = 'An error occurred while interacting with Google OAuth.'):
        super().__init__(message)
        self.message = message


class TokenError(Exception):
    """General error for all operations with tokens."""

    def __init__(self, message: str = 'An error occurred while working with the token.'):
        super().__init__(message)
        self.message = message

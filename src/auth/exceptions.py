class GoogleOAuthError(Exception):
    def __init__(self):
        super().__init__('An error occurred while interacting with Google OAuth.')

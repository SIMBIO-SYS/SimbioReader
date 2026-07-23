class LoadingError(Exception):
    def __init__(self, filename, message):
        self.filename = filename
        self.message = message
        super().__init__(self.filename, self.message)

    def __str__(self):
        return f"Error loading {self.filename}: {self.message}"


class DeprecatedMethodError(RuntimeError):
    """Raised when an obsolete SimbioReader method is called."""

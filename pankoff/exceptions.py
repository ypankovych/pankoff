class ValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors

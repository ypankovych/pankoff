class ValidationError(ValueError):
    """
    :param errors: a list of errors
    """
    def __init__(self, errors):
        self.errors = errors


class InconsistentOrderError(TypeError):
    pass

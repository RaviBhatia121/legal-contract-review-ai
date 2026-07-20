class ModelAdapterError(Exception):
    """Base class for typed model-adapter failures."""


class ModelTimeoutError(ModelAdapterError):
    pass


class ModelOutputInvalidError(ModelAdapterError):
    """Raised after one repair attempt still fails schema validation."""


class ProviderUnavailableError(ModelAdapterError):
    """Raised when the provider cannot be reached at all (connection refused, DNS, etc.)."""

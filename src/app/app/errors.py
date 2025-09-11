class EmbeddingError(Exception):
    """Raised when the embedding pipeline rejects or cannot process input."""
    pass

class InferenceError(Exception):
    """Raised when model forward pass fails."""
    pass
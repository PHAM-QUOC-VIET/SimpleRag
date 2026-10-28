"""Error taxonomy for Legal RAG system."""

from typing import Any, Dict, Optional


class LegalRAGError(Exception):
    """Base exception for all Legal RAG errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class IngestionError(LegalRAGError):
    """Raised when document loading or extraction fails."""
    pass


class ParsingError(LegalRAGError):
    """Raised when legal structure parsing fails."""
    pass


class ChunkingError(LegalRAGError):
    """Raised when chunk creation or validation fails."""
    pass


class IndexingError(LegalRAGError):
    """Raised when vector or sparse indexing fails."""
    pass


class RetrievalError(LegalRAGError):
    """Raised during retrieval or reranking failure."""
    pass


class GenerationError(LegalRAGError):
    """Raised when LLM generation fails."""
    pass


class InsufficientEvidenceError(LegalRAGError):
    """Raised when retrieved evidence is insufficient to answer reliably."""
    pass

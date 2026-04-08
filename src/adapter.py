"""Memory system adapter interface for DeepMemEval.

All memory systems must implement this interface to be evaluated.
"""

from abc import ABC, abstractmethod


class MemorySystemAdapter(ABC):
    """Base adapter that all evaluated memory systems must implement."""

    @abstractmethod
    def ingest_session(self, session: dict, timestamp: str) -> None:
        """Ingest a conversation session at a given timestamp.

        Args:
            session: Dict with 'session_id', 'date', and 'turns' (list of role/content dicts).
            timestamp: ISO 8601 timestamp for when this session occurred.
        """
        ...

    @abstractmethod
    def query(self, question: str, timestamp: str = "now") -> str:
        """Query the memory system.

        Args:
            question: The question to ask.
            timestamp: Point-in-time for the query. "now" means current state.

        Returns:
            The system's response string.
        """
        ...

    @abstractmethod
    def get_context_tokens(self) -> int:
        """Return the number of tokens in the last context assembly.

        Used for delta efficiency measurement.
        """
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset the memory system to empty state."""
        ...

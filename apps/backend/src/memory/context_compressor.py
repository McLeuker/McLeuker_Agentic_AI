"""
Context Compressor — Token Management for kimi-2.5's 256K Window
==================================================================

Manages context size to fit within model limits:
- Token estimation
- Priority-based truncation
- Message compression
- Key information extraction
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CompressionResult:
    """Result of context compression."""
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    information_retained: float


class ContextCompressor:
    """
    Compresses context to fit within token limits.

    Strategies:
    - Token estimation (chars / 4)
    - Priority-based truncation
    - Message compression (keep system + recent)
    - Key information extraction
    """

    CHARS_PER_TOKEN = 4

    def __init__(self, kimi_client=None):
        self.kimi_client = kimi_client

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count."""
        return len(text) // self.CHARS_PER_TOKEN

    def truncate_to_tokens(self, text: str, max_tokens: int, from_end: bool = False) -> str:
        """Truncate text to fit within token limit."""
        max_chars = max_tokens * self.CHARS_PER_TOKEN
        if len(text) <= max_chars:
            return text
        if from_end:
            return "..." + text[-max_chars + 3:]
        return text[:max_chars - 3] + "..."

    def compress_messages(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        preserve_system: bool = True,
        preserve_recent: int = 3,
    ) -> List[Dict[str, str]]:
        """Compress message list to fit within token limit."""
        if not messages:
            return messages

        total_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in messages)
        if total_tokens <= max_tokens:
            return messages

        system_messages = [m for m in messages if m.get("role") == "system"]
        other_messages = [m for m in messages if m.get("role") != "system"]

        result = []
        current_tokens = 0

        # Keep system messages
        if preserve_system:
            for msg in system_messages:
                tokens = self.estimate_tokens(msg.get("content", ""))
                if current_tokens + tokens <= max_tokens * 0.3:
                    result.append(msg)
                    current_tokens += tokens

        # Keep recent messages
        recent = other_messages[-preserve_recent:] if preserve_recent > 0 else []
        for msg in recent:
            tokens = self.estimate_tokens(msg.get("content", ""))
            if current_tokens + tokens <= max_tokens:
                result.append(msg)
                current_tokens += tokens

        # Add older messages if room
        older = other_messages[:-preserve_recent] if preserve_recent > 0 else other_messages
        for msg in older:
            tokens = self.estimate_tokens(msg.get("content", ""))
            if current_tokens + tokens <= max_tokens:
                result.append(msg)
                current_tokens += tokens
            else:
                break

        return result

    async def smart_compress(
        self,
        text: str,
        max_tokens: int,
        context_type: str = "general",
    ) -> CompressionResult:
        """Smart compression based on context type."""
        original_tokens = self.estimate_tokens(text)

        if original_tokens <= max_tokens:
            return CompressionResult(
                compressed_text=text,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                information_retained=1.0,
            )

        if context_type == "code":
            compressed = self._compress_code(text, max_tokens)
        else:
            compressed = self.truncate_to_tokens(text, max_tokens)

        compressed_tokens = self.estimate_tokens(compressed)

        return CompressionResult(
            compressed_text=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 1,
            information_retained=0.7,
        )

    def _compress_code(self, code: str, max_tokens: int) -> str:
        """Compress code by removing comments and docstrings."""
        lines = code.split("\n")
        result = []
        in_docstring = False

        for line in lines:
            stripped = line.strip()

            if '"""' in line or "'''" in line:
                count = line.count('"""') + line.count("'''")
                if count == 2:
                    continue
                in_docstring = not in_docstring
                continue

            if in_docstring:
                continue

            if stripped.startswith("#"):
                continue

            if stripped or (result and result[-1].strip()):
                result.append(line)

        compressed = "\n".join(result)

        if self.estimate_tokens(compressed) > max_tokens:
            compressed = self.truncate_to_tokens(compressed, max_tokens, from_end=True)

        return compressed

    def extract_key_information(self, text: str) -> List[str]:
        """Extract key information points from text."""
        key_points = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith(("- ", "* ", "• ")):
                key_points.append(line[2:])
            elif line and line[0].isdigit() and ". " in line[:4]:
                key_points.append(line.split(". ", 1)[1] if ". " in line else line)
            elif any(phrase in line.lower() for phrase in ["important:", "note:", "key:", "warning:"]):
                key_points.append(line)

        return key_points[:20]

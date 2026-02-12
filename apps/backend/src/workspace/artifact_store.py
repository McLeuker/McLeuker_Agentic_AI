"""
Artifact Store — Generated Artifact Management
================================================

Manages artifacts generated during execution:
- Code files, documents, images
- Artifact metadata and versioning
- Download and serving
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Artifact:
    """A generated artifact."""
    id: str
    name: str
    artifact_type: str  # code, document, image, data, other
    content: str = ""
    file_path: Optional[str] = None
    session_id: str = ""
    mime_type: str = "text/plain"
    size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "artifact_type": self.artifact_type,
            "mime_type": self.mime_type,
            "size": self.size,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "has_content": bool(self.content),
            "has_file": bool(self.file_path),
        }


class ArtifactStore:
    """
    Manages generated artifacts.
    """

    def __init__(self, storage_path: str = "/tmp/agentic_artifacts"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._artifacts: Dict[str, Artifact] = {}

    def store(
        self,
        name: str,
        content: str,
        artifact_type: str = "document",
        session_id: str = "",
        mime_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """Store an artifact."""
        artifact_id = str(uuid.uuid4())[:8]

        # Save to file
        file_path = self.storage_path / f"{artifact_id}_{name}"
        file_path.write_text(content)

        artifact = Artifact(
            id=artifact_id,
            name=name,
            artifact_type=artifact_type,
            content=content,
            file_path=str(file_path),
            session_id=session_id,
            mime_type=mime_type,
            size=len(content),
            metadata=metadata or {},
        )

        self._artifacts[artifact_id] = artifact
        logger.info(f"Stored artifact: {artifact_id} ({name})")
        return artifact

    def get(self, artifact_id: str) -> Optional[Artifact]:
        """Get an artifact by ID."""
        return self._artifacts.get(artifact_id)

    def list_by_session(self, session_id: str) -> List[Artifact]:
        """List artifacts for a session."""
        return [a for a in self._artifacts.values() if a.session_id == session_id]

    def delete(self, artifact_id: str) -> bool:
        """Delete an artifact."""
        artifact = self._artifacts.get(artifact_id)
        if not artifact:
            return False

        if artifact.file_path:
            try:
                Path(artifact.file_path).unlink(missing_ok=True)
            except Exception:
                pass

        del self._artifacts[artifact_id]
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get artifact store statistics."""
        return {
            "total_artifacts": len(self._artifacts),
            "total_size": sum(a.size for a in self._artifacts.values()),
            "types": list(set(a.artifact_type for a in self._artifacts.values())),
        }

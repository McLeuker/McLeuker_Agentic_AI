"""
State Manager — Session State Persistence and Checkpointing
=============================================================

Manages execution state across sessions:
- Session state tracking
- Checkpoint creation and restoration
- Context accumulation
- State serialization
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Represents the state of an execution session."""
    session_id: str
    user_id: Optional[str] = None
    status: str = "active"
    mode: str = "auto"  # instant / auto / agent
    objective: str = ""
    plan_id: Optional[str] = None
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    messages: List[Dict[str, str]] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status,
            "mode": self.mode,
            "objective": self.objective,
            "plan_id": self.plan_id,
            "current_step": self.current_step,
            "step_results": {k: str(v)[:500] for k, v in self.step_results.items()},
            "context_keys": list(self.context.keys()),
            "message_count": len(self.messages),
            "artifact_count": len(self.artifacts),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "checkpoint_count": len(self.checkpoints),
        }


class StateManager:
    """
    Manages session states for execution sessions.

    Features:
    - Create and track sessions
    - Checkpoint and restore
    - Context accumulation
    - Cleanup of old sessions
    """

    def __init__(self, persist_path: str = "/tmp/agentic_states"):
        """
        Initialize state manager.

        Args:
            persist_path: Path for state persistence
        """
        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
        self._sessions: Dict[str, SessionState] = {}
        self._lock = asyncio.Lock()

    def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        mode: str = "auto",
        objective: str = "",
    ) -> SessionState:
        """Create a new session state."""
        state = SessionState(
            session_id=session_id,
            user_id=user_id,
            mode=mode,
            objective=objective,
        )
        self._sessions[session_id] = state
        logger.info(f"Created session state: {session_id}")
        return state

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session state by ID."""
        return self._sessions.get(session_id)

    def update_session(
        self,
        session_id: str,
        **kwargs
    ) -> Optional[SessionState]:
        """Update session state fields."""
        state = self._sessions.get(session_id)
        if not state:
            return None

        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)

        state.updated_at = datetime.now().isoformat()
        return state

    def add_step_result(
        self,
        session_id: str,
        step_id: str,
        result: Any
    ):
        """Add a step result to the session."""
        state = self._sessions.get(session_id)
        if state:
            state.step_results[step_id] = result
            state.current_step = step_id
            state.updated_at = datetime.now().isoformat()

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """Add a message to the session history."""
        state = self._sessions.get(session_id)
        if state:
            state.messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            state.updated_at = datetime.now().isoformat()

    def add_artifact(self, session_id: str, artifact_id: str):
        """Add an artifact reference to the session."""
        state = self._sessions.get(session_id)
        if state:
            state.artifacts.append(artifact_id)
            state.updated_at = datetime.now().isoformat()

    def create_checkpoint(self, session_id: str, label: str = "") -> Optional[Dict]:
        """Create a checkpoint of the current session state."""
        state = self._sessions.get(session_id)
        if not state:
            return None

        checkpoint = {
            "label": label or f"checkpoint_{len(state.checkpoints) + 1}",
            "timestamp": datetime.now().isoformat(),
            "current_step": state.current_step,
            "step_results": dict(state.step_results),
            "context": dict(state.context),
        }

        state.checkpoints.append(checkpoint)
        logger.info(f"Created checkpoint for session {session_id}: {checkpoint['label']}")
        return checkpoint

    def restore_checkpoint(
        self,
        session_id: str,
        checkpoint_index: int = -1
    ) -> bool:
        """Restore session to a checkpoint."""
        state = self._sessions.get(session_id)
        if not state or not state.checkpoints:
            return False

        try:
            checkpoint = state.checkpoints[checkpoint_index]
            state.current_step = checkpoint["current_step"]
            state.step_results = checkpoint["step_results"]
            state.context = checkpoint["context"]
            state.updated_at = datetime.now().isoformat()
            logger.info(f"Restored checkpoint for session {session_id}: {checkpoint['label']}")
            return True
        except (IndexError, KeyError) as e:
            logger.error(f"Failed to restore checkpoint: {e}")
            return False

    async def persist_session(self, session_id: str) -> bool:
        """Persist session state to disk."""
        state = self._sessions.get(session_id)
        if not state:
            return False

        try:
            file_path = self.persist_path / f"{session_id}.json"
            data = state.to_dict()
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to persist session {session_id}: {e}")
            return False

    async def load_session(self, session_id: str) -> Optional[SessionState]:
        """Load session state from disk."""
        file_path = self.persist_path / f"{session_id}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            state = SessionState(
                session_id=data["session_id"],
                user_id=data.get("user_id"),
                status=data.get("status", "active"),
                mode=data.get("mode", "auto"),
                objective=data.get("objective", ""),
            )
            self._sessions[session_id] = state
            return state
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session state."""
        if session_id in self._sessions:
            del self._sessions[session_id]

        file_path = self.persist_path / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()

        return True

    def list_sessions(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all sessions with optional filtering."""
        sessions = list(self._sessions.values())

        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        if status:
            sessions = [s for s in sessions if s.status == status]

        return [s.to_dict() for s in sessions]

    async def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up sessions older than max_age_hours."""
        now = datetime.now()
        to_delete = []

        for session_id, state in self._sessions.items():
            created = datetime.fromisoformat(state.created_at)
            age_hours = (now - created).total_seconds() / 3600
            if age_hours > max_age_hours:
                to_delete.append(session_id)

        for session_id in to_delete:
            self.delete_session(session_id)

        return len(to_delete)

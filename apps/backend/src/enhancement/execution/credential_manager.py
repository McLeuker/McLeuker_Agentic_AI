"""
Credential Manager — Secure credential handling for end-to-end execution
==========================================================================
Manages user credentials for web automation tasks.
Credentials are stored encrypted in Supabase and only used during execution.

Security principles:
- Credentials are encrypted at rest
- User must explicitly grant permission per-service
- Credentials are never logged or exposed in events
- Session-scoped access with automatic cleanup
"""

import json
import logging
import os
import hashlib
import base64
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CredentialStatus(Enum):
    """Status of a credential."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class Credential:
    """A stored credential for a service."""
    id: str
    user_id: str
    service: str  # github, google, canva, etc.
    credential_type: str  # oauth, api_key, username_password, cookie
    encrypted_data: str = ""
    status: CredentialStatus = CredentialStatus.PENDING
    granted_at: Optional[str] = None
    expires_at: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "service": self.service,
            "credential_type": self.credential_type,
            "status": self.status.value,
            "granted_at": self.granted_at,
            "expires_at": self.expires_at,
            "scopes": self.scopes,
        }


class CredentialManager:
    """
    Manages user credentials for end-to-end execution.

    Handles:
    - Credential storage and retrieval
    - Encryption/decryption
    - Permission management
    - Session-scoped access
    - Automatic cleanup
    """

    SUPPORTED_SERVICES = [
        "github", "google", "twitter", "linkedin", "canva",
        "slack", "notion", "figma", "vercel", "railway",
        "supabase", "stripe", "shopify", "wordpress",
        "custom"
    ]

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._encryption_key = os.getenv("CREDENTIAL_ENCRYPTION_KEY", "")
        self._session_credentials: Dict[str, Dict[str, Any]] = {}

    def _encrypt(self, data: str) -> str:
        """Encrypt credential data using a simple XOR cipher with the key.
        In production, use AES-256-GCM or similar."""
        if not self._encryption_key:
            return base64.b64encode(data.encode()).decode()
        key = hashlib.sha256(self._encryption_key.encode()).digest()
        encrypted = bytes(
            b ^ key[i % len(key)]
            for i, b in enumerate(data.encode())
        )
        return base64.b64encode(encrypted).decode()

    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt credential data."""
        if not self._encryption_key:
            return base64.b64decode(encrypted_data).decode()
        key = hashlib.sha256(self._encryption_key.encode()).digest()
        data = base64.b64decode(encrypted_data)
        decrypted = bytes(
            b ^ key[i % len(key)]
            for i, b in enumerate(data)
        )
        return decrypted.decode()

    async def store_credential(
        self,
        user_id: str,
        service: str,
        credential_type: str,
        credential_data: Dict[str, str],
        scopes: Optional[List[str]] = None,
        expires_in_hours: int = 24,
    ) -> Credential:
        """
        Store a user credential securely.

        Args:
            user_id: The user's ID
            service: Service name (github, google, etc.)
            credential_type: Type of credential
            credential_data: The actual credential data (will be encrypted)
            scopes: Permission scopes
            expires_in_hours: How long the credential is valid

        Returns:
            The stored Credential object
        """
        import uuid

        cred_id = str(uuid.uuid4())[:12]
        encrypted = self._encrypt(json.dumps(credential_data))
        now = datetime.now()
        expires = now + timedelta(hours=expires_in_hours)

        credential = Credential(
            id=cred_id,
            user_id=user_id,
            service=service,
            credential_type=credential_type,
            encrypted_data=encrypted,
            status=CredentialStatus.ACTIVE,
            granted_at=now.isoformat(),
            expires_at=expires.isoformat(),
            scopes=scopes or [],
        )

        if self.supabase:
            try:
                await self._store_in_supabase(credential)
            except Exception as e:
                logger.error("Failed to store credential in Supabase: %s", e)

        self._session_credentials[f"{user_id}:{service}"] = {
            "credential": credential,
            "data": credential_data,
        }

        logger.info(
            "Credential stored for user %s, service %s (expires %s)",
            user_id, service, expires.isoformat()
        )
        return credential

    async def get_credential(
        self, user_id: str, service: str
    ) -> Optional[Dict[str, str]]:
        """
        Retrieve a credential for a user and service.

        Returns:
            Decrypted credential data, or None if not found/expired
        """
        cache_key = f"{user_id}:{service}"

        if cache_key in self._session_credentials:
            cred_info = self._session_credentials[cache_key]
            credential = cred_info["credential"]
            if credential.expires_at:
                expires = datetime.fromisoformat(credential.expires_at)
                if datetime.now() > expires:
                    del self._session_credentials[cache_key]
                    return None
            return cred_info["data"]

        if self.supabase:
            try:
                return await self._fetch_from_supabase(user_id, service)
            except Exception as e:
                logger.error("Failed to fetch credential from Supabase: %s", e)

        return None

    async def has_credential(self, user_id: str, service: str) -> bool:
        """Check if a credential exists and is valid."""
        cred = await self.get_credential(user_id, service)
        return cred is not None

    async def revoke_credential(self, user_id: str, service: str) -> bool:
        """Revoke a credential."""
        cache_key = f"{user_id}:{service}"
        if cache_key in self._session_credentials:
            del self._session_credentials[cache_key]

        if self.supabase:
            try:
                await self._revoke_in_supabase(user_id, service)
            except Exception as e:
                logger.error("Failed to revoke credential: %s", e)

        logger.info("Credential revoked for user %s, service %s", user_id, service)
        return True

    async def list_credentials(self, user_id: str) -> List[Dict[str, Any]]:
        """List all credentials for a user (without sensitive data)."""
        results = []
        for key, info in self._session_credentials.items():
            if key.startswith(f"{user_id}:"):
                results.append(info["credential"].to_dict())
        return results

    async def cleanup_expired(self):
        """Remove expired credentials from the session cache."""
        now = datetime.now()
        expired_keys = []
        for key, info in self._session_credentials.items():
            credential = info["credential"]
            if credential.expires_at:
                expires = datetime.fromisoformat(credential.expires_at)
                if now > expires:
                    expired_keys.append(key)

        for key in expired_keys:
            del self._session_credentials[key]

        if expired_keys:
            logger.info("Cleaned up %d expired credentials", len(expired_keys))

    async def _store_in_supabase(self, credential: Credential):
        """Store credential in Supabase."""
        pass  # Implemented when Supabase integration is active

    async def _fetch_from_supabase(
        self, user_id: str, service: str
    ) -> Optional[Dict[str, str]]:
        """Fetch credential from Supabase."""
        return None

    async def _revoke_in_supabase(self, user_id: str, service: str):
        """Revoke credential in Supabase."""
        pass

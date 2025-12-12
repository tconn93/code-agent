"""
Secret Management System with HashiCorp Vault and Encrypted Database Storage.
"""
import os
import hvac
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
import logging
import json
import base64

logger = logging.getLogger(__name__)


class VaultSecretManager:
    """
    HashiCorp Vault secret manager.

    Usage:
        vault = VaultSecretManager()
        api_key = vault.get_secret("anthropic_api_key")
    """

    def __init__(self):
        self.vault_url = os.getenv("VAULT_URL", "http://localhost:8200")
        self.vault_token = os.getenv("VAULT_TOKEN")
        self.vault_namespace = os.getenv("VAULT_NAMESPACE", "agent-platform")
        self.enabled = self._check_vault_enabled()

        if self.enabled:
            self.client = hvac.Client(url=self.vault_url, token=self.vault_token)
            logger.info(f"Vault client initialized: {self.vault_url}")
        else:
            self.client = None
            logger.warning("Vault not configured - using environment variables")

    def _check_vault_enabled(self) -> bool:
        """Check if Vault is configured and accessible."""
        if not self.vault_token:
            return False

        try:
            # Test connection
            client = hvac.Client(url=self.vault_url, token=self.vault_token)
            return client.is_authenticated()
        except Exception as e:
            logger.error(f"Vault connection failed: {e}")
            return False

    def get_secret(self, key: str, path: str = "secret/data/ai-providers") -> Optional[str]:
        """
        Retrieve secret from Vault.

        Args:
            key: Secret key name
            path: Vault path (default: secret/data/ai-providers)

        Returns:
            Secret value or None
        """
        if not self.enabled:
            # Fallback to environment variable
            env_key = key.upper().replace("-", "_")
            return os.getenv(env_key)

        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point='secret'
            )

            secrets = response['data']['data']
            return secrets.get(key)

        except Exception as e:
            logger.error(f"Failed to retrieve secret {key}: {e}")
            # Fallback to environment variable
            env_key = key.upper().replace("-", "_")
            return os.getenv(env_key)

    def set_secret(self, key: str, value: str, path: str = "ai-providers") -> bool:
        """
        Store secret in Vault.

        Args:
            key: Secret key name
            value: Secret value
            path: Vault path (default: ai-providers)

        Returns:
            True if successful
        """
        if not self.enabled:
            logger.warning("Vault not enabled - cannot store secret")
            return False

        try:
            # Get existing secrets
            try:
                response = self.client.secrets.kv.v2.read_secret_version(
                    path=path,
                    mount_point='secret'
                )
                existing_secrets = response['data']['data']
            except:
                existing_secrets = {}

            # Update with new secret
            existing_secrets[key] = value

            # Write back
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=existing_secrets,
                mount_point='secret'
            )

            logger.info(f"Secret {key} stored in Vault")
            return True

        except Exception as e:
            logger.error(f"Failed to store secret {key}: {e}")
            return False

    def delete_secret(self, key: str, path: str = "ai-providers") -> bool:
        """Delete secret from Vault."""
        if not self.enabled:
            return False

        try:
            # Get existing secrets
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point='secret'
            )
            secrets = response['data']['data']

            # Remove key
            if key in secrets:
                del secrets[key]

                # Write back
                self.client.secrets.kv.v2.create_or_update_secret(
                    path=path,
                    secret=secrets,
                    mount_point='secret'
                )

                logger.info(f"Secret {key} deleted from Vault")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete secret {key}: {e}")
            return False


class EncryptedSecretManager:
    """
    Database-backed encrypted secret storage.

    Uses Fernet (symmetric encryption) to encrypt secrets at rest.
    """

    def __init__(self):
        # Get encryption key from environment or generate
        encryption_key = os.getenv("ENCRYPTION_KEY")

        if not encryption_key:
            logger.warning("ENCRYPTION_KEY not set - secrets will not be encrypted!")
            self.cipher = None
        else:
            self.cipher = Fernet(encryption_key.encode())

    def encrypt(self, value: str) -> str:
        """Encrypt a value."""
        if not self.cipher:
            return value  # Store as plaintext if no encryption key

        encrypted = self.cipher.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt a value."""
        if not self.cipher:
            return encrypted_value  # Return as-is if no encryption

        try:
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt value: {e}")
            raise

    def store_secret(self, key: str, value: str, db: Session) -> bool:
        """
        Store encrypted secret in database.

        Args:
            key: Secret key
            value: Secret value (will be encrypted)
            db: Database session

        Returns:
            True if successful
        """
        from services.api.models import SystemConfig

        try:
            encrypted_value = self.encrypt(value)

            # Check if key exists
            config = db.query(SystemConfig).filter(SystemConfig.key == key).first()

            if config:
                config.value = encrypted_value
                config.is_sensitive = True
            else:
                config = SystemConfig(
                    key=key,
                    value=encrypted_value,
                    is_sensitive=True,
                    category="secrets"
                )
                db.add(config)

            db.commit()
            logger.info(f"Secret {key} stored in database (encrypted)")
            return True

        except Exception as e:
            logger.error(f"Failed to store secret {key}: {e}")
            db.rollback()
            return False

    def get_secret(self, key: str, db: Session) -> Optional[str]:
        """
        Retrieve and decrypt secret from database.

        Args:
            key: Secret key
            db: Database session

        Returns:
            Decrypted secret value or None
        """
        from services.api.models import SystemConfig

        try:
            config = db.query(SystemConfig).filter(
                SystemConfig.key == key,
                SystemConfig.is_sensitive == True
            ).first()

            if not config:
                return None

            return self.decrypt(config.value)

        except Exception as e:
            logger.error(f"Failed to retrieve secret {key}: {e}")
            return None


class UnifiedSecretManager:
    """
    Unified secret manager that tries Vault first, then encrypted DB, then env vars.

    Priority:
    1. HashiCorp Vault (if configured)
    2. Encrypted database storage
    3. Environment variables (fallback)
    """

    def __init__(self, db_session_factory=None):
        self.vault = VaultSecretManager()
        self.encrypted_db = EncryptedSecretManager()
        self.db_session_factory = db_session_factory

    def get_secret(self, key: str) -> Optional[str]:
        """
        Get secret from available sources (Vault → DB → Env).

        Args:
            key: Secret key

        Returns:
            Secret value or None
        """
        # Try Vault first
        if self.vault.enabled:
            secret = self.vault.get_secret(key)
            if secret:
                return secret

        # Try encrypted database
        if self.db_session_factory:
            db = self.db_session_factory()
            try:
                secret = self.encrypted_db.get_secret(key, db)
                if secret:
                    return secret
            finally:
                db.close()

        # Fallback to environment variable
        env_key = key.upper().replace("-", "_")
        return os.getenv(env_key)

    def set_secret(self, key: str, value: str) -> bool:
        """
        Store secret in best available location.

        Args:
            key: Secret key
            value: Secret value

        Returns:
            True if successful
        """
        # Prefer Vault
        if self.vault.enabled:
            return self.vault.set_secret(key, value)

        # Fallback to encrypted database
        if self.db_session_factory:
            db = self.db_session_factory()
            try:
                return self.encrypted_db.store_secret(key, value, db)
            finally:
                db.close()

        logger.error("No secret storage configured!")
        return False


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.

    Usage:
        key = generate_encryption_key()
        # Add to .env: ENCRYPTION_KEY=<key>
    """
    return Fernet.generate_key().decode()


# Global instance (initialized on import)
_secret_manager: Optional[UnifiedSecretManager] = None


def get_secret_manager(db_session_factory=None) -> UnifiedSecretManager:
    """Get or create global secret manager instance."""
    global _secret_manager

    if _secret_manager is None:
        _secret_manager = UnifiedSecretManager(db_session_factory)

    return _secret_manager


def migrate_secrets_to_vault(db_session_factory):
    """
    Migrate secrets from environment variables to Vault.

    This is a one-time migration script.
    """
    manager = get_secret_manager(db_session_factory)

    # List of secrets to migrate
    secrets_to_migrate = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
        "GROQ_API_KEY",
        "XAI_API_KEY",
        "SECRET_KEY",
        "DATABASE_URL",
        "REDIS_URL"
    ]

    migrated = []
    failed = []

    for secret_key in secrets_to_migrate:
        value = os.getenv(secret_key)
        if value:
            # Convert to lowercase with hyphens for Vault
            vault_key = secret_key.lower().replace("_", "-")

            if manager.set_secret(vault_key, value):
                migrated.append(secret_key)
                logger.info(f"Migrated {secret_key} to secret storage")
            else:
                failed.append(secret_key)
                logger.error(f"Failed to migrate {secret_key}")

    return {
        "migrated": migrated,
        "failed": failed,
        "total": len(secrets_to_migrate)
    }

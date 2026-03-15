import pytest
import json
import tempfile
import os
import sys

# Set test environment variables before importing
os.environ.setdefault("FEISHU_APP_ID", "test_app_id")
os.environ.setdefault("FEISHU_APP_SECRET", "test_app_secret")
os.environ.setdefault("DEFAULT_MODEL", "claude-opus-4-6")
os.environ.setdefault("PERMISSION_MODE", "bypassPermissions")

# Add parent directory to path to import session_store
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session_store import SessionStore


@pytest.fixture
def temp_store():
    """Create a temporary session store for testing"""
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)

    # Create a SessionStore with custom path
    store = SessionStore()
    store.SESSIONS_FILE = path
    store._data = {}
    store._save()

    yield store

    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


def test_get_current_with_chat_id_private(temp_store):
    """Test getting current session for private chat"""
    user_id = "user_123"
    chat_id = "user_123"  # Private chat: chat_id = user_id

    # Should return default session for new user
    session = temp_store.get_current(user_id, chat_id)
    assert session.model == "claude-opus-4-6"
    assert session.permission_mode == "bypassPermissions"


def test_get_current_with_chat_id_group(temp_store):
    """Test getting current session for group chat"""
    user_id = "user_123"
    chat_id = "group_456"

    # Should return default session for new group
    session = temp_store.get_current(user_id, chat_id)
    assert session.model == "claude-opus-4-6"
    assert session.permission_mode == "bypassPermissions"


def test_session_isolation_between_chats(temp_store):
    """Test that private and group sessions are isolated"""
    user_id = "user_123"
    private_chat_id = "user_123"
    group_chat_id = "group_456"

    # Set different models for private and group
    temp_store.set_model(user_id, private_chat_id, "claude-sonnet-4-6")
    temp_store.set_model(user_id, group_chat_id, "claude-haiku-4-5-20251001")

    # Verify isolation
    private_session = temp_store.get_current(user_id, private_chat_id)
    group_session = temp_store.get_current(user_id, group_chat_id)

    assert private_session.model == "claude-sonnet-4-6"
    assert group_session.model == "claude-haiku-4-5-20251001"

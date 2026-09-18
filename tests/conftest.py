"""
tests/conftest.py
------------------
Shared pytest fixtures. Uses an in-memory SQLite database so tests never
touch instance/app.db.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LLM_PROVIDER"] = "none"  # force Demo Mode during tests

from app import create_app
from database.database import db as _db


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def registered_user(client):
    """Registers and logs in a test user, returns the client (already logged in)."""
    client.post("/register", data={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)
    client.post("/login", data={
        "email": "test@example.com",
        "password": "password123",
    }, follow_redirects=True)
    return client

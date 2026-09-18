"""
database/database.py
---------------------
Creates the single SQLAlchemy() instance shared across the whole app.
Import `db` from here in models.py and in app.py — never create a
second SQLAlchemy() instance, or Flask-SQLAlchemy will break.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Attach db to the Flask app and create tables if they don't exist."""
    db.init_app(app)
    with app.app_context():
        # Import models here (not at module top) to avoid circular imports
        from database import models  # noqa: F401
        db.create_all()

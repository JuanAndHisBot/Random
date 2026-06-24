#!/usr/bin/env python
"""Initialize the database with schema."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import init_db

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        init_db(app)
        print("Database initialized successfully!")

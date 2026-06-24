#!/usr/bin/env python
"""Generate today's learning module using Claude API."""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.generator import generate_daily_module
from app.database import get_module_by_date, create_module, get_all_modules
from config import Config

if __name__ == '__main__':
    app = create_app()

    # Check if today's module already exists
    today = date.today()
    if get_module_by_date(today):
        print(f"Module for {today} already exists!")
        sys.exit(0)

    # Select topic based on round-robin (count of modules % num_topics)
    all_modules = get_all_modules(limit=None)
    topics = Config.LEARNING_TOPICS
    topic_index = len(all_modules) % len(topics)
    selected_topic = topics[topic_index]

    print(f"Generating module for {today}")
    print(f"Topic: {selected_topic}")

    try:
        module_data = generate_daily_module(selected_topic)

        with app.app_context():
            module = create_module(
                module_date=today,
                topic=module_data.get('topic', selected_topic),
                theory_overview=module_data.get('theory_overview', ''),
                code_examples=module_data.get('code_examples', []),
                socratic_questions=module_data.get('socratic_questions', []),
            )
            print(f"✓ Module created with {len(module.socratic_questions)} questions")
            print(f"✓ Saved to database")
    except Exception as e:
        print(f"✗ Error generating module: {e}")
        sys.exit(1)

import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///learning.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Claude API
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # Topics to generate (round-robin)
    LEARNING_TOPICS = [
        'Algorithms and Data Structures',
        'Database Design and SQL',
        'System Design Principles',
        'Software Architecture Patterns',
        'Distributed Systems',
        'Concurrency and Parallelism',
        'Network Protocols and Networking',
        'Security and Cryptography',
        'Performance Optimization',
        'Testing and Quality Assurance',
        'Machine Learning Fundamentals',
        'Cloud Computing',
        'DevOps and CI/CD',
        'API Design',
        'Software Design Patterns',
    ]

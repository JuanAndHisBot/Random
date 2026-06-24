# Daily Learning System

A personalized daily learning platform powered by Claude that uses the Socratic method to guide you through discovering knowledge in computer science, software engineering, system design, and programming.

## Features

- **Daily Learning Modules**: New module generated each day on a rotating set of CS topics
- **Socratic Method**: 5-7 progressive questions designed to guide deep thinking and discovery
- **Theory Reference**: Collapsible theory overview and code examples for reference
- **Progress Tracking**: Track completed modules and review your learning journey
- **Model Answers & Explanations**: After answering, see expert model answers and understand the "why"

## Topics Covered

- Algorithms and Data Structures
- Database Design and SQL
- System Design Principles
- Software Architecture Patterns
- Distributed Systems
- Concurrency and Parallelism
- Network Protocols
- Security and Cryptography
- Performance Optimization
- Testing and Quality Assurance
- Machine Learning Fundamentals
- Cloud Computing
- DevOps and CI/CD
- API Design
- Software Design Patterns

## Setup

### Prerequisites

- Python 3.8+
- Claude API key (from Anthropic)

### Installation

1. Clone the repository and navigate to the directory:
```bash
cd /home/user/Random
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the template:
```bash
cp .env.example .env
```

5. Add your Claude API key to `.env`:
```
ANTHROPIC_API_KEY=your-api-key-here
```

6. Initialize the database:
```bash
python scripts/init_db.py
```

### Generate Today's Module

```bash
python scripts/generate_daily.py
```

This will:
1. Select a topic (round-robin through the topics list)
2. Call Claude API to generate a module with Socratic questions
3. Store it in the database

### Run the Server

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **Visit Today's Module**: Navigate to `/today` to see today's learning module
2. **Read Theory**: Expand the theory overview and code examples for context
3. **Answer Questions**: Work through the 7 Socratic questions one by one
4. **Review Answers**: After answering, see model answers and explanations
5. **Browse Archive**: Visit `/archive` to access previous modules
6. **Track Progress**: Visit `/progress` to see your learning statistics

## Project Structure

```
app/
  __init__.py         - Flask app factory
  main.py            - Routes and endpoints
  models.py          - Database models (Module, SocraticQuestion, UserProgress)
  database.py        - Database helpers
  generator.py       - Claude API integration
  templates/         - HTML templates
    base.html
    module.html
    archive.html
    progress.html
    no_module.html

static/
  css/style.css      - Styling
  js/quiz.js         - Socratic dialogue interaction

scripts/
  init_db.py         - Database initialization
  generate_daily.py  - Daily module generation

config.py            - Configuration
requirements.txt     - Python dependencies
run.py              - Development server entry point
```

## Database Schema

- **modules**: Stores daily learning modules (date, topic, theory, code examples)
- **socratic_questions**: Stores the 7 Socratic questions for each module with model answers and explanations
- **user_progress**: Tracks user answers and module completion status

## API Endpoints

- `GET /` - Redirect to today's module
- `GET /today` - Display today's module
- `GET /module/<date>` - Display a specific module (YYYY-MM-DD format)
- `GET /archive` - List all modules
- `GET /progress` - User progress dashboard
- `GET /api/module/<date>/questions` - Get all questions for a module
- `POST /api/socratic/submit` - Submit an answer to a question
- `GET /api/module/<date>/review` - Get a module with all answers for review

## Scheduling Daily Generation

To generate a new module every day, set up a cron job:

```bash
# Run at 6 AM daily
0 6 * * * cd /home/user/Random && python scripts/generate_daily.py
```

Or on Windows, use Task Scheduler to run `generate_daily.py` daily.

## Future Enhancements

- Adaptive Socratic dialogue based on answer quality
- Difficulty levels (beginner, intermediate, advanced)
- Topic preferences and filtering
- Spaced repetition system
- Learning analytics and weak area identification
- Real-time Claude evaluation of answers
- Discussion threads for peer learning
- Dark mode
- Export learning journey as report

## License

Educational use

# Quick Start Guide

## Project Overview

You now have a fully functional **Daily Learning System** built with Flask that uses Claude's API to generate daily learning modules based on the Socratic method.

## Architecture

```
Daily Learning System
├── Backend (Flask + SQLAlchemy)
│   ├── Content Generation (Claude API)
│   ├── RESTful API for Socratic Dialogue
│   └── SQLite Database
├── Frontend (HTML/CSS/JavaScript)
│   ├── Module Display (Theory + Code Examples)
│   ├── Interactive Socratic Dialogue
│   └── Progress Dashboard
└── Scripts
    ├── Database Initialization
    └── Daily Module Generation
```

## What's Implemented

✅ **Core System**
- Flask web application with routes for all pages
- SQLAlchemy ORM with three models: Module, SocraticQuestion, UserProgress
- SQLite database (pre-initialized)

✅ **Content Generation**
- Claude API integration using anthropic SDK
- Structured JSON output parsing for modules and questions
- Daily generation script with round-robin topic selection

✅ **Web Interface**
- Today's module display with collapsible theory and code examples
- Interactive Socratic dialogue (questions 1-7, sequential flow)
- Archive page to browse past modules by topic
- Progress dashboard with completion statistics and learning history

✅ **API Endpoints**
- `/api/socratic/submit` - Submit answers and get model responses
- `/api/module/<date>/questions` - Fetch all questions for a module
- `/api/module/<date>/review` - Review all answers vs. model answers

✅ **Styling**
- Custom CSS with learning-optimized colors and typography
- Responsive design (desktop, tablet, mobile)
- Dark header with accent colors, light content areas

## Setup (Already Done)

```bash
# 1. Dependencies installed ✓
# 2. Database initialized ✓
# 3. Project pushed to branch ✓
```

## Next Steps to Use

### 1. Get Claude API Key

Get your API key from [api.anthropic.com](https://api.anthropic.com)

### 2. Create `.env` File

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Generate Today's Module

```bash
python scripts/generate_daily.py
```

This will:
- Select a topic (round-robin from the 15 topics list)
- Call Claude to generate the module
- Store it in the database

### 4. Run the Server

```bash
python run.py
```

Visit: http://localhost:5000

### 5. Explore the System

- **Today's Module**: See the Socratic dialogue in action
- **Archive**: Browse any previously generated modules
- **Progress**: Track your learning journey

## How It Works: Socratic Dialogue Flow

1. **User visits module page**
   - Theory overview (collapsible)
   - Code examples (collapsible)
   - Question 1 displayed

2. **User answers Question 1**
   - Types answer in textarea
   - Clicks "Submit Answer"

3. **System shows feedback**
   - Model answer
   - Explanation of why the answer matters
   - "Next Question" button

4. **Repeat for Questions 2-7**
   - Progressive questions build on previous answers
   - Each reveals more depth
   - User can review all answers at the end

5. **Module completion**
   - "Review Answers" button shows all Q&A pairs
   - Progress is saved to database

## Database Structure

### modules table
- date (unique)
- topic
- theory_overview
- code_examples (JSON array)

### socratic_questions table
- module_id (FK)
- question_number (1-7)
- question_text
- model_answer
- explanation
- code_context (optional)

### user_progress table
- module_id (FK)
- user_answers (JSON dict)
- completed (boolean)
- timestamp

## API Response Example

When you submit an answer to a Socratic question:

```json
{
  "question_number": 1,
  "model_answer": "A queue follows FIFO (First-In-First-Out) principle...",
  "explanation": "Understanding FIFO is crucial because...",
  "code_context": {},
  "next_question_number": 2,
  "next_question_text": "How would you implement a queue with an array?"
}
```

## Generate Multiple Modules

Run the generation script multiple times to populate the database:

```bash
# Generate 5 days worth of modules
for i in {1..5}; do
    python scripts/generate_daily.py
    # Manually adjust the date in the script if needed for testing
done
```

## Customize Topics

Edit `config.py` to add or change learning topics:

```python
LEARNING_TOPICS = [
    'Your Topic Here',
    'Another Topic',
    # ... more topics
]
```

## Architecture Decisions

- **Flask**: Simple, lightweight, good for learning systems
- **SQLAlchemy + SQLite**: No external database needed, easy setup
- **Claude API**: High-quality content generation with structured output
- **Vanilla JavaScript**: No heavy frameworks, pure interactive dialogue
- **Round-robin topics**: Fair distribution across CS domains

## Future Enhancement Ideas

See `/root/.claude/plans/lets-explore-this-idea-create-imperative-balloon.md` for detailed enhancement roadmap including:
- Adaptive dialogue (Claude evaluates answer quality)
- Spaced repetition
- Learning analytics
- Dark mode
- Discussion threads

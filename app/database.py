from .models import db, Module, SocraticQuestion, UserProgress
from datetime import datetime, date
from sqlalchemy import func


def init_db(app):
    """Initialize the database."""
    with app.app_context():
        db.create_all()


def get_module_by_date(module_date):
    """Get a module by its date."""
    if isinstance(module_date, str):
        from datetime import datetime as dt
        module_date = dt.fromisoformat(module_date).date()
    return Module.query.filter_by(date=module_date).first()


def get_today_module():
    """Get today's module, creating a placeholder if none exists."""
    today = date.today()
    module = get_module_by_date(today)
    return module


def get_all_modules(limit=None):
    """Get all modules ordered by date (newest first)."""
    query = Module.query.order_by(Module.date.desc())
    if limit:
        query = query.limit(limit)
    return query.all()


def create_module(module_date, topic, theory_overview, code_examples, socratic_questions):
    """Create a new module with its Socratic questions."""
    module = Module(
        date=module_date,
        topic=topic,
        theory_overview=theory_overview,
        code_examples=code_examples,
    )
    db.session.add(module)
    db.session.flush()  # Get the module ID

    for i, q_data in enumerate(socratic_questions, 1):
        question = SocraticQuestion(
            module_id=module.id,
            question_number=i,
            question_text=q_data['question_text'],
            model_answer=q_data['model_answer'],
            explanation=q_data['explanation'],
            code_context=q_data.get('code_context', {}),
        )
        db.session.add(question)

    db.session.commit()
    return module


def get_user_progress(module_date):
    """Get user progress for a module."""
    module = get_module_by_date(module_date)
    if not module:
        return None
    return UserProgress.query.filter_by(module_id=module.id).first()


def save_user_answer(module_date, question_number, user_answer):
    """Save or update a user's answer to a Socratic question."""
    module = get_module_by_date(module_date)
    if not module:
        return None

    progress = UserProgress.query.filter_by(module_id=module.id).first()
    if not progress:
        progress = UserProgress(module_id=module.id)
        db.session.add(progress)

    answers = progress.user_answers
    answers[str(question_number)] = user_answer
    progress.user_answers = answers

    # Mark as completed if all 7 questions are answered
    questions_count = len(module.socratic_questions)
    if len(answers) >= questions_count:
        progress.completed = True

    db.session.commit()
    return progress


def get_module_statistics():
    """Get learning statistics."""
    total_modules = db.session.query(func.count(Module.id)).scalar() or 0
    completed_modules = db.session.query(func.count(UserProgress.id)).filter(
        UserProgress.completed == True
    ).scalar() or 0

    return {
        'total_modules': total_modules,
        'completed_modules': completed_modules,
        'completion_percentage': (completed_modules / total_modules * 100) if total_modules > 0 else 0,
    }

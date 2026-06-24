from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import date, datetime
from .database import (
    get_today_module, get_module_by_date, get_all_modules,
    save_user_answer, get_user_progress, get_module_statistics
)

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Redirect to today's module."""
    return redirect(url_for('main.today'))


@bp.route('/today')
def today():
    """Display today's learning module."""
    today_date = date.today()
    module = get_today_module()

    if not module:
        return render_template('no_module.html', date=today_date)

    progress = get_user_progress(today_date)
    user_answers = progress.user_answers if progress else {}

    return render_template(
        'module.html',
        module=module,
        user_answers=user_answers,
        is_today=True
    )


@bp.route('/module/<module_date>')
def module_detail(module_date):
    """Display a specific module by date (YYYY-MM-DD format)."""
    try:
        date_obj = datetime.fromisoformat(module_date).date()
    except ValueError:
        return "Invalid date format", 400

    module = get_module_by_date(date_obj)
    if not module:
        return render_template('no_module.html', date=date_obj), 404

    progress = get_user_progress(date_obj)
    user_answers = progress.user_answers if progress else {}

    return render_template(
        'module.html',
        module=module,
        user_answers=user_answers,
        is_today=(date_obj == date.today())
    )


@bp.route('/archive')
def archive():
    """Display all past modules."""
    modules = get_all_modules()
    return render_template('archive.html', modules=modules)


@bp.route('/progress')
def progress():
    """Display user progress dashboard."""
    stats = get_module_statistics()
    modules = get_all_modules()

    # Enrich modules with progress data
    for module in modules:
        module_progress = get_user_progress(module.date)
        module.progress = module_progress
        module.is_completed = module_progress.completed if module_progress else False

    return render_template(
        'progress.html',
        stats=stats,
        modules=modules
    )


@bp.route('/api/module/<module_date>/questions')
def get_module_questions(module_date):
    """Get all Socratic questions for a module."""
    try:
        date_obj = datetime.fromisoformat(module_date).date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    module = get_module_by_date(date_obj)
    if not module:
        return jsonify({'error': 'Module not found'}), 404

    progress = get_user_progress(date_obj)
    user_answers = progress.user_answers if progress else {}

    questions = [{
        'id': q.id,
        'question_number': q.question_number,
        'question_text': q.question_text,
        'user_answer': user_answers.get(str(q.question_number), None),
    } for q in module.socratic_questions]

    return jsonify({
        'module_date': module_date,
        'topic': module.topic,
        'questions': questions,
    })


@bp.route('/api/socratic/submit', methods=['POST'])
def submit_socratic_answer():
    """Submit an answer to a Socratic question and get model answer."""
    data = request.json
    module_date = data.get('module_date')
    question_number = data.get('question_number')
    user_answer = data.get('user_answer', '').strip()

    if not module_date or not question_number or not user_answer:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        date_obj = datetime.fromisoformat(module_date).date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    module = get_module_by_date(date_obj)
    if not module:
        return jsonify({'error': 'Module not found'}), 404

    # Find the question
    question = next(
        (q for q in module.socratic_questions if q.question_number == question_number),
        None
    )
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    # Save user's answer
    save_user_answer(module_date, question_number, user_answer)

    # Determine next question
    next_question_number = question_number + 1
    next_question = next(
        (q for q in module.socratic_questions if q.question_number == next_question_number),
        None
    )

    response = {
        'question_number': question_number,
        'model_answer': question.model_answer,
        'explanation': question.explanation,
        'code_context': question.code_context,
        'next_question_number': next_question_number if next_question else None,
        'next_question_text': next_question.question_text if next_question else None,
    }

    return jsonify(response)


@bp.route('/api/module/<module_date>/review')
def review_module(module_date):
    """Get a module with all answers for review."""
    try:
        date_obj = datetime.fromisoformat(module_date).date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    module = get_module_by_date(date_obj)
    if not module:
        return jsonify({'error': 'Module not found'}), 404

    progress = get_user_progress(date_obj)
    user_answers = progress.user_answers if progress else {}

    questions_with_answers = []
    for question in module.socratic_questions:
        questions_with_answers.append({
            'question_number': question.question_number,
            'question_text': question.question_text,
            'user_answer': user_answers.get(str(question.question_number), None),
            'model_answer': question.model_answer,
            'explanation': question.explanation,
        })

    return jsonify({
        'module_date': module_date,
        'topic': module.topic,
        'completed': progress.completed if progress else False,
        'questions': questions_with_answers,
    })

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False, index=True)
    topic = db.Column(db.String(255), nullable=False)
    theory_overview = db.Column(db.Text, nullable=False)
    code_examples_json = db.Column(db.Text, nullable=False, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    socratic_questions = db.relationship('SocraticQuestion', backref='module', lazy=True, cascade='all, delete-orphan')
    user_progress = db.relationship('UserProgress', backref='module', lazy=True, cascade='all, delete-orphan')

    @property
    def code_examples(self):
        return json.loads(self.code_examples_json)

    @code_examples.setter
    def code_examples(self, value):
        self.code_examples_json = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'topic': self.topic,
            'theory_overview': self.theory_overview,
            'code_examples': self.code_examples,
            'created_at': self.created_at.isoformat(),
        }


class SocraticQuestion(db.Model):
    __tablename__ = 'socratic_questions'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    model_answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    code_context_json = db.Column(db.Text, nullable=False, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def code_context(self):
        return json.loads(self.code_context_json)

    @code_context.setter
    def code_context(self, value):
        self.code_context_json = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'question_number': self.question_number,
            'question_text': self.question_text,
            'model_answer': self.model_answer,
            'explanation': self.explanation,
            'code_context': self.code_context,
        }


class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_answers_json = db.Column(db.Text, nullable=False, default='{}')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def user_answers(self):
        return json.loads(self.user_answers_json)

    @user_answers.setter
    def user_answers(self, value):
        self.user_answers_json = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'completed': self.completed,
            'user_answers': self.user_answers,
            'timestamp': self.timestamp.isoformat(),
        }

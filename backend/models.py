from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    progress = db.relationship('UserProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    lab_submissions = db.relationship('LabSubmission', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_admin': self.is_admin
        }

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    is_published = db.Column(db.Boolean, default=True)
    day_start = db.Column(db.Integer)  # e.g., 1 for days 1-5
    day_end = db.Column(db.Integer)    # e.g., 5
    
    # Relationships
    lessons = db.relationship('Lesson', backref='module', lazy=True, cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='module', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_lessons=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order_index': self.order_index,
            'is_published': self.is_published,
            'day_start': self.day_start,
            'day_end': self.day_end
        }
        if include_lessons:
            data['lessons'] = [lesson.to_dict() for lesson in sorted(self.lessons, key=lambda x: x.order_index)]
        return data

class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    estimated_time = db.Column(db.Integer)  # in minutes
    is_published = db.Column(db.Boolean, default=True)
    
    # Relationships
    labs = db.relationship('Lab', backref='lesson', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('UserProgress', backref='lesson', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_content=True):
        data = {
            'id': self.id,
            'module_id': self.module_id,
            'title': self.title,
            'order_index': self.order_index,
            'estimated_time': self.estimated_time,
            'is_published': self.is_published
        }
        if include_content:
            data['content'] = self.content
        return data

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    passing_score = db.Column(db.Integer, default=70)
    time_limit = db.Column(db.Integer)  # in minutes, null = no limit
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_questions=True):
        data = {
            'id': self.id,
            'module_id': self.module_id,
            'title': self.title,
            'passing_score': self.passing_score,
            'time_limit': self.time_limit
        }
        if include_questions:
            data['questions'] = [q.to_dict() for q in self.questions]
        return data

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # multiple_choice, true_false, code_output
    options = db.Column(db.Text)  # JSON string
    correct_answer = db.Column(db.String(500), nullable=False)
    explanation = db.Column(db.Text)
    
    def to_dict(self, include_answer=False):
        data = {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': json.loads(self.options) if self.options else None,
            'explanation': self.explanation
        }
        if include_answer:
            data['correct_answer'] = self.correct_answer
        return data

class Lab(db.Model):
    __tablename__ = 'labs'
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    starter_code = db.Column(db.Text)
    solution_code = db.Column(db.Text)
    test_cases = db.Column(db.Text)  # JSON string
    difficulty = db.Column(db.String(20))  # beginner, intermediate, advanced
    hints = db.Column(db.Text)  # JSON array of hints
    
    # Relationships
    submissions = db.relationship('LabSubmission', backref='lab', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_solution=False):
        data = {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'description': self.description,
            'starter_code': self.starter_code,
            'difficulty': self.difficulty,
            'hints': json.loads(self.hints) if self.hints else [],
            'test_cases': json.loads(self.test_cases) if self.test_cases else []
        }
        if include_solution:
            data['solution_code'] = self.solution_code
        return data

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    answers = db.Column(db.Text)  # JSON string
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'score': self.score,
            'answers': json.loads(self.answers) if self.answers else {},
            'attempted_at': self.attempted_at.isoformat() if self.attempted_at else None
        }

class LabSubmission(db.Model):
    __tablename__ = 'lab_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    passed = db.Column(db.Boolean, default=False)
    test_results = db.Column(db.Text)  # JSON string with test results
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lab_id': self.lab_id,
            'code': self.code,
            'passed': self.passed,
            'test_results': json.loads(self.test_results) if self.test_results else {},
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

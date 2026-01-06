from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Module, Lesson, Quiz, Question, Lab
import json

admin_bp = Blueprint('admin', __name__)

def admin_required(fn):
    """Decorator to check if user is admin"""
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return fn(*args, **kwargs)
    
    wrapper.__name__ = fn.__name__
    return wrapper

# Module Management
@admin_bp.route('/modules', methods=['POST'])
@admin_required
def create_module():
    try:
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        module = Module(
            title=data['title'],
            description=data.get('description', ''),
            order_index=data.get('order_index', 1),
            is_published=data.get('is_published', False),
            day_start=data.get('day_start'),
            day_end=data.get('day_end')
        )
        
        db.session.add(module)
        db.session.commit()
        
        return jsonify({
            'message': 'Module created successfully',
            'module': module.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/modules/<int:module_id>', methods=['PUT'])
@admin_required
def update_module(module_id):
    try:
        module = Module.query.get(module_id)
        
        if not module:
            return jsonify({'error': 'Module not found'}), 404
        
        data = request.get_json()
        
        if 'title' in data:
            module.title = data['title']
        if 'description' in data:
            module.description = data['description']
        if 'order_index' in data:
            module.order_index = data['order_index']
        if 'is_published' in data:
            module.is_published = data['is_published']
        if 'day_start' in data:
            module.day_start = data['day_start']
        if 'day_end' in data:
            module.day_end = data['day_end']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Module updated successfully',
            'module': module.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Lesson Management
@admin_bp.route('/lessons', methods=['POST'])
@admin_required
def create_lesson():
    try:
        data = request.get_json()
        
        required_fields = ['module_id', 'title', 'content']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'module_id, title, and content are required'}), 400
        
        lesson = Lesson(
            module_id=data['module_id'],
            title=data['title'],
            content=data['content'],
            order_index=data.get('order_index', 1),
            estimated_time=data.get('estimated_time', 30),
            is_published=data.get('is_published', False)
        )
        
        db.session.add(lesson)
        db.session.commit()
        
        return jsonify({
            'message': 'Lesson created successfully',
            'lesson': lesson.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Quiz Management
@admin_bp.route('/quizzes', methods=['POST'])
@admin_required
def create_quiz():
    try:
        data = request.get_json()
        
        if not data or not data.get('module_id') or not data.get('title'):
            return jsonify({'error': 'module_id and title are required'}), 400
        
        quiz = Quiz(
            module_id=data['module_id'],
            title=data['title'],
            passing_score=data.get('passing_score', 70),
            time_limit=data.get('time_limit')
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz created successfully',
            'quiz': quiz.to_dict(include_questions=False)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/questions', methods=['POST'])
@admin_required
def create_question():
    try:
        data = request.get_json()
        
        required_fields = ['quiz_id', 'question_text', 'question_type', 'correct_answer']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        question = Question(
            quiz_id=data['quiz_id'],
            question_text=data['question_text'],
            question_type=data['question_type'],
            options=json.dumps(data.get('options', [])),
            correct_answer=data['correct_answer'],
            explanation=data.get('explanation', '')
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'message': 'Question created successfully',
            'question': question.to_dict(include_answer=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Lab Management
@admin_bp.route('/labs', methods=['POST'])
@admin_required
def create_lab():
    try:
        data = request.get_json()
        
        required_fields = ['lesson_id', 'title', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        lab = Lab(
            lesson_id=data['lesson_id'],
            title=data['title'],
            description=data['description'],
            starter_code=data.get('starter_code', ''),
            solution_code=data.get('solution_code', ''),
            test_cases=json.dumps(data.get('test_cases', [])),
            difficulty=data.get('difficulty', 'beginner'),
            hints=json.dumps(data.get('hints', []))
        )
        
        db.session.add(lab)
        db.session.commit()
        
        return jsonify({
            'message': 'Lab created successfully',
            'lab': lab.to_dict(include_solution=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        users = User.query.all()
        
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/admin', methods=['PUT'])
@admin_required
def toggle_admin(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_admin = not user.is_admin
        db.session.commit()
        
        return jsonify({
            'message': f'User admin status updated',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

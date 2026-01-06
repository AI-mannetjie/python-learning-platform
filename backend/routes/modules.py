from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Module, UserProgress, Lesson

modules_bp = Blueprint('modules', __name__)

@modules_bp.route('', methods=['GET'])
@jwt_required()
def get_modules():
    try:
        current_user_id = get_jwt_identity()
        modules = Module.query.filter_by(is_published=True).order_by(Module.order_index).all()
        
        # Get user progress for all lessons
        progress_records = UserProgress.query.filter_by(user_id=current_user_id).all()
        completed_lesson_ids = {p.lesson_id for p in progress_records if p.completed}
        
        result = []
        for module in modules:
            module_data = module.to_dict(include_lessons=False)
            
            # Calculate module completion
            lessons = Lesson.query.filter_by(module_id=module.id, is_published=True).all()
            total_lessons = len(lessons)
            completed_lessons = sum(1 for lesson in lessons if lesson.id in completed_lesson_ids)
            
            module_data['total_lessons'] = total_lessons
            module_data['completed_lessons'] = completed_lessons
            module_data['completion_percentage'] = (
                round((completed_lessons / total_lessons) * 100, 1) if total_lessons > 0 else 0
            )
            
            result.append(module_data)
        
        return jsonify({'modules': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@modules_bp.route('/<int:module_id>', methods=['GET'])
@jwt_required()
def get_module(module_id):
    try:
        current_user_id = get_jwt_identity()
        module = Module.query.get(module_id)
        
        if not module or not module.is_published:
            return jsonify({'error': 'Module not found'}), 404
        
        # Get user progress
        progress_records = UserProgress.query.filter_by(user_id=current_user_id).all()
        completed_lesson_ids = {p.lesson_id for p in progress_records if p.completed}
        
        module_data = module.to_dict(include_lessons=True)
        
        # Add completion status to each lesson
        for lesson in module_data['lessons']:
            lesson['completed'] = lesson['id'] in completed_lesson_ids
        
        return jsonify({'module': module_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@modules_bp.route('/<int:module_id>/lessons', methods=['GET'])
@jwt_required()
def get_module_lessons(module_id):
    try:
        current_user_id = get_jwt_identity()
        module = Module.query.get(module_id)
        
        if not module or not module.is_published:
            return jsonify({'error': 'Module not found'}), 404
        
        lessons = Lesson.query.filter_by(
            module_id=module_id,
            is_published=True
        ).order_by(Lesson.order_index).all()
        
        # Get user progress
        progress_records = UserProgress.query.filter_by(user_id=current_user_id).all()
        completed_lesson_ids = {p.lesson_id for p in progress_records if p.completed}
        
        result = []
        for lesson in lessons:
            lesson_data = lesson.to_dict(include_content=False)
            lesson_data['completed'] = lesson.id in completed_lesson_ids
            result.append(lesson_data)
        
        return jsonify({'lessons': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

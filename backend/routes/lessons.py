from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Lesson, UserProgress, Lab
from datetime import datetime

lessons_bp = Blueprint('lessons', __name__)

@lessons_bp.route('/<int:lesson_id>', methods=['GET'])
@jwt_required()
def get_lesson(lesson_id):
    try:
        current_user_id = get_jwt_identity()
        lesson = Lesson.query.get(lesson_id)
        
        if not lesson or not lesson.is_published:
            return jsonify({'error': 'Lesson not found'}), 404
        
        lesson_data = lesson.to_dict(include_content=True)
        
        # Check if user completed this lesson
        progress = UserProgress.query.filter_by(
            user_id=current_user_id,
            lesson_id=lesson_id
        ).first()
        
        lesson_data['completed'] = progress.completed if progress else False
        
        # Get associated labs
        labs = Lab.query.filter_by(lesson_id=lesson_id).all()
        lesson_data['labs'] = [lab.to_dict(include_solution=False) for lab in labs]
        
        # Get next and previous lessons
        current_order = lesson.order_index
        module_id = lesson.module_id
        
        prev_lesson = Lesson.query.filter(
            Lesson.module_id == module_id,
            Lesson.order_index < current_order,
            Lesson.is_published == True
        ).order_by(Lesson.order_index.desc()).first()
        
        next_lesson = Lesson.query.filter(
            Lesson.module_id == module_id,
            Lesson.order_index > current_order,
            Lesson.is_published == True
        ).order_by(Lesson.order_index).first()
        
        lesson_data['prev_lesson_id'] = prev_lesson.id if prev_lesson else None
        lesson_data['next_lesson_id'] = next_lesson.id if next_lesson else None
        
        return jsonify({'lesson': lesson_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lessons_bp.route('/<int:lesson_id>/complete', methods=['POST'])
@jwt_required()
def complete_lesson(lesson_id):
    try:
        current_user_id = get_jwt_identity()
        lesson = Lesson.query.get(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        # Check if progress record exists
        progress = UserProgress.query.filter_by(
            user_id=current_user_id,
            lesson_id=lesson_id
        ).first()
        
        if progress:
            if not progress.completed:
                progress.completed = True
                progress.completed_at = datetime.utcnow()
        else:
            progress = UserProgress(
                user_id=current_user_id,
                lesson_id=lesson_id,
                completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Lesson marked as complete',
            'progress': progress.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

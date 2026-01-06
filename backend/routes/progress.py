from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Module, Lesson, UserProgress, QuizAttempt, LabSubmission
from sqlalchemy import func

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('', methods=['GET'])
@jwt_required()
def get_user_progress():
    try:
        current_user_id = get_jwt_identity()
        
        # Get all modules
        total_modules = Module.query.filter_by(is_published=True).count()
        
        # Get all lessons
        total_lessons = Lesson.query.filter(
            Lesson.is_published == True,
            Lesson.module_id.in_(
                db.session.query(Module.id).filter(Module.is_published == True)
            )
        ).count()
        
        # Get completed lessons
        completed_lessons = UserProgress.query.filter_by(
            user_id=current_user_id,
            completed=True
        ).count()
        
        # Get quiz attempts
        quiz_attempts = QuizAttempt.query.filter_by(user_id=current_user_id).count()
        
        # Get average quiz score
        avg_quiz_score = db.session.query(
            func.avg(QuizAttempt.score)
        ).filter_by(user_id=current_user_id).scalar()
        
        # Get lab submissions
        total_labs = LabSubmission.query.filter_by(user_id=current_user_id).count()
        passed_labs = LabSubmission.query.filter_by(
            user_id=current_user_id,
            passed=True
        ).distinct(LabSubmission.lab_id).count()
        
        # Calculate streak (simplified version)
        # In production, you'd want to check consecutive days
        progress_records = UserProgress.query.filter_by(
            user_id=current_user_id,
            completed=True
        ).order_by(UserProgress.completed_at.desc()).limit(7).all()
        
        current_streak = len(progress_records)
        
        # Calculate overall completion percentage
        overall_completion = round((completed_lessons / total_lessons) * 100, 1) if total_lessons > 0 else 0
        
        # Get next recommended lesson
        completed_lesson_ids = {p.lesson_id for p in UserProgress.query.filter_by(
            user_id=current_user_id,
            completed=True
        ).all()}
        
        next_lesson = Lesson.query.filter(
            Lesson.is_published == True,
            ~Lesson.id.in_(completed_lesson_ids)
        ).order_by(Lesson.module_id, Lesson.order_index).first()
        
        # Get module-wise progress
        modules = Module.query.filter_by(is_published=True).order_by(Module.order_index).all()
        module_progress = []
        
        for module in modules:
            module_lessons = Lesson.query.filter_by(
                module_id=module.id,
                is_published=True
            ).all()
            
            total = len(module_lessons)
            completed = sum(1 for lesson in module_lessons if lesson.id in completed_lesson_ids)
            
            module_progress.append({
                'module_id': module.id,
                'module_title': module.title,
                'total_lessons': total,
                'completed_lessons': completed,
                'completion_percentage': round((completed / total) * 100, 1) if total > 0 else 0
            })
        
        return jsonify({
            'progress': {
                'overall_completion': overall_completion,
                'total_modules': total_modules,
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'quiz_attempts': quiz_attempts,
                'average_quiz_score': round(avg_quiz_score, 1) if avg_quiz_score else 0,
                'total_labs': total_labs,
                'passed_labs': passed_labs,
                'current_streak': current_streak,
                'next_lesson': next_lesson.to_dict(include_content=False) if next_lesson else None,
                'module_progress': module_progress
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent activity
        recent_lessons = UserProgress.query.filter_by(
            user_id=current_user_id,
            completed=True
        ).order_by(UserProgress.completed_at.desc()).limit(5).all()
        
        recent_quizzes = QuizAttempt.query.filter_by(
            user_id=current_user_id
        ).order_by(QuizAttempt.attempted_at.desc()).limit(5).all()
        
        recent_labs = LabSubmission.query.filter_by(
            user_id=current_user_id
        ).order_by(LabSubmission.submitted_at.desc()).limit(5).all()
        
        return jsonify({
            'dashboard': {
                'user': user.to_dict(),
                'recent_lessons': [
                    {
                        'lesson_id': p.lesson_id,
                        'completed_at': p.completed_at.isoformat() if p.completed_at else None
                    } for p in recent_lessons
                ],
                'recent_quizzes': [
                    {
                        'quiz_id': q.quiz_id,
                        'score': q.score,
                        'attempted_at': q.attempted_at.isoformat() if q.attempted_at else None
                    } for q in recent_quizzes
                ],
                'recent_labs': [
                    {
                        'lab_id': l.lab_id,
                        'passed': l.passed,
                        'submitted_at': l.submitted_at.isoformat() if l.submitted_at else None
                    } for l in recent_labs
                ]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

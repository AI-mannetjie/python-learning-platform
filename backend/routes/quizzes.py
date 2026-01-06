from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Quiz, Question, QuizAttempt
from datetime import datetime
import json

quizzes_bp = Blueprint('quizzes', __name__)

@quizzes_bp.route('/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    try:
        quiz = Quiz.query.get(quiz_id)
        
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        quiz_data = quiz.to_dict(include_questions=True)
        
        # Don't include correct answers when fetching quiz
        for question in quiz_data['questions']:
            question.pop('correct_answer', None)
        
        return jsonify({'quiz': quiz_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'answers' not in data:
            return jsonify({'error': 'Answers are required'}), 400
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        user_answers = data['answers']  # {question_id: answer}
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        # Grade the quiz
        correct_count = 0
        total_questions = len(questions)
        detailed_results = []
        
        for question in questions:
            user_answer = user_answers.get(str(question.id), '')
            is_correct = str(user_answer).strip().lower() == str(question.correct_answer).strip().lower()
            
            if is_correct:
                correct_count += 1
            
            detailed_results.append({
                'question_id': question.id,
                'user_answer': user_answer,
                'correct_answer': question.correct_answer,
                'is_correct': is_correct,
                'explanation': question.explanation
            })
        
        score = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0
        passed = score >= quiz.passing_score
        
        # Save attempt
        attempt = QuizAttempt(
            user_id=current_user_id,
            quiz_id=quiz_id,
            score=score,
            answers=json.dumps(user_answers),
            attempted_at=datetime.utcnow()
        )
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'score': score,
            'passed': passed,
            'correct_count': correct_count,
            'total_questions': total_questions,
            'passing_score': quiz.passing_score,
            'detailed_results': detailed_results,
            'attempt_id': attempt.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/<int:quiz_id>/attempts', methods=['GET'])
@jwt_required()
def get_quiz_attempts(quiz_id):
    try:
        current_user_id = get_jwt_identity()
        
        attempts = QuizAttempt.query.filter_by(
            user_id=current_user_id,
            quiz_id=quiz_id
        ).order_by(QuizAttempt.attempted_at.desc()).all()
        
        return jsonify({
            'attempts': [attempt.to_dict() for attempt in attempts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/module/<int:module_id>', methods=['GET'])
@jwt_required()
def get_module_quiz(module_id):
    try:
        quiz = Quiz.query.filter_by(module_id=module_id).first()
        
        if not quiz:
            return jsonify({'error': 'Quiz not found for this module'}), 404
        
        return jsonify({'quiz': quiz.to_dict(include_questions=False)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

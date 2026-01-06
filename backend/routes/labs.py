from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Lab, LabSubmission
from datetime import datetime
import json
import subprocess
import sys
import tempfile
import os

labs_bp = Blueprint('labs', __name__)

def execute_python_code(code, test_input=''):
    """
    Safely execute Python code with resource limits
    """
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute with timeout and capture output
            result = subprocess.run(
                [sys.executable, temp_file],
                input=test_input,
                capture_output=True,
                text=True,
                timeout=5,  # 5 second timeout
                check=False
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Execution timed out (5 second limit)',
            'return_code': -1
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'return_code': -1
        }

def run_test_cases(code, test_cases):
    """
    Run code against multiple test cases
    """
    results = []
    all_passed = True
    
    for i, test_case in enumerate(test_cases):
        test_input = test_case.get('input', '')
        expected_output = test_case.get('expected_output', '').strip()
        description = test_case.get('description', f'Test {i+1}')
        
        execution_result = execute_python_code(code, test_input)
        
        if execution_result['success']:
            actual_output = execution_result['output'].strip()
            passed = actual_output == expected_output
            
            results.append({
                'description': description,
                'passed': passed,
                'expected': expected_output,
                'actual': actual_output,
                'error': None
            })
            
            if not passed:
                all_passed = False
        else:
            results.append({
                'description': description,
                'passed': False,
                'expected': expected_output,
                'actual': None,
                'error': execution_result['error']
            })
            all_passed = False
    
    return all_passed, results

@labs_bp.route('/<int:lab_id>', methods=['GET'])
@jwt_required()
def get_lab(lab_id):
    try:
        current_user_id = get_jwt_identity()
        lab = Lab.query.get(lab_id)
        
        if not lab:
            return jsonify({'error': 'Lab not found'}), 404
        
        # Check if user has completed this lab
        submission = LabSubmission.query.filter_by(
            user_id=current_user_id,
            lab_id=lab_id,
            passed=True
        ).first()
        
        # Check number of attempts
        attempts = LabSubmission.query.filter_by(
            user_id=current_user_id,
            lab_id=lab_id
        ).count()
        
        lab_data = lab.to_dict(include_solution=(attempts >= 3 or submission is not None))
        lab_data['completed'] = submission is not None
        lab_data['attempts'] = attempts
        
        return jsonify({'lab': lab_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@labs_bp.route('/<int:lab_id>/execute', methods=['POST'])
@jwt_required()
def execute_lab_code(lab_id):
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({'error': 'Code is required'}), 400
        
        code = data['code']
        test_input = data.get('input', '')
        
        # Execute the code
        result = execute_python_code(code, test_input)
        
        return jsonify({
            'execution_result': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@labs_bp.route('/<int:lab_id>/submit', methods=['POST'])
@jwt_required()
def submit_lab(lab_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({'error': 'Code is required'}), 400
        
        lab = Lab.query.get(lab_id)
        if not lab:
            return jsonify({'error': 'Lab not found'}), 404
        
        code = data['code']
        test_cases = json.loads(lab.test_cases) if lab.test_cases else []
        
        # Run test cases
        all_passed, test_results = run_test_cases(code, test_cases)
        
        # Save submission
        submission = LabSubmission(
            user_id=current_user_id,
            lab_id=lab_id,
            code=code,
            passed=all_passed,
            test_results=json.dumps(test_results),
            submitted_at=datetime.utcnow()
        )
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({
            'message': 'Lab submitted successfully',
            'passed': all_passed,
            'test_results': test_results,
            'submission_id': submission.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@labs_bp.route('/<int:lab_id>/submissions', methods=['GET'])
@jwt_required()
def get_lab_submissions(lab_id):
    try:
        current_user_id = get_jwt_identity()
        
        submissions = LabSubmission.query.filter_by(
            user_id=current_user_id,
            lab_id=lab_id
        ).order_by(LabSubmission.submitted_at.desc()).all()
        
        return jsonify({
            'submissions': [submission.to_dict() for submission in submissions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@labs_bp.route('/<int:lab_id>/hints', methods=['GET'])
@jwt_required()
def get_lab_hints(lab_id):
    try:
        lab = Lab.query.get(lab_id)
        
        if not lab:
            return jsonify({'error': 'Lab not found'}), 404
        
        hints = json.loads(lab.hints) if lab.hints else []
        
        return jsonify({'hints': hints}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

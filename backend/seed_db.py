"""
Database seeding script
Run this after migrations to populate initial sample data
"""
import sys
import os
from app import app, db
from models import Module, Lesson, Quiz, Question, Lab
import json

def seed_database():
    """Seed the database with initial sample data"""
    
    with app.app_context():
        # Check if data already exists
        if Module.query.first():
            print("Database already contains data. Skipping seed.")
            return
        
        print("Seeding database with sample data...")
        
        # Create Module 1: Python Fundamentals
        module1 = Module(
            title='Python Fundamentals',
            description='Learn the basics of Python programming including variables, data types, and basic operations.',
            order_index=1,
            is_published=True,
            day_start=1,
            day_end=5
        )
        db.session.add(module1)
        db.session.flush()  # Get the ID
        
        # Create Lesson 1
        lesson1 = Lesson(
            module_id=module1.id,
            title='Introduction to Python',
            content='''# Welcome to Python Programming!

## What is Python?

Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum in 1991, Python has become one of the most popular programming languages in the world.

## Why Learn Python?

- **Easy to Learn**: Python's syntax is clear and intuitive, making it perfect for beginners
- **Versatile**: Used in web development, data science, AI, automation, and more
- **Large Community**: Extensive libraries and active community support
- **Career Opportunities**: High demand for Python developers across industries

## Your First Python Program

Let's write the classic "Hello, World!" program:

```python
print("Hello, World!")
```

This simple line of code displays text on the screen. The `print()` function is one of Python's built-in functions that outputs information.

## Variables and Basic Data Types

Variables store data that your program can use:

```python
# String (text)
name = "Alice"

# Integer (whole number)
age = 25

# Float (decimal number)
height = 5.6

# Boolean (True/False)
is_student = True

print(f"My name is {name} and I am {age} years old.")
```

## Key Takeaways

- Python is beginner-friendly and powerful
- `print()` displays output
- Variables store different types of data
- Python uses indentation for code structure

In the next lesson, we'll explore more data types and operations!''',
            order_index=1,
            estimated_time=45,
            is_published=True
        )
        db.session.add(lesson1)
        db.session.flush()
        
        # Create Lab 1
        lab1 = Lab(
            lesson_id=lesson1.id,
            title='Your First Python Program',
            description='Create a program that displays your name, age, and favorite programming language.',
            starter_code='''# Write your code here
# Use print() to display:
# 1. Your name
# 2. Your age
# 3. Your favorite programming language

''',
            solution_code='''# Solution
name = "Student"
age = 20
favorite_language = "Python"

print(f"My name is {name}")
print(f"I am {age} years old")
print(f"My favorite language is {favorite_language}")''',
            test_cases=json.dumps([
                {
                    "description": "Test basic output",
                    "input": "",
                    "expected_output": "My name is Student\nI am 20 years old\nMy favorite language is Python"
                }
            ]),
            difficulty='beginner',
            hints=json.dumps([
                "Start by creating variables for name, age, and language",
                "Use print() function to display each variable",
                "Try using f-strings for formatting: print(f'Text {variable}')"
            ])
        )
        db.session.add(lab1)
        
        # Create Quiz 1
        quiz1 = Quiz(
            module_id=module1.id,
            title='Python Fundamentals Quiz',
            passing_score=70,
            time_limit=30
        )
        db.session.add(quiz1)
        db.session.flush()
        
        # Create Questions
        questions = [
            Question(
                quiz_id=quiz1.id,
                question_text='What is the correct way to print "Hello" in Python?',
                question_type='multiple_choice',
                options=json.dumps(['echo("Hello")', 'print("Hello")', 'console.log("Hello")', 'printf("Hello")']),
                correct_answer='print("Hello")',
                explanation='The print() function is used to output text in Python. echo() is for shell scripts, console.log() is for JavaScript, and printf() is for C.'
            ),
            Question(
                quiz_id=quiz1.id,
                question_text='Which of the following is a valid Python variable name?',
                question_type='multiple_choice',
                options=json.dumps(['2nd_value', 'my-variable', 'my_variable', 'my variable']),
                correct_answer='my_variable',
                explanation='Python variable names must start with a letter or underscore, and can contain letters, numbers, and underscores. They cannot contain spaces or hyphens.'
            ),
            Question(
                quiz_id=quiz1.id,
                question_text='Python is a case-sensitive language.',
                question_type='true_false',
                options=json.dumps(['True', 'False']),
                correct_answer='True',
                explanation='Python is case-sensitive, meaning "variable" and "Variable" are treated as different identifiers.'
            ),
            Question(
                quiz_id=quiz1.id,
                question_text='What data type is the value True?',
                question_type='multiple_choice',
                options=json.dumps(['String', 'Integer', 'Boolean', 'Float']),
                correct_answer='Boolean',
                explanation='True and False are Boolean values in Python, representing logical states.'
            )
        ]
        
        for question in questions:
            db.session.add(question)
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   - Created {Module.query.count()} module(s)")
        print(f"   - Created {Lesson.query.count()} lesson(s)")
        print(f"   - Created {Lab.query.count()} lab(s)")
        print(f"   - Created {Quiz.query.count()} quiz(zes)")
        print(f"   - Created {Question.query.count()} question(s)")

if __name__ == '__main__':
    try:
        seed_database()
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        sys.exit(1)

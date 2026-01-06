-- This file is run automatically when the database container starts
-- It creates initial sample data for the platform

-- Note: Tables are created by Flask-Migrate, so we only insert data here

-- Sample Module 1: Python Fundamentals (Days 1-5)
INSERT INTO modules (title, description, order_index, is_published, day_start, day_end) 
VALUES (
    'Python Fundamentals',
    'Learn the basics of Python programming including variables, data types, and basic operations.',
    1,
    true,
    1,
    5
);

-- Sample Lesson for Module 1
INSERT INTO lessons (module_id, title, content, order_index, estimated_time, is_published)
VALUES (
    1,
    'Introduction to Python',
    '# Welcome to Python Programming!

## What is Python?

Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum in 1991, Python has become one of the most popular programming languages in the world.

## Why Learn Python?

- **Easy to Learn**: Python''s syntax is clear and intuitive, making it perfect for beginners
- **Versatile**: Used in web development, data science, AI, automation, and more
- **Large Community**: Extensive libraries and active community support
- **Career Opportunities**: High demand for Python developers across industries

## Your First Python Program

Let''s write the classic "Hello, World!" program:

```python
print("Hello, World!")
```

This simple line of code displays text on the screen. The `print()` function is one of Python''s built-in functions that outputs information.

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

In the next lesson, we''ll explore more data types and operations!',
    1,
    45,
    true
);

-- Sample Lab for the lesson
INSERT INTO labs (lesson_id, title, description, starter_code, solution_code, test_cases, difficulty, hints)
VALUES (
    1,
    'Your First Python Program',
    'Create a program that displays your name, age, and favorite programming language.',
    '# Write your code here
# Use print() to display:
# 1. Your name
# 2. Your age
# 3. Your favorite programming language

',
    '# Solution
name = "Student"
age = 20
favorite_language = "Python"

print(f"My name is {name}")
print(f"I am {age} years old")
print(f"My favorite language is {favorite_language}")',
    '[
        {
            "description": "Test basic output",
            "input": "",
            "expected_output": "My name is Student\nI am 20 years old\nMy favorite language is Python"
        }
    ]',
    'beginner',
    '["Start by creating variables for name, age, and language", "Use print() function to display each variable", "Try using f-strings for formatting: print(f\"Text {variable}\")"]'
);

-- Sample Quiz for Module 1
INSERT INTO quizzes (module_id, title, passing_score, time_limit)
VALUES (1, 'Python Fundamentals Quiz', 70, 30);

-- Sample Questions
INSERT INTO questions (quiz_id, question_text, question_type, options, correct_answer, explanation)
VALUES 
(
    1,
    'What is the correct way to print "Hello" in Python?',
    'multiple_choice',
    '["echo(\"Hello\")", "print(\"Hello\")", "console.log(\"Hello\")", "printf(\"Hello\")"]',
    'print("Hello")',
    'The print() function is used to output text in Python. echo() is for shell scripts, console.log() is for JavaScript, and printf() is for C.'
),
(
    1,
    'Which of the following is a valid Python variable name?',
    'multiple_choice',
    '["2nd_value", "my-variable", "my_variable", "my variable"]',
    'my_variable',
    'Python variable names must start with a letter or underscore, and can contain letters, numbers, and underscores. They cannot contain spaces or hyphens.'
),
(
    1,
    'Python is a case-sensitive language.',
    'true_false',
    '["True", "False"]',
    'True',
    'Python is case-sensitive, meaning "variable" and "Variable" are treated as different identifiers.'
),
(
    1,
    'What data type is the value True?',
    'multiple_choice',
    '["String", "Integer", "Boolean", "Float"]',
    'Boolean',
    'True and False are Boolean values in Python, representing logical states.'
);

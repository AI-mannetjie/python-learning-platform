# Quick Start Guide - Python Learning Platform

## Installation (5 Minutes)

### Step 1: Prerequisites
- Install Docker: https://docs.docker.com/get-docker/
- Install Docker Compose: https://docs.docker.com/compose/install/

### Step 2: Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd python-learning-platform

# Run the setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Check for Docker and Docker Compose
- Create secure environment variables
- Build and start all services
- Initialize the database
- Run migrations

### Step 3: Access the Application
Open your browser and go to: **http://localhost**

### Step 4: Create an Account
1. Click "Register"
2. Enter your details
3. Start learning Python!

## Manual Setup (Alternative)

If the setup script doesn't work:

```bash
# 1. Create environment file
cp .env.example .env
nano .env  # Update passwords and keys

# 2. Build and start
docker-compose up -d --build

# 3. Run migrations
docker-compose exec backend flask db upgrade
```

## First Steps

1. **Register**: Create your account
2. **Dashboard**: View all 12 modules
3. **Module 1**: Start with Python Fundamentals
4. **Lesson 1**: Read "Introduction to Python"
5. **Lab 1**: Complete your first coding exercise
6. **Quiz**: Test your knowledge

## Curriculum Overview

**60-Day Journey:**
- Days 1-10: Foundation (Variables, Control Flow)
- Days 11-20: Intermediate (Functions, Data Structures)
- Days 21-30: Advanced Basics (OOP, Error Handling)
- Days 31-40: Practical Skills (APIs, Databases)
- Days 41-50: Frameworks (Flask/Django basics)
- Days 51-60: Capstone Projects

## Key Features

✅ **Interactive Code Editor**: Write and run Python code in your browser
✅ **Automated Testing**: Get instant feedback on your labs
✅ **Progress Tracking**: See your completion percentage
✅ **Quizzes**: Test your knowledge with multiple choice questions
✅ **Projects**: Build real applications

## Support

**Issues?**
- Check logs: `docker-compose logs -f`
- Restart: `docker-compose restart`
- Stop: `docker-compose down`

**Documentation:** See full README.md for detailed information

**Happy Learning!** 🚀🐍

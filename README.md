# Python Learning Platform - Master Python in 60 Days

A comprehensive web-based learning platform that teaches Python programming from beginner to proficient level in 60 days through structured lessons, interactive labs, and quizzes.

## Features

- **Structured 60-Day Curriculum**: 12 modules with progressive difficulty
- **Interactive Code Editor**: Built-in Monaco Editor (VS Code's editor) for writing and testing Python code
- **Automated Testing**: Labs with automated test cases and immediate feedback
- **Quiz System**: Multiple choice, true/false, and code output prediction questions
- **Progress Tracking**: Dashboard showing completion percentage, quiz scores, and streaks
- **Secure Code Execution**: Sandboxed Python execution environment
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Technology Stack

### Backend
- Flask 3.0 (Python web framework)
- PostgreSQL 14 (Database)
- SQLAlchemy (ORM)
- Flask-JWT-Extended (Authentication)
- Gunicorn (WSGI server)

### Frontend
- React 18 (UI framework)
- React Router v6 (Navigation)
- Monaco Editor (Code editor)
- Axios (HTTP client)
- React Markdown (Content rendering)

### DevOps
- Docker & Docker Compose
- Nginx (Reverse proxy)

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd python-learning-platform
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and update the values (especially passwords and secret keys)
nano .env
```

**Important**: Change the default passwords and secret keys in production!

### 3. Start the Application

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Initialize the Database

```bash
# Run migrations
docker-compose exec backend flask db upgrade

# The database will be automatically initialized with sample data
```

### 5. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api
- **Health Check**: http://localhost/api/health

### 6. Create Admin User (Optional)

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U admin -d python_learning

# Update a user to be admin
UPDATE users SET is_admin = true WHERE email = 'your-email@example.com';
\q
```

## Project Structure

```
python-learning-platform/
├── backend/                 # Flask backend
│   ├── routes/             # API endpoints
│   │   ├── auth.py        # Authentication
│   │   ├── modules.py     # Module management
│   │   ├── lessons.py     # Lesson management
│   │   ├── quizzes.py     # Quiz system
│   │   ├── labs.py        # Lab system with code execution
│   │   ├── progress.py    # Progress tracking
│   │   └── admin.py       # Admin endpoints
│   ├── app.py             # Main Flask application
│   ├── models.py          # Database models
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Backend Docker image
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js        # Main React application
│   │   ├── App.css       # Styling
│   │   ├── index.js      # Entry point
│   │   └── index.css     # Base styles
│   ├── public/
│   │   └── index.html    # HTML template
│   ├── package.json      # Node dependencies
│   └── Dockerfile        # Frontend Docker image
├── nginx/                 # Nginx configuration
│   ├── nginx.conf        # Main Nginx config
│   └── default.conf      # Server configuration
├── database/             # Database initialization
│   └── init.sql         # Sample data
├── docker-compose.yml    # Docker orchestration
└── .env.example         # Environment variables template
```

## Usage

### For Students

1. **Register**: Create an account at http://localhost/register
2. **Dashboard**: View all modules and your progress
3. **Learn**: Click on a module to see lessons
4. **Practice**: Complete labs with instant feedback
5. **Test**: Take quizzes to assess your knowledge
6. **Track**: Monitor your progress on the dashboard

### For Admins

Admins can create and manage content through the API:

```bash
# Example: Create a new module
curl -X POST http://localhost/api/admin/modules \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Python",
    "description": "Advanced Python concepts",
    "order_index": 2,
    "is_published": true,
    "day_start": 11,
    "day_end": 15
  }'
```

## API Documentation

### Authentication Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/me` - Update profile

### Module Endpoints

- `GET /api/modules` - List all modules
- `GET /api/modules/:id` - Get module details
- `GET /api/modules/:id/lessons` - Get module lessons

### Lesson Endpoints

- `GET /api/lessons/:id` - Get lesson content
- `POST /api/lessons/:id/complete` - Mark lesson complete

### Quiz Endpoints

- `GET /api/quizzes/:id` - Get quiz
- `POST /api/quizzes/:id/submit` - Submit quiz answers
- `GET /api/quizzes/:id/attempts` - Get quiz attempts

### Lab Endpoints

- `GET /api/labs/:id` - Get lab details
- `POST /api/labs/:id/execute` - Execute code
- `POST /api/labs/:id/submit` - Submit lab solution
- `GET /api/labs/:id/hints` - Get hints

### Progress Endpoints

- `GET /api/progress` - Get user progress
- `GET /api/progress/dashboard` - Get dashboard data

### Admin Endpoints

- `POST /api/admin/modules` - Create module
- `POST /api/admin/lessons` - Create lesson
- `POST /api/admin/quizzes` - Create quiz
- `POST /api/admin/questions` - Create question
- `POST /api/admin/labs` - Create lab
- `GET /api/admin/users` - List users

## Development

### Running in Development Mode

```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_ENV=development
flask run

# Frontend development
cd frontend
npm install
npm start
```

### Database Migrations

```bash
# Create a new migration
docker-compose exec backend flask db migrate -m "Description"

# Apply migrations
docker-compose exec backend flask db upgrade

# Rollback
docker-compose exec backend flask db downgrade
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

## Deployment

### Production Checklist

- [ ] Update all passwords and secret keys in `.env`
- [ ] Set `FLASK_ENV=production`
- [ ] Use strong `SECRET_KEY` and `JWT_SECRET_KEY` (32+ characters)
- [ ] Configure HTTPS with SSL certificates
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Update `REACT_APP_API_URL` to production domain
- [ ] Review CORS settings
- [ ] Set up firewall rules

### Deploying to Cloud

The application is containerized and can be deployed to:
- AWS (EC2, ECS, or Lightsail)
- Google Cloud Platform (GCE or Cloud Run)
- DigitalOcean (Droplets or App Platform)
- Azure (Container Instances or App Service)
- Heroku
- Any VPS with Docker support

### Example Deployment to DigitalOcean

```bash
# 1. Create a droplet with Docker
# 2. SSH into the droplet
ssh root@your-server-ip

# 3. Clone repository
git clone <your-repo-url>
cd python-learning-platform

# 4. Configure environment
cp .env.example .env
nano .env  # Update values

# 5. Start services
docker-compose up -d

# 6. Set up domain and SSL (optional)
# Install certbot and obtain SSL certificate
```

## Troubleshooting

### Backend won't start

```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Rebuild if needed
docker-compose up -d --build backend
```

### Database connection errors

```bash
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Frontend not loading

```bash
# Check nginx logs
docker-compose logs nginx

# Check frontend build
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

### Code execution not working

- Ensure the backend container has Python installed
- Check backend logs for execution errors
- Verify file permissions in the container

## Security Considerations

1. **Code Execution**: Code runs in a subprocess with timeout and resource limits
2. **SQL Injection**: Using SQLAlchemy ORM with parameterized queries
3. **XSS Prevention**: React automatically escapes output
4. **Authentication**: JWT tokens with expiration
5. **CORS**: Configured for specific origins
6. **Input Validation**: Server-side validation on all endpoints

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Email: support@yourplatform.com
- Documentation: [Full documentation link]

## Roadmap

- [ ] Add video lessons
- [ ] Implement discussion forums
- [ ] Add real-time collaboration
- [ ] Mobile apps (iOS/Android)
- [ ] AI-powered code review
- [ ] Certificate generation
- [ ] Multiple language support
- [ ] Advanced analytics dashboard
- [ ] Integration with GitHub

## Credits

- Built with React, Flask, and PostgreSQL
- Code editor powered by Monaco Editor
- Markdown rendering by react-markdown
- Syntax highlighting by react-syntax-highlighter

---

**Start your Python journey today!** 🚀🐍

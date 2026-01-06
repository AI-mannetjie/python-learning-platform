import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './App.css';

// API Configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth Context
const AuthContext = createContext(null);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data.user);
    } catch (error) {
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    localStorage.setItem('token', response.data.access_token);
    setUser(response.data.user);
    return response.data;
  };

  const register = async (email, password, fullName) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    localStorage.setItem('token', response.data.access_token);
    setUser(response.data.user);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return user ? children : <Navigate to="/login" />;
};

// Login Page
const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <h1>Python Mastery in 60 Days</h1>
        <h2>Login</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Login</button>
        </form>
        <p>
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
};

// Register Page
const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await register(email, password, fullName);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <h1>Python Mastery in 60 Days</h1>
        <h2>Register</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Full Name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password (min 8 characters)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
          <button type="submit">Register</button>
        </form>
        <p>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
};

// Dashboard Page
const Dashboard = () => {
  const [modules, setModules] = useState([]);
  const [progress, setProgress] = useState(null);
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [modulesRes, progressRes] = await Promise.all([
        api.get('/modules'),
        api.get('/progress'),
      ]);
      setModules(modulesRes.data.modules);
      setProgress(progressRes.data.progress);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard">
      <nav className="navbar">
        <h1>Python Learning Platform</h1>
        <div className="nav-right">
          <span>Welcome, {user?.full_name}</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="progress-summary">
          <h2>Your Progress</h2>
          {progress && (
            <div className="stats-grid">
              <div className="stat-card">
                <h3>{progress.overall_completion}%</h3>
                <p>Overall Completion</p>
              </div>
              <div className="stat-card">
                <h3>{progress.completed_lessons}/{progress.total_lessons}</h3>
                <p>Lessons Completed</p>
              </div>
              <div className="stat-card">
                <h3>{progress.average_quiz_score}%</h3>
                <p>Average Quiz Score</p>
              </div>
              <div className="stat-card">
                <h3>{progress.passed_labs}</h3>
                <p>Labs Passed</p>
              </div>
            </div>
          )}
        </div>

        <div className="modules-section">
          <h2>Course Modules</h2>
          <div className="modules-grid">
            {modules.map((module) => (
              <div key={module.id} className="module-card">
                <h3>{module.title}</h3>
                <p>{module.description}</p>
                <p className="module-days">
                  Days {module.day_start}-{module.day_end}
                </p>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${module.completion_percentage}%` }}
                  />
                </div>
                <p className="progress-text">
                  {module.completed_lessons}/{module.total_lessons} lessons completed
                </p>
                <button onClick={() => navigate(`/module/${module.id}`)}>
                  View Module
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Module Page
const ModulePage = () => {
  const { moduleId } = useParams();
  const [module, setModule] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchModule();
  }, [moduleId]);

  const fetchModule = async () => {
    try {
      const response = await api.get(`/modules/${moduleId}`);
      setModule(response.data.module);
    } catch (error) {
      console.error('Failed to fetch module:', error);
    }
  };

  if (!module) return <div className="loading">Loading...</div>;

  return (
    <div className="module-page">
      <nav className="navbar">
        <h1>Python Learning Platform</h1>
        <button onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
      </nav>

      <div className="module-content">
        <h2>{module.title}</h2>
        <p className="module-description">{module.description}</p>

        <div className="lessons-list">
          <h3>Lessons</h3>
          {module.lessons.map((lesson) => (
            <div
              key={lesson.id}
              className={`lesson-item ${lesson.completed ? 'completed' : ''}`}
              onClick={() => navigate(`/lesson/${lesson.id}`)}
            >
              <div className="lesson-info">
                <h4>{lesson.title}</h4>
                <span className="lesson-time">{lesson.estimated_time} min</span>
              </div>
              {lesson.completed && <span className="checkmark">✓</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Lesson Page
const LessonPage = () => {
  const { lessonId } = useParams();
  const [lesson, setLesson] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLesson();
  }, [lessonId]);

  const fetchLesson = async () => {
    try {
      const response = await api.get(`/lessons/${lessonId}`);
      setLesson(response.data.lesson);
    } catch (error) {
      console.error('Failed to fetch lesson:', error);
    }
  };

  const handleComplete = async () => {
    try {
      await api.post(`/lessons/${lessonId}/complete`);
      if (lesson.next_lesson_id) {
        navigate(`/lesson/${lesson.next_lesson_id}`);
      } else {
        navigate(`/module/${lesson.module_id}`);
      }
    } catch (error) {
      console.error('Failed to mark lesson as complete:', error);
    }
  };

  if (!lesson) return <div className="loading">Loading...</div>;

  return (
    <div className="lesson-page">
      <nav className="navbar">
        <h1>Python Learning Platform</h1>
        <button onClick={() => navigate(`/module/${lesson.module_id}`)}>
          Back to Module
        </button>
      </nav>

      <div className="lesson-content">
        <h2>{lesson.title}</h2>
        <div className="markdown-content">
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={tomorrow}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {lesson.content}
          </ReactMarkdown>
        </div>

        {lesson.labs && lesson.labs.length > 0 && (
          <div className="lesson-labs">
            <h3>Practice Labs</h3>
            {lesson.labs.map((lab) => (
              <button
                key={lab.id}
                onClick={() => navigate(`/lab/${lab.id}`)}
                className="lab-button"
              >
                {lab.title}
              </button>
            ))}
          </div>
        )}

        <div className="lesson-navigation">
          {lesson.prev_lesson_id && (
            <button onClick={() => navigate(`/lesson/${lesson.prev_lesson_id}`)}>
              Previous Lesson
            </button>
          )}
          <button onClick={handleComplete} className="complete-button">
            {lesson.completed ? 'Completed ✓' : 'Mark as Complete'}
          </button>
          {lesson.next_lesson_id && (
            <button onClick={() => navigate(`/lesson/${lesson.next_lesson_id}`)}>
              Next Lesson
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// Lab Page
const LabPage = () => {
  const { labId } = useParams();
  const [lab, setLab] = useState(null);
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [testResults, setTestResults] = useState(null);
  const [showHints, setShowHints] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLab();
  }, [labId]);

  const fetchLab = async () => {
    try {
      const response = await api.get(`/labs/${labId}`);
      setLab(response.data.lab);
      setCode(response.data.lab.starter_code || '');
    } catch (error) {
      console.error('Failed to fetch lab:', error);
    }
  };

  const handleRunCode = async () => {
    try {
      const response = await api.post(`/labs/${labId}/execute`, { code });
      const result = response.data.execution_result;
      setOutput(result.success ? result.output : result.error);
    } catch (error) {
      setOutput('Failed to execute code');
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await api.post(`/labs/${labId}/submit`, { code });
      setTestResults(response.data);
      if (response.data.passed) {
        alert('Congratulations! All tests passed!');
        navigate(`/lesson/${lab.lesson_id}`);
      }
    } catch (error) {
      alert('Failed to submit lab');
    }
  };

  if (!lab) return <div className="loading">Loading...</div>;

  return (
    <div className="lab-page">
      <nav className="navbar">
        <h1>Python Learning Platform</h1>
        <button onClick={() => navigate(`/lesson/${lab.lesson_id}`)}>
          Back to Lesson
        </button>
      </nav>

      <div className="lab-content">
        <div className="lab-info">
          <h2>{lab.title}</h2>
          <p>{lab.description}</p>
          <button onClick={() => setShowHints(!showHints)}>
            {showHints ? 'Hide Hints' : 'Show Hints'}
          </button>
          {showHints && lab.hints && (
            <div className="hints">
              {lab.hints.map((hint, index) => (
                <p key={index}>💡 {hint}</p>
              ))}
            </div>
          )}
        </div>

        <div className="editor-section">
          <h3>Code Editor</h3>
          <Editor
            height="400px"
            defaultLanguage="python"
            value={code}
            onChange={(value) => setCode(value || '')}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
            }}
          />
        </div>

        <div className="lab-actions">
          <button onClick={handleRunCode}>Run Code</button>
          <button onClick={handleSubmit} className="submit-button">
            Submit Solution
          </button>
        </div>

        {output && (
          <div className="output-section">
            <h3>Output</h3>
            <pre>{output}</pre>
          </div>
        )}

        {testResults && (
          <div className="test-results">
            <h3>Test Results</h3>
            <p className={testResults.passed ? 'passed' : 'failed'}>
              {testResults.passed
                ? '✓ All tests passed!'
                : '✗ Some tests failed'}
            </p>
            {testResults.test_results.map((result, index) => (
              <div key={index} className="test-case">
                <p>
                  {result.passed ? '✓' : '✗'} {result.description}
                </p>
                {!result.passed && (
                  <div>
                    <p>Expected: {result.expected}</p>
                    <p>Got: {result.actual || result.error}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/module/:moduleId"
            element={
              <ProtectedRoute>
                <ModulePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/lesson/:lessonId"
            element={
              <ProtectedRoute>
                <LessonPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/lab/:labId"
            element={
              <ProtectedRoute>
                <LabPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

# Troubleshooting Guide

## Common Setup Issues and Solutions

### Issue 1: npm ci fails - "can only install with existing package-lock.json"

**Error:**
```
npm error The `npm ci` command can only install with an existing package-lock.json
```

**Solution:**
Already fixed in the latest version. The Dockerfile now uses `npm install` instead of `npm ci`.

If you're using an old version:
```bash
# Edit frontend/Dockerfile
# Change line 10 from:
RUN npm ci
# To:
RUN npm install
```

---

### Issue 2: Frontend build fails - "COPY failed: no source files were specified"

**Error:**
```
COPY failed: no source files were specified
```

**Solution:**
This happens if the directory structure is incorrect. Run the fix script:
```bash
./fix-directories.sh
```

Or manually check:
```bash
ls -la frontend/
# Should show: Dockerfile, package.json, public/, src/
# Should NOT show: {public,src or other weird names
```

---

### Issue 3: Backend fails to start - "Connection refused" to database

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
The database container might not be ready yet.

```bash
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Wait for database to be ready, then restart backend
docker-compose restart backend
```

---

### Issue 4: "Port already in use" error

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use
```

**Solution:**
Another service is using port 80, 5000, or 5432.

```bash
# Check what's using the ports
sudo lsof -i :80
sudo lsof -i :5000
sudo lsof -i :5432

# Option 1: Stop the conflicting service
# Option 2: Change ports in docker-compose.yml
# For example, change:
#   ports:
#     - "8080:80"  # Use 8080 instead of 80
```

---

### Issue 5: Permission denied when running setup.sh

**Error:**
```
bash: ./setup.sh: Permission denied
```

**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

---

### Issue 6: Database migrations fail

**Error:**
```
alembic.util.exc.CommandError: Can't locate revision identified by...
```

**Solution:**
```bash
# Initialize migrations from scratch
docker-compose exec backend flask db init
docker-compose exec backend flask db migrate -m "Initial migration"
docker-compose exec backend flask db upgrade
```

---

### Issue 7: Frontend shows blank page or 404

**Symptoms:**
- Blank white page
- Browser console shows 404 errors
- "Cannot GET /api/..." errors

**Solution:**

Check if all services are running:
```bash
docker-compose ps
# All services should show "Up"
```

Check nginx logs:
```bash
docker-compose logs nginx
```

Check if backend is accessible:
```bash
curl http://localhost/api/health
# Should return: {"status":"healthy",...}
```

If backend is not responding:
```bash
docker-compose logs backend
docker-compose restart backend
```

---

### Issue 8: CORS errors in browser console

**Error:**
```
Access to XMLHttpRequest at 'http://localhost/api/...' from origin 'http://localhost' 
has been blocked by CORS policy
```

**Solution:**
This should not happen with the default configuration, but if it does:

1. Check backend/app.py CORS settings
2. Check nginx/default.conf for CORS headers
3. Clear browser cache and reload

---

### Issue 9: Code execution timeout

**Symptoms:**
- Lab code runs indefinitely
- "Execution timed out" errors

**Solution:**
This is expected behavior for infinite loops or very slow code. The timeout is set to 5 seconds for security.

To adjust:
```python
# In backend/routes/labs.py, line ~14
result = subprocess.run(
    [sys.executable, temp_file],
    timeout=10,  # Change from 5 to 10 seconds
    ...
)
```

---

### Issue 10: "ModuleNotFoundError" in backend

**Error:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
Dependencies weren't installed properly.

```bash
# Rebuild backend container
docker-compose up -d --build backend

# Or manually install in container
docker-compose exec backend pip install -r requirements.txt
```

---

## General Debugging Commands

### View all logs
```bash
docker-compose logs -f
```

### View specific service logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
docker-compose logs -f nginx
```

### Check service status
```bash
docker-compose ps
```

### Restart a specific service
```bash
docker-compose restart backend
docker-compose restart frontend
docker-compose restart nginx
```

### Rebuild and restart everything
```bash
docker-compose down
docker-compose up -d --build
```

### Access container shell
```bash
# Backend
docker-compose exec backend /bin/bash

# Database
docker-compose exec db psql -U admin -d python_learning

# Frontend (during build)
docker-compose run frontend sh
```

### Clean start (removes all data!)
```bash
docker-compose down -v  # -v removes volumes (DATABASE WILL BE DELETED!)
docker-compose up -d --build
```

---

## Verification Checklist

After setup, verify everything works:

- [ ] All containers running: `docker-compose ps`
- [ ] Backend health check: `curl http://localhost/api/health`
- [ ] Frontend loads: Open http://localhost in browser
- [ ] Can register: Create a new account
- [ ] Can login: Login with new account
- [ ] Dashboard loads: See modules on dashboard
- [ ] Can view lesson: Click on a module and lesson
- [ ] Code editor works: Try running code in a lab
- [ ] No console errors: Check browser developer console

---

## Getting Help

If you're still stuck:

1. **Check logs**: `docker-compose logs -f`
2. **Check this guide**: Review the issue that matches your error
3. **Check Docker**: Ensure Docker and Docker Compose are up to date
4. **Check ports**: Make sure ports 80, 5000, 5432 are available
5. **Check resources**: Ensure enough disk space and memory

### System Requirements
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB free disk space
- Ports 80, 5000, 5432 available

---

## Clean Reinstall

If all else fails, do a clean reinstall:

```bash
# Stop and remove everything
docker-compose down -v

# Remove all Docker images for this project
docker rmi python-learning-platform_backend
docker rmi python-learning-platform_frontend

# Delete the directory
cd ..
rm -rf python-learning-platform

# Extract fresh copy from zip
unzip python-learning-platform.zip
cd python-learning-platform

# Run setup
./setup.sh
```

---

**Still having issues?** Check the main README.md for additional information or review the deployment checklist.

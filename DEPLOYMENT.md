# 🚀 LLP Incorporation Automation API - Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Current Status
- ✅ Core Flask API functionality working
- ✅ All dependencies specified in requirements.txt  
- ✅ Thread-safe task management
- ✅ Proper error handling and logging
- ✅ Swagger UI documentation
- ✅ CORS configuration for frontend
- ✅ UI properly connected to API endpoint

### ⚠️ Production Updates Made
- ✅ Environment-based configuration
- ✅ Debug mode configurable
- ✅ Production server configurations (Gunicorn/Waitress)
- ✅ Deployment scripts created

## 🔧 Deployment Options

### Option 1: Quick Development Deployment
```bash
# Set environment variables
export FLASK_DEBUG=false
export FLASK_HOST=0.0.0.0
export FLASK_PORT=8009

# Run with Flask dev server
python api_main.py
```

### Option 2: Production Deployment with Waitress (Recommended for Windows)
```bash
# Windows
deploy.bat

# Or manually:
pip install -r requirements.txt
playwright install
waitress-serve --host=0.0.0.0 --port=8009 api_main:app
```

### Option 3: Production Deployment with Gunicorn (Linux/Mac)
```bash
# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Or manually:
pip install -r requirements.txt  
playwright install
gunicorn --config gunicorn_config.py api_main:app
```

## 🌐 Access Points

After deployment, your API will be available at:
- **Root Info**: `http://65.0.202.146:8009/`
- **API Info**: `http://65.0.202.146:8009/api`
- **Documentation**: `http://65.0.202.146:8009/api/docs`
- **Main Endpoint**: `POST http://65.0.202.146:8009/api/automate`
- **Status Check**: `GET http://65.0.202.146:8009/api/status/{task_id}`

## 🔐 Security Configuration

### Environment Variables
1. Copy `config.template` to `.env`
2. Update with your actual values:
   - TrueCaptcha credentials
   - Secret keys
   - Database URLs (if needed)

### Production Security (Recommended)
- [ ] Add authentication middleware
- [ ] Implement rate limiting
- [ ] Restrict CORS origins
- [ ] Add input validation
- [ ] Use HTTPS in production
- [ ] Set up reverse proxy (nginx/Apache)

## 📊 Monitoring & Logging

### Logs Location
- Application logs: `logs/app.log`
- Server logs: Console output

### Health Check
```bash
curl -X GET http://65.0.202.146:8009/
```

## 🐛 Troubleshooting

### Common Issues
1. **Port Already in Use**: Change `FLASK_PORT` in environment
2. **Permission Denied**: Run with appropriate user permissions
3. **Browser Automation Issues**: Ensure Playwright browsers are installed
4. **Memory Issues**: Adjust Gunicorn worker count

### Debug Mode
```bash
export FLASK_DEBUG=true
python api_main.py
```

## 🔄 Updates & Maintenance

### Updating the Application
```bash
git pull origin main
pip install -r requirements.txt
playwright install
# Restart the server
```

### Backup Important Files
- `config_data.json`
- `.env` file
- `static/swagger.json`
- Any custom configurations

## 📈 Performance Optimization

### For High Traffic
- Use more Gunicorn workers
- Implement Redis for task queue
- Set up load balancer
- Use database instead of in-memory task storage

### Resource Management
- Monitor memory usage
- Set up log rotation
- Clean up temporary files

## 🎯 Final Deployment Command

**For immediate deployment on Windows:**
```bash
deploy.bat
```

**For Linux/Mac:**
```bash
chmod +x deploy.sh && ./deploy.sh
```

Your LLP Automation API is now production-ready! 🎉 
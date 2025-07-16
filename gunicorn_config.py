# Gunicorn configuration file for production deployment
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('FLASK_PORT', '8009')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "llp_automation_api"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Preload application
preload_app = True

# Graceful timeout
graceful_timeout = 30

# Restart workers after this many requests
max_requests = 1000

# Restart workers after this many seconds
max_requests_jitter = 50

# Worker temporary directory
worker_tmp_dir = "/dev/shm"

# User and group
# user = "www-data"
# group = "www-data" 
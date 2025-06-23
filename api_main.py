# api_main.py
from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import json
from automation_worker import AutomationWorker
import threading
import os
import time
import logging

# Configure logging to be more informative
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s',
    handlers=[
        logging.StreamHandler() # Outputs logs to the console
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for all routes, allowing frontend to communicate with the API
# Added 'file://' to allow opening index.html directly from the filesystem for testing
CORS(app, resources={r"/api/*": {"origins": "*"}})


# --- Swagger API Documentation Setup ---
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json' # The path to the swagger.json file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "LLP Incorporation Automation API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Store automation task status in a thread-safe way
running_tasks = {}
tasks_lock = threading.Lock()

def run_automation_task(task_id, config_json):
    """
    This function runs the automation in a separate thread to prevent
    the API from freezing.
    """
    logger.info(f"Automation task {task_id} started.")
    try:
        worker = AutomationWorker()
        
        with tasks_lock:
            running_tasks[task_id] = {"status": "initializing", "message": "Browser setup..."}
        
        # Initialize browser and load configuration
        if not worker.initialize_browser(config_json.get('firefox_profile_path')):
            raise Exception("Failed to initialize browser.")
            
        if not worker.load_config(json.dumps(config_json)):
             raise Exception("Failed to load configuration.")

        with tasks_lock:
            running_tasks[task_id] = {"status": "running", "message": "Automation in progress..."}
        
        # Execute the main automation logic
        result = worker.execute_automation()
        
        with tasks_lock:
            running_tasks[task_id] = result # Store the final result

        logger.info(f"Automation task {task_id} finished with status: {result.get('status')}")

    except Exception as e:
        error_message = f"An error occurred in task {task_id}: {str(e)}"
        logger.error(error_message, exc_info=True)
        with tasks_lock:
            running_tasks[task_id] = {"status": "error", "message": error_message}
    finally:
        # Ensure the browser is always cleaned up
        if 'worker' in locals() and worker.driver:
            worker.cleanup()
            logger.info(f"Browser for task {task_id} has been cleaned up.")

@app.route('/api/automate', methods=['POST'])
def start_automation():
    """
    API endpoint to receive form data and start the automation process.
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Invalid request: Content-Type must be application/json"}), 400

    try:
        data = request.get_json()
        
        # --- THIS IS THE KEY DEBUGGING ADDITION ---
        # Log the received data structure to the console to easily debug mismatches.
        logger.info("----- Received Automation Request -----")
        logger.info(json.dumps(data, indent=2))
        logger.info("------------------------------------")
        
        config_data = data.get('config_data')
        if not config_data:
            return jsonify({"status": "error", "message": "Missing 'config_data' in request body"}), 400

        task_id = str(int(time.time()))
        
        with tasks_lock:
            running_tasks[task_id] = {"status": "pending", "message": "Task is queued for execution."}

        # Start the automation in a background thread
        thread = threading.Thread(target=run_automation_task, args=(task_id, config_data), name=f"Task-{task_id}")
        thread.start()

        logger.info(f"Dispatched task {task_id} to a background thread.")
        return jsonify({"status": "success", "message": "Automation process started.", "task_id": task_id}), 202

    except Exception as e:
        logger.error(f"Error in /api/automate endpoint: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """
    API endpoint to check the status of a running automation task.
    """
    with tasks_lock:
        task = running_tasks.get(task_id)
        if not task:
            return jsonify({"status": "error", "message": "Task not found"}), 404
        return jsonify(task)

if __name__ == '__main__':
    # Ensure the static directory exists for swagger.json
    if not os.path.exists('static'):
        os.makedirs('static')
    # Note: For production, use a proper WSGI server like Gunicorn or Waitress instead of app.run()
    logger.info("Starting Flask API server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

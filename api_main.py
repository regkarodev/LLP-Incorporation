# api_main.py
from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import json
from automation_worker import AutomationWorker
import threading
import os
import time
import logging
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Swagger configuration
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

# Configure Swagger UI
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "LLP Incorporation Automation API",
        'displayRequestDuration': True,
        'docExpansion': 'list'
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Create static directory if it doesn't exist
os.makedirs('static', exist_ok=True)

# Create swagger.json with detailed documentation
swagger_config = {
    "swagger": "2.0",
    "info": {
        "title": "LLP Incorporation Automation API",
        "description": "API for automating LLP incorporation form filling process",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "email": "support@example.com"
        }
    },
    "basePath": "/",
    "schemes": ["http"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "paths": {
        "/api/automate": {
            "post": {
                "summary": "Start Automation Process",
                "description": "Initiates the LLP incorporation automation with the provided configuration",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["config_data"],
                            "properties": {
                                "config_data": {
                                    "type": "object",
                                    "required": ["firefox_profile_path", "fillip_url", "user_email", "user_password", "form_data"],
                                    "properties": {
                                        "firefox_profile_path": {"type": "string"},
                                        "fillip_url": {"type": "string"},
                                        "user_email": {"type": "string"},
                                        "user_password": {"type": "string"},
                                        "form_data": {
                                            "type": "object",
                                            "properties": {
                                                "file_paths": {
                                                    "type": "object",
                                                    "properties": {
                                                        "first_file": {"type": "string"},
                                                        "second_file": {"type": "string"},
                                                        "third_file": {"type": "string"},
                                                        "fourth_file": {"type": "string"}
                                                    }
                                                },
                                                "fields": {
                                                    "type": "object",
                                                    "properties": {
                                                        "Service Request Number": {"type": "string"},
                                                        "Address Line I": {"type": "string"},
                                                        "Address Line II": {"type": "string"},
                                                        "PIN CODE": {"type": "string"},
                                                        "Area/Locality1": {"type": "string"},
                                                        "Longitude": {"type": "string"},
                                                        "Latitude": {"type": "string"},
                                                        "Jurisdiction of Police Station": {"type": "string"},
                                                        "Phone (with STD/ISD code)": {"type": "string"},
                                                        "Mobile No": {"type": "string"},
                                                        "Fax": {"type": "string"},
                                                        "Email ID": {"type": "string"},
                                                        "Name of the office of Registrar": {"type": "string"},
                                                        "Individuals Having valid DIN/DPIN": {"type": "string"},
                                                        "Individuals Not having valid DIN/DPIN": {"type": "string"},
                                                        "Body corporates and their nominees Having valid DIN/DPIN": {"type": "string"},
                                                        "Body corporates and their nominee not having valid DIN/DPIN": {"type": "string"},
                                                        "Individuals Having valid DIN/DPIN1": {"type": "string"},
                                                        "Individuals Not having valid DIN/DPIN1": {"type": "string"},
                                                        "Body corporates and their nominees Having valid DIN/DPIN1": {"type": "string"},
                                                        "Body corporates and their nominee not having valid DIN/DPIN1": {"type": "string"},
                                                        "PAN Area code": {"type": "string"},
                                                        "PAN Area code1": {"type": "string"},
                                                        "PAN Area code2": {"type": "string"},
                                                        "PAN AO type": {"type": "string"},
                                                        "PAN AO type1": {"type": "string"},
                                                        "PAN Range code": {"type": "string"},
                                                        "PAN Range code1": {"type": "string"},
                                                        "PAN Range code2": {"type": "string"},
                                                        "PAN AO No.": {"type": "string"},
                                                        "PAN AO No1": {"type": "string"},
                                                        "PAN AO No2": {"type": "string"},
                                                        "PAN AO No3": {"type": "string"},
                                                        "TAN Area code1": {"type": "string"},
                                                        "TAN Area code2": {"type": "string"},
                                                        "TAN Area code3": {"type": "string"},
                                                        "TAN AO type1": {"type": "string"},
                                                        "TAN AO type2": {"type": "string"},
                                                        "TAN Range code": {"type": "string"},
                                                        "TAN Range code1": {"type": "string"},
                                                        "TAN Range code2": {"type": "string"},
                                                        "TAN AO No": {"type": "string"},
                                                        "TAN AO No1": {"type": "string"},
                                                        "TAN AO No2": {"type": "string"},
                                                        "TAN AO No3": {"type": "string"},
                                                        "Income Source": {"type": "string"},
                                                        "DIN/DPIN/PAN of designated partner": {"type": "string"},
                                                        "Enter Name": {"type": "string"},
                                                        "Enter Father's Name": {"type": "string"},
                                                        "partnership and my membership number": {"type": "string"}
                                                    }
                                                },
                                                "dynamic_form_index": {
                                                    "type": "object",
                                                    "properties": {
                                                        "individuals_having_valid_din_dpin": {"type": "string"},
                                                        "individuals_not_having_valid_din_dpin": {"type": "string"},
                                                        "body_corporates_and_their_nominees_having_valid_din_dpin": {"type": "string"},
                                                        "body_corporates_and_their_nominee_not_having_valid_din_dpin": {"type": "string"}
                                                    }
                                                },
                                                "designated_partners": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "Designated partner identification number (DIN/DPIN)": {"type": "string"},
                                                            "Form of contribution": {"type": "string"},
                                                            "If 'Other than cash' selected, please specify": {"type": "string"},
                                                            "Monetary value of contribution (in INR) (in figures)": {"type": "string"},
                                                            "Number of LLP(s) in which he/ she is a partner": {"type": "string"},
                                                            "Number of company(s) in which he/ she is a director": {"type": "string"}
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "partners_without_din": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "First Name": {"type": "string"},
                                                    "Middle Name": {"type": "string"},
                                                    "Surname": {"type": "string"},
                                                    "Father's First Name": {"type": "string"},
                                                    "Father's Middle Name": {"type": "string"},
                                                    "Father's Surname": {"type": "string"},
                                                    "Gender": {"type": "string"},
                                                    "Date of Birth": {"type": "string"},
                                                    "Nationality": {"type": "string"},
                                                    "Whether resident of India": {
                                                        "type": "object",
                                                        "properties": {
                                                            "Yes": {"type": "boolean"},
                                                            "No": {"type": "boolean"}
                                                        }
                                                    },
                                                    "Income-tax PAN/Passport number": {
                                                        "type": "object",
                                                        "properties": {
                                                            "PAN": {"type": "boolean"},
                                                            "Passport number": {"type": "boolean"}
                                                        }
                                                    },
                                                    "Income-tax PAN/Passport number details": {"type": "string"},
                                                    "Place of Birth (State)": {"type": "string"},
                                                    "Place of Birth (District)": {"type": "string"},
                                                    "Whether citizen of India": {
                                                        "type": "object",
                                                        "properties": {
                                                            "Yes": {"type": "boolean"},
                                                            "No": {"type": "boolean"}
                                                        }
                                                    },
                                                    "Occupation type": {"type": "string"},
                                                    "Area of Occupation": {"type": "string"},
                                                    "Educational qualification": {"type": "string"},
                                                    "Mobile No.": {"type": "string"},
                                                    "Email ID": {"type": "string"},
                                                    "Permanent Address Line I": {"type": "string"},
                                                    "Permanent Address Line II": {"type": "string"},
                                                    "Permanent Country": {"type": "string"},
                                                    "Permanent Pin code": {"type": "string"},
                                                    "Permanent Area/Locality": {"type": "string"},
                                                    "Permanent Police Station": {"type": "string"},
                                                    "Permanent Phone": {"type": "string"},
                                                    "Whether present residential address same as permanent": {
                                                        "type": "object",
                                                        "properties": {
                                                            "Yes": {"type": "boolean"},
                                                            "No": {"type": "boolean"}
                                                        }
                                                    },
                                                    "Present Address Line I": {"type": "string"},
                                                    "Present Address Line II": {"type": "string"},
                                                    "Present Country": {"type": "string"},
                                                    "Present Pin code": {"type": "string"},
                                                    "Present Area/Locality": {"type": "string"},
                                                    "Present Phone": {"type": "string"},
                                                    "Present Jurisdiction": {"type": "string"},
                                                    "Duration Years": {"type": "string"},
                                                    "Duration Months": {"type": "string"},
                                                    "Identity Proof": {"type": "string"},
                                                    "Residential Proof": {"type": "string"},
                                                    "Identity Proof No.": {"type": "string"},
                                                    "Residential Proof No.": {"type": "string"},
                                                    "Proof of identity": {"type": "string"},
                                                    "Residential proof": {"type": "string"},
                                                    "Form of contribution": {"type": "string"},
                                                    "Monetary value": {"type": "string"},
                                                    "Number of LLPs": {"type": "string"},
                                                    "Number of companies": {"type": "string"}
                                                }
                                            }
                                        },
                                        "bodies_corporate_with_din": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "Type of body corporate": {"type": "string"},
                                                    "CIN/FCRN": {"type": "string"},
                                                    "PAN": {"type": "string"},
                                                    "Name of the body corporate": {"type": "string"},
                                                    "Address Line I": {"type": "string"},
                                                    "Address Line II": {"type": "string"},
                                                    "Country": {"type": "string"},
                                                    "Pin code": {"type": "string"},
                                                    "Area/ Locality": {"type": "string"},
                                                    "Jurisdiction of Police Station": {"type": "string"},
                                                    "Phone (with STD/ISD code)": {"type": "string"},
                                                    "Mobile No": {"type": "string"},
                                                    "Fax": {"type": "string"},
                                                    "Email ID": {"type": "string"},
                                                    "Form of contribution": {"type": "string"},
                                                    "Monetary value of contribution (in INR) (in figures)": {"type": "string"},
                                                    "Number of LLP(s) in which it is a partner": {"type": "string"},
                                                    "Number of company(s) in which it is a director": {"type": "string"},
                                                    "DIN/DPIN": {"type": "string"},
                                                    "Name": {"type": "string"},
                                                    "Whether resident of India": {
                                                        "type": "object",
                                                        "properties": {
                                                            "Yes": {"type": "boolean"},
                                                            "No": {"type": "boolean"}
                                                        }
                                                    },
                                                    "Designation and Authority in body corporate": {"type": "string"},
                                                    "Copy of resolution": {"type": "string"}
                                                }
                                            }
                                        },
                                        "bodies_corporate_nominee_no_din": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "corporate_details": {
                                                        "type": "object",
                                                        "properties": {
                                                            "type": {"type": "string"},
                                                            "registration_number": {"type": "string"},
                                                            "pan": {"type": "string"},
                                                            "name": {"type": "string"},
                                                            "address": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "line1": {"type": "string"},
                                                                    "line2": {"type": "string"},
                                                                    "country": {"type": "string"},
                                                                    "pincode": {"type": "string"},
                                                                    "area": {"type": "string"},
                                                                    "jurisdiction": {"type": "string"}
                                                                }
                                                            },
                                                            "contact": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "phone": {"type": "string"},
                                                                    "mobile": {"type": "string"},
                                                                    "fax": {"type": "string"},
                                                                    "email": {"type": "string"}
                                                                }
                                                            },
                                                            "conversion": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "shares_held": {"type": "string"},
                                                                    "share_value": {"type": "string"}
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "contribution": {
                                                        "type": "object",
                                                        "properties": {
                                                            "form": {"type": "string"},
                                                            "other_specify": {"type": "string"},
                                                            "value_figures": {"type": "string"},
                                                            "llp_count": {"type": "string"},
                                                            "company_count": {"type": "string"}
                                                        }
                                                    },
                                                    "nominee": {
                                                        "type": "object",
                                                        "properties": {
                                                            "first_name": {"type": "string"},
                                                            "middle_name": {"type": "string"},
                                                            "surname": {"type": "string"},
                                                            "father_first": {"type": "string"},
                                                            "father_middle": {"type": "string"},
                                                            "father_surname": {"type": "string"},
                                                            "gender": {"type": "string"},
                                                            "dob": {"type": "string"},
                                                            "nationality": {"type": "string"},
                                                            "resident": {"type": "string"},
                                                            "PAN/Passport number": {"type": "string"},
                                                            "pan/passport": {"type": "string"},
                                                            "birth_state": {"type": "string"},
                                                            "birth_district": {"type": "string"},
                                                            "citizen": {"type": "string"},
                                                            "occupation_type": {"type": "string"},
                                                            "occupation_other": {"type": "string"},
                                                            "Area of Occupation": {"type": "string"},
                                                            "If 'Others' selected, please specify": {"type": "string"},
                                                            "education": {"type": "string"},
                                                            "education_other": {"type": "string"},
                                                            "mobile": {"type": "string"},
                                                            "email": {"type": "string"}
                                                        }
                                                    },
                                                    "permanent_address": {
                                                        "type": "object",
                                                        "properties": {
                                                            "line1": {"type": "string"},
                                                            "line2": {"type": "string"},
                                                            "country": {"type": "string"},
                                                            "pincode": {"type": "string"},
                                                            "area": {"type": "string"},
                                                            "jurisdiction": {"type": "string"},
                                                            "phone": {"type": "string"}
                                                        }
                                                    },
                                                    "present_same": {
                                                        "type": "object",
                                                        "properties": {
                                                            "Yes": {"type": "boolean"},
                                                            "No": {"type": "boolean"}
                                                        }
                                                    },
                                                    "present_address": {
                                                        "type": "object",
                                                        "properties": {
                                                            "line1": {"type": "string"},
                                                            "line2": {"type": "string"},
                                                            "country": {"type": "string"},
                                                            "pincode": {"type": "string"},
                                                            "area": {"type": "string"},
                                                            "jurisdiction": {"type": "string"},
                                                            "phone": {"type": "string"}
                                                        }
                                                    },
                                                    "stay_duration": {
                                                        "type": "object",
                                                        "properties": {
                                                            "years": {"type": "string"},
                                                            "months": {"type": "string"}
                                                        }
                                                    },
                                                    "identity_proof": {
                                                        "type": "object",
                                                        "properties": {
                                                            "type": {"type": "string"},
                                                            "number": {"type": "string"}
                                                        }
                                                    },
                                                    "residential_proof": {
                                                        "type": "object",
                                                        "properties": {
                                                            "type": {"type": "string"},
                                                            "number": {"type": "string"}
                                                        }
                                                    },
                                                    "uploads": {
                                                        "type": "object",
                                                        "properties": {
                                                            "identity_proof_path": {"type": "string"},
                                                            "residential_proof_path": {"type": "string"},
                                                            "resolution_copy_path": {"type": "string"}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Automation started successfully",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"},
                                "task_id": {"type": "string"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid input or missing required fields"
                    },
                    "500": {
                        "description": "Internal server error"
                    }
                }
            }
        },
        "/api/status/{task_id}": {
            "get": {
                "summary": "Get Automation Status",
                "description": "Retrieve the current status of an automation task",
                "parameters": [
                    {
                        "name": "task_id",
                        "in": "path",
                        "required": True,
                        "type": "string",
                        "description": "ID of the automation task"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Task status retrieved successfully",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "message": {"type": "string"},
                                "progress": {"type": "number"},
                                "details": {"type": "object"}
                            }
                        }
                    },
                    "404": {
                        "description": "Task not found"
                    }
                }
            }
        }
    }
}

# Save swagger.json
with open('static/swagger.json', 'w') as f:
    json.dump(swagger_config, f, indent=2)

# Store running tasks and a lock for thread-safe access
running_tasks = {}
tasks_lock = threading.Lock()

def run_automation_task(task_id, config_json):
    """Run automation in a separate thread"""
    try:
        worker = AutomationWorker()
        
        # Update task status
        with tasks_lock:
            running_tasks[task_id] = {
                "status": "initializing",
                "message": "Setting up automation...",
                "progress": 0
            }

        # Initialize browser
        if not worker.initialize_browser(config_json.get('firefox_profile_path')):
            with tasks_lock:
                running_tasks[task_id] = {
                    "status": "error",
                    "message": "Failed to initialize browser",
                    "progress": 0
                }
            return

        # Load config
        try:
            config_json_str = json.dumps(config_json)
        except TypeError as e:
            with tasks_lock:
                running_tasks[task_id] = {
                    "status": "error",
                    "message": f"Invalid configuration format: {str(e)}",
                    "progress": 0
                }
            worker.cleanup()
            return

        if not worker.load_config(config_json_str):
            with tasks_lock:
                running_tasks[task_id] = {
                    "status": "error",
                    "message": "Failed to load configuration",
                    "progress": 0
                }
            worker.cleanup()
            return

        # Execute automation
        with tasks_lock:
            running_tasks[task_id]["status"] = "running"
            running_tasks[task_id]["message"] = "Automation in progress..."
            running_tasks[task_id]["progress"] = 10

        result = worker.execute_automation()
        
        with tasks_lock:
            running_tasks[task_id] = {
                "status": result["status"],
                "message": result["message"],
                "progress": 100,
                "details": result.get("details", {})
            }

    except Exception as e:
        logger.error(f"Error in automation task {task_id}: {str(e)}", exc_info=True)
        with tasks_lock:
            running_tasks[task_id] = {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "progress": 0
            }
    finally:
        if 'worker' in locals():
            worker.cleanup()

@app.route('/api/automate', methods=['POST'])
def start_automation():
    """Start automation with provided configuration"""
    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 400

        try:
            data = request.get_json()
        except Exception as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Invalid JSON format in request body"
            }), 400

        if not data or 'config_data' not in data:
            return jsonify({
                "status": "error",
                "message": "No configuration data provided"
            }), 400

        config_to_use = data['config_data']
        
        # Validate required fields
        required_fields = ['firefox_profile_path', 'fillip_url']
        missing_fields = [field for field in required_fields if field not in config_to_use]
        if missing_fields:
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Generate task ID
        task_id = str(int(time.time()))
        logger.info(f"Starting automation task {task_id}")

        # Initialize task status
        with tasks_lock:
            running_tasks[task_id] = {
                "status": "pending",
                "message": "Task received and initializing...",
                "progress": 0
            }

        # Start automation in a separate thread
        thread = threading.Thread(
            target=run_automation_task,
            args=(task_id, config_to_use)
        )
        thread.start()

        return jsonify({
            "status": "success",
            "message": "Automation started successfully",
            "task_id": task_id
        })

    except Exception as e:
        logger.error(f"Error in start_automation: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """Get status of an automation task"""
    with tasks_lock:
        if task_id not in running_tasks:
            return jsonify({
                "status": "error",
                "message": "Task not found"
            }), 404
        
        return jsonify(running_tasks[task_id])

if __name__ == '__main__':
    logger.info("Starting API server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
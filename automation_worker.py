# automation_worker.py
import os
import time
import json
import logging
import tempfile
import shutil
import base64
import zipfile
import main
import automate1
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomationWorker:
    def __init__(self):
        self.driver = None
        self.config_data = None
        self.temp_profile_dir = None
        self.wait_timeout = 30  # Default wait timeout in seconds

    def initialize_browser(self, firefox_profile_path):
        """Initialize the Firefox browser with the specified profile"""
        try:
            options = FirefoxOptions()
            options.add_argument("--start-maximized")
            
            # Handle both string path and base64 encoded profile data
            if isinstance(firefox_profile_path, str):
                if os.path.exists(firefox_profile_path):
                    logger.info(f"Using existing profile at: {firefox_profile_path}")
                    options.profile = FirefoxProfile(firefox_profile_path)
                else:
                    try:
                        logger.info("Processing base64 encoded profile data")
                        profile_data = base64.b64decode(firefox_profile_path)
                        self.temp_profile_dir = tempfile.mkdtemp()
                        
                        # Save the decoded data to a temporary file
                        profile_file = os.path.join(self.temp_profile_dir, 'profile.zip')
                        with open(profile_file, 'wb') as f:
                            f.write(profile_data)
                        
                        # Extract the profile
                        with zipfile.ZipFile(profile_file, 'r') as zip_ref:
                            zip_ref.extractall(self.temp_profile_dir)
                        
                        # Use the extracted profile
                        options.profile = FirefoxProfile(self.temp_profile_dir)
                        logger.info(f"Created temporary profile at: {self.temp_profile_dir}")
                    except Exception as e:
                        logger.error(f"Failed to process profile data: {str(e)}")
                        return False
            
            self.driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options
            )
            logger.info("Browser initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            return False

    def load_config(self, config_json):
        """Load configuration from JSON string"""
        try:
            self.config_data = json.loads(config_json)
            logger.info("Configuration loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return False

    def save_config_to_file(self):
        """Save the current config to config_data.json"""
        try:
            with open("config_data.json", "w") as f:
                json.dump(self.config_data, f, indent=2)
            logger.info("Configuration saved to config_data.json")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            return False

    def execute_automation(self):
        """Execute the automation sequence"""
        try:
            if not self.driver or not self.config_data:
                return {
                    "status": "error",
                    "message": "Browser or config not initialized",
                    "details": {}
                }

            # Save config to file for main.py to use
            if not self.save_config_to_file():
                return {
                    "status": "error",
                    "message": "Failed to save config file",
                    "details": {}
                }

            # Execute main.py workflow which handles login and automation
            logger.info("Starting main workflow...")
            # Pass the existing driver to main.py
            main.perform_login(driver=self.driver, close_after_login=False)

            # After login, run the automation sequence
            if self.driver:
                # Initialize automate1 with our driver
                automate1.setup_driver(self.driver)
                success = automate1.run_llp_form_sequence(self.driver)
                
                if success:
                    logger.info("Automation completed successfully")
                    return {
                        "status": "success",
                        "message": "Automation completed successfully",
                        "details": {
                            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    }
                else:
                    logger.error("Automation failed during form sequence execution")
                    return {
                        "status": "error",
                        "message": "Automation failed during form sequence execution",
                        "details": {
                            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    }
            else:
                return {
                    "status": "error",
                    "message": "Browser session lost after login",
                    "details": {}
                }

        except Exception as e:
            logger.error(f"Unexpected error during automation: {str(e)}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "details": {}
            }

    def cleanup(self):
        """Clean up resources by quitting the browser and removing temporary files."""
        if self.driver:
            try:
                logger.info("Quitting browser...")
                self.driver.quit()
                self.driver = None
                logger.info("Browser quit successfully")
            except Exception as e:
                logger.error(f"Error during browser cleanup: {str(e)}")
        
        # Clean up temporary profile directory if it exists
        if self.temp_profile_dir and os.path.exists(self.temp_profile_dir):
            try:
                shutil.rmtree(self.temp_profile_dir)
                logger.info("Temporary profile directory cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up temporary profile directory: {str(e)}")

if __name__ == "__main__":
    worker = AutomationWorker()
    try:
        # Load configuration
        with open("config_data.json", "r") as f:
            config = json.load(f)
        
        # Initialize browser
        if worker.initialize_browser(config.get("firefox_profile_path")):
            # Load config
            worker.load_config(json.dumps(config))
            
            # Execute automation
            result = worker.execute_automation()
            print(f"Automation result: {result}")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
    finally:
        worker.cleanup()
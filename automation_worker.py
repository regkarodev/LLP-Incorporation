# automation_worker.py

import os
import json
import time
import logging

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Import the necessary modules it will call
import main
import automate1 

# Configure logging for this module
logger = logging.getLogger(__name__)

class AutomationWorker:
    """
    A class to orchestrate the automation process by delegating tasks.
    It initializes the browser and then calls other scripts to perform login and form-filling.
    """
    def __init__(self):
        """Initializes the worker's state."""
        self.driver = None
        self.config_data = None

    def initialize_browser(self, firefox_profile_path):
        """
        Initializes a Firefox browser instance using a direct profile path.
        """
        try:
            logger.info(f"Initializing browser with profile: {firefox_profile_path}")
            
            if not isinstance(firefox_profile_path, str) or not os.path.exists(firefox_profile_path):
                logger.error(f"Invalid or non-existent profile path: '{firefox_profile_path}'.")
                return False

            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("-profile")
            options.add_argument(firefox_profile_path)
            
            logger.info("Installing/updating geckodriver...")
            service = Service(GeckoDriverManager().install())
            
            self.driver = webdriver.Firefox(service=service, options=options)
            logger.info("Browser initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}", exc_info=True)
            return False

    def load_config(self, config_json_str):
        """
        Loads configuration from a JSON string.
        This corrected version assumes the string is the config object itself,
        not a wrapper object.
        """
        try:
            # **THE FIX**: Directly parse the incoming string as the config data.
            self.config_data = json.loads(config_json_str)
            
            # Validate that the necessary keys exist in the loaded config.
            if "form_data" not in self.config_data:
                 raise ValueError("Loaded config is missing the 'form_data' key.")
            logger.info("Configuration loaded successfully.")
            return True
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to load or validate config: {e}")
            return False

    def save_config_to_file(self):
        """
        Saves the received configuration to 'config_data.json' so that
        the external main.py script can read it.
        """
        try:
            with open("config_data.json", "w") as f:
                # We save the content of self.config_data, not the whole object
                json.dump(self.config_data, f, indent=4)
            logger.info("Configuration saved to config_data.json for main.py to use.")
            return True
        except Exception as e:
            logger.error(f"Failed to save config to file: {e}", exc_info=True)
            return False

    def execute_automation(self):
        """
        Executes the automation by calling external scripts for login and form-filling.
        """
        try:
            if not self.driver or not self.config_data:
                return {"status": "error", "message": "Browser or config not initialized."}

            # Step 1: Save the config to a file for main.py to access
            if not self.save_config_to_file():
                return {"status": "error", "message": "Could not write config file for sub-process."}

            # Step 2: Delegate login to main.py's perform_login function
            logger.info("Delegating login task to main.perform_login...")
            driver, login_success = main.perform_login(driver=self.driver, close_after_login=False)

            if not login_success:
                logger.error("main.py reported a login failure.")
                return {"status": "error", "message": "Login failed as per main.py execution."}
            
            # Update driver instance, as main.py might have changed it
            self.driver = driver
            logger.info("Login successful. Navigating to the Fillip form URL.")

            # Step 3: Navigate to the form and execute the form-filling sequence
            # fillip_url = self.config_data.get("fillip_url")
            # self.driver.get(fillip_url)
            
            logger.info("Handing off to automate1.py to fill the form.")
            automate1.setup_driver(self.driver)
            form_data = self.config_data.get("form_data", {})

            success = automate1.run_llp_form_sequence()
            
            if success:
                logger.info("Automation sequence completed successfully.")
                return {"status": "success", "message": "LLP form automation completed."}
            else:
                logger.error("The form filling sequence in automate1.py reported an error.")
                return {"status": "error", "message": "An error occurred during form filling."}

        except Exception as e:
            logger.critical(f"A critical error occurred during automation execution: {e}", exc_info=True)
            return {"status": "error", "message": f"Critical error: {e}"}

    def cleanup(self):
        """Closes the browser."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully.")
            except Exception as e:
                logger.error(f"Error during browser cleanup: {e}")
        self.driver = None


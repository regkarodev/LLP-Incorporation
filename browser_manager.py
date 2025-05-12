from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from logger import Logger
import os
import psutil
import time

class BrowserManager:
    def __init__(self, profile_path):
        """Initialize browser manager with profile settings"""
        self.profile_path = profile_path
        self.driver = None
        self.wait = None
        self.logger = Logger()
        
    def kill_firefox_processes(self):
        """Kill any existing Firefox processes"""
        try:
            for proc in psutil.process_iter(['name']):
                if 'firefox' in proc.info['name'].lower():
                    proc.kill()
            time.sleep(2)  # Wait for processes to be killed
        except Exception as e:
            self.logger.log(f"Error killing Firefox processes: {str(e)}", "warning")
        
    def start_browser(self):
        """Start Firefox with dedicated profile that preserves sessions"""
        try:
            self.logger.log("\n=== Starting Firefox with Persistent Profile ===")
            self.logger.log(f"Using Firefox profile at: {self.profile_path}")
            
            # Kill any existing Firefox processes
            self.kill_firefox_processes()
            
            # Verify profile directory exists
            if not os.path.exists(self.profile_path):
                self.logger.log(f"Firefox profile directory not found: {self.profile_path}", "error")
                return False
            
            # Initialize Firefox with the profile
            firefox_options = Options()
            firefox_options.add_argument("-profile")
            firefox_options.add_argument(self.profile_path)
            
            # Set preferences for browser behavior
            firefox_options.set_preference("dom.webnotifications.enabled", False)
            firefox_options.set_preference("app.update.enabled", False)
            firefox_options.set_preference("browser.sessionstore.resume_from_crash", False)
            firefox_options.set_preference("browser.sessionstore.max_tabs_undo", 0)
            
            # Initialize the driver with explicit wait
            self.logger.log("Initializing Firefox WebDriver...")
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            self.wait = WebDriverWait(self.driver, 20)  # 20 seconds timeout
            
            # Maximize the browser window
            self.driver.maximize_window()
            self.logger.log("Firefox started successfully with persistent profile")
            return True
            
        except Exception as e:
            self.logger.log(f"Error starting browser: {str(e)}", "error")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            return False
            
    def quit_browser(self):
        """Safely quit the browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.log("Browser closed")
            except Exception as e:
                self.logger.log(f"Error closing browser: {str(e)}", "warning")
            finally:
                self.kill_firefox_processes() 
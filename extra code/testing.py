# automation_worker.py
import os
import time
import json
import logging
import traceback
import sys
import platform
import tempfile
import shutil
import base64
import zipfile
import automate1
import function1
import partners_without_din
import bodies_corporate_with_din
import bodies_corporate_without_din
import document_upload_file
import attachment_upload

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException, NoSuchElementException, InvalidSessionIdException
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager

# Conditional import for pynput based on OS, and mock if not available
try:
    if platform.system() == "Windows":
        import win32gui
        import win32con
    from pynput.keyboard import Controller, Key
except ImportError:
    logging.warning("pynput not installed or not supported on this OS. File uploads requiring keyboard input may fail.")
    class MockKeyboard:
        def press(self, key): pass
        def release(self, key): pass
    Controller = MockKeyboard
    Key = type('Key', (object,), {'enter': None}) # Mock Key.enter

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global driver variable
driver = None

def scroll_into_view(driver_instance, element):
    """Helper function to scroll an element into view using JavaScript."""
    try:
        driver_instance.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
        return True
    except Exception as e:
        logger.error(f"Error scrolling element into view: {str(e)}")
        return False

def click_element(driver_instance, *, xpath=None, id=None, css_selector=None, class_name=None, name=None):
    """Robust function to click a web element, trying multiple strategies."""
    if not driver_instance:
        logger.error("No driver instance for click_element.")
        return False

    element = None
    strategies = {
        "xpath": xpath,
        "id": id,
        "css_selector": css_selector,
        "class_name": class_name,
        "name": name
    }

    found_by = None
    for strategy, value in strategies.items():
        if value:
            try:
                if strategy == "xpath":
                    element = WebDriverWait(driver_instance, 10).until(
                        EC.element_to_be_clickable((By.XPATH, value))
                    )
                elif strategy == "id":
                    element = WebDriverWait(driver_instance, 10).until(
                        EC.element_to_be_clickable((By.ID, value))
                    )
                elif strategy == "css_selector":
                    element = WebDriverWait(driver_instance, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, value))
                    )
                elif strategy == "class_name":
                    element = WebDriverWait(driver_instance, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, value))
                    )
                elif strategy == "name":
                    element = WebDriverWait(driver_instance, 10).until(
                        EC.element_to_be_clickable((By.NAME, value))
                    )
                found_by = strategy
                break
            except TimeoutException:
                logger.warning(f"Timeout: Element not clickable by {strategy} '{value}'.")
            except NoSuchElementException:
                logger.warning(f"No such element: Element not found by {strategy} '{value}'.")
            except Exception as e:
                logger.warning(f"An error occurred while finding element by {strategy} '{value}': {e}")
                
    if element:
        scroll_into_view(driver_instance, element)
        time.sleep(0.5) # Short pause after scroll
        try:
            element.click()
            logger.info(f"Successfully clicked element found by {found_by} '{strategies[found_by]}'.")
            return True
        except ElementClickInterceptedException:
            logger.warning(f"Click intercepted for element found by {found_by}. Trying JavaScript click.")
            try:
                driver_instance.execute_script("arguments[0].click();", element)
                logger.info("Successfully clicked element using JavaScript.")
                return True
            except Exception as js_click_e:
                logger.error(f"JavaScript click failed for element found by {found_by}: {js_click_e}")
        except Exception as e:
            logger.error(f"Failed to click element found by {found_by}: {e}")
    else:
        logger.error(f"Could not find or make clickable the element with strategies: {strategies}")
    return False

def send_text(driver_instance, *, xpath=None, id=None, css_selector=None, class_name=None, name=None, keys):
    """Robust function to send text to a web element."""
    if not driver_instance:
        logger.error("No driver instance for send_text.")
        return False

    element = None
    strategies = {
        "xpath": xpath,
        "id": id,
        "css_selector": css_selector,
        "class_name": class_name,
        "name": name
    }

    found_by = None
    for strategy, value in strategies.items():
        if value:
            try:
                if strategy == "xpath":
                    element = WebDriverWait(driver_instance, 10).until(
                        EC.presence_of_element_located((By.XPATH, value))
                    )
                elif strategy == "id":
                    element = WebDriverWait(driver_instance, 10).until(
                        EC.presence_of_element_located((By.ID, value))
                    )
                elif strategy == "css_selector":
                    element = WebDriverWait(driver_instance, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, value))
                    )
                elif strategy == "class_name":
                    element = WebDriverWait(driver_instance, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, value))
                    )
                elif strategy == "name":
                    element = WebDriverWait(driver_instance, 10).until(
                        EC.presence_of_element_located((By.NAME, value))
                    )
                found_by = strategy
                break
            except TimeoutException:
                logger.warning(f"Timeout: Element not found for text input by {strategy} '{value}'.")
            except NoSuchElementException:
                logger.warning(f"No such element: Element not found for text input by {strategy} '{value}'.")
            except Exception as e:
                logger.warning(f"An error occurred while finding text input element by {strategy} '{value}': {e}")

    if element:
        try:
            scroll_into_view(driver_instance, element)
            element.clear()
            element.send_keys(keys)
            logger.info(f"Successfully sent text '{keys}' to element found by {found_by} '{strategies[found_by]}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to send text to element found by {found_by}: {e}")
    else:
        logger.error(f"Could not find element for text input with strategies: {strategies}")
    return False

def set_date_field(driver_instance, date_field_id, your_date):
    """Sets a date input field using JavaScript for robustness."""
    try:
        logger.info(f"Starting streamlined DOB selection for ID: {date_field_id}")
        date_input = WebDriverWait(driver_instance, 10).until(
            EC.presence_of_element_located((By.ID, date_field_id))
        )

        logger.info(f"Target date: {your_date}")

        # Try to set date directly via value attribute (most reliable)
        driver_instance.execute_script(f"arguments[0].value = '{your_date}';", date_input)
        logger.info("Set date using direct input")

        # In some cases, JS might be needed to trigger events if just setting value doesn't work
        driver_instance.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_input)
        driver_instance.execute_script("arguments[0].dispatchEvent(new Event('blur'));", date_input)
        logger.info("Triggered change and blur events via JavaScript")
        
        # Optional: verify the date was set correctly
        current_value = date_input.get_attribute('value')
        if current_value == your_date:
            logger.info(f"Successfully verified date was set correctly to {current_value}")
            return True
        else:
            logger.warning(f"Date verification failed. Expected {your_date}, but found {current_value}. Attempting alternative method.")
            # Fallback to send_keys if JS direct set fails validation
            date_input.clear()
            date_input.send_keys(your_date)
            # Send an extra tab to ensure the field loses focus and triggers validation
            date_input.send_keys(Keys.TAB)
            if date_input.get_attribute('value') == your_date:
                logger.info(f"Successfully set date using send_keys as fallback.")
                return True
            else:
                logger.error(f"Failed to set date for {date_field_id} even with fallback. Current value: {date_input.get_attribute('value')}")
                return False

    except TimeoutException:
        logger.error(f"Timeout: Date input field with ID '{date_field_id}' not found.")
        return False
    except Exception as e:
        logger.error(f"An error occurred while setting date field '{date_field_id}': {e}")
        return False

def click_button(driver_instance, selector_value, selector_type="css_selector", timeout=10):
    """
    Clicks a button element identified by various selector types, with robust error handling.
    Args:
        driver_instance: The Selenium WebDriver instance.
        selector_value: The value of the selector (e.g., "#myButtonId", "//button[text()='Next']").
        selector_type: The type of selector ('id', 'css_selector', 'xpath', 'link_text', 'partial_link_text', 'name', 'tag_name', 'class_name').
        timeout: Maximum time to wait for the element to be clickable.
    Returns:
        bool: True if the button was clicked successfully, False otherwise.
    """
    try:
        by_strategy = getattr(By, selector_type.upper(), None)
        if by_strategy is None:
            logger.error(f"Invalid selector type: {selector_type}")
            return False

        button = WebDriverWait(driver_instance, timeout).until(
            EC.element_to_be_clickable((by_strategy, selector_value))
        )
        
        scroll_into_view(driver_instance, button)
        time.sleep(0.5) # Short pause after scroll

        try:
            button.click()
            logger.info(f"Successfully clicked button '{selector_value}' using .click()")
            return True
        except ElementClickInterceptedException:
            logger.warning(f"Click intercepted for '{selector_value}'. Trying JavaScript click.")
            driver_instance.execute_script("arguments[0].click();", button)
            logger.info(f"Successfully clicked button '{selector_value}' using JavaScript.")
            return True
        except Exception as e:
            logger.error(f"Error clicking button '{selector_value}': {e}. Attempting ActionChains.")
            try:
                ActionChains(driver_instance).move_to_element(button).click().perform()
                logger.info(f"Successfully clicked button '{selector_value}' using ActionChains.")
                return True
            except Exception as e_actions:
                logger.error(f"ActionChains click failed for '{selector_value}': {e_actions}. Final attempt with force click.")
                try:
                    driver_instance.execute_script("""
                        arguments[0].disabled = false;
                        arguments[0].style.pointerEvents = 'auto';
                        arguments[0].style.opacity = '1';
                        arguments[0].click();
                    """, button)
                    logger.info(f"Successfully clicked button '{selector_value}' using forced JavaScript.")
                    return True
                except Exception as e_force:
                    logger.error(f"Force click failed for '{selector_value}': {e_force}")
                    return False
    except TimeoutException:
        logger.error(f"Timeout: Button with {selector_type} '{selector_value}' not found or not clickable.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while trying to click button '{selector_value}': {e}")
    return False

def handle_file_upload(driver_instance, parent_div_id, file_path, timeout=20):
    """Handles file uploads via keyboard automation and verifies success"""
    logger.info(f"[DEBUG] Starting file upload for {parent_div_id}")
    
    try:
        # Locate the parent div
        parent_div = WebDriverWait(driver_instance, timeout).until(
            EC.presence_of_element_located((By.ID, parent_div_id))
        )
        logger.info(f"[DEBUG] Found parent div: {parent_div.get_attribute('id')}")

        # Find the attach button within the parent div
        attach_button = WebDriverWait(parent_div, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.guide-fu-attach-button"))
        )

        scroll_into_view(driver_instance, attach_button)
        time.sleep(1) # Small delay after scrolling

        attach_button.click()
        logger.info("[DEBUG] Clicked the 'Attach' button.")
        time.sleep(2) # Give time for file dialog to appear

        # Get the current window handle (main browser window)
        main_window_handle = driver_instance.current_window_handle

        # Type file path via keyboard
        normalized_path = os.path.normpath(file_path)
        keyboard = Controller()

        # Bring the browser window to front (might help with focus for pynput)
        if platform.system() == "Windows":
            try:
                hwnd = driver_instance.execute_script('return window.top.document.body.parentElement.outerText;')
                # This needs refinement to get the actual browser window handle
                # For now, relying on pynput to target the active window
                logger.info("Attempting to bring browser window to front (Windows specific).")
                # Find the window handle of the browser
                top_level_windows = []
                win32gui.EnumWindows(lambda hwnd, top_level_windows: top_level_windows.append(hwnd), top_level_windows)
                for hwnd in top_level_windows:
                    if driver_instance.title in win32gui.GetWindowText(hwnd):
                        win32gui.SetForegroundWindow(hwnd)
                        break
            except Exception as win_e:
                logger.warning(f"Could not bring window to front on Windows: {win_e}")

        logger.info(f"[DEBUG] Typing path: {normalized_path}")
        for char in normalized_path:
            keyboard.press(char)
            keyboard.release(char)
            time.sleep(0.01) # Small delay between key presses

        time.sleep(0.5)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(1) # Wait for file to be selected and dialog to close

        # Handle success dialog if it appears
        try:
            ok_button = WebDriverWait(driver_instance, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ok-button, #okSuccessModalBtn"))
            )
            ok_button.click()
            logger.info("[AGILE PRO] Clicked OK on upload success dialog.")
        except TimeoutException:
            logger.info("[INFO] No success dialog found (or it closed automatically).")
        except Exception as e:
            logger.warning(f"[WARNING] Error closing upload dialog: {e}")

        # Verify file appears in the list (important for robust automation)
        try:
            file_list = parent_div.find_element(By.CSS_SELECTOR, "ul.guide-fu-fileItemList")
            if file_list.find_elements(By.TAG_NAME, "li"):
                logger.info("[AGILE PRO] File appears in upload list. Upload successful.")
                return True
            else:
                logger.warning("[WARNING] No file found in upload list after apparent upload.")
                return False
        except NoSuchElementException:
            logger.warning("[INFO] Upload list element not found, cannot verify upload visually.")
            return True # Assume success if no list to check
        except Exception as e:
            logger.error(f"[ERROR] Error during upload verification: {e}")
            return False

    except TimeoutException:
        logger.error(f"[ERROR] Timeout during file upload for parent_div_id '{parent_div_id}'. Element not found or not interactable.")
        return False
    except Exception as e:
        logger.error(f"[ERROR] An unexpected error occurred during file upload for '{parent_div_id}': {e}")
        traceback.print_exc()
        return False

def setup_driver(browser_type="firefox", profile_path=None, headless=False):
    """Sets up and returns the Selenium WebDriver."""
    global driver
    if driver and check_driver_session():
        logger.info("Existing driver session found and is active. Reusing it.")
        return driver

    try:
        if browser_type.lower() == "firefox":
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
            try:
                from webdriver_manager.firefox import GeckoDriverManager
                service = FirefoxService(GeckoDriverManager().install())
            except ImportError:
                logger.warning("webdriver_manager not found. Please ensure geckodriver is in your PATH or provide its path.")
                service = FirefoxService(executable_path="geckodriver") # Assumes geckodriver is in PATH or current dir

            options = FirefoxOptions()
            options.add_argument("--start-maximized")
            if headless:
                options.add_argument("--headless")
            if profile_path and os.path.exists(profile_path):
                options.profile = FirefoxProfile(profile_path)
                logger.info(f"Using Firefox profile: {profile_path}")
            else:
                logger.warning(f"Firefox profile path '{profile_path}' not found or not provided. Starting with a new profile.")

            driver = webdriver.Firefox(service=service, options=options)
        elif browser_type.lower() == "chrome":
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.chrome.service import Service as ChromeDriverService
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = ChromeDriverService(ChromeDriverManager().install())
            except ImportError:
                logger.warning("webdriver_manager not found. Please ensure chromedriver is in your PATH or provide its path.")
                service = ChromeDriverService(executable_path="chromedriver") # Assumes chromedriver is in PATH or current dir

            options = ChromeOptions()
            options.add_argument("--start-maximized")
            if headless:
                options.add_argument("--headless")
            # Chrome profiles are handled differently, typically through user data directories
            # For simplicity, not implementing Chrome profile loading here directly from a path like Firefox
            driver = webdriver.Chrome(service=service, options=options)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}. Choose 'firefox' or 'chrome'.")

        driver.maximize_window()
        logger.info(f"WebDriver for {browser_type} initialized successfully.")
        return driver
    except Exception as e:
        logger.error(f"Failed to set up WebDriver: {e}")
        traceback.print_exc()
        return None

def check_driver_session():
    """Check if the driver session is still active."""
    global driver
    if not driver:
        return False
    try:
        driver.current_url
        return True
    except (WebDriverException, InvalidSessionIdException):
        return False

def perform_login(driver_instance, url, email, password):
    """Performs login on the given URL."""
    if not driver_instance:
        logger.error("No driver instance provided for login.")
        return False

    logger.info(f"Attempting to navigate to {url} for login...")
    try:
        driver_instance.get(url)
        WebDriverWait(driver_instance, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logger.info("Page loaded successfully.")
    except TimeoutException:
        logger.error(f"Timed out waiting for page to load at {url}. Check URL or network.")
        return False
    except Exception as e:
        logger.error(f"Error navigating to login page: {e}")
        return False

    try:
        # Assuming login elements are identifiable by these selectors
        email_field = WebDriverWait(driver_instance, 10).until(
            EC.presence_of_element_located((By.ID, "user_email")) # Example ID
        )
        password_field = driver_instance.find_element(By.ID, "user_password") # Example ID
        login_button = driver_instance.find_element(By.ID, "login_button") # Example ID

        email_field.send_keys(email)
        password_field.send_keys(password)
        login_button.click()

        # Wait for post-login redirection or element to appear
        WebDriverWait(driver_instance, 20).until(
            EC.url_changes(url) or EC.presence_of_element_located((By.ID, "dashboard_element")) # Example post-login element
        )
        logger.info("Login successful!")
        return True
    except Exception as e:
        logger.error(f"Login failed: {e}")
        traceback.print_exc()
        return False

def solve_captcha(driver_instance, captcha_img_element):
    """Placeholder for captcha solving. In a real scenario, this would integrate with a captcha-solving service."""
    logger.info("Attempting to solve captcha...")
    # This is a mock implementation. In a real system, you'd integrate with an API like TrueCaptcha.
    # For now, we'll just return a placeholder or raise an error.
    
    # Example of how to get screenshot and send to a service:
    # captcha_img_element.screenshot("captcha.png")
    # with open("captcha.png", "rb") as image_file:
    #     base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    # response = requests.post(
    #     "https://api.truecaptcha.com/solve",
    #     json={"user": TRUECAPTCHA_USER, "key": TRUECAPTCHA_KEY, "image": base64_image}
    # )
    # return response.json()["solution"]

    # For now, simulate manual input or bypass
    print("Please manually solve the captcha and enter the text in the console.")
    solved_captcha = input("Enter captcha text: ") # For local testing
    return solved_captcha

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

    def wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be present and visible"""
        if timeout is None:
            timeout = self.wait_timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {value}")
            return None

    def execute_automation(self):
        """Execute the automation sequence"""
        try:
            if not self.driver or not self.config_data:
                return {
                    "status": "error",
                    "message": "Browser or config not initialized",
                    "details": {}
                }

            # Save config to file for other modules to use
            if not self.save_config_to_file():
                return {
                    "status": "error",
                    "message": "Failed to save config file",
                    "details": {}
                }

            # Navigate to the form URL
            fillip_url = self.config_data.get('fillip_url', '')
            if not fillip_url:
                logger.error("'fillip_url' not found in config_data")
                return {
                    "status": "error",
                    "message": "'fillip_url' not found in config_data",
                    "details": {}
                }
            
            logger.info(f"Navigating to URL: {fillip_url}")
            self.driver.get(fillip_url)

            # Wait for page to load
            time.sleep(5)
            logger.info("Page loaded, starting automation sequence")

            # Run the form sequence
            automate1.setup_driver(self.driver)
            result = automate1.run_llp_form_sequence(self.driver)
            
            if result:
                logger.info("Automation completed successfully")
                return {
                    "status": "success",
                    "message": "Automation completed successfully",
                    "details": {
                        "url": fillip_url,
                        "company_name": self.config_data.get('company_name', ''),
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
            else:
                logger.error("Automation failed during form sequence execution")
                return {
                    "status": "error",
                    "message": "Automation failed during form sequence execution",
                    "details": {
                        "url": fillip_url,
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }

        except WebDriverException as e:
            logger.error(f"WebDriver error during automation: {str(e)}")
            return {
                "status": "error",
                "message": f"WebDriver error: {str(e)}",
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
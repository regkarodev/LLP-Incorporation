import os
import time
import traceback
import psutil
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

class MCAAutomation:
    def __init__(self):
        self.profile_path = os.path.join(os.getcwd(), "firefox_profile")
        self.driver = None
        self.login_url = "https://www.mca.gov.in/content/mca/global/en/foportal/fologin.html"
        self.target_url = "https://www.mca.gov.in/content/mca/global/en/mca/llp-e-filling/Fillip.html"
        self.credentials = {
            "email": "shagun@registerkaro.in",
            "password": "SLPL@1234"
        }
        self.wait = None

    def log_terminal_output(self, message, level="info"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level.upper()}] {message}")

    def kill_firefox_processes(self):
        try:
            for proc in psutil.process_iter(['name']):
                if 'firefox' in proc.info['name'].lower():
                    proc.kill()
            time.sleep(4)  # Increased from 2
        except Exception as e:
            self.log_terminal_output(f"Error killing Firefox processes: {str(e)}", "warning")

    def start_browser_with_profile(self):
        try:
            self.log_terminal_output("\n=== Starting Firefox with Persistent Profile ===")
            self.kill_firefox_processes()

            if not os.path.exists(self.profile_path):
                os.makedirs(self.profile_path)
                self.log_terminal_output(f"Created new profile directory at {self.profile_path}")

            firefox_options = Options()
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--disable-gpu")
            firefox_options.add_argument("--disable-extensions")
            firefox_options.add_argument("--disable-software-rasterizer")
            firefox_options.add_argument("-profile")
            firefox_options.add_argument(self.profile_path)

            firefox_options.set_preference("dom.webnotifications.enabled", False)
            firefox_options.set_preference("app.update.enabled", False)
            firefox_options.set_preference("browser.sessionstore.resume_from_crash", False)

            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            self.driver.set_page_load_timeout(30)
            self.driver.maximize_window()
            self.log_terminal_output("Firefox started successfully with persistent profile")
            return True
        except Exception as e:
            self.log_terminal_output(f"Error starting browser: {str(e)}", "error")
            self.log_terminal_output(traceback.format_exc(), "error")
            if self.driver:
                self.driver.quit()
            return False

    def is_logged_in(self):
        try:
            # Check for multiple possible indicators of successful login
            success_indicators = [
                "//a[contains(text(), 'Logout')]",
                "//a[contains(@href, 'logout')]",
                "//a[contains(text(), 'My MCA')]",
                "//div[contains(text(), 'Welcome')]",
                "//div[contains(text(), 'Dashboard')]",
                "//span[contains(text(), 'Welcome')]",
                "//div[contains(@class, 'user-info')]",
                "//div[contains(@class, 'user-profile')]",
                "//a[contains(@href, 'my-mca')]",
                "//div[contains(@class, 'dashboard')]"
            ]

            # First check if we're on the login page
            if "login" in self.driver.current_url.lower():
                self.log_terminal_output("Currently on login page")
                return False

            # Check each indicator
            for indicator in success_indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    for element in elements:
                        if element.is_displayed():
                            self.log_terminal_output(f"Found login indicator: {indicator}")
                            return True
                except:
                    continue

            # Check for specific MCA dashboard elements
            try:
                dashboard_elements = [
                    "//div[contains(@class, 'dashboard-container')]",
                    "//div[contains(@class, 'user-dashboard')]",
                    "//div[contains(@class, 'mca-dashboard')]"
                ]
                for element in dashboard_elements:
                    if self.driver.find_element(By.XPATH, element).is_displayed():
                        self.log_terminal_output(f"Found dashboard element: {element}")
                        return True
            except:
                pass

            self.log_terminal_output("No login indicators found")
            return False
        except Exception as e:
            self.log_terminal_output(f"Error checking login status: {str(e)}", "error")
            return False

    def perform_login(self):
        try:
            self.log_terminal_output("Starting automated login process...")
            self.driver.get(self.login_url)
            time.sleep(8)  # Wait for page to load completely

            # Handle optional OK popup
            try:
                self.log_terminal_output("Looking for OK button popup...")
                ok_button = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".btn"))
                )
                self.log_terminal_output("OK button found, attempting to click...")
                
                # Try multiple click methods with logging
                click_methods = [
                    ("direct click", lambda: ok_button.click()),
                    ("javascript click", lambda: self.driver.execute_script("arguments[0].click();", ok_button)),
                    ("mouse event", lambda: self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {'bubbles': true, 'cancelable': true}));", ok_button))
                ]
                
                for method_name, click_method in click_methods:
                    try:
                        self.log_terminal_output(f"Trying {method_name}...")
                        click_method()
                        self.log_terminal_output(f"{method_name} successful")
                        break
                    except Exception as e:
                        self.log_terminal_output(f"{method_name} failed: {str(e)}", "debug")
                
                time.sleep(4)
                self.log_terminal_output("OK button handling completed")
            except Exception as e:
                self.log_terminal_output(f"No OK button found or couldn't click it: {str(e)}", "warning")

            # Fill email with better verification
            try:
                self.log_terminal_output("Looking for email field...")
                email_field = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#guideContainer-rootPanel-panel_1846244155-guidetextbox___widget"))
                )
                self.log_terminal_output("Email field found, attempting to enter email...")
                
                # Clear and verify field is empty
                email_field.clear()
                if email_field.get_attribute("value"):
                    self.log_terminal_output("Warning: Email field not cleared properly", "warning")
                    email_field.clear()  # Try clearing again
                
                # Enter email with verification
                email_field.send_keys(self.credentials["email"])
                entered_email = email_field.get_attribute("value")
                if entered_email != self.credentials["email"]:
                    self.log_terminal_output(f"Warning: Email mismatch. Expected: {self.credentials['email']}, Got: {entered_email}", "warning")
                    # Try entering email again
                    email_field.clear()
                    email_field.send_keys(self.credentials["email"])
                
                self.log_terminal_output("Email entered successfully")
            except Exception as e:
                self.log_terminal_output(f"Failed to enter email: {str(e)}", "error")
                return False

            # Fill password with better verification
            try:
                self.log_terminal_output("Looking for password field...")
                password_field = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#guideContainer-rootPanel-panel_1846244155-guidepasswordbox___widget"))
                )
                self.log_terminal_output("Password field found, attempting to enter password...")
                
                # Clear and verify field is empty
                password_field.clear()
                if password_field.get_attribute("value"):
                    self.log_terminal_output("Warning: Password field not cleared properly", "warning")
                    password_field.clear()  # Try clearing again
                
                # Enter password with verification
                password_field.send_keys(self.credentials["password"])
                entered_password_length = len(password_field.get_attribute("value"))
                expected_password_length = len(self.credentials["password"])
                
                if entered_password_length != expected_password_length:
                    self.log_terminal_output(f"Warning: Password length mismatch. Expected: {expected_password_length}, Got: {entered_password_length}", "warning")
                    # Try entering password again
                    password_field.clear()
                    password_field.send_keys(self.credentials["password"])
                
                self.log_terminal_output("Password entered successfully")
            except Exception as e:
                self.log_terminal_output(f"Failed to enter password: {str(e)}", "error")
                return False

            # Wait for captcha to be solved manually with automated wait
            self.log_terminal_output("🧠 Please solve the captcha manually in the browser.")
            self.log_terminal_output("Current page state before captcha:")
            self.log_terminal_output(f"URL: {self.driver.current_url}")
            self.driver.save_screenshot("before_captcha.png")

            self.log_terminal_output("⏳ Waiting 25 seconds for captcha to be solved manually...")
            time.sleep(25)

            # Click login with better verification
            try:
                self.log_terminal_output("Looking for login button...")
                login_button = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#guideContainer-rootPanel-panel_1846244155-submit___widget"))
                )
                self.log_terminal_output("Login button found, preparing to click...")
                
                # Take screenshot before clicking
                self.driver.save_screenshot("before_login_click.png")
                
                # Try click with retries
                max_attempts = 3
                for attempt in range(1, max_attempts + 1):
                    try:
                        self.log_terminal_output(f"Clicking login button, attempt {attempt}")
                        login_button.click()
                        break
                    except Exception as e:
                        self.log_terminal_output(f"Attempt {attempt} failed to click login: {str(e)}", "warning")
                        time.sleep(1)
                else:
                    self.log_terminal_output("Failed to click login button after multiple attempts", "error")
                    return False
                
                self.log_terminal_output("Login button clicked successfully")
            except Exception as e:
                self.log_terminal_output(f"Login button not found or not clickable: {str(e)}", "error")
                return False

            # Wait for login to complete with enhanced verification
            try:
                self.log_terminal_output("Waiting for login to complete...")
                # Wait for either URL change or login indicators
                WebDriverWait(self.driver, 30).until(
                    lambda driver: (
                        "dashboard" in driver.current_url.lower() or
                        "my-mca" in driver.current_url.lower() or
                        self.is_logged_in()
                    )
                )
                
                # Additional verification after login
                if self.is_logged_in():
                    self.log_terminal_output("Login successful - verified with indicators")
                    return True
                else:
                    self.log_terminal_output("Login verification failed - no indicators found", "error")
                    return False

            except Exception as e:
                self.log_terminal_output(f"Login wait timeout or failure: {str(e)}", "error")
                return False

        except Exception as e:
            self.log_terminal_output(f"Exception during login process: {str(e)}", "error")
            self.log_terminal_output(traceback.format_exc(), "error")
            return False

    def navigate_to_llp_page(self):
        try:
            self.log_terminal_output("Navigating to LLP e-filling page...")
            self.driver.get("https://www.mca.gov.in/content/mca/global/en/mca/llp-e-filling/Fillip.html")
            self.log_terminal_output("Waiting 10 seconds for page to load completely...")
            time.sleep(10)  # Wait for 10 seconds
            self.log_terminal_output("LLP page loaded")
            return True
        except Exception as e:
            self.log_terminal_output(f"Error navigating to LLP page: {str(e)}", "error")
            return False

    def run_main_ipynb(self):
        try:
            notebook_path = os.path.join(os.getcwd(), "main.ipynb")
            self.log_terminal_output(f"Executing notebook {notebook_path} ...")

            with open(notebook_path) as f:
                nb = nbformat.read(f, as_version=4)

            ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
            ep.preprocess(nb, {'metadata': {'path': os.getcwd()}})

            self.log_terminal_output("Notebook executed successfully")
        except Exception as e:
            self.log_terminal_output(f"Error running main.ipynb: {str(e)}", "error")
            self.log_terminal_output(traceback.format_exc(), "error")

    def start_automation(self):
        try:
            if not self.start_browser_with_profile():
                self.log_terminal_output("Failed to start browser, aborting automation.", "error")
                return

            # First perform login
            self.log_terminal_output("Starting login process...")
            if not self.perform_login():
                self.log_terminal_output("Login failed, aborting.", "error")
                return

            # Wait for login to be fully processed
            time.sleep(5)
            self.log_terminal_output("Login successful, proceeding with automation...")

            # Navigate to LLP e-filling page
            self.log_terminal_output("Navigating to LLP e-filling page...")
            self.driver.get("https://www.mca.gov.in/content/mca/global/en/mca/llp-e-filling/Fillip.html")
            self.log_terminal_output("Waiting 10 seconds for page to load completely...")
            time.sleep(10)

            # Verify we're on the correct page
            if "Fillip.html" not in self.driver.current_url:
                self.log_terminal_output("Failed to reach LLP e-filling page", "error")
                return

            self.log_terminal_output("Successfully reached LLP e-filling page")
            
            # Execute main.ipynb
            self.log_terminal_output("Starting execution of main.ipynb...")
            try:
                notebook_path = os.path.join(os.getcwd(), "main.ipynb")
                self.log_terminal_output(f"Executing notebook: {notebook_path}")

                with open(notebook_path, "r", encoding="utf-8") as f:
                    nb = nbformat.read(f, as_version=4)

                ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
                ep.preprocess(nb, {'metadata': {'path': os.getcwd()}})
                self.log_terminal_output("main.ipynb executed successfully")
            except Exception as e:
                self.log_terminal_output(f"Error executing main.ipynb: {str(e)}", "error")
                self.log_terminal_output(traceback.format_exc(), "error")
                return

        except Exception as e:
            self.log_terminal_output(f"Error in automation process: {str(e)}", "error")
            self.log_terminal_output(traceback.format_exc(), "error")
        finally:
            self.log_terminal_output("Automation process complete. Cleaning up...")
            if self.driver:
                self.driver.quit()


def auto_upload_file(driver, button_css_selector, file_path):
    """Automatically click the Choose File button and upload a document.
    
    Args:
        driver: Selenium WebDriver instance
        button_css_selector: CSS selector for the Choose File button
        file_path: Path to the file to upload
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        log_terminal_output("\n=== Starting Automatic File Upload Process ===")
        
        # Validate inputs
        if not driver:
            log_terminal_output("Error: WebDriver instance is required", "error")
            return False
            
        if not button_css_selector:
            log_terminal_output("Error: Button CSS selector is required", "error")
            return False
            
        if not file_path:
            log_terminal_output("Error: File path is required", "error")
            return False
            
        # Normalize file path
        try:
            if '\\' in file_path:
                file_path = file_path.replace('\\', '/')
            abs_file_path = os.path.abspath(file_path)
            log_terminal_output(f"Normalized file path: {abs_file_path}")
        except Exception as e:
            log_terminal_output(f"Error normalizing file path: {str(e)}", "error")
            return False
            
        # Verify file exists
        if not os.path.exists(abs_file_path):
            log_terminal_output(f"Error: File not found at path: {abs_file_path}", "error")
            return False
            
        # Take screenshot before starting
        try:
            screenshot_path = f"before_upload_click_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            log_terminal_output(f"Screenshot saved before upload: {screenshot_path}")
        except Exception as e:
            log_terminal_output(f"Warning: Could not take screenshot: {str(e)}", "warning")
            
        # Find and click the Choose File button
        try:
            # Wait for button to be present and clickable
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, button_css_selector))
            )
            
            # Scroll button into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            
            # Try multiple click methods
            click_success = False
            
            # Method 1: Direct click
            try:
                button.click()
                log_terminal_output("Clicked button directly")
                click_success = True
            except Exception as e:
                log_terminal_output(f"Direct click failed: {str(e)}", "warning")
                
            # Method 2: JavaScript click
            if not click_success:
                try:
                    driver.execute_script("arguments[0].click();", button)
                    log_terminal_output("Clicked button using JavaScript")
                    click_success = True
                except Exception as e:
                    log_terminal_output(f"JavaScript click failed: {str(e)}", "warning")
                    
            # Method 3: ActionChains
            if not click_success:
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(button).click().perform()
                    log_terminal_output("Clicked button using ActionChains")
                    click_success = True
                except Exception as e:
                    log_terminal_output(f"ActionChains click failed: {str(e)}", "warning")
            
            if not click_success:
                log_terminal_output("Error: Could not click the Choose File button", "error")
                return False
                
            # Wait for file input to appear
            time.sleep(2)  # Increased wait time
            
            # Find the file input element that appears after clicking
            try:
                # Try different selectors for the file input
                file_input_selectors = [
                    "input[type='file']",
                    "input[accept*='pdf']",
                    "input[accept*='document']",
                    "input.file-upload",
                    "input.upload-input",
                    "input[class*='file']",
                    "input[class*='upload']",
                    "input[style*='display: none']",  # Hidden file inputs
                    "input[style*='display:none']",
                    "input[type='file'][style*='display: none']",
                    "input[type='file'][style*='display:none']"
                ]
                
                # Also try finding by XPath
                xpath_selectors = [
                    "//input[@type='file']",
                    "//input[contains(@class, 'file')]",
                    "//input[contains(@class, 'upload')]",
                    "//input[contains(@style, 'display: none')]",
                    "//input[contains(@style, 'display:none')]"
                ]
                
                file_input = None
                
                # First try CSS selectors
                for selector in file_input_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            # Check if element is present in DOM
                            if element.is_enabled():
                                file_input = element
                                log_terminal_output(f"Found file input using CSS selector: {selector}")
                                break
                        if file_input:
                            break
                    except Exception as e:
                        log_terminal_output(f"Warning: CSS selector {selector} failed: {str(e)}", "warning")
                        continue
                
                # If not found, try XPath selectors
                if not file_input:
                    for xpath in xpath_selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, xpath)
                            for element in elements:
                                if element.is_enabled():
                                    file_input = element
                                    log_terminal_output(f"Found file input using XPath: {xpath}")
                                    break
                            if file_input:
                                break
                        except Exception as e:
                            log_terminal_output(f"Warning: XPath {xpath} failed: {str(e)}", "warning")
                            continue
                
                # If still not found, try JavaScript to find hidden inputs
                if not file_input:
                    try:
                        file_input = driver.execute_script("""
                            return document.querySelector('input[type="file"]') || 
                                   document.querySelector('input[accept*="pdf"]') ||
                                   document.querySelector('input[class*="file"]') ||
                                   document.querySelector('input[class*="upload"]');
                        """)
                        if file_input:
                            log_terminal_output("Found file input using JavaScript")
                    except Exception as e:
                        log_terminal_output(f"Warning: JavaScript file input search failed: {str(e)}", "warning")
                
                if not file_input:
                    log_terminal_output("Error: Could not find file input element", "error")
                    return False
                    
                # Send file path to input
                try:
                    # Try direct send_keys first
                    file_input.send_keys(abs_file_path)
                    log_terminal_output("File path sent to input using send_keys")
                except Exception as e:
                    log_terminal_output(f"Warning: Direct send_keys failed: {str(e)}", "warning")
                    try:
                        # Try JavaScript as fallback
                        driver.execute_script("""
                            arguments[0].value = arguments[1];
                            arguments[0].dispatchEvent(new Event('change', { 'bubbles': true }));
                        """, file_input, abs_file_path)
                        log_terminal_output("File path sent to input using JavaScript")
                    except Exception as e:
                        log_terminal_output(f"Error: Could not send file path to input: {str(e)}", "error")
                        return False
                
                # Take screenshot after upload
                try:
                    screenshot_path = f"after_upload_{int(time.time())}.png"
                    driver.save_screenshot(screenshot_path)
                    log_terminal_output(f"Screenshot saved after upload: {screenshot_path}")
                except Exception as e:
                    log_terminal_output(f"Warning: Could not take screenshot: {str(e)}", "warning")
                
                # Wait for upload to complete
                time.sleep(2)
                
                # Verify upload
                try:
                    # Check if file input has the file path
                    actual_value = file_input.get_attribute('value')
                    if abs_file_path in actual_value:
                        log_terminal_output("Successfully verified file upload")
                        return True
                    else:
                        log_terminal_output(f"Warning: File path verification failed. Expected: {abs_file_path}, Got: {actual_value}", "warning")
                        return False
                except Exception as e:
                    log_terminal_output(f"Warning: Could not verify upload: {str(e)}", "warning")
                    return False
                    
            except Exception as e:
                log_terminal_output(f"Error handling file input: {str(e)}", "error")
                return False
                
        except Exception as e:
            log_terminal_output(f"Error finding or clicking button: {str(e)}", "error")
            return False
            
    except Exception as e:
        log_terminal_output(f"Error in auto_upload_file: {str(e)}", "error")
        log_terminal_output(traceback.format_exc(), "error")
        return False

def auto_upload_file_xpath(driver, button_xpath, file_path):
    """Automatically click the Choose File button and upload a document using XPath.
    
    Args:
        driver: Selenium WebDriver instance
        button_xpath: XPath for the Choose File button
        file_path: Path to the file to upload
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        log_terminal_output("\n=== Starting Automatic File Upload Process (XPath) ===")
        
        # Validate inputs
        if not driver:
            log_terminal_output("Error: WebDriver instance is required", "error")
            return False
            
        if not button_xpath:
            log_terminal_output("Error: Button XPath is required", "error")
            return False
            
        if not file_path:
            log_terminal_output("Error: File path is required", "error")
            return False
            
        # Normalize file path
        try:
            if '\\' in file_path:
                file_path = file_path.replace('\\', '/')
            abs_file_path = os.path.abspath(file_path)
            log_terminal_output(f"Normalized file path: {abs_file_path}")
        except Exception as e:
            log_terminal_output(f"Error normalizing file path: {str(e)}", "error")
            return False
            
        # Verify file exists
        if not os.path.exists(abs_file_path):
            log_terminal_output(f"Error: File not found at path: {abs_file_path}", "error")
            return False
            
        # Take screenshot before starting
        try:
            screenshot_path = f"before_upload_click_xpath_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            log_terminal_output(f"Screenshot saved before upload: {screenshot_path}")
        except Exception as e:
            log_terminal_output(f"Warning: Could not take screenshot: {str(e)}", "warning")
            
        # Find and click the Choose File button
        try:
            # Wait for button to be present and clickable
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            
            # Scroll button into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            
            # Try multiple click methods
            click_success = False
            
            # Method 1: Direct click
            try:
                button.click()
                log_terminal_output("Clicked button directly")
                click_success = True
            except Exception as e:
                log_terminal_output(f"Direct click failed: {str(e)}", "warning")
                
            # Method 2: JavaScript click
            if not click_success:
                try:
                    driver.execute_script("arguments[0].click();", button)
                    log_terminal_output("Clicked button using JavaScript")
                    click_success = True
                except Exception as e:
                    log_terminal_output(f"JavaScript click failed: {str(e)}", "warning")
                    
            # Method 3: ActionChains
            if not click_success:
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(button).click().perform()
                    log_terminal_output("Clicked button using ActionChains")
                    click_success = True
                except Exception as e:
                    log_terminal_output(f"ActionChains click failed: {str(e)}", "warning")
            
            if not click_success:
                log_terminal_output("Error: Could not click the Choose File button", "error")
                return False
                
            # Wait for file input to appear
            time.sleep(2)  # Increased wait time
            
            # Find the file input element that appears after clicking
            try:
                # Try different XPath patterns for the file input
                xpath_patterns = [
                    "//input[@type='file']",
                    "//input[contains(@class, 'file')]",
                    "//input[contains(@class, 'upload')]",
                    "//input[contains(@style, 'display: none')]",
                    "//input[contains(@style, 'display:none')]",
                    "//input[contains(@accept, 'pdf')]",
                    "//input[contains(@accept, 'document')]",
                    "//input[contains(@id, 'file')]",
                    "//input[contains(@id, 'upload')]",
                    "//input[contains(@name, 'file')]",
                    "//input[contains(@name, 'upload')]"
                ]
                
                file_input = None
                
                # Try each XPath pattern
                for xpath in xpath_patterns:
                    try:
                        elements = driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            if element.is_enabled():
                                file_input = element
                                log_terminal_output(f"Found file input using XPath: {xpath}")
                                break
                        if file_input:
                            break
                    except Exception as e:
                        log_terminal_output(f"Warning: XPath {xpath} failed: {str(e)}", "warning")
                        continue
                
                # If not found, try JavaScript to find hidden inputs
                if not file_input:
                    try:
                        file_input = driver.execute_script("""
                            return document.querySelector('input[type="file"]') || 
                                   document.querySelector('input[accept*="pdf"]') ||
                                   document.querySelector('input[class*="file"]') ||
                                   document.querySelector('input[class*="upload"]');
                        """)
                        if file_input:
                            log_terminal_output("Found file input using JavaScript")
                    except Exception as e:
                        log_terminal_output(f"Warning: JavaScript file input search failed: {str(e)}", "warning")
                
                if not file_input:
                    log_terminal_output("Error: Could not find file input element", "error")
                    return False
                    
                # Send file path to input
                try:
                    # Try direct send_keys first
                    file_input.send_keys(abs_file_path)
                    log_terminal_output("File path sent to input using send_keys")
                except Exception as e:
                    log_terminal_output(f"Warning: Direct send_keys failed: {str(e)}", "warning")
                    try:
                        # Try JavaScript as fallback
                        driver.execute_script("""
                            arguments[0].value = arguments[1];
                            arguments[0].dispatchEvent(new Event('change', { 'bubbles': true }));
                        """, file_input, abs_file_path)
                        log_terminal_output("File path sent to input using JavaScript")
                    except Exception as e:
                        log_terminal_output(f"Error: Could not send file path to input: {str(e)}", "error")
                        return False
                
                # Take screenshot after upload
                try:
                    screenshot_path = f"after_upload_xpath_{int(time.time())}.png"
                    driver.save_screenshot(screenshot_path)
                    log_terminal_output(f"Screenshot saved after upload: {screenshot_path}")
                except Exception as e:
                    log_terminal_output(f"Warning: Could not take screenshot: {str(e)}", "warning")
                
                # Wait for upload to complete
                time.sleep(2)
                
                # Verify upload
                try:
                    # Check if file input has the file path
                    actual_value = file_input.get_attribute('value')
                    
                    # Get just the filename from both paths
                    expected_filename = os.path.basename(abs_file_path)
                    actual_filename = os.path.basename(actual_value)
                    
                    # Check if the filenames match (ignoring the fakepath)
                    if expected_filename == actual_filename:
                        log_terminal_output("Successfully verified file upload")
                        return True
                    else:
                        log_terminal_output(f"Warning: File name verification failed. Expected: {expected_filename}, Got: {actual_filename}", "warning")
                        return False
                except Exception as e:
                    log_terminal_output(f"Warning: Could not verify upload: {str(e)}", "warning")
                    return False
                    
            except Exception as e:
                log_terminal_output(f"Error handling file input: {str(e)}", "error")
                return False
                
        except Exception as e:
            log_terminal_output(f"Error finding or clicking button: {str(e)}", "error")
            return False
            
    except Exception as e:
        log_terminal_output(f"Error in auto_upload_file_xpath: {str(e)}", "error")
        log_terminal_output(traceback.format_exc(), "error")
        return False

if __name__ == "__main__":
    try:
        MCAAutomation().start_automation()
    finally:
        input("\n\n🔚 Automation finished. Press Enter to exit...")

def log_terminal_output(message, level="info"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level.upper()}] {message}")




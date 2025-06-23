import os
import time
import base64
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager # <-- Added this import
from function1 import click_element

driver = None

# --- Configuration Loading ---
try:
    with open("config_data.json", "r") as f:
        config = json.load(f)
    LOGIN_URL = config.get("fillip_url")
    LOGIN_ID = config.get("user_email")
    LOGIN_PASSWORD = config.get("user_password")
    FIREFOX_PROFILE_PATH = config.get("firefox_profile_path")

    # LOGIN_URL = "https://www.mca.gov.in/content/mca/global/en/application-history.html"

    if not all([LOGIN_URL, LOGIN_ID, LOGIN_PASSWORD]):
        raise ValueError("LOGIN_URL, LOGIN_ID, or LOGIN_PASSWORD missing in login_data.json")

except FileNotFoundError:
    print("[ERROR] login_data.json not found. Please create it with necessary configurations.")
    raise
except Exception as e:
    print(f"[ERROR] Error loading config from login_data.json: {e}")
    raise

APPLICATION_HISTORY_URL = "https://www.mca.gov.in/content/mca/global/en/application-history.html"
MCA_HOME_URL = "https://www.mca.gov.in/content/mca/global/en/home.html"


# --- TrueCaptcha Credentials (Hardcoded) ---
TRUECAPTCHA_USER = "techteam@registerkaro.in"
TRUECAPTCHA_KEY = "z7kzX7lqeiNkGayvXjiY"

# --- Logger Functions ---
def log_info(message):
    """Prints an info message."""
    print(f"[INFO] {time.strftime('%Y-%m-%d %H:%M:%S')} {message}")

def log_error(message):
    """Prints an error message."""
    print(f"[ERROR] {time.strftime('%Y-%m-%d %H:%M:%S')} {message}")

def log_warning(message):
    """Prints a warning message."""
    print(f"[WARNING] {time.strftime('%Y-%m-%d %H:%M:%S')} {message}")

# --- Helper Functions ---
def initialize_driver(firefox_options):
    """Initializes the Firefox driver using webdriver-manager."""
    try:
        print("Setting up geckodriver using webdriver-manager...")
        driver_path = GeckoDriverManager().install()
        print(f"Geckodriver installed at: {driver_path}")

        # Initialize the driver with the Service object
        service = FirefoxService(driver_path)
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"Error setting up geckodriver: {e}")
        raise

def solve_captcha_api(image_data):
    """Solve captcha using TrueCaptcha API"""
    log_info("Attempting to solve CAPTCHA via API...")
    try:
        encoded_string = base64.b64encode(image_data).decode('ascii')
        url = 'https://api.apitruecaptcha.org/one/gettext'
        data = {
            'userid': TRUECAPTCHA_USER,
            'apikey': TRUECAPTCHA_KEY,
            'data': encoded_string
        }
        response = requests.post(url=url, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        captcha_text = result.get('result', '')
        if captcha_text:
            log_info(f"CAPTCHA API returned: {captcha_text}")
            return captcha_text
        else:
            log_warning(f"CAPTCHA API did not return a result. Response: {result}")
            return None
    except requests.exceptions.RequestException as e:
        log_error(f"Error connecting to CAPTCHA API: {e}")
        return None
    except Exception as e:
        log_error(f"Error solving captcha via API: {e}")
        return None

def handle_captcha_on_page(driver, max_attempts=5):
    """Handle captcha on the website with retry logic"""
    log_info("Handling CAPTCHA on page...")
    attempt = 0
    captcha_image_id = "captchaCanvas"
    captcha_input_id = "customCaptchaInput"
    submit_button_id = "guideContainer-rootPanel-panel_1846244155-submit___widget" # Ensure this ID is correct for the login page
    refresh_button_id = "refresh-img"
    captcha_error_message_id = "showResult"

    while attempt < max_attempts:
        log_info(f"CAPTCHA attempt {attempt + 1} of {max_attempts}")
        try:
            captcha_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, captcha_image_id))
            )
            time.sleep(1)
            image_data = captcha_element.screenshot_as_png
            captcha_text = solve_captcha_api(image_data)

            if captcha_text:
                captcha_input_field = driver.find_element(By.ID, captcha_input_id)
                captcha_input_field.clear()
                captcha_input_field.send_keys(captcha_text)
                time.sleep(0.5)
                submit_button = driver.find_element(By.ID, submit_button_id)
                submit_button.click()
                log_info("Clicked submit after entering CAPTCHA.")
                time.sleep(3.5)

                try:
                    error_message_element = driver.find_element(By.ID, captcha_error_message_id)
                    if error_message_element.is_displayed() and "The captcha entered is incorrect" in error_message_element.text:
                        log_warning("CAPTCHA incorrect. Refreshing...")
                        captcha_input_field.clear()
                        driver.find_element(By.ID, refresh_button_id).click()
                        time.sleep(2)
                        attempt += 1
                        continue
                    else:
                        log_info("CAPTCHA submitted, no immediate 'incorrect captcha' error found.")
                        return True
                except NoSuchElementException:
                    log_info("No CAPTCHA error message element found. Assuming CAPTCHA was accepted or page changed.")
                    return True
            else:
                log_warning("CAPTCHA API did not return text. Refreshing CAPTCHA on page.")
                driver.find_element(By.ID, refresh_button_id).click()
                time.sleep(2)
                attempt += 1
        except TimeoutException:
            log_error(f"Timeout waiting for CAPTCHA element ({captcha_image_id}).")
            return False
        except NoSuchElementException as e:
            log_error(f"A CAPTCHA related element not found: {e}. Check IDs if on login page.")
            # If not on a page with captcha, this might be expected if redirected.
            # Consider how to handle this if the redirect logic already moved past login.
            # For now, assume if this function is called, captcha elements should be there.
            try:
                # Try refreshing only if refresh button is actually present
                if driver.find_elements(By.ID, refresh_button_id):
                    driver.find_element(By.ID, refresh_button_id).click()
                    time.sleep(2)
                else: # Cannot refresh, likely not on captcha page
                    return False # Cannot proceed with captcha handling
            except Exception as refresh_e:
                log_error(f"Could not refresh CAPTCHA after element not found: {refresh_e}")
                return False
            attempt += 1
        except Exception as e:
            log_error(f"General error in handle_captcha_on_page: {e}")
            attempt += 1
            if attempt < max_attempts:
                try:
                    if driver.find_elements(By.ID, refresh_button_id):
                        driver.find_element(By.ID, refresh_button_id).click()
                        time.sleep(2)
                except Exception as refresh_e:
                    log_error(f"Could not refresh CAPTCHA after general error: {refresh_e}")
            time.sleep(1)
    log_error("Max CAPTCHA attempts reached.")
    return False

def close_initial_popup_option_b(driver, max_close_attempts=2):
    """
    Close the initial popup if present, using Option B (check for absence) with retries.
    Adjust XPATH as needed.
    """
    popup_element_xpath = "/html/body/div[2]/div/div[2]/div/div/div/div[2]/button" # User-provided XPath

    for attempt in range(max_close_attempts):
        log_info(f"Attempting to close pop-up and verify absence (Attempt {attempt + 1} of {max_close_attempts})...")
        try:
            close_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, popup_element_xpath))
            )
            close_button.click()
            log_info(f"Clicked pop-up element on attempt {attempt + 1}.")
            time.sleep(0.5)

            try:
                WebDriverWait(driver, 2).until_not(
                    EC.presence_of_element_located((By.XPATH, popup_element_xpath))
                )
                log_info("Pop-up successfully closed (element no longer present).")
                return True
            except TimeoutException:
                log_warning(f"Pop-up element still present after click attempt {attempt + 1}.")
                if attempt < max_close_attempts - 1:
                    log_info("Will retry closing pop-up.")
                else:
                    log_error("Max attempts reached, pop-up still present.")
                    return False

        except TimeoutException:
            log_info(f"Pop-up element not found or not clickable on attempt {attempt + 1}. Assuming pop-up is not an issue.")
            try:
                WebDriverWait(driver, 1).until_not(
                       EC.presence_of_element_located((By.XPATH, popup_element_xpath))
                )
                log_info("Confirmed: Pop-up element is not present.")
                return True
            except TimeoutException:
                log_warning(f"Pop-up element (e.g. close button) was not initially clickable/found in attempt {attempt +1}, but an element matching XPath '{popup_element_xpath}' is still present.")
                if attempt < max_close_attempts - 1:
                    continue
                else:
                    return False
        except Exception as e:
            log_error(f"An error occurred during pop-up close attempt {attempt + 1}: {e}")
            if attempt < max_close_attempts - 1:
                log_info("Will retry closing pop-up due to error.")
            else:
                log_error("Max attempts reached due to errors, pop-up could not be closed reliably.")
                return False



    log_error("Exited pop-up close attempts loop without success.")
    return False

def check_login_success_url_only(driver):
    """Verify if login was successful by checking URL ONLY."""
    log_info("Checking login success (URL only)...")
    try:
        WebDriverWait(driver, 15).until(
            lambda d: APPLICATION_HISTORY_URL in d.current_url
        )
        current_url = driver.current_url
        log_info(f"Current URL is: {current_url}. Expected to contain: {APPLICATION_HISTORY_URL}")
        if APPLICATION_HISTORY_URL in current_url:
            log_info("Login success confirmed by URL.")
            return True
        else:
            log_error(f"Login failed. URL is: {current_url}, expected to contain: {APPLICATION_HISTORY_URL}")
            return False
    except TimeoutException:
        log_error(f"Login verification failed: Timed out waiting for URL to contain {APPLICATION_HISTORY_URL}. Current URL: {driver.current_url}")
        return False
    except Exception as e:
        log_error(f"Exception during URL check for login success: {e}")
        return False

def login_to_mca_and_verify():
    """Main function to login to MCA and verify."""
    log_info("Starting MCA login process...")
    driver = None
    login_successful = False
    perform_form_login = True # Flag to determine if form login steps are needed

    try:
        firefox_options = FirefoxOptions()
        if FIREFOX_PROFILE_PATH and os.path.exists(FIREFOX_PROFILE_PATH):
            firefox_options.add_argument("-profile")
            firefox_options.add_argument(FIREFOX_PROFILE_PATH)
            log_info(f"Using Firefox profile: {FIREFOX_PROFILE_PATH}")
        else:
            log_info("No valid Firefox profile path provided or found. Using default profile.")

        # --- MODIFIED SECTION ---
        # Initialize driver using the new function
        driver = initialize_driver(firefox_options)
        log_info("Firefox browser initialized.")
        # --- END MODIFIED SECTION ---


        driver.get(LOGIN_URL)
        log_info(f"Navigated to login page: {LOGIN_URL}")
        time.sleep(3) # User-specified wait time after initial get

        # --- Check for homepage redirect ---
        current_url_after_get = driver.current_url
        log_info(f"Current URL after initial load and 3s wait: {current_url_after_get}")

        if MCA_HOME_URL in current_url_after_get:
            log_info(f"Detected landing on MCA homepage ('{MCA_HOME_URL}'). Attempting to navigate directly to Application History.")
            driver.get(APPLICATION_HISTORY_URL)
            log_info(f"Navigated to Application History page: {APPLICATION_HISTORY_URL}")
            time.sleep(4) # Allow application history page to load
            perform_form_login = False # Skip form login steps
        else:
            log_info("Not on MCA homepage. Proceeding with normal login flow.")
            perform_form_login = True

        if perform_form_login:
            if not close_initial_popup_option_b(driver):
                log_warning("Could not reliably close initial pop-up. Proceeding with caution.")

            user_field_id = "guideContainer-rootPanel-panel_1846244155-guidetextbox___widget"
            password_field_id = "guideContainer-rootPanel-panel_1846244155-guidepasswordbox___widget"

            try:
                log_info("Attempting to fill login details...")
                user_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, user_field_id))
                )
                user_field.clear()
                user_field.send_keys(LOGIN_ID)
                log_info("Entered Login ID.")

                password_field = driver.find_element(By.ID, password_field_id)
                password_field.clear()
                password_field.send_keys(LOGIN_PASSWORD)
                log_info("Entered Password.")
            except TimeoutException:
                log_error("Timeout waiting for login ID or Password field. Check element IDs.")
                # If fields aren't found, and we were supposed to do form login, it's a failure for this path
                return driver, False
            except NoSuchElementException:
                log_error("Login ID or Password field not found. Check element IDs.")
                return driver, False

            if not handle_captcha_on_page(driver):
                log_error("CAPTCHA handling failed.")
                # If captcha fails, login_successful remains false, proceed to final check
            else:
                log_info("CAPTCHA handling reported success or moved past.")

        # --- Verify Login Success (common to both paths) ---
        time.sleep(2) # Give a moment for any post-submit redirect or direct navigation to fully complete
        if check_login_success_url_only(driver):
            log_info("MCA Login Successful!")
            login_successful = True
        else:
            log_error("MCA Login Failed based on URL check.")
            log_info(f"Current page URL: {driver.current_url}")
            log_info("Current page title: " + driver.title)

        log_info("Script has finished its tasks.")

    except Exception as e:
        log_error(f"An unexpected error occurred in the main process: {e}")
    finally:
        if driver:
            log_info("Browser will remain open as per request.")
        else:
            log_info("Driver was not initialized, or an error occurred before initialization was complete.")

    return driver, login_successful



if __name__ == "__main__":
    active_driver, success_status = login_to_mca_and_verify()

    click_element(active_driver, css_selector='#btnPendingAction')
    log_info(f"Final Login Status: {'Successful' if success_status else 'Failed'}")
    log_info("Python script execution finished. The browser window should remain open.")
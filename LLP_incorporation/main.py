import os
import time
import base64
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
def solve_captcha(captcha_img):
    """
    Solve the captcha by taking a screenshot and using TrueCaptcha API.
    Args:
        captcha_img: The WebElement representing the captcha image
    Returns:
        str: The solved captcha text
    """
    # Create screenshots directory if it doesn't exist
    os.makedirs("screenshots", exist_ok=True)
    captcha_path = os.path.join("screenshots", "captcha.png")
    # Take screenshot of the captcha
    captcha_img.screenshot(captcha_path)
    # Base64-encode the screenshot
    with open(captcha_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    # Send to TrueCaptcha API
    resp = requests.post(
        "https://api.apitruecaptcha.org/one/gettext",
        json={"userid": TRUECAPTCHA_USER, "apikey": TRUECAPTCHA_KEY, "data": b64}
    )
    resp.raise_for_status()
    # Return the solved captcha text
    return resp.json().get("result", "").strip()
def initialize_browser(firefox_profile_path):
    """
    Initialize Firefox browser with specified profile path
    Args:
        firefox_profile_path: Path to the Firefox profile to use
    Returns:
        WebDriver: Initialized Firefox WebDriver instance
    """
    try:
        print("Initializing Firefox browser...")
        firefox_options = Options()
        
        if firefox_profile_path and os.path.exists(firefox_profile_path):
            print(f"Using existing Firefox profile: {firefox_profile_path}")
            firefox_options.profile = firefox_profile_path
        else:
            print("No Firefox profile specified or profile not found. Using default profile.")
        
        # Initialize the driver
        driver = webdriver.Firefox(options=firefox_options)
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"Error initializing browser: {str(e)}")
        raise
def main():
    """Main function to handle the login process to MCA portal."""
    try:
        # Load profile path from config.json
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
            firefox_profile_path = config.get("firefox_profile_path", "")
        except FileNotFoundError:
            print("config.json not found. Using default settings.")
            firefox_profile_path = ""
        
        # Initialize the WebDriver with the specified profile
        driver = initialize_browser(firefox_profile_path)
        
        try:
            # Navigate to login page
            print("Attempting to navigate to login page...")
            driver.get("https://www.mca.gov.in/content/mca/global/en/foportal/fologin.html")
            print("Navigation command executed. Waiting for page to load...")
            
            # Wait for page to load with timeout
            try:
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                print("Page load completed")
            except Exception as e:
                print(f"Timeout waiting for page to load: {str(e)}")
            
            # Check if we're on the correct page
            current_url = driver.current_url
            print(f"Current URL: {current_url}")
            
            if "mca.gov.in" not in current_url:
                print("Warning: Not on MCA website. Current URL:", current_url)
            
            time.sleep(5)  # Additional wait for dynamic content
            
            # Handle the dialog box that appears first
            print("Looking for dialog box...")
            try:
                # Wait for the dialog to appear and find the OK button
                ok_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-primary' and @data-dismiss='modal' and contains(text(), 'OK')]"))
                )
                print("Dialog found. Clicking OK button...")
                ok_button.click()
                time.sleep(2)  # Wait for dialog to close
                print("Dialog closed successfully")
            except Exception as e:
                print(f"No dialog detected or couldn't click OK button: {e}")
                print("Continuing with login process...")
            
            # Fill in User ID - try different selectors until one works
            print("Entering user ID...")
            for selector in [
                "//input[@type='text']",
                "//input[contains(@placeholder,'User ID')]",
                "//input[contains(@name,'userId')]"
            ]:
                try:
                    user_field = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.XPATH, selector))
                    )
                    user_field.clear()
                    user_field.send_keys("shagun@registerkaro.in")
                    break
                except:
                    continue
            
            # Fill in Password
            print("Entering password...")
            password_field = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            password_field.clear()
            password_field.send_keys("SLPL@1234")
            
            # Set expected successful URL after login
            expected_url = "https://www.mca.gov.in/content/mca/global/en/mca/llp-e-filling/Fillip.html"
            max_attempts = 10
            attempt = 1
            same_captcha_count = 0
            last_captcha_text = ""
            
            # Loop until successful login or max attempts reached
            while attempt <= max_attempts:
                print(f"\nCaptcha attempt {attempt}/{max_attempts}")
                
                # Find and solve the captcha
                print("Locating captcha image...")
                captcha_img = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "img[src*='captcha']"))
                )
                
                # Solve the captcha
                print("Solving captcha...")
                captcha_text = solve_captcha(captcha_img)
                print(f"Captcha solved: {captcha_text}")
                
                # Check if we're getting the same captcha result repeatedly
                if captcha_text == last_captcha_text:
                    same_captcha_count += 1
                    print(f"Same captcha solution detected {same_captcha_count} times in a row")
                else:
                    same_captcha_count = 0
                    last_captcha_text = captcha_text
                
                # If we've had the same captcha solution 2 times, refresh the captcha
                if same_captcha_count >= 2:
                    print("Refreshing captcha image...")
                    try:
                        refresh_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.ID, "refresh-img"))
                        )
                        refresh_button.click()
                        print("Captcha refresh button clicked")
                        time.sleep(2)  # Wait for new captcha to load
                        
                        # Reset the counter and get the new captcha
                        same_captcha_count = 0
                        captcha_img = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "img[src*='captcha']"))
                        )
                        print("Solving new captcha...")
                        captcha_text = solve_captcha(captcha_img)
                        print(f"New captcha solved: {captcha_text}")
                        last_captcha_text = captcha_text
                    except Exception as e:
                        print(f"Error refreshing captcha: {e}")
                
                # Enter the solved captcha
                print("Entering captcha solution...")
                captcha_field = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "customCaptchaInput"))
                )
                captcha_field.clear()
                captcha_field.send_keys(captcha_text)
                
                # Click Login button
                print("Clicking login button...")
                login_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login') or @type='submit']"))
                )
                login_button.click()
                
                # Wait for navigation
                print("Waiting for login response...")
                time.sleep(5)  # Increased wait time for page loading
                
                # Check if login was successful by checking URL
                current_url = driver.current_url
                print(f"Current URL: {current_url}")
                
                if expected_url in current_url:
                    print("Login successful! Redirected to application history page.")
                    break
                else:
                    print("Login failed. Incorrect captcha or other error.")
                    # Check for error message if any
                    try:
                        error_msg = driver.find_element(By.CSS_SELECTOR, ".alert-danger")
                        print(f"Error message: {error_msg.text}")
                    except:
                        print("No specific error message found.")
                    
                    # Increment attempt counter
                    attempt += 1
                    if attempt <= max_attempts:
                        print("Retrying with a new captcha...")
                        # Wait briefly before retrying
                        time.sleep(2)
            
            if attempt > max_attempts:
                print(f"Failed to login after {max_attempts} attempts. Please try manually.")
            else:
                print("Login process completed successfully.")
                
        except Exception as e:
            print(f"Error during page navigation: {str(e)}")
            # Take screenshot of the error state
            try:
                driver.save_screenshot("error_screenshot.png")
                print("Error screenshot saved as 'error_screenshot.png'")
            except:
                print("Could not save error screenshot")
            raise
        finally:
            # Keep the browser open for now (uncomment to close automatically)
            # driver.quit()
            pass
            
    except Exception as e:
        print(f"Fatal error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Load TrueCaptcha credentials from .env file
        load_dotenv()
        TRUECAPTCHA_USER = os.getenv("TRUECAPTCHA_USER")
        TRUECAPTCHA_KEY = os.getenv("TRUECAPTCHA_KEY")
        
        if not TRUECAPTCHA_USER or not TRUECAPTCHA_KEY:
            print("Warning: TrueCaptcha credentials not found in environment variables")
        
        # Execute the main login function
        main()
    except Exception as e:
        print(f"Script failed with error: {str(e)}")
        input("Press Enter to exit...")
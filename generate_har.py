# generate_har.py
import asyncio
import os
import time
import base64
import requests
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

# --- Load Configuration ---
load_dotenv()
LOGIN_URL = "https://www.mca.gov.in/content/mca/global/en/foportal/fologin.html"
LOGIN_ID = os.getenv("MCA_LOGIN_ID")
LOGIN_PASSWORD = os.getenv("MCA_LOGIN_PASSWORD")
TRUECAPTCHA_USER = os.getenv("TRUECAPTCHA_USER")
TRUECAPTCHA_KEY = os.getenv("TRUECAPTCHA_KEY")
APPLICATION_HISTORY_URL = "https://www.mca.gov.in/content/mca/global/en/application-history.html"
HOME_URL = "https://www.mca.gov.in/content/mca/global/en/home.html"
FIREFOX_PROFILE_PATH = os.getenv("FIREFOX_PROFILE_PATH")

# --- Helper Functions ---
def log_info(message):
    print(f"[INFO] {time.strftime('%Y-%m-%d %H:%M:%S')} {message}")

def log_error(message):
    print(f"[ERROR] {time.strftime('%Y-%m-%d %H:%M:%S')} {message}")

def solve_captcha_api(image_data):
    """Solves captcha using TrueCaptcha API."""
    log_info("Attempting to solve CAPTCHA via API...")
    try:
        encoded_string = base64.b64encode(image_data).decode('ascii')
        data = {'userid': TRUECAPTCHA_USER, 'apikey': TRUECAPTCHA_KEY, 'data': encoded_string}
        response = requests.post(url='https://api.apitruecaptcha.org/one/gettext', json=data, timeout=30)
        response.raise_for_status()
        return response.json().get('result')
    except Exception as e:
        log_error(f"Error solving captcha: {e}")
        return None

# --- Main Automation Logic ---
async def main():
    """Launches browser, logs in, handles OTP, and saves a HAR file."""
    if not all([LOGIN_ID, LOGIN_PASSWORD]):
        log_error("MCA_LOGIN_ID or MCA_LOGIN_PASSWORD not found in your .env file.")
        return

    async with async_playwright() as p:
        if FIREFOX_PROFILE_PATH and os.path.isdir(FIREFOX_PROFILE_PATH):
            log_info(f"Using persistent Firefox profile: {FIREFOX_PROFILE_PATH}")
            context = await p.firefox.launch_persistent_context(
                user_data_dir=FIREFOX_PROFILE_PATH, headless=False, record_har_path="network_log.har"
            )
        else:
            log_info("No valid Firefox profile path found. Using a temporary profile.")
            browser = await p.firefox.launch(headless=False)
            context = await browser.new_context(record_har_path="network_log.har")
        
        page = await context.new_page()
        login_successful = False

        try:
            log_info(f"Navigating to login page: {LOGIN_URL}")
            await page.goto(LOGIN_URL, wait_until="load", timeout=60000)
            
            # Check if already logged in by trying to access application history
            log_info("Checking if already logged in...")
            await page.goto(APPLICATION_HISTORY_URL, wait_until="load", timeout=30000)
            
            # If we can access application history directly, we're already logged in
            if "application-history" in page.url:
                log_info("Already logged in. Successfully accessed application history page.")
                login_successful = True
            else:
                log_info("Not logged in. Redirecting back to login page...")
                await page.goto(LOGIN_URL, wait_until="load", timeout=30000)
                
                log_info("Proceeding with login form...")
                await page.locator("#guideContainer-rootPanel-panel_1846244155-guidetextbox___widget").click()
                await page.locator("#guideContainer-rootPanel-panel_1846244155-guidetextbox___widget").type(LOGIN_ID, delay=100)
                
                await page.locator("#guideContainer-rootPanel-panel_1846244155-guidepasswordbox___widget").click()
                await page.locator("#guideContainer-rootPanel-panel_1846244155-guidepasswordbox___widget").type(LOGIN_PASSWORD, delay=100)

                max_attempts = 5
                for attempt in range(max_attempts):
                    log_info(f"CAPTCHA attempt {attempt + 1}/{max_attempts}")
                    captcha_element = page.locator("#captchaCanvas")
                    image_data = await captcha_element.screenshot()
                    captcha_text = solve_captcha_api(image_data)

                    if captcha_text:
                        await page.locator("#customCaptchaInput").fill(captcha_text)
                        await page.locator("#guideContainer-rootPanel-panel_1846244155-submit___widget").click()
                        
                        try:
                            # Wait for redirect after login (could be to home page or application history)
                            log_info("Waiting for login redirect...")
                            await page.wait_for_load_state("networkidle", timeout=30000)
                            
                            current_url = page.url
                            log_info(f"Current URL after login: {current_url}")
                            
                            # Check if we're on home page or application history page
                            if "home.html" in current_url:
                                log_info("Redirected to home page. Navigating to application history...")
                                await page.goto(APPLICATION_HISTORY_URL, wait_until="load", timeout=30000)
                                login_successful = True
                                break
                            elif "application-history" in current_url:
                                log_info("Successfully redirected to application history page!")
                                login_successful = True
                                break
                            else:
                                log_info(f"Unexpected redirect to: {current_url}")
                                # Try to navigate to application history anyway
                                await page.goto(APPLICATION_HISTORY_URL, wait_until="load", timeout=30000)
                                login_successful = True
                                break
                                
                        except PlaywrightTimeoutError:
                            log_info("Login redirect timeout. Checking for error message.")
                            try:
                               error_message = await page.locator("#showResult").text_content(timeout=2000)
                               if "incorrect" in error_message.lower():
                                    log_info("CAPTCHA incorrect, refreshing...")
                                    await page.locator("#refresh-img").click()
                                    await page.wait_for_timeout(1000)
                               else:
                                    log_error(f"An unknown login error occurred. Message: '{error_message}'. Aborting.")
                                    break
                            except PlaywrightTimeoutError:
                                log_error("Could not find a specific error message. Login has likely failed. Aborting.")
                                break
                    else:
                        log_error("Failed to get response from CAPTCHA API. Refreshing for next attempt.")
                        await page.locator("#refresh-img").click()
                        await page.wait_for_timeout(1000)
                        continue # Move to the next attempt in the loop

            if not login_successful:
                log_error("Login process failed. The script will not proceed.")
                return

            # Ensure we're on the application history page
            if "application-history" not in page.url:
                log_info("Navigating to application history page...")
                await page.goto(APPLICATION_HISTORY_URL, wait_until="load", timeout=30000)
            
            log_info("Successfully on application history page. Clicking tab to trigger API calls...")
            await page.locator("#btnApproved").click() 
            await page.wait_for_timeout(3000)
            log_info("Successfully captured network traffic.")

        except Exception as e:
            log_error(f"An unexpected error occurred: {e}")
        finally:
            log_info("Closing browser context and saving HAR file 'network_log.har'")
            await context.close()
            if 'browser' in locals() and browser.is_connected():
                await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

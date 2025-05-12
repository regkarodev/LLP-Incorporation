import base64
import requests
import os
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from logger import Logger
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Get Google Gemini API key from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def take_fullscreen_screenshot(driver, button_name="button", wait_for_scroll=True):
    logger = Logger()
    try:
        ss_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ss")
        os.makedirs(ss_folder, exist_ok=True)
        
        existing_files = [f for f in os.listdir(ss_folder) if f.startswith(f"{button_name}_") and f.endswith(".png")]
        if existing_files:
            existing_file = os.path.join(ss_folder, existing_files[-1])
            logger.log(f"Using existing screenshot: {existing_file}")
            return existing_file
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{button_name}_{timestamp}.png"
        filepath = os.path.join(ss_folder, filename)
        
        if wait_for_scroll:
            time.sleep(1)
            last_height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(0.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            while new_height != last_height:
                last_height = new_height
                time.sleep(0.5)
                new_height = driver.execute_script("return document.body.scrollHeight")
        
        viewport_width = driver.execute_script("return window.innerWidth;")
        viewport_height = driver.execute_script("return window.innerHeight;")
        
        driver.execute_script("document.documentElement.style.overflow = 'hidden'; document.body.style.overflow = 'hidden';")
        driver.save_screenshot(filepath)
        driver.execute_script("document.documentElement.style.overflow = ''; document.body.style.overflow = '';")
        
        logger.log(f"Successfully saved viewport screenshot to: {filepath}")
        logger.log(f"Viewport dimensions: {viewport_width}x{viewport_height}")
        return filepath

    except Exception as e:
        logger.log(f"Error taking screenshot: {str(e)}", "error")
        return None

def click_button_with_vision(driver, image_path="C:\\Users\\Admin\\Downloads\\mca_automation\\mca_automation\\src\\save_and_continue.png", prompt="Locate the blue-colored 'SAVE AND CONTINUE' button in the image. The button should be visible and clickable. Return only its exact screen coordinates in the format: x=..., y=.... Do not include any explanation or extra text. If the button is not visible or not found, return NOT_FOUND. This will be repeated in a loop until coordinates are successfully returned.", wait_for_scroll=True):
    logger = Logger()
    
    logger.log("Step 1: Checking if image exists")
    if os.path.exists(image_path) and os.path.isfile(image_path):
        logger.log(f"Using existing image: {image_path}")
    else:
        logger.log("Step 1.1: Taking new screenshot")
        screenshot_path = take_fullscreen_screenshot(driver, "button_co", wait_for_scroll)
        if not screenshot_path:
            logger.log("Failed to take screenshot, using default image path", "warning")
        else:
            image_path = screenshot_path
            logger.log(f"Using new screenshot: {image_path}")
    
    logger.log("Step 2: Checking API key")
    if not GEMINI_API_KEY:
        logger.log("Error: GEMINI_API_KEY is not set. Please follow these steps:", "error")
        logger.log("1. Create a .env file in your project directory", "error")
        logger.log("2. Add your API key like this: GEMINI_API_KEY=your_api_key_here", "error")
        logger.log("3. Get your API key from: https://makersuite.google.com/app/apikey", "error")
        return False

    logger.log(f"Using Google Gemini API key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-10:]}")
    
    logger.log("Step 3: Reading image file")
    try:
        if not os.path.exists(image_path):
            logger.log(f"Error: Image file not found at {image_path}", "error")
            return False
            
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
        logger.log(f"Successfully read image from: {image_path}")
    except Exception as e:
        logger.log(f"Error reading image file: {str(e)}", "error")
        return False

    logger.log("Step 4: Preparing API request")
    try:
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        
        data = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_data
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 2048,
            }
        }

        logger.log("Step 5: Sending API request")
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            headers=headers,
            json=data
        )

        if response.status_code != 200:
            logger.log(f"API request failed with status code: {response.status_code}", "error")
            logger.log(f"Response content: {response.text}", "error")
            return False

        logger.log("Step 6: Processing API response")
        result = response.json()
        logger.log(f"Full Gemini API response: {result}")

        if 'error' in result:
            logger.log(f"Gemini API error: {result['error']}", "error")
            return False

        if 'candidates' in result and len(result['candidates']) > 0:
            response_text = result['candidates'][0]['content']['parts'][0]['text']
            logger.log(f"Gemini API response text: {response_text}")
        else:
            logger.log("No response text found in Gemini API response", "error")
            return False

    except requests.exceptions.RequestException as e:
        logger.log(f"Network error in Gemini API request: {str(e)}", "error")
        return False
    except ValueError as e:
        logger.log(f"Invalid JSON response from Gemini API: {str(e)}", "error")
        logger.log(f"Raw response: {response.text}", "error")
        return False
    except Exception as e:
        logger.log(f"Unexpected error in Gemini API request: {str(e)}", "error")
        return False

    logger.log("Step 7: Parsing coordinates")
    try:
        import re
        patterns = [
            r"x\s*=\s*(\d+)[, ]+y\s*=\s*(\d+)",
            r"x:?\s*(\d+)[, ]+y:?\s*(\d+)",
            r"\((\d+),\s*(\d+)\)",
            r"(\d+),\s*(\d+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, response_text)
            if match:
                x, y = int(match.group(1)), int(match.group(2))
                
                logger.log("Step 8: Validating coordinates")
                if x == 0 and y == 0:
                    logger.log("Invalid coordinates (0,0) received. Button might not be visible.", "warning")
                    return False
                    
                logger.log(f"Found coordinates using pattern '{pattern}': x={x}, y={y}")

                logger.log("Step 9: Checking window bounds")
                window_size = driver.get_window_size()
                logger.log(f"Window size: {window_size}")
                viewport_height = driver.execute_script("return window.innerHeight;")
                logger.log(f"Viewport height: {viewport_height}")
                
                # Check if coordinates are within viewport bounds
                if x > window_size['width']:
                    logger.log(f"X-coordinate {x} is outside window width {window_size['width']}", "warning")
                    return False

                # If y-coordinate is below viewport, scroll to make it visible
                if y > viewport_height:
                    # Calculate scroll amount to bring the element into view with some margin
                    scroll_amount = y - (viewport_height // 2)
                    logger.log(f"Scrolling down by {scroll_amount}px to bring element into view")
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    time.sleep(1)  # Allow time for scrolling
                    
                    # Recalculate y-coordinate relative to the new viewport position
                    scroll_position = driver.execute_script("return window.pageYOffset;")
                    new_y = y - scroll_position
                    
                    if new_y < 0 or new_y > viewport_height:
                        logger.log(f"Element still out of viewport after scrolling. Y-coordinate: {new_y}, Viewport height: {viewport_height}", "warning")
                        # Try clicking at a safe coordinate instead
                        new_y = min(new_y, viewport_height - 10) 
                        new_y = max(new_y, 10)  # Ensure it's at least 10px from the top
                    
                    logger.log(f"Adjusted Y-coordinate after scrolling: {new_y}")
                    y = new_y

                # Print final coordinates before clicking
                logger.log(f"FINAL CLICK COORDINATES: x={x}, y={y}", "info")
                
                logger.log("Step 10: Performing click action")
                try:
                    ActionChains(driver).move_by_offset(x, y).click().perform()
                    ActionChains(driver).move_by_offset(-x, -y).perform()  # Reset mouse position
                    logger.log(f"Successfully clicked at coordinates: x={x}, y={y}")
                    return True
                except Exception as click_error:
                    logger.log(f"Error during click operation: {str(click_error)}", "error")
                    
                    # Alternative approach - use JavaScript to click
                    logger.log("Trying JavaScript click as fallback")
                    try:
                        driver.execute_script(f"document.elementFromPoint({x}, {y}).click();")
                        logger.log(f"Successfully clicked using JavaScript at coordinates: x={x}, y={y}")
                        return True
                    except Exception as js_error:
                        logger.log(f"JavaScript click also failed: {str(js_error)}", "error")
                        return False

        logger.log(f"Could not parse coordinates from response: {response_text}", "warning")
        return False

    except Exception as e:
        logger.log(f"Error clicking at coordinates: {str(e)}", "error")
        return False

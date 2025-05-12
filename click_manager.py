import os
import json
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
from logger import Logger
from vision_click_helper import click_button_with_vision
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class ClickManager:
    """
    Manages button click operations using various methods including:
    - Pre-defined coordinates
    - Cached coordinates from previous operations
    - Vision-based detection
    """
    
    # Class-level constants
    COORDINATES_FILE = "button_coordinates.json"
    LOG_FILE = "log.txt"
    MAX_SCROLL_ATTEMPTS = 3
    COORD_PATTERN = r"FINAL CLICK COORDINATES: x=(\d+), y=(\d+)"
    
    # Button name mappings for alternatives
    BUTTON_ALTERNATIVES = {
        "SAVE AND CONTINUE": ["SAVE AND CONTINUE_LOWER"],
        "NEXT": ["NEXT_LOWER", "NEXT_BUTTON"],
        # Add more button alternatives here
    }
    
    def __init__(self, driver, wait):
        """
        Initialize the click manager
        
        Args:
            driver: Selenium WebDriver instance
            wait: WebDriverWait instance
        """
        self.driver = driver
        self.wait = wait
        self.logger = Logger()
        self.coordinates_cache = {}
        
        # Pre-defined coordinates for common buttons - screen position mapping
        self.common_buttons = {
            "SAVE AND CONTINUE": (1281, 161),
            "SAVE AND CONTINUE_LOWER": (1282, 550),
            "NEXT": (1281, 161),
            "NEXT_LOWER": (1282, 550),
            # Add other button coordinates here
        }
        
        # Load any saved coordinates
        self.load_saved_coordinates()
        
    def load_saved_coordinates(self):
        """Load coordinates from saved file"""
        try:
            if os.path.exists(self.COORDINATES_FILE):
                with open(self.COORDINATES_FILE, "r") as f:
                    saved_coords = json.load(f)
                    
                for button, coords in saved_coords.items():
                    if isinstance(coords, list) and len(coords) == 2:
                        self.coordinates_cache[button] = tuple(coords)
                    elif isinstance(coords, tuple) and len(coords) == 2:
                        self.coordinates_cache[button] = coords
                        
                self.logger.log(f"Loaded {len(saved_coords)} button coordinates from file")
        except Exception as e:
            self.logger.log(f"Could not load saved coordinates: {str(e)}", "warning")
            
    def save_coordinates(self):
        """Save current coordinates cache to file"""
        try:
            # Convert tuple coordinates to lists for JSON serialization
            serializable_dict = {
                button: list(coords) if isinstance(coords, tuple) else coords
                for button, coords in self.coordinates_cache.items()
                if coords  # Only save non-None values
            }
            
            with open(self.COORDINATES_FILE, 'w') as f:
                json.dump(serializable_dict, f, indent=4)
                
            self.logger.log(f"Saved {len(serializable_dict)} coordinates to {self.COORDINATES_FILE}")
            return True
        except Exception as e:
            self.logger.log(f"Error saving coordinates: {str(e)}", "error")
            return False
            
    def get_best_coordinates(self, button_name):
        """
        Get the best available coordinates for a button
        
        Args:
            button_name: Name of the button
            
        Returns:
            tuple: Coordinates (x, y) or None if not found
        """
        # First check the cache for the most recently used coordinates
        coords = self.coordinates_cache.get(button_name)
        if coords:
            self.logger.log(f"Using cached coordinates for {button_name}")
            return coords
            
        # If not in cache, check pre-defined coordinates
        coords = self.common_buttons.get(button_name)
        if coords:
            self.logger.log(f"Using pre-defined coordinates for {button_name}")
            return coords
            
        # No coordinates found
        return None
        
    def click_at_coordinates(self, x, y):
        """
        Click at specific coordinates using multiple methods for reliability
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            bool: True if click was successful, False otherwise
        """
        self.logger.log(f"Clicking at coordinates: x={x}, y={y}")
        
        # Store page URL before clicking to check if navigation occurs
        current_url = self.driver.current_url
        page_source_length = len(self.driver.page_source)
        
        # Try multiple clicking methods until one works
        click_methods = [
            self._click_with_action_chains,
            self._click_with_javascript,
            self._click_with_offset_adjustment,
            self._click_with_force_javascript
        ]
        
        for i, click_method in enumerate(click_methods):
            method_name = click_method.__name__.replace("_click_with_", "")
            self.logger.log(f"Trying click method {i+1}/{len(click_methods)}: {method_name}")
            
            try:
                click_method(x, y)
                
                # Wait briefly for page to respond
                time.sleep(1)
                
                # Check if the page changed (indicating a successful click)
                if self._verify_page_changed(current_url, page_source_length):
                    self.logger.log(f"Click successful! Page changed after using {method_name}")
                    return True
                
                self.logger.log(f"Click registered but page didn't change using {method_name}", "warning")
            except Exception as e:
                self.logger.log(f"Error with {method_name}: {str(e)}", "error")
        
        # If all methods failed, log an error and return False
        self.logger.log("All click methods failed to produce page change", "error")
        return False
        
    def _click_with_action_chains(self, x, y):
        """Click using ActionChains"""
        actions = ActionChains(self.driver)
        actions.move_by_offset(x, y).click().perform()
        actions.move_by_offset(-x, -y).perform()  # Reset position
        self.logger.log("Click performed using ActionChains")
        
    def _click_with_javascript(self, x, y):
        """Click using JavaScript elementFromPoint"""
        self.driver.execute_script(f"""
            var element = document.elementFromPoint({x}, {y});
            if(element) {{
                element.click();
                return true;
            }}
            return false;
        """)
        self.logger.log("Click performed using JavaScript")
        
    def _click_with_offset_adjustment(self, x, y):
        """Click with slight offset adjustments"""
        # Try clicking slightly above the target
        actions = ActionChains(self.driver)
        actions.move_by_offset(x, y-5).click().perform()
        actions.move_by_offset(-x, -(y-5)).perform()
        self.logger.log("Click performed using offset adjustment")
        
    def _click_with_force_javascript(self, x, y):
        """Force click using advanced JavaScript"""
        self.driver.execute_script(f"""
            var element = document.elementFromPoint({x}, {y});
            if(element) {{
                // Try multiple events
                function triggerMouseEvent(el, eventType) {{
                    var event = new MouseEvent(eventType, {{
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: {x},
                        clientY: {y}
                    }});
                    el.dispatchEvent(event);
                }}
                
                // Simulate a full click sequence
                triggerMouseEvent(element, 'mousedown');
                triggerMouseEvent(element, 'mouseup');
                triggerMouseEvent(element, 'click');
                
                // If it's a form button, try to submit the closest form
                var form = element.closest('form');
                if(form) {{
                    try {{
                        form.submit();
                    }} catch(e) {{}}
                }}
                
                return true;
            }}
            return false;
        """)
        self.logger.log("Click performed using forced JavaScript events")
        
    def _verify_page_changed(self, original_url, original_length):
        """
        Verify if the page changed after a click
        
        Args:
            original_url: URL before clicking
            original_length: Length of page source before clicking
            
        Returns:
            bool: True if page changed, False otherwise
        """
        # Method 1: Check if URL changed
        current_url = self.driver.current_url
        if current_url != original_url:
            self.logger.log(f"URL changed from {original_url} to {current_url}")
            return True
            
        # Method 2: Check if page content length changed significantly
        new_length = len(self.driver.page_source)
        percent_change = abs(new_length - original_length) / original_length * 100
        if percent_change > 5:  # If content changed by more than 5%
            self.logger.log(f"Page content changed by {percent_change:.2f}%")
            return True
            
        # Method 3: Check for loading indicators
        try:
            loading_indicators = self.driver.find_elements(
                By.CSS_SELECTOR, ".loading, .spinner, .progress, [role='progressbar']")
            if loading_indicators:
                self.logger.log("Found loading indicators after click")
                # Wait for them to disappear
                time.sleep(2)
                return True
        except Exception as e:
            self.logger.log(f"Error checking for loading indicators: {str(e)}", "debug")
            
        return False
    
    def get_alternative_button_names(self, button_name):
        """Get alternative names for a button"""
        return self.BUTTON_ALTERNATIVES.get(button_name, [])
    
    def extract_coords_from_log(self):
        """Extract coordinates from log file if available"""
        try:
            if os.path.exists(self.LOG_FILE):
                with open(self.LOG_FILE, "r") as log_file:
                    log_content = log_file.read()
                    coord_match = re.search(self.COORD_PATTERN, log_content)
                    if coord_match:
                        return (int(coord_match.group(1)), int(coord_match.group(2)))
        except Exception as e:
            self.logger.log(f"Could not extract coordinates from log: {str(e)}", "warning")
        return None
    
    def verify_blue_button_at_coordinates(self, x, y, button_name="SAVE AND CONTINUE"):
        """
        Verify whether a blue button exists at the specified coordinates
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            button_name: Name of the button (for logging purposes)
            
        Returns:
            bool: True if button is detected at coordinates, False otherwise
        """
        self.logger.log(f"Verifying if '{button_name}' button exists at coordinates x={x}, y={y}")
        
        try:
            # Method 1: Check if there's a clickable element at the coordinates
            element_js = self.driver.execute_script(f"""
                var element = document.elementFromPoint({x}, {y});
                if (!element) return null;
                
                // Check element properties to determine if it's a button
                var tag = element.tagName.toLowerCase();
                var text = element.innerText || element.textContent || '';
                var backgroundColor = window.getComputedStyle(element).backgroundColor;
                var isBlueish = backgroundColor.includes('rgb(') && 
                                (backgroundColor.match(/rgb\((\d+),\s*(\d+),\s*(\d+)/) || []).some(function(color) {{
                                    return color && parseInt(color) > 0 && parseInt(color) < 100;
                                }});
                
                return {{
                    'isButton': tag === 'button' || tag === 'a' || tag === 'input' || 
                                element.getAttribute('role') === 'button' ||
                                element.classList.contains('btn') || 
                                element.classList.contains('button'),
                    'text': text.trim(),
                    'isBlue': isBlueish,
                    'tag': tag,
                    'classes': element.className
                }};
            """)
            
            if element_js:
                self.logger.log(f"Element found at coordinates: {element_js}")
                
                # Check if it looks like a button
                if element_js.get('isButton'):
                    self.logger.log("Element appears to be a button based on HTML structure")
                    
                    # Check if the button contains the expected text (case insensitive)
                    button_text = element_js.get('text', '').lower()
                    expected_text = button_name.lower().replace('_', ' ')
                    
                    # Check for "SAVE AND CONTINUE" button
                    if 'save' in button_name.lower() and 'continue' in button_name.lower():
                        if 'save' in button_text and 'continue' in button_text:
                            self.logger.log(f"✅ VERIFIED: Blue 'Save and Continue' button found at coordinates ({x}, {y})")
                            return True
                    # Check for "NEXT" button
                    elif 'next' in button_name.lower():
                        if 'next' in button_text:
                            self.logger.log(f"✅ VERIFIED: Blue 'Next' button found at coordinates ({x}, {y})")
                            return True
                    # Generic blue button fallback
                    elif element_js.get('isBlue'):
                        self.logger.log(f"✅ VERIFIED: Blue button found at coordinates ({x}, {y}), but text doesn't match exactly")
                        return True
                    else:
                        self.logger.log(f"❌ Button found but doesn't appear to be blue or have matching text")
                        return False
                else:
                    self.logger.log(f"❌ Element at coordinates doesn't appear to be a button")
                    return False
            else:
                self.logger.log(f"❌ No element found at coordinates ({x}, {y})")
                return False
                
        except Exception as e:
            self.logger.log(f"Error verifying button at coordinates: {str(e)}", "error")
            return False
            
    def is_blue_save_continue_button_present(self, expected_coordinates=None):
        """
        Check if a blue 'Save and Continue' button is present at expected coordinates
        
        Args:
            expected_coordinates: Tuple of (x, y) coordinates to check, or None to check all known positions
            
        Returns:
            bool: True if button is found at expected coordinates, False otherwise
            tuple: The coordinates where button was found, or None if not found
        """
        self.logger.log("Checking for presence of blue 'Save and Continue' button")
        
        # If specific coordinates were provided, check only those
        if expected_coordinates:
            x, y = expected_coordinates
            is_present = self.verify_blue_button_at_coordinates(x, y)
            if is_present:
                self.logger.log(f"✅ SUCCESS: 'Save and Continue' button verified at expected coordinates ({x}, {y})")
                return True, (x, y)
            else:
                self.logger.log(f"❌ FAILED: 'Save and Continue' button not found at expected coordinates ({x}, {y})")
                return False, None
        
        # Otherwise check all known coordinates
        # Check predefined coordinates first
        for button_name, coords in self.common_buttons.items():
            if "SAVE AND CONTINUE" in button_name:
                x, y = coords
                self.logger.log(f"Checking predefined position for '{button_name}': ({x}, {y})")
                
                is_present = self.verify_blue_button_at_coordinates(x, y, button_name)
                if is_present:
                    self.logger.log(f"✅ SUCCESS: '{button_name}' button verified at coordinates ({x}, {y})")
                    return True, (x, y)
        
        # Then check cached coordinates
        for button_name, coords in self.coordinates_cache.items():
            if "SAVE AND CONTINUE" in button_name and coords:
                x, y = coords
                self.logger.log(f"Checking cached position for '{button_name}': ({x}, {y})")
                
                is_present = self.verify_blue_button_at_coordinates(x, y, button_name)
                if is_present:
                    self.logger.log(f"✅ SUCCESS: '{button_name}' button verified at coordinates ({x}, {y})")
                    return True, (x, y)
        
        self.logger.log("❌ FAILED: No 'Save and Continue' button found at any known position")
        return False, None
    
    def is_blue_next_button_present(self, expected_coordinates=None):
        """
        Check if a blue 'Next' button is present at expected coordinates
        
        Args:
            expected_coordinates: Tuple of (x, y) coordinates to check, or None to check all known positions
            
        Returns:
            bool: True if button is found at expected coordinates, False otherwise
            tuple: The coordinates where button was found, or None if not found
        """
        self.logger.log("Checking for presence of blue 'Next' button")
        
        # If specific coordinates were provided, check only those
        if expected_coordinates:
            x, y = expected_coordinates
            is_present = self.verify_blue_button_at_coordinates(x, y, "NEXT")
            if is_present:
                self.logger.log(f"✅ SUCCESS: 'Next' button verified at expected coordinates ({x}, {y})")
                return True, (x, y)
            else:
                self.logger.log(f"❌ FAILED: 'Next' button not found at expected coordinates ({x}, {y})")
                return False, None
        
        # Otherwise check all known coordinates
        # Check predefined coordinates first
        for button_name, coords in self.common_buttons.items():
            if "NEXT" in button_name:
                x, y = coords
                self.logger.log(f"Checking predefined position for '{button_name}': ({x}, {y})")
                
                is_present = self.verify_blue_button_at_coordinates(x, y, button_name)
                if is_present:
                    self.logger.log(f"✅ SUCCESS: '{button_name}' button verified at coordinates ({x}, {y})")
                    return True, (x, y)
        
        # Then check cached coordinates
        for button_name, coords in self.coordinates_cache.items():
            if "NEXT" in button_name and coords:
                x, y = coords
                self.logger.log(f"Checking cached position for '{button_name}': ({x}, {y})")
                
                is_present = self.verify_blue_button_at_coordinates(x, y, button_name)
                if is_present:
                    self.logger.log(f"✅ SUCCESS: '{button_name}' button verified at coordinates ({x}, {y})")
                    return True, (x, y)
        
        self.logger.log("❌ FAILED: No 'Next' button found at any known position")
        return False, None
    
    def click_button(self, button_name, force_vision=False, max_vision_attempts=2):
        """
        Click a button using the best available method
        
        Args:
            button_name: Name of the button to click
            force_vision: If True, use vision detection even if coordinates are available
            max_vision_attempts: Maximum number of vision detection attempts
            
        Returns:
            bool: True if button was clicked successfully, False otherwise
            tuple: The coordinates that were used, or None if unsuccessful
        """
        self.logger.log(f"Attempting to click {button_name} button")
        
        # Generate alternative button names to try
        alt_button_names = self.get_alternative_button_names(button_name)
        
        # Try direct coordinates first (unless force_vision is True)
        if not force_vision:
            # First try with the main button name
            coords = self.get_best_coordinates(button_name)
            if coords:
                x, y = coords
                if self.click_at_coordinates(x, y):
                    self.logger.log(f"Successfully clicked {button_name} at coordinates ({x}, {y})")
                    # Ensure these coordinates are in the cache
                    self.coordinates_cache[button_name] = (x, y)
                    self.save_coordinates()
                    return True, (x, y)
                else:
                    self.logger.log(f"Failed to click at cached coordinates for {button_name}")
            
            # If main button name failed, try alternatives
            for alt_name in alt_button_names:
                self.logger.log(f"Trying alternative button name: {alt_name}")
                alt_coords = self.get_best_coordinates(alt_name)
                if alt_coords:
                    x, y = alt_coords
                    if self.click_at_coordinates(x, y):
                        self.logger.log(f"Successfully clicked {alt_name} at coordinates ({x}, {y})")
                        # Save successful coordinates under both names for future use
                        self.coordinates_cache[button_name] = (x, y)
                        self.coordinates_cache[alt_name] = (x, y)
                        self.save_coordinates()
                        return True, (x, y)
                    else:
                        self.logger.log(f"Failed to click at cached coordinates for {alt_name}")
        
        # Fall back to vision detection
        self.logger.log(f"Using vision detection to find {button_name} button")
        
        # Custom prompt based on button name
        prompt = f"Locate the blue '{button_name}' button in the image. The button should be visible and clickable. Return only its exact screen coordinates in the format: x=..., y=.... Do not include any explanation or extra text. If the button is not visible or not found, return NOT_FOUND."
        
        # Try vision detection with smart scrolling
        for attempt in range(max_vision_attempts):
            self.logger.log(f"Vision detection attempt {attempt+1}/{max_vision_attempts}")
            
            # Adjust scrolling based on attempt number
            if attempt > 0:
                scroll_amount = 150 * attempt
                self.logger.log(f"Scrolling down by {scroll_amount}px before attempt {attempt+1}")
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(0.8)  # Wait for scroll to complete
            
            # Try button detection
            success = click_button_with_vision(
                driver=self.driver,
                prompt=prompt,
                image_path=f"ss/{button_name}_attempt{attempt}.png",
                wait_for_scroll=True
            )
            
            if success:
                # Try to extract the coordinates from the log
                coords = self.extract_coords_from_log()
                if coords:
                    x, y = coords
                    self.logger.log(f"Extracted coordinates from successful click: x={x}, y={y}")
                    
                    # Save to cache
                    self.coordinates_cache[button_name] = (x, y)
                    self.save_coordinates()
                    
                    return True, (x, y)
                
                # If we couldn't extract coordinates but click was successful
                return True, None
        
        self.logger.log(f"Failed to click {button_name} button after all attempts", "error")
        return False, None
    
    def try_submit_form(self):
        """
        Try to find and submit a form on the page - last resort when button clicking fails
        
        Returns:
            bool: True if form was submitted, False otherwise
        """
        self.logger.log("Attempting to submit form directly...")
        
        try:
            # Store original page state
            original_url = self.driver.current_url
            original_length = len(self.driver.page_source)
            
            # Method 1: Find form and submit directly
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            
            if forms:
                self.logger.log(f"Found {len(forms)} forms on the page")
                # Try to submit each form
                for i, form in enumerate(forms):
                    try:
                        self.logger.log(f"Attempting to submit form {i+1}/{len(forms)}")
                        # Try JavaScript submit
                        self.driver.execute_script("arguments[0].submit();", form)
                        time.sleep(1)
                        
                        # Check if page changed
                        if self._verify_page_changed(original_url, original_length):
                            self.logger.log("Form submission successful!")
                            return True
                    except Exception as e:
                        self.logger.log(f"Error submitting form {i+1}: {str(e)}", "warning")
            else:
                self.logger.log("No forms found on the page")
                
            # Method 2: Find submit or save buttons and click them
            button_selectors = [
                "button[type='submit']", 
                "input[type='submit']", 
                "button:contains('Save')", 
                "button:contains('Continue')",
                "a.btn", 
                ".btn-primary"
            ]
            
            for selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.log(f"Found {len(buttons)} buttons matching '{selector}'")
                    
                    for i, button in enumerate(buttons):
                        if button.is_displayed() and button.is_enabled():
                            self.logger.log(f"Clicking '{selector}' button {i+1}")
                            # Use JavaScript click for more reliability
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                            
                            # Check if page changed
                            if self._verify_page_changed(original_url, original_length):
                                self.logger.log(f"Button click on '{selector}' successful!")
                                return True
                except Exception as e:
                    self.logger.log(f"Error with selector '{selector}': {str(e)}", "warning")
            
            # Method 3: Try pressing Enter key on the active element
            try:
                active_element = self.driver.switch_to.active_element
                active_element.send_keys(Keys.RETURN)
                time.sleep(1)
                
                # Check if page changed
                if self._verify_page_changed(original_url, original_length):
                    self.logger.log("Form submission using Enter key successful!")
                    return True
            except Exception as e:
                self.logger.log(f"Error sending Enter key: {str(e)}", "warning")
                
            self.logger.log("All form submission attempts failed", "error")
            return False
            
        except Exception as e:
            self.logger.log(f"Error in form submission: {str(e)}", "error")
            return False 
#!/usr/bin/env python3
"""
Save and Continue/Next Button Clicker - Specialized tool for clicking Save and Continue or Next buttons

This tool implements multiple strategies to ensure the button is actually clicked
and the form is submitted successfully.

Usage:
    python click_with_verification.py [--url URL] [--wait SECONDS] [--button-type BUTTON_TYPE]
"""

import sys
import time
import argparse
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from click_manager import ClickManager
from logger import Logger

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Button Clicker with Verification")
    parser.add_argument("--url", help="URL to navigate to")
    parser.add_argument("--wait", type=int, default=3, help="Wait time in seconds before clicking (default: 3)")
    parser.add_argument("--quiet", action="store_true", help="Reduce console output")
    parser.add_argument("--no-logs", action="store_true", help="Don't write to log file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--screenshot", action="store_true", help="Save screenshots during each step")
    parser.add_argument("--button-type", choices=["save-continue", "next"], default="save-continue",
                       help="Type of button to click (default: save-continue)")
    
    return parser.parse_args()

def save_screenshot(driver, name):
    """Save a screenshot with the given name"""
    try:
        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)
        
        # Generate timestamped filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshots/{name}_{timestamp}.png"
        
        # Save screenshot
        driver.save_screenshot(filename)
        print(f"Saved screenshot: {filename}")
        return filename
    except Exception as e:
        print(f"Error saving screenshot: {str(e)}")
        return None

def main():
    """Main function for button clicking"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize logger
    logger = Logger(
        debug=args.debug, 
        console_output=not args.quiet,
        log_to_file=not args.no_logs
    )
    
    # Set up browser
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    # Create click manager
    click_manager = ClickManager(driver, wait)
    
    # Set button information based on button-type argument
    if args.button_type == "save-continue":
        button_name = "SAVE AND CONTINUE"
        button_display_name = "Save and Continue"
        check_method = click_manager.is_blue_save_continue_button_present
    else:  # next
        button_name = "NEXT"
        button_display_name = "Next"
        check_method = click_manager.is_blue_next_button_present
    
    try:
        # Navigate to URL if provided
        if args.url:
            logger.log(f"Navigating to {args.url}")
            driver.get(args.url)
            time.sleep(args.wait)  # Wait for page to load
        else:
            # If no URL, just open a blank page
            driver.get("about:blank")
            logger.log("No URL provided. Please navigate to the desired page manually.")
            input("Press Enter when ready to check for the button...")
        
        # Take screenshot before attempting to click
        if args.screenshot:
            save_screenshot(driver, "before_click")
        
        # Store initial page state
        initial_url = driver.current_url
        initial_title = driver.title
        logger.log(f"Initial page: '{initial_title}' at {initial_url}")
        
        # Strategy 1: Look for blue button using ClickManager
        logger.log(f"Strategy 1: Using click manager to find {button_display_name} button")
        is_present, found_coords = check_method()
        
        if is_present and found_coords:
            logger.log(f"Found {button_display_name} button at {found_coords}")
            
            # Try clicking the button using multiple methods
            success = click_manager.click_at_coordinates(*found_coords)
            
            if success:
                logger.log("Successfully clicked button using click manager")
                if args.screenshot:
                    save_screenshot(driver, "after_click_success")
            else:
                logger.log("Click manager failed to click the button", "warning")
                
                # Strategy 2: Look for specific button selectors
                logger.log("Strategy 2: Searching for button by CSS selectors")
                button_selectors = [
                    "button.btn-primary",
                    "input[type='submit']",
                    "button:contains('Save')",
                    "button:contains('Continue')",
                    "button:contains('Next')",
                    ".btn-primary",
                    ".save-button",
                    ".next-button",
                    "button.blue",
                    "a.btn-primary"
                ]
                
                button_clicked = False
                for selector in button_selectors:
                    try:
                        logger.log(f"Looking for buttons matching: {selector}")
                        buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for i, button in enumerate(buttons):
                            if not button.is_displayed() or not button.is_enabled():
                                continue
                                
                            try:
                                logger.log(f"Attempting to click {selector} button {i+1}")
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                                time.sleep(0.5)
                                
                                # Try JavaScript click
                                driver.execute_script("arguments[0].click();", button)
                                time.sleep(1)
                                
                                # Check if page changed
                                current_url = driver.current_url
                                if current_url != initial_url:
                                    logger.log(f"Button click successful! URL changed to {current_url}")
                                    button_clicked = True
                                    if args.screenshot:
                                        save_screenshot(driver, f"after_click_{selector.replace(':', '_')}")
                                    break
                            except Exception as e:
                                logger.log(f"Error clicking button: {str(e)}", "warning")
                        
                        if button_clicked:
                            break
                    except Exception as e:
                        logger.log(f"Error with selector {selector}: {str(e)}", "warning")
                
                if not button_clicked:
                    # Strategy 3: Try to submit the form directly
                    logger.log("Strategy 3: Attempting to submit form directly")
                    if click_manager.try_submit_form():
                        logger.log("Successfully submitted form directly")
                        if args.screenshot:
                            save_screenshot(driver, "after_form_submit")
                    else:
                        # Strategy 4: Use keyboard Tab and Enter
                        logger.log("Strategy 4: Using keyboard navigation")
                        
                        # First reset focus to body
                        driver.execute_script("document.body.focus();")
                        
                        # Try tab navigation to find the button
                        body = driver.find_element(By.TAG_NAME, "body")
                        
                        # Press Tab up to 20 times to navigate through focusable elements
                        for i in range(20):
                            # Take screenshot to see what's focused
                            if args.screenshot:
                                save_screenshot(driver, f"tab_navigation_{i}")
                                
                            # Send tab key
                            body.send_keys(Keys.TAB)
                            time.sleep(0.3)
                            
                            # Get the active (focused) element
                            active = driver.switch_to.active_element
                            
                            # Check if the focused element is a button or looks like a submit element
                            tag_name = active.tag_name.lower()
                            element_text = active.text.lower() if active.text else ""
                            element_type = active.get_attribute("type")
                            element_class = active.get_attribute("class") or ""
                            
                            logger.log(f"Focus on: {tag_name} '{element_text}' (type={element_type}, class={element_class})")
                            
                            # Check if this looks like our target button
                            is_target_button = False
                            if args.button_type == "save-continue":
                                is_target_button = (
                                    "save" in element_text and "continue" in element_text or
                                    tag_name == "button" and "blue" in element_class or
                                    tag_name == "button" and "primary" in element_class or
                                    element_type == "submit"
                                )
                            else:  # next button
                                is_target_button = (
                                    "next" in element_text or
                                    tag_name == "button" and "blue" in element_class or
                                    tag_name == "button" and "primary" in element_class or
                                    element_type == "submit"
                                )
                            
                            if is_target_button:
                                logger.log(f"Found possible target button: {tag_name} '{element_text}'")
                                
                                # Press Enter to click the button
                                try:
                                    active.send_keys(Keys.RETURN)
                                    time.sleep(1)
                                    
                                    # Check if page changed
                                    current_url = driver.current_url
                                    if current_url != initial_url:
                                        logger.log(f"Button click with keyboard successful! URL changed to {current_url}")
                                        if args.screenshot:
                                            save_screenshot(driver, "after_keyboard_enter")
                                        break
                                except Exception as e:
                                    logger.log(f"Error pressing Enter on element: {str(e)}", "warning")
        else:
            logger.log(f"Could not find {button_display_name} button", "error")
            if args.screenshot:
                save_screenshot(driver, "button_not_found")
            return 1
        
        # Take final screenshot to see the result
        if args.screenshot:
            save_screenshot(driver, "final_state")
            
        # Final verification - check if anything changed
        current_url = driver.current_url
        current_title = driver.title
        
        if current_url != initial_url or current_title != initial_title:
            logger.log(f"Page changed to: '{current_title}' at {current_url}")
            logger.log("Form submission appears successful!")
            return 0
        else:
            logger.log("No page change detected after all button click attempts", "warning")
            return 1
            
    except Exception as e:
        logger.log(f"Error during button click: {str(e)}", "error")
        if args.screenshot:
            save_screenshot(driver, "error_state")
        return 1
    
    finally:
        # Ask whether to close the browser
        if not args.quiet:
            user_input = input("Press Enter to close the browser, or type 'keep' to leave it open: ").lower().strip()
            if user_input != "keep":
                driver.quit()
                logger.log("Browser closed")
            else:
                logger.log("Browser left open. Remember to close it manually when done.")
        else:
            driver.quit()

if __name__ == "__main__":
    sys.exit(main()) 
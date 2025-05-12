#!/usr/bin/env python3
"""
Quick Button Clicker - Automated button clicking using coordinates and vision detection

Usage:
    python quick_click.py BUTTON_NAME [URL] [--no-maximize] [--headless]
    
Examples:
    python quick_click.py "SAVE AND CONTINUE"
    python quick_click.py "SAVE AND CONTINUE" https://www.mca.gov.in/content/mca/global/en/mca/llp-e-filling/Fillip.html
"""

import sys
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from click_manager import ClickManager

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Automatically click buttons using coordinates or vision detection")
    parser.add_argument("button_name", help="Name of the button to click (e.g., 'SAVE AND CONTINUE')")
    parser.add_argument("url", nargs="?", help="URL to navigate to (optional)")
    parser.add_argument("--no-maximize", action="store_true", help="Don't maximize browser window")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--force-vision", action="store_true", help="Force using vision detection even if coordinates exist")
    parser.add_argument("--attempts", type=int, default=2, help="Maximum vision detection attempts (default: 2)")
    parser.add_argument("--quiet", action="store_true", help="Reduce console output")
    
    return parser.parse_args()

def setup_webdriver(args):
    """Set up and configure webdriver based on arguments"""
    chrome_options = Options()
    
    if not args.no_maximize:
        chrome_options.add_argument("--start-maximized")
    
    if args.headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    return driver, wait

def log(message, quiet=False):
    """Print log message if not in quiet mode"""
    if not quiet:
        print(message)

def main():
    """Main function for quick button clicking"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up browser
    driver, wait = setup_webdriver(args)
    
    # Create click manager
    click_manager = ClickManager(driver, wait)
    
    try:
        # Navigate to URL if provided
        if args.url:
            log(f"Navigating to {args.url}", args.quiet)
            driver.get(args.url)
            time.sleep(2)  # Wait for page to load
        else:
            # If no URL, just open a blank page
            driver.get("about:blank")
            log("No URL provided. Please navigate to the desired page manually.", args.quiet)
            input("Press Enter when ready to click the button...")
        
        # Click the button
        log(f"Attempting to click '{args.button_name}' button...", args.quiet)
        success, coords = click_manager.click_button(
            button_name=args.button_name,
            force_vision=args.force_vision,
            max_vision_attempts=args.attempts
        )
        
        if success:
            log(f"Successfully clicked '{args.button_name}' button" + 
                (f" at coordinates {coords}" if coords else ""), args.quiet)
            
            # Wait to see the result
            time.sleep(3)
        else:
            log(f"Failed to click '{args.button_name}' button", args.quiet)
            return 1
        
        return 0  # Success
        
    except Exception as e:
        log(f"Error: {str(e)}", args.quiet)
        return 1
    
    finally:
        # Ask whether to close the browser
        close = input("Close the browser? (y/n): ").lower().strip()
        if close == 'y':
            driver.quit()
            log("Browser closed", args.quiet)
        else:
            log("Browser left open. Remember to close it manually when done.", args.quiet)

if __name__ == "__main__":
    sys.exit(main()) 
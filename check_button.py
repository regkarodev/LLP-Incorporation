#!/usr/bin/env python3
"""
Button Verification Tool - Check if a blue "Save and Continue" button exists at specific coordinates

Usage:
    python check_button.py [--url URL] [--x X] [--y Y]
    
Examples:
    python check_button.py
    python check_button.py --url https://www.mca.gov.in/content/mca/global/en/mca/llp-e-filling/Fillip.html
    python check_button.py --x 1281 --y 161
"""

import sys
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from click_manager import ClickManager
from logger import Logger

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Check if a blue 'Save and Continue' button exists at coordinates")
    parser.add_argument("--url", help="URL to navigate to")
    parser.add_argument("--x", type=int, help="X coordinate to check (defaults to checking all known positions)")
    parser.add_argument("--y", type=int, help="Y coordinate to check (required if --x is provided)")
    parser.add_argument("--delay", type=int, default=3, help="Delay in seconds before checking button (default: 3)")
    parser.add_argument("--quiet", action="store_true", help="Reduce console output")
    parser.add_argument("--no-logs", action="store_true", help="Don't write to log file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--clear-logs", action="store_true", help="Clear log file before starting")
    
    args = parser.parse_args()
    
    # If only one coordinate is provided, require the other
    if (args.x is not None and args.y is None) or (args.x is None and args.y is not None):
        parser.error("Both --x and --y must be provided together")
        
    return args

def log(message, quiet=False):
    """Print log message if not in quiet mode"""
    if not quiet:
        print(message)

def main():
    """Main function for button verification"""
    # Parse command line arguments
    args = parse_arguments()
    coordinates = (args.x, args.y) if args.x is not None and args.y is not None else None
    
    # Initialize logger
    logger_instance = Logger(
        debug=args.debug,
        console_output=not args.quiet,
        log_to_file=not args.no_logs
    )
    
    # Clear logs if requested
    if args.clear_logs and not args.no_logs:
        logger_instance.clear_log_file()
    
    # Set up browser
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    # Create click manager
    click_manager = ClickManager(driver, wait)
    
    try:
        # Navigate to URL if provided
        if args.url:
            log(f"Navigating to {args.url}", args.quiet)
            driver.get(args.url)
            time.sleep(args.delay)  # Wait for page to load
        else:
            # If no URL, just open a blank page
            driver.get("about:blank")
            log("No URL provided. Please navigate to the desired page manually.", args.quiet)
            input("Press Enter when ready to check for the button...")
        
        # Check for button presence
        log("Checking for blue 'Save and Continue' button...", args.quiet)
        is_present, found_coords = click_manager.is_blue_save_continue_button_present(coordinates)
        
        if is_present:
            log(f"✅ BUTTON FOUND: Blue 'Save and Continue' button found at coordinates {found_coords}", args.quiet)
            
            # Ask if user wants to click the button
            if not args.quiet:
                click_button = input("Do you want to click the button? (y/n): ").lower().strip()
                if click_button == 'y':
                    success = click_manager.click_at_coordinates(*found_coords)
                    if success:
                        log(f"Successfully clicked button at {found_coords}")
                    else:
                        log(f"Failed to click button at {found_coords}")
        else:
            log("❌ BUTTON NOT FOUND: No blue 'Save and Continue' button found at specified coordinates", args.quiet)
            
        # Give user time to see the results
        if not args.quiet:
            time.sleep(2)
        
        return 0 if is_present else 1
        
    except Exception as e:
        log(f"Error: {str(e)}", args.quiet)
        return 1
    
    finally:
        # Ask whether to close the browser
        if not args.quiet:
            close = input("Close the browser? (y/n): ").lower().strip()
            if close == 'y':
                driver.quit()
                log("Browser closed", args.quiet)
            else:
                log("Browser left open. Remember to close it manually when done.", args.quiet)
        else:
            driver.quit()

if __name__ == "__main__":
    sys.exit(main()) 
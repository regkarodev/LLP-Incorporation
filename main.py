import time
import os
import json
import argparse
import sys
from browser_manager import BrowserManager
from navigation_manager import NavigationManager
from click_manager import ClickManager
from logger import Logger

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="MCA Form Automation Tool")
    parser.add_argument("--profile", help="Path to Firefox profile (optional)")
    parser.add_argument("--quiet", action="store_true", help="Reduce console output")
    parser.add_argument("--no-logs", action="store_true", help="Don't write to log file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--clear-logs", action="store_true", help="Clear log file before starting")
    
    return parser.parse_args()

class MCAAutomation:
    """Main class for automating MCA form submission processes"""
    
    def __init__(self, profile_path=None, debug=False, console_output=True, log_to_file=True, clear_logs=False):
        """Initialize the MCA automation with necessary settings"""
        self.profile_path = profile_path or r"C:\Users\Admin\AppData\Local\Mozilla\Firefox\Profiles\coyayv9e.default"
        self.logger = Logger(
            debug=debug,
            console_output=console_output,
            log_to_file=log_to_file
        )
        
        # Clear logs if requested
        if clear_logs and log_to_file:
            self.logger.clear_log_file()
            
        self.browser_manager = None
        self.navigation_manager = None
        self.click_manager = None
        
    def initialize_managers(self):
        """Initialize all required managers for browser automation"""
        try:
            # Initialize browser manager
            self.browser_manager = BrowserManager(self.profile_path)
            if not self.browser_manager.start_browser():
                self.logger.log("Failed to start browser", "error")
                return False
                
            # Initialize navigation manager
            self.navigation_manager = NavigationManager(
                self.browser_manager.driver,
                self.browser_manager.wait
            )
            
            # Initialize click manager
            self.click_manager = ClickManager(
                self.browser_manager.driver,
                self.browser_manager.wait
            )
            
            return True
        except Exception as e:
            self.logger.log(f"Failed to initialize managers: {str(e)}", "error")
            return False

    def run(self):
        """Main execution method for MCA automation"""
        try:
            # Initialize all required managers
            if not self.initialize_managers():
                return False
                
            # Navigate to login page
            if not self.navigation_manager.navigate_to_login():
                return False
                
            # Wait for manual login
            self.logger.log("Please login manually. The session will be saved in your Firefox profile.")
            time.sleep(5)  # Wait for 5 seconds to allow manual login
            
            # Navigate to RUN LLP page
            if not self.navigation_manager.navigate_to_run_llp():
                return False
                
            # Fill form information
            if not self.complete_form_fields():
                return False
            
            # Click Save and Continue button using the click manager
            if not self.click_save_and_continue_button():
                return False
                
            # Wait for page to load
            time.sleep(2)
            
            # Click Next button if present
            if not self.click_next_button():
                self.logger.log("No Next button found or failed to click it. Continuing with process.", "warning")
            else:
                # If Next button was clicked successfully, wait for the next page to load
                time.sleep(2)
                
                # Fill registered office address details
                self.logger.log("Proceeding to fill registered office address details...")
                if not self.navigation_manager.fill_registered_office_address():
                    self.logger.log("Error filling registered office address details.", "error")
                    # Continue execution anyway since we might want to click Save and Continue even if some fields failed
                else:
                    self.logger.log("Successfully filled registered office address details.")
                
                # Fill contact details section
                self.logger.log("Proceeding to fill contact details section...")
                if not self.navigation_manager.fill_contact_details():
                    self.logger.log("Error filling contact details.", "error")
                    # Continue execution anyway since we might want to click Save and Continue even if some fields failed
                else:
                    self.logger.log("Successfully filled contact details section.")
                
                # Attempt to click Save and Continue button again on this page
                self.logger.log("Attempting to click Save and Continue after filling address and contact details...")
                self.click_save_and_continue_button()
                
                # Wait for page to load
                time.sleep(1)
                
                # Fill industrial activities description (add this section)
                self.logger.log("Continuing with form filling process...")
                
                # Scroll down to designated partner section and fill partner details
                self.logger.log("Proceeding to fill designated partner details...")
                if not self.navigation_manager.fill_designated_partner_details():
                    self.logger.log("Error filling designated partner details.", "error")
                    # Continue execution anyway since we might want to click Save and Continue
                else:
                    self.logger.log("Successfully filled designated partner details.")
                
                # Attempt to click Save and Continue button again after filling partner details
                self.logger.log("Attempting to click Save and Continue after filling partner details...")
                self.click_save_and_continue_button()
            
            # Verify that something happened after clicking (page changed)
            self.logger.log("Verifying page navigation after form submission...")
            time.sleep(2)  # Give page time to load
            
            # Add code to detect success based on your application's behavior
            # For example, check if a specific element appears that indicates success
            try:
                # Look for elements that would indicate successful submission
                # This is a placeholder - adjust to your specific application
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support import expected_conditions as EC
                
                # Wait for up to 10 seconds for a page element that indicates success
                success_indicators = [
                    "h1:contains('Success')",
                    ".success-message",
                    ".alert-success",
                    "form:not(.active)"  # If the form disappears or becomes inactive
                ]
                
                page_changed = False
                for indicator in success_indicators:
                    try:
                        elements = self.browser_manager.driver.find_elements(By.CSS_SELECTOR, indicator)
                        if elements:
                            self.logger.log(f"Found success indicator: {indicator}")
                            page_changed = True
                            break
                    except:
                        pass
                
                if not page_changed:
                    # Check if URL changed
                    title = self.browser_manager.driver.title
                    url = self.browser_manager.driver.current_url
                    self.logger.log(f"Current page: {title} at {url}")
            except Exception as e:
                self.logger.log(f"Error checking form submission result: {str(e)}", "warning")
            
            # Keep browser open for manual interaction
            self.logger.log("Form submitted - check the browser to confirm if it was successful.")
            self.wait_for_manual_close()
            
            return True
            
        except Exception as e:
            self.logger.log(f"Error in main execution: {str(e)}", "error")
            return False
        finally:
            if self.browser_manager:
                self.browser_manager.quit_browser()
    
    def complete_form_fields(self):
        """Complete all required form fields"""
        try:
            # Step 1: Scroll to form section
            if not self.navigation_manager.scroll_to_form_section():
                return False
                
            # Step 2: Select 'Yes' for name approval
            if not self.navigation_manager.select_name_approved_yes():
                return False
                
            # Step 3: Fill SRN of RUN-LLP
            if not self.navigation_manager.fill_srn_of_run_llp('M28055632'):
                return False
                
            # Step 4: Select 'New Incorporation' for type of incorporation
            if not self.navigation_manager.select_type_of_incorporation_new():
                return False
                
            # Step 5: Scroll to '(a) Proposed or approved name' field
            if not self.navigation_manager.scroll_to_proposed_name_field():
                return False
                
            return True
        except Exception as e:
            self.logger.log(f"Error completing form fields: {str(e)}", "error")
            return False
    
    def wait_for_manual_close(self):
        """Wait for manual closure or user input"""
        self.logger.log("Press Ctrl+C to close the browser when ready.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.log("Received close signal. Closing browser...")
    
    def click_save_and_continue_button(self):
        """Click the Save and Continue button using multiple strategies"""
        self.logger.log("Attempting to click 'SAVE AND CONTINUE' button...")
        success, coords = self.click_manager.click_button("SAVE AND CONTINUE")
        
        if success:
            self.logger.log(f"Successfully clicked Save and Continue button" + 
                          (f" at coordinates {coords}" if coords else ""))
            return True
        else:
            # If direct click failed, try alternative approach with form submission
            self.logger.log("Direct button click failed, trying form submission...", "warning")
            if self.click_manager.try_submit_form():
                self.logger.log("Successfully submitted form using alternative method")
                return True
            else:
                self.logger.log("Failed to submit form with all methods", "error")
                return False
                
    def click_next_button(self):
        """Click the Next button using multiple strategies"""
        self.logger.log("Attempting to click 'NEXT' button...")
        success, coords = self.click_manager.click_button("NEXT")
        
        if success:
            self.logger.log(f"Successfully clicked Next button" + 
                          (f" at coordinates {coords}" if coords else ""))
            return True
        else:
            # If direct click failed, try alternative approach with form submission
            self.logger.log("Direct button click failed, trying form submission...", "warning")
            if self.click_manager.try_submit_form():
                self.logger.log("Successfully submitted form using alternative method")
                return True
            else:
                self.logger.log("Failed to click Next button with all methods", "error")
                return False

if __name__ == "__main__":
    args = parse_arguments()
    
    automation = MCAAutomation(
        profile_path=args.profile,
        debug=args.debug,
        console_output=not args.quiet,
        log_to_file=not args.no_logs,
        clear_logs=args.clear_logs
    )
    
    success = automation.run()
    sys.exit(0 if success else 1)
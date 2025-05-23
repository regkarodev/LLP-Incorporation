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
    
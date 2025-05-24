import time
import os
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import function1, attachment_upload, json, document_upload_file, last_upload
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException


# Global driver variable
driver = None

def setup_driver(webdriver_instance):
    """Set up the driver for this module"""
    global driver
    driver = webdriver_instance
    return driver

def log_terminal_output(message, level="info"):
    """Helper function for logging"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level.upper()}] {message}")

def log_message(message):
    """Simple logging function"""
    print(f"[AUTOMATE1] {message}")

def scroll_to_middle(driver, element):
    """Scroll element to middle of viewport"""
    try:
        # Get viewport height
        viewport_height = driver.execute_script("return window.innerHeight")
        
        # Get element's Y position
        element_y = element.location['y']
        
        # Calculate scroll position to center the element
        scroll_position = element_y - (viewport_height / 2)
        
        # Store current scroll position
        current_scroll = driver.execute_script("return window.pageYOffset;")
        
        # Only scroll if the element is not already in view
        if abs(current_scroll - scroll_position) > 100:  # Threshold of 100 pixels
            # Scroll to position
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(0.5)  # Small delay to allow scroll to complete
            
            # Prevent any automatic scrolling
            driver.execute_script("""
                window.onscroll = function() {
                    if (window.scrollY !== arguments[0]) {
                        window.scrollTo(0, arguments[0]);
                    }
                };
            """, scroll_position)
    except Exception as e:
        print(f"Error scrolling to element: {e}")

def check_driver_session():
    """Check if the driver session is still active"""
    global driver
    try:
        # Try a simple command to check if session is alive
        driver.current_url
        return True
    except (WebDriverException, InvalidSessionIdException):
        return False

def ensure_driver_session():
    """Ensure driver session is active, reconnect if necessary"""
    global driver
    if not check_driver_session():
        print("Browser session lost. Attempting to reconnect...")
        try:
            # Reinitialize the driver
            from selenium import webdriver
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from webdriver_manager.firefox import GeckoDriverManager
            
            # Load config for browser settings
            with open("config.json", "r") as f:
                config = json.load(f)
            
            # Set up Firefox options
            options = FirefoxOptions()
            options.add_argument("--start-maximized")
            
            # Initialize new driver
            driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options
            )
            
            # Navigate back to the form
            driver.get(config.get('fillip_url', ''))
            print("Successfully reconnected to browser session")
            return True
        except Exception as e:
            print(f"Failed to reconnect: {e}")
            return False
    return True

def click_element(css_selector):
    """Click an element using CSS selector"""
    global driver
    try:
        if not ensure_driver_session():
            raise Exception("Could not establish browser session")
            
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        function1.click_element(driver=driver, css_selector=css_selector)
    except Exception as e:
        print(f"Error clicking element: {e}")
        raise

def send_text(css_selector, keys):
    """Send text to an element using CSS selector"""
    global driver
    try:
        if not ensure_driver_session():
            raise Exception("Could not establish browser session")
            
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        function1.send_text(driver=driver, css_selector=css_selector, keys=keys)
    except Exception as e:
        print(f"Error sending text: {e}")
        raise

def upload_documents(documents=None):
    """
    Upload required documents
    Args:
        documents: Dictionary mapping document types to file paths
    Returns:
        bool: Success status
    """
    global driver
    if documents is None:
        documents = get_default_documents()
    
    log_message("Starting document upload process...")
    
    try:
        for doc_type, file_path in documents.items():
            log_message(f"Uploading {doc_type}...")
            
            # Find the appropriate upload button for this document type
            button_xpath = f"//button[contains(text(), '{doc_type}') or contains(@aria-label, '{doc_type}')]"
            
            # Attempt to upload the document
            success = function1.auto_upload_file_xpath(driver, button_xpath, file_path)
            
            if not success:
                log_message(f"Failed to upload {doc_type}")
                return False
            
            # Wait a moment between uploads
            time.sleep(2)
        
        log_message("All documents uploaded successfully")
        return True
        
    except Exception as e:
        log_message(f"Error uploading documents: {e}")
        return False

def submit_application():
    """
    Submit the LLP application
    Returns:
        bool: Success status
    """
    global driver
    log_message("Preparing to submit application...")
    
    try:
        # Look for and click the submit button
        submit_button_xpaths = [
            "//button[contains(text(), 'Submit') or contains(@value, 'Submit')]",
            "//input[@type='submit']",
            "//button[@type='submit']"
        ]
        
        for xpath in submit_button_xpaths:
            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                function1.click_element(driver, xpath=xpath)
                log_message("Submit button clicked")
                break
            except:
                continue
        
        # Wait for confirmation message
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'success') or contains(text(), 'submitted')]"))
            )
            log_message("Application submitted successfully!")
            return True
        except:
            log_message("Could not confirm successful submission")
            return False
            
    except Exception as e:
        log_message(f"Error submitting application: {e}")
        return False

def get_default_documents():
    """Return default document paths for testing"""
    docs_dir = os.path.join(os.getcwd(), "documents")
    return {
        "ID Proof": os.path.join(docs_dir, "id_proof.pdf"),
        "Address Proof": os.path.join(docs_dir, "address_proof.pdf"),
        "Certificate": os.path.join(docs_dir, "certificate.pdf")
    }

def run_llp_form_sequence(webdriver_instance=None):
    """Run the full LLP form filling sequence"""
    global driver
    
    # Set driver if provided
    if webdriver_instance:
        driver = webdriver_instance
    
    # Make sure driver is initialized
    if not driver:
        raise ValueError("Driver is not initialized. Call setup_driver first or provide a driver instance.")
    
    try:
        # Load the JSON config
        with open("config_data.json", "r") as f:
            config_data = json.load(f)

        with open('config.json', 'r') as f:
            config_selectors = json.load(f)

        # Begin the form sequence
        print("[AUTOMATE1] Starting LLP form sequence...")
        
        # Add periodic session checks
        check_interval = 10  # Check every 10 operations
        operation_count = 0
        
        # Registrar of Companies
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy-panel1626772568950-guideradiobutton__-1_widget')

        # Service Request Number
        send_text('#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy-panel1626772568950-guidetextbox_copy___widget', config_data['form_data']['fields']['Service Request Number'])

        # Type of incorporation
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy-panel1626772568950-guideradiobutton_1069538009__-1_widget')

        # SAVE AND CONTINUE BUTTON 
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy_copy-mca_button___widget')

        # OK POP_UP BUTTON
        time.sleep(2)
        click_element('#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')

        # NEXT BUTTON
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel-panel_copy_copy_copy_1792429032-mca_button___widget')

        # *Address Line I
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_copy_11___widget', config_data['form_data']['fields']['Address Line I'])

        # *Address Line II
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_copy_11_635080626___widget', config_data['form_data']['fields']['Address Line II'])

        # *PIN CODE
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_copy_11_1386963699___widget', config_data['form_data']['fields']['PIN CODE'])

        # *Area/ Locality
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_9527960___widget')
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_9527960___widget', config_data['form_data']['fields']['Area/Locality1'])

        # *Longitude
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_1045433___widget', config_data['form_data']['fields']['Longitude'])

        # *Latitude
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_1045433_1076286455___widget', config_data['form_data']['fields']['Latitude'])

        # *Jurisdiction of Police Station
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_copy___widget', config_data['form_data']['fields']['Jurisdiction of Police Station'])

        # (b) Contact Details

        # Phone (with STD/ISD code)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_417418999-panel_2000768201_cop-phonestdisdbox___widget', config_data['form_data']['fields']['Phone (with STD/ISD code)'])

        # *Mobile No.
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_417418999-panel_2000768201_cop-guidetextbox_copy_11_211671462___widget', config_data['form_data']['fields']['Mobile No'])

        # Fax
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_417418999-panel_2000768201_cop-guidenumericbox_1010___widget', config_data['form_data']['fields']['Fax'])

        # *Email ID
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_417418999-panel_2000768201_cop-guidetextbox_copy_11___widget', config_data['form_data']['fields']['Email ID'])

        # partnership and my membership number
        send_text('#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox_1809173783___widget', config_data['form_data']['fields']['partnership and my membership number'])

        ## (c) Attachments

        # Wait before uploading

        # Upload files using the loaded config
        time.sleep(2)
        attachment_upload.handle_file_uploads(driver, config_data)
        time.sleep(2)
        attachment_upload.handle_file_uploads(driver, config_data)
        
        #(d) *Name of the office of Registrar in whose jurisdiction the proposed LLP is to be registered
        
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_2015234307-guidedropdownlist_co___widget', config_data['form_data']['fields']['Name of the office of Registrar'])

        # 5 Total number of designated partners and partners of the LLP

        # *Individuals Having valid DIN/DPIN
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629350115276-tableItem1629350115279___widget', config_data['form_data']['fields']['Individuals Having valid DIN/DPIN'])

        # *Individuals Not having valid DIN/DPIN
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629350123645-tableItem1629350123648___widget', config_data['form_data']['fields']['Individuals Not having valid DIN/DPIN'])

        # *Body corporates and their nominees Having valid DIN/DPIN
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629350126976-tableItem1629350126979___widget', config_data['form_data']['fields']['Body corporates and their nominees Having valid DIN/DPIN'])

        # *Body corporates and their nominee not having valid DIN/DPIN
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629350131849-tableItem1629350131852___widget', config_data['form_data']['fields']['Body corporates and their nominee not having valid DIN/DPIN'])

        # *Individuals Having valid DIN/DPIN
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629350148437-tableItem1629350148441___widget', config_data['form_data']['fields']['Individuals Having valid DIN/DPIN1'])

        # *Individuals Not having valid DIN/DPIN
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629356006750-tableItem1629356006753___widget', config_data['form_data']['fields']['Individuals Not having valid DIN/DPIN1'])

        # *Body corporates and their nominees Having valid DIN/DPIN
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629356019361-tableItem1629356019364___widget', config_data['form_data']['fields']['Body corporates and their nominees Having valid DIN/DPIN1'])

        # *Body corporates and their nominee not having valid DIN/DPIN
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629356041275-tableItem1629356041278___widget', config_data['form_data']['fields']['Body corporates and their nominee not having valid DIN/DPIN1'])



        # (A) Particulars of individual designated partners having DIN/DPIN
        # Support for multiple partners from config_data and config selectors
        
        # Get the number of partners to fill
        num_partners = int(config_data['form_data']['fields'].get('Individuals Having valid DIN/DPIN', 0))
        
        if num_partners < 1:
            print('No designated partners with DIN/DPIN to fill.')
        else:
            if num_partners > 5:
                print('Reached the limit of 5 designated partners. Only filling 5.')
                num_partners = 5
            
            # Load selectors from config.json
            try:
                with open('config.json', 'r') as f:
                    config_selectors = json.load(f)
                selectors_list = config_selectors['Basic details']['form1']
            except:
                print("Error loading config.json for selectors")
                selectors_list = []
            
            # Get partner data (check multiple locations)
            designated_partners = config_data['form_data'].get('designated_partners', None)
            if not designated_partners:
                # Check under options
                designated_partners = config_data['form_data'].get('options', {}).get('designated_partners', None)
            
            if not designated_partners:
                # Fallback: use the same data for all
                designated_partners = [config_data['form_data']['fields']] * num_partners
            
            # Fill each partner's subform
            for idx in range(num_partners):
                print(f'Filling subform for designated partner {idx+1}')
                
                # Get partner data and selectors for this index
                partner = designated_partners[idx] if idx < len(designated_partners) else designated_partners[0]
                filled_successfully = False
                
                # First try: Use selectors from config.json (only for partner 1)
                if selectors_list and idx == 0:
                    selectors = selectors_list[idx]
                    
                    # Check if this is a dynamic GUID selector that might not work
                    first_selector = list(selectors.values())[0] if selectors else ""
                    if idx > 0 and "GUID" in first_selector:
                        print(f"Note: Partner {idx+1} uses dynamic GUID selectors which may not match the page")
                    
                    fields_filled = 0
                    for field, selector in selectors.items():
                        # Map field names...
                        field_mapping = {
                            'Designated partner identification number (DIN/DPIN)': 'Designated partner identification number (DIN/DPIN)',
                            'resident_india': 'Whether resident of India',
                            'form_of_contribution': 'Form of contribution',
                            'monetary_value_of_contribution': 'Monetary value of contribution (in INR) (in figures)',
                            'number_of_llp': 'Number of LLP(s) in which he/ she is a partner',
                            'number_of_company': 'Number of company(s) in which he/ she is a director',
                            'value': None,
                            "If 'Other than cash' selected, please specify": "If 'Other than cash' selected, please specify"
                        }
                        actual_field = field_mapping.get(field, field)
                        if actual_field is None:
                            continue
                        value = partner.get(actual_field)
                        if value is not None:
                            try:
                                if field == 'resident_india':
                                    if str(value).lower() == 'yes':
                                        element = driver.find_element(By.CSS_SELECTOR, selector)
                                        click_element(selector)
                                    time.sleep(0.5)
                                elif field == 'form_of_contribution':
                                    # Always use XPath fallback for dropdown with debugging
                                    position = idx + 1
                                    try:
                                        # Debug: Check what elements exist
                                        all_contribution_elements = driver.find_elements(By.XPATH, "//*[@aria-label='Form of contribution']")
                                        print(f"Debug: Found {len(all_contribution_elements)} elements with aria-label='Form of contribution'")
                                        for i, el in enumerate(all_contribution_elements):
                                            print(f"  Element {i+1}: tag={el.tag_name}, type={el.get_attribute('type')}, displayed={el.is_displayed()}")
                                        
                                        contribution_element = None
                                        
                                        # Try different XPath patterns
                                        xpath_patterns = [
                                            f"(//input[@aria-label='Form of contribution'])[{position}]",
                                            f"(//select[@aria-label='Form of contribution'])[{position}]", 
                                            f"(//*[@aria-label='Form of contribution'])[{position}]"
                                        ]
                                        
                                        for xpath in xpath_patterns:
                                            try:
                                                contribution_element = driver.find_element(By.XPATH, xpath)
                                                print(f"Found contribution element using: {xpath}")
                                                break
                                            except:
                                                continue
                                        
                                        if not contribution_element:
                                            raise Exception("Could not find Form of contribution element with any pattern")
                                        
                                        # Handle different element types
                                        if contribution_element.tag_name.lower() == 'select':
                                            # Use Selenium's Select for native dropdowns
                                            from selenium.webdriver.support.ui import Select
                                            select = Select(contribution_element)
                                            select.select_by_visible_text(value)
                                            print(f"Selected contribution type using Select: {value}")
                                        else:
                                            # Handle input or custom dropdown
                                            contribution_element.click()
                                            time.sleep(0.5)
                                            try:
                                                option_xpath = f"//li[contains(text(), '{value}') or contains(., '{value}')]"
                                                option = driver.find_element(By.XPATH, option_xpath)
                                                option.click()
                                                print(f"Selected contribution type for partner {position}: {value}")
                                            except Exception as e:
                                                contribution_element.send_keys(value)
                                                print(f"Fallback: sent keys for contribution type for partner {position}: {value}")
                                        
                                        if str(value).lower() == 'other than cash':
                                            spec_value = partner.get("If 'Other than cash' selected, please specify", '')
                                            if spec_value:
                                                try:
                                                    spec_element = driver.find_element(By.XPATH, f"(//*[contains(@aria-label, 'please specify')])[{position}]")
                                                    spec_element.clear()
                                                    spec_element.send_keys(spec_value)
                                                    print(f"Filled 'Other than cash' specification for partner {position}")
                                                except Exception as e:
                                                    print(f"Warning: Could not fill 'Other than cash' specification: {str(e)}")
                                    except Exception as e:
                                        print(f"Could not fill 'Form of contribution' for partner {position}: {str(e)}")
                                else:
                                    element = driver.find_element(By.CSS_SELECTOR, selector)
                                    send_text(selector, str(value))
                                fields_filled += 1
                            except Exception as e:
                                print(f"Warning: Could not fill field '{field}' with selector '{selector}': {str(e)}")
                                continue
                    
                    if fields_filled > 0:
                        filled_successfully = True
                        print(f"Successfully filled {fields_filled} fields for partner {idx+1}")
                
                # Always use XPath fallback for all partners (including partner 1 if config selectors fail)
                if not filled_successfully:
                    print(f"Using XPath fallback for partner {idx+1}")
                    try:
                        position = idx + 1
                        # DIN/DPIN
                        try:
                            din_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Designated partner identification number (DIN/DPIN)'])[{position}]")
                            din_element.clear()
                            din_element.send_keys(partner.get('Designated partner identification number (DIN/DPIN)', ''))
                            print(f"Filled DIN for partner {position}")
                        except Exception as e:
                            print(f"Warning: Could not fill DIN for partner {position}: {str(e)}")
                        # Click resident radio if available
                        if partner.get('Whether resident of India', '').lower() == 'yes':
                            try:
                                resident_radio = driver.find_element(By.XPATH, f"(//input[@aria-label='Whether resident of India'])[{position}]")
                                resident_radio.click()
                                print(f"Selected resident of India for partner {position}")
                            except:
                                try:
                                    resident_radio = driver.find_element(By.XPATH, f"(//*[contains(@aria-label, 'resident of India')])[{position}]")
                                    resident_radio.click()
                                    print(f"Selected resident of India for partner {position}")
                                except Exception as e:
                                    print(f"Warning: Could not select resident radio for partner {position}: {str(e)}")
                        # Form of contribution
                        try:
                            # Debug: Check what elements exist
                            all_contribution_elements = driver.find_elements(By.XPATH, "//*[@aria-label='Form of contribution']")
                            print(f"Debug: Found {len(all_contribution_elements)} elements with aria-label='Form of contribution'")
                            for i, el in enumerate(all_contribution_elements):
                                print(f"  Element {i+1}: tag={el.tag_name}, type={el.get_attribute('type')}, displayed={el.is_displayed()}")
                            
                            contribution_value = partner.get('Form of contribution', '')
                            contribution_element = None
                            
                            # Try different XPath patterns
                            xpath_patterns = [
                                f"(//input[@aria-label='Form of contribution'])[{position}]",
                                f"(//select[@aria-label='Form of contribution'])[{position}]", 
                                f"(//*[@aria-label='Form of contribution'])[{position}]"
                            ]
                            
                            for xpath in xpath_patterns:
                                try:
                                    contribution_element = driver.find_element(By.XPATH, xpath)
                                    print(f"Found contribution element using: {xpath}")
                                    break
                                except:
                                    continue
                            
                            if not contribution_element:
                                raise Exception("Could not find Form of contribution element with any pattern")
                            
                            # Handle different element types
                            if contribution_element.tag_name.lower() == 'select':
                                # Use Selenium's Select for native dropdowns
                                from selenium.webdriver.support.ui import Select
                                select = Select(contribution_element)
                                select.select_by_visible_text(contribution_value)
                                print(f"Selected contribution type using Select: {contribution_value}")
                            else:
                                # Handle input or custom dropdown
                                contribution_element.click()
                                time.sleep(0.5)
                                try:
                                    # Try to find and click option
                                    option_xpath = f"//li[contains(text(), '{contribution_value}') or contains(., '{contribution_value}')]"
                                    option = driver.find_element(By.XPATH, option_xpath)
                                    option.click()
                                    print(f"Selected contribution type for partner {position}: {contribution_value}")
                                except Exception as e:
                                    # Fallback to send_keys
                                    contribution_element.send_keys(contribution_value)
                                    print(f"Fallback: sent keys for contribution type for partner {position}: {contribution_value}")
                            
                            # Handle "Other than cash" specification
                            if contribution_value.lower() == 'other than cash':
                                try:
                                    spec_element = driver.find_element(By.XPATH, f"(//*[contains(@aria-label, 'please specify')])[{position}]")
                                    spec_element.clear()
                                    spec_element.send_keys(partner.get("If 'Other than cash' selected, please specify", ''))
                                    print(f"Filled 'Other than cash' specification for partner {position}")
                                except Exception as e:
                                    print(f"Warning: Could not fill 'Other than cash' specification: {str(e)}")
                        except Exception as e:
                            print(f"Warning: Could not fill contribution for partner {position}: {str(e)}")
                        # Monetary value
                        try:
                            monetary_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Monetary value of contribution (in INR) (in figures)'])[{position}]")
                            monetary_element.clear()
                            monetary_element.send_keys(partner.get('Monetary value of contribution (in INR) (in figures)', ''))
                            print(f"Filled monetary value for partner {position}")
                        except Exception as e:
                            print(f"Warning: Could not fill monetary value for partner {position}: {str(e)}")
                        # Number of LLPs
                        try:
                            llp_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Number of LLP(s) in which he/ she is a partner'])[{position}]")
                            llp_element.clear()
                            llp_element.send_keys(partner.get('Number of LLP(s) in which he/ she is a partner', ''))
                            print(f"Filled LLP count for partner {position}")
                        except Exception as e:
                            print(f"Warning: Could not fill LLP count for partner {position}: {str(e)}")
                        # Number of companies
                        try:
                            company_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Number of company(s) in which he/ she is a director'])[{position}]")
                            company_element.clear()
                            company_element.send_keys(partner.get('Number of company(s) in which he/ she is a director', ''))
                            print(f"Filled company count for partner {position}")
                        except Exception as e:
                            print(f"Warning: Could not fill company count for partner {position}: {str(e)}")
                    except Exception as e:
                        print(f"Error with XPath fallback for partner {idx+1}: {str(e)}")
                        print(f"This usually means the form structure is different than expected.")
                        print(f"Please check that {num_partners} subforms are actually visible on the page.")
                
                time.sleep(1)  # Wait between partners



        # (B) Particulars of individual designated partners not having DIN/DPIN
        # (i) Basic details of Designated partner

        # First Name
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11___widget', config_data['form_data']['fields']['First Name'])

        # Middle Name
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_1103730967___widget', config_data['form_data']['fields']['Middle Name'])
        
        # Surname
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_1562614891___widget', config_data['form_data']['fields']['Surname'])

        # Father's First Name
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_2008497050___widget', config_data['form_data']['fields']['Father Name'])

        # Father's Middle Name
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_97181591___widget', config_data['form_data']['fields']['Father Middle Name'])

        # Father's Surname
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_489985667___widget', config_data['form_data']['fields']['Father Surname'])

        # Gender
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_1126939658___widget', config_data['form_data']['fields']['Gender'])

        # Fill DOB
        # Example usage:
        date_field_id = "guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidedatepicker___widget"
        your_date = config_data['form_data']['fields']['Date of Birth']
        function1.set_date_field(driver, date_field_id, your_date)

        # Nationality
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_905293595___widget')
        time.sleep(2)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_905293595___widget > option:nth-child(102)', keys=config_data['form_data']['fields']['Nationality'])

        # Whether resident of India
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidecheckbox_copy_c_1044176976__-1_widget')

        # Income-tax PAN/Passport number
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guideradiobutton_290__-1_widget')

        # Income-tax PAN/Passport number details
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-panel_130595931_copy-guidetextbox_copy_11___widget', config_data['form_data']['fields']['Income-tax PAN/Passport number details'])

        time.sleep(3)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-panel_130595931_copy-mca_button___widget')

        # Place of Birth (State)
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_1516867585___widget')
        time.sleep(2)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_1516867585___widget > option:nth-child(11)', config_data['form_data']['fields']['Place of Birth (State)'])

        # Place of Birth (District)
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_1713202154___widget')
        time.sleep(2)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_1713202154___widget > option:nth-child(603)', config_data['form_data']['fields']['Place of Birth (District)'])

        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidecheckbox_copy_c__-1_widget')

        # Occupation type
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_2129385629___widget')
        time.sleep(2)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_2129385629___widget > option:nth-child(4)', config_data['form_data']['fields']['Occupation type'])

        # Area of Occupation
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_1003108991___widget')
        time.sleep(2)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_1003108991___widget > option:nth-child(5)', config_data['form_data']['fields']['Area of Occupation'])

        # Educational qualification
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_164495912___widget')
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_164495912___widget > option:nth-child(5)')

        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetelephone_copy___widget', config_data['form_data']['fields']['Mobile No'])
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_2056351___widget', config_data['form_data']['fields']['Email ID Designated partner'])

        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox___widget', config_data['form_data']['fields']['Designated partner Address Line I'])
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy___widget', config_data['form_data']['fields']['Designated partner Address Line II'])

        # Country
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidedropdownlist___widget')
        time.sleep(2)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidedropdownlist___widget > option:nth-child(102)', config_data['form_data']['fields']['Designated partner country'])

        # Pin code / Zip Code
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy_1737891757___widget', config_data['form_data']['fields']['Designated partner Pin code / Zip Code'])

        # Area/ Locality
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidedropdownlist_1592911853___widget')
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidedropdownlist_1592911853___widget > option:nth-child(10)', config_data['form_data']['fields']['Area/ Locality2'])

        # Jurisdiction of Police Station
        time.sleep(2)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_1308366___widget', config_data['form_data']['fields']['Designated partner Jurisdiction of Police Station'])

        # Phone (with STD/ISD code)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy_165380706___widget', config_data['form_data']['fields']['Designated partner Phone (with STD/ISD code)'])

        # Whether present residential address same as permanent residential address
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guideradiobutton__-1_widget')

        # Identity Proof
        time.sleep(2)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1688891306-guidedropdownlist___widget', config_data['form_data']['fields']['Identity Proof'])

        # Residential Proof
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1688891306-guidedropdownlist_54267595___widget', config_data['form_data']['fields']['Residential Proof'])

        # Identity Proof No.
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1688891306-guidetextbox___widget', config_data['form_data']['fields']['Identity Proof No.'])

        # Residential Proof No.
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1688891306-guidetextbox_1665947846___widget', config_data['form_data']['fields']['Residential Proof No.'])

        # Submit a copy of the proof of identity and proof of address
        # Wait before uploading
        time.sleep(2)

        # Upload files using the loaded config
        time.sleep(2)
        document_upload_file.handle_file_uploads(driver, config_data)
        time.sleep(2)
        document_upload_file.handle_file_uploads(driver, config_data)

        # Form of contribution
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_254891280-guidedropdownlist___widget', config_data['form_data']['fields']['Form of contribution1'])

        # Monetary value of contribution (in INR.) (in figures)
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_254891280-guidetextbox_copy___widget', config_data['form_data']['fields']['Monetary value of contribution (in INR.) (in figures)'])

        # Number of LLP(s) in which he/ she is a partner
        # send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_254891280-guidetextbox_copy_1389782663___widget', 'two hundred')

        # Number of LLP(s) in which he/ she is a partner
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_254891280-guidetextbox_copy_1672616692___widget', config_data['form_data']['fields']['Number of LLP(s) in which he/ she is a partner1'])

        # Number of company(s) in which he/ she is a director
        send_text('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_254891280-guidetextbox_copy_709870004___widget', config_data['form_data']['fields']['Number of company(s) in which he/ she is a director1'])

        # SAVE BUTTON
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel_copy_copy_copy-mca_button_copy___widget')

        # POPUP - OK BUTTON
        time.sleep(2)
        click_element('#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')

        # NEXT BUTTON
        click_element('#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel_copy_copy_copy-mca_button___widget')

        # *Area code
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel-guidetextbox___widget', config_data['form_data']['fields']['PAN Area code'])
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel-guidetextbox_copy___widget', config_data['form_data']['fields']['PAN Area code1'])
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel-guidetextbox_copy_2031803169___widget', config_data['form_data']['fields']['PAN Area code2'])

        # *AO type
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_912586437-guidetextbox___widget', config_data['form_data']['fields']['PAN AO type'])

        # *Range code
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_450718701-guidetextbox___widget', config_data['form_data']['fields']['PAN Range code'])
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_450718701-guidetextbox_copy___widget', config_data['form_data']['fields']['PAN Range code1'])

        # *AO No.
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_912586437_1323045745-guidetextbox___widget', config_data['form_data']['fields']['PAN AO No.'])

        # *Area code
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel-guidetextbox___widget', config_data['form_data']['fields']['TAN Area code1'])
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel-guidetextbox_copy___widget', config_data['form_data']['fields']['TAN Area code2'])
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel-guidetextbox_copy_2031803169___widget', config_data['form_data']['fields']['TAN Area code3'])

        # *AO type
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_912586437-guidetextbox___widget', config_data['form_data']['fields']['TAN AO type1'])

        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_912586437-guidetextbox_copy___widget', config_data['form_data']['fields']['TAN AO type2'])

        # *Range code
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_450718701-guidetextbox___widget', config_data['form_data']['fields']['TAN Range code'])
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_450718701-guidetextbox_copy___widget', config_data['form_data']['fields']['TAN Range code1'])

        # *AO No.
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_912586437_1323045745-guidetextbox___widget', config_data['form_data']['fields']['TAN AO No'])

        # Income Source - fixing the potential issue with this line
        time.sleep(2)
        send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-guidetextbox_2064455___widget', config_data['form_data']['fields']['Income Source'])

        # SAVE BUTTON
        time.sleep(2)
        click_element('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy_copy-mca_button_copy___widget')

        # POPUP - OK BUTTON
        time.sleep(2)
        click_element('#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')

        # NEXT BUTTON
        click_element('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy_copy-mca_button___widget')

        # Upload files using the loaded config
        time.sleep(2)
        last_upload.handle_file_uploads(driver, config_data)
        time.sleep(2)
        last_upload.handle_file_uploads(driver, config_data)

        #*DIN/DPIN/PAN of designated partner
        send_text('#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-guidetextbox_1527295062___widget', config_data['form_data']['fields']['DIN/DPIN/PAN of designated partner'])

        # Declaration and certification by professional

        # Enter Name
        send_text('#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox___widget', config_data['form_data']['fields']['Enter Name'])

        # Son/Daughter
        click_element(css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guideradiobutton__-1_widget')

        # Enter Father's Name
        send_text('#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox_1141998439___widget', config_data['form_data']['fields']["Enter Father's Name"])

        # do state that I am
        click_element(css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guideradiobutton_2109271305__-3_widget')

        # partnership and my membership number
        send_text('#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox_1809173783___widget', config_data['form_data']['fields']['partnership and my membership number'])

        # *Whether associate or fellow
        click_element(css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guideradiobutton_598616795__-1_widget')

        # SAVE         
        click_element(css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel_copy_copy_copy-mca_button_copy___widget')

        # ====== WAIT TO OBSERVE UPLOAD RESPONSE ======
        time.sleep(2)

        from selenium.common.exceptions import NoAlertPresentException

        time.sleep(2)
        try:
            alert = driver.switch_to.alert
            print("[+] Alert text:", alert.text)
            alert.accept()
            print("[+] Alert accepted.")
        except NoAlertPresentException:
            print("[!] No alert present.")

        # POP-UP
        click_element(css_selector='#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')

        # NEXT
        click_element(css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel_copy_copy_copy-mca_button___widget')

        # Proceed to Form 9
        click_element(css_selector='#guideContainer-rootPanel-panel-panel_1448122692-panel_copy_copy_copy-mca_button___widget')

        # Try to submit the application
        submit_result = submit_application()
        if submit_result:
            log_message("Application submitted successfully!")
        else:
            log_message("Submission may not have completed successfully. Please check the form status.")
            
        print("[AUTOMATE1] LLP form sequence completed successfully")
        return True
            
    except Exception as e:
        print(f"[AUTOMATE1] Error in LLP form sequence: {e}")
        traceback.print_exc()
        return False
    finally:
        # Clean up
        try:
            if driver:
                driver.quit()
        except:
            pass


# Execute if script is run directly
if __name__ == "__main__":
    print("[AUTOMATE1] This script should be imported by main.py")
    print("[AUTOMATE1] To run standalone, initialize a driver and call run_llp_form_sequence(driver)")
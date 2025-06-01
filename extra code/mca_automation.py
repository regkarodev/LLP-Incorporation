from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import json
import function1
import os
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

def handle_partners_without_din(driver, config_data, config_selectors):
    """Handle filling details for partners without DIN/DPIN"""
    try:
        # Validate config_data
        if not isinstance(config_data, dict):
            print("[ERROR] Invalid config_data format")
            return
            
        # Get form data from config_data
        form_data = config_data.get('form_data', {})
        if not form_data:
            print("[ERROR] No form_data found in config_data")
            return
            
        fields = form_data.get('fields', {})
        if not fields:
            print("[ERROR] No fields found in form_data")
            return

        # Get the number of partners to fill
        try:
            num_partners_no_din = int(fields.get('Individuals Not having valid DIN/DPIN', 0))
        except (ValueError, TypeError):
            print("[ERROR] Invalid number of partners without DIN/DPIN")
            return
        
        if num_partners_no_din < 1:
            print('[LOG] No designated partners without DIN/DPIN to fill.')
            return
        
        # Set maximum limit to 8
        if num_partners_no_din > 8:
            print('[WARNING] Reached the limit of 8 designated partners. Only filling 8.')
            num_partners_no_din = 8
        
        print(f'[LOG] Starting to fill details for {num_partners_no_din} partners without DIN/DPIN')
        
        # Get partner data from config_data
        partners_no_din = config_data.get('partners_without_din', [])
        
        if not partners_no_din:
            print("[WARNING] No partners_without_din data found in config_data")
            return

        # Initialize counters for overall success/failure tracking
        total_fields_filled = 0
        total_fields_failed = 0

        # Find all form sections using multiple strategies
        section_elements = []
        
        try:
            print("[DEBUG] Attempting to find form sections...")
            
            # Strategy 1: Find sections by panel class and guideFieldNode
            try:
                section_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((
                        By.XPATH, 
                        "//div[contains(@class, 'guideFieldNode') and contains(@class, 'panel') and contains(@class, 'guideContainer')]"
                    ))
                )
                print(f"[DEBUG] Strategy 1 found {len(section_elements)} sections")
            except Exception as e:
                print(f"[DEBUG] Strategy 1 failed: {str(e)}")
            
            # Strategy 2: Find sections by specific panel IDs
            if not section_elements:
                try:
                    section_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((
                            By.XPATH, 
                            "//div[contains(@id, 'guideContainer') and contains(@id, 'panel')]"
                        ))
                    )
                    print(f"[DEBUG] Strategy 2 found {len(section_elements)} sections")
                except Exception as e:
                    print(f"[DEBUG] Strategy 2 failed: {str(e)}")
            
            # Strategy 3: Find sections by form structure
            if not section_elements:
                try:
                    section_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((
                            By.XPATH, 
                            "//div[contains(@class, 'panel')]//div[contains(@class, 'guideFieldNode')]"
                        ))
                    )
                    print(f"[DEBUG] Strategy 3 found {len(section_elements)} sections")
                except Exception as e:
                    print(f"[DEBUG] Strategy 3 failed: {str(e)}")
            
            if not section_elements:
                print("[ERROR] No form sections found with any strategy")
                return
                
            if len(section_elements) < num_partners_no_din:
                print(f"[WARNING] Found only {len(section_elements)} form sections, but need to fill {num_partners_no_din}")
                return
                
            print(f"[LOG] Found {len(section_elements)} form sections")
            
            # Process each form section
            for section_index in range(num_partners_no_din):
                print(f'\n[LOG] ========== Processing Form Section {section_index + 1} of {num_partners_no_din} ==========')
                
                # Get partner data for this section
                partner = partners_no_din[section_index] if section_index < len(partners_no_din) else {}
                
                # Initialize counters for this section
                fields_filled_count = 0
                fields_failed_count = 0

                try:
                    # Get the specific section element
                    section_element = section_elements[section_index]
                    
                    # Generate dynamic XPath for this section
                    section_xpath = f"//div[contains(@class, 'guideFieldNode') and contains(@class, 'panel')][{section_index + 1}]"
                    
                    # Scroll to the section with a small offset
                    driver.execute_script("""
                        var element = arguments[0];
                        var headerOffset = 100;
                        var elementPosition = element.getBoundingClientRect().top;
                        var offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                        window.scrollTo({
                            top: offsetPosition,
                            behavior: 'smooth'
                        });
                    """, section_element)
                    time.sleep(1)  # Wait for scroll to complete
                    
                    # Make sure the section is visible and interactive
                    driver.execute_script("""
                        var section = arguments[0];
                        section.style.display = 'block';
                        section.style.visibility = 'visible';
                        section.style.opacity = '1';
                        section.style.height = 'auto';
                        section.style.overflow = 'visible';
                    """, section_element)
                    
                    # Fill each section of the form with dynamic XPath context
                    print("\n[LOG] Filling Personal Information...")
                    fields_filled_count, fields_failed_count = fill_personal_information(
                        driver, partner, fields_filled_count, fields_failed_count, section_element
                    )
                    
                    print("\n[LOG] Filling Permanent Address...")
                    fields_filled_count, fields_failed_count = fill_permanent_address(
                        driver, partner, fields_filled_count, fields_failed_count, section_element
                    )
                    
                    print("\n[LOG] Filling Present Address...")
                    fields_filled_count, fields_failed_count = fill_present_address(
                        driver, partner, fields_filled_count, fields_failed_count, section_element
                    )
                    
                    print("\n[LOG] Filling Identity and Residential Proof...")
                    fields_filled_count, fields_failed_count = fill_identity_proof(
                        driver, partner, fields_filled_count, fields_failed_count, section_element
                    )

                    print("\n[LOG] Filling Additional Form Fields...")
                    fields_filled_count, fields_failed_count = fill_additional_form_fields(
                        driver, partner, fields_filled_count, fields_failed_count, section_element
                    )

                    if fields_filled_count > 0:
                        print(f"\n[SUCCESS] ✓ Form Section {section_index + 1} filled: {fields_filled_count} fields filled, {fields_failed_count} failed")
                        total_fields_filled += fields_filled_count
                        total_fields_failed += fields_failed_count
                    else:
                        print(f"\n[WARNING] ⚠️ Form Section {section_index + 1} not filled: No fields were successfully filled")
                        total_fields_failed += 1

                    # Wait between sections
                    time.sleep(1)

                except Exception as e:
                    print(f"[ERROR] Failed to process form section {section_index + 1}: {str(e)}")
                    total_fields_failed += 1

            print(f"\n[LOG] ========== Completed all {num_partners_no_din} form sections ==========")
            print(f"Total fields filled: {total_fields_filled}")
            print(f"Total fields failed: {total_fields_failed}")
            
        except Exception as e:
            print(f"[ERROR] Failed to find form sections: {str(e)}")
            return
        
    except Exception as e:
        print(f"[ERROR] An error occurred in handle_partners_without_din: {str(e)}")
        import traceback
        traceback.print_exc()

def fill_input_field(driver, form_container, aria_label, value, fields_filled_count, fields_failed_count):
    """Helper function to fill an input field"""
    try:
        input_field = form_container.find_element(By.XPATH, f".//input[@aria-label='{aria_label}']")
        
        if value:
            # Make sure the input is visible
            driver.execute_script("""
                var input = arguments[0];
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
                input.removeAttribute('aria-readonly');
            """, input_field)
            
            # Clear and set value
            input_field.clear()
            input_field.send_keys(value)
            time.sleep(0.5)
            
            if input_field.get_attribute('value') == value:
                print(f"[SUCCESS] Filled: {aria_label} = {value}")
                fields_filled_count += 1
            else:
                print(f"[FAIL] Could not fill: {aria_label} = {value}")
                fields_failed_count += 1
        else:
            print(f"[INFO] No value provided for {aria_label}")
    except Exception as e:
        print(f"[FAIL] Error handling {aria_label}: {str(e)}")
        fields_failed_count += 1

    return fields_filled_count, fields_failed_count

def fill_select_field(driver, form_container, aria_label, value, fields_filled_count, fields_failed_count):
    """Helper function to fill a select field"""
    try:
        select_element = form_container.find_element(By.XPATH, f".//select[@aria-label='{aria_label}']")
        
        if value:
            # Make sure the select is visible
            driver.execute_script("""
                var select = arguments[0];
                select.style.display = 'block';
                select.style.visibility = 'visible';
                select.style.opacity = '1';
                select.removeAttribute('readonly');
                select.removeAttribute('disabled');
                select.removeAttribute('aria-readonly');
            """, select_element)
            
            # Create Select object and select value
            select = Select(select_element)
            select.select_by_visible_text(value)
            time.sleep(0.5)
            
            if select.first_selected_option.text.strip() == value:
                print(f"[SUCCESS] Filled: {aria_label} = {value}")
                fields_filled_count += 1
            else:
                print(f"[FAIL] Could not fill: {aria_label} = {value}")
                fields_failed_count += 1
        else:
            print(f"[INFO] No value provided for {aria_label}")
    except Exception as e:
        print(f"[FAIL] Error handling {aria_label}: {str(e)}")
        fields_failed_count += 1

    return fields_filled_count, fields_failed_count

def fill_radio_field(driver, form_container, field_name, options, fields_filled_count, fields_failed_count):
    """Helper function to fill a radio field"""
    try:
        if 'options' in options and field_name in options['options']:
            normalized_options = normalize_options_dict(options['options'])
            true_option = None
            for option, value in normalized_options.get(field_name, {}).items():
                if value is True:
                    true_option = option
                    break
            
            if true_option:
                radio_input = form_container.find_element(By.XPATH, f".//input[@type='radio' and @aria-label='{true_option}']")
                driver.execute_script("arguments[0].click();", radio_input)
                time.sleep(0.5)
                
                if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                    print(f"[SUCCESS] Filled: {field_name} = {true_option}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: {field_name} = {true_option}")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No option selected for {field_name}")
        else:
            print(f"[INFO] No options found for {field_name}")
    except Exception as e:
        print(f"[FAIL] Error handling {field_name}: {str(e)}")
        fields_failed_count += 1

    return fields_filled_count, fields_failed_count

def fill_personal_information(driver, partner, fields_filled_count, fields_failed_count, parent=None):
    """Fill personal information section"""
    try:
        # First find the personal information section by text
        section_title = "Particulars of individual designated partners not having DIN/DPIN"
        form_container = None
        try:
            # Find the section by text
            section_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{section_title}')]"))
            )
            
            # Get the parent container
            form_container = section_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'panel')]")
            
            # Make sure the container is visible
            driver.execute_script("""
                var container = arguments[0];
                container.style.display = 'block';
                container.style.visibility = 'visible';
                container.style.opacity = '1';
                container.style.height = 'auto';
                container.style.overflow = 'visible';
            """, form_container)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", form_container)
            time.sleep(1)
        except Exception as e:
            print(f"[ERROR] Could not find or prepare personal information section container: {str(e)}")
            fields_failed_count += 1
            return fields_filled_count, fields_failed_count

        if form_container:
            # Fill name fields with proper XPath escaping
            name_fields = {
                "First Name": "First Name",
                "Middle Name": "Middle Name",
                "Surname": "Surname"
            }
            
            for field_label, field_key in name_fields.items():
                try:
                    # Use proper XPath escaping for fields with apostrophes
                    if "'" in field_label:
                        xpath = f'.//input[contains(@aria-label, "{field_label}")]'
                    else:
                        xpath = f'.//input[@aria-label="{field_label}"]'
                    
                    input_elem = form_container.find_element(By.XPATH, xpath)
                    
                    driver.execute_script("""
                        var input = arguments[0];
                        input.style.display = 'block';
                        input.style.visibility = 'visible';
                        input.style.opacity = '1';
                        input.removeAttribute('readonly');
                        input.removeAttribute('disabled');
                        input.removeAttribute('aria-readonly');
                    """, input_elem)
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
                    time.sleep(0.5)
                    
                    value = partner.get(field_key, '').strip()
                    if value:
                        input_elem.clear()
                        input_elem.send_keys(value)
                        time.sleep(0.5)
                        
                        if input_elem.get_attribute('value') == value:
                            print(f"[SUCCESS] Filled: {field_label} = {value}")
                            fields_filled_count += 1
                        else:
                            print(f"[FAIL] Could not fill: {field_label} = {value} (value mismatch)")
                            fields_failed_count += 1
                    else:
                        print(f"[INFO] No value provided for {field_label}")
                except Exception as e:
                    print(f"[FAIL] Error handling {field_label}: {str(e)}")
                    fields_failed_count += 1

            # Fill father's name fields
            father_fields = {
                "Father's First Name": "Father Name",
                "Father's Middle Name": "Father Middle Name",
                "Father's Surname": "Father Surname"
            }
            
            for field_label, field_key in father_fields.items():
                try:
                    input_elem = form_container.find_element(By.XPATH, f'.//input[@aria-label="{field_label}"]')
                    
                    driver.execute_script("""
                        var input = arguments[0];
                        input.style.display = 'block';
                        input.style.visibility = 'visible';
                        input.style.opacity = '1';
                        input.removeAttribute('readonly');
                        input.removeAttribute('disabled');
                        input.removeAttribute('aria-readonly');
                    """, input_elem)
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
                    time.sleep(0.5)
                    
                    value = partner.get(field_key, '').strip()
                    if value:
                        input_elem.clear()
                        input_elem.send_keys(value)
                        time.sleep(0.5)
                        
                        if input_elem.get_attribute('value') == value:
                            print(f"[SUCCESS] Filled: {field_label} = {value}")
                            fields_filled_count += 1
                        else:
                            print(f"[FAIL] Could not fill: {field_label} = {value} (value mismatch)")
                            fields_failed_count += 1
                    else:
                        print(f"[INFO] No value provided for {field_label}")
                except Exception as e:
                    print(f"[FAIL] Error handling {field_label}: {str(e)}")
                    fields_failed_count += 1

            # Fill Whether resident of India
            try:
                if 'options' in partner and 'Whether resident of India' in partner['options']:
                    # Add retry logic for clicking the radio button
                    max_retries = 3
                    retry_count = 0
                    success = False
                    
                    while retry_count < max_retries and not success:
                        try:
                            # Wait for the page to be fully loaded
                            WebDriverWait(driver, 10).until(
                                lambda d: d.execute_script('return document.readyState') == 'complete'
                            )
                            
                            # Find the radio group container using the specific XPath
                            radio_container = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((
                                    By.XPATH, 
                                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidecheckbox_copy_c_1044176976___guide-item']"
                                ))
                            )
                            
                            # Make sure the container is visible
                            driver.execute_script("""
                                var container = arguments[0];
                                container.style.display = 'block';
                                container.style.visibility = 'visible';
                                container.style.opacity = '1';
                                container.style.height = 'auto';
                                container.style.overflow = 'visible';
                            """, radio_container)
                            
                            # Get the value from options
                            options = partner['options']['Whether resident of India']
                            radio_value = None
                            for option, value in options.items():
                                if value == "True":
                                    radio_value = option
                                    break
                            
                            if radio_value:
                                # Find the radio input within the container
                                radio_input = radio_container.find_element(
                                    By.XPATH, 
                                    f".//input[@type='radio' and @aria-label='{radio_value}']"
                                )
                                
                                # Make sure the radio input is visible and interactive
                                driver.execute_script("""
                                    var input = arguments[0];
                                    input.style.display = 'block';
                                    input.style.visibility = 'visible';
                                    input.style.opacity = '1';
                                    input.removeAttribute('readonly');
                                    input.removeAttribute('disabled');
                                    input.removeAttribute('aria-readonly');
                                """, radio_input)
                                
                                # Scroll into view
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_container)
                                time.sleep(0.5)
                                
                                # Try multiple click strategies
                                try:
                                    # Strategy 1: Click the label
                                    label = radio_container.find_element(By.XPATH, f".//label[text()='{radio_value}']")
                                    driver.execute_script("arguments[0].click();", label)
                                except:
                                    try:
                                        # Strategy 2: Direct click
                                        driver.execute_script("arguments[0].click();", radio_input)
                                    except:
                                        try:
                                            # Strategy 3: Set checked property
                                            driver.execute_script("""
                                                var input = arguments[0];
                                                input.checked = true;
                                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                                input.dispatchEvent(new Event('click', { bubbles: true }));
                                            """, radio_input)
                                        except:
                                            print("[DEBUG] All click strategies failed")
                                            raise Exception("Could not click radio button")
                                
                                time.sleep(0.5)
                                
                                # Verify the selection
                                if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                                    print(f"[SUCCESS] Filled: Whether resident of India = {radio_value}")
                                    fields_filled_count += 1
                                    success = True
                                else:
                                    print(f"[RETRY {retry_count + 1}/{max_retries}] Selection not verified")
                                    retry_count += 1
                                    time.sleep(1)
                            else:
                                print("[INFO] No True value found in options")
                                break
                                
                        except TimeoutException as te:
                            print(f"[RETRY {retry_count + 1}/{max_retries}] Timeout while trying to click: {str(te)}")
                            retry_count += 1
                            time.sleep(1)
                        except Exception as e:
                            print(f"[RETRY {retry_count + 1}/{max_retries}] Error: {str(e)}")
                            retry_count += 1
                            time.sleep(1)
                    
                    if not success:
                        print("[FAIL] Could not fill: Whether resident of India after all retries")
                        fields_failed_count += 1
                else:
                    print("[INFO] No options found for Whether resident of India")
            except Exception as e:
                print(f"[FAIL] Error handling Whether resident of India: {str(e)}")
                fields_failed_count += 1

            # Fill Date of Birth
            try:
                # Try multiple strategies to find the date input field
                dob_input = None
                try:
                    # Strategy 1: Exact aria-label match
                    dob_input = form_container.find_element(By.XPATH, './/input[@aria-label="Date of Birth   Please Enter date in DD/MM/YYYY format only"]')
                except:
                    try:
                        # Strategy 2: Partial aria-label match
                        dob_input = form_container.find_element(By.XPATH, './/input[contains(@aria-label, "Date of Birth")]')
                    except:
                        try:
                            # Strategy 3: Find by label text
                            label = form_container.find_element(By.XPATH, './/label[contains(text(), "Date of Birth")]')
                            dob_input = label.find_element(By.XPATH, './following::input[1]')
                        except:
                            try:
                                # Strategy 4: Find by class and type
                                dob_input = form_container.find_element(By.XPATH, './/input[@type="text" and contains(@class, "guidedatepicker")]')
                            except:
                                print("[DEBUG] Could not find Date of Birth input using any strategy")
                                raise Exception("Date of Birth input field not found")

                if dob_input:
                    dob = partner.get("Date of Birth", "").strip()
                    if dob:
                        # Get the input element's ID
                        dob_id = dob_input.get_attribute('id')
                        if not dob_id:
                            # If no ID exists, generate a unique one
                            dob_id = f"dob_input_{int(time.time())}"
                            driver.execute_script(f"arguments[0].id = '{dob_id}';", dob_input)
                        
                        # Use the set_date_field function from function1
                        if function1.set_date_field(driver, dob_id, dob):
                            print(f"[SUCCESS] Filled: Date of Birth = {dob}")
                            fields_filled_count += 1
                        else:
                            print(f"[FAIL] Could not fill: Date of Birth = {dob}")
                            fields_failed_count += 1
                    else:
                        print(f"[INFO] No value provided for Date of Birth")
                else:
                    print("[FAIL] Could not find Date of Birth input field")
                    fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Error handling Date of Birth: {str(e)}")
                fields_failed_count += 1

            # Fill Whether citizen of India
            try:
                if 'options' in partner and 'Whether citizen of India' in partner['options']:
                    # Add retry logic for clicking the radio button
                    max_retries = 3
                    retry_count = 0
                    success = False
                    
                    while retry_count < max_retries and not success:
                        try:
                            # Wait for the page to be fully loaded
                            WebDriverWait(driver, 10).until(
                                lambda d: d.execute_script('return document.readyState') == 'complete'
                            )
                            
                            # Find the radio group container using the specific XPath
                            radio_container = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((
                                    By.XPATH, 
                                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidecheckbox_copy_c___guide-item']"
                                ))
                            )
                            
                            # Make sure the container is visible
                            driver.execute_script("""
                                var container = arguments[0];
                                container.style.display = 'block';
                                container.style.visibility = 'visible';
                                container.style.opacity = '1';
                                container.style.height = 'auto';
                                container.style.overflow = 'visible';
                            """, radio_container)
                            
                            # Get the value from options
                            options = partner['options']['Whether citizen of India']
                            radio_value = None
                            for option, value in options.items():
                                if value == "True":
                                    radio_value = option
                                    break
                            
                            if radio_value:
                                # Find the radio input within the container
                                radio_input = radio_container.find_element(
                                    By.XPATH, 
                                    f".//input[@type='radio' and @aria-label='{radio_value}']"
                                )
                                
                                # Make sure the radio input is visible and interactive
                                driver.execute_script("""
                                    var input = arguments[0];
                                    input.style.display = 'block';
                                    input.style.visibility = 'visible';
                                    input.style.opacity = '1';
                                    input.removeAttribute('readonly');
                                    input.removeAttribute('disabled');
                                    input.removeAttribute('aria-readonly');
                                """, radio_input)
                                
                                # Scroll into view
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_container)
                                time.sleep(0.5)
                                
                                # Try multiple click strategies
                                try:
                                    # Strategy 1: Click the label
                                    label = radio_container.find_element(By.XPATH, f".//label[text()='{radio_value}']")
                                    driver.execute_script("arguments[0].click();", label)
                                except:
                                    try:
                                        # Strategy 2: Direct click
                                        driver.execute_script("arguments[0].click();", radio_input)
                                    except:
                                        try:
                                            # Strategy 3: Set checked property
                                            driver.execute_script("""
                                                var input = arguments[0];
                                                input.checked = true;
                                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                                input.dispatchEvent(new Event('click', { bubbles: true }));
                                            """, radio_input)
                                        except:
                                            print("[DEBUG] All click strategies failed")
                                            raise Exception("Could not click radio button")
                                
                                time.sleep(0.5)
                                
                                # Verify the selection
                                if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                                    print(f"[SUCCESS] Filled: Whether citizen of India = {radio_value}")
                                    fields_filled_count += 1
                                    success = True
                                else:
                                    print(f"[RETRY {retry_count + 1}/{max_retries}] Selection not verified")
                                    retry_count += 1
                                    time.sleep(1)
                            else:
                                print("[INFO] No True value found in options")
                                break
                                
                        except TimeoutException as te:
                            print(f"[RETRY {retry_count + 1}/{max_retries}] Timeout while trying to click: {str(te)}")
                            retry_count += 1
                            time.sleep(1)
                        except Exception as e:
                            print(f"[RETRY {retry_count + 1}/{max_retries}] Error: {str(e)}")
                            retry_count += 1
                            time.sleep(1)
                    
                    if not success:
                        print("[FAIL] Could not fill: Whether citizen of India after all retries")
                        fields_failed_count += 1
                else:
                    print("[INFO] No options found for Whether citizen of India")
            except Exception as e:
                print(f"[FAIL] Error handling Whether citizen of India: {str(e)}")
                fields_failed_count += 1

            # Fill Occupation type and Description of others
            try:
                occupation_select_elem = form_container.find_element(By.XPATH, './/select[@aria-label="Occupation type"]')
                occupation = partner.get("Occupation type", "").strip()
                if occupation:
                    select = Select(occupation_select_elem)
                    select.select_by_visible_text(occupation)
                    time.sleep(0.5)
                    
                    if select.first_selected_option.text == occupation:
                        print(f"[SUCCESS] Filled: Occupation type = {occupation}")
                        fields_filled_count += 1
                        
                        if occupation.lower() == "other":
                            try:
                                others_input = form_container.find_element(By.XPATH, './/input[@aria-label="Description of others"]')
                                driver.execute_script("""
                                    var input = arguments[0];
                                    input.style.display = 'block';
                                    input.style.visibility = 'visible';
                                    input.style.opacity = '1';
                                    input.removeAttribute('readonly');
                                    input.removeAttribute('disabled');
                                    input.removeAttribute('aria-readonly');
                                """, others_input)
                                
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", others_input)
                                time.sleep(0.5)
                                
                                description = partner.get("Description of others", "").strip()
                                if description:
                                    others_input.clear()
                                    others_input.send_keys(description)
                                    time.sleep(0.5)
                                    
                                    if others_input.get_attribute('value') == description:
                                        print(f"[SUCCESS] Filled: Description of others = {description}")
                                        fields_filled_count += 1
                                    else:
                                        print(f"[FAIL] Could not fill: Description of others = {description} (value mismatch)")
                                        fields_failed_count += 1
                                else:
                                    print(f"[INFO] No value for Description of others (Occupation was Other)")
                            except Exception as e_desc:
                                print(f"[FAIL] Error handling Description of others: {str(e_desc)}")
                                fields_failed_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Occupation type = {occupation} (selection mismatch)")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] No value provided for Occupation type")
            except Exception as e_occ:
                print(f"[FAIL] Error handling Occupation type: {str(e_occ)}")
                fields_failed_count += 1

            # Fill Area of Occupation and If Others selected
            try:
                area_select_elem = form_container.find_element(By.XPATH, './/select[@aria-label="Area of Occupation"]')
                area = partner.get("Area of Occupation", "").strip()
                if area:
                    select = Select(area_select_elem)
                    select.select_by_visible_text(area)
                    time.sleep(0.5)
                    
                    if select.first_selected_option.text == area:
                        print(f"[SUCCESS] Filled: Area of Occupation = {area}")
                        fields_filled_count += 1
                        
                        if area.lower() == "other":
                            try:
                                others_input = form_container.find_element(By.XPATH, './/input[@aria-label="If \'Others\' selected, please specify"]')
                                driver.execute_script("""
                                    var input = arguments[0];
                                    input.style.display = 'block';
                                    input.style.visibility = 'visible';
                                    input.style.opacity = '1';
                                    input.removeAttribute('readonly');
                                    input.removeAttribute('disabled');
                                    input.removeAttribute('aria-readonly');
                                """, others_input)
                                
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", others_input)
                                time.sleep(0.5)
                                
                                description = partner.get("If Others selected, please specify", "").strip()
                                if description:
                                    others_input.clear()
                                    others_input.send_keys(description)
                                    time.sleep(0.5)
                                    
                                    if others_input.get_attribute('value') == description:
                                        print(f"[SUCCESS] Filled: If 'Others' selected, please specify = {description}")
                                        fields_filled_count += 1
                                    else:
                                        print(f"[FAIL] Could not fill: If 'Others' selected, please specify = {description} (value mismatch)")
                                        fields_failed_count += 1
                                else:
                                    print(f"[INFO] No value for If 'Others' selected, please specify (Area of Occupation was Other)")
                            except Exception as e_area_desc:
                                print(f"[FAIL] Error handling If 'Others' selected, please specify: {str(e_area_desc)}")
                                fields_failed_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Area of Occupation = {area} (selection mismatch)")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] No value provided for Area of Occupation")
            except Exception as e_area:
                print(f"[FAIL] Error handling Area of Occupation: {str(e_area)}")
                fields_failed_count += 1

            # Fill gender
            try:
                select_elem = form_container.find_element(By.XPATH, './/select[@aria-label="Gender"]')
                gender = partner.get("Gender", "").strip()
                if gender:
                    select = Select(select_elem)
                    select.select_by_visible_text(gender)
                    time.sleep(0.5)
                    
                    if select.first_selected_option.text == gender:
                        print(f"[SUCCESS] Filled: Gender = {gender}")
                        fields_filled_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Gender = {gender} (selection mismatch)")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] No value provided for Gender")
            except Exception as e:
                print(f"[FAIL] Error handling Gender: {str(e)}")
                fields_failed_count += 1

            # Fill educational qualification
            try:
                # Find the educational qualification container using the specific ID
                edu_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((
                        By.XPATH, 
                        "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidetextbox_copy_11_164495912___guide-item']"
                    ))
                )
                
                # Make sure the container is visible
                driver.execute_script("""
                    var container = arguments[0];
                    container.style.display = 'block';
                    container.style.visibility = 'visible';
                    container.style.opacity = '1';
                    container.style.height = 'auto';
                    container.style.overflow = 'visible';
                """, edu_container)
                
                # Find the select element within the container
                select_elem = edu_container.find_element(
                    By.XPATH, 
                    ".//select[@aria-label='Educational qualification']"
                )
                
                # Make sure the select is visible and interactive
                driver.execute_script("""
                    var select = arguments[0];
                    select.style.display = 'block';
                    select.style.visibility = 'visible';
                    select.style.opacity = '1';
                    select.removeAttribute('readonly');
                    select.removeAttribute('disabled');
                    select.removeAttribute('aria-readonly');
                """, select_elem)
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edu_container)
                time.sleep(0.5)
                
                # Get the value from partner data
                edu_qualification = partner.get("Educational qualification", "").strip()
                if edu_qualification:
                    # Create Select object
                    select = Select(select_elem)
                    
                    # Try multiple selection strategies
                    try:
                        # Strategy 1: Select by visible text
                        select.select_by_visible_text(edu_qualification)
                    except:
                        try:
                            # Strategy 2: Select by value
                            select.select_by_value(edu_qualification)
                        except:
                            try:
                                # Strategy 3: Case-insensitive partial match
                                for option in select.options:
                                    if edu_qualification.lower() in option.text.lower():
                                        select.select_by_visible_text(option.text)
                                        break
                            except:
                                print(f"[FAIL] Could not select educational qualification: {edu_qualification}")
                                raise Exception("Failed to select educational qualification")
                    
                    time.sleep(0.5)
                    
                    # Verify selection
                    if select.first_selected_option.text.strip() == edu_qualification:
                        print(f"[SUCCESS] Filled: Educational qualification = {edu_qualification}")
                        fields_filled_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Educational qualification = {edu_qualification} (selection mismatch)")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] No value provided for Educational qualification")
            except Exception as e:
                print(f"[FAIL] Error handling Educational qualification: {str(e)}")
                fields_failed_count += 1

            # Fill nationality
            try:
                nationality_select_elem = form_container.find_element(By.XPATH, './/select[@aria-label="Nationality"]')
                nationality = partner.get("Nationality", "").strip()
                if nationality:
                    select = Select(nationality_select_elem)
                    select.select_by_visible_text(nationality)
                    time.sleep(0.5)
                    
                    if select.first_selected_option.text == nationality:
                        print(f"[SUCCESS] Filled: Nationality = {nationality}")
                        fields_filled_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Nationality = {nationality} (selection mismatch)")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] No value provided for Nationality")
            except Exception as e:
                print(f"[FAIL] Error handling Nationality: {str(e)}")
                fields_failed_count += 1


            # Fill income tax PAN/Passport number radio
            try:
                # Assuming PAN is the default or desired selection if not specified
                pan_radio_value = partner.get("Income-tax PAN/Passport number type", "PAN").strip().upper()
                pan_radio = form_container.find_element(By.XPATH, f'.//input[@type="radio" and @aria-label="{pan_radio_value}"]')
                driver.execute_script("arguments[0].click();", pan_radio)
                time.sleep(0.5)
                
                if pan_radio.get_attribute('aria-checked') == 'true':
                    print(f"[SUCCESS] Filled: Income-tax PAN/Passport number type = {pan_radio_value}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Income-tax PAN/Passport number type = {pan_radio_value}")
                    fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Error handling Income-tax PAN/Passport number type radio: {str(e)}")
                fields_failed_count += 1


            # Fill income tax PAN/Passport number details
            try:
                pan_details_input = form_container.find_element(
                    By.XPATH, './/input[contains(@aria-label, "Income-tax PAN/Passport number details")]'
                )
                pan_value = partner.get("Income-tax PAN/Passport number details", "").strip()
                
                if pan_value:
                    # Make input visible and editable via JS (sometimes required for hidden or readonly inputs)
                    driver.execute_script("""
                        var input = arguments[0];
                        input.style.display = 'block';
                        input.style.visibility = 'visible';
                        input.style.opacity = '1';
                        input.removeAttribute('readonly');
                        input.removeAttribute('disabled');
                        input.removeAttribute('aria-readonly');
                    """, pan_details_input)
                    
                    pan_details_input.clear()
                    pan_details_input.send_keys(pan_value)
                    time.sleep(0.5)  # small delay to let UI update

                    # Verify if the value was correctly set
                    if pan_details_input.get_attribute('value') == pan_value:
                        print(f"[SUCCESS] Filled: Income-tax PAN/Passport number details = {pan_value}")
                        fields_filled_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Income-tax PAN/Passport number details = {pan_value} (value mismatch)")
                        fields_failed_count += 1
                else:
                    print("[INFO] No value for Income-tax PAN/Passport number details")
            except Exception as e:
                print(f"[FAIL] Error handling Income-tax PAN/Passport number details: {str(e)}")
                fields_failed_count += 1

            # Fill place of birth (state)
            try:
                state_select_elem = form_container.find_element(By.XPATH, './/select[@aria-label="Place of Birth (State)"]')
                state = partner.get("Place of Birth (State)", "").strip()
                if state:
                    select = Select(state_select_elem)
                    select.select_by_visible_text(state)
                    time.sleep(0.5)
                    if select.first_selected_option.text == state:
                        print(f"[SUCCESS] Filled: Place of Birth (State) = {state}")
                        fields_filled_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Place of Birth (State) = {state} (selection mismatch)")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] No value for Place of Birth (State)")
            except Exception as e:
                print(f"[FAIL] Error handling Place of Birth (State): {str(e)}")
                fields_failed_count += 1

            # Fill place of birth (district)
            try:
                # Find the district select element using multiple strategies
                district_select = None
                try:
                    # Strategy 1: Direct aria-label match
                    district_select = form_container.find_element(By.XPATH, './/select[@aria-label="Place of Birth (District)"]')
                except:
                    try:
                        # Strategy 2: Find by class and ID pattern
                        district_select = form_container.find_element(By.XPATH, './/select[contains(@id, "guideContainer") and contains(@id, "guidetextbox_copy_11")]')
                    except:
                        try:
                            # Strategy 3: Find by label text
                            label = form_container.find_element(By.XPATH, './/label[contains(text(), "Place of Birth (District)")]')
                            district_select = label.find_element(By.XPATH, './following::select[1]')
                        except:
                            print("[DEBUG] Could not find Place of Birth (District) select using any strategy")
                            raise Exception("Place of Birth (District) select not found")

                if district_select:
                    district = partner.get("Place of Birth (District)", "").strip()
                    if district:
                        # Make sure the select is visible
                        driver.execute_script("""
                            var select = arguments[0];
                            select.style.display = 'block';
                            select.style.visibility = 'visible';
                            select.style.opacity = '1';
                            select.removeAttribute('readonly');
                            select.removeAttribute('disabled');
                            select.removeAttribute('aria-readonly');
                        """, district_select)
                        
                        # Scroll into view
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", district_select)
                        time.sleep(0.5)
                        
                        # Create Select object and select value
                        select = Select(district_select)
                        
                        # Try multiple selection strategies
                        try:
                            # Strategy 1: Select by visible text
                            select.select_by_visible_text(district)
                        except:
                            try:
                                # Strategy 2: Select by value
                                select.select_by_value(district)
                            except:
                                try:
                                    # Strategy 3: Case-insensitive partial match
                                    for option in select.options:
                                        if district.lower() in option.text.lower():
                                            select.select_by_visible_text(option.text)
                                            break
                                except:
                                    print(f"[FAIL] Could not select district: {district}")
                                    raise Exception("Failed to select district")
                        
                        time.sleep(0.5)
                        
                        # Verify selection
                        if select.first_selected_option.text.strip() == district:
                            print(f"[SUCCESS] Filled: Place of Birth (District) = {district}")
                            fields_filled_count += 1
                        else:
                            print(f"[FAIL] Could not fill: Place of Birth (District) = {district} (selection mismatch)")
                            fields_failed_count += 1
                    else:
                        print(f"[INFO] No value provided for Place of Birth (District)")
                else:
                    print(f"[FAIL] Could not find Place of Birth (District) select element")
                    fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Error handling Place of Birth (District): {str(e)}")
                fields_failed_count += 1

            # Mobile No. - Assuming fill_mobile_no is a robust helper
            try:
                mobile = partner.get("Mobile No", "").strip()
                if mobile:
                    if fill_mobile_no(driver, mobile, parent=form_container):
                        fields_filled_count += 1
                    else:
                        fields_failed_count += 1
                else:
                    print(f"[INFO] No value for Mobile No.")
            except Exception as e:
                print(f"[FAIL] Error handling Mobile No.: {str(e)}")
                fields_failed_count += 1

            # Email ID
            try:
                email_input = form_container.find_element(By.XPATH, './/input[@aria-label="Email ID"]')
                email = partner.get("Email ID", "").strip()
                if email:
                    driver.execute_script("""
                        var input = arguments[0];
                        input.style.display = 'block';
                        input.style.visibility = 'visible';
                        input.style.opacity = '1';
                        input.removeAttribute('readonly');
                        input.removeAttribute('disabled');
                        input.removeAttribute('aria-readonly');
                    """, email_input)
                    
                    email_input.clear()
                    email_input.send_keys(email)
                    time.sleep(0.5)
                    
                    if email_input.get_attribute('value') == email:
                        print(f"[SUCCESS] Filled: Email ID = {email}")
                        fields_filled_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Email ID = {email} (value mismatch)")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] No value for Email ID")
            except Exception as e:
                print(f"[FAIL] Error handling Email ID: {str(e)}")
                fields_failed_count += 1
        else:
            print("[ERROR] form_container was not found for personal information.")
            fields_failed_count += 1

    except Exception as e:
        print(f"[ERROR] Major error in fill_personal_information: {str(e)}")
        fields_failed_count += 1

    return fields_filled_count, fields_failed_count

def fill_permanent_address(driver, partner, fields_filled_count, fields_failed_count, parent=None):
    """Fill permanent address section"""
    try:
        # First find the permanent address section
        if not parent:
            section_title = "Permanent Address"
            try:
                # Try multiple strategies to find the section
                section_element = None
                try:
                    # Strategy 1: Direct text match
                    section_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{section_title}')]"))
                    )
                except:
                    try:
                        # Strategy 2: Class-based search
                        section_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'guideFieldNode') and contains(@class, 'panel')]"))
                        )
                    except:
                        # Strategy 3: Generic panel search
                        section_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'panel')]"))
                        )
                
                if section_element:
                    parent = section_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'panel')]")
                else:
                    print(f"[ERROR] Could not find permanent address section")
                    return fields_filled_count, fields_failed_count
            except Exception as e:
                print(f"[ERROR] Could not find permanent address section: {str(e)}")
                return fields_filled_count, fields_failed_count

        # Fill Address Line I
        try:
            address_line1_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox___guide-item']"
                ))
            )
            
            input_elem = address_line1_container.find_element(
                By.XPATH, 
                ".//input[@aria-label='Address Line I']"
            )
            
            # Make input visible and interactive
            driver.execute_script("""
                var input = arguments[0];
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
                input.removeAttribute('aria-readonly');
            """, input_elem)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", address_line1_container)
            time.sleep(0.5)
            
            address_line1 = partner.get("Address Line I", "").strip()
            if address_line1:
                # Validate max length (160 characters)
                if len(address_line1) > 160:
                    print(f"[WARNING] Address Line I exceeds maximum length of 160 characters: {address_line1}")
                    address_line1 = address_line1[:160]
                
                input_elem.clear()
                input_elem.send_keys(address_line1)
                time.sleep(0.5)
                
                if input_elem.get_attribute('value') == address_line1:
                    print(f"[SUCCESS] Filled: Address Line I = {address_line1}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Address Line I = {address_line1} (value mismatch)")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Address Line I")
        except Exception as e:
            print(f"[FAIL] Error handling Address Line I: {str(e)}")
            fields_failed_count += 1

        # Fill Address Line II
        try:
            address_line2_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy___guide-item']"
                ))
            )
            
            input_elem = address_line2_container.find_element(
                By.XPATH, 
                ".//input[@aria-label='Address Line II']"
            )
            
            # Make input visible and interactive
            driver.execute_script("""
                var input = arguments[0];
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
                input.removeAttribute('aria-readonly');
            """, input_elem)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", address_line2_container)
            time.sleep(0.5)
            
            address_line2 = partner.get("Address Line II", "").strip()
            if address_line2:
                # Validate max length (100 characters)
                if len(address_line2) > 100:
                    print(f"[WARNING] Address Line II exceeds maximum length of 100 characters: {address_line2}")
                    address_line2 = address_line2[:100]
                
                input_elem.clear()
                input_elem.send_keys(address_line2)
                time.sleep(0.5)
                
                if input_elem.get_attribute('value') == address_line2:
                    print(f"[SUCCESS] Filled: Address Line II = {address_line2}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Address Line II = {address_line2} (value mismatch)")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Address Line II")
        except Exception as e:
            print(f"[FAIL] Error handling Address Line II: {str(e)}")
            fields_failed_count += 1

        # Fill Country
        try:
            country_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidedropdownlist___guide-item']"
                ))
            )
            
            select_elem = country_container.find_element(
                By.XPATH, 
                ".//select[@aria-label='Country']"
            )
            
            # Make select visible and interactive
            driver.execute_script("""
                var select = arguments[0];
                select.style.display = 'block';
                select.style.visibility = 'visible';
                select.style.opacity = '1';
                select.removeAttribute('readonly');
                select.removeAttribute('disabled');
                select.removeAttribute('aria-readonly');
            """, select_elem)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", country_container)
            time.sleep(0.5)
            
            country = partner.get("Country", "").strip()
            if country:
                select = Select(select_elem)
                
                # Try multiple selection strategies
                try:
                    # Strategy 1: Select by visible text
                    select.select_by_visible_text(country)
                except:
                    try:
                        # Strategy 2: Select by value
                        select.select_by_value(country)
                    except:
                        try:
                            # Strategy 3: Case-insensitive partial match
                            for option in select.options:
                                if country.lower() in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    break
                        except:
                            print(f"[FAIL] Could not select country: {country}")
                            raise Exception("Failed to select country")
                
                time.sleep(0.5)
                
                if select.first_selected_option.text.strip() == country:
                    print(f"[SUCCESS] Filled: Country = {country}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Country = {country} (selection mismatch)")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Country")
        except Exception as e:
            print(f"[FAIL] Error handling Country: {str(e)}")
            fields_failed_count += 1

        # Fill Pin code / Zip Code
        time.sleep(0.5)
        try:
            pincode_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy_1737891757___guide-item']"
                ))
            )
            
            input_elem = pincode_container.find_element(
                By.XPATH, 
                ".//input[@aria-label='Pin code / Zip Code']"
            )
            
            # Make input visible and interactive
            driver.execute_script("""
                var input = arguments[0];
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
                input.removeAttribute('aria-readonly');
            """, input_elem)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pincode_container)
            time.sleep(0.5)
            
            pincode = partner.get("Pin code / Zip Code", "").strip()
            if pincode:
                # Validate max length (6 characters)
                if len(pincode) > 6:
                    print(f"[WARNING] Pin code exceeds maximum length of 6 characters: {pincode}")
                    pincode = pincode[:6]
                
                input_elem.clear()
                input_elem.send_keys(pincode)
                time.sleep(0.5)
                
                if input_elem.get_attribute('value') == pincode:
                    print(f"[SUCCESS] Filled: Pin code / Zip Code = {pincode}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Pin code / Zip Code = {pincode} (value mismatch)")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Pin code / Zip Code")
        except Exception as e:
            print(f"[FAIL] Error handling Pin code / Zip Code: {str(e)}")
            fields_failed_count += 1

        # Fill Area/ Locality
        try:
            print("[DEBUG] Attempting to fill Area/Locality...")
            
            # Find the container using the specific XPath
            area_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidedropdownlist_1592911853___guide-item']"
                ))
            )
            print("[DEBUG] Found Area/Locality container")
            
            # Make sure the container is visible
            driver.execute_script("""
                var container = arguments[0];
                container.style.display = 'block';
                container.style.visibility = 'visible';
                container.style.opacity = '1';
                container.style.height = 'auto';
                container.style.overflow = 'visible';
            """, area_container)
            
            # Find the select element within the container
            select_elem = area_container.find_element(
                By.XPATH, 
                ".//select[@aria-label='Area/ Locality']"
            )
            print("[DEBUG] Found Area/Locality select element")
            
            # Make select visible and interactive
            driver.execute_script("""
                var select = arguments[0];
                select.style.display = 'block';
                select.style.visibility = 'visible';
                select.style.opacity = '1';
                select.removeAttribute('readonly');
                select.removeAttribute('disabled');
                select.removeAttribute('aria-readonly');
            """, select_elem)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", area_container)
            time.sleep(1)  # Increased wait time to ensure element is fully interactive

            area = partner.get("Area/ Locality", "").strip()
            if area:
                print(f"[DEBUG] Attempting to select Area/Locality: {area}")
                
                # Create Select object
                select = Select(select_elem)
                
                # Log available options for debugging
                print("[DEBUG] Available options in Area/Locality dropdown:")
                for option in select.options:
                    print(f"  - {option.text} (value: {option.get_attribute('value')})")
                
                # Try multiple selection strategies
                success = False
                
                # Strategy 1: Select by visible text (exact match)
                try:
                    select.select_by_visible_text(area)
                    time.sleep(0.5)
                    if select.first_selected_option.text.strip() == area:
                        success = True
                        print(f"[DEBUG] Successfully selected Area/Locality using exact match")
                except Exception as e:
                    print(f"[DEBUG] Exact match failed: {str(e)}")
                
                # Strategy 2: Select by value
                if not success:
                    try:
                        select.select_by_value(area)
                        time.sleep(0.5)
                        if select.first_selected_option.text.strip() == area:
                            success = True
                            print(f"[DEBUG] Successfully selected Area/Locality using value match")
                    except Exception as e:
                        print(f"[DEBUG] Value match failed: {str(e)}")
                
                # Strategy 3: Case-insensitive partial match
                if not success:
                    try:
                        for option in select.options:
                            if area.lower() in option.text.lower():
                                select.select_by_visible_text(option.text)
                                time.sleep(0.5)
                                if select.first_selected_option.text.strip() == option.text:
                                    success = True
                                    print(f"[DEBUG] Successfully selected Area/Locality using partial match")
                                    break
                    except Exception as e:
                        print(f"[DEBUG] Partial match failed: {str(e)}")
                
                if success:
                    print(f"[SUCCESS] Filled: Area/ Locality = {area}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Area/ Locality = {area} (no matching option found)")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Area/ Locality")
        except Exception as e:
            print(f"[FAIL] Error handling Area/ Locality: {str(e)}")
            fields_failed_count += 1

        # Fill Jurisdiction of Police Station
        try:
            police_station_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_1308366___guide-item']"
                ))
            )
            
            input_elem = police_station_container.find_element(
                By.XPATH, 
                ".//input[@aria-label='Jurisdiction of Police Station']"
            )
            
            # Make input visible and interactive
            driver.execute_script("""
                var input = arguments[0];
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
                input.removeAttribute('aria-readonly');
            """, input_elem)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", police_station_container)
            time.sleep(0.5)
            
            police_station = partner.get("Jurisdiction of Police Station", "").strip()
            if police_station:
                # Validate max length (150 characters)
                if len(police_station) > 150:
                    print(f"[WARNING] Jurisdiction of Police Station exceeds maximum length of 150 characters: {police_station}")
                    police_station = police_station[:150]
                
                input_elem.clear()
                input_elem.send_keys(police_station)
                time.sleep(0.5)
                
                if input_elem.get_attribute('value') == police_station:
                    print(f"[SUCCESS] Filled: Jurisdiction of Police Station = {police_station}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Jurisdiction of Police Station = {police_station} (value mismatch)")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Jurisdiction of Police Station")
        except Exception as e:
            print(f"[FAIL] Error handling Jurisdiction of Police Station: {str(e)}")
            fields_failed_count += 1

        # Fill Phone (with STD/ISD code)
        try:
            phone_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy_165380706___guide-item']"
                ))
            )
            
            input_elem = phone_container.find_element(
                By.XPATH, 
                ".//input[@aria-label='Phone (with STD/ISD code)']"
            )
            
            # Make input visible and interactive
            driver.execute_script("""
                var input = arguments[0];
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
                input.removeAttribute('aria-readonly');
            """, input_elem)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_container)
            time.sleep(0.5)
            
            phone = partner.get("Phone (with STD/ISD code)", "").strip()
            if phone:
                # Validate max length (13 characters)
                if len(phone) > 13:
                    print(f"[WARNING] Phone number exceeds maximum length of 13 characters: {phone}")
                    phone = phone[:13]
                
                input_elem.clear()
                input_elem.send_keys(phone)
                time.sleep(0.5)
                
                if input_elem.get_attribute('value') == phone:
                    print(f"[SUCCESS] Filled: Phone (with STD/ISD code) = {phone}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Phone (with STD/ISD code) = {phone} (value mismatch)")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Phone (with STD/ISD code)")
        except Exception as e:
            print(f"[FAIL] Error handling Phone (with STD/ISD code): {str(e)}")
            fields_failed_count += 1

    except Exception as e:
        print(f"[ERROR] Error in fill_permanent_address: {str(e)}")
        fields_failed_count += 1

    return fields_filled_count, fields_failed_count

def set_dropdown_by_aria_label(driver, label, value, parent=None, timeout=15):
    """Set dropdown value by aria-label, robust for guideDropDownList structure with clear success/fail logs and debug info for failures."""
    try:
        if value:
            value_clean = value.strip()
            xpath = f'.//select[@aria-label="{label}"]' if parent else f'//select[@aria-label="{label}"]'
            # Step 1: Wait for presence
            try:
                if parent:
                    select_elem = WebDriverWait(parent, timeout).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                else:
                    select_elem = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
            except TimeoutException as e:
                print(f"[FAIL] Could not fill: {label} = {value_clean} | Reason: Dropdown not present in DOM after {timeout}s. Possible causes: dynamic dependency, wrong field type, or slow load.")
                # Print all selects for debugging
                selects = parent.find_elements(By.TAG_NAME, "select") if parent else driver.find_elements(By.TAG_NAME, "select")
                print(f"[DEBUG] Selects found: {[s.get_attribute('aria-label') for s in selects]}")
                # Try to check if it's an input instead
                try:
                    input_elem = driver.find_element(By.XPATH, f'//input[@aria-label="{label}"]')
                    print(f"[FAIL] Field '{label}' is an <input>, not a <select>. Use set_text_field_by_aria_label instead.")
                except Exception:
                    pass
                return False
            # Step 2: Wait for clickable
            try:
                if parent:
                    select_elem = WebDriverWait(parent, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                else:
                    select_elem = WebDriverWait(driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
            except TimeoutException as e:
                print(f"[FAIL] Could not fill: {label} = {value_clean} | Reason: Dropdown not clickable after {timeout}s. Possible causes: dynamic dependency, disabled field, or slow load.")
                return False
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_elem)
            select = Select(select_elem)
            # Do NOT call .clear() on <select> elements!
            # Try to select by value attribute (case-insensitive)
            for option in select.options:
                if option.get_attribute('value') and option.get_attribute('value').strip().lower() == value_clean.lower():
                    select.select_by_value(option.get_attribute('value'))
                    print(f"[SUCCESS] Filled: {label} = {option.text}")
                    time.sleep(0.5)
                    return True
            # Try to select by visible text (case-insensitive)
            for option in select.options:
                if option.text.strip().lower() == value_clean.lower():
                    select.select_by_visible_text(option.text)
                    print(f"[SUCCESS] Filled: {label} = {option.text}")
                    time.sleep(0.5)
                    return True
            # Try partial match (case-insensitive)
            for option in select.options:
                if value_clean.lower() in option.text.strip().lower() or option.text.strip().lower() in value_clean.lower():
                    select.select_by_visible_text(option.text)
                    print(f"[SUCCESS] Filled: {label} = {option.text}")
                    time.sleep(0.5)
                    return True
            print(f"[FAIL] Could not fill: {label} = {value_clean} | Reason: No matching option found. Available options:")
            for option in select.options:
                print(f"    Option: '{option.text}' (value: '{option.get_attribute('value')}')")
            return False
    except StaleElementReferenceException:
        print(f"[FAIL] Could not fill: {label} = {value if value else ''} | Reason: StaleElementReferenceException, retrying...")
        return set_dropdown_by_aria_label(driver, label, value, parent, timeout)
    except Exception as e:
        print(f"[FAIL] Could not fill: {label} = {value if value else ''} | Reason: {str(e)}")
        return False

def set_radio_button(driver, label, value, parent=None):
    """Set radio button value by label and value, robust for guideFieldNode structure with clear success/fail logs."""
    try:
        if value:
            value_clean = value.strip().capitalize()
            try:
                # First try to find the radio group within the parent if provided
                if parent:
                    radio_group = parent.find_element(By.XPATH, f".//div[contains(@class, 'guideFieldNode') and contains(@class, 'guideCheckBox')]//label[contains(text(), '{label}')]/ancestor::div[contains(@class, 'guideFieldNode')]")
                else:
                    radio_group = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'guideFieldNode') and contains(@class, 'guideCheckBox')]//label[contains(text(), '{label}')]/ancestor::div[contains(@class, 'guideFieldNode')]"))
                    )
            except Exception as e:
                print(f"[FAIL] Could not fill: {label} = {value_clean} | Reason: Radio group not found")
                return False

            try:
                # Find the radio input with the matching value
                radio_input = radio_group.find_element(By.XPATH, f".//input[@type='radio' and @aria-label='{value_clean}']")
                
                # Scroll the radio group into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_group)
                
                # Make sure the radio group and its container are visible
                driver.execute_script("""
                    var radioGroup = arguments[0];
                    var container = radioGroup.closest('.fd-col-lg-12');
                    
                    // Make container visible
                    container.style.display = 'block';
                    container.style.visibility = 'visible';
                    container.style.opacity = '1';
                    
                    // Make radio group visible
                    radioGroup.style.display = 'block';
                    radioGroup.style.visibility = 'visible';
                    radioGroup.style.opacity = '1';
                """, radio_group)
                
                # Remove readonly and disabled attributes
                driver.execute_script("""
                    var input = arguments[0];
                    input.removeAttribute('readonly');
                    input.removeAttribute('disabled');
                    input.removeAttribute('aria-readonly');
                """, radio_input)
                
                # Try clicking the radio input directly first
                try:
                    driver.execute_script("arguments[0].click();", radio_input)
                except Exception:
                    # If direct click fails, try clicking the label
                    input_id = radio_input.get_attribute('id')
                    label_elem = radio_group.find_element(By.XPATH, f".//label[@for='{input_id}']")
                    driver.execute_script("arguments[0].click();", label_elem)
                
                time.sleep(0.2)
                
                # Verify the selection
                if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                    print(f"[SUCCESS] Filled: {label} = {value_clean}")
                    return True
                else:
                    # If still not selected, try one more time with a different approach
                    driver.execute_script("""
                        var input = arguments[0];
                        input.checked = true;
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        input.dispatchEvent(new Event('click', { bubbles: true }));
                    """, radio_input)
                    
                    time.sleep(0.2)
                    
                    if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                        print(f"[SUCCESS] Filled: {label} = {value_clean} (after retry)")
                        return True
                    else:
                        print(f"[FAIL] Could not fill: {label} = {value_clean} | Reason: Not selected after click")
                        return False
                        
            except Exception as e:
                print(f"[FAIL] Could not fill: {label} = {value_clean} | Reason: Radio input not found or not clickable: {str(e)}")
                return False
    except Exception as e:
        print(f"[FAIL] Could not fill: {label} = {value if value else ''} | Reason: {str(e)}")
        return False

def set_date_field(driver, label, value, parent=None):
    """Set date field value by label"""
    try:
        if value:
            # Wait for date input
            date_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//label[text()='{label}']/ancestor::div[contains(@class, 'guidedatepicker')]//input"))
            )
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", date_input)
            
            # Get the input element's ID
            date_id = date_input.get_attribute('id')
            
            # Set the date using JavaScript
            js_script = f"""
                const input = document.getElementById('{date_id}');
                if (input) {{
                    input.removeAttribute('readonly');
                    input.focus();
                    input.value = '{value}';
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                    return input.value;
                }}
                return null;
            """
            
            result = driver.execute_script(js_script)
            if result == value:
                print(f"[+] {label} set to: {value}")
                return True
            else:
                print(f"[-] Could not set {label} to: {value}")
                return False
    except Exception as e:
        print(f"[ERROR] Could not fill {label}: {str(e)}")
        return False 

def fill_mobile_no(driver, value, parent=None):
    try:
        input_elem = None
        # Try with dot (correct for your HTML)
        try:
            if parent:
                input_elem = parent.find_element(By.XPATH, './/input[@aria-label="Mobile No."]')
            else:
                input_elem = driver.find_element(By.XPATH, '//input[@aria-label="Mobile No."]')
        except Exception:
            # Print all aria-labels for debugging
            inputs = parent.find_elements(By.TAG_NAME, "input") if parent else driver.find_elements(By.TAG_NAME, "input")
            print(f"[DEBUG] Inputs found: {[i.get_attribute('aria-label') for i in inputs]}")
            print(f"[FAIL] Could not find Mobile No. input")
            return False
        # 2. Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
        # 3. Remove readonly/disabled if present and set value using JS
        js = '''
            var input = arguments[0];
            input.removeAttribute('readonly');
            input.removeAttribute('disabled');
            input.value = '';
            input.value = arguments[1];
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new Event('blur', { bubbles: true }));
        '''
        driver.execute_script(js, input_elem, value)
        # 4. Wait and verify
        time.sleep(0.2)
        actual_value = input_elem.get_attribute('value')
        if actual_value == value:
            print(f"[SUCCESS] Filled: Mobile No. = {value}")
            return True
        else:
            print(f"[FAIL] Could not fill: Mobile No. = {value} | Reason: Value mismatch after JS injection")
            return False
    except Exception as e:
        print(f"[FAIL] Could not fill: Mobile No. = {value} | Reason: {str(e)}")
        return False 

def fill_additional_form_fields(driver, partner, fields_filled_count, fields_failed_count, parent=None):
    """Fill additional form fields"""
    try:
        # Determine search context
        search_context = parent if parent else driver
        
        # Fill form of contribution
        try:
            form_contribution_select = search_context.find_element(By.XPATH, './/select[@aria-label="Form of contribution"]')
            form_contribution = partner.get("Form of contribution", "").strip()
            if form_contribution:
                select = Select(form_contribution_select)
                select.select_by_visible_text(form_contribution)
                time.sleep(0.5)
                if select.first_selected_option.text == form_contribution:
                    print(f"[SUCCESS] Filled: Form of contribution = {form_contribution}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Form of contribution = {form_contribution}")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Form of contribution")
        except Exception as e:
            print(f"[FAIL] Error handling Form of contribution: {str(e)}")
            fields_failed_count += 1

        # Fill number of LLPs
        try:
            llp_count_input = search_context.find_element(By.XPATH, './/input[@aria-label="Number of LLPs"]')
            llp_count = partner.get("Number of LLPs", "").strip()
            if llp_count:
                llp_count_input.clear()
                llp_count_input.send_keys(llp_count)
                time.sleep(0.5)
                if llp_count_input.get_attribute('value') == llp_count:
                    print(f"[SUCCESS] Filled: Number of LLPs = {llp_count}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Number of LLPs = {llp_count}")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Number of LLPs")
        except Exception as e:
            print(f"[FAIL] Error handling Number of LLPs: {str(e)}")
            fields_failed_count += 1

    except Exception as e:
        print(f"[ERROR] Major error in fill_additional_form_fields: {str(e)}")
        fields_failed_count += 1

    return fields_filled_count, fields_failed_count

def fill_identity_proof(driver, partner, fields_filled_count, fields_failed_count, parent=None):
    """Fill identity and residential proof section"""
    try:
        # Wait for dynamic dependencies
        time.sleep(1)
        
        # Identity Proof - Using specific XPath
        try:
            # Find the container using exact XPath
            identity_proof_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1688891306-guidedropdownlist___guide-item']"
                ))
            )
            
            # Make sure the container is visible
            driver.execute_script("""
                var container = arguments[0];
                container.style.display = 'block';
                container.style.visibility = 'visible';
                container.style.opacity = '1';
                container.style.height = 'auto';
                container.style.overflow = 'visible';
            """, identity_proof_container)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", identity_proof_container)
            time.sleep(0.5)
            
            # Find the select element within the container
            select_elem = identity_proof_container.find_element(By.XPATH, ".//select[@aria-label='(iv) Identity Proof']")
            
            # Remove readonly and disabled attributes
            driver.execute_script("""
                var select = arguments[0];
                select.removeAttribute('readonly');
                select.removeAttribute('disabled');
                select.removeAttribute('aria-readonly');
                select.style.display = 'block';
                select.style.visibility = 'visible';
                select.style.opacity = '1';
            """, select_elem)

            # Get the value from partner data
            identity_proof = partner.get("Identity Proof", "").strip()
            if identity_proof:
                # Create Select object
                select = Select(select_elem)
                
                # Try multiple selection strategies
                try:
                    # Strategy 1: Select by visible text
                    select.select_by_visible_text(identity_proof)
                except:
                    try:
                        # Strategy 2: Select by value
                        select.select_by_value(identity_proof)
                    except:
                        try:
                            # Strategy 3: Case-insensitive partial match
                            for option in select.options:
                                if identity_proof.lower() in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    break
                        except:
                            print(f"[FAIL] Could not select Identity Proof: {identity_proof}")
                            raise Exception("Failed to select Identity Proof")
                
                time.sleep(0.5)
                
                # Verify the selection
                if select.first_selected_option.text.strip() == identity_proof:
                    print(f"[SUCCESS] Filled: Identity Proof = {identity_proof}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Identity Proof = {identity_proof} (selection mismatch)")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Identity Proof")
        except Exception as e:
            print(f"[FAIL] Error handling Identity Proof: {str(e)}")
            fields_failed_count += 1

        return fields_filled_count, fields_failed_count
    except Exception as e:
        print(f"[ERROR] Major error in fill_identity_proof: {str(e)}")
        fields_failed_count += 1
        return fields_filled_count, fields_failed_count

def fill_present_address(driver, partner, fields_filled_count, fields_failed_count, parent=None):
    """Fill present address section"""
    try:
        # First find the present address section
        if not parent:
            section_title = "Present Address"
            try:
                # Try multiple strategies to find the section
                section_element = None
                try:
                    # Strategy 1: Direct text match
                    section_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{section_title}')]"))
                    )
                except:
                    try:
                        # Strategy 2: Class-based search
                        section_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'guideFieldNode') and contains(@class, 'panel')]"))
                        )
                    except:
                        # Strategy 3: Generic panel search
                        section_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'panel')]"))
                        )
                
                if section_element:
                    parent = section_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'panel')]")
                else:
                    print(f"[ERROR] Could not find present address section")
                    return fields_filled_count, fields_failed_count
            except Exception as e:
                print(f"[ERROR] Could not find present address section: {str(e)}")
                return fields_filled_count, fields_failed_count

        # Handle "Whether present residential address same as permanent residential address" radio button
        try:
            # Find the radio button container using the specific XPath
            radio_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//*[@id='guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guideradiobutton___guide-item']"
                ))
            )
            
            # Make sure the container is visible
            driver.execute_script("""
                var container = arguments[0];
                container.style.display = 'block';
                container.style.visibility = 'visible';
                container.style.opacity = '1';
                container.style.height = 'auto';
                container.style.overflow = 'visible';
            """, radio_container)
            
            # Get the value from partner data
            same_address = partner.get("Whether present residential address same as permanent residential address", "").strip()
            if same_address:
                # Find the radio input with the matching value
                radio_input = radio_container.find_element(
                    By.XPATH, 
                    f".//input[@type='radio' and @aria-label='{same_address}']"
                )
                
                # Make sure the radio input is visible and interactive
                driver.execute_script("""
                    var input = arguments[0];
                    input.style.display = 'block';
                    input.style.visibility = 'visible';
                    input.style.opacity = '1';
                    input.removeAttribute('readonly');
                    input.removeAttribute('disabled');
                    input.removeAttribute('aria-readonly');
                """, radio_input)
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_container)
                time.sleep(0.5)
                
                # Try multiple click strategies
                try:
                    # Strategy 1: Click the label
                    label = radio_container.find_element(By.XPATH, f".//label[text()='{same_address}']")
                    driver.execute_script("arguments[0].click();", label)
                except:
                    try:
                        # Strategy 2: Direct click
                        driver.execute_script("arguments[0].click();", radio_input)
                    except:
                        try:
                            # Strategy 3: Set checked property
                            driver.execute_script("""
                                var input = arguments[0];
                                input.checked = true;
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                input.dispatchEvent(new Event('click', { bubbles: true }));
                            """, radio_input)
                        except:
                            print("[DEBUG] All click strategies failed")
                            raise Exception("Could not click radio button")
                
                time.sleep(0.5)
                
                # Verify the selection
                if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                    print(f"[SUCCESS] Filled: Whether present residential address same as permanent residential address = {same_address}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Whether present residential address same as permanent residential address = {same_address}")
                    fields_failed_count += 1
            else:
                print(f"[INFO] No value provided for Whether present residential address same as permanent residential address")
        except Exception as e:
            print(f"[FAIL] Error handling Whether present residential address same as permanent residential address: {str(e)}")
            fields_failed_count += 1

        # If address is not same as permanent address, fill the present address fields
        if same_address and same_address.lower() != "yes":
            # Fill Address Line I
            try:
                address_line1 = partner.get("Present Address Line I", "").strip()
                if address_line1:
                    if set_text_field_by_aria_label(driver, "Present Address Line I", address_line1, parent):
                        fields_filled_count += 1
                    else:
                        fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Error handling Present Address Line I: {str(e)}")
                fields_failed_count += 1

            # Fill Address Line II
            try:
                address_line2 = partner.get("Present Address Line II", "").strip()
                if address_line2:
                    if set_text_field_by_aria_label(driver, "Present Address Line II", address_line2, parent):
                        fields_filled_count += 1
                    else:
                        fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Error handling Present Address Line II: {str(e)}")
                fields_failed_count += 1

            # Fill Country
            try:
                country = partner.get("Present Country", "").strip()
                if country:
                    if set_dropdown_by_aria_label(driver, "Present Country", country, parent):
                        fields_filled_count += 1
                    else:
                        fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Error handling Present Country: {str(e)}")
                fields_failed_count += 1

            # Fill Pin code / Zip Code
            try:
                pincode = partner.get("Present Pin code / Zip Code", "").strip()
                if pincode:
                    if set_text_field_by_aria_label(driver, "Present Pin code / Zip Code", pincode, parent):
                        fields_filled_count += 1
                    else:
                        fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Error handling Present Pin code / Zip Code: {str(e)}")
                fields_failed_count += 1

            # Fill Area/ Locality
            try:
                area = partner.get("Present Area/ Locality", "").strip()
                if area:
                    if set_dropdown_by_aria_label(driver, "Present Area/ Locality", area, parent):
                        fields_filled_count += 1
                    else:
                        fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Error handling Present Area/ Locality: {str(e)}")
                fields_failed_count += 1

            # Fill Jurisdiction of Police Station
            try:
                police_station = partner.get("Present Jurisdiction of Police Station", "").strip()
                if police_station:
                    if set_text_field_by_aria_label(driver, "Present Jurisdiction of Police Station", police_station, parent):
                        fields_filled_count += 1
                    else:
                        fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Error handling Present Jurisdiction of Police Station: {str(e)}")
                fields_failed_count += 1

            # Fill Phone (with STD/ISD code)
            try:
                phone = partner.get("Present Phone (with STD/ISD code)", "").strip()
                if phone:
                    if set_text_field_by_aria_label(driver, "Present Phone (with STD/ISD code)", phone, parent):
                        fields_filled_count += 1
                    else:
                        fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Error handling Present Phone (with STD/ISD code): {str(e)}")
                fields_failed_count += 1

    except Exception as e:
        print(f"[ERROR] Error in fill_present_address: {str(e)}")
        fields_failed_count += 1

    return fields_filled_count, fields_failed_count

def set_text_field_by_aria_label(driver, label, value, parent=None, timeout=15):
    """Set text field value by aria-label with robust error handling and validation"""
    try:
        if value:
            value_clean = value.strip()
            xpath = f'.//input[@aria-label="{label}"]' if parent else f'//input[@aria-label="{label}"]'
            
            # Step 1: Wait for presence
            try:
                if parent:
                    input_elem = WebDriverWait(parent, timeout).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                else:
                    input_elem = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
            except TimeoutException as e:
                print(f"[FAIL] Could not fill: {label} = {value_clean} | Reason: Input field not present in DOM after {timeout}s")
                # Print all inputs for debugging
                inputs = parent.find_elements(By.TAG_NAME, "input") if parent else driver.find_elements(By.TAG_NAME, "input")
                print(f"[DEBUG] Inputs found: {[i.get_attribute('aria-label') for i in inputs]}")
                return False

            # Step 2: Wait for clickable
            try:
                if parent:
                    input_elem = WebDriverWait(parent, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                else:
                    input_elem = WebDriverWait(driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
            except TimeoutException as e:
                print(f"[FAIL] Could not fill: {label} = {value_clean} | Reason: Input field not clickable after {timeout}s")
                return False

            # Step 3: Make element visible and interactive
            driver.execute_script("""
                var input = arguments[0];
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
                input.removeAttribute('aria-readonly');
            """, input_elem)

            # Step 4: Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
            time.sleep(0.5)  # Wait for scroll to complete

            # Step 5: Clear existing value
            try:
                input_elem.clear()
            except:
                # If clear() fails, try JavaScript clear
                driver.execute_script("arguments[0].value = '';", input_elem)

            # Step 6: Set value using multiple strategies
            success = False
            
            # Strategy 1: Direct send_keys
            try:
                input_elem.send_keys(value_clean)
                time.sleep(0.5)
                if input_elem.get_attribute('value') == value_clean:
                    success = True
            except:
                pass

            # Strategy 2: JavaScript value setting
            if not success:
                try:
                    driver.execute_script("""
                        var input = arguments[0];
                        input.value = arguments[1];
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        input.dispatchEvent(new Event('blur', { bubbles: true }));
                    """, input_elem, value_clean)
                    time.sleep(0.5)
                    if input_elem.get_attribute('value') == value_clean:
                        success = True
                except:
                    pass

            # Strategy 3: Focus and send_keys
            if not success:
                try:
                    input_elem.click()
                    input_elem.send_keys(Keys.CONTROL + "a")  # Select all
                    input_elem.send_keys(Keys.DELETE)  # Delete selection
                    input_elem.send_keys(value_clean)
                    time.sleep(0.5)
                    if input_elem.get_attribute('value') == value_clean:
                        success = True
                except:
                    pass

            # Verify the value was set
            if success:
                print(f"[SUCCESS] Filled: {label} = {value_clean}")
                return True
            else:
                print(f"[FAIL] Could not fill: {label} = {value_clean} | Reason: Value mismatch after all strategies")
                print(f"[DEBUG] Current value: {input_elem.get_attribute('value')}")
                return False

    except StaleElementReferenceException:
        print(f"[FAIL] Could not fill: {label} = {value if value else ''} | Reason: StaleElementReferenceException, retrying...")
        return set_text_field_by_aria_label(driver, label, value, parent, timeout)
    except Exception as e:
        print(f"[FAIL] Could not fill: {label} = {value if value else ''} | Reason: {str(e)}")
        return False
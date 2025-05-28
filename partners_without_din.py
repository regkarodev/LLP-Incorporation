from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import json
import function1
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

def handle_partners_without_din(driver, config_data, config_selectors):
    """
    Handle filling details for partners without DIN/DPIN
    """
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

        # Ensure we iterate at least num_partners_no_din times
        iterations = max(num_partners_no_din, len(partners_no_din))
        
        # Fill each partner's subform
        for idx in range(iterations):
            print(f'\n[LOG] ========== Filling Partner {idx+1} without DIN/DPIN ==========')
            
            # Get partner data for this index, use empty dict if index exceeds available data
            partner = partners_no_din[idx] if idx < len(partners_no_din) else {}
            position = idx + 1
            fields_filled_count = 0
            fields_failed_count = 0

            try:
                # Find the form by text
                section_title = "Particulars of individual designated partners not having DIN/DPIN"
                
                # Wait for the section title to be present and find the first occurrence
                section_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{section_title}')]"))
                )
                
                # Get the parent div containing the form
                parent_div = section_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'panel')]")
                
                if parent_div:
                    print(f"[LOG] Found parent div for partner {position}")
                    
                    # Find all input elements within the parent div
                    input_elements = parent_div.find_elements(By.TAG_NAME, "input")
                    
                    if input_elements:
                        # Get the first input element
                        first_input = input_elements[0]
                        
                        # Scroll to the first input element
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_input)
                    
                    # (i) Personal Information
                    print("\n[LOG] Filling Personal Information...")
                    fields_filled_count, fields_failed_count = fill_personal_information(driver, partner, fields_filled_count, fields_failed_count, parent_div)
                    
                    # (ii) Permanent Address
                    print("\n[LOG] Filling Permanent Address...")
                    fields_filled_count, fields_failed_count = fill_permanent_address(driver, partner, fields_filled_count, fields_failed_count, parent_div)
                    
                    # (iii) Present Address
                    print("\n[LOG] Filling Present Address...")
                    fields_filled_count, fields_failed_count = fill_present_address(driver, partner, fields_filled_count, fields_failed_count)
                    
                    # (iv) Identity and Residential Proof
                    print("\n[LOG] Filling Identity and Residential Proof...")
                    fields_filled_count, fields_failed_count = fill_identity_proof(driver, partner, fields_filled_count, fields_failed_count, parent_div)

                    if fields_filled_count > 0:
                        print(f"\n[SUCCESS] ✓ Partner {position} form filled: {fields_filled_count} fields filled, {fields_failed_count} failed")
                        total_fields_filled += fields_filled_count
                        total_fields_failed += fields_failed_count
                    else:
                        print(f"\n[WARNING] ⚠️ Partner {position} form not filled: No fields were successfully filled")
                        total_fields_failed += 1
                else:
                    print(f"[ERROR] No input elements found in the parent div for partner {position}")
                    total_fields_failed += 1

                time.sleep(1)  # Wait between partners

            except Exception as e:
                print(f"[ERROR] Failed to process partner {position}: {str(e)}")
                total_fields_failed += 1

        print(f"\n[LOG] ========== Completed all {iterations} partners without DIN/DPIN ==========")
        print(f"Total fields filled: {total_fields_filled}")
        print(f"Total fields failed: {total_fields_failed}")
        
    except Exception as e:
        print(f"[ERROR] An error occurred in handle_partners_without_din: {str(e)}")
        import traceback
        traceback.print_exc()

def normalize_options_dict(options_dict):
    """Convert string 'True'/'False' to boolean True/False in options_dict."""
    normalized = {}
    for k, v in options_dict.items():
        if isinstance(v, dict):
            normalized[k] = {opt: (val is True or (isinstance(val, str) and val.lower() == "true")) for opt, val in v.items()}
        else:
            normalized[k] = v
    return normalized

def fill_personal_information(driver, partner, fields_filled_count, fields_failed_count, parent=None):
    """Fill personal information section"""
    try:
        # Name fields
        name_fields = {
            "First Name": "First Name",
            "Middle Name": "Middle Name",
            "Surname": "Surname",
            "Father's First Name": "Father Name",
            "Father's Middle Name": "Father Middle Name",
            "Father's Surname": "Father Surname"
        }
        
        for aria_label, field_key in name_fields.items():
            if set_text_field_by_aria_label(driver, aria_label, partner.get(field_key, ''), parent):
                fields_filled_count += 1
            else:
                # Fallback: try dropdown if not an input field
                print(f"[DEBUG] Trying dropdown fallback for {aria_label}")
                if set_dropdown_by_aria_label(driver, aria_label, partner.get(field_key, ''), parent):
                    fields_filled_count += 1
                else:
                    fields_failed_count += 1

        # Gender
        if set_dropdown_by_aria_label(driver, "Gender", partner.get("Gender", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # Date of Birth
        if set_date_field(driver, "Date of Birth", partner.get("Date of Birth", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # Nationality
        if set_dropdown_by_aria_label(driver, "Nationality", partner.get("Nationality", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # Whether resident of India
        if 'options' in partner and 'Whether resident of India' in partner['options']:
            normalized_options = normalize_options_dict(partner['options'])
            try:
                # Find the specific container using the exact XPath
                container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidecheckbox_copy_c_1044176976___guide-item"]'))
                )
                
                # Make sure the container is visible
                driver.execute_script("""
                    var container = arguments[0];
                    container.style.display = 'block';
                    container.style.visibility = 'visible';
                    container.style.opacity = '1';
                    container.style.height = 'auto';
                    container.style.overflow = 'visible';
                """, container)
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
                time.sleep(0.5)
                
                # Find the true option from normalized options
                true_option = None
                for option, value in normalized_options.get("Whether resident of India", {}).items():
                    if value is True:
                        true_option = option
                        break
                
                if true_option:
                    # Find and click the radio input with the matching aria-label
                    radio_input = container.find_element(By.XPATH, f".//input[@type='radio' and @aria-label='{true_option}']")
                    
                    # Remove readonly and disabled attributes
                    driver.execute_script("""
                        var input = arguments[0];
                        input.removeAttribute('readonly');
                        input.removeAttribute('disabled');
                        input.removeAttribute('aria-readonly');
                        input.style.display = 'block';
                        input.style.visibility = 'visible';
                        input.style.opacity = '1';
                    """, radio_input)
                    
                    # Click the radio input
                    driver.execute_script("arguments[0].click();", radio_input)
                    time.sleep(0.5)
                    
                    # Verify the selection
                    if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                        print(f"[SUCCESS] Filled: Whether resident of India = {true_option}")
                        fields_filled_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Whether resident of India = {true_option}")
                        fields_failed_count += 1
                else:
                    print("[FAIL] No true option found for Whether resident of India")
                    fields_failed_count += 1
                    
            except Exception as e:
                print(f"[FAIL] Error handling Whether resident of India: {str(e)}")
                fields_failed_count += 1
        else:
            fields_failed_count += 1

        # Income-tax PAN/Passport number
        if 'options' in partner and 'Income-tax PAN/Passport number' in partner['options']:
            normalized_options = normalize_options_dict(partner['options'])
            if function1.click_true_option(
                driver,
                "Income-tax PAN/Passport number",
                normalized_options,
                section_heading="Particulars of individual designated partners not having DIN/DPIN"
            ):
                fields_filled_count += 1
            else:
                fields_failed_count += 1
        else:
            if set_radio_button(driver, "Income-tax PAN/Passport number", partner.get("Income-tax PAN/Passport number", ""), parent):
                fields_filled_count += 1
            else:
                fields_failed_count += 1

        # Income-tax PAN/Passport number details
        if set_text_field_by_aria_label(driver, "Income-tax PAN/Passport number details", partner.get("Income-tax PAN/Passport number details", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # Place of Birth
        if set_dropdown_by_aria_label(driver, "Place of Birth (State)", partner.get("Place of Birth (State)", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1
        # Wait for dependent dropdown to populate if needed
        time.sleep(0.5)
        if set_dropdown_by_aria_label(driver, "Place of Birth (District)", partner.get("Place of Birth (District)", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # Whether citizen of India
        if 'options' in partner and 'Whether citizen of India' in partner['options']:
            normalized_options = normalize_options_dict(partner['options'])
            if function1.click_true_option(
                driver,
                "Whether citizen of India",
                normalized_options,
                section_heading="Particulars of individual designated partners not having DIN/DPIN"
            ):
                fields_filled_count += 1
            else:
                fields_failed_count += 1
        else:
            fields_failed_count += 1

        # Occupation type
        if set_dropdown_by_aria_label(driver, "Occupation type", partner.get("Occupation type", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # Area of Occupation
        if set_dropdown_by_aria_label(driver, "Area of Occupation", partner.get("Area of Occupation", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # Description of others
        if partner.get("Occupation type", "").lower() == "others":
            if set_text_field_by_aria_label(driver, "Description of others", partner.get("Description of others", ""), parent):
                fields_filled_count += 1
            else:
                fields_failed_count += 1

        # Educational qualification
        if set_dropdown_by_aria_label(driver, "Educational qualification", partner.get("Educational qualification", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # If 'Others' selected, please specify
        if partner.get("Educational qualification", "").lower() == "others":
            if set_text_field_by_aria_label(driver, "If 'Others' selected, please specify", partner.get("If 'Others' selected, please specify", ""), parent):
                fields_filled_count += 1
            else:
                fields_failed_count += 1

        # Contact Information
        time.sleep(1)
        if fill_mobile_no(driver, partner.get("Mobile No", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # Email ID
        if set_text_field_by_aria_label(driver, "Email ID", partner.get("Email ID", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

    except Exception as e:
        print(f"[ERROR] Error in fill_personal_information: {str(e)}")
        fields_failed_count += 1

    return fields_filled_count, fields_failed_count

def fill_permanent_address(driver, partner, fields_filled_count, fields_failed_count, parent=None):
    """Fill permanent address section"""
    try:
        # First find the permanent address section
        if not parent:
            section_title = "Permanent Address"
            try:
                section_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{section_title}')]"))
                )
                parent = section_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'panel')]")
            except Exception as e:
                print(f"[ERROR] Could not find permanent address section: {str(e)}")
                return fields_filled_count, fields_failed_count

        # Fill address fields in correct order to handle dependencies
        address_fields = {
            "Address Line I": "Permanent Address Line I",
            "Country": "Permanent Country",
            "Pin code / Zip Code": "Pin code / Zip Code",
            "Area/ Locality": "Permanent Area/ Locality"
        }

        # First fill the basic fields, always scoped to parent
        for aria_label, field_key in address_fields.items():
            if set_text_field_by_aria_label(driver, aria_label, partner.get(field_key, ''), parent):
                fields_filled_count += 1
            else:
                print(f"[DEBUG] Trying dropdown fallback for {aria_label} in Permanent Address section")
                if set_dropdown_by_aria_label(driver, aria_label, partner.get(field_key, ''), parent):
                    fields_filled_count += 1
                else:
                    fields_failed_count += 1
            time.sleep(0.5)  # Wait for dynamic updates

        # Permanent Address Line II - Using specific XPath
        try:
            # Find the container using exact XPath
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy___guide-item"]'))
            )
            
            # Make sure the container is visible
            driver.execute_script("""
                var container = arguments[0];
                container.style.display = 'block';
                container.style.visibility = 'visible';
                container.style.opacity = '1';
                container.style.height = 'auto';
                container.style.overflow = 'visible';
            """, container)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
            time.sleep(0.5)
            
            # Find the input field within the container
            input_field = container.find_element(By.XPATH, ".//input")
            
            # Remove readonly and disabled attributes
            driver.execute_script("""
                var input = arguments[0];
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
                input.removeAttribute('aria-readonly');
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
            """, input_field)
            
            # Set the value using JavaScript
            value = partner.get("Permanent Address Line II", "")
            driver.execute_script("""
                var input = arguments[0];
                var value = arguments[1];
                input.value = value;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.dispatchEvent(new Event('blur', { bubbles: true }));
            """, input_field, value)
            
            time.sleep(0.5)
            
            # Verify the value was set
            if input_field.get_attribute('value') == value:
                print(f"[SUCCESS] Filled: Permanent Address Line II = {value}")
                fields_filled_count += 1
            else:
                print(f"[FAIL] Could not fill: Permanent Address Line II = {value}")
                fields_failed_count += 1
                
        except Exception as e:
            print(f"[FAIL] Error handling Permanent Address Line II: {str(e)}")
            fields_failed_count += 1

        # City, District, State are auto-populated based on pincode
        # Just verify they are filled
        auto_fields = ["City", "District", "State / UT"]
        for field in auto_fields:
            try:
                if parent:
                    input_elem = parent.find_element(By.XPATH, f'.//input[@aria-label="{field}"]')
                else:
                    input_elem = driver.find_element(By.XPATH, f'//input[@aria-label="{field}"]')
                if input_elem.get_attribute('value'):
                    print(f"[SUCCESS] Auto-filled: {field}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not auto-fill: {field}")
                    fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Could not verify auto-fill for {field}: {str(e)}")
                fields_failed_count += 1

        # Fill remaining fields
        remaining_fields = {
            "Jurisdiction of Police Station": "Permanent Jurisdiction of Police Station"
        }

        for aria_label, field_key in remaining_fields.items():
            if set_text_field_by_aria_label(driver, aria_label, partner.get(field_key, ''), parent):
                fields_filled_count += 1
            else:
                print(f"[DEBUG] Trying dropdown fallback for {aria_label}")
                if set_dropdown_by_aria_label(driver, aria_label, partner.get(field_key, ''), parent):
                    fields_filled_count += 1
                else:
                    fields_failed_count += 1
            time.sleep(0.5)  # Wait between fields

        # Phone (with STD/ISD code) - Using specific XPath
        try:
            # Find the container using exact XPath
            phone_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy_165380706___guide-item"]'))
            )
            
            # Make sure the container is visible
            driver.execute_script("""
                var container = arguments[0];
                container.style.display = 'block';
                container.style.visibility = 'visible';
                container.style.opacity = '1';
                container.style.height = 'auto';
                container.style.overflow = 'visible';
            """, phone_container)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_container)
            time.sleep(0.5)
            
            # Find the input field within the container
            phone_input = phone_container.find_element(By.XPATH, ".//input")
            
            # Remove readonly and disabled attributes
            driver.execute_script("""
                var input = arguments[0];
                input.removeAttribute('readonly');
                input.removeAttribute('disabled');
                input.removeAttribute('aria-readonly');
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
            """, phone_input)
            
            # Set the value using JavaScript
            phone_value = partner.get("Phone (with STD/ISD code)", "")
            driver.execute_script("""
                var input = arguments[0];
                var value = arguments[1];
                input.value = value;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.dispatchEvent(new Event('blur', { bubbles: true }));
            """, phone_input, phone_value)
            
            time.sleep(0.5)
            
            # Verify the value was set
            if phone_input.get_attribute('value') == phone_value:
                print(f"[SUCCESS] Filled: Phone (with STD/ISD code) = {phone_value}")
                fields_filled_count += 1
            else:
                print(f"[FAIL] Could not fill: Phone (with STD/ISD code) = {phone_value}")
                fields_failed_count += 1
                
        except Exception as e:
            print(f"[FAIL] Error handling Phone (with STD/ISD code): {str(e)}")
            fields_failed_count += 1

    except Exception as e:
        print(f"[ERROR] Error in fill_permanent_address: {str(e)}")
        fields_failed_count += 1

    return fields_filled_count, fields_failed_count

def fill_present_address(driver, partner, fields_filled_count, fields_failed_count):
    """Fill present address section"""
    try:
        # Whether present residential address same as permanent residential address
        if 'options' in partner and 'Same address' in partner['options']:
            normalized_options = normalize_options_dict(partner['options'])
            try:
                # Find the container using exact XPath
                container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guideradiobutton___guide-item"]'))
                )
                
                # Make sure the container is visible
                driver.execute_script("""
                    var container = arguments[0];
                    container.style.display = 'block';
                    container.style.visibility = 'visible';
                    container.style.opacity = '1';
                    container.style.height = 'auto';
                    container.style.overflow = 'visible';
                """, container)
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
                time.sleep(0.5)
                
                # Find the true option from normalized options
                true_option = None
                for option, value in normalized_options.get("Same address", {}).items():
                    if value is True:
                        true_option = option
                        break
                
                if true_option:
                    # Find and click the radio input with the matching aria-label
                    radio_input = container.find_element(By.XPATH, f".//input[@type='radio' and @aria-label='{true_option}']")
                    
                    # Remove readonly and disabled attributes
                    driver.execute_script("""
                        var input = arguments[0];
                        input.removeAttribute('readonly');
                        input.removeAttribute('disabled');
                        input.removeAttribute('aria-readonly');
                        input.style.display = 'block';
                        input.style.visibility = 'visible';
                        input.style.opacity = '1';
                    """, radio_input)
                    
                    # Click the radio input
                    driver.execute_script("arguments[0].click();", radio_input)
                    time.sleep(0.5)
                    
                    # Verify the selection
                    if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                        print(f"[SUCCESS] Filled: Whether present residential address same as permanent residential address = {true_option}")
                        fields_filled_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Whether present residential address same as permanent residential address = {true_option}")
                        fields_failed_count += 1
                else:
                    print("[FAIL] No true option found for Same_address")
                    fields_failed_count += 1
                    
            except Exception as e:
                print(f"[FAIL] Error handling Same_address: {str(e)}")
                fields_failed_count += 1
        else:
            fields_failed_count += 1

        # If not same as permanent address, fill present address fields
        if 'options' in partner and 'Same address' in partner['options'] and normalized_options.get("Same address", {}).get("No", False):
            # Present Address Line II - Using specific XPath
            try:
                # Find the container using exact XPath
                container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy___guide-item"]'))
                )
                
                # Make sure the container is visible
                driver.execute_script("""
                    var container = arguments[0];
                    container.style.display = 'block';
                    container.style.visibility = 'visible';
                    container.style.opacity = '1';
                    container.style.height = 'auto';
                    container.style.overflow = 'visible';
                """, container)
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
                time.sleep(0.5)
                
                # Find the input field within the container
                input_field = container.find_element(By.XPATH, ".//input")
                
                # Remove readonly and disabled attributes
                driver.execute_script("""
                    var input = arguments[0];
                    input.removeAttribute('readonly');
                    input.removeAttribute('disabled');
                    input.removeAttribute('aria-readonly');
                    input.style.display = 'block';
                    input.style.visibility = 'visible';
                    input.style.opacity = '1';
                """, input_field)
                
                # Set the value using JavaScript
                value = partner.get("Present Address Line II", "")
                driver.execute_script("""
                    var input = arguments[0];
                    var value = arguments[1];
                    input.value = value;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    input.dispatchEvent(new Event('blur', { bubbles: true }));
                """, input_field, value)
                
                time.sleep(0.5)
                
                # Verify the value was set
                if input_field.get_attribute('value') == value:
                    print(f"[SUCCESS] Filled: Present Address Line II = {value}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Present Address Line II = {value}")
                    fields_failed_count += 1
                    
            except Exception as e:
                print(f"[FAIL] Error handling Present Address Line II: {str(e)}")
                fields_failed_count += 1

            # Fill remaining address fields
            address_fields = {
                "Address Line I": "Present Address Line I",
                "Country": "Present Country",
                "Pin code / Zip Code": "Present Pin code",
                "Area/ Locality": "Present Area/ Locality",
                "City": "Present City",
                "District": "Present District",
                "State / UT": "Present State / UT",
                "Jurisdiction of Police Station": "Present Jurisdiction of Police Station"
            }

            for aria_label, field_key in address_fields.items():
                if set_text_field_by_aria_label(driver, aria_label, partner.get(field_key, '')):
                    fields_filled_count += 1
                else:
                    fields_failed_count += 1

            # Phone (with STD/ISD code) - Using specific XPath
            try:
                # Find the container using exact XPath
                phone_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy_165380706___guide-item"]'))
                )
                
                # Make sure the container is visible
                driver.execute_script("""
                    var container = arguments[0];
                    container.style.display = 'block';
                    container.style.visibility = 'visible';
                    container.style.opacity = '1';
                    container.style.height = 'auto';
                    container.style.overflow = 'visible';
                """, phone_container)
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_container)
                time.sleep(0.5)
                
                # Find the input field within the container
                phone_input = phone_container.find_element(By.XPATH, ".//input")
                
                # Remove readonly and disabled attributes
                driver.execute_script("""
                    var input = arguments[0];
                    input.removeAttribute('readonly');
                    input.removeAttribute('disabled');
                    input.removeAttribute('aria-readonly');
                    input.style.display = 'block';
                    input.style.visibility = 'visible';
                    input.style.opacity = '1';
                """, phone_input)
                
                # Set the value using JavaScript
                phone_value = partner.get("Present Phone", "")
                driver.execute_script("""
                    var input = arguments[0];
                    var value = arguments[1];
                    input.value = value;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    input.dispatchEvent(new Event('blur', { bubbles: true }));
                """, phone_input, phone_value)
                
                time.sleep(0.5)
                
                # Verify the value was set
                if phone_input.get_attribute('value') == phone_value:
                    print(f"[SUCCESS] Filled: Phone (with STD/ISD code) = {phone_value}")
                    fields_filled_count += 1
                else:
                    print(f"[FAIL] Could not fill: Phone (with STD/ISD code) = {phone_value}")
                    fields_failed_count += 1
                    
            except Exception as e:
                print(f"[FAIL] Error handling Phone (with STD/ISD code): {str(e)}")
                fields_failed_count += 1

            # Duration of stay
            if set_text_field_by_aria_label(driver, "Years", partner.get("Duration Years", "")):
                fields_filled_count += 1
            else:
                fields_failed_count += 1

            if set_text_field_by_aria_label(driver, "Months", partner.get("Duration Months", "")):
                fields_filled_count += 1
            else:
                fields_failed_count += 1

    except Exception as e:
        print(f"[ERROR] Error in fill_present_address: {str(e)}")
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
            container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1688891306-guidedropdownlist___guide-item"]'))
            )
            
            # Make sure the container is visible
            driver.execute_script("""
                var container = arguments[0];
                container.style.display = 'block';
                container.style.visibility = 'visible';
                container.style.opacity = '1';
                container.style.height = 'auto';
                container.style.overflow = 'visible';
            """, container)
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
            time.sleep(0.5)
            
            # Find the select element within the container
            select_elem = container.find_element(By.XPATH, ".//select")
            
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
            identity_proof = partner.get("Identity Proof", "")
            if identity_proof:
                # Create Select object
                select = Select(select_elem)
                
                # Try to select by visible text
                try:
                    select.select_by_visible_text(identity_proof)
                    time.sleep(0.5)
                    
                    # Verify the selection
                    if select.first_selected_option.text == identity_proof:
                        print(f"[SUCCESS] Filled: Identity Proof = {identity_proof}")
                        fields_filled_count += 1
                    else:
                        print(f"[FAIL] Could not fill: Identity Proof = {identity_proof}")
                        fields_failed_count += 1
                except Exception as e:
                    print(f"[FAIL] Error selecting Identity Proof: {str(e)}")
                    fields_failed_count += 1
            else:
                print("[FAIL] No Identity Proof value provided")
                fields_failed_count += 1
                
        except Exception as e:
            print(f"[FAIL] Error handling Identity Proof: {str(e)}")
            fields_failed_count += 1

        # Residential Proof
        if set_dropdown_by_aria_label(driver, "Residential Proof", partner.get("Residential Proof", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # Identity Proof No.
        time.sleep(1)
        if set_text_field_by_aria_label(driver, "Identity Proof No.", partner.get("Identity Proof No.", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # Residential Proof No.
        if set_text_field_by_aria_label(driver, "Residential Proof No.", partner.get("Residential Proof No.", ""), parent):
            fields_filled_count += 1
        else:
            fields_failed_count += 1

        # File uploads would be handled separately
        # Proof of identity
        # Residential proof

    except Exception as e:
        print(f"[ERROR] Error in fill_identity_proof: {str(e)}")
        fields_failed_count += 1

    return fields_filled_count, fields_failed_count

def set_readonly_input(driver, element, value):
    driver.execute_script("arguments[0].removeAttribute('readonly');", element)
    element.clear()
    element.send_keys(value)

def set_pan_details_and_verify(driver, value, parent=None):
    """Set PAN/Passport number details and click Verify PAN button robustly."""
    try:
        # 1. Find the input by aria-label (with trailing space)
        input_elem = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@aria-label="Income-tax PAN/Passport number details "]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)

        # 2. Set value using advanced JS
        driver.execute_script('''
            const input = arguments[0];
            const val = arguments[1];
            input.removeAttribute('readonly');
            input.focus();
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(input, val);
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new Event('blur', { bubbles: true }));
        ''', input_elem, value)
        time.sleep(0.5)

        # 3. Find the Verify PAN button by aria-label or text
        try:
            fd_row = input_elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'fd-row')]")
            verify_btn = fd_row.find_element(By.XPATH, ".//button[@aria-label='Verify PAN' or contains(., 'Verify PAN')]")
            if verify_btn.is_displayed() and verify_btn.is_enabled():
                verify_btn.click()
                print("[LOG] Clicked Verify PAN button.")
                time.sleep(1)
            else:
                print("[LOG] Verify PAN button not clickable.")
        except Exception as e:
            print(f"[LOG] Could not click Verify PAN button: {str(e)}")

        # 4. Optionally, check if the value stuck
        actual_value = input_elem.get_attribute('value')
        if actual_value == value:
            print("[SUCCESS] PAN/Passport number details set and verified.")
            return True
        else:
            print("[FAIL] PAN/Passport number details did not stick.")
            return False
    except Exception as e:
        print(f"[ERROR] PAN/Passport number details automation failed: {str(e)}")
        return False

def set_text_field_by_aria_label(driver, label, value, parent=None):
    """Set text field value by aria-label, with fallback to id if aria-label fails (handles trailing spaces)."""
    try:
        if value:
            if label.strip().lower().startswith("income-tax pan/passport number details"):
                return set_pan_details_and_verify(driver, value, parent)
            input_elem = None
            try:
                if parent:
                    input_elem = WebDriverWait(parent, 3).until(
                        EC.element_to_be_clickable((By.XPATH, f'.//input[@aria-label="{label}"]'))
                    )
                else:
                    input_elem = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, f'//input[@aria-label="{label}"]'))
                    )
            except Exception:
                try:
                    if parent:
                        input_elem = WebDriverWait(parent, 2).until(
                            EC.element_to_be_clickable((By.XPATH, f'.//input[@aria-label="{label.strip()}"]'))
                        )
                    else:
                        input_elem = WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, f'//input[@aria-label="{label.strip()}"]'))
                        )
                except Exception:
                    try:
                        if parent:
                            label_elem = parent.find_element(By.XPATH, f'.//label[normalize-space(text())="{label.strip()}"]')
                        else:
                            label_elem = driver.find_element(By.XPATH, f'//label[normalize-space(text())="{label.strip()}"]')
                        input_id = label_elem.get_attribute('for')
                        if parent:
                            input_elem = parent.find_element(By.ID, input_id)
                        else:
                            input_elem = driver.find_element(By.ID, input_id)
                    except Exception:
                        print(f"[FAIL] Could not fill: {label} = {value} | Reason: Input not found")
                        return False

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)

            tag = input_elem.tag_name.lower()
            if tag != "input":
                print(f"[FAIL] {label} is not an input field, skipping JS injection.")
                return False

            # Special handling for Phone (with STD/ISD code)
            if label.strip() == "Phone (with STD/ISD code)":
                try:
                    # Force the field to be visible and enabled
                    driver.execute_script("""
                        var input = arguments[0];
                        var container = input.closest('.guideFieldNode');
                        var parentContainer = container.closest('.fd-col-lg-4');
                        
                        // Make all parent containers visible
                        parentContainer.style.display = 'block';
                        parentContainer.style.visibility = 'visible';
                        parentContainer.style.opacity = '1';
                        
                        // Make the field container visible
                        container.style.display = 'block';
                        container.style.visibility = 'visible';
                        container.style.opacity = '1';
                        
                        // Make the input visible and enabled
                        input.style.display = 'block';
                        input.style.visibility = 'visible';
                        input.style.opacity = '1';
                        input.removeAttribute('disabled');
                        input.removeAttribute('readonly');
                        input.removeAttribute('aria-readonly');
                    """, input_elem)
                    
                    # Clear existing value
                    driver.execute_script("arguments[0].value = '';", input_elem)
                    time.sleep(0.2)
                    
                    # Set new value using multiple methods
                    try:
                        # Method 1: Direct value setting
                        driver.execute_script("""
                            var input = arguments[0];
                            var value = arguments[1];
                            input.value = value;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new Event('blur', { bubbles: true }));
                        """, input_elem, value)
                        time.sleep(0.2)
                        
                        # Method 2: Native value setter
                        driver.execute_script("""
                            var input = arguments[0];
                            var value = arguments[1];
                            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            nativeInputValueSetter.call(input, value);
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new Event('blur', { bubbles: true }));
                        """, input_elem, value)
                        time.sleep(0.2)
                        
                        # Method 3: Send keys as fallback
                        if not input_elem.get_attribute('value'):
                            input_elem.clear()
                            input_elem.send_keys(value)
                            time.sleep(0.2)
                    except Exception as e:
                        print(f"[WARNING] Error setting phone value: {str(e)}")
                    
                    # Verify the value was set
                    actual_value = input_elem.get_attribute('value')
                    if actual_value == value:
                        print(f"[SUCCESS] Filled: {label} = {value}")
                        return True
                    else:
                        print(f"[FAIL] Could not fill: {label} = {value} | Reason: Value mismatch after setting")
                        return False
                        
                except Exception as e:
                    print(f"[FAIL] Could not fill: {label} = {value} | Reason: {str(e)}")
                    return False

            # For all other fields, use the existing logic
            try:
                input_elem.clear()
            except Exception:
                pass
            input_id = input_elem.get_attribute('id')
            safe_value = value.replace("\\", "\\\\").replace("'", "\\'")
            js_script = f"""
                var input = document.getElementById('{input_id}');
                if (input) {{
                    input.removeAttribute('readonly');
                    input.removeAttribute('disabled');
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(input, '{safe_value}');
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                    setTimeout(function() {{
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                    }}, 100);
                    return input.value;
                }}
                return null;
            """
            driver.execute_script(js_script)
            time.sleep(0.5)
            actual_value = input_elem.get_attribute('value')
            if actual_value == value:
                print(f"[SUCCESS] Filled: {label} = {value}")
                return True
            else:
                try:
                    set_readonly_input(driver, input_elem, value)
                    time.sleep(0.5)
                    actual_value = input_elem.get_attribute('value')
                    if actual_value == value:
                        print(f"[SUCCESS] Filled: {label} = {value}")
                        return True
                    else:
                        print(f"[FAIL] Could not fill: {label} = {value} | Reason: set_readonly_input did not work")
                        return False
                except Exception as e:
                    print(f"[FAIL] Could not fill: {label} = {value} | Reason: set_readonly_input error: {str(e)}")
                    return False
    except Exception as e:
        print(f"[FAIL] Could not fill: {label} = {value} | Reason: {str(e)}")
        return False

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

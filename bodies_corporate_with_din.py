import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from function1 import scroll_into_view, send_text, click_element, click_button
from selenium.webdriver.common.action_chains import ActionChains
import json
from pynput.keyboard import Controller, Key

def validate_file_paths(file_paths):
    """Validate that all file paths exist."""
    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")


def handle_dynamic_identity_upload(driver, parent_div, file_path, i, timeout=5):
    """
    Handles file uploads dynamically for partner/nominee identity proofs using index-based dynamic parent div ID
    and static input XPath for fallback.
    """
    print(f"[DEBUG] Uploading file for index={i}")

    try:
        # If parent_div is given as XPath string, resolve it
        if isinstance(parent_div, str):
            parent_div_xpath = parent_div
            parent_div = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, parent_div_xpath))
            )

        print(f"[DEBUG] Found dynamic parent div: {parent_div.get_attribute('id')}")

        # Now find the attach button
        try:
            attach_button = parent_div.find_element(By.CSS_SELECTOR, "button.guide-fu-attach-button")
        except Exception as e:
            print(f"[WARNING] Attach button not found via CSS inside parent_div: {e}")
            fallback_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[18]/div/div/div/div[1]/div/div[5]/div/div/div[2]/div[1]/button"  # Keep your full fallback XPath here
            attach_button = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, fallback_xpath))
            )

        # Scroll and click
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", attach_button)
        time.sleep(2)
        try:
            attach_button.click()
        except:
            try:
                driver.execute_script("arguments[0].click();", attach_button)
            except:
                ActionChains(driver).move_to_element(attach_button).click().perform()

        time.sleep(2)

        # Type file path via keyboard
        normalized_path = os.path.normpath(file_path)
        keyboard = Controller()
        driver.switch_to.window(driver.current_window_handle)

        print(f"[DEBUG] Typing path: {normalized_path}")
        for char in normalized_path:
            keyboard.press(char)
            keyboard.release(char)
            time.sleep(0.1 if char in [":", "\\", "/"] else 0.05)

        time.sleep(1)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(1)

        # Success dialog handling
        try:
            ok_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ok-button, #okSuccessModalBtn"))
            )
            driver.execute_script("arguments[0].click();", ok_button)
            print("[AGILE PRO] Clicked OK on upload success dialog.")
        except TimeoutException:
            print("[INFO] No success dialog found.")
        except Exception as e:
            print(f"[WARNING] Error closing upload dialog: {e}")

        # Upload verification
        try:
            file_list = parent_div.find_element(By.CSS_SELECTOR, "ul.guide-fu-fileItemList")
            if file_list.find_elements(By.TAG_NAME, "li"):
                print("[AGILE PRO] File appears in upload list.")
                return True
            else:
                print("[WARNING] No file found in upload list.")
                return False
        except Exception as e:
            print(f"[INFO] Upload list not found: {e}")
            return True  # assume success if not verifiable

    except Exception as e:
        print(f"[ERROR] Upload failed for index={i}: {e}")
        return False



def handle_bodies_corporate_with_din(driver, config_data):
    """
    Handle the section for bodies corporate with DIN in the MCA LLP form.

    Args:
        driver: Selenium WebDriver instance
        config_data: Dictionary containing form data
    """
    try:
        # Get the number of bodies corporate from config with better error handling
        try:
            num_bodies = int(config_data['form_data']['fields'].get('Body corporates and their nominees Having valid DIN/DPIN', 0))
            print(f"[DEBUG] Number of bodies corporate found: {num_bodies}")
        except (ValueError, TypeError) as e:
            print(f"[ERROR] Invalid value for 'Bodies Corporate having valid DIN/DPIN': {e}")
            return

        if num_bodies == 0:
            print("[INFO] No bodies corporate with DIN/DPIN to process")
            return

        print(f"[INFO] Processing {num_bodies} Body corporates and their nominees Having valid DIN/DPIN")

        # Get bodies corporate data from config with better validation
        bodies_data = config_data.get('bodies_corporate_with_din', [])
        if not bodies_data:
            print("[WARNING] No bodies corporate data found in config")
            print("[DEBUG] Available keys in config_data:", list(config_data.keys()))
            return

        if not isinstance(bodies_data, list):
            print("[ERROR] bodies_corporate_with_din must be a list")
            return

        print(f"[DEBUG] Found {len(bodies_data)} bodies corporate entries in config")
        

        # Safely extract DIN/DPIN values as strings, falling back to empty string if None
        num_din_raw = config_data.get('form_data', {}).get('fields', {}).get('Individuals Having valid DIN/DPIN')
        num_no_din_raw = config_data.get('form_data', {}).get('fields', {}).get('Individuals Not having valid DIN/DPIN')

        num_din_str = str(num_din_raw).strip() if num_din_raw is not None else ''
        num_no_din_str = str(num_no_din_raw).strip() if num_no_din_raw is not None else ''

        # Convert to integers safely
        try:
            num_din = int(num_din_str) if num_din_str else 0
        except ValueError:
            print(f"[WARN] Invalid value for 'Individuals Having valid DIN/DPIN': '{num_din_str}', defaulting to 0")
            num_din = 0

        try:
            num_no_din = int(num_no_din_str) if num_no_din_str else 0
        except ValueError:
            print(f"[WARN] Invalid value for 'Individuals Not having valid DIN/DPIN': '{num_no_din_str}', defaulting to 0")
            num_no_din = 0
        
        if num_din > 0 and num_din == 0:
            dynamic_start_index = 2
            i = dynamic_start_index + num_din + 2
            print(f"[INFO] Using dynamic form index for body corporates with DIN/DPIN: i={i}")
        elif num_no_din > 0 and num_din == 0:
            dynamic_start_index = 4
            i = dynamic_start_index + num_no_din
            print(f"[INFO] Using dynamic form index for body corporates with DIN/DPIN: i={i}")
        # Calculate dynamic form index
        elif num_din > 0 or num_no_din > 0:
            dynamic_start_index = 2  # Where individual forms begin
            i = dynamic_start_index + num_din + num_no_din + 1
            print(f"[INFO] Using dynamic form index for body corporates with DIN/DPIN: i={i}")
        else:
            try:
                i = int(config_data.get('dynamic_form_index', {}).get('body_corporates_and_their_nominees_having_valid_din_dpin', 5))
            except (ValueError, TypeError):
                i = 5  # fallback default
                print("[WARN] Invalid fallback index, defaulting to 5")
            print(f"[INFO] No individual partners found. Using fallback index for body corporates with DIN/DPIN: i={i}")


            
        for idx, body in enumerate(bodies_data):
            position = idx + 1  # XPath is 1-based
            i += 1  # Increment 'i' for each partner

            # Ensure we don't try to access data beyond what's available
            if position > num_bodies:
                print(f"[INFO] Skipping body corporate {position} as it exceeds the specified number of bodies corporate ({num_bodies}).")
                continue

            print(f"\n[INFO] Filling details for body corporate {position}")
            fields_filled_count = 0
            fields_failed_count = 0

            # Validate body data structure
            if not isinstance(body, dict):
                print(f"[ERROR] Invalid data structure for body corporate {position}")
                continue
                

            # --- Type of body corporate ---
            time.sleep(2)
            try:
                body_corporate_type = body.get('Type of body corporate', '').strip()
                if body_corporate_type:
                    dropdown_xpath = f"(//select[@aria-label='Type of body corporate'])[{position}]"
                    try:
                        corporate_type_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, dropdown_xpath))
                        )
                        # Scroll to middle before interacting
                        scroll_into_view(driver, corporate_type_element)
                        select = Select(corporate_type_element)
                        select.select_by_visible_text(body_corporate_type)
                        print(f"[✓] Body Corporate {position}: Selected Type of body corporate - {body_corporate_type}")
                        fields_filled_count += 1
                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding Type of body corporate dropdown using aria-label.")
                        fields_failed_count += 1
                    except NoSuchElementException:
                        print(f"[✗] Body Corporate {position}: Could not find Type of body corporate dropdown using aria-label.")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: Type of body corporate not provided.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Error selecting Type of body corporate: {e}")
                fields_failed_count += 1

            # --- Corporate Identity Number(CIN) ---
            time.sleep(0.5)
            try:
                cin_fcrn_value = body.get('CIN/FCRN', '').strip()
                if cin_fcrn_value:
                    # Use aria-label to locate the CIN/FCRN input
                    cin_fcrn_xpath = f"(//input[@aria-label='Corporate Identity Number(CIN) or Foreign Company Registration Number(FCRN) or Limited Liability Partnership Identification Number(LLPIN) or Foreign Limited Liability Partnership Identification number(FLLPIN) or any other registration number'])[{position}]"
                    try:
                        cin_fcrn_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, cin_fcrn_xpath)))
                        cin_fcrn_input.clear()
                        cin_fcrn_input.send_keys(cin_fcrn_value)
                        print(f"[✓] Body Corporate {position}: Entered CIN/FCRN: {cin_fcrn_value}")
                        fields_filled_count += 1
                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding CIN/FCRN input using aria-label.")
                        fields_failed_count += 1
                    except NoSuchElementException:
                        print(f"[✗] Body Corporate {position}: Could not find CIN/FCRN input using aria-label.")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No CIN/FCRN provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process CIN/FCRN: {e}")
                fields_failed_count += 1

            # --- PAN ---
            time.sleep(0.5)
            try:
                pan_value = body.get('PAN', '').strip()
                if pan_value:
                    # More specific XPath to target only input fields with PAN aria-label
                    pan_xpath = f"(//input[@type='text' and @aria-label='PAN'])[{position}]"
                    
                    try:
                        pan_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, pan_xpath))
                        )
                        
                        # Ensure element is visible and enabled
                        if not pan_input.is_enabled():
                            print(f"[INFO] Body Corporate {position}: PAN field is disabled, attempting to enable...")
                            driver.execute_script("arguments[0].disabled = false;", pan_input)
                        
                        # Scroll into view and wait
                        driver.execute_script("arguments[0].scrollIntoView(true);", pan_input)
                        time.sleep(0.2)
                        
                        # Clear and set value
                        pan_input.clear()
                        pan_input.send_keys(pan_value)
                        
                        # Verify the value was set
                        time.sleep(0.2)
                        actual_value = pan_input.get_attribute('value')
                        if actual_value:
                            print(f"[✓] Body Corporate {position}: Entered PAN: {pan_value}")
                            print(f"[VERIFY] PAN value set to: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[WARNING] Body Corporate {position}: PAN value appears to be empty after filling")
                            fields_failed_count += 1
                            
                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding PAN input field")
                        fields_failed_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting PAN value: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No PAN provided in data")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process PAN: {str(e)}")
                fields_failed_count += 1


            # --- Name of the body corporate ---
            time.sleep(0.5)
            try:
                name_value = body.get('Name of the body corporate', '').strip()
                if name_value:
                    name_xpath = f"(//input[@aria-label='Name of body corporate'])[{position}]"
                    try:
                        name_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, name_xpath))
                        )
                        
                        # Scroll into view and wait
                        driver.execute_script("arguments[0].scrollIntoView(true);", name_input)
                        time.sleep(0.2)
                        
                        # Clear and set value with proper event handling
                        driver.execute_script("""
                            var element = arguments[0];
                            var value = arguments[1];
                            element.value = value;
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                            element.dispatchEvent(new Event('input', { bubbles: true }));
                            element.dispatchEvent(new Event('blur', { bubbles: true }));
                            // Simulate form submission
                            var form = element.closest('form');
                            if (form) {
                                form.dispatchEvent(new Event('submit', { bubbles: true }));
                            }
                        """, name_input, name_value)
                        
                        # Verify the value was set
                        time.sleep(0.2)
                        actual_value = driver.execute_script("return arguments[0].value;", name_input)
                        if actual_value:
                            print(f"[✓] Body Corporate {position}: Entered Name of body corporate: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[WARNING] Body Corporate {position}: Name value not visible after setting")
                            fields_failed_count += 1
                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding 'Name of body corporate' input")
                        fields_failed_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting name: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: 'Name of body corporate' not provided in data")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process 'Name of body corporate': {str(e)}")
                fields_failed_count += 1
                
            
            # --- Address Line I ---
            try:
                address1_value = body.get('Address Line I', '').strip()
                
                if address1_value:
                    # Dynamically build XPath for "Address Line I" using index i
                    address1_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"


                    # Wait for the field to appear
                    address1_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, address1_xpath))
                    )

                    # Scroll to the element using a helper function if available
                    if callable(globals().get('scroll_into_view')):
                        scroll_into_view(driver, address1_input)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", address1_input)

                    # Clear existing value and set new one using JavaScript (bypass read-only)
                    driver.execute_script("arguments[0].value = '';", address1_input)
                    driver.execute_script("arguments[0].value = arguments[1];", address1_input, address1_value)

                    # Dispatch 'input' and 'change' events to trigger any dynamic behavior
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", address1_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", address1_input)

                    # Use function1's send_text with the element directly
                    send_text(driver, xpath=address1_xpath, keys=address1_value)

                    fields_filled_count += 1
                    print(f"[✓] Body Corporate {position}: Entered Address Line I: {address1_value}")
                
                else:
                    print(f"[!] Body Corporate {position}: 'Address Line I' is empty or missing in input data. Skipping.")
                    # Optionally count as failure:
                    # fields_failed_count += 1

            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to fill 'Address Line I' due to error: {str(e)}")
                fields_failed_count += 1


            # --- Address Line II ---
            try:
                address2_value = body.get('Address Line II', '').strip()
                
                if address2_value:
                    # Updated static XPath with dynamic 'i'
                    address2_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"
                    

                    address2_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, address2_xpath))
                    )

                    # Scroll to the element
                    if callable(globals().get('scroll_into_view')):
                        scroll_into_view(driver, address2_input)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", address2_input)

                    # Clear existing value and set new one using JavaScript (bypass read-only)
                    driver.execute_script("arguments[0].value = '';", address2_input)
                    driver.execute_script("arguments[0].value = arguments[1];", address2_input, address2_value)

                    # Dispatch 'input' and 'change' events to trigger any dynamic behavior
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", address2_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", address2_input)

                    # Use function1's send_text with the element directly
                    send_text(driver, xpath=address2_xpath, keys=address2_value)


                    fields_filled_count += 1
                    print(f"[✓] Body Corporate {position}: Entered Address Line II: {address2_value}")

                else:
                    print(f"[!] Body Corporate {position}: 'Address Line II' is empty or missing in input data. Skipping.")
                    # Optionally count as failure
                    # fields_failed_count += 1

            except Exception as e:
                xpath_info = address2_xpath if 'address2_xpath' in locals() and address2_xpath else 'XPath not yet defined or N/A'
                print(f"[✗] Body Corporate {position}: Error processing Address Line II (XPath: {xpath_info}): {e}")
                fields_failed_count += 1


            # --- Country (dropdown) ---
            try:
                country_value = body.get('Country', '').strip()
                
                if country_value:
                    try:
                        # Static XPath for the Country dropdown, with dynamic index i
                        country_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[3]/div/div/div[2]/select"

                        country_select_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, country_xpath))
                        )

                        # Scroll to the dropdown element
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, country_select_element)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", country_select_element)

                        # Use JavaScript to set the dropdown value
                        driver.execute_script("""
                            let select = arguments[0];
                            let value = arguments[1];
                            for (let i = 0; i < select.options.length; i++) {
                                if (select.options[i].text.trim().toLowerCase() === value.toLowerCase()) {
                                    select.selectedIndex = i;
                                    select.dispatchEvent(new Event('change', { bubbles: true }));
                                    break;
                                }
                            }
                        """, country_select_element, country_value)

                        # Verify the selected option (optional)
                        selected_value = driver.execute_script("return arguments[0].options[arguments[0].selectedIndex].text;", country_select_element)

                        if selected_value.strip().lower() == country_value.lower():
                            print(f"[✓] Body Corporate {position}: Selected Country: {selected_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[✗] Body Corporate {position}: Could not select Country value: {country_value}")
                            fields_failed_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error selecting Country (XPath: {country_xpath}): {str(e)}")
                        fields_failed_count += 1

                else:
                    print(f"[!] Body Corporate {position}: 'Country' is empty or missing in input data. Skipping.")
                    # Optionally count as failure
                    # fields_failed_count += 1

            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Country block: {str(e_outer)}")
                fields_failed_count += 1
                

            # --- Pin code / Zip Code ---
            try:
                pincode_value = body.get('Pin code', '').strip()

                if pincode_value:
                    # Static XPath for Pin code input with dynamic index 'i'
                    pincode_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[4]/div/div/div[2]/input"
                

                    try:
                        pincode_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, pincode_xpath))
                        )

                        # Scroll to the input field
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, pincode_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pincode_input)

                        # Clear and input the pin code
                        driver.execute_script("arguments[0].value = '';", pincode_input)
                        driver.execute_script("arguments[0].value = arguments[1];", pincode_input, pincode_value)

                        # Dispatch 'input' and 'change' events
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", pincode_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", pincode_input)

                        send_text(driver, xpath=pincode_xpath, keys=pincode_value)

                        print(f"[✓] Body Corporate {position}: Entered Pin code: {pincode_value}")
                        fields_filled_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Pin code (XPath: {pincode_xpath}): {e}")
                        fields_failed_count += 1

                else:
                    print(f"[!] Body Corporate {position}: 'Pin code / Zip Code' is empty or missing in input data. Skipping.")
                    # Optionally count as failure
                    # fields_failed_count += 1

            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Pin code block: {str(e_outer)}")
                fields_failed_count += 1


            # --- Area/ Locality (dropdown) ---
            try:
                area_value = body.get('Area/ Locality', '').strip()

                if area_value:
                    # Static XPath for Area/Locality dropdown with dynamic index i
                    area_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[5]/div/div/div[2]/select"

                    try:
                        area_select_element = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, area_xpath))
                        )

                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, area_select_element)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", area_select_element)

                        # Use send_text helper to select by typing visible text
                        click_element(driver, xpath=area_xpath)
                        send_text(driver, xpath=area_xpath, keys=area_value)

                        # Verify selected value
                        selected_area = driver.execute_script("return arguments[0].options[arguments[0].selectedIndex].text;", area_select_element)

                        if selected_area.strip().lower() == area_value.lower():
                            print(f"[✓] Body Corporate {position}: Selected Area/ Locality: {selected_area}")
                            fields_filled_count += 1
                        else:
                            print(f"[✗] Body Corporate {position}: Area/ Locality mismatch (Expected: {area_value}, Found: {selected_area})")
                            fields_failed_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error selecting Area/ Locality (XPath: {area_xpath}): {e}")
                        fields_failed_count += 1

                else:
                    print(f"[!] Body Corporate {position}: 'Area/ Locality' is empty or missing in input data. Skipping.")
                    # Optionally count as failure
                    # fields_failed_count += 1

            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Area/ Locality block: {str(e_outer)}")
                fields_failed_count += 1


            # --- Jurisdiction of Police Station (readonly text) ---
            try:
                police_value = body.get('Jurisdiction of Police Station', '').strip()

                if police_value:
                    # Static XPath for Police Station input with dynamic index i
                    police_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[10]/div/div/div[2]/input"
                    
                    try:
                        police_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, police_xpath))
                        )

                        # Scroll to the input field
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, police_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", police_input)

                        # Remove readonly and fill value
                        driver.execute_script("arguments[0].removeAttribute('readonly');", police_input)
                        driver.execute_script("arguments[0].value = '';", police_input)
                        driver.execute_script("arguments[0].value = arguments[1];", police_input, police_value)

                        # Dispatch events
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", police_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", police_input)

                        send_text(driver, xpath=police_xpath, keys=police_value)

                        print(f"[✓] Body Corporate {position}: Entered Jurisdiction of Police Station: {police_value}")
                        fields_filled_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Jurisdiction of Police Station (XPath: {police_xpath}): {e}")
                        fields_failed_count += 1

                else:
                    print(f"[!] Body Corporate {position}: 'Jurisdiction of Police Station' is empty or missing in input data. Skipping.")
                    # Optionally count as failure:
                    # fields_failed_count += 1

            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Police Station field block: {str(e_outer)}")
                fields_failed_count += 1


            # --- Phone (with STD/ISD code) ---
            try:
                phone_value = body.get('Phone (with STD/ISD code)', '').strip()

                if phone_value:
                    # Static XPath for Phone input with dynamic index i
                    phone_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[10]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"

                    try:
                        phone_input = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, phone_xpath))
                        )

                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, phone_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_input)

                        # Remove readonly and set value
                        driver.execute_script("arguments[0].removeAttribute('readonly');", phone_input)
                        driver.execute_script("arguments[0].value = '';", phone_input)
                        driver.execute_script("arguments[0].value = arguments[1];", phone_input, phone_value)

                        # Dispatch input/change events
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", phone_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", phone_input)

                        send_text(driver, xpath=phone_xpath, keys=phone_value)

                        print(f"[✓] Body Corporate {position}: Entered Phone (with STD/ISD code): {phone_value}")
                        fields_filled_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Phone (with STD/ISD code) (XPath: {phone_xpath}): {e}")
                        fields_failed_count += 1

                else:
                    print(f"[!] Body Corporate {position}: 'Phone (with STD/ISD code)' is empty or missing in input data. Skipping.")

            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Phone input block: {str(e_outer)}")
                fields_failed_count += 1


            # --- Mobile No. ---
            time.sleep(1)
            try:
                mobile_value = body.get('Mobile No', '')

                if mobile_value:
                    # Static XPath for Mobile No input with dynamic index i
                    mobile_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[10]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"
                    
                    try:
                        mobile_input = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, mobile_xpath))
                        )

                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, mobile_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", mobile_input)

                        # Remove readonly attribute and clear value
                        driver.execute_script("arguments[0].removeAttribute('readonly');", mobile_input)
                        driver.execute_script("arguments[0].value = '';", mobile_input)
                        driver.execute_script("arguments[0].value = arguments[1];", mobile_input, mobile_value)

                        # Dispatch events
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", mobile_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", mobile_input)

                        # Optionally simulate typing via send_text if you want extra safety
                        send_text(driver, xpath=mobile_xpath, keys=mobile_value)

                        print(f"[✓] Body Corporate {position}: Entered Mobile No.: {mobile_value}")
                        fields_filled_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Mobile No. (XPath: {mobile_xpath}): {e}")
                        fields_failed_count += 1
                else:
                    print(f"[!] Body Corporate {position}: 'Mobile No.' is empty or missing in input data. Skipping.")

            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Mobile No. input block: {str(e_outer)}")
                fields_failed_count += 1


            # --- Fax ---
            time.sleep(0.5)
            try:
                fax_value = body.get('Fax', '').strip()

                if fax_value:
                    # Static XPath for Fax input with dynamic index i
                    fax_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[10]/div/div/div/div[1]/div/div[3]/div/div/div[2]/input"

                    try:
                        fax_input = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, fax_xpath))
                        )

                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, fax_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fax_input)

                        # Remove readonly attribute and clear value
                        driver.execute_script("arguments[0].removeAttribute('readonly');", fax_input)
                        driver.execute_script("arguments[0].value = '';", fax_input)
                        driver.execute_script("arguments[0].value = arguments[1];", fax_input, fax_value)

                        # Dispatch input/change events
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", fax_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", fax_input)

                        # Optionally simulate typing via sexecend_text
                        send_text(driver, xpath=fax_xpath, keys=fax_value)

                        print(f"[✓] Body Corporate {position}: Entered Fax: {fax_value}")
                        fields_filled_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Fax (XPath: {fax_xpath}): {e}")
                        fields_failed_count += 1

                else:
                    print(f"[INFO] Body Corporate {position}: 'Fax' not provided in data")

            except TimeoutException:
                print(f"[✗] Body Corporate {position}: Timeout finding 'Fax' input")
                fields_failed_count += 1

            except Exception as e:
                print(f"[✗] Body Corporate {position}: Error setting Fax: {str(e)}")
                fields_failed_count += 1


            # --- Email ID ---
            time.sleep(0.5)
            try:
                email_value = body.get('Email ID', '').strip()
                if email_value:
                    # Static XPath for Email input with dynamic index i
                    email_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[10]/div/div/div/div[1]/div/div[4]/div/div/div[2]/input"
                    

                    try:
                        email_input = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, email_xpath))
                        )

                        # Scroll into view (use your scroll_into_view if available)
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, email_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_input)

                        # Remove readonly attribute, clear and set value via JS
                        driver.execute_script("arguments[0].removeAttribute('readonly');", email_input)
                        driver.execute_script("arguments[0].value = '';", email_input)
                        driver.execute_script("arguments[0].value = arguments[1];", email_input, email_value)

                        # Dispatch input/change events
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", email_input)

                        # Optional: simulate typing via send_text helper
                        send_text(driver, xpath=email_xpath, keys=email_value)

                        print(f"[✓] Body Corporate {position}: Entered Email ID: {email_value}")
                        fields_filled_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Email ID (XPath: {email_xpath}): {e}")
                        fields_failed_count += 1

                else:
                    print(f"[INFO] Body Corporate {position}: 'Email ID' not provided in data")

            except TimeoutException:
                print(f"[✗] Body Corporate {position}: Timeout finding 'Email ID' input")
                fields_failed_count += 1

            except Exception as e:
                print(f"[✗] Body Corporate {position}: Error setting Email ID: {str(e)}")
                fields_failed_count += 1
            

            # --- Form of contribution ---
            time.sleep(0.5)
            try:
                form_of_contribution_value = body.get('Form of contribution', '').strip()
                if form_of_contribution_value:
                    # XPath for Form of contribution dropdown with dynamic index i
                    form_of_contribution_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[1]/div/div/div[2]/select"

                    try:
                        form_of_contribution_dropdown = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, form_of_contribution_xpath))
                        )

                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", form_of_contribution_dropdown)
                        time.sleep(0.2)

                        select = Select(form_of_contribution_dropdown)

                        available_options = [option.text.strip() for option in select.options]
                        print(f"[DEBUG] Available Form of contribution options: {available_options}")

                        try:
                            select.select_by_visible_text(form_of_contribution_value)
                            time.sleep(0.2)

                            selected_value = select.first_selected_option.text
                            if selected_value == form_of_contribution_value:
                                print(f"[✓] Body Corporate {position}: Selected Form of contribution: {selected_value}")
                                fields_filled_count += 1

                                # If "Other than cash" selected, fill the specification field
                                if form_of_contribution_value == "Other than cash":
                                    other_contribution_value = body.get("If 'Other than cash' selected, please specify", '').strip()
                                    if other_contribution_value:
                                        other_contribution_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"
                                        

                                        try:
                                            other_contribution_input = WebDriverWait(driver, 10).until(
                                                EC.presence_of_element_located((By.XPATH, other_contribution_xpath))
                                            )

                                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", other_contribution_input)
                                            time.sleep(0.2)

                                            other_contribution_input.clear()
                                            other_contribution_input.send_keys(other_contribution_value)

                                            print(f"[✓] Body Corporate {position}: Entered 'Other than cash' specification: {other_contribution_value}")
                                            fields_filled_count += 1
                                        except Exception as e:
                                            print(f"[✗] Body Corporate {position}: Error setting 'Other than cash' specification: {str(e)}")
                                            fields_failed_count += 1
                                    else:
                                        print(f"[INFO] Body Corporate {position}: 'Other than cash' specification not provided")
                            else:
                                print(f"[WARNING] Body Corporate {position}: Form of contribution value not set correctly")
                                fields_failed_count += 1

                        except Exception as e:
                            print(f"[✗] Body Corporate {position}: Error selecting Form of contribution: {str(e)}")
                            fields_failed_count += 1

                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding Form of contribution dropdown")
                        fields_failed_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error processing Form of contribution: {str(e)}")
                        fields_failed_count += 1

                else:
                    print(f"[INFO] Body Corporate {position}: 'Form of contribution' not provided in data")

            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process 'Form of contribution': {str(e)}")
                fields_failed_count += 1


            # --- Monetary value of contribution (in INR) (in figures) ---
            time.sleep(0.5)
            try:
                monetary_value = body.get('Monetary value of contribution (in INR) (in figures)', '').strip()
                
                if monetary_value:
                    # Exact XPath with index i for the input field
                    monetary_value_xpath = (
                        f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]"
                        f"/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]"
                        f"/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/"
                        f"div[1]/div/div[3]/div/div/div[2]/input"
                    )

                    try:
                        monetary_value_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, monetary_value_xpath))
                        )

                        # Scroll to element
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, monetary_value_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", monetary_value_input)
                        time.sleep(0.2)

                        # Set the value via JavaScript
                        driver.execute_script("arguments[0].value = '';", monetary_value_input)
                        driver.execute_script("arguments[0].value = arguments[1];", monetary_value_input, monetary_value)

                        # Dispatch input and change events
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", monetary_value_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", monetary_value_input)

                        # Use your helper as fallback for maximum reliability
                        send_text(driver, xpath=monetary_value_xpath, keys=monetary_value)

                        # Verification
                        actual_value = monetary_value_input.get_attribute('value').strip()
                        if actual_value == monetary_value:
                            print(f"[✓] Body Corporate {position}: Entered Monetary value: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[WARNING] Body Corporate {position}: Monetary value not set correctly (Expected: {monetary_value}, Found: {actual_value})")
                            fields_failed_count += 1

                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding Monetary value input")
                        fields_failed_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Monetary value: {str(e)}")
                        fields_failed_count += 1

                else:
                    print(f"[INFO] Body Corporate {position}: 'Monetary value' not provided in data")

            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process 'Monetary value': {str(e)}")
                fields_failed_count += 1


            # --- Number of LLP(s) in which entity is a partner ---
            time.sleep(0.5)
            try:
                num_llps = body.get('Number of LLP(s) in which entity is a partner', '0').strip()
                if not num_llps:  # default to '0' if blank
                    num_llps = '0'

                # Absolute XPath with index i
                num_llps_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[5]/div/div/div[2]/input"
                

                try:
                    num_llps_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, num_llps_xpath))
                    )

                    # Scroll into view
                    if callable(globals().get('scroll_into_view')):
                        scroll_into_view(driver, num_llps_input)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", num_llps_input)
                    time.sleep(0.2)

                    # Set value using JS for reliability
                    driver.execute_script("arguments[0].value = '';", num_llps_input)
                    driver.execute_script("arguments[0].value = arguments[1];", num_llps_input, num_llps)

                    # Trigger input and change events
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", num_llps_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", num_llps_input)

                    # Fallback send_keys
                    send_text(driver, xpath=num_llps_xpath, keys=num_llps)

                    # Verify final value
                    actual_value = num_llps_input.get_attribute('value').strip()
                    if actual_value == num_llps:
                        print(f"[✓] Body Corporate {position}: Entered Number of LLPs: {actual_value}")
                        fields_filled_count += 1
                    else:
                        print(f"[WARNING] Body Corporate {position}: Number of LLPs not set correctly (Expected: {num_llps}, Found: {actual_value})")
                        fields_failed_count += 1

                except Exception as e:
                    print(f"[✗] Body Corporate {position}: Error setting Number of LLPs: {str(e)}")
                    fields_failed_count += 1

            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process 'Number of LLPs': {str(e)}")
                fields_failed_count += 1


            # --- Number of company(s) in which entity is a director ---
            time.sleep(0.5)
            try:
                num_companies = body.get('Number of company(s) in which entity is a director', '0').strip()

                # Use provided absolute XPath with dynamic index {i}
                num_companies_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[6]/div/div/div[2]/input"
                
                try:
                    num_companies_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, num_companies_xpath))
                    )

                    # Scroll to view
                    if callable(globals().get('scroll_into_view')):
                        scroll_into_view(driver, num_companies_input)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", num_companies_input)

                    time.sleep(0.2)

                    # Set value via JS
                    driver.execute_script("arguments[0].value = '';", num_companies_input)
                    driver.execute_script("arguments[0].value = arguments[1];", num_companies_input, num_companies)

                    # Dispatch input/change events
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", num_companies_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", num_companies_input)

                    # Fallback input
                    send_text(driver, xpath=num_companies_xpath, keys=num_companies)

                    # Confirm
                    actual_value = num_companies_input.get_attribute('value')
                    if actual_value == num_companies:
                        print(f"[✓] Body Corporate {position}: Entered Number of companies: {actual_value}")
                        fields_filled_count += 1
                    else:
                        print(f"[WARNING] Body Corporate {position}: Number of companies not set correctly (Expected: {num_companies}, Found: {actual_value})")
                        fields_failed_count += 1

                except Exception as e:
                    print(f"[✗] Body Corporate {position}: Error setting Number of companies: {str(e)}")
                    fields_failed_count += 1

            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process 'Number of companies': {str(e)}")
                fields_failed_count += 1
            


            # --- Designated partner Identification number (DIN/DPIN) ---
            time.sleep(0.5)
            try:
                din_dpin_value = body.get('DIN/DPIN', '')
                if din_dpin_value:

                    # Absolute XPath with dynamic index {i}
                    din_dpin_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[18]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"
                    

                    try:
                        din_dpin_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, din_dpin_xpath))
                        )

                        # Scroll to view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, din_dpin_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", din_dpin_input)

                        time.sleep(0.2)

                        # Set value via JavaScript
                        driver.execute_script("arguments[0].value = '';", din_dpin_input)
                        driver.execute_script("arguments[0].value = arguments[1];", din_dpin_input, din_dpin_value)

                        # Trigger input/change events
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", din_dpin_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", din_dpin_input)

                        # Fallback input (in case the JS set didn't take effect)
                        send_text(driver, xpath=din_dpin_xpath, keys=din_dpin_value)

                        # Confirm
                        actual_value = din_dpin_input.get_attribute('value').strip()
                        if actual_value == din_dpin_value:
                            print(f"[✓] Body Corporate {position}: Entered DIN/DPIN: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[WARNING] Body Corporate {position}: DIN/DPIN not set correctly (Expected: {din_dpin_value}, Found: {actual_value})")
                            fields_failed_count += 1

                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding DIN/DPIN input")
                        fields_failed_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting DIN/DPIN: {str(e)}")
                        fields_failed_count += 1

                else:
                    print(f"[INFO] Body Corporate {position}: 'DIN/DPIN' not provided in data")

            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process 'DIN/DPIN': {str(e)}")
                fields_failed_count += 1



            # --- Name of Designated Partner ---
            time.sleep(0.5)
            try:
                din_dpin_value = body.get('Name', '')
                if din_dpin_value:

                    # Absolute XPath with dynamic index {i}
                    din_dpin_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[18]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"
                    
                    try:
                        din_dpin_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, din_dpin_xpath))
                        )

                        # Scroll to view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, din_dpin_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", din_dpin_input)

                        time.sleep(0.2)

                        # Set value via JavaScript
                        driver.execute_script("arguments[0].value = '';", din_dpin_input)
                        driver.execute_script("arguments[0].value = arguments[1];", din_dpin_input, din_dpin_value)

                        # Trigger input/change events
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", din_dpin_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", din_dpin_input)

                        # Fallback input using helper
                        send_text(driver, xpath=din_dpin_xpath, keys=din_dpin_value)

                        # Confirm final value
                        actual_value = din_dpin_input.get_attribute('value').strip()
                        if actual_value == din_dpin_value:
                            print(f"[✓] Body Corporate {position}: Entered DIN/DPIN: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[WARNING] Body Corporate {position}: DIN/DPIN not set correctly (Expected: {din_dpin_value}, Found: {actual_value})")
                            fields_failed_count += 1

                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding DIN/DPIN input")
                        fields_failed_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting DIN/DPIN: {str(e)}")
                        fields_failed_count += 1

                else:
                    print(f"[INFO] Body Corporate {position}: 'DIN/DPIN' not provided in data")

            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process 'DIN/DPIN': {str(e)}")
                fields_failed_count += 1


            # --- Whether resident of India --- 
            time.sleep(0.5)
            try:
                # Get the resident status, defaulting to False if not provided
                is_resident = False
                resident_data = body.get('Whether resident of India', {})
                if isinstance(resident_data, dict):
                    is_resident = resident_data.get('Yes', False)
                elif isinstance(resident_data, str):
                    is_resident = resident_data.lower() in ['true', 'yes']
                elif isinstance(resident_data, bool):
                    is_resident = resident_data

                # Absolute XPath with dynamic index {i}
                radio_container_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[18]/div/div/div/div[1]/div/div[3]/div/div/div[2]"
                
                try:
                    radio_container = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, radio_container_xpath))
                    )

                    radio_buttons = radio_container.find_elements(By.XPATH, ".//input[@type='radio']")

                    if len(radio_buttons) >= 2:
                        try:
                            if is_resident:
                                driver.execute_script("arguments[0].click();", radio_buttons[0])  # 'Yes'
                                print(f"[✓] Body Corporate {position}: Selected 'Yes' for Whether resident of India.")
                            else:
                                driver.execute_script("arguments[0].click();", radio_buttons[1])  # 'No'
                                print(f"[✓] Body Corporate {position}: Selected 'No' for Whether resident of India.")
                            fields_filled_count += 1
                        except Exception as e:
                            print(f"[WARNING] Body Corporate {position}: Error clicking radio button: {str(e)}")
                            fields_failed_count += 1
                    else:
                        print(f"[WARNING] Body Corporate {position}: Less than 2 radio buttons found for 'Whether resident of India'.")
                        fields_failed_count += 1

                except TimeoutException:
                    print(f"[✗] Body Corporate {position}: Timeout finding 'Whether resident of India' radio button container.")
                    fields_failed_count += 1
                except Exception as e:
                    print(f"[✗] Body Corporate {position}: Error handling 'Whether resident of India' radio buttons: {str(e)}")
                    fields_failed_count += 1

            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process 'Whether resident of India': {str(e)}")
                fields_failed_count += 1



            # --- Designation and Authority in body corporate ---   
            time.sleep(0.5)
            try:
                designation_authority_value = body.get('Designation and Authority in body corporate', '')
                if designation_authority_value:
                    # Absolute XPath with dynamic index {i}
                    designation_authority_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[18]/div/div/div/div[1]/div/div[4]/div/div/div[2]/input"
                    try:
                        designation_authority_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, designation_authority_xpath))
                        )

                        # Scroll into view
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", designation_authority_input)
                        time.sleep(0.2)

                        # Clear and fill the input using JS
                        driver.execute_script("arguments[0].value = '';", designation_authority_input)
                        driver.execute_script("arguments[0].value = arguments[1];", designation_authority_input, designation_authority_value)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", designation_authority_input)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", designation_authority_input)

                        # Fallback: Use standard Selenium send_keys
                        designation_authority_input.clear()
                        designation_authority_input.send_keys(designation_authority_value)

                        # Verify input
                        actual_value = designation_authority_input.get_attribute('value').strip()
                        if actual_value == designation_authority_value:
                            print(f"[✓] Body Corporate {position}: Entered Designation and Authority: {designation_authority_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[WARNING] Body Corporate {position}: Designation and Authority value mismatch (Expected: {designation_authority_value}, Found: {actual_value})")
                            fields_failed_count += 1

                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding 'Designation and Authority in body corporate' input.")
                        fields_failed_count += 1
                    except NoSuchElementException:
                        print(f"[✗] Body Corporate {position}: Could not find 'Designation and Authority in body corporate' input.")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: 'Designation and Authority in body corporate' not provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to process 'Designation and Authority in body corporate': {e}")
                fields_failed_count += 1

            print(f"\n[INFO] Finished filling details for body corporate {position}. Fields Filled: {fields_filled_count}, Fields Failed: {fields_failed_count}")


            # Copy of resolution
            try:
                # SRN
                parent_div_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[18]/div/div/div/div[1]/div/div[5]/div/div/div[2]/div[1]"

                if body.get('Copy of resolution'):
                    file_path = body.get('Copy of resolution')
                    success = handle_dynamic_identity_upload(driver, parent_div_xpath, file_path, i)
                    if success:
                        print(f" {i} document uploaded successfully.")
                    else:
                        print(f" {i} document upload failed.")
                
                click_element(
                driver,
                css_selector="#guideContainer-rootPanel-modal_container_131700874-guidebutton___widget"
                )
            except Exception as e:
                            print(f"[ERROR] Failed to handle file uploads: {e}")
                            fields_failed_count += 2

        print("[SUCCESS] Completed processing all bodies corporate with DIN/DPIN")

    except Exception as e:
        print(f"[ERROR] Failed to process bodies corporate with DIN/DPIN: {str(e)}")
        raise
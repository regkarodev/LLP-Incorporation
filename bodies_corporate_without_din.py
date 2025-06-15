import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from function1 import scroll_into_view, send_text, click_element, set_date_field
from selenium.webdriver.common.action_chains import ActionChains
import json
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from pynput.keyboard import Controller, Key



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
            fallback_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[29]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[1]/button"  # Keep your full fallback XPath here
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


def handle_dynamic_residency_upload(driver, parent_div, file_path, i, timeout=5):
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
            fallback_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[29]/div/div/div/div[1]/div/div[3]/div/div/div[2]/div[1]/button"  # Keep your full fallback XPath here
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


def handle_dynamic_resolution_upload(driver, parent_div, file_path, i, timeout=5):
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
            fallback_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[29]/div/div/div/div[1]/div/div[4]/div/div/div[2]/div[1]/button"  # Keep your full fallback XPath here
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


def handle_bodies_corporate_without_din(driver, config_data):
    """
    Handle the section for bodies corporate with DIN in the MCA LLP form.

    Args:
        driver: Selenium WebDriver instance
        config_data: Dictionary containing form data
    """
    try:
        # Get the number of bodies corporate from config with better error handling
        try:
            num_bodies = int(config_data['form_data']['fields'].get('Body corporates and their nominee not having valid DIN/DPIN', 0))
            print(f"[DEBUG] Number of bodies corporate found: {num_bodies}")
        except (ValueError, TypeError) as e:
            print(f"[ERROR] Invalid value for Particulars of bodies corporate and their nominees as designated partners not having  DIN/DPIN': {e}")
            return

        if num_bodies == 0:
            print("[INFO] No bodies corporate with having DIN/DPIN to process")
            return

        print(f"[INFO] Processing {num_bodies} Body corporates and their nominees not Having valid DIN/DPIN")

        # Get bodies corporate data from config with better validation
        bodies_data = config_data.get('bodies_corporate_nominee_no_din', [])
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
        bodies_cor_with_din_raw = config_data.get('form_data', {}).get('fields', {}).get('Body corporates and their nominees Having valid DIN/DPIN')

        num_din_str = str(num_din_raw).strip() if num_din_raw is not None else ''
        num_no_din_str = str(num_no_din_raw).strip() if num_no_din_raw is not None else ''
        bodies_cor_with_din_str = str(bodies_cor_with_din_raw).strip() if bodies_cor_with_din_raw is not None else ''

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

        try:
            bodies_cor_with_din = int(bodies_cor_with_din_str) if bodies_cor_with_din_str else 0
        except ValueError:
            print(f"[WARN] Invalid value for 'Body corporates and their nominees Having valid DIN/DPIN': '{bodies_cor_with_din_str}', defaulting to 0")
            bodies_cor_with_din = 0


        
        if num_din > 0 and num_no_din == 0 and bodies_cor_with_din == 0:
            dynamic_start_index = 2
            i = dynamic_start_index + num_din + 4
            print(f"[INFO] Using dynamic form index for body corporates without DIN/DPIN: i={i}")
        elif num_no_din > 0 and num_din == 0 and bodies_cor_with_din == 0:
            dynamic_start_index = 4
            i = dynamic_start_index + num_no_din + 2
            print(f"[INFO] Using dynamic form index for body corporates without DIN/DPIN: i={i}")
        elif bodies_cor_with_din > 0 and num_din == 0 and num_no_din == 0:
            dynamic_start_index = 6
            i = dynamic_start_index + bodies_cor_with_din 
            print(f"[INFO] Using dynamic form index for body corporates without DIN/DPIN: i={i}")
        # Calculate dynamic form index
        elif num_din > 0 or num_no_din > 0 or bodies_cor_with_din > 0:
            # dynamic_start_index = 2   Where individual forms begin
            i =  num_din + num_no_din + bodies_cor_with_din + 4
            print(f"[INFO] Using dynamic form index for body corporates without DIN/DPIN: i={i}")
        else:
            try:
                i = int(config_data.get('dynamic_form_index', {}).get('body_corporates_and_their_nominee_not_having_valid_din_dpin', 7))
            except (ValueError, TypeError):
                i = 7  # fallback default
                print("[WARN] Invalid fallback index, defaulting to 7")
            print(f"[INFO] No individual partners found. Using fallback index for body corporates without DIN/DPIN: i={i}")


            
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
            
            # Get corporate details
            corporate_details = body.get('corporate_details', {})
            contribution = body.get('contribution', {})
            
            # --- Type of body corporate ---
            time.sleep(2)
            try:
                body_corporate_type = corporate_details.get('type', '').strip()
                if body_corporate_type:
                    # Absolute XPath using index i (1-based)
                    dropdown_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[1]/div/div/div[2]/select"

                    try:
                        # Wait for dropdown to appear
                        corporate_type_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, dropdown_xpath))
                        )

                        # Scroll element into view before interacting
                        scroll_into_view(driver, corporate_type_element)

                        # Select the value
                        select = Select(corporate_type_element)
                        select.select_by_visible_text(body_corporate_type)

                        print(f"[✓] Body Corporate {position}: Selected Type of body corporate - {body_corporate_type}")
                        fields_filled_count += 1
                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding dropdown at absolute XPath.")
                        fields_failed_count += 1
                    except NoSuchElementException:
                        print(f"[✗] Body Corporate {position}: Dropdown not found at absolute XPath.")
                        fields_failed_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Unexpected error while selecting dropdown: {e}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No type provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing type: {e}")
                fields_failed_count += 1
            
            # --- Registration Number ---
            time.sleep(0.5)
            try:
                reg_number = corporate_details.get('registration_number', '').strip()
                if reg_number:
                    reg_number_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"
                    
                    try:
                        reg_number_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, reg_number_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, reg_number_input)
                        
                        # Clear and set value
                        reg_number_input.clear()
                        reg_number_input.send_keys(reg_number)
                        
                        print(f"[✓] Body Corporate {position}: Entered Registration Number: {reg_number}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Registration Number: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No registration number provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing registration number: {e}")
                fields_failed_count += 1

            # --- PAN ---
            time.sleep(0.5)
            try:
                pan = corporate_details.get('pan', '').strip()
                if pan:
                    pan_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[3]/div/div/div[2]/input"

                    try:
                        pan_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, pan_xpath))
                        )

                        # Scroll to view
                        scroll_into_view(driver, pan_input)
                        
                        # Clear and set value
                        pan_input.clear()
                        pan_input.send_keys(pan)
                        
                        print(f"[✓] Body Corporate {position}: Entered PAN: {pan}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting PAN: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No PAN provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing PAN: {e}")
                fields_failed_count += 1

            # --- Name of the Body Corporate ---
            time.sleep(0.5)
            try:
                name_value = corporate_details.get('name', '').strip()
                if name_value:
                    name_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[4]/div/div/div[2]/input"
                    
                    try:
                        name_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, name_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, name_input)
                        
                        # Clear and set value
                        name_input.clear()
                        name_input.send_keys(name_value)
                        
                        print(f"[✓] Body Corporate {position}: Entered Name: {name_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Name: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No name provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing name: {e}")
                fields_failed_count += 1

            # --- Address Line I ---
            time.sleep(0.5)
            try:
                address1_value = corporate_details.get('address', {}).get('line1', '').strip()
                if address1_value:
                    address1_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"
                    
                    try:
                        address1_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, address1_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, address1_input)
                        
                        # Clear and set value
                        address1_input.clear()
                        address1_input.send_keys(address1_value)
                        
                        print(f"[✓] Body Corporate {position}: Entered Address Line I: {address1_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Address Line I: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Address Line I provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Address Line I: {e}")
                fields_failed_count += 1

            # --- Address Line II ---
            time.sleep(0.5)
            try:
                address2_value = corporate_details.get('address', {}).get('line2', '').strip()
                if address2_value:
                    address2_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"
                    
                    try:
                        address2_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, address2_xpath))
                        )

                        # Scroll to view
                        scroll_into_view(driver, address2_input)
                        
                        # Clear and set value
                        address2_input.clear()
                        address2_input.send_keys(address2_value)
                        
                        print(f"[✓] Body Corporate {position}: Entered Address Line II: {address2_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Address Line II: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Address Line II provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Address Line II: {e}")
                fields_failed_count += 1


            # --- Country ---
            time.sleep(0.5)
            try:
                country_value = corporate_details.get('address', {}).get('country', '').strip()
                if country_value:
                    # Updated XPath for Country dropdown
                    country_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[3]/div/div/div[2]/select"
                    
                    try:
                        # Wait for dropdown to be present and clickable
                        country_select = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, country_xpath))
                        )

                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, country_select)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", country_select)
                        
                        time.sleep(0.5)  # Small delay after scrolling
                        
                        # Click to open dropdown
                        country_select.click()
                        time.sleep(0.5)  # Small delay after clicking
                        
                        # Send keys to filter and select
                        country_select.send_keys(country_value)
                        time.sleep(0.5)  # Small delay after sending keys
                        
                        # Press Enter to select
                        country_select.send_keys(Keys.ENTER)
                        
                        print(f"[✓] Body Corporate {position}: Selected Country: {country_value}")
                        fields_filled_count += 1
                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding Country dropdown (XPath: {country_xpath})")
                        fields_failed_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error selecting Country: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Country provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Country: {str(e)}")
                fields_failed_count += 1


            # --- Pin Code ---
            time.sleep(0.5)
            try:
                pincode_value = corporate_details.get('address', {}).get('pincode', '').strip()
                if pincode_value:
                    pincode_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[4]/div/div/div[2]/input"
                    
                    try:
                        pincode_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, pincode_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, pincode_input)
                        
                        # Clear and set value
                        pincode_input.clear()
                        pincode_input.send_keys(pincode_value)
                        
                        print(f"[✓] Body Corporate {position}: Entered Pin Code: {pincode_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Pin Code: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Pin Code provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Pin Code: {e}")
                fields_failed_count += 1


            # --- Area/Locality ---
            time.sleep(0.5)
            try:
                area_value = corporate_details.get('address', {}).get('area', '').strip()
                if area_value:
                    area_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[5]/div/div/div[2]/select"
                    
                    try:
                        area_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, area_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, area_input)
                        
                        # Clear and set value
                        time.sleep(2)
                        click_element(driver, xpath=area_xpath)
                        send_text(driver, xpath=area_xpath, keys=area_value)
                        
                        
                        print(f"[✓] Body Corporate {position}: Entered Area/Locality: {area_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Area/Locality: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Area/Locality provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Area/Locality: {e}")
                fields_failed_count += 1


            # --- Jurisdiction of Police Station ---
            time.sleep(0.5)
            try:
                jurisdiction_value = corporate_details.get('address', {}).get('jurisdiction', '').strip()
                if jurisdiction_value:
                    jurisdiction_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[7]/div/div/div/div[1]/div/div[10]/div/div/div[2]/input"
                    
                    try:
                        jurisdiction_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, jurisdiction_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, jurisdiction_input)
                        
                        # Clear and set value
                        jurisdiction_input.clear()
                        jurisdiction_input.send_keys(jurisdiction_value)
                        
                        print(f"[✓] Body Corporate {position}: Entered Jurisdiction: {jurisdiction_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Jurisdiction: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Jurisdiction provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Jurisdiction: {e}")
                fields_failed_count += 1


            # --- Contact Details ---
            contact = corporate_details.get('contact', {})
            
            # Phone
            time.sleep(0.5)
            try:
                phone_value = contact.get('phone', '').strip()
                if phone_value:
                    phone_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[10]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"
                    
                    try:
                        phone_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, phone_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, phone_input)
                        
                        # Clear and set value
                        phone_input.clear()
                        phone_input.send_keys(phone_value)
                        
                        print(f"[✓] Body Corporate {position}: Entered Phone: {phone_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Phone: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Phone provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Phone: {e}")
                fields_failed_count += 1


            # Mobile
            time.sleep(0.5)
            try:
                mobile_value = contact.get('mobile', '').strip()
                if mobile_value:
                    mobile_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[10]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"
                    
                    try:
                        mobile_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, mobile_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, mobile_input)
                        
                        # Clear and set value
                        mobile_input.clear()
                        mobile_input.send_keys(mobile_value)
                        
                        print(f"[✓] Body Corporate {position}: Entered Mobile: {mobile_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Mobile: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Mobile provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Mobile: {e}")
                fields_failed_count += 1

            # Fax
            time.sleep(0.5)
            try:
                fax_value = contact.get('fax', '').strip()
                if fax_value:
                    fax_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[10]/div/div/div/div[1]/div/div[3]/div/div/div[2]/input"
                    
                    try:
                        fax_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, fax_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, fax_input)
                        
                        # Clear and set value
                        fax_input.clear()
                        fax_input.send_keys(fax_value)
                        
                        print(f"[✓] Body Corporate {position}: Entered Fax: {fax_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Fax: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Fax provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Fax: {e}")
                fields_failed_count += 1

            # Email
            time.sleep(0.5)
            try:
                email_value = contact.get('email', '').strip()
                if email_value:
                    email_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[10]/div/div/div/div[1]/div/div[4]/div/div/div[2]/input"
                    
                    try:
                        email_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, email_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, email_input)
                        
                        # Clear and set value
                        email_input.clear()
                        email_input.send_keys(email_value)
                        
                        print(f"[✓] Body Corporate {position}: Entered Email: {email_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Email: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Email provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Email: {e}")
                fields_failed_count += 1


            # --- Contribution Details ---
            # Form of contribution
            time.sleep(0.5)
            try:
                form_value = contribution.get('form', '').strip()
                if form_value:
                    form_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[1]/div/div/div[2]/select"
                    
                    try:
                        form_select = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, form_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, form_select)
                        
                        # Select value
                        select = Select(form_select)
                        select.select_by_visible_text(form_value)
                        
                        print(f"[✓] Body Corporate {position}: Selected Form of contribution: {form_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error selecting Form of contribution: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Form of contribution provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Form of contribution: {e}")
                fields_failed_count += 1

            # If form is "Other than cash", handle other_specify
            if form_value and form_value.lower() == "other than cash":
                time.sleep(0.5)
                try:
                    other_specify_value = contribution.get('other_specify', '').strip()
                    if other_specify_value:
                        other_specify_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"
                        
                        try:
                            other_specify_input = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, other_specify_xpath))
                            )
                            
                            # Scroll to view
                            scroll_into_view(driver, other_specify_input)
                            
                            # Clear and set value
                            other_specify_input.clear()
                            other_specify_input.send_keys(other_specify_value)
                            
                            print(f"[✓] Body Corporate {position}: Entered Other specify: {other_specify_value}")
                            fields_filled_count += 1
                        except Exception as e:
                            print(f"[✗] Body Corporate {position}: Error setting Other specify: {str(e)}")
                            fields_failed_count += 1
                    else:
                        print(f"[INFO] Body Corporate {position}: No Other specify provided in data.")
                except Exception as e:
                    print(f"[✗] Body Corporate {position}: Exception while processing Other specify: {e}")
                    fields_failed_count += 1

            # Monetary value
            time.sleep(0.5)
            try:
                value_figures = contribution.get('value_figures', '').strip()
                if value_figures:
                    value_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[3]/div/div/div[2]/input"
                    
                    try:
                        value_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, value_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, value_input)
                        
                        # Clear and set value
                        value_input.clear()
                        value_input.send_keys(value_figures)
                        
                        print(f"[✓] Body Corporate {position}: Entered Monetary value: {value_figures}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Monetary value: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Monetary value provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Monetary value: {e}")
                fields_failed_count += 1

            # Number of LLPs
            time.sleep(0.5)
            try:
                llp_count = contribution.get('llp_count', '0')
                if llp_count:
                    llp_count_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[5]/div/div/div[2]/input"
                    
                    try:
                        llp_count_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, llp_count_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, llp_count_input)
                        
                        # Clear and set value
                        llp_count_input.clear()
                        llp_count_input.send_keys(str(llp_count))
                        
                        print(f"[✓] Body Corporate {position}: Entered Number of LLPs: {llp_count}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Number of LLPs: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Number of LLPs provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Number of LLPs: {e}")
                fields_failed_count += 1

            # Number of companies
            time.sleep(0.5)
            try:
                company_count = contribution.get('company_count', '0')
                if company_count:
                    company_count_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[6]/div/div/div[2]/input"
                    
                    try:
                        company_count_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, company_count_xpath))
                        )
                        
                        # Scroll to view
                        scroll_into_view(driver, company_count_input)
                        
                        # Clear and set value
                        company_count_input.clear()

                        send_text(driver, xpath=company_count_xpath, keys=company_count)
                        
                        print(f"[✓] Body Corporate {position}: Entered Number of companies: {company_count}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Number of companies: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Number of companies provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Number of companies: {e}")
                fields_failed_count += 1

            print(f"\n[INFO] Finished filling details for body corporate {position}. Fields Filled: {fields_filled_count}, Fields Failed: {fields_failed_count}")


            # --- Nominee Details ---
            # --- First Name ---
            try:
                first_name = body.get("nominee", {}).get("first_name", "").strip()

                if first_name:
                    # Static XPath for First Name with dynamic index i
                    first_name_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"

                    try:
                        first_name_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, first_name_xpath))
                        )

                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, first_name_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_name_input)

                        # Use send_text directly
                        send_text(driver, xpath=first_name_xpath, keys=first_name)
                        time.sleep(0.2)

                        # Confirm value
                        actual_value = first_name_input.get_attribute("value")
                        if actual_value and actual_value.strip().lower() == first_name.lower():
                            print(f"[✓] Body Corporate {position}: First Name entered: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[✗] Body Corporate {position}: First Name mismatch (Expected: {first_name}, Found: {actual_value})")
                            fields_failed_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting First Name (XPath: {first_name_xpath}): {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[!] Body Corporate {position}: First Name missing in data. Skipping.")
            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in First Name block: {str(e_outer)}")
                fields_failed_count += 1

            
            # --- Middle Name ---
            try:
                middle_name = body.get("nominee", {}).get("middle_name", "").strip()

                if first_name:
                    # Static XPath for First Name with dynamic index i
                    middle_name_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"

                    try:
                        middle_name_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, middle_name_xpath))
                        )

                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, middle_name_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", middle_name_input)

                        # Use send_text directly
                        send_text(driver, xpath=middle_name_xpath, keys=middle_name)
                        time.sleep(0.2)

                        # Confirm value
                        actual_value = middle_name_input.get_attribute("value")
                        if actual_value and actual_value.strip().lower() == middle_name.lower():
                            print(f"[✓] Body Corporate {position}: Mddie Name entered: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[✗] Body Corporate {position}: Middle Name mismatch (Expected: {middle_name}, Found: {actual_value})")
                            fields_failed_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Middle Name (XPath: {middle_name_xpath}): {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[!] Body Corporate {position}: Middle Name missing in data. Skipping.")
            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in First Name block: {str(e_outer)}")
                fields_failed_count += 1


            # --- Surname ---
            try:
                surname = body.get("nominee", {}).get("surname", "").strip()
                
                if surname:
                    # Static XPath for First Name with dynamic index i
                    surname_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div[2]/input"

                    try:
                        surname_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, surname_xpath))
                        )
                        
                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, surname_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", surname_input)
                        
                        
                        # Use send_text directly
                        send_text(driver, xpath=surname_xpath, keys=surname)
                        time.sleep(0.2)
                        
                        # Confirm value
                        actual_value = surname_input.get_attribute("value")
                        if actual_value and actual_value.strip().lower() == surname.lower():
                            print(f"[✓] Body Corporate {position}: Surname entered: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[✗] Body Corporate {position}: Surname mismatch (Expected: {surname}, Found: {actual_value})")
                            fields_failed_count += 1

                    except Exception as e:  
                        print(f"[✗] Body Corporate {position}: Error setting Surname (XPath: {surname_xpath}): {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[!] Body Corporate {position}: Surname missing in data. Skipping.")
            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Surname block: {str(e_outer)}")
                fields_failed_count += 1


            # --- Father's First Name ---
            try:
                father_first_name = body.get("nominee", {}).get("father_first", "").strip()
                
                if father_first_name:
                    # Static XPath for First Name with dynamic index i
                    father_first_name_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[5]/div/div/div[2]/input"

                    try:
                        father_first_name_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, father_first_name_xpath))
                        )
                        
                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, father_first_name_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", father_first_name_input)
                        
                        # Use send_text directly
                        send_text(driver, xpath=father_first_name_xpath, keys=father_first_name)
                        time.sleep(0.2)

                        # Confirm value
                        actual_value = father_first_name_input.get_attribute("value")
                        if actual_value and actual_value.strip().lower() == father_first_name.lower():
                            print(f"[✓] Body Corporate {position}: Father's First Name entered: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[✗] Body Corporate {position}: Father's First Name mismatch (Expected: {father_first_name}, Found: {actual_value})")
                            fields_failed_count += 1

                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Father's First Name (XPath: {father_first_name_xpath}): {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[!] Body Corporate {position}: Father's First Name missing in data. Skipping.")
            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Father's First Name block: {str(e_outer)}")
                fields_failed_count += 1


            # --- Father's Middle Name ---
            try:
                father_middle_name = body.get("nominee", {}).get("father_middle", "").strip()
                
                if father_middle_name:
                    # Static XPath for First Name with dynamic index i
                    father_middle_name_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[6]/div/div/div[2]/input"

                    try:
                        father_middle_name_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, father_middle_name_xpath))
                        )
                        
                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, father_middle_name_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", father_middle_name_input)
                        
                        # Use send_text directly
                        send_text(driver, xpath=father_middle_name_xpath, keys=father_middle_name)
                        time.sleep(0.2)

                        # Confirm value
                        actual_value = father_middle_name_input.get_attribute("value")
                        if actual_value and actual_value.strip().lower() == father_middle_name.lower():
                            print(f"[✓] Body Corporate {position}: Father's Middle Name entered: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[✗] Body Corporate {position}: Father's Middle Name mismatch (Expected: {father_middle_name}, Found: {actual_value})")
                            fields_failed_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Father's Middle Name (XPath: {father_middle_name_xpath}): {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[!] Body Corporate {position}: Father's Middle Name missing in data. Skipping.")
            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Father's Middle Name block: {str(e_outer)}")
                fields_failed_count += 1
            
            # --- Father's Surname ---
            try:
                father_surname = body.get("nominee", {}).get("father_surname", "").strip()
                
                if father_surname:
                    # Static XPath for First Name with dynamic index i
                    father_surname_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[7]/div/div/div[2]/input"

                    try:
                        father_surname_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, father_surname_xpath))
                        )
                        
                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, father_surname_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", father_surname_input)
                        
                        # Use send_text directly
                        send_text(driver, xpath=father_surname_xpath, keys=father_surname)
                        time.sleep(0.2)

                        # Confirm value
                        actual_value = father_surname_input.get_attribute("value")
                        if actual_value and actual_value.strip().lower() == father_surname.lower():
                            print(f"[✓] Body Corporate {position}: Father's Surname entered: {actual_value}")
                            fields_filled_count += 1
                        else:
                            print(f"[✗] Body Corporate {position}: Father's Surname mismatch (Expected: {father_surname}, Found: {actual_value})")
                            fields_failed_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Father's Surname (XPath: {father_surname_xpath}): {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[!] Body Corporate {position}: Father's Surname missing in data. Skipping.")
            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Father's Surname block: {str(e_outer)}")
                fields_failed_count += 1
            

            # --- Gender ---
            try:
                gender = body.get("nominee", {}).get("gender", "").strip()
                
                if gender:
                    # Static XPath for First Name with dynamic index i
                    gender_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[8]/div/div/div[2]/select"

                    try:
                        gender_select = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, gender_xpath))
                        )
                        
                        # Scroll to view    
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, gender_select)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gender_select)
                        
                        click_element(driver, xpath=gender_xpath)
                        send_text(driver, xpath=gender_xpath, keys=gender)
                        
                        print(f"[✓] Body Corporate {position}: Selected Gender: {gender}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error selecting Gender: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[!] Body Corporate {position}: Gender missing in data. Skipping.")
            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Gender block: {str(e_outer)}")
                fields_failed_count += 1

            # --- Date of Birth ---
            try:
                dob = body.get("nominee", {}).get("dob", "").strip()
                if dob:
                    # Static XPath with dynamic index i
                    dob_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[9]/div/div/div[2]/div/input"

                    try:
                        dob_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, dob_xpath))
                        )

                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, dob_input)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dob_input)

                        # Get or set an ID for the DOB input
                        dob_id = dob_input.get_attribute("id")
                        if not dob_id:
                            dob_id = f"dob_input_{int(time.time())}"
                            driver.execute_script(f"arguments[0].id = '{dob_id}';", dob_input)

                        # Use set_date_field helper
                        if set_date_field(driver, dob_id, dob):
                            print(f"[✓] Body Corporate {position}: Date of Birth filled: {dob}")
                            fields_filled_count += 1
                        else:
                            print(f"[✗] Body Corporate {position}: Failed to set Date of Birth: {dob}")
                            fields_failed_count += 1

                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding DOB input field (i={i}).")
                        fields_failed_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting DOB (XPath: {dob_xpath}): {e}")
                        fields_failed_count += 1
                else:
                    print(f"[!] Body Corporate {position}: Date of Birth missing. Skipping.")
            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Date of Birth block: {e_outer}")
                fields_failed_count += 1

            
            # --- Nationality ---
            try:
                nationality = body.get("nominee", {}).get("nationality", "").strip()
                
                if nationality:
                    # Static XPath for First Name with dynamic index i
                    nationality_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[10]/div/div/div[2]/select"

                    try:
                        nationality_select = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, nationality_xpath))
                        )
                        nationality_select.click()
                        time.sleep(0.5)
                        nationality_select.send_keys(nationality)
                        time.sleep(0.5)
                        nationality_select.send_keys(Keys.ENTER)
                        print(f"[✓] Body Corporate {position}: Selected Nationality: {nationality}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error selecting Nationality: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[!] Body Corporate {position}: Nationality missing in data. Skipping.")
            except Exception as e_outer:
                print(f"[✗] Body Corporate {position}: Unexpected error in Nationality block: {str(e_outer)}")
                fields_failed_count += 1

            # --- Resident ---
            time.sleep(0.5)
            try:
                # Parse boolean value
                is_resident = body.get("nominee", {}).get("resident", "").strip().lower() == "yes"

                # Static XPath for the nominee resident field container with dynamic index i
                radio_container_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[11]/div/div/div[2]"

                radio_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, radio_container_xpath))
                )

                # Scroll into view
                if callable(globals().get('scroll_into_view')):
                    scroll_into_view(driver, radio_container)
                else:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_container)

                if is_resident:
                    try:
                        yes_radio = radio_container.find_element(By.XPATH, ".//input[@type='radio' and @aria-label='Yes']")
                        driver.execute_script("arguments[0].click();", yes_radio)
                        print(f"[✓] Body Corporate {position}: Clicked 'Yes' for nominee residency (i={i}).")
                        fields_filled_count += 1
                    except NoSuchElementException:
                        print(f"[✗] Body Corporate {position}: Could not find 'Yes' radio button.")
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error clicking 'Yes' for nominee residency (i={i}): {e}")
                else:
                    try:
                        no_radio = radio_container.find_element(By.XPATH, ".//input[@type='radio' and @aria-label='No']")
                        driver.execute_script("arguments[0].click();", no_radio)
                        print(f"[✓] Body Corporate {position}: Clicked 'No' for nominee residency (i={i}).")
                        fields_filled_count += 1
                    except NoSuchElementException:
                        print(f"[✗] Body Corporate {position}: Could not find 'No' radio button.")
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error clicking 'No' for nominee residency (i={i}): {e}")

            except TimeoutException:
                print(f"[✗] Body Corporate {position}: Timeout finding nominee residency container (i={i}).")
                fields_failed_count += 1
            except NoSuchElementException:
                print(f"[✗] Body Corporate {position}: Could not find nominee residency radio group (i={i}).")
                fields_failed_count += 1
            except Exception as e:
                print(f"[FAIL] Body Corporate {position}: Unexpected error in nominee residency block (i={i}): {e}")
                fields_failed_count += 1

            
            # --- PAN/Passport number ---
            time.sleep(0.5)
            try:
                        pan_passport_details = body.get('nominee', {}).get('pan/passport', '').strip()
                        if pan_passport_details:
                            details_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[14]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"
                            details_xpath = f"{details_xpath_base}//input[@aria-label='Income-tax PAN/Passport number details ']"
                            details_input = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, details_xpath))
                            )
                            details_input.clear()
                            details_input.send_keys(pan_passport_details)
                            print(f"[✓] Partner {position}: Entered Income-tax PAN/Passport number details: {pan_passport_details} (i={i}).")
                            fields_filled_count += 1
                        else:
                            print(f"[INFO] Partner {position}: No Income-tax PAN/Passport number details provided in data.")
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Income-tax PAN/Passport number details input.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Income-tax PAN/Passport number details input.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Failed to enter Income-tax PAN/Passport number details: {e}")
                        fields_failed_count += 1
            
           # --- Income-tax PAN/Passport number details ---
            time.sleep(0.5)
            try:
                pan_passport_details = body.get("nominee", {}).get("pan/passport", "").strip()
                
                if pan_passport_details:
                    # ✅ Updated XPath
                    details_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[14]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"

                    # Wait for the input field
                    details_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, details_xpath))
                    )

                    # Scroll into view
                    if callable(globals().get('scroll_into_view')):
                        scroll_into_view(driver, details_input)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", details_input)

                    # Clear and set value using JS (handles read-only fields)
                    driver.execute_script("arguments[0].value = '';", details_input)
                    driver.execute_script("arguments[0].value = arguments[1];", details_input, pan_passport_details)

                    # Trigger events
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", details_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", details_input)

                    # Send keys using helper for robustness
                    send_text(driver, xpath=details_xpath, keys=pan_passport_details)

                    print(f"[✓] Partner {position}: Entered Income-tax PAN/Passport number details: {pan_passport_details} (i={i}).")
                    fields_filled_count += 1
                else:
                    print(f"[INFO] Partner {position}: No Income-tax PAN/Passport number details provided in data.")
            except TimeoutException:
                print(f"[✗] Partner {position}: Timeout finding Income-tax PAN/Passport number details input.")
            except NoSuchElementException:
                print(f"[✗] Partner {position}: Could not find Income-tax PAN/Passport number details input.")
            except Exception as e:
                print(f"[✗] Partner {position}: Failed to enter Income-tax PAN/Passport number details: {e}")
                fields_failed_count += 1

            # --- Verify PAN Button ---
            time.sleep(0.5)
            try:
                        verify_pan_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[14]/div/div/div/div[1]/div/div[3]/div/div/div[1]/button"
                        verify_pan_xpath = f"{verify_pan_xpath_base}/button[@aria-label='Verify PAN']"

                        verify_pan_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, verify_pan_xpath))
                        )
                        # driver.execute_script("arguments[0].click();", verify_pan_button)
                        click_element(driver, verify_pan_xpath)
                        print(f"[SUCCESS] Partner {position}: Clicked Verify PAN button (i={i}).")
                        fields_filled_count += 1
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Verify PAN button.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Verify PAN button.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Failed to click Verify PAN button: {e}")
                        fields_failed_count += 1

            # --- Place of Birth (State) ---            
            try:
                        birth_state = body.get("nominee", {}).get("birth_state", "").strip()
                        if birth_state:
                            dropdown_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[15]/div/div/div[2]/select"  # your full XPath here

                            birth_state_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, dropdown_xpath))
                            )

                            # Use Select class to choose the option
                            time
                            select = Select(birth_state_element)
                            select.select_by_visible_text(birth_state)

                            print(f"[✓] Partner {position}: Selected Place of Birth (State) - {birth_state}")
                        else:
                            print(f"[INFO] Partner {position}: Place of Birth (State) not provided.")
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Place of Birth (State) dropdown.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Place of Birth (State) dropdown.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Error selecting Place of Birth (State) (i={i}): {e}")

 
            # --- Place of Birth (District) ---
            time.sleep(5)
            try:
                        district_value = body.get('nominee', {}).get('birth_district', '').strip()
                        if district_value:
                            dropdown_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[16]/div/div/div[2]/select"

                            birth_district_dropdown = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, dropdown_xpath))
                            )
                
                            # Click to open the dropdown (if necessary)
                            birth_district_dropdown.click()
                            time.sleep(2)

                            # Send keys to filter and select (behavior depends on the dropdown)
                            birth_district_dropdown.send_keys(district_value)
                            time.sleep(0.5)

                            # Press Enter to select (if necessary)
                            birth_district_dropdown.send_keys(Keys.ENTER)
                            print(f"[✓] Partner {position}: Selected Place of Birth (District) '{district_value}' (i={i}).")
                            fields_filled_count += 1
                        else:
                            print(f"[INFO] Partner {position}: Place of Birth (District) not provided.")
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Place of Birth (District) dropdown.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Place of Birth (District) dropdown.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Error selecting Place of Birth (District) (i={i}): {e}")
                        fields_filled_count += 1


            # --- Whether citizen of India ---
            time.sleep(0.5)
            try:
                citizen_value = body.get('nominee', {}).get('citizen', '').strip().lower()
                if citizen_value:
                    # Updated XPath with correct static structure and dynamic i
                    radio_container_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[17]/div/div/div[2]"
                    radio_xpath = f"{radio_container_xpath_base}//input[@type='radio' and @aria-label='{citizen_value.title()}']"

                    for attempt in range(3):
                        try:
                            radio_input = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, radio_xpath))
                            )

                            # Ensure it's interactable
                            driver.execute_script("""
                                arguments[0].style.display = 'block';
                                arguments[0].style.visibility = 'visible';
                                arguments[0].style.opacity = '1';
                                arguments[0].removeAttribute('readonly');
                                arguments[0].removeAttribute('disabled');
                            """, radio_input)

                            # Scroll into view and click
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_input)
                            time.sleep(0.3)
                            radio_input.click()
                            time.sleep(0.3)

                            # Confirm selection
                            if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                                print(f"[✓] Partner {position}: Selected Whether citizen of India: {citizen_value.title()}")
                                fields_filled_count += 1
                                break
                            else:
                                print(f"[RETRY {attempt+1}] Not selected, retrying...")
                        except Exception as e:
                            print(f"[RETRY {attempt+1}] Error clicking radio: {e}")
                            time.sleep(1)
                    else:
                        print("[FAIL] Could not select 'Whether citizen of India' after all retries")
                        fields_failed_count += 1
                else:
                    print("[INFO] No value provided for 'Whether citizen of India'")
                    fields_failed_count += 1
            except TimeoutException:
                print(f"[✗] Partner {position}: Timeout finding 'Whether citizen of India' container.")
                fields_failed_count += 1
            except NoSuchElementException:
                print(f"[✗] Partner {position}: Could not find 'Whether citizen of India' label/container.")
                fields_failed_count += 1
            except Exception as e:
                print(f"[ERROR] Partner {position}: Exception in 'Whether citizen of India': {e}")
                fields_failed_count += 1

            # --- Occupation type ---
            time.sleep(0.5)
            try:
                occupation_type = body.get("nominee", {}).get('occupation_type', '').strip()
                if occupation_type:
                    # Updated XPath for Occupation Type dropdown
                    occupation_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[18]/div/div/div[2]/select"

                    try:
                        # Wait for dropdown to be present and clickable
                        occupation_dropdown = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, occupation_xpath))
                        )
                        
                        # Scroll into view
                        if callable(globals().get('scroll_into_view')):
                            scroll_into_view(driver, occupation_dropdown)
                        else:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", occupation_dropdown)
                        
                        time.sleep(0.5)  # Small delay after scrolling
                        
                        # Click to open dropdown
                        occupation_dropdown.click()
                        time.sleep(0.5)  # Small delay after clicking
                        
                        # Send keys to filter and select
                        occupation_dropdown.send_keys(occupation_type)
                        time.sleep(0.5)  # Small delay after sending keys
                        
                        # Press Enter to select
                        occupation_dropdown.send_keys(Keys.ENTER)
                        
                        print(f"[✓] Partner {position}: Selected Occupation type: {occupation_type}")
                        fields_filled_count += 1

                        # Handle 'Others' case
                        if occupation_type.lower() == 'others':
                            others_description = body.get("nominee", {}).get('occupation_other', '').strip()
                            if others_description:
                                # Updated XPath for 'Description of others' input
                                others_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[19]/div/div/div[2]/input"

                                others_input = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, others_xpath))
                                )
                                others_input.send_keys(others_description)
                                print(f"[✓] Partner {position}: Filled 'Description of others': '{others_description}'")
                                fields_filled_count += 1
                            else:
                                print(f"[INFO] Partner {position}: 'Description of others' not provided.")
                    except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Occupation type dropdown.")
                        fields_failed_count += 1
                    except Exception as e:
                        print(f"[✗] Partner {position}: Error selecting Occupation type: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Partner {position}: Occupation type not provided.")
            except Exception as e:
                print(f"[✗] Partner {position}: Exception while processing Occupation type: {str(e)}")
                fields_failed_count += 1


            # --- Area of Occupation ---
            time.sleep(0.5)
            try:
                area_of_occupation = body.get("nominee", {}).get('Area of Occupation', '').strip()
                if area_of_occupation:
                    # Wrap XPath(s) in a list so we can iterate properly
                    area_xpath_patterns = [
                        f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[20]/div/div/div[2]/select"
                    ]

                    area_dropdown = None
                    used_xpath = None

                    for xpath in area_xpath_patterns:
                        try:
                            print(f"[DEBUG] Trying XPath for Area of Occupation: {xpath}")
                            area_dropdown = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.XPATH, xpath))
                            )
                            used_xpath = xpath
                            break
                        except TimeoutException:
                            continue

                    if area_dropdown:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", area_dropdown)
                        time.sleep(1)

                        area_dropdown = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, used_xpath))
                        )

                        try:
                            select = Select(area_dropdown)
                            select.select_by_visible_text(area_of_occupation)
                        except Exception:
                            area_dropdown.click()
                            area_dropdown.send_keys(area_of_occupation)
                            area_dropdown.send_keys(Keys.ENTER)

                        selected_value = area_dropdown.get_attribute('value')
                        if selected_value and area_of_occupation.lower() in selected_value.lower():
                            print(f"[✓] Partner {position}: Selected Area of Occupation: {area_of_occupation}")
                            fields_filled_count += 1
                        else:
                            print(f"[✗] Partner {position}: Failed to verify Area of Occupation selection")
                            fields_failed_count += 1

                        # Handle 'Others' option
                        if area_of_occupation.lower() == 'others':
                            others_specify = body.get("nominee", {}).get("If 'Others' selected, please specify", '').strip()
                            if others_specify:
                                others_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[20]/div/div/div[2]/input"
                                try:
                                    others_input = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.XPATH, others_xpath))
                                    )
                                    others_input.clear()
                                    others_input.send_keys(others_specify)
                                    print(f"[✓] Partner {position}: Filled 'If Others selected, please specify': '{others_specify}'")
                                    fields_filled_count += 1
                                except Exception as e:
                                    print(f"[✗] Partner {position}: Error filling 'Others' specification: {str(e)}")
                                    fields_failed_count += 1
                            else:
                                print(f"[INFO] Partner {position}: 'If Others selected, please specify' not provided.")
                    else:
                        print(f"[✗] Partner {position}: Could not find Area of Occupation dropdown with any XPath pattern")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Partner {position}: Area of Occupation not provided.")
            except Exception as e:
                print(f"[✗] Partner {position}: Exception while processing Area of Occupation: {str(e)}")
                fields_failed_count += 1


            # --- Educational qualification ---
            time.sleep(0.5)
            try:
                educational_qualification = body.get("nominee", {}).get("education", "").strip()
                if educational_qualification:
                    # ✅ Updated XPath for Educational qualification dropdown
                    education_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[22]/div/div/div[2]/select"

                    education_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, education_xpath))
                    )
                    
                    # Click the dropdown first
                    education_dropdown.click()
                    time.sleep(0.5)
                    
                    # Then send the text
                    education_dropdown.send_keys(educational_qualification)
                    time.sleep(0.5)
                    
                    # Press Enter to select
                    education_dropdown.send_keys(Keys.ENTER)

                    print(f"[✓] Partner {position}: Selected Educational qualification: '{educational_qualification}' (i={i}).")
                    fields_filled_count += 1

                    # ✅ Handle 'Others' case
                    if educational_qualification.lower() == 'others':
                        education_others = body.get("nominee", {}).get('education_other', '').strip()
                        if education_others:
                            # ✅ Updated XPath for 'Others' input
                            others_input_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[23]/div/div/div[2]/input"

                            others_input = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, others_input_xpath))
                            )
                            others_input.send_keys(education_others)
                            print(f"[✓] Partner {position}: Filled 'If Others' selected for education: '{education_others}' (i={i}).")
                            fields_filled_count += 1
                        else:
                            print(f"[INFO] Partner {position}: 'Educational qualification others' not provided.")
                else:
                    print(f"[INFO] Partner {position}: Educational qualification not provided.")
            except TimeoutException:
                print(f"[✗] Partner {position}: Timeout finding Educational qualification dropdown.")
                fields_failed_count += 1
            except NoSuchElementException:
                print(f"[✗] Partner {position}: Could not find Educational qualification dropdown or 'If Others' specify input.")
                fields_failed_count += 1
            except Exception as e:
                print(f"[✗] Partner {position}: Error selecting Educational qualification (i={i}): {e}")
                fields_failed_count += 1

            # --- Mobile No. ---
            time.sleep(1)
            try:
                mobile_value = body.get('nominee', {}).get('mobile', '').strip()

                if mobile_value:
                    # ✅ Updated XPath for Mobile No. input
                    mobile_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[24]/div/div/div[2]/input"
                    
                    try:
                        mobile_input = WebDriverWait(driver, 10).until(
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

            
            # --- Email ID ---
            time.sleep(0.5)
            try:
                email_value = body.get("nominee", {}).get('email', '').strip()
                if email_value:
                    # Static XPath for Email input with dynamic index i
                    email_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[25]/div/div/div[2]/input"
                    

                    try:
                        email_input = WebDriverWait(driver, 10).until(
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




            # ---Permanent address---



            # --- Address Line I ---
            try:
                address1_value = body.get('permanent_address', {}).get('line1', '').strip()
                
                if address1_value:
                    # Updated XPath for "Address Line I" using index i
                    address1_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[22]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"

                    # Wait for the field to appear
                    address1_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, address1_xpath))
                    )

                    # Scroll to the element using helper function or JS fallback
                    if callable(globals().get('scroll_into_view')):
                        scroll_into_view(driver, address1_input)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", address1_input)

                    # Clear existing value and set new one using JavaScript
                    driver.execute_script("arguments[0].value = '';", address1_input)
                    driver.execute_script("arguments[0].value = arguments[1];", address1_input, address1_value)

                    # Dispatch 'input' and 'change' events
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", address1_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", address1_input)

                    # Also use send_text if needed (defensive double entry)
                    send_text(driver, xpath=address1_xpath, keys=address1_value)

                    fields_filled_count += 1
                    print(f"[✓] Body Corporate {position}: Entered Address Line I: {address1_value}")
                
                else:
                    print(f"[!] Body Corporate {position}: 'Address Line I' is empty or missing in input data. Skipping.")


            except Exception as e:
                print(f"[✗] Body Corporate {position}: Failed to fill 'Address Line I' due to error: {str(e)}")
                fields_failed_count += 1


            # --- Address Line II ---
            try:
                address2_value = body.get('permanent_address', {}).get('line2', '').strip()
                
                if address2_value:
                    # Updated static XPath with dynamic 'i'
                    address2_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[22]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"
                    

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
                country_value = body.get('permanent_address', {}).get('country', '').strip()
                
                if country_value:
                    try:
                        # Static XPath for the Country dropdown, with dynamic index i
                        country_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[22]/div/div/div/div[1]/div/div[3]/div/div/div[2]/select"

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
                pincode_value = body.get('permanent_address', {}).get('pincode', '').strip()

                if pincode_value:
                    # Static XPath for Pin code input with dynamic index 'i'
                    pincode_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[22]/div/div/div/div[1]/div/div[4]/div/div/div[2]/input"
                

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

                        time.sleep(0.5)
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



            # --- Area/Locality ---
            time.sleep(0.5)
            try:
                area_value = body.get('permanent_address', {}).get('area', '').strip()
                if area_value:
                    area_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[22]/div/div/div/div[1]/div/div[5]/div/div/div[2]/select"

                    try:
                        area_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, area_xpath))
                        )

                        # Scroll to view
                        scroll_into_view(driver, area_input)
                        
                        # Clear and set value
                        time.sleep(2)
                        click_element(driver, xpath=area_xpath)
                        time.sleep(2)
                        send_text(driver, xpath=area_xpath, keys=area_value)


                        print(f"[✓] Body Corporate {position}: Entered Area/Locality: {area_value}")
                        fields_filled_count += 1
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error setting Area/Locality: {str(e)}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: No Area/Locality provided in data.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Exception while processing Area/Locality: {e}")
                fields_failed_count += 1


             # --- Jurisdiction of Police Station (readonly text) ---
            try:
                police_value = body.get('permanent_address', {}).get('jurisdiction', '').strip()

                if police_value:
                    # Static XPath for Police Station input with dynamic index i
                    police_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[22]/div/div/div/div[1]/div/div[10]/div/div/div[2]/input"
                    
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
                phone_value = body.get('permanent_address', {}).get('phone', '').strip()

                if phone_value:
                    # Static XPath for Phone input with dynamic index i
                    phone_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[22]/div/div/div/div[1]/div/div[11]/div/div/div[2]/input"

                    try:
                        phone_input = WebDriverWait(driver, 10).until(
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

            

            # --- Whether present residential address same as permanent ---
            time.sleep(0.5)
            try:
                same_address_data = body.get('present_same', {})
                label = next((k for k, v in same_address_data.items() if v.lower() == 'true'), None) if isinstance(same_address_data, dict) else None

                if label:
                    # ✅ Updated static XPath
                    radio_container_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[22]/div/div/div/div[1]/div/div[12]/div/div/div[2]"
                    
                    radio_container = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, radio_container_xpath_base))
                    )
                    
                    yes_radio_xpath = f"{radio_container_xpath_base}//input[@type='radio' and @aria-label='Yes']"
                    no_radio_xpath = f"{radio_container_xpath_base}//input[@type='radio' and @aria-label='No']"

                    if label.lower() == 'yes':
                        try:
                            yes_radio = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, yes_radio_xpath))
                            )
                            yes_radio.click()
                            print(f"[✓] Partner {position}: Selected 'Yes' for Whether present address same as permanent (i={i}).")
                            fields_filled_count += 1
                        except Exception as e:
                            print(f"[✗] Partner {position}: Error clicking 'Yes' for Whether present address same as permanent (i={i}): {e}")
                            fields_failed_count += 1
                    elif label.lower() == 'no':
                        try:
                            no_radio = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, no_radio_xpath))
                            )
                            no_radio.click()
                            print(f"[✓] Partner {position}: Selected 'No' for Whether present address same as permanent (i={i}).")
                            fields_filled_count += 1
                        except Exception as e:
                            print(f"[✗] Partner {position}: Error clicking 'No' for Whether present address same as permanent (i={i}): {e}")
                        fields_failed_count += 1
                else:
                        print(f"[INFO] Partner {position}: Invalid value for 'Whether present address same as permanent': {label}")
                
            except TimeoutException:
                print(f"[✗] Partner {position}: Timeout finding 'Whether present address same as permanent' container.")
            except NoSuchElementException:
                print(f"[✗] Partner {position}: Could not find 'Whether present address same as permanent' label/container.")
            except Exception as e:
                print(f"[ERROR] Exception in 'Whether present address same as permanent': {e}")
                fields_failed_count += 1

            
            # --- Present Address ---
            try:
                present_address_data = body.get('present_address', {})
                if present_address_data:
                    # --- Address Line I ---
                    address1_value = present_address_data.get('line1', '').strip()
                    if address1_value:
                        address1_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[25]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"

                        # Wait for the input field
                        address1_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, address1_xpath))
                        )

                        driver.execute_script("arguments[0].value = arguments[1];", address1_input, address1_value)
                        print(f"[✓] Body Corporate {position}: Entered Address Line I: {address1_value}")
                        fields_filled_count += 1
                    else:
                        print(f"[INFO] Body Corporate {position}: 'Address Line I' is empty or missing in input data. Skipping.")

                    # --- Address Line II ---
                    address2_value = present_address_data.get('line2', '').strip()
                    if address2_value:
                        address2_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[25]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"

                        address2_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, address2_xpath))
                        )

                        driver.execute_script("arguments[0].value = arguments[1];", address2_input, address2_value)
                        print(f"[✓] Body Corporate {position}: Entered Address Line II: {address2_value}")
                        fields_filled_count += 1
                else:
                        print(f"[INFO] Body Corporate {position}: 'Address Line II' is empty or missing in input data. Skipping.")

                    # --- Country (dropdown) ---
                # country_value = present_address_data.get('country', '').strip()
                # if country_value:
                #         country_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[25]/div/div/div/div[1]/div/div[3]/div/div/div[2]/select"

                #         try:
                #             country_select_element = WebDriverWait(driver, 10).until(
                #                 EC.presence_of_element_located((By.XPATH, country_xpath))
                #             )
                #             country_select = Select(country_select_element)
                #             country_select.select_by_visible_text(country_value)
                #             print(f"[✓] Body Corporate {position}: Selected Country: {country_value}")
                #             fields_filled_count += 1
                #         except Exception as e:
                #             print(f"[✗] Body Corporate {position}: Error selecting Country: {str(e)}")
                #             fields_failed_count += 1
                # else:
                #         print(f"[INFO] Body Corporate {position}: 'Country' is empty or missing in input data. Skipping.")

                    # --- Pin code / Zip Code ---
                try:
                        pincode1_value = body.get('present_address', {}).get('pincode', '').strip()
                        if pincode1_value:
                            pincode1_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[25]/div/div/div/div[1]/div/div[4]/div/div/div[2]/input"

                            try:
                                # Wait for the input field
                                pincode1_input = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, pincode1_xpath))
                                )

                                # Scroll to the input field
                                if callable(globals().get('scroll_into_view')):
                                    scroll_into_view(driver, pincode1_input)
                                else:
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pincode1_input)

                                # Remove readonly if present, clear and set value
                                driver.execute_script("arguments[0].removeAttribute('readonly');", pincode1_input)
                                driver.execute_script("arguments[0].value = '';", pincode1_input)
                                driver.execute_script("arguments[0].value = arguments[1];", pincode1_input, pincode1_value)

                                # Dispatch standard input/change events
                                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", pincode1_input)
                                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", pincode1_input)

                                time.sleep(0.5)
                                send_text(driver, xpath=pincode1_xpath, keys=pincode1_value)

                                print(f"[✓] Body Corporate {position}: Entered Pin code: {pincode1_value}")
                                fields_filled_count += 1
                            except Exception as e:
                                print(f"[✗] Body Corporate {position}: Error setting Pin code (XPath: {pincode1_xpath}): {e}")
                                fields_failed_count += 1
                        else:
                            print(f"[INFO] Body Corporate {position}: 'Pin code / Zip Code' is empty or missing in input data. Skipping.")
                except Exception as e_outer:
                        print(f"[✗] Body Corporate {position}: Unexpected error in Pin code block: {str(e_outer)}")
                        fields_failed_count += 1


                    
                    # --- Area/Locality (dropdown) ---
                time.sleep(1)
                try:
                        area_value = present_address_data.get('area', '').strip()

                        if area_value:
                            area_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[25]/div/div/div/div[1]/div/div[5]/div/div/div[2]/select"

        
                        try:
                            area_input = WebDriverWait(driver, 25).until(
                                EC.presence_of_element_located((By.XPATH, area_xpath))
                            )

                            time.sleep(2)
                            click_element(driver, xpath=area_xpath)
                            time.sleep(2)
                            send_text(driver, xpath=area_xpath, keys=area_value)

                            print(f"[✓] Body Corporate: Entered Area/Locality: {area_value}")
                            # fields_filled_count += 1
                        except Exception as e:
                            print(f"[✗] Body Corporate: Error setting Area/Locality: {e}")
                            # fields_failed_count += 1
                        else:
                            print(f"[INFO] Body Corporate: No Area/Locality provided in data.")
                except Exception as e:
                                print(f"[✗] Body Corporate {position}: Error selecting Area/Locality: {str(e)}")
                                fields_failed_count += 1


                    # --- Jurisdiction of Police Station ---

                    # time.sleep(0.5)
                    # try:
                    #     jurisdiction_value = present_address_data.get('jurisdiction', '').strip()
                    #     if jurisdiction_value:
                    #             jurisdiction_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[25]/div/div/div/div[1]/div/div[10]/div/div/div[2]/input"
                            
                    #             try:
                    #                 jurisdiction_input = WebDriverWait(driver, 10).until(
                    #                     EC.presence_of_element_located((By.XPATH, jurisdiction_xpath))
                    #                 )
                                    
                    #                 # Scroll to view
                    #                 scroll_into_view(driver, jurisdiction_input)
                    #                 time.sleep(0.5)
                                    
                    #                 # Clear and set value
                    #                 jurisdiction_input.clear()
                    #                 jurisdiction_input.send_keys(jurisdiction_value)
                                    
                    #                 print(f"[✓] Body Corporate {position}: Entered Jurisdiction: {jurisdiction_value}")
                    #                 fields_filled_count += 1
                    #             except Exception as e:
                    #                 print(f"[✗] Body Corporate {position}: Error setting Jurisdiction: {str(e)}")
                    #                 fields_failed_count += 1
                    #     else:
                    #         print(f"[INFO] Body Corporate {position}: No Jurisdiction provided in data.")
                    # except Exception as e:
                    #     print(f"[✗] Body Corporate {position}: Exception while processing Jurisdiction: {e}")
                    #     fields_failed_count += 1



                    # --- Phone (with STD/ISD code) ---
                phone_value = body.get('present_address', {}).get('phone', '').strip()
                if phone_value:
                        phone_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[25]/div/div/div/div[1]/div/div[11]/div/div/div[2]/input"
                        
                        try:
                            phone_input = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, phone_xpath))
                            )
                            
                            # Scroll to the input field
                            if callable(globals().get('scroll_into_view')):
                                scroll_into_view(driver, phone_input)
                            else:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_input)

                            # Remove readonly and fill value
                            driver.execute_script("arguments[0].removeAttribute('readonly');", phone_input)
                            driver.execute_script("arguments[0].value = '';", phone_input)
                            driver.execute_script("arguments[0].value = arguments[1];", phone_input, phone_value)
                            
                            # Dispatch events
                            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", phone_input)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", phone_input)

                            time.sleep(0.5)
                            send_text(driver, xpath=phone_xpath, keys=phone_value)

                            print(f"[✓] Body Corporate {position}: Entered Phone: {phone_value}")
                            fields_filled_count += 1
                        except Exception as e:
                            print(f"[✗] Body Corporate {position}: Error entering Phone: {str(e)}")
                            fields_failed_count += 1
                else:
                        print(f"[INFO] Body Corporate {position}: No present address data provided.")

            except Exception as e:
                print(f"[ERROR] Exception in 'Present Address': {e}")
                fields_failed_count += 1

            # --- Year Block ---
            try:
                year_value = body.get('stay_duration', {}).get('years', '').strip()
                if year_value:
                    year_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[25]/div/div/div/div[1]/div/div[13]/div/div/div/div[1]/div/div[2]/div/div/div[2]/select"

                    year_select_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, year_xpath))
                    )
                    if callable(globals().get('scroll_into_view')):
                        scroll_into_view(driver, year_select_element)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", year_select_element)

                    year_select = Select(year_select_element)
                    year_select.select_by_visible_text(year_value)

                    print(f"[✓] Body Corporate {position}: Selected Year: {year_value}")
                    fields_filled_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: 'Year' is empty or missing in input data. Skipping.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Error selecting Year: {str(e)}")
                fields_failed_count += 1


            # --- Month Block ---
            try:
                month_value = body.get('stay_duration', {}).get('months', '').strip()
                if month_value:
                    month_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[25]/div/div/div/div[1]/div/div[13]/div/div/div/div[1]/div/div[3]/div/div/div[2]/select"

                    month_select_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, month_xpath))
                    )
                    if callable(globals().get('scroll_into_view')):
                        scroll_into_view(driver, month_select_element)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", month_select_element)

                    month_select = Select(month_select_element)
                    month_select.select_by_visible_text(month_value)

                    print(f"[✓] Body Corporate {position}: Selected Month: {month_value}")
                    fields_filled_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: 'Month' is empty or missing in input data. Skipping.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Error selecting Month: {str(e)}")
                fields_failed_count += 1


            # --- Identity Proof ---
            try:
                identity_proof_value = body.get('identity_proof', {}).get('type', '').strip()
                if identity_proof_value:
                    identity_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[27]/div/div/div/div[1]/div/div[1]/div/div/div[2]/select"

                    try:
                        identity_select = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, identity_xpath))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", identity_select)
                        Select(identity_select).select_by_visible_text(identity_proof_value)

                        print(f"[✓] Partner {position}: Selected Identity Proof: {identity_proof_value} (i={i})")
                        fields_filled_count += 1

                    except (TimeoutException, NoSuchElementException):
                        print(f"[✗] Partner {position}: Identity Proof dropdown not found at XPath:\n{identity_xpath}")
                        fields_failed_count += 1
                    except Exception as e:
                        print(f"[✗] Partner {position}: Error selecting Identity Proof: {e}")
                        fields_failed_count += 1
                else:
                    print(f"[INFO] Partner {position}: No Identity Proof provided in input data.")
            except Exception as e:
                print(f"[✗] Partner {position}: Unexpected error in Identity Proof block: {e}")
                fields_failed_count += 1


            # --- Residential Proof ---
            try:
                residential_proof_value = body.get('residential_proof', {}).get('type', '').strip()
                if residential_proof_value:
                    residential_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[27]/div/div/div/div[1]/div/div[2]/div/div/div[2]/select"

                    try:
                        # Wait for any loading overlay to disappear
                        WebDriverWait(driver, 15).until(
                            EC.invisibility_of_element_located((By.ID, "loadingPage"))
                        )

                        # Wait for dropdown to appear
                        residential_select = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, residential_xpath))
                        )

                        # Scroll into view
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", residential_select)

                        # Try selecting value
                        try:
                            Select(residential_select).select_by_visible_text(residential_proof_value)
                            print(f"[✓] Partner {position}: Selected Residential Proof: {residential_proof_value} (i={i})")
                            fields_filled_count += 1

                        except ElementClickInterceptedException:
                            print(f"[RETRY] Partner {position}: Element was initially not clickable, retrying...")
                            time.sleep(2)
                            driver.execute_script("arguments[0].click();", residential_select)
                            Select(residential_select).select_by_visible_text(residential_proof_value)
                            print(f"[✓] Partner {position}: Selected Residential Proof after retry: {residential_proof_value} (i={i})")
                            fields_filled_count += 1

                    except (TimeoutException, NoSuchElementException):
                        print(f"[✗] Partner {position}: Residential Proof dropdown not found at XPath:\n{residential_xpath}")
                        fields_failed_count += 1

                    except Exception as e:
                        print(f"[✗] Partner {position}: Error selecting Residential Proof: {e}")
                        fields_failed_count += 1

                else:
                    print(f"[INFO] Partner {position}: No Residential Proof provided in input data.")

            except Exception as e:
                print(f"[✗] Partner {position}: Unexpected error in Residential Proof block: {e}")
                fields_failed_count += 1

            
            # ---Identity Proof No. ---
            try:
                proof_number = body.get('identity_proof', {}).get('number', '').strip()
                if proof_number:
                    proof_number_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[27]/div/div/div/div[1]/div/div[3]/div/div/div[2]/input"
                    
                    proof_number_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, proof_number_xpath))
                    )

                    # Scroll into view
                    if callable(globals().get('scroll_into_view')):
                        scroll_into_view(driver, proof_number_input)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", proof_number_input)

                    # Remove readonly if exists (precaution)
                    driver.execute_script("arguments[0].removeAttribute('readonly');", proof_number_input)

                    # Clear any existing text and send keys
                    proof_number_input.clear()
                    time.sleep(0.2)
                    proof_number_input.send_keys(proof_number)

                    # Dispatch real input and change events
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", proof_number_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", proof_number_input)

                    print(f"[✓] Body Corporate {position}: Entered Proof Number: {proof_number}")
                    fields_filled_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: 'Proof Number' is empty or missing in input data. Skipping.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Error setting Proof Number: {str(e)}")
                fields_failed_count += 1

            # ---Residential Proof No.---
            try:
                proof_number = body.get('residential_proof', {}).get('number', '').strip()
                if proof_number:
                    proof_number_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[27]/div/div/div/div[1]/div/div[4]/div/div/div[2]/input"

                    proof_number_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, proof_number_xpath))
                    )

                    # Scroll into view
                    if callable(globals().get('scroll_into_view')):
                        scroll_into_view(driver, proof_number_input)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", proof_number_input)

                    # Remove readonly if exists (precautionary)
                    driver.execute_script("arguments[0].removeAttribute('readonly');", proof_number_input)

                    # Clear and type into input
                    proof_number_input.clear()
                    time.sleep(0.2)
                    proof_number_input.send_keys(proof_number)

                    # Trigger JS-bound events (input + change)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", proof_number_input)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", proof_number_input)

                    print(f"[✓] Body Corporate {position}: Entered Residential Proof Number: {proof_number}")
                    fields_filled_count += 1
                else:
                    print(f"[INFO] Body Corporate {position}: 'Proof Number' is empty or missing in input data. Skipping.")
            except Exception as e:
                print(f"[✗] Body Corporate {position}: Error setting Residential Proof Number: {str(e)}")
                fields_failed_count += 1


            # --- File Uploads ---
            try: 
                # Copy of resolution
            
                # Identity Proof Upload
                parent_div_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[29]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[1]"

                if body.get('uploads', {}).get('identity_proof_path', ''):
                    file_path = body.get('uploads', {}).get('identity_proof_path', '')
                    success = handle_dynamic_identity_upload(driver, parent_div_xpath, file_path, i)
                    if success:
                        print(f" {i} document uploaded successfully.")
                    else:
                        print(f" {i} document upload failed.")
                
                click_element(
                driver,
                css_selector="#guideContainer-rootPanel-modal_container_131700874-guidebutton___widget"
                )


                # Residential Proof Upload
                parent_div_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[29]/div/div/div/div[1]/div/div[3]/div/div/div[2]/div[1]"

                if body.get('uploads', {}).get('residential_proof_path', ''):
                    file_path = body.get('uploads', {}).get('residential_proof_path', '')
                    success = handle_dynamic_residency_upload(driver, parent_div_xpath, file_path, i)
                    if success:
                        print(f" {i} document uploaded successfully.")
                    else:
                        print(f" {i} document upload failed.")
                
                click_element(
                driver,
                css_selector="#guideContainer-rootPanel-modal_container_131700874-guidebutton___widget"
                )
                
                # Upload files
                parent_div_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[29]/div/div/div/div[1]/div/div[4]/div/div/div[2]/div[1]"

                if body.get('uploads', {}).get('resolution_copy_path', ''):
                    file_path = body.get('uploads', {}).get('resolution_copy_path', '')
                    success = handle_dynamic_resolution_upload(driver, parent_div_xpath, file_path, i)
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

            # Add a small delay between bodies corporate
            time.sleep(1)

        print("[SUCCESS] Completed processing all bodies corporate without DIN/DPIN")

    except Exception as e:
        print(f"[ERROR] Failed to process bodies corporate without DIN/DPIN: {str(e)}")
        raise
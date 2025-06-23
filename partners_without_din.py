import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from function1 import send_text, click_element, scroll_into_view, set_date_field, click_button
import function1
import platform
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pynput.keyboard import Controller, Key
import win32gui, win32con

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
            fallback_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[1]/button"  # Keep your full fallback XPath here
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

        # Short delay to wait for file dialog to open
        time.sleep(2)
        
        # Bring browser window to focus
        try:
            hwnd = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            print("[DEBUG] Browser window focused using Win32")
        except Exception as e:
            print(f"[WARNING] Could not focus browser window: {e}")

        # Type file path using pynput
        keyboard = Controller()
        normalized_path = os.path.normpath(file_path)
        print(f"[DEBUG] Typing normalized path: {normalized_path}")
        for char in normalized_path:
            try:
                keyboard.press(char)
                keyboard.release(char)
                if char in [":", "\\"]:
                    time.sleep(0.15)
                else:
                    time.sleep(0.07)
            except Exception as e:
                print(f"[ERROR] Failed to type character {char}: {e}")

        # Press Enter to submit
        time.sleep(2)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(2)
        
        # Handle success popup
        try:
            ok_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ok-button, #okSuccessModalBtn"))
            )
            driver.execute_script("arguments[0].click();", ok_button)
            print("[AGILE PRO] Clicked OK on success dialog")
            time.sleep(0.3)
        except TimeoutException:
            print("[INFO] No success dialog found, assuming upload completed")
        except Exception as e:
            print(f"[WARNING] Failed to interact with success dialog: {e}")

        # Check uploaded file list
        try:
            file_list = parent_div.find_element(By.CSS_SELECTOR, "ul.guide-fu-fileItemList")
            if file_list.find_elements(By.TAG_NAME, "li"):
                print("[AGILE PRO] File upload verified in list")
                return True
            else:
                print("[WARNING] File upload may have failed: no file found in list")
                return False
        except Exception as e:
            print(f"[INFO] No file list found for verification: {e}")
            return True  # Optimistically assume success

    except Exception as e:
        print(f"[ERROR] File upload failed for {parent_div}: {e}")
        return False




def handle_dynamic_residency_upload(driver, parent_div, file_path, i, timeout=5):
    """
    Handles file uploads dynamically for partner/nominee identity proofs using index-based dynamic parent div ID
    and static input XPath for fallback.
    """
    print(f"[DEBUG] Uploading file for index={i}")

    try:
        # Re-fetch parent_div in case DOM has refreshed
        parent_div = WebDriverWait(driver, timeout + 5).until(
            EC.presence_of_element_located((By.XPATH, parent_div))
        )
        print(f"[DEBUG] Fresh parent_div resolved: {parent_div.get_attribute('id')}")

        # Try to get the attach button reliably
        try:
            attach_button = WebDriverWait(parent_div, timeout + 5).until(
                lambda d: d.find_element(By.XPATH, ".//button[contains(@class, 'guide-fu-attach-button')]")
            )
        except Exception as e:
            print(f"[WARNING] Attach button not found via parent_div: {e}")
            fallback_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[3]/div/div/div[2]/div[1]/button"
            attach_button = WebDriverWait(driver, timeout + 5).until(
                EC.element_to_be_clickable((By.XPATH, fallback_xpath))
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

        # Short delay to wait for file dialog to open
        time.sleep(2)
        
        # Bring browser window to focus
        try:
            hwnd = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            print("[DEBUG] Browser window focused using Win32")
        except Exception as e:
            print(f"[WARNING] Could not focus browser window: {e}")

        # Type file path using pynput
        keyboard = Controller()
        normalized_path = os.path.normpath(file_path)
        print(f"[DEBUG] Typing normalized path: {normalized_path}")
        for char in normalized_path:
            try:
                keyboard.press(char)
                keyboard.release(char)
                if char in [":", "\\"]:
                    time.sleep(0.15)
                else:
                    time.sleep(0.07)
            except Exception as e:
                print(f"[ERROR] Failed to type character {char}: {e}")

        # Press Enter to submit
        time.sleep(2)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(2)
        
        # Handle success popup
        try:
            ok_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ok-button, #okSuccessModalBtn"))
            )
            driver.execute_script("arguments[0].click();", ok_button)
            print("[AGILE PRO] Clicked OK on success dialog")
            time.sleep(0.3)
        except TimeoutException:
            print("[INFO] No success dialog found, assuming upload completed")
        except Exception as e:
            print(f"[WARNING] Failed to interact with success dialog: {e}")

        # Check uploaded file list
        try:
            file_list = parent_div.find_element(By.CSS_SELECTOR, "ul.guide-fu-fileItemList")
            if file_list.find_elements(By.TAG_NAME, "li"):
                print("[AGILE PRO] File upload verified in list")
                return True
            else:
                print("[WARNING] File upload may have failed: no file found in list")
                return False
        except Exception as e:
            print(f"[INFO] No file list found for verification: {e}")
            return True  # Optimistically assume success

    except Exception as e:
        print(f"[ERROR] File upload failed for {parent_div}: {e}")
        return False



def handle_partners_without_din(driver, config_data):
    """
    Handle the section for partners without DIN/DPIN in the MCA LLP form.
    
    Args:
        driver: Selenium WebDriver instance
        config_data: Dictionary containing form data
        config_selectors: Dictionary containing CSS selectors
    """
    time.sleep(2)
    try:
        # Get the number of partners without DIN from config
        num_partners = int(config_data['form_data']['fields'].get('Individuals Not having valid DIN/DPIN', 0))
        if num_partners == 0:
            print("[INFO] No partners without DIN/DPIN to process")
            return

        # Validate maximum limit of 8 partners
        if num_partners > 8:
            print("[WARNING] Maximum limit is 8 partners. Truncating to 8.")
            num_partners = 8

        print(f"[INFO] Processing {num_partners} partners without DIN/DPIN")
        
        # Get partners data from config
        partners_data = config_data.get('form_data', {}).get('partners_without_din', [])
        if not partners_data:
            print("[WARNING] No partner data found in config")
            print(f"[DEBUG] Available keys in config_data: {list(config_data.keys())}")
            if 'form_data' in config_data:
                print(f"[DEBUG] Available keys in form_data: {list(config_data['form_data'].keys())}")
            return

        print(f"[DEBUG] Found {len(partners_data)} partners in config data")
        if partners_data:
            print(f"[DEBUG] First partner data keys: {list(partners_data[0].keys())}")
            print(f"[DEBUG] Sample partner data: {partners_data[0]}")

        # Get number of partners having valid DIN/DPIN
        num_partners_str = config_data.get('form_data', {}).get('fields', {}).get('Individuals Having valid DIN/DPIN', '').strip()

        try:
            num_din_partners = int(num_partners_str) if num_partners_str else 0
        except ValueError:
            print(f"[WARN] Invalid DIN/DPIN value: '{num_partners_str}', defaulting to 0")
            num_din_partners = 0

        # If valid number found, calculate dynamic starting index
        if num_din_partners > 0:
            dynamic_num_starting_index = 2
            i = dynamic_num_starting_index + num_din_partners
            print(f"[INFO] Detected {num_din_partners} DIN/DPIN partners. Using dynamic form index: i={i}")
        else:
            # Fallback only if field is truly missing or invalid
            i = int(config_data.get('dynamic_form_index', {}).get('individuals_not_having_valid_din_dpin', 3))
            print(f"[INFO] No valid DIN/DPIN partners found. Using fallback dynamic form index: i={i}")
        



        # Process each partner sequentially
        for idx in range(num_partners):
            position = idx + 1  # XPath is 1-based
            if idx < len(partners_data):
                partner = partners_data[idx]
            else:
                print(f"[WARNING] No data found for partner {position}")
                continue

            print(f"\n[INFO] Filling details for partner {position} without DIN/DPIN")
            fields_filled_count = 0
            fields_failed_count = 0
            i += 1  #

            try:
                # Wait for the subform to be visible
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements(By.XPATH, f"(//input[@aria-label='First Name'])[{position}]")) > 0
                )

                # Personal Details Section
                # First Name
                first_name_xpath = f"(//input[@aria-label='First Name'])[{position}]"
                driver.find_element(By.XPATH, first_name_xpath).send_keys(partner.get('First Name', ''))

                # Middle Name
                middle_name_xpath = f"(//input[@aria-label='Middle Name'])[{position}]"
                try:
                    driver.find_element(By.XPATH, middle_name_xpath).send_keys(partner.get('Middle Name', ''))
                except NoSuchElementException:
                    pass

                # Surname
                surname_xpath = f"(//input[@aria-label='Surname'])[{position}]"
                driver.find_element(By.XPATH, surname_xpath).send_keys(partner.get('Surname', ''))

                # Father's Name Details
                father_first_name_xpath = f"(//input[@aria-label=\"Father's First Name\"])[{position}]"
                driver.find_element(By.XPATH, father_first_name_xpath).send_keys(partner.get("Father's First Name", ''))

                father_middle_name_xpath = f"(//input[@aria-label=\"Father's Middle Name\"])[{position}]"
                try:
                    driver.find_element(By.XPATH, father_middle_name_xpath).send_keys(partner.get("Father's Middle Name", ''))
                except NoSuchElementException:
                    pass

                father_surname_xpath = f"(//input[@aria-label=\"Father's Surname\"])[{position}]"
                driver.find_element(By.XPATH, father_surname_xpath).send_keys(partner.get("Father's Surname", ''))
            except Exception as e:
                print(f"[ERROR] Failed to fill basic details for partner {position}: {str(e)}")
                fields_failed_count += 1
                continue

            # Gender
            time.sleep(0.5)
            gender = partner.get('Gender', '').capitalize()
            if gender in ['Male', 'Female', 'Transgender']:
                gender_xpath = f"(//select[@aria-label='Gender'])[{position}]"
                gender_dropdown = driver.find_element(By.XPATH, gender_xpath)

                # Use Select to choose the gender option
                select = Select(gender_dropdown)
                select.select_by_visible_text(gender)
                print(f"[✓] Selected gender: {gender}")
            else:
                print(f"[!] Gender '{gender}' not valid or missing.")



            # Date of Birth - Using robust approach
            time.sleep(3)
            try:
                # Try multiple strategies to find the date input field
                dob_input = None
                try:
                    # Strategy 1: Exact aria-label match
                    dob_input = driver.find_element(By.XPATH, f"(//input[@aria-label='Date of Birth   Please Enter date in DD/MM/YYYY format only'])[{position}]")
                except:
                    try:
                        # Strategy 2: Partial aria-label match
                        dob_input = driver.find_element(By.XPATH, f"(//input[contains(@aria-label, 'Date of Birth')])[{position}]")
                    except:
                        time.sleep(1)
                        try:
                            # Strategy 3: Find by label text
                            label = driver.find_element(By.XPATH, f"(//label[contains(text(), 'Date of Birth')])[{position}]")
                            dob_input = label.find_element(By.XPATH, './following::input[1]')
                        except:
                            try:
                                # Strategy 4: Find by class and type
                                dob_input = driver.find_element(By.XPATH, f"(//input[@type='text' and contains(@class, 'guidedatepicker')])[{position}]")
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
                        
                        # ✅ Call set_date_field directly
                        if set_date_field(driver, dob_id, dob):
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
            

            # Nationality
            time.sleep(1.5)
            try:
                        nationality = partner.get('Nationality', '').strip()  # Get the nationality value

                        if nationality:
                            # Construct XPath to target the Nationality dropdown
                            nationality_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[10]/div/div/div[2]/select"

                            # Wait for the dropdown to be present
                            nationality_dropdown = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, nationality_xpath))
                            )

                            # Use Select class to choose the nationality
                            select = Select(nationality_dropdown)
                            select.select_by_visible_text(nationality)

                            print(f"[✓] Partner {position}: Nationality '{nationality}' selected using dynamic 'i' (i={i}).")
                            fields_filled_count += 1
                        else:
                            print(f"[!] Partner {position}: Nationality value not provided.")

            except Exception as e:
                        print(f"[✗] Failed to select nationality using dynamic 'i' (i={i}): {e}")
                        fields_failed_count += 1

            
            # --- Whether resident of India using dynamic 'i' and clicking radio (dynamic IDs handled) ---
            time.sleep(1.5)
            try:
                is_resident_data = partner.get('Whether resident of India', {})
                is_resident = is_resident_data.get('Yes', 'false').lower() == 'true'

                radio_container_xpath_resident = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[11]/div/div/div[2]"
                
                radio_container_resident = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, radio_container_xpath_resident))
                )

                if is_resident:
                    try:
                        yes_radio = radio_container_resident.find_element(By.XPATH, ".//input[@type='radio' and @aria-label='Yes']")
                        driver.execute_script("arguments[0].click();", yes_radio)
                        print(f"[✓] Partner {position}: Clicked 'Yes' for Whether resident of India (i={i}).")
                        fields_filled_count += 1
                    except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find 'Yes' radio button.")
                    except Exception as e:
                        print(f"[✗] Partner {position}: Error clicking 'Yes' for Whether resident of India (i={i}): {e}")
                else:
                    try:
                        no_radio = radio_container_resident.find_element(By.XPATH, ".//input[@type='radio' and @aria-label='No']")
                        driver.execute_script("arguments[0].click();", no_radio)
                        print(f"[✓] Partner {position}: Clicked 'No' for Whether resident of India (i={i}).")
                        fields_filled_count += 1
                    except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find 'No' radio button.")
                    except Exception as e:
                        print(f"[✗] Partner {position}: Error clicking 'No' for Whether resident of India (i={i}): {e}")

            except TimeoutException:
                print(f"[✗] Partner {position}: Timeout finding 'Whether resident of India' container.")
            except NoSuchElementException:
                print(f"[✗] Partner {position}: Could not find 'Whether resident of India' label/container.")
            except Exception as e:
                print(f"[FAIL] Partner {position}: Error handling 'Whether resident of India' (i={i}): {e}")
                fields_failed_count += 1


            # --- Income-tax PAN/Passport number type ---
            time.sleep(1.5)
            try:
                        id_type_data = partner.get('Income-tax PAN/Passport number', {})
                        radio_container_xpath_id = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[12]/div/div/div[2]"
                        radio_container_id = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, radio_container_xpath_id))
                        )

                        if isinstance(id_type_data, dict):
                            if id_type_data.get('PAN') == 'true':
                                try:
                                    pan_radio = radio_container_id.find_element(By.XPATH, ".//input[@type='radio' and @aria-label='PAN']")
                                    driver.execute_script("arguments[0].click();", pan_radio)
                                    print(f"[✓] Partner {position}: Selected PAN radio button (i={i}).")
                                    fields_filled_count += 1
                                except NoSuchElementException:
                                    print(f"[✗] Partner {position}: Could not find PAN radio button.")
                                except Exception as e:
                                    print(f"[✗] Partner {position}: Error clicking PAN radio button (i={i}): {e}")
                            elif id_type_data.get('Passport number') == 'true':
                                try:
                                    passport_radio = radio_container_id.find_element(By.XPATH, ".//input[@type='radio' and @aria-label='Passport number']")
                                    driver.execute_script("arguments[0].click();", passport_radio)
                                    print(f"[✓] Partner {position}: Selected Passport Number radio button (i={i}).")
                                    fields_filled_count += 1
                                except NoSuchElementException:
                                    print(f"[✗] Partner {position}: Could not find Passport Number radio button.")
                                except Exception as e:
                                    print(f"[✗] Partner {position}: Error clicking Passport Number radio button (i={i}): {e}")
                            else:
                                print(f"[!] Partner {position}: No valid ID type specified in data.")
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding PAN/Passport radio button container.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find PAN/Passport radio button container.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Failed to select PAN/Passport radio button (i={i}): {e}")
                        fields_failed_count += 1



            # --- Income-tax PAN/Passport number details ---
            time.sleep(1.5)
            try:
                        pan_passport_details = partner.get('Income-tax PAN/Passport number details', '').strip()
                        if pan_passport_details:
                            details_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[14]/div/div/div/div[1]/div/div[1]/div/div/div[2]"
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



                    # --- Verify PAN Button ---
            time.sleep(1.5)
            try:
                        verify_pan_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[14]/div/div/div/div[1]/div/div[3]/div/div/div[1]"
                        verify_pan_xpath = f"{verify_pan_xpath_base}/button[@aria-label='Verify PAN']"

                        click_button(driver, verify_pan_xpath, selector_type='xpath')
                        print(f"[SUCCESS] Partner {position}: Clicked Verify PAN button (i={i}).")
                        fields_filled_count += 1
            except Exception as e:
                        print(f"[✗] Partner {position}: Failed to click Verify PAN button: {e}")
                        fields_failed_count += 1



            # --- Place of Birth (State) ---
            time.sleep(1.5)
            try:
                        birth_state = partner.get('Place of Birth (State)', '').strip()
                        if birth_state:
                            dropdown_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[15]/div/div/div[2]/select"  # your full XPath here

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
            time.sleep(1.5)
            try:
                        district_value = partner.get('Place of Birth (District)', '').strip()
                        if district_value:
                            dropdown_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[16]/div/div/div[2]/select"

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
            time.sleep(1.5)
            try:
                            citizen_data = partner.get('Whether citizen of India', {})
                            label = next((k for k, v in citizen_data.items() if v.lower() == 'true'), None) if isinstance(citizen_data, dict) else None

                            if label:
                                radio_container_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[17]/div/div/div[2]"
                                radio_xpath = f"{radio_container_xpath_base}//input[@type='radio' and @aria-label='{label}']"

                                for attempt in range(3):
                                    try:
                                        # Wait for the radio input to be clickable
                                        radio_input = WebDriverWait(driver, 5).until(
                                            EC.element_to_be_clickable((By.XPATH, radio_xpath))
                                        )

                                        # Ensure it is interactable
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

                                        # Confirm if selected
                                        if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                                            print(f"[✓] Partner {position}: Selected: Whether citizen of India = {label} (i={i}).")
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
                                print("[INFO] No valid option marked as True for 'Whether citizen of India'")
            except TimeoutException:
                            print(f"[✗] Partner {position}: Timeout finding 'Whether citizen of India' container.")
            except NoSuchElementException:
                            print(f"[✗] Partner {position}: Could not find 'Whether citizen of India' label/container.")
            except Exception as e:
                            print(f"[ERROR] Exception in 'Whether citizen of India': {e}")
                            fields_failed_count += 1





            # --- Occupation type ---
            time.sleep(1.5)
            try:
                            occupation_type = partner.get('Occupation type', '').strip()
                            if occupation_type:
                                dropdown_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[18]/div/div/div[2]"
                                occupation_xpath = f"{dropdown_xpath_base}//select[@aria-label='Occupation type']"

                                occupation_dropdown = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, occupation_xpath))
                                )
                                select = Select(occupation_dropdown)
                                select.select_by_visible_text(occupation_type)
                                print(f"[✓] Partner {position}: Selected Occupation type '{occupation_type}' (i={i}).")
                                fields_filled_count += 1

                                # If 'Others' selected for occupation, fill description
                                if occupation_type.lower() == 'others':
                                    others_description = partner.get('Description of others', '').strip()
                                    if others_description:
                                        others_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[19]/div/div/div[2]"
                                        others_xpath = f"{others_xpath_base}//input[@aria-label='Description of others']"
                                        others_input = WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable((By.XPATH, others_xpath))
                                        )
                                        others_input.send_keys(others_description)
                                        print(f"[✓] Partner {position}: Filled 'Description of others': '{others_description}' (i={i}).")
                                        fields_filled_count += 1
                                    else:
                                        print(f"[INFO] Partner {position}: 'Description of others' not provided.")

                            else:
                                print(f"[INFO] Partner {position}: Occupation type not provided.")
            except TimeoutException:
                            print(f"[✗] Partner {position}: Timeout finding Occupation type dropdown.")
            except NoSuchElementException:
                            print(f"[✗] Partner {position}: Could not find Occupation type dropdown or 'Description of others' input.")
            except Exception as e:
                            print(f"[✗] Partner {position}: Error selecting Occupation type (i={i}): {e}")
                            fields_filled_count += 1





                    # --- Area of Occupation ---
            time.sleep(1.5)
            try:
                            area_of_occupation = partner.get("Area of Occupation", "").strip()
                            if area_of_occupation:
                                dropdown_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[20]/div/div/div[2]"
                                area_xpath = f"{dropdown_xpath_base}//select[@aria-label='Area of Occupation']"

                                area_select_elem = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, area_xpath))
                                )
                                select = Select(area_select_elem)
                                select.select_by_visible_text(area_of_occupation)
                                print(f"[✓] Partner {position}: Selected Area of Occupation: {area_of_occupation} (i={i}).")
                                fields_filled_count += 1

                                # If 'Others' selected for Area of Occupation, fill description
                                if area_of_occupation.lower() == "others":
                                    others_description = partner.get("If Others selected, please specify", "").strip()
                                    if others_description:
                                        others_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[21]/div/div/div[2]"
                                        others_input_xpath = f"{others_xpath_base}//input[@aria-label='If \'Others\' selected, please specify']"
                                        others_input = WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable((By.XPATH, others_input_xpath))
                                        )
                                        others_input.send_keys(others_description)
                                        print(f"[✓] Partner {position}: Filled 'If Others' selected, please specify: '{others_description}' (i={i}).")
                                        fields_filled_count += 1
                                    else:
                                        print(f"[INFO] Partner {position}: No value to specify for 'Others' in Area of Occupation.")

                            else:
                                print(f"[INFO] Partner {position}: No value provided for Area of Occupation.")
            except TimeoutException:
                            print(f"[✗] Partner {position}: Timeout finding Area of Occupation dropdown.")
            except NoSuchElementException:
                            print(f"[✗] Partner {position}: Could not find Area of Occupation dropdown or 'If Others' specify input.")
            except Exception as e:
                            print(f"[✗] Partner {position}: Error filling Area of Occupation: {e}")
                            fields_filled_count += 1



                    # --- Educational qualification ---
            time.sleep(1.5)
            try:
                            educational_qualification = partner.get('Educational qualification', '').strip()
                            if educational_qualification:
                                dropdown_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[22]/div/div/div[2]"
                                education_xpath = f"{dropdown_xpath_base}//select[@aria-label='Educational qualification']"

                                education_dropdown = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, education_xpath))
                                )
                                select = Select(education_dropdown)
                                select.select_by_visible_text(educational_qualification)
                                print(f"[✓] Partner {position}: Selected Educational qualification: '{educational_qualification}' (i={i}).")
                                fields_filled_count += 1

                                # If 'Others' selected for education, fill description
                                if educational_qualification.lower() == 'others':
                                    education_others = partner.get('Educational qualification others', '').strip()
                                    if education_others:
                                        others_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[23]/div/div/div[2]"
                                        others_input_xpath = f"{others_xpath_base}//input[@aria-label='If \'Others\' selected, please specify']"
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
            except NoSuchElementException:
                            print(f"[✗] Partner {position}: Could not find Educational qualification dropdown or 'If Others' specify input.")
            except Exception as e:
                            print(f"[✗] Partner {position}: Error selecting Educational qualification (i={i}): {e}")
                            fields_filled_count += 1



                    # Contact Details
            time.sleep(1.5)
            try:
                            mobile_value = partner.get('Mobile No.', '').strip()
                            if mobile_value:
                                mobile_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[24]/div/div/div[2]"
                                mobile_xpath = f"{mobile_xpath_base}//input[@aria-label='Mobile No.']"
                                mobile_input = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, mobile_xpath))
                                )
                                mobile_input.clear()
                                mobile_input.send_keys(mobile_value)
                                print(f"[SUCCESS] Partner {position}: Entered Mobile No.: {mobile_value} (i={i}).")
                                fields_filled_count += 1
                            else:
                                print(f"[INFO] Partner {position}: No Mobile No. provided in data.")
            except TimeoutException:
                            print(f"[✗] Partner {position}: Timeout finding Mobile No. input.")
            except NoSuchElementException:
                            print(f"[✗] Partner {position}: Could not find Mobile No. input.")
            except Exception as e:
                            print(f"[✗] Partner {position}: Failed to enter Mobile No.: {e}")
                            fields_failed_count += 1



                        # --- Email ID ---
            time.sleep(1.5)
            try:
                            email_value = partner.get('Email ID', '').strip()
                            if email_value:
                                email_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[25]/div/div/div[2]"
                                email_xpath = f"{email_xpath_base}//input[@aria-label='Email ID']"
                                email_input = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, email_xpath))
                                )
                                email_input.clear()
                                email_input.send_keys(email_value)
                                print(f"[SUCCESS] Partner {position}: Entered Email ID: {email_value} (i={i}).")
                                fields_filled_count += 1
                            else:
                                print(f"[INFO] Partner {position}: No Email ID provided in data.")
            except TimeoutException:
                            print(f"[✗] Partner {position}: Timeout finding Email ID input.")
            except NoSuchElementException:
                            print(f"[✗] Partner {position}: Could not find Email ID input.")
            except Exception as e:
                            print(f"[✗] Partner {position}: Failed to enter Email ID: {e}")
                            fields_failed_count += 1


            # --- Permanent Address - Address Line I ---
            time.sleep(1.5)
            try:
                            perm_address1 = partner.get('Permanent Address Line I', '').strip()
                            if perm_address1:
                                address1_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[1]/div/div/div[2]"
                                address1_xpath = f"{address1_xpath_base}//input[@aria-label='Address Line I']"
                                address1_input = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, address1_xpath))
                                )
                                address1_input.clear()
                                address1_input.send_keys(perm_address1)
                                print(f"[✓] Partner {position}: Entered Permanent Address Line I: {perm_address1} (i={i}).")
                                fields_filled_count += 1
                            else:
                                print(f"[INFO] Partner {position}: No Permanent Address Line I provided in data.")
            except TimeoutException:
                            print(f"[✗] Partner {position}: Timeout finding Permanent Address Line I input.")
            except NoSuchElementException:
                            print(f"[✗] Partner {position}: Could not find Permanent Address Line I input.")
            except Exception as e:
                            print(f"[✗] Partner {position}: Failed to enter Permanent Address Line I: {e}")
                            fields_failed_count += 1


                    # --- Permanent Address - Address Line II ---
            time.sleep(0.5)
            try:
                            perm_address2 = partner.get('Permanent Address Line II', '').strip()
                            if perm_address2:
                                address2_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[2]/div/div/div[2]"
                                address2_xpath = f"{address2_xpath_base}//input[@aria-label='Address Line II']"
                                address2_input = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, address2_xpath))
                                )
                                address2_input.clear()
                                address2_input.send_keys(perm_address2)
                                print(f"[✓] Partner {position}: Entered Permanent Address Line II: {perm_address2} (i={i}).")
                                fields_filled_count += 1
                            else:
                                print(f"[INFO] Partner {position}: No Permanent Address Line II provided in data.")
            except TimeoutException:
                            print(f"[✗] Partner {position}: Timeout finding Permanent Address Line II input.")
            except NoSuchElementException:
                            print(f"[✗] Partner {position}: Could not find Permanent Address Line II input.")
            except Exception as e:
                            print(f"[✗] Partner {position}: Failed to enter Permanent Address Line II: {e}")
                            fields_failed_count += 1



            # --- Permanent Country ---
            time.sleep(0.5)
            try:
                        perm_country = partner.get('Permanent Country', '').strip()
                        if perm_country:
                            country_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[3]/div/div/div[2]/select"

                            country_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, country_xpath))
                            )

                            select = Select(country_element)
                            select.select_by_visible_text(perm_country)

                            print(f"[✓] Partner {position}: Selected Permanent Country: {perm_country} (i={i}).")
                            fields_filled_count += 1
                        else:
                            print(f"[INFO] Partner {position}: No Permanent Country provided in data.")
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Permanent Country dropdown.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Permanent Country dropdown.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Error selecting Permanent Country: {e}")
                        fields_failed_count += 1


            # --- Permanent Pin code ---
            time.sleep(0.5)        
            try:
                            perm_pin = partner.get('Permanent Pin code', '').strip()
                            if perm_pin:
                                pin_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[4]/div/div/div[2]"
                                perm_pin_xpath = f"{pin_xpath_base}//input[@aria-label='Pin code / Zip Code']"
                                perm_pin_input = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, perm_pin_xpath))
                                )
                                perm_pin_input.clear()
                                perm_pin_input.send_keys(perm_pin)
                                print(f"[✓] Partner {position}: Entered Permanent Pin code: {perm_pin} (i={i}).")
                                fields_filled_count += 1
                            else:
                                print(f"[INFO] Partner {position}: No Permanent Pin code provided in data.")
            except TimeoutException:
                            print(f"[✗] Partner {position}: Timeout finding Permanent Pin code input.")
            except NoSuchElementException:
                            print(f"[✗] Partner {position}: Could not find Permanent Pin code input.")
            except Exception as e:
                                print(f"[✗] Partner {position}: Failed to enter Permanent Pin code: {e}")
                                fields_failed_count += 1


            # --- Area/ Locality ---
            time.sleep(0.5)
            try:
                            area_locality = partner.get('Permanent Area/Locality', '').strip()
                            if area_locality:
                                dropdown_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[5]/div/div/div[2]"
                                area_xpath = f"{dropdown_xpath_base}//select[@aria-label='Area/ Locality']"

                                area_select_elem = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, area_xpath))
                                )
                                # Click to open the dropdown (if necessary)
                                area_select_elem.click()
                                time.sleep(0.5)

                                # Send keys to filter and select (behavior depends on the dropdown)
                                area_select_elem.send_keys(area_locality)
                                time.sleep(0.5)

                                # Press Enter to select (if necessary)
                                area_select_elem.send_keys(Keys.ENTER)

                                print(f"[✓] Partner {position}: Selected Area/Locality: {area_locality} (i={i}).")
                                fields_filled_count += 1

                                if area_locality.lower() == "others":
                                        others_input_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[5]/div/div/div/div[1]/div/div[9]/div/div/div[2]"
                                        others_input_xpath = f"{others_input_xpath_base}//input[@aria-label='If \\'Others\\' selected, please specify']"
                                        others_input = WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable((By.XPATH, others_input_xpath))
                                        )
                                        others_description = partner.get("If Others selected, please specify", "").strip()
                                        if others_description:
                                            others_input.send_keys(others_description)
                                            print(f"[✓] Partner {position}: Filled 'If Others' selected for Area/Locality: '{others_description}' (i={i}).")
                                            fields_filled_count += 1
                                        else:
                                            print(f"[INFO] Partner {position}: No value to specify for 'Others' in Area/Locality.")

                            else:
                                    print(f"[INFO] Partner {position}: No value provided for Area/Locality.")
            except TimeoutException:
                                print(f"[✗] Partner {position}: Timeout finding Area/Locality dropdown.")
            except NoSuchElementException:
                                print(f"[✗] Partner {position}: Could not find Area/Locality dropdown or 'If Others' specify input.")
            except Exception as e:
                                print(f"[✗] Partner {position}: Error filling Area/Locality: {e}")
                                fields_filled_count += 1



            # --- Permanent Police Station ---
            time.sleep(0.5)
            try:
                                perm_police = partner.get('Permanent Police Station', '').strip()
                                if perm_police:
                                    police_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[10]/div/div/div[2]"
                                    perm_police_xpath = f"{police_xpath_base}//input[@aria-label='Jurisdiction of Police Station']"
                                    perm_police_input = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, perm_police_xpath))
                                    )
                                    perm_police_input.clear()
                                    perm_police_input.send_keys(perm_police)
                                    print(f"[✓] Partner {position}: Entered Permanent Police Station: {perm_police} (i={i}).")
                                    fields_filled_count += 1
                                else:
                                    print(f"[INFO] Partner {position}: No Permanent Police Station provided in data.")
            except TimeoutException:
                                print(f"[✗] Partner {position}: Timeout finding Permanent Police Station input.")
            except NoSuchElementException:
                                print(f"[✗] Partner {position}: Could not find Permanent Police Station input.")
            except Exception as e:
                                print(f"[✗] Partner {position}: Failed to enter Permanent Police Station: {e}")
                                fields_failed_count += 1


                            # --- Permanent Phone ---
            time.sleep(0.5)
            try:
                                phone_value = partner.get('Permanent Phone', '').strip()

                                if phone_value:
                                    phone_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[11]/div/div/div[2]"
                                    perm_phone_xpath = f"{phone_xpath_base}//input[@aria-label='Phone (with STD/ISD code)']"

                                    phone_input = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.XPATH, perm_phone_xpath))
                                    )

                                    phone_input.clear()
                                    phone_input.send_keys(phone_value)

                                    print(f"[SUCCESS] Partner {position}: Filled Phone (STD/ISD): {phone_value} (i={i}).")
                                    fields_filled_count += 1
                                else:
                                    print("[INFO] No value provided for 'Permanent Phone'")
            except TimeoutException:
                                print(f"[✗] Partner {position}: Timeout finding Permanent Phone input.")
            except NoSuchElementException:
                                print(f"[✗] Partner {position}: Could not find Permanent Phone input.")
            except Exception as e:
                                print(f"[ERROR] Could not fill Phone (STD/ISD) field: {e}")
                                fields_failed_count += 1


            # --- Whether present residential address same as permanent ---
            time.sleep(0.5)
            try:
                                same_address_data = partner.get('Whether present residential address same as permanent', {})
                                label = next((k for k, v in same_address_data.items() if v.lower() == 'true'), None) if isinstance(same_address_data, dict) else None

                                if label:
                                    radio_container_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[12]/div/div/div[2]"
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
                                            driver.execute_script("arguments[0].click();", yes_radio)
                                            print(f"[✓] Partner {position}: Selected 'Yes' for Whether present address same as permanent (i={i}).")
                                            fields_filled_count += 1
                                        except Exception as e:
                                            print(f"[✗] Partner {position}: Error clicking 'Yes' for Whether present address same as permanent (i={i}): {e}")
                                    elif label.lower() == 'no':
                                        try:
                                            no_radio = WebDriverWait(driver, 5).until(
                                                EC.element_to_be_clickable((By.XPATH, no_radio_xpath))
                                            )
                                            driver.execute_script("arguments[0].click();", no_radio)
                                            print(f"[✓] Partner {position}: Selected 'No' for Whether present address same as permanent (i={i}).")
                                            # fields_filled_count += 1 # Increment will happen in the subsequent address fields
                                        except Exception as e:
                                            print(f"[✗] Partner {position}: Error clicking 'No' for Whether present address same as permanent (i={i}): {e}")
                                    else:
                                        print(f"[INFO] Partner {position}: Invalid value for 'Whether present address same as permanent': {label}")
                                else:
                                    print(f"[INFO] Partner {position}: 'Whether present address same as permanent' not found in data.")
            except TimeoutException:
                                print(f"[✗] Partner {position}: Timeout finding 'Whether present address same as permanent' container.")
            except NoSuchElementException:
                                print(f"[✗] Partner {position}: Could not find 'Whether present address same as permanent' label/container.")
            except Exception as e:
                                print(f"[ERROR] Exception in 'Whether present address same as permanent': {e}")
                                fields_failed_count += 1
                                
                    # --- Present Address ---
                     
            try:                        
                        # --- Address Line I ---
                        address1_value = partner.get('Present Address Line I', '')
                        if address1_value:
                                address1_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[11]/div/div/div/div[1]/div/div[1]/div/div/div[2]/input"
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
                                

                            # --- Address Line II ---
                        address2_value = partner.get('Present Address Line II', '')
                        if address2_value:
                                address2_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[11]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"

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


                            # --- Country (dropdown) ---
                        country_value = partner.get('Present Country', '')
                        if country_value:
                                country_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[11]/div/div/div/div[1]/div/div[3]/div/div/div[2]/select"

                                try:
                                    country_select_element = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, country_xpath))
                                    )
                                    country_select = Select(country_select_element)
                                    country_select.select_by_visible_text(country_value)
                                    print(f"[✓] Body Corporate {position}: Selected Country: {country_value}")
                                    fields_filled_count += 1
                                except Exception as e:
                                    print(f"[✗] Body Corporate {position}: Error selecting Country: {str(e)}")
                                    fields_failed_count += 1
                        else:
                                print(f"[INFO] Body Corporate {position}: 'Country' is empty or missing in input data. Skipping.")


                            # --- Pin code / Zip Code ---
                        try:
                                pincode1_value = partner.get('Present Pin code', '')
                                if pincode1_value:
                                    pincode1_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[11]/div/div/div/div[1]/div/div[4]/div/div/div[2]/input"

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


                        time.sleep(0.8)


                        # --- Area/Locality (dropdown) ---
                        time.sleep(1)
                        try:
                                area_value = partner.get('Present Area/Locality', '')

                                if area_value:
                                    area_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[11]/div/div/div/div[1]/div/div[5]/div/div/div[2]/select"

                
                                try:
                                    area_input = WebDriverWait(driver, 30).until(
                                        EC.presence_of_element_located((By.XPATH, area_xpath))
                                    )

                                    time.sleep(2)
                                    click_element(driver, xpath=area_xpath)
                                    time.sleep(2)
                                    function1.send_text(driver, xpath=area_xpath, keys=area_value)

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

                        time.sleep(0.5)
                        try:
                                jurisdiction_value = partner.get('Present Jurisdiction', '')
                                if jurisdiction_value:
                                        jurisdiction_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[11]/div/div/div/div[1]/div/div[10]/div/div/div[2]/input"
                                    
                                        try:
                                            jurisdiction_input = WebDriverWait(driver, 10).until(
                                                EC.presence_of_element_located((By.XPATH, jurisdiction_xpath))
                                            )
                                            
                                            # Scroll to view
                                            scroll_into_view(driver, jurisdiction_input)
                                            time.sleep(0.5)
                                            
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



                            # --- Phone (with STD/ISD code) ---
                        phone_value = partner.get('Present Phone', '')
                        if phone_value:
                                phone_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[11]/div/div/div/div[1]/div/div[11]/div/div/div[2]/input"
                                
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
                        year_value = partner.get('Duration Years', '')
                        if year_value:
                            year_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[11]/div/div/div/div[1]/div/div[13]/div/div/div/div[1]/div/div[2]/div/div/div[2]/select"

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
                        month_value = partner.get('Duration Months', '')
                        if month_value:
                            month_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[11]/div/div/div/div[1]/div/div[13]/div/div/div/div[1]/div/div[3]/div/div/div[2]/select"

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


                    


                    # --- (iv) Identity Proof ---

            time.sleep(0.5)
            try:
                        identity_proof_value = partner.get('Identity Proof', '').strip()

                        if identity_proof_value:
                            dropdown_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[13]/div/div/div/div[1]/div/div[1]/div/div/div[2]/select"

                            # Wait for the dropdown to be present
                            dropdown_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, dropdown_xpath))
                            )

                            # ✅ Use Select to choose by visible text
                            select = Select(dropdown_element)
                            select.select_by_visible_text(identity_proof_value)

                            print(f"[✓] Partner {position}: Selected Identity Proof: {identity_proof_value} (i={i}).")
                            fields_filled_count += 1
                        else:
                            print(f"[INFO] Partner {position}: No Identity Proof provided in input data.")
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Identity Proof dropdown.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Identity Proof dropdown.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Failed to select Identity Proof: {e}")
                        fields_failed_count += 1


                    # (v) Residential Proof    
            time.sleep(0.5)
            try:
                        residential_proof_value = partner.get('Residential Proof', '').strip()

                        if residential_proof_value:
                            dropdown_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[13]/div/div/div/div[1]/div/div[2]/div/div/div[2]/select"

                            # Wait for dropdown
                            dropdown_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, dropdown_xpath))
                            )

                            # Use Select helper to choose option
                            select = Select(dropdown_element)
                            select.select_by_visible_text(residential_proof_value)

                            print(f"[✓] Partner {position}: Selected Residential Proof: {residential_proof_value} (i={i}).")
                            fields_filled_count += 1
                        else:
                            print(f"[INFO] Partner {position}: No Residential Proof provided in input data.")

            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Residential Proof dropdown.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Residential Proof dropdown.")
            except Exception as e:
                        print(f"[✗] Failed to select Residential Proof: {e}")
                        fields_failed_count += 1
                        

            # Identity and Residential Proof
            identity_proof_xpath = f"(//input[@aria-label='Identity Proof No.'])[{position}]"
            driver.find_element(By.XPATH, identity_proof_xpath).send_keys(partner.get('Identity Proof No.', ''))

            residential_proof_xpath = f"(//input[@aria-label='Residential Proof No.'])[{position}]"
            driver.find_element(By.XPATH, residential_proof_xpath).send_keys(partner.get('Residential Proof No.', ''))

            
            # Upload proof documents
            try:
                # Identity Proof Upload
                parent_div_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[1]"

                if partner.get('Proof of identity'):
                    file_path = partner.get('Proof of identity')
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
                parent_div_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[3]/div/div/div[2]"

                if partner.get('Residential proof'):
                        file_path = partner.get('Residential proof')
                        success = handle_dynamic_residency_upload(driver, parent_div_xpath, file_path, i)
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

            # --- Contribution Details ---
            print(f"[INFO] Partner {position}: Processing Contribution Details...")

            # --- Form of contribution ---
            time.sleep(1)
            try:
                        form_of_contribution = partner.get('Form of contribution', '').strip()
                        if form_of_contribution:
                            dropdown_xpath_base = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[20]/div/div/div/div[1]/div/div[1]/div/div/div[2]/select"

                            contribution_dropdown = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, dropdown_xpath_base))
                            )
                            select = Select(contribution_dropdown)
                            select.select_by_visible_text(form_of_contribution)
                            print(f"[✓] Partner {position}: Selected Form of contribution: '{form_of_contribution}' (i={i}).")
                            fields_filled_count += 1

                            # Handle "Other than cash" case
                            if form_of_contribution.lower() == 'other than cash':
                                other_detail = partner.get('Other contribution details', '').strip()
                                if other_detail:
                                    other_input_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[20]/div/div/div/div[1]/div/div[2]/div/div/div[2]/input"

                                    other_input = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable((By.XPATH, other_input_xpath))
                                    )
                                    other_input.send_keys(other_detail)
                                    print(f"[✓] Partner {position}: Filled 'Other than cash' details: '{other_detail}' (i={i}).")
                                    fields_filled_count += 1
                                else:
                                    print(f"[INFO] Partner {position}: No 'Other contribution details' provided.")
                        else:
                            print(f"[INFO] Partner {position}: Form of contribution not provided.")
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Form of contribution dropdown.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Form of contribution dropdown.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Error selecting Form of contribution: {e}")
                        fields_failed_count += 1
                            
                    # --- Monetary value of contribution (in INR.) (in figures) ---
            time.sleep(0.5)
            try:
                        num_companies = partner.get('Monetary value', '')
                        if num_companies:
                            company_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[20]/div/div/div/div[1]/div/div[3]/div/div/div[2]/input"

                            company_input = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, company_xpath))
                            )
                            driver.execute_script("arguments[0].scrollIntoView(true);", company_input)
                            company_input.clear()
                            company_input.send_keys(num_companies)
                            print(f"[✓] Partner {position}: Entered Number of company(s): {num_companies} (i={i}).")
                            fields_filled_count += 1
                        else:
                            print(f"[INFO] Partner {position}: No Number of company(s) provided in data.")
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Number of company(s) input.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Number of company(s) input.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Failed to enter Number of company(s): {e}")
                        fields_failed_count += 1


            # --- Number of LLP(s) in which he/ she is a partner ---
            time.sleep(0.5)
            try:
                        num_llps = partner.get('Number of LLPs', '').strip()
                        if num_llps:
                            llp_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[20]/div/div/div/div[1]/div/div[5]/div/div/div[2]/input"

                            llp_input = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, llp_xpath))
                            )
                            driver.execute_script("arguments[0].scrollIntoView(true);", llp_input)
                            llp_input.clear()
                            llp_input.send_keys(num_llps)
                            print(f"[✓] Partner {position}: Entered Number of LLP(s): {num_llps} (i={i}).")
                            fields_filled_count += 1
                        else:
                            print(f"[INFO] Partner {position}: No Number of LLP(s) provided in data.")
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Number of LLP(s) input.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Number of LLP(s) input.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Failed to enter Number of LLP(s): {e}")
                        fields_failed_count += 1



            # --- Number of company(s) in which he/ she is a director ---
            time.sleep(0.5)
            try:
                        num_companies = partner.get('Number of companies', '').strip()
                        if num_companies:
                            company_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[20]/div/div/div/div[1]/div/div[6]/div/div/div[2]/input"

                            company_input = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, company_xpath))
                            )
                            driver.execute_script("arguments[0].scrollIntoView(true);", company_input)
                            company_input.clear()
                            company_input.send_keys(num_companies)
                            print(f"[✓] Partner {position}: Entered Number of company(s): {num_companies} (i={i}).")
                            fields_filled_count += 1
                        else:
                            print(f"[INFO] Partner {position}: No Number of company(s) provided in data.")
            except TimeoutException:
                        print(f"[✗] Partner {position}: Timeout finding Number of company(s) input.")
            except NoSuchElementException:
                        print(f"[✗] Partner {position}: Could not find Number of company(s) input.")
            except Exception as e:
                        print(f"[✗] Partner {position}: Failed to enter Number of company(s): {e}")
                        fields_failed_count += 1
            # Add a small delay between partners
            time.sleep(1)

        print("[SUCCESS] Completed processing all partners without DIN/DPIN")

    except Exception as e:
        print(f"[ERROR] Failed to process partners without DIN/DPIN: {str(e)}")
        raise

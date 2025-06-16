from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException
import time
import os
import json
from pynput.keyboard import Controller, Key

def handle_file_upload(driver, parent_div_id, file_path, timeout=20):
    """Helper function to handle file uploads using keyboard input"""
    print(f"[DEBUG] Starting file upload for {parent_div_id}")
    
    try:
        # Try to find the parent div and attach button by class (main logic)
        parent_div = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, parent_div_id))
        )
        try:
            attach_button = parent_div.find_element(By.CSS_SELECTOR, "button.guide-fu-attach-button")
        except Exception as e:
            print(f"[WARNING] Could not find attach button by class in parent div: {e}")
            # Fallback to XPath if provided and if this is a bank proof upload
            id_proof_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[5]/div/div/div[2]/div[1]/input[1]"
            address_proof_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[9]/div/div/div[2]/div[1]/input[1]"
            if "cop_72059460" in parent_div_id:
                button_xpath = id_proof_xpath
            else:
                button_xpath = address_proof_xpath
            attach_button = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, button_xpath))
            )
        
        # Scroll to and click the Attach button
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", attach_button)
        time.sleep(2)
        
        # Try multiple click methods
        try:
            attach_button.click()
        except:
            try:
                driver.execute_script("arguments[0].click();", attach_button)
            except:
                actions = ActionChains(driver)
                actions.move_to_element(attach_button).click().perform()
        
        # Wait for the file dialog to be ready (short delay to ensure dialog opens)
        time.sleep(2)

        # Initialize keyboard controller
        keyboard = Controller()

        # Ensure browser window is in focus
        driver.switch_to.window(driver.current_window_handle)
        normalized_path = os.path.normpath(file_path)
        print(f"[DEBUG] Normalized path for typing: {normalized_path}")

        # Type the file path character by character with a small delay to ensure stability
        for char in normalized_path:
            keyboard.press(char)
            keyboard.release(char)
            # Add a slightly longer delay for critical characters like ':' to ensure dialog captures it
            if char in [":", "\\"]:
                time.sleep(0.1)
            else:
                time.sleep(0.05)

        # Wait briefly to ensure typing is complete
        time.sleep(1)

        # Press Enter to submit the dialog
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(1)

        # Handle the "Document Added Successfully!" dialog with shorter wait time
        try:
            ok_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ok-button, #okSuccessModalBtn"))
            )
            driver.execute_script("arguments[0].click();", ok_button)
            print(f"[AGILE PRO] Clicked OK on success dialog")
            time.sleep(0.3)
        except TimeoutException:
            print("[INFO] No success dialog found, assuming upload completed without dialog")
        except Exception as e:
            print(f"[WARNING] Failed to interact with success dialog: {str(e)}")

        # Verify upload success by checking the file list
        try:
            file_list = parent_div.find_element(By.CSS_SELECTOR, "ul.guide-fu-fileItemList")
            if file_list.find_elements(By.TAG_NAME, "li"):
                print(f"[AGILE PRO] File upload verified: File appears in the uploaded list")
                return True
            else:
                print(f"[WARNING] File upload may not have completed: No files found in the upload list")
                return False
        except Exception as e:
            print(f"[INFO] No file list found, unable to verify upload via UI: {str(e)}")
            return True  # Assume success if no file list is found

    except Exception as e:
        print(f"[ERROR] File upload failed for {parent_div_id}: {str(e)}")
        return False
    


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
            id_proof_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[9]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[1]/input[1]"
            address_proof_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[9]/div/div/div/div[1]/div/div[3]/div/div/div[2]/div[1]/input[1]"
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
        
        time.sleep(2)  # Increased wait to ensure file dialog is ready
        
        # Initialize keyboard controller
        keyboard = Controller()

        # Type the file path
        time.sleep(5)  # after initializing keyboard
        keyboard.type(file_path)
        time.sleep(5)
        
        # Press Enter
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(1)
        
        # Handle the "Document Added Successfully!" dialog with shorter wait time
        try:
            ok_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ok-button"))
            )
            ok_button.click()
            print(f"[AGILE PRO] Clicked OK on success dialog")
            time.sleep(0.3)
        except Exception as e:
            print(f"[WARNING] Could not click OK button on success dialog: {str(e)}")
            try:
                ok_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.ID, "okSuccessModalBtn"))
                )
                ok_button.click()
                print(f"[AGILE PRO] Clicked OK on success dialog (using alternative selector)")
                time.sleep(0.3)
            except Exception as e2:
                print(f"[WARNING] Could not click OK button using alternative selector: {str(e2)}")
                try:
                    ok_button = driver.find_element(By.CSS_SELECTOR, "button.ok-button, #okSuccessModalBtn")
                    driver.execute_script("arguments[0].click();", ok_button)
                    print(f"[AGILE PRO] Clicked OK on success dialog (using JavaScript)")
                    time.sleep(0.3)
                except Exception as e3:
                    print(f"[ERROR] All attempts to click OK button failed: {str(e3)}")
        
        print(f"[AGILE PRO] Uploaded file: {file_path}")
    except Exception as e:
        print(f"[ERROR] File upload failed for {parent_div_id}: {str(e)}")
        raise

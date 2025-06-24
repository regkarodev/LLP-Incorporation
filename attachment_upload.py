from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import time
import os
import json
from pynput.keyboard import Controller, Key
import win32gui
import win32con
from pywinauto import Application, findwindows

def handle_file_upload(driver, parent_div_id, file_path, json_file_path, timeout=20):
    """Helper function to handle file uploads, verifying and correcting path from JSON"""
    print(f"[DEBUG] Starting file upload for {parent_div_id}")
    
    # Load expected path from JSON
    try:
        with open(json_file_path, 'r') as f:
            json_data = json.load(f)
            expected_path = os.path.normpath(json_data.get('file_path', ''))
        if not expected_path:
            print("[ERROR] No file_path found in JSON")
            return False
        print(f"[DEBUG] Expected path from JSON: {expected_path}")
    except Exception as e:
        print(f"[ERROR] Failed to read JSON file {json_file_path}: {e}")
        return False

    try:
        # Try to find the parent div and attach button by class
        parent_div = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, parent_div_id))
        )
        try:
            attach_button = parent_div.find_element(By.CSS_SELECTOR, "button.guide-fu-attach-button")
        except Exception as e:
            print(f"[WARNING] Could not find attach button by class in parent div: {e}")
            # Fallback to XPath
            id_proof_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[5]/div/div/div[2]/div[1]/input[1]"
            address_proof_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[9]/div/div/div[2]/div[1]/input[1]"
            button_xpath = id_proof_xpath if "cop_72059460" in parent_div_id else address_proof_xpath
            attach_button = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, button_xpath))
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

        # Type initial file path using pynput
        keyboard = Controller()
        normalized_path = os.path.normpath(file_path)
        print(f"[DEBUG] Typing initial path: {normalized_path}")
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

        # Verify the typed path in the file dialog using pywinauto
        try:
            # Connect to the file dialog
            app = Application().connect(title_re="Open", timeout=5)
            dlg = app.window(title_re="Open")
            
            # Access the "File name" edit box
            file_name_edit = dlg.child_window(class_name="Edit", found_index=0)
            typed_text = file_name_edit.window_text()
            print(f"[DEBUG] Typed text in file dialog: {typed_text}")

            # Compare with JSON path
            if typed_text.lower() == expected_path.lower():
                print("[AGILE PRO] Typed path matches JSON path")
            else:
                print(f"[WARNING] Typed path mismatch! Expected: {expected_path}, Got: {typed_text}")
                # Clear the input field
                file_name_edit.set_focus()
                file_name_edit.type_keys("^a{DELETE}")  # Select all and delete
                time.sleep(0.5)
                # Type the JSON path
                print(f"[DEBUG] Typing corrected path from JSON: {expected_path}")
                file_name_edit.type_keys(expected_path, with_spaces=True, pause=0.07)
                time.sleep(0.5)
                # Verify corrected path
                corrected_text = file_name_edit.window_text()
                if corrected_text.lower() == expected_path.lower():
                    print("[AGILE PRO] Corrected path verified successfully")
                else:
                    print(f"[ERROR] Failed to correct path. Expected: {expected_path}, Got: {corrected_text}")
                    return False

        except findwindows.ElementNotFoundError:
            print("[ERROR] File dialog not found for verification")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to verify or correct path in file dialog: {e}")
            return False

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
        print(f"[ERROR] File upload failed for {parent_div_id}: {e}")
        return False
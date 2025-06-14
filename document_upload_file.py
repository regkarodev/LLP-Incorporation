from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import time
import os
from pynput.keyboard import Controller, Key
import win32gui
import win32con

def handle_file_upload(driver, parent_div_id, file_path, timeout=20):
    """Handles file uploads via keyboard automation and verifies success"""
    print(f"[DEBUG] Starting file upload for {parent_div_id}")
    
    try:
        # Locate the parent div
        parent_div = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, parent_div_id))
        )
        
        # Try to find attach button by class name
        try:
            attach_button = parent_div.find_element(By.CSS_SELECTOR, "button.guide-fu-attach-button")
        except Exception as e:
            print(f"[WARNING] Could not find attach button by class: {e}")
            # Fallback to known absolute XPaths
            id_proof_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[9]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[1]/input[1]"
            address_proof_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[9]/div/div/div/div[1]/div/div[3]/div/div/div[2]/div[1]/input[1]"
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
        time.sleep(1)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(1)

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

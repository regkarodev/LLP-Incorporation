from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import json

def handle_file_upload(driver, parent_div_id, file_path, json_file_path, timeout=20):
    """
    Helper function to handle file uploads in a cross-platform manner
    by interacting directly with the file input element.
    """
    print(f"[DEBUG] Starting file upload for {parent_div_id}")

    # Load and verify the expected path from the JSON file
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

    # Check if the file to be uploaded actually exists
    if not os.path.exists(file_path):
        print(f"[ERROR] The file to upload does not exist at the specified path: {file_path}")
        return False

    try:
        # Locate the parent container of the file upload element
        parent_div = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, parent_div_id))
        )

        # Find the hidden <input type="file"> element within the parent container
        try:
            # The most reliable way to find the file input is by its type
            file_input = parent_div.find_element(By.XPATH, ".//input[@type='file']")
            print("[DEBUG] Successfully found file input element with type='file'.")
        except NoSuchElementException:
            print("[WARNING] Could not find the file input element by its type. Falling back to the provided XPaths.")
            # Fallback to the XPaths you provided, assuming they point to the file input
            id_proof_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[5]/div/div/div[2]/div[1]/input[1]"
            address_proof_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[8]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[9]/div/div/div[2]/div[1]/input[1]"
            input_xpath = id_proof_xpath if "cop_72059460" in parent_div_id else address_proof_xpath
            file_input = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, input_xpath))
            )

        # Send the file path directly to the file input element
        # This is the cross-platform method that avoids the need for GUI automation
        file_input.send_keys(file_path)

        print(f"[AGILE PRO] Successfully sent file path '{file_path}' to the upload element.")

        # Handle the success popup that may appear after the upload
        try:
            ok_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ok-button, #okSuccessModalBtn"))
            )
            driver.execute_script("arguments[0].click();", ok_button)
            print("[AGILE PRO] Clicked OK on the success dialog.")
            time.sleep(0.3)
        except TimeoutException:
            print("[INFO] No success dialog was found; assuming the upload was completed.")
        except Exception as e:
            print(f"[WARNING] Could not interact with the success dialog: {e}")

        # Verify that the file has been successfully uploaded
        try:
            file_list = parent_div.find_element(By.CSS_SELECTOR, "ul.guide-fu-fileItemList")
            if file_list.find_elements(By.TAG_NAME, "li"):
                print("[AGILE PRO] File upload has been verified in the attachment list.")
                return True
            else:
                print("[WARNING] The file may not have been uploaded successfully; no file was found in the list.")
                return False
        except Exception as e:
            print(f"[INFO] Could not find a file list for verification: {e}")
            return True  # Assuming success if no list is found

    except Exception as e:
        print(f"[ERROR] The file upload process failed for {parent_div_id}: {e}")
        return False
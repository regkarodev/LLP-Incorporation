import json
import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Removing the direct driver initialization
def scroll_into_view(driver, element):
    """Helper function to scroll an element into view using JavaScript."""
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Error scrolling element into view: {str(e)}")
        return False



def click_element(driver, *, xpath=None, id=None, css_selector=None, class_name=None, name=None):
    try:
        if xpath is not None and id is not None and css_selector is not None and class_name is not None and name is not None:
            raise ValueError("Error: Cannot provide multiple arguments. Choose one.")
        elif xpath is not None:
            try:
                xpath_item = driver.find_element(By.XPATH, xpath)
                xpath_item.click()
            except:
                print('{} is not found'.format(xpath))
        elif id is not None:
            try:
                id_item = driver.find_element(By.ID, id)
                id_item.click()
            except:
                print('{} is not found'.format(id))
        elif css_selector is not None:
            try:
                css_item = driver.find_element(By.CSS_SELECTOR, css_selector)
                css_item.click()
            except:
                print('{} is not found'.format(css_selector))
        elif class_name is not None:
            try:
                class_item = driver.find_element(By.CLASS_NAME, class_name)
                class_item.click()
            except:
                print('{} is not found'.format(class_name))
        elif name is not None:
            try:
                name_item = driver.find_element(By.NAME, name)
                name_item.click()
            except:
                print('{} is not found'.format(name))
        else:
            pass
    except:
        pass

def send_text(driver, *, xpath=None, id=None, css_selector=None, class_name=None, name=None, keys=None):
    try:
        if xpath is not None and id is not None and css_selector is not None and class_name is not None and name is not None:
            raise ValueError("Error: Cannot provide multiple arguments. Choose one.")
        elif xpath is not None:
            try:
                xpath_item = driver.find_element(By.XPATH, xpath)
                xpath_item.send_keys(keys)
            except:
                print('{} is not found'.format(xpath))
        elif id is not None:
            try:
                id_item = driver.find_element(By.ID, id)
                id_item.send_keys(keys)
            except:
                print('{} is not found'.format(id))
        elif css_selector is not None:
            try:
                css_item = driver.find_element(By.CSS_SELECTOR, css_selector)
                css_item.send_keys(keys)
            except:
                print('{} is not found'.format(css_selector))
        elif class_name is not None:
            try:
                class_item = driver.find_element(By.CLASS_NAME, class_name)
                class_item.send_keys(keys)
            except:
                print('{} is not found'.format(class_name))
        elif name is not None:
            try:
                name_item = driver.find_element(By.NAME, name)
                name_item.send_keys(keys)
            except:
                print('{} is not found'.format(name))
        else:
            pass
    except:
        pass


def log_terminal_output(message, level="info"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level.upper()}] {message}")


def set_date_field(driver, date_field_id, your_date):
    """
    Set date in a date field using JavaScript and verify the input
    
    Args:
        driver: Selenium WebDriver instance
        date_field_id: ID of the date input field
        your_date: Date to be set in DD/MM/YYYY format
    """
    # Wait for the date input field to be present and interactable
    date_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, date_field_id))
    )

    # Wait for the element to be clickable
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, date_field_id))
    )

    # Set the date using JavaScript with full event dispatch
    driver.execute_script(f"""
        const input = document.getElementById('{date_field_id}');
        if (input) {{
            input.focus();
            input.value = '{your_date}';
            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
        }}
    """)
    print("[+] Date field set via JS and events dispatched.")

    # Wait for any validation to complete
    time.sleep(1)

    # Verify the date was set correctly
    actual_value = date_input.get_attribute('value')
    if actual_value == your_date:
        print("[+] Date verified successfully")
    else:
        print(f"[-] Date verification failed. Expected: {your_date}, Got: {actual_value}")

def click_true_option(driver, parent_key, options_dict, section_heading=None):
    """
    Click the option that is marked as true in the options dictionary
    Args:
        driver: Selenium WebDriver instance
        parent_key: The parent key in the JSON structure
        options_dict: Dictionary containing options with boolean values
        section_heading: Optional. If provided, scope the search to this section.
    """
    try:
        options = options_dict.get(parent_key, {})
        true_option = None
        for option, value in options.items():
            if value is True:
                true_option = option
                break
        if true_option is None:
            print(f"No true option found for parent key: {parent_key}")
            return False
        # Print all label texts for debugging
        labels = driver.find_elements(By.XPATH, "//label")
        for lbl in labels:
            print(f"[DEBUG] Label text: '{lbl.text}'")
        # If section_heading is provided, scope the search to that section
        if section_heading:
            try:
                section_xpath = f"//*[contains(text(), '{section_heading}')]/ancestor::div[contains(@class, 'panel') or contains(@class, 'section') or contains(@class, 'guidePanel')]"
                print(f"[DEBUG] Searching for section with XPath: {section_xpath}")
                section = driver.find_element(By.XPATH, section_xpath)
                print(f"[DEBUG] Found section HTML: {section.get_attribute('outerHTML')[:1000]}")
                group_label_xpath = f".//label[contains(normalize-space(text()), '{parent_key}') or normalize-space(text())='{parent_key}']"
                print(f"[DEBUG] Searching for group label within section with XPath: {group_label_xpath}")
                group_label = section.find_element(By.XPATH, group_label_xpath)
                print(f"[DEBUG] Found group label text: '{group_label.text}'")
                group_container = group_label.find_element(By.XPATH, "./ancestor::div[contains(@class, 'guideradiobutton') or contains(@class, 'guideFieldNode')]")
                print(f"[DEBUG] Found group container HTML: {group_container.get_attribute('outerHTML')[:1000]}")
                radio_input = group_container.find_element(By.XPATH, f".//input[@type='radio' and @aria-label='{true_option}']")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_input)
                driver.execute_script("arguments[0].removeAttribute('readonly'); arguments[0].removeAttribute('disabled');", radio_input)
                driver.execute_script("arguments[0].click();", radio_input)
                print(f"Successfully clicked radio input with aria-label: {true_option} in group: {parent_key} in section: {section_heading}")
                return True
            except Exception as e:
                print(f"[DEBUG] Could not click radio input by aria-label in section {section_heading}, group {parent_key}: {str(e)}")
        # Fallback to global search as before
        try:
            group_label_xpath = f"//label[contains(normalize-space(text()), '{parent_key}') or normalize-space(text())='{parent_key}']"
            print(f"[DEBUG] Searching for group label with XPath: {group_label_xpath}")
            group_label = driver.find_element(By.XPATH, group_label_xpath)
            group_container = group_label.find_element(By.XPATH, "./ancestor::div[contains(@class, 'guideradiobutton') or contains(@class, 'guideFieldNode')]")
            radio_input = group_container.find_element(By.XPATH, f".//input[@type='radio' and @aria-label='{true_option}']")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_input)
            driver.execute_script("arguments[0].removeAttribute('readonly'); arguments[0].removeAttribute('disabled');", radio_input)
            driver.execute_script("arguments[0].click();", radio_input)
            print(f"Successfully clicked radio input with aria-label: {true_option} in group: {parent_key}")
            return True
        except Exception as e:
            print(f"[DEBUG] Could not click radio input by aria-label in group {parent_key}: {str(e)}")
        selectors = [
            f"//label[contains(text(), '{true_option}')]",
            f"//div[contains(text(), '{true_option}')]",
            f"//span[contains(text(), '{true_option}')]",
            f"//input[@value='{true_option}']",
            f"//button[contains(text(), '{true_option}')]"
        ]
        for selector in selectors:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                scroll_into_view(driver, element)
                element.click()
                print(f"Successfully clicked option: {true_option}")
                return True
            except:
                continue
        print(f"Could not find clickable element for option: {true_option}")
        return False
    except Exception as e:
        print(f"Error in click_true_option: {e}")
        return False


def upload_proof_of_identity(driver, file_path, partner_position=1):
    """
    Uploads the 'Proof of identity' file for a specific partner.

    Args:
        driver: Selenium WebDriver instance.
        file_path (str): The absolute path to the file to be uploaded.
        partner_position (int): The 1-based index for the partner section if there are multiple.
                                This helps in targeting the correct upload field if the page
                                structure repeats for multiple partners.
    Returns:
        bool: True if upload was likely successful, False otherwise.
    """
    print(f"\n--- UPLOADING PROOF OF IDENTITY FOR PARTNER {partner_position} ---")
    print(f"File path: {file_path}")

    if not os.path.exists(file_path):
        print(f"[ERROR] File does not exist at path: {file_path}")
        return False

    try:
        # Step 1: Locate the main container for the "Proof of identity" upload field.
        # We will use the label "Proof of identity" to find its parent `guideFieldNode` container.
        # This assumes each partner's "Proof of identity" is indexed if multiple exist.
        # If there's only one "Proof of identity" regardless of partner, remove `[{partner_position}]`.
        
        # Find the label first
        label_xpath = f"(.//label[normalize-space(text())='Proof of identity'])[{partner_position}]"
        print(f"[DEBUG] Looking for label with XPath: {label_xpath}")
        
        identity_proof_label = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, label_xpath))
        )
        print("[SUCCESS] Found 'Proof of identity' label.")

        # Navigate to the overall component container (guideFieldNode)
        # This assumes the label's parent div is the 'guideFieldLabel', and its parent is the 'guideFieldNode'
        field_container = identity_proof_label.find_element(By.XPATH, "./ancestor::div[contains(@class, 'guideFieldNode') and contains(@class, 'guideFileUpload')]")
        print("[SUCCESS] Found field container for 'Proof of identity'.")

        # Step 2: Find the file input element within this container.
        # The input element has a unique attribute `uniquename="6bIdentityProof"` which we can use.
        # Or, more simply, it's the input type="file".
        file_input_xpath = ".//input[@type='file']" # This is usually the most reliable within a scoped container
        # Alternative using unique attribute if the above is not specific enough:
        # file_input_xpath = ".//input[@type='file' and @uniquename='6bIdentityProof']"
        print(f"[DEBUG] Looking for file input with relative XPath: {file_input_xpath} within the field container.")
        
        file_input_element = field_container.find_element(By.XPATH, file_input_xpath)
        print("[SUCCESS] Found file input element.")

        # Step 3: Make the file input visible and enabled using JavaScript.
        # This is often necessary because these inputs are styled to be hidden.
        print("[INFO] Making file input element visible and enabled via JavaScript...")
        driver.execute_script(
            "arguments[0].style.display = 'block'; " +
            "arguments[0].style.visibility = 'visible'; " +
            "arguments[0].style.opacity = '1'; " +
            "arguments[0].removeAttribute('disabled');" +
            "arguments[0].removeAttribute('hidden');",  # Ensure not hidden
            file_input_element
        )
        # A small pause for the DOM to update if needed, though send_keys to a file input is usually robust.
        time.sleep(1) 

        # Step 4: Send the file path to the input element.
        print(f"[INFO] Sending file path '{file_path}' to the input element...")
        file_input_element.send_keys(file_path)
        print("[SUCCESS] File path sent.")
        
        # Step 5: Optional verification.
        # Wait a moment for the UI to potentially update with the filename.
        time.sleep(2) 
        filename_for_verification = os.path.basename(file_path)
        
        # Look for the filename in the list of attached files (ul class="guide-fu-fileItemList")
        try:
            attached_files_list = field_container.find_element(By.XPATH, ".//ul[contains(@class, 'guide-fu-fileItemList')]")
            WebDriverWait(attached_files_list, 5).until(
                EC.text_to_be_present_in_element((By.XPATH, ".//li"), filename_for_verification)
            )
            print(f"[SUCCESS] Verification: Filename '{filename_for_verification}' found in the attachment list.")
            return True
        except TimeoutException:
            print(f"[WARNING] Verification: Filename '{filename_for_verification}' not found in attachment list after 5 seconds.")
            print("[INFO] The file might still be uploaded; UI verification failed or is slow.")
            # Depending on strictness, you might return False here or assume success if send_keys didn't error.
            return True # Assuming send_keys success is primary for now
        except NoSuchElementException:
            print(f"[WARNING] Verification: Could not find the attachment list 'ul.guide-fu-fileItemList'.")
            return True # Assuming send_keys success

    except TimeoutException as e:
        print(f"[ERROR] Timeout while trying to locate elements for 'Proof of identity' upload: {e}")
        return False
    except NoSuchElementException as e:
        print(f"[ERROR] Could not find an element for 'Proof of identity' upload: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during 'Proof of identity' file upload: {type(e).__name__} - {e}")
        return False

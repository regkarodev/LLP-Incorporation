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


# Removing the direct driver initialization

def scroll_to_middle(driver, element):
    """Scroll element to middle of viewport"""
    try:
        # Get viewport height
        viewport_height = driver.execute_script("return window.innerHeight")
        
        # Get element position and size
        element_y = element.location['y']
        element_height = element.size['height']
        
        # Calculate scroll position to center element
        scroll_y = element_y - (viewport_height / 2) + (element_height / 2)
        
        # Scroll to position with smooth behavior
        driver.execute_script("""
            window.scrollTo({
                top: arguments[0],
                behavior: 'smooth',
                block: 'center'
            });
        """, scroll_y)
        
        # Wait for scroll to complete
        time.sleep(1)
        
        # Ensure element is in view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Error in scroll_to_middle: {e}")
        # Fallback to basic scroll if smooth scroll fails
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
        except:
            pass

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


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def click_true_option(driver, parent_key, options_dict):
    """
    Click the option that is marked as true in the options dictionary
    
    Args:
        driver: Selenium WebDriver instance
        parent_key: The parent key in the JSON structure
        options_dict: Dictionary containing options with boolean values
        Example:
        {
            "parent_key": {
                "option1": true,
                "option2": false,
                "option3": false
            }
        }
    """
    try:
        # Get the options for the parent key
        options = options_dict.get(parent_key, {})
        
        # Find the option that is true
        true_option = None
        for option, value in options.items():
            if value is True:
                true_option = option
                break
        
        if true_option is None:
            print(f"No true option found for parent key: {parent_key}")
            return False
            
        # Try different selectors to find and click the element
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
                scroll_to_middle(driver, element)
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


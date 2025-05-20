import json
import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager

#init driver
firefox_options = FirefoxOptions()
firefox_options.add_argument("--start-maximized")
service = FirefoxService(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=firefox_options)
driver.get("https://www.mca.gov.in/content/mca/global/en/mca/llp-e-filling/Fillip.html")
# driver.get('https://www.mca.gov.in/content/mca/global/en/foportal/fologin.html')
time.sleep(10)



def click_element(*, xpath=None, id=None, css_selector=None, class_name=None, name=None):
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

def send_text(*, xpath=None, id=None, css_selector=None, class_name=None, name=None, keys=None):
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



# testing

def radio_click(radio_name, value):
    try:
        # Use a more specific XPath to find the label directly
        xpath = f"//label[contains(@class, 'ant-radio-wrapper')]//input[@name='{radio_name}' and @value='{value}']/.."
        label = driver.find_element(By.XPATH, xpath)
        
        # Click the label
        label.click()
        
        # Wait a moment for the selection to take effect
        time.sleep(0.5)
        
        # Verify the selection
        if "ant-radio-checked" in label.get_attribute("class"):
            print(f"Successfully selected radio button: {value}")
        else:
            print(f"Failed to select radio button: {value}")
            
    except Exception as e:
        print(f"Error selecting radio button: {e}")
        # Print more detailed error information
        print(f"Radio name: {radio_name}")
        print(f"Value: {value}")



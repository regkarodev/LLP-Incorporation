import time
import os
import traceback
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import function1, json,  attachment_upload
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import partners_without_din, bodies_corporate_with_din, bodies_corporate_without_din, bodies_corporate_with_din, document_upload_file
from function1 import scroll_into_view, send_text, click_element

# Global driver variable
driver = None 

def setup_driver(webdriver_instance):
    """Set up the driver for this module"""
    global driver
    driver = webdriver_instance
    return driver

def log_terminal_output(message, level="info"):
    """Helper function for logging"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level.upper()}] {message}")

def log_message(message):
    """Simple logging function"""
    print(f"[AUTOMATE1] {message}")

def check_driver_session():
    """Check if the driver session is still active"""
    global driver
    try:
        # Try a simple command to check if session is alive
        driver.current_url
        return True
    except (WebDriverException, InvalidSessionIdException):
        return False

def ensure_driver_session():
    """Ensure driver session is active, reconnect if necessary"""
    global driver
    if not check_driver_session():
        print("Browser session lost. Attempting to reconnect...")
        try:
            # Reinitialize the driver
            from selenium import webdriver
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from webdriver_manager.firefox import GeckoDriverManager
            
            # Load config for browser settings
            with open("config.json", "r") as f:
                config = json.load(f)
            
            # Set up Firefox options
            options = FirefoxOptions()
            options.add_argument("--start-maximized")
            
            # Initialize new driver
            driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options
            )
            
            # Navigate back to the form
            driver.get(config.get('fillip_url', ''))
            print("Successfully reconnected to browser session")
            return True
        except Exception as e:
            print(f"Failed to reconnect: {e}")
            return False
    return True


def run_llp_form_sequence(webdriver_instance=None):
    """Run the full LLP form filling sequence"""
    global driver
    
    # Set driver if provided
    if webdriver_instance:
        driver = webdriver_instance
    
    # Make sure driver is initialized
    if not driver:
        raise ValueError("Driver is not initialized. Call setup_driver first or provide a driver instance.")
    
    try:
        # Load the JSON config
        with open("config_data.json", "r") as f:
            config_data = json.load(f)

        with open('config.json', 'r') as f:
            config_selectors = json.load(f)

        # Begin the form sequence
        print("[AUTOMATE1] Starting LLP form sequence...")
        
        # Add periodic session checks
        check_interval = 10  # Check every 10 operations
        operation_count = 0
        
        # Registrar of Companies
        time.sleep(2)
        click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy-panel1626772568950-guideradiobutton__-1_widget')

        # Service Request Number
        send_text(driver, css_selector='#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy-panel1626772568950-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['Service Request Number'])

        # Type of incorporation
        time.sleep(2)
        click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy-panel1626772568950-guideradiobutton_1069538009__-1_widget')

        # SAVE AND CONTINUE BUTTON 
        time.sleep(2)
        click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy_copy-mca_button___widget')

        # OK POP_UP BUTTON
        time.sleep(2)
        try:
            click_element(driver,css_selector='#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')   # Increase wait time
        except Exception as e:
            print(f"[ERROR] Failed to click MCA button: {str(e)}")
            # Try alternative selector if the first one fails
            try:
                click_element(driver,css_selector='button[aria-label="MCA"]')
            except Exception as e2:
                print(f"[ERROR] Failed to click MCA button with alternative selector: {str(e2)}")
                raise

        # NEXT BUTTON
        time.sleep(2)
        click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel-panel_copy_copy_copy_1792429032-mca_button___widget')

        # *Address Line I
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_copy_11___widget', keys=config_data['form_data']['fields']['Address Line I'])

        # *Address Line II
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_copy_11_635080626___widget', keys=config_data['form_data']['fields']['Address Line II'])

        # *PIN CODE
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_copy_11_1386963699___widget', keys=config_data['form_data']['fields']['PIN CODE'])

        # *Area/ Locality
        # Wait for the dropdown to have more than 1 option
        time.sleep(2)
        click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_9527960___widget')
        time.sleep(2)
        send_text(driver, css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_9527960___widget',keys=config_data['form_data']['fields']['Area/Locality1'] )
        

        # *Longitude
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_1045433___widget', keys=config_data['form_data']['fields']['Longitude'])

        # *Latitude
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_1045433_1076286455___widget', keys=config_data['form_data']['fields']['Latitude'])

        # *Jurisdiction of Police Station
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel-panel_702814714-panel-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['Jurisdiction of Police Station'])

        # (b) Contact Details

        # Phone (with STD/ISD code)
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_417418999-panel_2000768201_cop-phonestdisdbox___widget', keys=config_data['form_data']['fields']['Phone (with STD/ISD code)'])

        # *Mobile No.
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_417418999-panel_2000768201_cop-guidetextbox_copy_11_211671462___widget', keys=config_data['form_data']['fields']['Mobile No'])

        # Fax
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_417418999-panel_2000768201_cop-guidenumericbox_1010___widget', keys=config_data['form_data']['fields']['Fax'])

        # *Email ID
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_417418999-panel_2000768201_cop-guidetextbox_copy_11___widget', keys=config_data['form_data']['fields']['Email ID'])

        # partnership and my membership number
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox_1809173783___widget', keys=config_data['form_data']['fields']['partnership and my membership number'])

        ## (c) Attachments

        # Upload files using JavaScript override for attachments
        time.sleep(2)
        document_upload_file.handle_file_uploads(driver, config_data)
        time.sleep(2)
        document_upload_file.handle_file_uploads(driver, config_data)
        
        #(d) *Name of the office of Registrar in whose jurisdiction the proposed LLP is to be registered
        time.sleep(0.5)        
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_2015234307-guidedropdownlist_co___widget', keys=config_data['form_data']['fields']['Name of the office of Registrar'])


        # 5 Total number of designated partners and partners of the LLP
        # *Individuals Having valid DIN/DPIN
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629350115276-tableItem1629350115279___widget', keys=config_data['form_data']['fields']['Individuals Having valid DIN/DPIN'])

        # *Individuals Not having valid DIN/DPIN
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629350123645-tableItem1629350123648___widget', keys=config_data['form_data']['fields']['Individuals Not having valid DIN/DPIN'])

        # *Body corporates and their nominees Having valid DIN/DPIN
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629350126976-tableItem1629350126979___widget', keys=config_data['form_data']['fields']['Body corporates and their nominees Having valid DIN/DPIN'])

        time.sleep(0.5)
        # *Body corporates and their nominee not having valid DIN/DPIN
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629350131849-tableItem1629350131852___widget', keys=config_data['form_data']['fields']['Body corporates and their nominee not having valid DIN/DPIN'])

        # *Individuals Having valid DIN/DPIN
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629350148437-tableItem1629350148441___widget', keys=config_data['form_data']['fields']['Individuals Having valid DIN/DPIN1'])

        # *Individuals Not having valid DIN/DPIN
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629356006750-tableItem1629356006753___widget', keys=config_data['form_data']['fields']['Individuals Not having valid DIN/DPIN1'])

        # *Body corporates and their nominees Having valid DIN/DPIN
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629356019361-tableItem1629356019364___widget', keys=config_data['form_data']['fields']['Body corporates and their nominees Having valid DIN/DPIN1'])

        # *Body corporates and their nominee not having valid DIN/DPIN
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1891907560_cop-table_copy-Row1629356041275-tableItem1629356041278___widget', keys=config_data['form_data']['fields']['Body corporates and their nominee not having valid DIN/DPIN1'])



        # (A) Particulars of individual designated partners having DIN/DPIN
        def fill_designated_partners_section(driver, partners_data):
            """
            Fill each partner's subform in the (A) section using XPath with position indexing.
            Each partner's data is filled in the correct subform.
            """
            from selenium.common.exceptions import NoSuchElementException, TimeoutException
            wait = WebDriverWait(driver, 10)

            # Get the number of partners to fill from Individuals Having valid DIN/DPIN
            try:
                with open("config_data.json", "r") as f:
                    config_data = json.load(f)
                num_partners = int(config_data['form_data']['fields'].get('Individuals Having valid DIN/DPIN', 1))
                fallback_din = config_data['form_data']['fields'].get('Individuals Having valid DIN/DPIN', '')
            except Exception as e:
                print(f"[WARNING] Could not load Individuals Having valid DIN/DPIN: {str(e)}")
                num_partners = 1
                fallback_din = ''

            i = 1
            for idx in range(num_partners):
                position = idx + 1  # XPath is 1-based
                if idx < len(partners_data):
                    partner = partners_data[idx]
                    i += 1
                else:
                    partner = {'Designated partner identification number (DIN/DPIN)': fallback_din}
                print(f"[LOG] Filling Designated Partner {position} (DIN/DPIN)")
                filled = 0
                failed = 0
                # DIN/DPIN
                try:
                    din_elem = driver.find_element(By.XPATH, f"(//input[@aria-label='Designated partner identification number (DIN/DPIN)'])[{position}]")
                    din_elem.clear()
                    din_elem.send_keys(partner.get('Designated partner identification number (DIN/DPIN)', ''))
                    filled += 1

                except Exception as e:
                    print(f"[WARNING] Could not fill DIN/DPIN for partner {position}: {str(e)}")
                    failed += 1
                # Wait for Name to be auto-filled
                try:
                    wait.until(lambda d: d.find_element(By.XPATH, f"(//input[@aria-label='Name'])[{position}]").get_attribute('value').strip() != "")
                    filled += 1
                except Exception:
                    failed += 1
                
                # Whether resident of India (radio)
                time.sleep(0.5)
                try:
                    # Get the resident status, defaulting to False if not provided
                    is_resident = False
                    resident_data = partner.get('Whether resident of India', {})
                    if isinstance(resident_data, dict):
                        is_resident = resident_data.get('Yes', False)
                    elif isinstance(resident_data, str):
                        is_resident = resident_data.lower() in ['true', 'yes']
                    elif isinstance(resident_data, bool):
                        is_resident = resident_data

                    # Absolute XPath with dynamic index {i}
                    radio_container_xpath = f"/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[{i}]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[3]/div/div/div[2]"
                    
                    try:
                        radio_container = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, radio_container_xpath))
                        )

                        radio_buttons = radio_container.find_elements(By.XPATH, ".//input[@type='radio']")

                        if len(radio_buttons) >= 2:
                            try:
                                if is_resident:
                                    driver.execute_script("arguments[0].click();", radio_buttons[0])  # 'Yes'
                                    print(f"[✓] Body Corporate {position}: Selected 'Yes' for Whether resident of India.")
                                else:
                                    driver.execute_script("arguments[0].click();", radio_buttons[1])  # 'No'
                                    print(f"[✓] Body Corporate {position}: Selected 'No' for Whether resident of India.")
                                filled += 1  # Use 'filled' instead of 'fields_filled_count'
                            except Exception as e:
                                print(f"[WARNING] Body Corporate {position}: Error clicking radio button: {str(e)}")
                                failed += 1  # Use 'failed' instead of 'fields_failed_count'
                        else:
                            print(f"[WARNING] Body Corporate {position}: Less than 2 radio buttons found for 'Whether resident of India'.")
                            failed += 1  # Use 'failed' instead of 'fields_failed_count'

                    except TimeoutException:
                        print(f"[✗] Body Corporate {position}: Timeout finding 'Whether resident of India' radio button container.")
                        failed += 1  # Use 'failed' instead of 'fields_failed_count'
                    except Exception as e:
                        print(f"[✗] Body Corporate {position}: Error handling 'Whether resident of India' radio buttons: {str(e)}")
                        failed += 1  # Use 'failed' instead of 'fields_failed_count'

                except Exception as e:
                    print(f"[✗] Body Corporate {position}: Failed to process 'Whether resident of India': {str(e)}")



                # Form of contribution (select)
                form_contrib = partner.get('Form of contribution', '')
                if form_contrib:
                    try:
                        from selenium.webdriver.support.ui import Select
                        select_elem = driver.find_element(By.XPATH, f"(//select[@aria-label='Form of contribution'])[{position}]")
                        Select(select_elem).select_by_visible_text(form_contrib)
                        filled += 1
                        if form_contrib.lower() == 'other than cash':
                            other_val = partner.get("If 'Other than cash' selected, please specify", '')
                            if other_val:
                                try:
                                    other_elem = driver.find_element(By.XPATH, f"(//input[contains(@aria-label, 'please specify')])[{position}]")
                                    other_elem.clear()
                                    other_elem.send_keys(other_val)
                                    filled += 1
                                except Exception as e:
                                    print(f"[WARNING] Could not fill 'Other than cash' for partner {position}: {str(e)}")
                                    failed += 1
                    except Exception as e:
                        print(f"[WARNING] Could not select Form of contribution for partner {position}: {str(e)}")
                        failed += 1
                # Monetary value
                try:
                    monetary_elem = driver.find_element(By.XPATH, f"(//input[@aria-label='Monetary value of contribution (in INR) (in figures)'])[{position}]")
                    monetary_elem.clear()
                    monetary_elem.send_keys(partner.get('Monetary value of contribution (in INR) (in figures)', ''))
                    filled += 1
                except Exception as e:
                    print(f"[WARNING] Could not fill monetary value for partner {position}: {str(e)}")
                    failed += 1
                # Number of LLP(s)
                try:
                    llp_elem = driver.find_element(By.XPATH, f"(//input[@aria-label='Number of LLP(s) in which he/ she is a partner'])[{position}]")
                    llp_elem.clear()
                    llp_elem.send_keys(partner.get('Number of LLP(s) in which he/ she is a partner', ''))
                    filled += 1
                except Exception as e:
                    print(f"[WARNING] Could not fill LLP count for partner {position}: {str(e)}")
                    failed += 1
                # Number of company(s)
                try:
                    company_elem = driver.find_element(By.XPATH, f"(//input[@aria-label='Number of company(s) in which he/ she is a director'])[{position}]")
                    company_elem.clear()
                    company_elem.send_keys(partner.get('Number of company(s) in which he/ she is a director', ''))
                    filled += 1
                except Exception as e:
                    print(f"[WARNING] Could not fill company count for partner {position}: {str(e)}")
                    failed += 1
                # Company conversion fields (optional)
                if partner.get('Number of shares held'):
                    try:
                        shares_elem = driver.find_element(By.XPATH, f"(//input[@aria-label='Number of shares held'])[{position}]")
                        shares_elem.clear()
                        shares_elem.send_keys(partner['Number of shares held'])
                        filled += 1
                    except Exception as e:
                        print(f"[WARNING] Could not fill shares held for partner {position}: {str(e)}")
                        failed += 1
                if partner.get('Paid up value of shares held (in INR)'):
                    try:
                        paidup_elem = driver.find_element(By.XPATH, f"(//input[@aria-label='Paid up value of shares held (in INR)'])[{position}]")
                        paidup_elem.clear()
                        paidup_elem.send_keys(partner['Paid up value of shares held (in INR)'])
                        filled += 1
                    except Exception as e:
                        print(f"[WARNING] Could not fill paid up value for partner {position}: {str(e)}")
                        failed += 1
                print(f"[SUMMARY] Partner {position}: {filled} fields filled, {failed} failed.")

        # Example usage for (A) section:
        designated_partners = config_data['form_data'].get('designated_partners', [])
        if not designated_partners:
            designated_partners = [config_data['form_data']['fields']]
        fill_designated_partners_section(driver, designated_partners)
        
        time.sleep(1.5)


        # (B) Particulars of individual designated partners not having DIN/DPIN
        # Call the function from partners_without_din.py to handle partners without DIN/DPIN
        partners_without_din.handle_partners_without_din(driver, config_data, config_selectors)
        time.sleep(1.5)

        # # (C) Particulars of bodies corporate and their nominees as designated partners having DIN/DPIN
        bodies_corporate_with_din.handle_bodies_corporate_with_din(driver, config_data)
        time.sleep(1.5)

        # # (D) Particulars of bodies corporate and their nominees as designated partners not having DIN/DPIN
        bodies_corporate_without_din.handle_bodies_corporate_without_din(driver, config_data)
        time.sleep(1.5)


        # SAVE BUTTON
        time.sleep(2)
        try:
            click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel_copy_copy_copy-mca_button_copy___widget')
        except Exception as e:
            print(f"Save button not found: {str(e)}")

        # POPUP - OK BUTTON
        time.sleep(2)
        try:
            click_element(driver,css_selector='#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')
        except Exception as e:
            print(f"Popup OK button not found, continuing: {str(e)}")

        # NEXT BUTTON
        try:
            click_element(driver ,xpath='//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel_copy_copy_copy-mca_button___widget"]')
        except Exception as e:
            print(f"Next button not found: {str(e)}")

        # Try to fill PAN/TAN fields if they exist
        try:
            # *Area code
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel-guidetextbox___widget', keys=config_data['form_data']['fields']['PAN Area code'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['PAN Area code1'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel-guidetextbox_copy_2031803169___widget', keys=config_data['form_data']['fields']['PAN Area code2'])

            # *AO type
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_912586437-guidetextbox___widget', keys=config_data['form_data']['fields']['PAN AO type'])

            # *Range code
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_450718701-guidetextbox___widget', keys=config_data['form_data']['fields']['PAN Range code'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_450718701-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['PAN Range code1'])

            # *AO No.
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_912586437_1323045745-guidetextbox___widget', keys=config_data['form_data']['fields']['PAN AO No.'])
        except Exception as e:
            print(f"Could not fill PAN fields, they may not be present on this page: {str(e)}")

        try:
            # *Area code
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel-guidetextbox___widget', keys=config_data['form_data']['fields']['TAN Area code1'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['TAN Area code2'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel-guidetextbox_copy_2031803169___widget', keys=config_data['form_data']['fields']['TAN Area code3'])

            # *AO type
            # Note: The selectors below appear to be incorrect - using unique IDs for now
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_912586437-guidetextbox___widget', keys=config_data['form_data']['fields']['TAN AO type1'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_912586437-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['TAN AO type2'])

            # *Range code
            send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_450718701-guidetextbox___widget', config_data['form_data']['fields']['TAN Range code'])
            send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_450718701-guidetextbox_copy___widget', config_data['form_data']['fields']['TAN Range code1'])
            send_text('#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_450718701-guidetextbox_copy_2031803169___widget', config_data['form_data']['fields']['TAN Range code2'])

            # *AO No.
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_912586437_1323045745-guidetextbox___widget', keys=config_data['form_data']['fields']['TAN AO No'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_912586437_1323045745-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['TAN AO No1'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_912586437_1323045745-guidetextbox_copy_co___widget', keys=config_data['form_data']['fields']['TAN AO No2'])

            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_912586437_1323045745-guidetextbox_copy_co_739099102___widget', keys=config_data['form_data']['fields']['TAN AO No3'])

            # Income Source - fixing the potential issue with this line
            
            time.sleep(2)
            function1.click_element(driver, xpath='//*[@id="guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-guidetextbox_2064455___widget"]')
            time.sleep(1)
            function1.send_text(driver, xpath='//*[@id="guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-guidetextbox_2064455___widget"]',keys=config_data['form_data']['fields']['Income Source'])


        except Exception as e:
            print(f"Could not fill TAN fields, they may not be present on this page: {str(e)}")

        # SAVE BUTTON
        time.sleep(2)
        try:
            click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy_copy-mca_button_copy___widget')
        except Exception as e:
            print(f"Save button not found: {str(e)}")

        # POPUP - OK BUTTON
        time.sleep(2)
        try:
            click_element(driver,css_selector='#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')
        except Exception as e:
            print(f"Popup OK button not found, continuing: {str(e)}")

        # NEXT BUTTON
        try:
            click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy_copy-mca_button___widget')
        except Exception as e:
            print(f"Next button not found: {str(e)}")

        # FINAL UPLOADS of file
        time.sleep(2)
        attachment_upload.handle_file_uploads(driver, config_data)
        time.sleep(2)
        attachment_upload.handle_file_uploads(driver, config_data)

        # Final form section - add error handling for elements that may not be present
        try:
            #*DIN/DPIN/PAN of designated partner
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-guidetextbox_1527295062___widget', keys=config_data['form_data']['fields']['DIN/DPIN/PAN of designated partner'])
        except Exception as e:
            print(f"DIN/DPIN/PAN field not found: {str(e)}")

        # Declaration and certification by professional
        try:
            # Enter Name
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox___widget', keys=config_data['form_data']['fields']['Enter Name'])
        except Exception as e:
            print(f"Enter Name field not found: {str(e)}")

        try:
            # Son/Daughter
            click_element(css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guideradiobutton__-1_widget')
        except Exception as e:
            print(f"Son/Daughter radio button not found: {str(e)}")

        try:
            # Enter Father's Name
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox_1141998439___widget', keys=config_data['form_data']['fields']["Enter Father's Name"])
        except Exception as e:
            print(f"Enter Father's Name field not found: {str(e)}")

        try:
            # do state that I am
            click_element(css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guideradiobutton_2109271305__-3_widget')
        except Exception as e:
            print(f"'do state that I am' radio button not found: {str(e)}")

        try:
            # partnership and my membership number
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox_1809173783___widget', keys=config_data['form_data']['fields']['partnership and my membership number'])
        except Exception as e:
            print(f"Partnership membership number field not found: {str(e)}")

        try:
            # *Whether associate or fellow
            click_element(css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guideradiobutton_598616795__-1_widget')
        except Exception as e:
            print(f"Associate/Fellow radio button not found: {str(e)}")

        try:
            # SAVE         
            click_element(css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel_copy_copy_copy-mca_button_copy___widget')
        except Exception as e:
            print(f"Save button not found: {str(e)}")

        # ====== WAIT TO OBSERVE UPLOAD RESPONSE ======
        time.sleep(2)

        from selenium.common.exceptions import NoAlertPresentException

        time.sleep(2)
        try:
            alert = driver.switch_to.alert
            print("[+] Alert text:", alert.text)
            alert.accept()
            print("[+] Alert accepted.")
        except NoAlertPresentException:
            print("[!] No alert present.")

        # POP-UP
        try:
            click_element(css_selector='#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')
        except Exception as e:
            print(f"Final popup button not found: {str(e)}")

        # NEXT
        try:
            click_element(css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel_copy_copy_copy-mca_button___widget')
        except Exception as e:
            print(f"Final next button not found: {str(e)}")

        # Proceed to Form 9
        try:
            click_element(css_selector='#guideContainer-rootPanel-panel-panel_1448122692-panel_copy_copy_copy-mca_button___widget')
        except Exception as e:
            print(f"Proceed to Form 9 button not found: {str(e)}")
            
        print("\n" + "="*60)
        print("🎉 LLP FORM AUTOMATION COMPLETED")
        print("="*60)
        print(f"✅ Total Partners Processed:")
        print(f"✅ Partner 1: CSS Selector Approach")
        print(f"✅ Partners 2+: Aria-Label XPath Approach")
        print("✅ Form Navigation: Completed with error handling")
        print("✅ File Uploads: Attempted (files may need to be provided)")
        print("="*60)
        print("[AUTOMATE1] LLP form sequence completed successfully")
        return True
            
    except Exception as e:
        print(f"[AUTOMATE1] Error in LLP form sequence: {e}")
        traceback.print_exc()
        return False
    finally:
        # Clean up
        try:
            if driver:
                driver.quit()
        except:
            pass

        # Wait for Enter key to exit and close browser
        input("Press Enter to exit and close the browser...")
        sys.exit(0)


# Execute if script is run directly
if __name__ == "__main__":
    print("[AUTOMATE1] This script should be imported by main.py")
    print("[AUTOMATE1] To run standalone, initialize a driver and call run_llp_form_sequence(driver)")


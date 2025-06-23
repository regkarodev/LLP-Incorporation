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
import partners_without_din, bodies_corporate_with_din, bodies_corporate_without_din, document_upload_file
from function1 import scroll_into_view, send_text, click_element, click_button

# Global driver variable
driver = None 

def setup_driver(webdriver_instance):
    """Set up the driver for this module"""
    global driver
    driver = webdriver_instance
    return driver

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
            with open("config_data.json", "r") as f:
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

        with open('config_data.json', 'r') as f:
            config_selectors = json.load(f)

        # Begin the form sequence
        print("[AUTOMATE1] Starting LLP form sequence...")
        
        # Add periodic session checks
        check_interval = 10  # Check every 10 operations
        operation_count = 0
        
        # Registrar of Companies
        time.sleep(2)
        click_element(driver, css_selector='#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy-panel1626772568950-guideradiobutton__-1_widget')

        # Service Request Number
        send_text(driver, css_selector='#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy-panel1626772568950-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['Service Request Number'])

        # Type of incorporation
        time.sleep(2)
        click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy-panel1626772568950-guideradiobutton_1069538009__-1_widget')


        # SAVE AND CONTINUE BUTTON 
        time.sleep(2)
        click_button(driver, '#guideContainer-rootPanel-panel-panel-panel-panel_copy_copy_copy-mca_button___widget')

        # OK POP_UP BUTTON
        time.sleep(2)
        try:
            click_button(driver, '#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')
        except Exception as e:
            print(f"[ERROR] Failed to click MCA button: {str(e)}")
            # Try alternative selector if the first one fails
            try:
                click_button(driver, 'button[aria-label="MCA"]')
            except Exception as e2:
                print(f"[ERROR] Failed to click MCA button with alternative selector: {str(e2)}")
                raise

        # NEXT BUTTON
        time.sleep(2)
        click_button(driver, '#guideContainer-rootPanel-panel-panel-panel_copy_copy_copy_1792429032-mca_button___widget')

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


        ## (c) Attachments
        
        # Upload files using JavaScript override for attachments
        time.sleep(2)
        file_path = config_data['form_data']['file_paths']['first_file']

        # Locator for the hidden input type="file" element
        file_input_element_id = "guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_copy-fileuploadwithplaceh__"

        # Call the updated send_file function
        print("Attempting to upload file...")
        upload_successful = document_upload_file.handle_file_upload(
            driver,
            file_input_element_id,
            file_path,            
            timeout=30
        )
        if upload_successful:
            print(f"File '{file_path}' upload process initiated successfully.")
            # Add further assertions here to validate the upload, e.g., check for success message [1]
        else:
            print(f"File '{file_path}' upload process failed.")
        
        click_element(
            driver,
            css_selector="#guideContainer-rootPanel-modal_container_131700874-guidebutton___widget"
        )
        



        # ---  *Copy of the utility bills (not older than two months) ---
        time.sleep(2)
        file_path = config_data['form_data']['file_paths']['second_file']

        # Locator for the hidden input type="file" element
        file_input_element_id = "guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_copy-fileuploadwithplaceh_376676005__"

        # Call the updated send_file function
        print("Attempting to upload file...")
        upload_successful = document_upload_file.handle_file_upload(
            driver,
            file_input_element_id,
            file_path,
            timeout=30
        )
        if upload_successful:
            print(f"File '{file_path}' upload process initiated successfully.")
            # Add further assertions here to validate the upload, e.g., check for success message [1]
        else:
            print(f"File '{file_path}' upload process failed.")
        

        click_element(
            driver,
            css_selector="#guideContainer-rootPanel-modal_container_131700874-guidebutton___widget"
        )
        


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
            wait = WebDriverWait(driver, 20)

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
        partners_without_din.handle_partners_without_din(driver, config_data)
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
            click_button(driver, '#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel_copy_copy_copy-mca_button_copy___widget')
        except Exception as e:
            print(f"Save button not found: {str(e)}")

        # POPUP - OK BUTTON
        time.sleep(2)
        try:
            click_button(driver, '#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')
        except Exception as e:
            print(f"Popup OK button not found, continuing: {str(e)}")

        # NEXT BUTTON
        time.sleep(2)
        try:
            click_button(driver, '#guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel_copy_copy_copy-mca_button___widget')
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
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_912586437-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['PAN AO type1'])

            # *Range code
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_450718701-guidetextbox___widget', keys=config_data['form_data']['fields']['PAN Range code'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_450718701-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['PAN Range code1'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_450718701-guidetextbox_copy_2031803169___widget', keys=config_data['form_data']['fields']['PAN Range code2'])

            # *AO No.
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_912586437_1323045745-guidetextbox___widget', keys=config_data['form_data']['fields']['PAN AO No.'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_912586437_1323045745-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['PAN AO No1'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_912586437_1323045745-guidetextbox_copy_co___widget', keys=config_data['form_data']['fields']['PAN AO No2'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_969275493-panel_copy_912586437_1323045745-guidetextbox_copy_co_1184221772___widget', keys=config_data['form_data']['fields']['PAN AO No3'])

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
            time.sleep(2)
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_450718701-guidetextbox___widget', keys=config_data['form_data']['fields']['TAN Range code'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_450718701-guidetextbox_copy___widget', keys=config_data['form_data']['fields']['TAN Range code1'])
            send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy-panel-panel_copy-panel_copy-panel_969275493_copy-panel_copy_450718701-guidetextbox_copy_2031803169___widget', keys=config_data['form_data']['fields']['TAN Range code2'])

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
            click_button(driver, '#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy_copy-mca_button_copy___widget')
        except Exception as e:
            print(f"Save button not found: {str(e)}")

        # POPUP - OK BUTTON
        time.sleep(2)
        try:
            click_button(driver, '#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')
        except Exception as e:
            print(f"Popup OK button not found, continuing: {str(e)}")

        # NEXT BUTTON
        time.sleep(2)
        try:
            click_button(driver, '#guideContainer-rootPanel-panel-panel_358466187-panel-panel_copy_copy_copy-mca_button___widget')
        except Exception as e:
            print(f"Next button not found: {str(e)}")

        # FINAL UPLOADS of file
        # Upload files using JavaScript override for attachments
        time.sleep(2)
        file_path = config_data['form_data']['file_paths']['third_file']

        # Locator for the hidden input type="file" element
        file_input_element_id = "guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-mca_custom_multifile__"

        # Call the updated send_file function
        print("Attempting to upload file...")
        upload_successful = attachment_upload.handle_file_upload(
            driver,
            file_input_element_id,
            file_path,            
            timeout=30
        )
        if upload_successful:
            print(f"File '{file_path}' upload process initiated successfully.")
            # Add further assertions here to validate the upload, e.g., check for success message [1]
        else:
            print(f"File '{file_path}' upload process failed.")
        
        click_element(
            driver,
            css_selector="#guideContainer-rootPanel-modal_container_131700874-guidebutton___widget"
        )
        



        # ---  *Copy of the utility bills (not older than two months) ---
        time.sleep(2)
        file_path = config_data['form_data']['file_paths']['fourth_file']

        # Locator for the hidden input type="file" element
        file_input_element_id = "guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-mca_custom_file_uplo__"

        # Call the updated send_file function
        print("Attempting to upload file...")
        upload_successful = attachment_upload.handle_file_upload(
            driver,
            file_input_element_id,
            file_path,
            timeout=30
        )
        if upload_successful:
            print(f"File '{file_path}' upload process initiated successfully.")
            # Add further assertions here to validate the upload, e.g., check for success message [1]
        else:
            print(f"File '{file_path}' upload process failed.")
        

        click_element(
            driver,
            css_selector="#guideContainer-rootPanel-modal_container_131700874-guidebutton___widget"
        )
        

        # Final form section - add error handling for elements that may not be present
        # Final form section - add error handling for elements that may not be present
        time.sleep(1)
        #*DIN/DPIN/PAN of designated partner
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-guidetextbox_1527295062___widget', keys=config_data['form_data']['fields']['DIN/DPIN/PAN of designated partner'])
        print("DIN/DPIN/PAN of designated partner field filled successfully")

        # Declaration and certification by professional
        time.sleep(1)

        send_text(driver, css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox___widget', keys=config_data['form_data']['fields']['Enter Name'])
        print("Enter Name field filled successfully")

        time.sleep(1)

        # Son/Daughter
        click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guideradiobutton__-1_widget')
        print("Son/Daughter radio button clicked successfully")


        # Enter Father's Name
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox_1141998439___widget', keys=config_data['form_data']['fields']["Enter Father's Name"])
        print("Enter Father's Name field filled successfully")



            # do state that I am
        click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guideradiobutton_2109271305__-3_widget')
        print("do state that I am radio button clicked successfully")


        # partnership and my membership number
        time.sleep(1)
        send_text(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guidetextbox_1809173783___widget', keys=config_data['form_data']['fields']['partnership and my membership number'])
        print("Partnership membership number field filled successfully")



            # *Whether associate or fellow
        click_element(driver,css_selector='#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel-panel_1137005940_cop-guideradiobutton_598616795__-1_widget')
        print("Associate/Fellow radio button clicked successfully")


            # SAVE 
        time.sleep(1)        
        print("save button before clicked")
        click_button(driver, '#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel_copy_copy_copy-mca_button_copy___widget')
        print("save button clicked successfully")
            
        # POP-UP
        time.sleep(1)   
        click_button(driver, '#guideContainer-rootPanel-modal_container_copy-panel_86338280-panel-mca_button___widget')
        print("popup button clicked successfully")

        # NEXT
        time.sleep(1)   
        click_button(driver, '#guideContainer-rootPanel-panel-panel_1696210624-panel_1548670294-panel_copy_copy_copy-mca_button___widget')
        print("Next button clicked successfully")


        # Proceed to Form 9
        click_element(driver, css_selector='#guideContainer-rootPanel-panel-panel_1448122692-panel_copy_copy_copy-mca_button___widget')
        
        # --- Form 9 ---
        time.sleep(1)
        click_button(driver, '#guideContainer-rootPanel-modal_container-panel-guidebutton___widget')

        time.sleep(1)
        click_button(driver, '#guideContainer-rootPanel-panel-mca_button___widget')

        time.sleep(1)
        click_button(driver, '#guideContainer-rootPanel-panel_1029056258-mca_button_814968004___widget')

        time.sleep(2)








    except Exception as e:
        print(f"[AUTOMATE1] Error in LLP form sequence: {e}")
        traceback.print_exc()
        return False


    # Wait for Enter key to exit and close browser
    input("Press Enter to exit and close the browser...")
    sys.exit(0)


# Execute if script is run directly
if __name__ == "__main__":
    print("[AUTOMATE1] This script should be imported by main.py")
    print("[AUTOMATE1] To run standalone, initialize a driver and call run_llp_form_sequence(driver)")


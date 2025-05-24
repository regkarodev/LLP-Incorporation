import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fill_designated_partners_form(driver):
    """
    Fill designated partners section dynamically using XPath with position indexing
    """
    try:
        # Load configuration files
        with open('config_data.json', 'r') as f:
            config_data = json.load(f)
        
        with open('config.json', 'r') as f:
            config_selectors = json.load(f)
        
        # Get number of partners from config
        num_partners = int(config_data['form_data']['fields'].get('Individuals Having valid DIN/DPIN', 0))
        
        if num_partners < 1:
            print('No designated partners with DIN/DPIN to fill.')
            return True
        
        if num_partners > 5:
            print('Warning: Maximum 5 designated partners allowed. Only filling 5.')
            num_partners = 5
        
        # Get partner data from config_data
        designated_partners = config_data['form_data'].get('designated_partners', None)
        if not designated_partners:
            # Check under options
            designated_partners = config_data['form_data'].get('options', {}).get('designated_partners', None)
        
        if not designated_partners:
            print("Warning: No designated_partners array found in config_data.json")
            # Use the same data for all partners as fallback
            designated_partners = [config_data['form_data']['fields']] * num_partners
        
        print(f"Filling forms for {num_partners} designated partner(s)")
        
        # Wait for the form to be ready
        time.sleep(2)
        
        # Fill each partner's details
        for idx in range(num_partners):
            position = idx + 1  # XPath uses 1-based indexing
            print(f"\n--- Filling Partner {position} ---")
            
            partner = designated_partners[idx] if idx < len(designated_partners) else designated_partners[0]
            
            # For the first partner, try the direct ID selectors first
            if idx == 0:
                try:
                    selectors_list = config_selectors.get('Basic details', {}).get('form1', [])
                    if selectors_list and len(selectors_list) > 0:
                        selectors = selectors_list[0]
                        fields_filled = fill_with_selectors(driver, selectors, partner)
                        if fields_filled > 0:
                            print(f"Successfully filled {fields_filled} fields for partner 1 using config selectors")
                            continue
                except Exception as e:
                    print(f"Config selectors failed for partner 1, falling back to XPath: {str(e)}")
            
            # Use XPath with position indexing for all partners (including first if config failed)
            fill_partner_by_xpath(driver, partner, position)
            
            # Small delay between partners
            time.sleep(1)
        
        print("\nCompleted filling all designated partners")
        return True
        
    except Exception as e:
        print(f"Error in fill_designated_partners_form: {e}")
        import traceback
        traceback.print_exc()
        return False

def fill_partner_by_xpath(driver, partner_data, position):
    """Fill partner fields using XPath with position indexing"""
    print(f"Using XPath approach for partner {position}")
    
    # Fill DIN/DPIN
    try:
        din_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Designated partner identification number (DIN/DPIN)'])[{position}]")
        din_element.clear()
        din_element.send_keys(partner_data.get('Designated partner identification number (DIN/DPIN)', ''))
        print(f"  ✓ Filled DIN for partner {position}")
    except Exception as e:
        print(f"  ✗ Could not fill DIN for partner {position}: {str(e)}")
    
    # Click resident radio if applicable
    if partner_data.get('Whether resident of India', '').lower() == 'yes':
        try:
            # Try exact match first
            resident_radio = driver.find_element(By.XPATH, f"(//input[@aria-label='Whether resident of India'])[{position}]")
            resident_radio.click()
            print(f"  ✓ Selected resident of India for partner {position}")
        except:
            # Try partial match
            try:
                resident_radio = driver.find_element(By.XPATH, f"(//*[contains(@aria-label, 'resident of India')])[{position}]")
                resident_radio.click()
                print(f"  ✓ Selected resident of India for partner {position}")
            except Exception as e:
                print(f"  ✗ Could not select resident radio for partner {position}: {str(e)}")
    
    # Fill Form of contribution
    try:
        contribution_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Form of contribution'])[{position}]")
        contribution_value = partner_data.get('Form of contribution', '')
        contribution_element.click()
        time.sleep(0.5)
        contribution_element.send_keys(contribution_value)
        print(f"  ✓ Filled contribution type: {contribution_value}")
        
        # Handle "Other than cash" specification
        if contribution_value.lower() == 'other than cash':
            try:
                spec_element = driver.find_element(By.XPATH, f"(//*[contains(@aria-label, 'please specify')])[{position}]")
                spec_element.clear()
                spec_element.send_keys(partner_data.get("If 'Other than cash' selected, please specify", ''))
                print(f"  ✓ Filled 'Other than cash' specification")
            except Exception as e:
                print(f"  ✗ Could not fill 'Other than cash' specification: {str(e)}")
    except Exception as e:
        print(f"  ✗ Could not fill contribution: {str(e)}")
    
    # Fill Monetary value
    try:
        monetary_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Monetary value of contribution (in INR) (in figures)'])[{position}]")
        monetary_element.clear()
        monetary_element.send_keys(partner_data.get('Monetary value of contribution (in INR) (in figures)', ''))
        print(f"  ✓ Filled monetary value")
    except Exception as e:
        print(f"  ✗ Could not fill monetary value: {str(e)}")
    
    # Fill Number of LLPs
    try:
        llp_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Number of LLP(s) in which he/ she is a partner'])[{position}]")
        llp_element.clear()
        llp_element.send_keys(partner_data.get('Number of LLP(s) in which he/ she is a partner', ''))
        print(f"  ✓ Filled LLP count")
    except Exception as e:
        print(f"  ✗ Could not fill LLP count: {str(e)}")
    
    # Fill Number of companies
    try:
        company_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Number of company(s) in which he/ she is a director'])[{position}]")
        company_element.clear()
        company_element.send_keys(partner_data.get('Number of company(s) in which he/ she is a director', ''))
        print(f"  ✓ Filled company count")
    except Exception as e:
        print(f"  ✗ Could not fill company count: {str(e)}")

def fill_with_selectors(driver, selectors, partner_data):
    """Helper function to fill fields using config selectors"""
    fields_filled = 0
    
    # Map field names
    field_mapping = {
        'Designated partner identification number (DIN/DPIN)': 'Designated partner identification number (DIN/DPIN)',
        'resident_india': 'Whether resident of India',
        'form_of_contribution': 'Form of contribution',
        'monetary_value_of_contribution': 'Monetary value of contribution (in INR) (in figures)',
        'number_of_llp': 'Number of LLP(s) in which he/ she is a partner',
        'number_of_company': 'Number of company(s) in which he/ she is a director',
        "If 'Other than cash' selected, please specify": "If 'Other than cash' selected, please specify"
    }
    
    for field, selector in selectors.items():
        actual_field = field_mapping.get(field, field)
        value = partner_data.get(actual_field)
        
        if value is not None:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if field == 'resident_india' and str(value).lower() == 'yes':
                    element.click()
                else:
                    element.clear()
                    element.send_keys(str(value))
                fields_filled += 1
            except:
                pass
    
    return fields_filled

if __name__ == "__main__":
    # Example usage
    from selenium import webdriver
    driver = webdriver.Firefox()  # or Chrome()
    
    # Navigate to your form first
    # driver.get("YOUR_FORM_URL")
    
    # Fill the designated partners
    success = fill_designated_partners_form(driver)
    
    if success:
        print("\nDesignated partners filled successfully!")
    else:
        print("\nFailed to fill designated partners")
    
    input("Press Enter to close browser...")
    driver.quit() 
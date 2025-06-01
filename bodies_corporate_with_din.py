from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def fill_dropdown(driver, element, value):
    try:
        Select(element).select_by_visible_text(value)
    except:
        print(f"Dropdown value '{value}' not found. Trying manual input.")
        element.send_keys(value)

def fill_input(element, value):
    if value:
        element.clear()
        element.send_keys(value)

def upload_file(element, file_path):
    if os.path.exists(file_path):
        element.send_keys(os.path.abspath(file_path))
    else:
        print(f"File not found: {file_path}")

def wait_and_find(driver, by, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))

def fill_bodies_corporate_designated_partners(driver, data):
    partners = data.get("bodies_corporate_designated_partners", [])
    
    for index, partner in enumerate(partners):
        print(f"Filling subform {index + 1} of {len(partners)}")

        # Scope subform: this assumes each subform has a repeatable container (update the XPath/CSS accordingly)
        subform_xpath = f"(//div[contains(@class, 'body-corporate-subform')])[{index + 1}]"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, subform_xpath)))
        subform = driver.find_element(By.XPATH, subform_xpath)

        # (i) Body Corporate Details
        fill_dropdown(subform.find_element(By.NAME, "corporateType"), partner["corporate_type"])
        fill_input(subform.find_element(By.NAME, "registrationNumber"), partner["registration_number"])
        fill_input(subform.find_element(By.NAME, "pan"), partner["pan"])
        fill_input(subform.find_element(By.NAME, "corporateName"), partner["corporate_name"])

        # Address
        address = partner["address"]
        fill_input(subform.find_element(By.NAME, "addressLine1"), address["line1"])
        fill_input(subform.find_element(By.NAME, "addressLine2"), address["line2"])
        fill_dropdown(subform.find_element(By.NAME, "country"), address["country"])
        fill_input(subform.find_element(By.NAME, "pincode"), address["pincode"])
        fill_input(subform.find_element(By.NAME, "area"), address["area"])
        fill_input(subform.find_element(By.NAME, "city"), address["city"])
        fill_input(subform.find_element(By.NAME, "district"), address["district"])
        fill_dropdown(subform.find_element(By.NAME, "state"), address["state"])
        fill_input(subform.find_element(By.NAME, "jurisdiction"), address["jurisdiction"])

        # Contact
        contact = partner["contact"]
        fill_input(subform.find_element(By.NAME, "phone"), contact["phone"])
        fill_input(subform.find_element(By.NAME, "mobile"), contact["mobile"])
        if contact.get("fax"):
            fill_input(subform.find_element(By.NAME, "fax"), contact["fax"])
        fill_input(subform.find_element(By.NAME, "email"), contact["email"])

        # Conversion (optional)
        conv = partner.get("conversion_details", {})
        if conv.get("shares_held"):
            fill_input(subform.find_element(By.NAME, "sharesHeld"), conv["shares_held"])
        if conv.get("share_value"):
            fill_input(subform.find_element(By.NAME, "shareValue"), conv["share_value"])

        # (ii) Contribution
        contrib = partner["contribution"]
        fill_dropdown(subform.find_element(By.NAME, "contributionForm"), contrib["form"])
        if contrib["form"].lower() != "cash":
            fill_input(subform.find_element(By.NAME, "otherSpecify"), contrib["other_specify"])
        fill_input(subform.find_element(By.NAME, "valueFigures"), contrib["value_figures"])
        fill_input(subform.find_element(By.NAME, "valueWords"), contrib["value_words"])
        fill_input(subform.find_element(By.NAME, "llpCount"), str(contrib["llp_count"]))
        fill_input(subform.find_element(By.NAME, "companyCount"), str(contrib["company_count"]))

        # (iii) Nominee
        nominee = partner["nominee"]
        fill_input(subform.find_element(By.NAME, "nomineeDIN"), nominee["din"])
        fill_input(subform.find_element(By.NAME, "nomineeName"), nominee["name"])
        fill_dropdown(subform.find_element(By.NAME, "nomineeResident"), nominee["resident"])
        fill_input(subform.find_element(By.NAME, "nomineeDesignation"), nominee["designation"])

        # Upload resolution and authorization
        upload_file(subform.find_element(By.NAME, "resolutionUpload"), nominee["resolution_upload_path"])
        upload_file(subform.find_element(By.NAME, "authorizationUpload"), nominee["authorization_upload_path"])

        time.sleep(1)  # Optional wait between subforms

    print("✅ Finished filling all body corporate subforms.")

def handle_bodies_corporate_with_din(driver, config_data, config_selectors):
    """
    Handle the section for bodies corporate with DIN in the MCA LLP form.
    
    Args:
        driver: Selenium WebDriver instance
        config_data: Dictionary containing form data
        config_selectors: Dictionary containing CSS selectors
    """
    try:
        # Get the number of bodies corporate from config
        num_bodies = int(config_data['form_data']['fields'].get('Bodies Corporate having valid DIN/DPIN', 0))
        if num_bodies == 0:
            print("[INFO] No bodies corporate with DIN/DPIN to process")
            return

        print(f"[INFO] Processing {num_bodies} bodies corporate with DIN/DPIN")
        
        # Get bodies corporate data from config
        bodies_data = config_data.get('bodies_corporate_designated_partners', [])
        if not bodies_data:
            print("[WARNING] No bodies corporate data found in config")
            return

        # Process each body corporate
        for idx in range(num_bodies):
            position = idx + 1  # XPath is 1-based
            if idx < len(bodies_data):
                body = bodies_data[idx]
            else:
                print(f"[WARNING] No data found for body corporate {position}")
                continue

            print(f"\n[INFO] Filling details for body corporate {position}")
            fields_filled_count = 0
            fields_failed_count = 0

            try:
                # Wait for the subform to be visible
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements(By.XPATH, f"(//input[@aria-label='Body Corporate Name'])[{position}]")) > 0
                )

                # Fill the form using the existing helper function
                fill_bodies_corporate_designated_partners(driver, config_data)
                print(f"[SUCCESS] Completed filling details for body corporate {position}")
                fields_filled_count += 1

            except Exception as e:
                print(f"[ERROR] Failed to fill details for body corporate {position}: {str(e)}")
                fields_failed_count += 1
                continue

            # Add a small delay between bodies corporate
            time.sleep(1)

        print("[SUCCESS] Completed processing all bodies corporate with DIN/DPIN")

    except Exception as e:
        print(f"[ERROR] Failed to process bodies corporate with DIN/DPIN: {str(e)}")
        raise

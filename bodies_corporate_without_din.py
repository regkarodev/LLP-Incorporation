from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime
from selenium.common.exceptions import TimeoutException

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

def fill_radio(driver, label, value):
    try:
        radio = driver.find_element(By.XPATH, f"//label[contains(text(), '{label}')]/following-sibling::input[@type='radio' and @value='{value}']")
        radio.click()
    except:
        print(f"Radio button not found for {label} with value {value}")

def upload_file(element, file_path):
    if os.path.exists(file_path):
        element.send_keys(os.path.abspath(file_path))
    else:
        print(f"File not found: {file_path}")

def fill_date(element, date_str):
    try:
        # Convert date string to DD/MM/YYYY format
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d/%m/%Y")
        element.clear()
        element.send_keys(formatted_date)
    except Exception as e:
        print(f"Error filling date: {str(e)}")

def fill_address(driver, address_data, prefix=""):
    """Helper function to fill address fields"""
    fill_input(driver.find_element(By.NAME, f"{prefix}addressLine1"), address_data["line1"])
    fill_input(driver.find_element(By.NAME, f"{prefix}addressLine2"), address_data["line2"])
    fill_dropdown(driver.find_element(By.NAME, f"{prefix}country"), address_data["country"])
    fill_input(driver.find_element(By.NAME, f"{prefix}pincode"), address_data["pincode"])
    fill_input(driver.find_element(By.NAME, f"{prefix}area"), address_data["area"])
    fill_input(driver.find_element(By.NAME, f"{prefix}city"), address_data["city"])
    fill_input(driver.find_element(By.NAME, f"{prefix}district"), address_data["district"])
    fill_dropdown(driver.find_element(By.NAME, f"{prefix}state"), address_data["state"])
    fill_input(driver.find_element(By.NAME, f"{prefix}jurisdiction"), address_data["jurisdiction"])
    if address_data.get("phone"):
        fill_input(driver.find_element(By.NAME, f"{prefix}phone"), address_data["phone"])

def fill_bodies_corporate_nominee_no_din(driver, data):
    """Main function to fill Section D forms"""
    try:
        partners = data.get("bodies_corporate_nominee_no_din", [])
        if not partners:
            print("[INFO] No bodies corporate without DIN to process")
            return

        print(f"[INFO] Processing {len(partners)} bodies corporate without DIN")
        
        # Wait for the form section to be visible
        try:
            # Wait for any element that indicates the form is loaded
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'guideContainer')]"))
            )
            print("[INFO] Form container found")
        except TimeoutException:
            print("[ERROR] Form container not found after 20 seconds")
            return

        for index, partner in enumerate(partners):
            position = index + 1
            print(f"\n[INFO] Filling details for body corporate {position}")
            
            try:
                # Wait for the form to be interactive
                time.sleep(2)  # Give time for dynamic content to load
                
                # Try to find the first field with multiple strategies
                first_field = None
                field_xpaths = [
                    f"(//input[@aria-label='Body Corporate Name'])[{position}]",
                    f"(//input[contains(@aria-label, 'Corporate Name')])[{position}]",
                    f"(//input[contains(@placeholder, 'Corporate Name')])[{position}]"
                ]
                
                for xpath in field_xpaths:
                    try:
                        first_field = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        if first_field:
                            print(f"[INFO] Found first field using XPath: {xpath}")
                            break
                    except:
                        continue
                
                if not first_field:
                    print(f"[ERROR] Could not find any input field for position {position}")
                    continue

                # Make sure the field is visible and interactable
                driver.execute_script("""
                    arguments[0].scrollIntoView({block: 'center'});
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                    arguments[0].style.opacity = '1';
                """, first_field)
                time.sleep(1)

                # (i) Body Corporate Details
                corp = partner["corporate_details"]
                
                # Corporate Type
                try:
                    corp_type_xpath = f"(//select[@aria-label='Body Corporate Type'])[{position}]"
                    corp_type = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, corp_type_xpath))
                    )
                    fill_dropdown(driver, corp_type, corp["type"])
                    print("[SUCCESS] Filled Corporate Type")
                except Exception as e:
                    print(f"[ERROR] Failed to fill Corporate Type: {str(e)}")
                
                # Registration Number
                try:
                    reg_num_xpath = f"(//input[@aria-label='Registration Number'])[{position}]"
                    reg_num = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, reg_num_xpath))
                    )
                    fill_input(reg_num, corp["registration_number"])
                    print("[SUCCESS] Filled Registration Number")
                except Exception as e:
                    print(f"[ERROR] Failed to fill Registration Number: {str(e)}")
                
                # PAN
                try:
                    pan_xpath = f"(//input[@aria-label='PAN'])[{position}]"
                    pan = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, pan_xpath))
                    )
                    fill_input(pan, corp["pan"])
                    print("[SUCCESS] Filled PAN")
                except Exception as e:
                    print(f"[ERROR] Failed to fill PAN: {str(e)}")
                
                # Corporate Name
                try:
                    name_xpath = f"(//input[@aria-label='Body Corporate Name'])[{position}]"
                    name = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, name_xpath))
                    )
                    fill_input(name, corp["name"])
                    print("[SUCCESS] Filled Corporate Name")
                except Exception as e:
                    print(f"[ERROR] Failed to fill Corporate Name: {str(e)}")

                # Address
                fill_address(driver, corp["address"])

                # Contact
                contact = corp["contact"]
                fill_input(driver.find_element(By.NAME, "phone"), contact["phone"])
                fill_input(driver.find_element(By.NAME, "mobile"), contact["mobile"])
                if contact.get("fax"):
                    fill_input(driver.find_element(By.NAME, "fax"), contact["fax"])
                fill_input(driver.find_element(By.NAME, "email"), contact["email"])

                # Conversion (optional)
                conv = corp.get("conversion", {})
                if conv.get("shares_held"):
                    fill_input(driver.find_element(By.NAME, "sharesHeld"), conv["shares_held"])
                if conv.get("share_value"):
                    fill_input(driver.find_element(By.NAME, "shareValue"), conv["share_value"])

                # (ii) Contribution
                contrib = partner["contribution"]
                fill_dropdown(driver.find_element(By.NAME, "contributionForm"), contrib["form"])
                if contrib["form"].lower() != "cash":
                    fill_input(driver.find_element(By.NAME, "otherSpecify"), contrib["other_specify"])
                fill_input(driver.find_element(By.NAME, "valueFigures"), contrib["value_figures"])
                fill_input(driver.find_element(By.NAME, "valueWords"), contrib["value_words"])
                fill_input(driver.find_element(By.NAME, "llpCount"), str(contrib["llp_count"]))
                fill_input(driver.find_element(By.NAME, "companyCount"), str(contrib["company_count"]))

                # (iii) Nominee Details
                nominee = partner["nominee"]
                
                # Personal Info
                fill_input(driver.find_element(By.NAME, "firstName"), nominee["first_name"])
                fill_input(driver.find_element(By.NAME, "middleName"), nominee["middle_name"])
                fill_input(driver.find_element(By.NAME, "surname"), nominee["surname"])
                fill_input(driver.find_element(By.NAME, "fatherFirstName"), nominee["father_first"])
                fill_input(driver.find_element(By.NAME, "fatherMiddleName"), nominee["father_middle"])
                fill_input(driver.find_element(By.NAME, "fatherSurname"), nominee["father_surname"])
                fill_dropdown(driver.find_element(By.NAME, "gender"), nominee["gender"])
                fill_date(driver.find_element(By.NAME, "dob"), nominee["dob"])
                fill_input(driver.find_element(By.NAME, "nationality"), nominee["nationality"])
                fill_radio(driver, "Whether resident in India", nominee["resident"])
                
                # PAN/Passport
                if nominee.get("pan"):
                    fill_input(driver.find_element(By.NAME, "pan"), nominee["pan"])
                elif nominee.get("passport"):
                    fill_input(driver.find_element(By.NAME, "passport"), nominee["passport"])
                    
                fill_input(driver.find_element(By.NAME, "birthState"), nominee["birth_state"])
                fill_input(driver.find_element(By.NAME, "birthDistrict"), nominee["birth_district"])
                fill_radio(driver, "Whether Citizen of India", nominee["citizen"])

                # Occupation & Education
                fill_dropdown(driver.find_element(By.NAME, "occupationType"), nominee["occupation_type"])
                if nominee["occupation_type"].lower() == "other":
                    fill_input(driver.find_element(By.NAME, "occupationOther"), nominee["occupation_other"])
                fill_dropdown(driver.find_element(By.NAME, "education"), nominee["education"])
                if nominee["education"].lower() == "other":
                    fill_input(driver.find_element(By.NAME, "educationOther"), nominee["education_other"])

                # Contact Info
                fill_input(driver.find_element(By.NAME, "nomineeMobile"), nominee["mobile"])
                fill_input(driver.find_element(By.NAME, "nomineeEmail"), nominee["email"])

                # Permanent Address
                fill_address(driver, nominee["permanent_address"], "permanent")

                # Present Address
                fill_radio(driver, "Whether same as Permanent", "Yes" if nominee["present_same"] else "No")
                if not nominee["present_same"]:
                    fill_address(driver, nominee["present_address"], "present")
                    fill_input(driver.find_element(By.NAME, "stayYears"), str(nominee["stay_duration"]["years"]))
                    fill_input(driver.find_element(By.NAME, "stayMonths"), str(nominee["stay_duration"]["months"]))

                # Identity & Residential Proof
                identity = nominee["identity_proof"]
                fill_dropdown(driver.find_element(By.NAME, "identityProofType"), identity["type"])
                fill_input(driver.find_element(By.NAME, "identityProofNumber"), identity["number"])

                residential = nominee["residential_proof"]
                fill_dropdown(driver.find_element(By.NAME, "residentialProofType"), residential["type"])
                fill_input(driver.find_element(By.NAME, "residentialProofNumber"), residential["number"])

                # File Uploads
                uploads = nominee["uploads"]
                upload_file(driver.find_element(By.NAME, "identityProofUpload"), uploads["identity_proof_path"])
                upload_file(driver.find_element(By.NAME, "residentialProofUpload"), uploads["residential_proof_path"])
                upload_file(driver.find_element(By.NAME, "resolutionPartnerUpload"), uploads["resolution_partner_path"])
                upload_file(driver.find_element(By.NAME, "resolutionNomineeUpload"), uploads["resolution_nominee_path"])

            except TimeoutException as e:
                print(f"[ERROR] Timeout waiting for subform {position}: {str(e)}")
                continue
            except Exception as e:
                print(f"[ERROR] Failed to fill details for body corporate {position}: {str(e)}")
                continue

            # Add a small delay between subforms
            time.sleep(2)

        print("[SUCCESS] Completed processing all bodies corporate without DIN")

    except Exception as e:
        print(f"[ERROR] Failed to process bodies corporate without DIN: {str(e)}")
        raise 
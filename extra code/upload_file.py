                # Educational qualification
                try:
                    education_value = partner.get('Educational qualification', '').strip()
                    if education_value:
                        education_xpath = f"(//select[@aria-label='Educational qualification'])[{position}]"
                        dropdown = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, education_xpath))
                        )

                        Select(dropdown).select_by_visible_text(education_value)
                        print(f"[SUCCESS] Selected Educational qualification: {education_value}")
                        fields_filled_count += 1
                    else:
                        print("[INFO] No educational qualification provided in data.")
                except Exception as e:
                    print(f"[ERROR] Failed to select 'Educational qualification': {e}")
                    fields_failed_count += 1



                # If 'Others' selected for education
                if partner.get('Educational qualification', '').lower() == 'others':
                    edu_others_xpath = f"(//input[@aria-label='If \'Others\' selected, please specify'])[{position}]"
                    driver.find_element(By.XPATH, edu_others_xpath).send_keys(partner.get('Educational qualification others', ''))



                # Area of Occupation
                # try:
                #     area = partner.get("Area of Occupation", "").strip()
                #     if area:
                #         # Wait for the Area of Occupation select element on the whole page
                #         area_select_elem = WebDriverWait(driver, 10).until(
                #             EC.presence_of_element_located((By.XPATH, '//select[@aria-label="Area of Occupation"]'))
                #         )
                #         select = Select(area_select_elem)
                #         select.select_by_visible_text(area)

                #         if select.first_selected_option.text == area:
                #             print(f"[SUCCESS] Filled: Area of Occupation = {area}")
                #             fields_filled_count += 1

                #             if area.lower() == "others":
                #                 try:
                #                     others_input = WebDriverWait(driver, 5).until(
                #                         EC.presence_of_element_located((By.XPATH, '//input[@aria-label="If \'Others\' selected, please specify"]'))
                #                     )
                #                     driver.execute_script("""
                #                         var input = arguments[0];
                #                         input.style.display = 'block';
                #                         input.style.visibility = 'visible';
                #                         input.style.opacity = '1';
                #                         input.removeAttribute('readonly');
                #                         input.removeAttribute('disabled');
                #                         input.removeAttribute('aria-readonly');
                #                     """, others_input)
                #                     driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", others_input)

                #                     description = partner.get("If Others selected, please specify", "").strip()
                #                     if description:
                #                         others_input.clear()
                #                         others_input.send_keys(description)

                #                         if others_input.get_attribute('value') == description:
                #                             print(f"[SUCCESS] Filled: If 'Others' selected, please specify = {description}")
                #                             fields_filled_count += 1
                #                         else:
                #                             print(f"[FAIL] Value mismatch in 'If Others selected' field")
                #                             fields_failed_count += 1
                #                     else:
                #                         print(f"[INFO] No value to specify for 'Others' selected")
                #                 except Exception as e:
                #                     print(f"[FAIL] Error filling 'If Others selected, please specify': {e}")
                #                     fields_failed_count += 1
                #         else:
                #             print(f"[FAIL] Selection mismatch for Area of Occupation = {area}")
                #             fields_failed_count += 1
                #     else:
                #         print(f"[INFO] No value provided for Area of Occupation")
                # except Exception as e:
                #     print(f"[FAIL] Error filling Area of Occupation: {e}")
                #     fields_failed_count += 1




                # # Occupation type
                # time.sleep(0.5)
                # occupation_xpath = f"(//select[@aria-label='Occupation type'])[{position}]"
                # Select(driver.find_element(By.XPATH, occupation_xpath)).select_by_visible_text(partner.get('Occupation type', ''))

                # # If 'Others' selected for occupation
                # if partner.get('Occupation type', '').lower() == 'others':
                #     others_xpath = f"(//input[@aria-label='Description of others'])[{position}]"
                #     driver.find_element(By.XPATH, others_xpath).send_keys(partner.get('Description of others', ''))



                                # Place of Birth (District)                
                # Position index, if you have multiple entries (else omit the index)
                # XPath for the select element at `position` (if multiple)





                                # Place of Birth (State)
                # birth_state_xpath = f"(//select[@aria-label='Place of Birth (State)'])[{position}]"
                # Select(driver.find_element(By.XPATH, birth_state_xpath)).select_by_visible_text(partner.get('Place of Birth (State)', ''))




                                    # PAN/Passport details
                    # Locate input field based on associated label text
                    # input_xpath = f"(//label[contains(text(), 'Income-tax PAN/Passport number details')]/following::input[@type='text'])[i]"
                    # input_element = WebDriverWait(driver, 10).until(
                    #     EC.element_to_be_clickable((By.XPATH, input_xpath))
                    # )
                    # input_element.clear()
                    # input_element.send_keys(partner.get('Income-tax PAN/Passport number details', ''))





                    try:
                        email_value = partner.get('Email ID', '').strip()
                        if email_value:
                            email_xpath = f"(//input[@aria-label='Email ID'])[{position}]"
                            email_input = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, email_xpath))
                            )
                            email_input.clear()
                            email_input.send_keys(email_value)
                            print(f"[SUCCESS] Entered Email ID: {email_value}")
                            fields_filled_count += 1
                        else:
                            print("[INFO] No Email ID provided in data.")
                    except Exception as e:
                        print(f"[ERROR] Failed to enter Email ID: {e}")
                        fields_failed_count += 1



# Contact Details

                try:

                    mobile_value = partner.get('Mobile No.', '').strip()

                    if mobile_value:

                        mobile_xpath = f"(//input[@aria-label='Mobile No.'])[{position}]"

                        mobile_input = WebDriverWait(driver, 10).until(

                            EC.presence_of_element_located((By.XPATH, mobile_xpath))

                        )



                        mobile_input.clear()

                        mobile_input.send_keys(mobile_value)

                        print(f"[SUCCESS] Entered Mobile No.: {mobile_value}")

                        fields_filled_count += 1

                    else:

                        print("[INFO] No Mobile No. provided in data.")

                except Exception as e:

                    print(f"[ERROR] Failed to enter Mobile No.: {e}")

                    fields_failed_count += 1





# Permanent Address
                perm_address1_xpath = f"(//input[@aria-label='Address Line I'])[{position}]"
                driver.find_element(By.XPATH, perm_address1_xpath).send_keys(partner.get('Permanent Address Line I', ''))



try:
                    # Construct the dynamic container XPath based on visible structure
                    container_xpath = "(//div[starts-with(@id, 'guideContainer-rootPanel') and contains(@id, 'guidetextbox_copy___guide-item')])"

                    # Use position to access the correct element
                    input_xpath = f"{container_xpath}//input[@aria-label='Address Line II'][{position}]"

                    # Wait until the input field is present in the DOM
                    input_elem = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, input_xpath))
                    )

                    # Unlock if hidden or disabled
                    driver.execute_script("""
                        var input = arguments[0];
                        input.style.display = 'block';
                        input.style.visibility = 'visible';
                        input.style.opacity = '1';
                        input.removeAttribute('readonly');
                        input.removeAttribute('disabled');
                        input.removeAttribute('aria-readonly');
                    """, input_elem)

                    # Scroll to element
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
                    time.sleep(0.5)

                    address_line2 = partner.get("Permanent Address Line II", "").strip()

                    if address_line2:
                        # Enforce 100 character max
                        if len(address_line2) > 100:
                            print(f"[WARNING] Address Line II exceeds max length (100): {address_line2}")
                            address_line2 = address_line2[:100]

                        input_elem.clear()
                        input_elem.send_keys(address_line2)
                        time.sleep(0.5)

                        if input_elem.get_attribute("value") == address_line2:
                            print(f"[SUCCESS] Filled: Address Line II = {address_line2}")
                            fields_filled_count += 1
                        else:
                            print(f"[FAIL] Address Line II value mismatch after sending keys")
                            fields_failed_count += 1
                    else:
                        print("[INFO] No value provided for Address Line II")

                except Exception as e:
                    print(f"[FAIL] Error handling Address Line II: {str(e)}")
                    fields_failed_count += 1


                            # Permanent Country
                perm_country_xpath = f"(//select[@aria-label='Country'])[{position}]"
                Select(driver.find_element(By.XPATH, perm_country_xpath)).select_by_visible_text(partner.get('Permanent Country', ''))




                # Permanent Pin code
                perm_pin_xpath = f"(//input[@aria-label='Pin code / Zip Code'])[{position}]"
                driver.find_element(By.XPATH, perm_pin_xpath).send_keys(partner.get('Permanent Pin code', ''))


                # Fill Area/ Locality
                try:
                    print("[DEBUG] Attempting to fill Area/Locality...")
                    time.sleep(2)  # Wait for any dynamic elements to load

                    # XPath for the select element from the second script
                    area_locality_xpath = '//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidedropdownlist_1592911853___widget"]'
                    
                    # Wait for the select element to be clickable
                    select_elem = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, area_locality_xpath))
                    )
                    print(f"[DEBUG] Found Area/Locality select element using XPath: {area_locality_xpath}")

                    # Make select element visible and interactive (using JavaScript execution from the second script)
                    driver.execute_script("""
                        arguments[0].style.display = 'block';
                        arguments[0].style.visibility = 'visible';
                        arguments[0].style.opacity = '1';
                        arguments[0].removeAttribute('disabled');
                    """, select_elem)

                    # Scroll the select element into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_elem)
                    time.sleep(0.5)  # Allow time for scrolling and element to be ready

                    # Get the area value using the key from the second script
                    area = partner.get('Permanent Area/Locality', '').strip()

                    if area:
                        print(f"[DEBUG] Attempting to select Area/Locality: {area}")
                        
                        # Create a Select object
                        select = Select(select_elem)
                        
                        # Log available options for debugging (retained from the first script for usefulness)
                        print("[DEBUG] Available options in Area/Locality dropdown:")
                        for option in select.options:
                            print(f"  - {option.text} (value: {option.get_attribute('value')})")
                        
                        try:
                            # Use select_by_visible_text as in the second script
                            select.select_by_visible_text(area)
                            time.sleep(0.5)  # Wait for the selection to register

                            # Verify selection
                            selected_option_text = select.first_selected_option.text.strip()
                            if selected_option_text == area:
                                print(f"[SUCCESS] Selected Area/Locality: {area}")
                                fields_filled_count += 1

                                # Handle "Others" case if selected (logic from the second script)
                                if area.lower() == "others":
                                    print("[DEBUG] 'Others' selected. Attempting to fill the description field...")
                                    others_input_xpath = '//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy___widget"]'
                                    others_input = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.XPATH, others_input_xpath))
                                    )
                                    print("[DEBUG] Found 'Others' description input field.")

                                    # Make 'Others' input field visible and interactive
                                    driver.execute_script("""
                                        arguments[0].style.display = 'block';
                                        arguments[0].style.visibility = 'visible';
                                        arguments[0].style.opacity = '1';
                                        arguments[0].removeAttribute('readonly');
                                        arguments[0].removeAttribute('disabled');
                                    """, others_input)
                                    
                                    # Scroll 'Others' input field into view
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", others_input)
                                    time.sleep(0.5)

                                    description = partner.get("If Others selected, please specify", "").strip()
                                    if description:
                                        others_input.clear()
                                        others_input.send_keys(description)
                                        print(f"[SUCCESS] Filled 'Others' description: {description}")
                                        fields_filled_count += 1  # Increment count for the filled description
                                    else:
                                        print("[INFO] No description provided for 'Others' in Area/Locality.")
                            else:
                                print(f"[FAIL] Could not fill: Area/ Locality = {area}. Expected '{area}', but found '{selected_option_text}'.")
                                fields_failed_count += 1

                        except NoSuchElementException:
                            print(f"[FAIL] Could not fill: Area/ Locality = {area}. Option not found by visible text.")
                            fields_failed_count += 1
                        except Exception as e_select:
                            print(f"[FAIL] Error while trying to select Area/ Locality '{area}': {str(e_select)}")
                            fields_failed_count += 1
                            
                    else:
                        print(f"[INFO] No value provided for Area/ Locality.")

                # Specific exception for timeout when finding the dropdown (from the second script)
                except TimeoutException:
                    print(f"[FAIL] Error handling Area/ Locality: Timeout occurred while waiting for the dropdown element (XPath: {area_locality_xpath}).")
                    fields_failed_count += 1
                except Exception as e:
                    print(f"[FAIL] Error handling Area/ Locality: {str(e)}")
                    fields_failed_count += 1


                # Permanent Police Station
                perm_police_xpath = f"(//input[@aria-label='Jurisdiction of Police Station'])[{position}]"
                driver.find_element(By.XPATH, perm_police_xpath).send_keys(partner.get('Permanent Police Station', ''))


                # Permanent Phone
                try:
                    phone_value = partner.get('Permanent Phone', '').strip()

                    if phone_value:
                        # Dynamic XPath targeting the input inside its container with dynamic ID pattern and position
                        container_xpath = "(//div[starts-with(@id, 'guideContainer-rootPanel') and contains(@id, 'guidetextbox_copy') and contains(@id, '___guide-item')])"
                        perm_phone_xpath = f"{container_xpath}//input[@aria-label='Phone (with STD/ISD code)'][{position}]"

                        # Wait for the input to be visible and enabled
                        phone_input = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, perm_phone_xpath))
                        )

                        # Clear if needed, then send keys
                        phone_input.clear()
                        phone_input.send_keys(phone_value)

                        print(f"[SUCCESS] Filled Phone (STD/ISD): {phone_value}")
                        fields_filled_count += 1
                    else:
                        print("[INFO] No value provided for 'Permanent Phone'")
                except Exception as e:
                    print(f"[ERROR] Could not fill Phone (STD/ISD) field: {e}")
                    fields_failed_count += 1



                # Whether present address same as permanent
                try:
                    same_address_data = partner.get('Whether present residential address same as permanent', {})
                    label = next((k for k, v in same_address_data.items() if v.lower() == 'true'), None) if isinstance(same_address_data, dict) else None

                    if label:
                        # Dynamic XPath for the radio button container
                        container_xpath = f"(//div[contains(@class, 'guideContainer') and contains(@class, 'guideradiobutton')])[{position}]"
                        print(f"[DEBUG] Searching for radio container with XPath: {container_xpath}")

                        # Radio input XPath within container for the chosen label (Yes/No)
                        radio_xpath = (
                            f"{container_xpath}//input[@type='radio' and @aria-label='{label}']"
                        )

                        for attempt in range(3):
                            try:
                                radio_input = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, radio_xpath))
                                )

                                # Make sure radio is interactable
                                driver.execute_script("""
                                    arguments[0].style.display = 'block';
                                    arguments[0].style.visibility = 'visible';
                                    arguments[0].style.opacity = '1';
                                    arguments[0].removeAttribute('readonly');
                                    arguments[0].removeAttribute('disabled');
                                """, radio_input)

                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_input)
                                time.sleep(0.3)

                                radio_input.click()
                                time.sleep(0.3)

                                if radio_input.get_attribute('aria-checked') == 'true' or radio_input.is_selected():
                                    print(f"[SUCCESS] Selected: Address same as permanent = {label}")
                                    fields_filled_count += 1
                                    break
                                else:
                                    print(f"[RETRY {attempt+1}] Not selected, retrying...")
                            except Exception as e:
                                print(f"[RETRY {attempt+1}] Error: {e}")
                                time.sleep(1)
                        else:
                            print("[FAIL] Could not select address same as permanent after retries")
                            fields_failed_count += 1

                        # If selected "No", fill additional fields
                        if label.lower() == 'no':
                            try:
                                pres_address1_xpath = f"(//input[@aria-label='Present Address Line I'])[{position}]"
                                years_xpath = f"(//input[@aria-label='Years'])[{position}]"
                                months_xpath = f"(//input[@aria-label='Months'])[{position}]"

                                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, pres_address1_xpath))).send_keys(partner.get('Present Address Line I', ''))
                                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, years_xpath))).send_keys(partner.get('Duration Years', ''))
                                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, months_xpath))).send_keys(partner.get('Duration Months', ''))

                                print("[SUCCESS] Filled present address and duration fields.")
                                fields_filled_count += 3
                            except Exception as e:
                                print(f"[ERROR] Failed to fill present address fields: {e}")
                                fields_failed_count += 3
                    else:
                        print("[INFO] No valid option marked as True for 'Whether present address same as permanent'")
                except Exception as e:
                    print(f"[ERROR] Exception in 'Whether present address same as permanent': {e}")
                    fields_failed_count += 1


                            try:
                    residential_proof_value = partner.get('Residential Proof', '').strip()

                    if residential_proof_value:
                        dropdown_xpath = "//select[@aria-label='Residential Proof']"

                        # Wait for the dropdown to be present
                        dropdown_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, dropdown_xpath))
                        )

                        # Scroll into view and make sure it's visible/enabled
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_element)
                        driver.execute_script("arguments[0].style.opacity = 1; arguments[0].removeAttribute('disabled');", dropdown_element)
                        time.sleep(0.3)

                        select = Select(dropdown_element)
                        select.select_by_visible_text(residential_proof_value)

                        print(f"[SUCCESS] Selected residential proof: {residential_proof_value}")
                        fields_filled_count += 1
                    else:
                        print("[INFO] No residential proof provided in input data.")
                except Exception as e:
                    print(f"[ERROR] Failed to select residential proof: {e}")
                    fields_failed_count += 1


                

                try:

identity_proof_value = partner.get('Identity Proof', '').strip()



if identity_proof_value:

dropdown_xpath = "//select[@aria-label='(iv) Identity Proof']"


# Wait for the dropdown to be present

dropdown_element = WebDriverWait(driver, 10).until(

EC.presence_of_element_located((By.XPATH, dropdown_xpath))

)



# Scroll into view and make sure it's visible

driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_element)

driver.execute_script("arguments[0].style.opacity = 1; arguments[0].removeAttribute('disabled');", dropdown_element)

time.sleep(0.3)



select = Select(dropdown_element)

select.select_by_visible_text(identity_proof_value)


print(f"[SUCCESS] Selected identity proof: {identity_proof_value}")

fields_filled_count += 1

else:

print("[INFO] No identity proof provided in input data.")

except Exception as e:

print(f"[ERROR] Failed to select identity proof: {e}")

fields_failed_count += 1
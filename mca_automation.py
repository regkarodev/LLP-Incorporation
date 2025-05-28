# Get the number of partners to fill
        num_partners = int(config_data['form_data']['fields'].get('Individuals Having valid DIN/DPIN', 0))
        
        if num_partners < 1:
            print('No designated partners with DIN/DPIN to fill.')
        else:
            if num_partners > 5:
                print('Reached the limit of 5 designated partners. Only filling 5.')
                num_partners = 5
            
            # Load selectors from config.json
            try:
                with open('config.json', 'r') as f:
                    config_selectors = json.load(f)
                selectors_list = config_selectors['Basic details']['form1']
            except:
                print("Error loading config.json for selectors")
                selectors_list = []
            
            # Get partner data (check multiple locations)
            designated_partners = config_data['form_data'].get('designated_partners', None)
            if not designated_partners:
                # Check under options
                designated_partners = config_data['form_data'].get('options', {}).get('designated_partners', None)
            
            if not designated_partners:
                # Fallback: use the same data for all
                designated_partners = [config_data['form_data']['fields']] * num_partners
            
            # Fill each partner's subform
            for idx in range(num_partners):
                print(f'Filling subform for designated partner {idx+1}')
                
                # Get partner data and selectors for this index
                partner = designated_partners[idx] if idx < len(designated_partners) else designated_partners[0]
                filled_successfully = False
                
                # First try: Use selectors from config.json (only for partner 1)
                if selectors_list and idx == 0:
                    selectors = selectors_list[idx]
                    
                    # Check if this is a dynamic GUID selector that might not work
                    first_selector = list(selectors.values())[0] if selectors else ""
                    if idx > 0 and "GUID" in first_selector:
                        print(f"Note: Partner {idx+1} uses dynamic GUID selectors which may not match the page")
                    
                    fields_filled = 0
                    for field, selector in selectors.items():
                        # Map field names...
                        field_mapping = {
                            'Designated partner identification number (DIN/DPIN)': 'Designated partner identification number (DIN/DPIN)',
                            'resident_india': 'Whether resident of India',
                            'form_of_contribution': 'Form of contribution',
                            'monetary_value_of_contribution': 'Monetary value of contribution (in INR) (in figures)',
                            'number_of_llp': 'Number of LLP(s) in which he/ she is a partner',
                            'number_of_company': 'Number of company(s) in which he/ she is a director',
                            'value': None,
                            "If 'Other than cash' selected, please specify": "If 'Other than cash' selected, please specify"
                        }
                        actual_field = field_mapping.get(field, field)
                        if actual_field is None:
                            continue
                        value = partner.get(actual_field)
                        if value is not None:
                            try:
                                if field == 'resident_india':
                                    if str(value).lower() == 'yes':
                                        element = driver.find_element(By.CSS_SELECTOR, selector)
                                        click_element(selector)
                                    time.sleep(0.5)
                                elif field == 'form_of_contribution':
                                    # Use XPath fallback for dropdown with enhanced handling
                                    position = idx + 1
                                    try:
                                        contribution_value = partner.get('Form of contribution', '')
                                        if not contribution_value:
                                            print(f"Warning: No contribution value provided for partner {position}")
                                            continue

                                        # Try different XPath patterns with wait
                                        xpath_patterns = [
                                            f"(//input[@aria-label='Form of contribution'])[{position}]",
                                            f"(//select[@aria-label='Form of contribution'])[{position}]", 
                                            f"(//*[@aria-label='Form of contribution'])[{position}]",
                                            f"(//*[contains(@aria-label, 'Form of contribution')])[{position}]"
                                        ]
                                        
                                        contribution_element = None
                                        for xpath in xpath_patterns:
                                            try:
                                                contribution_element = WebDriverWait(driver, 10).until(
                                                    EC.presence_of_element_located((By.XPATH, xpath))
                                                )
                                                if contribution_element:
                                                    break
                                            except:
                                                continue
                                        
                                        if not contribution_element:
                                            print(f"Warning: Could not find Form of contribution element for partner {position}")
                                            continue
                                        
                                        # Handle different element types
                                        if contribution_element.tag_name.lower() == 'select':
                                            from selenium.webdriver.support.ui import Select
                                            select = Select(contribution_element)
                                            try:
                                                select.select_by_visible_text(contribution_value)
                                                print(f"Selected contribution via select: {contribution_value}")
                                            except:
                                                try:
                                                    select.select_by_value(contribution_value)
                                                    print(f"Selected contribution via value: {contribution_value}")
                                                except:
                                                    print(f"Warning: Could not select contribution value: {contribution_value}")
                                        else:
                                            # Try clicking and selecting from dropdown
                                            try:
                                                contribution_element.click()
                                                time.sleep(1)
                                                
                                                # Try to find and click the option
                                                option_xpath = f"//li[contains(text(), '{contribution_value}') or contains(., '{contribution_value}')]"
                                                option = WebDriverWait(driver, 5).until(
                                                    EC.presence_of_element_located((By.XPATH, option_xpath))
                                                )
                                                option.click()
                                                print(f"Selected contribution via dropdown: {contribution_value}")
                                            except:
                                                # Fallback to direct input
                                                try:
                                                    contribution_element.clear()
                                                    contribution_element.send_keys(contribution_value)
                                                    print(f"Entered contribution via direct input: {contribution_value}")
                                                except Exception as e:
                                                    print(f"Warning: Could not set contribution value: {str(e)}")
                                        
                                        # Handle "Other than cash" specification
                                        if str(contribution_value).lower() == 'other than cash':
                                            spec_value = partner.get("If 'Other than cash' selected, please specify", '')
                                            if spec_value:
                                                try:
                                                    spec_xpath = f"(//*[contains(@aria-label, 'please specify')])[{position}]"
                                                    spec_element = WebDriverWait(driver, 5).until(
                                                        EC.presence_of_element_located((By.XPATH, spec_xpath))
                                                    )
                                                    spec_element.clear()
                                                    spec_element.send_keys(spec_value)
                                                    print(f"Filled 'Other than cash' specification for partner {position}")
                                                except Exception as e:
                                                    print(f"Warning: Could not fill 'Other than cash' specification: {str(e)}")
                                    except Exception as e:
                                        print(f"Warning: Could not handle form of contribution for partner {position}: {str(e)}")
                                else:
                                    element = driver.find_element(By.CSS_SELECTOR, selector)
                                    send_text(selector, str(value))
                                fields_filled += 1
                            except Exception as e:
                                print(f"Warning: Could not fill field '{field}' with selector '{selector}': {str(e)}")
                                continue
                    
                    if fields_filled > 5:  # Lower threshold for success
                        filled_successfully = True
                        print(f"✓ Successfully filled {fields_filled} fields for partner 1 using CSS selectors")
                    else:
                        print(f"⚠️ Only filled {fields_filled} fields for partner 1 using CSS selectors, trying fallback...")
                
                # Always use XPath fallback for all partners (including partner 1 if config selectors fail)
                if not filled_successfully:
                    print(f"Using XPath fallback for partner {idx+1}")
                    try:
                        position = idx + 1
                        # DIN/DPIN
                        try:
                            din_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Designated partner identification number (DIN/DPIN)'])[{position}]")
                            din_element.clear()
                            din_element.send_keys(partner.get('Designated partner identification number (DIN/DPIN)', ''))
                            print(f"Filled DIN for partner {position}")
                        except Exception as e:
                            print(f"Warning: Could not fill DIN for partner {position}: {str(e)}")
                        # Click resident radio if available
                        if partner.get('Whether resident of India', '') == 'Yes':
                            radio_selected = False
                            # Try multiple approaches to find the radio button
                            radio_approaches = [
                                # Approach 1: By aria-label exact match
                                f"(//input[@type='radio' and @aria-label='Whether resident of India'])[{position}]",
                                # Approach 2: By partial aria-label match
                                f"(//input[@type='radio' and contains(@aria-label, 'resident')])[{position}]",
                                # Approach 3: By value for Yes
                                f"(//input[@type='radio' and @value='Y'])[{position}]",
                                # Approach 4: By name containing resident
                                f"(//input[@type='radio' and contains(@name, 'resident')])[{position}]",
                                # Approach 5: By id containing resident
                                f"(//input[@type='radio' and contains(@id, 'resident')])[{position}]",
                                # Approach 6: Look for radio in the same row/container as DIN field
                                f"(//input[@aria-label='Designated partner identification number (DIN/DPIN)'])[{position}]/ancestor::*[contains(@class, 'panel') or contains(@class, 'row')]//input[@type='radio' and @value='Y']",
                                # Approach 7: Generic radio button by position
                                f"(//input[@type='radio'])[{position * 2 - 1}]"  # Assuming Yes is first radio in pair
                            ]
                            
                            for xpath in radio_approaches:
                                try:
                                    resident_radio = driver.find_element(By.XPATH, xpath)
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", resident_radio)
                                    time.sleep(0.5)
                                    try:
                                        resident_radio.click()
                                    except Exception:
                                        try:
                                            driver.execute_script("arguments[0].click();", resident_radio)
                                        except Exception:
                                            ActionChains(driver).move_to_element(resident_radio).click().perform()
                                    print(f"Selected resident of India for partner {position}")
                                    radio_selected = True
                                    break
                                except Exception:
                                    continue
                            if not radio_selected:
                                print(f"Warning: Could not select resident radio for partner {position} - field may not exist or have different structure")
                        # Form of contribution
                        try:
                            contribution_value = partner.get('Form of contribution', '')
                            contribution_element = None
                            
                            # Try different XPath patterns
                            xpath_patterns = [
                                f"(//input[@aria-label='Form of contribution'])[{position}]",
                                f"(//select[@aria-label='Form of contribution'])[{position}]", 
                                f"(//*[@aria-label='Form of contribution'])[{position}]"
                            ]
                            
                            for xpath in xpath_patterns:
                                try:
                                    contribution_element = driver.find_element(By.XPATH, xpath)
                                    break
                                except:
                                    continue
                            
                            if not contribution_element:
                                raise Exception("Could not find Form of contribution element")

                            # Handle different element types
                            if contribution_element.tag_name.lower() == 'select':
                                from selenium.webdriver.support.ui import Select
                                select = Select(contribution_element)
                                select.select_by_visible_text(contribution_value)
                                print(f"Selected contribution: {contribution_value}")
                            else:
                                contribution_element.click()
                                time.sleep(0.5)
                                try:
                                    option_xpath = f"//li[contains(text(), '{contribution_value}') or contains(., '{contribution_value}')]"
                                    option = driver.find_element(By.XPATH, option_xpath)
                                    option.click()
                                    print(f"Selected contribution: {contribution_value}")
                                except Exception as e:
                                    contribution_element.send_keys(contribution_value)
                                    print(f"Sent keys for contribution: {contribution_value}")
                            
                            # Handle "Other than cash" specification
                            if contribution_value.lower() == 'other than cash':
                                try:
                                    spec_element = driver.find_element(By.XPATH, f"(//*[contains(@aria-label, 'please specify')])[{position}]")
                                    spec_element.clear()
                                    spec_element.send_keys(partner.get("If 'Other than cash' selected, please specify", ''))
                                    print(f"Filled 'Other than cash' specification for partner {position}")
                                except Exception as e:
                                    print(f"Warning: Could not fill 'Other than cash' specification: {str(e)}")
                        except Exception as e:
                            print(f"Warning: Could not fill contribution for partner {position}: {str(e)}")
                        # Monetary value
                        try:
                            monetary_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Monetary value of contribution (in INR) (in figures)'])[{position}]")
                            monetary_element.clear()
                            monetary_element.send_keys(partner.get('Monetary value of contribution (in INR) (in figures)', ''))
                            print(f"Filled monetary value for partner {position}")
                        except Exception as e:
                            print(f"Warning: Could not fill monetary value for partner {position}: {str(e)}")
                        # Number of LLPs
                        try:
                            llp_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Number of LLP(s) in which he/ she is a partner'])[{position}]")
                            llp_element.clear()
                            llp_element.send_keys(partner.get('Number of LLP(s) in which he/ she is a partner', ''))
                            print(f"Filled LLP count for partner {position}")
                        except Exception as e:
                            print(f"Warning: Could not fill LLP count for partner {position}: {str(e)}")
                        # Number of companies
                        try:
                            company_element = driver.find_element(By.XPATH, f"(//input[@aria-label='Number of company(s) in which he/ she is a director'])[{position}]")
                            company_element.clear()
                            company_element.send_keys(partner.get('Number of company(s) in which he/ she is a director', ''))
                            print(f"Filled company count for partner {position}")
                        except Exception as e:
                            print(f"Warning: Could not fill company count for partner {position}: {str(e)}")
                    except Exception as e:
                        print(f"Error with XPath fallback for partner {idx+1}: {str(e)}")
                        print(f"This usually means the form structure is different than expected.")
                        print(f"Please check that {num_partners} subforms are actually visible on the page.")
                
                time.sleep(1)  # Wait between partners



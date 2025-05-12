import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from logger import Logger
from vision_click_helper import click_button_with_vision

class NavigationManager:
    def __init__(self, driver, wait):
        """Initialize navigation manager with driver and wait objects"""
        self.driver = driver
        self.wait = wait
        self.logger = Logger()
        self.login_url = "https://www.mca.gov.in/content/mca/global/en/foportal/fologin.html"
        self.run_llp_url = "https://www.mca.gov.in/content/mca/global/en/mca/llp-e-filling/Fillip.html"
        # Add coordinate cache dictionary to store successful button coordinates
        self.button_coordinates_cache = {}

    def navigate_to_login(self):
        """Navigate to the MCA login page"""
        try:
            self.logger.log("Navigating to MCA login page...")
            self.driver.get(self.login_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.logger.log("Successfully loaded login page")
            self.handle_info_popup()
            return True
        except Exception as e:
            self.logger.log(f"Error navigating to login page: {str(e)}", "error")
            return False

    def navigate_to_run_llp(self):
        """Navigate to the RUN LLP page"""
        try:
            self.logger.log("Navigating to RUN LLP page...")
            self.driver.get(self.run_llp_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.logger.log("Successfully loaded RUN LLP page")
            self.handle_info_popup()
            return True
        except Exception as e:
            self.logger.log(f"Error navigating to RUN LLP page: {str(e)}", "error")
            return False

    def handle_info_popup(self):
        """Handle info popup if it appears"""
        try:
            self.logger.log("Checking for info popup with OK button...")
            max_attempts = 3  # Reduced from 20 to 3 since we don't need to wait as long
            for attempt in range(max_attempts):
                try:
                    # Try different button selectors
                    button_selectors = [
                        "//button[normalize-space(text())='OK' or normalize-space(text())='Ok']",
                        "//button[contains(@class, 'btn-primary')]",
                        "//button[contains(@class, 'btn')]",
                        "//button[contains(@class, 'blue')]",
                        "//input[@type='button' and (normalize-space(@value)='OK' or normalize-space(@value)='Ok')]"
                    ]
                    
                    for selector in button_selectors:
                        try:
                            ok_button = self.driver.find_element(By.XPATH, selector)
                            if ok_button.is_displayed() and ok_button.is_enabled():
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", ok_button)
                                ok_button.click()
                                self.logger.log(f"OK button clicked using selector: {selector}")
                                return True
                        except Exception:
                            continue
                    
                    time.sleep(0.5)  # Reduced from 1 second to 0.5 seconds
                    
                except Exception as e:
                    self.logger.log(f"Attempt {attempt + 1} failed: {str(e)}", "warning")
                
            self.logger.log("No OK popup button found after checking all selectors.", "info")
            return True  # Return True even if no popup found, as this is not a critical error
        
        except Exception as e:
            self.logger.log(f"Error in popup handler: {str(e)}", "error")
            return True  # Return True to allow the script to continue

    def scroll_to_form_section(self):
        """Scroll to the '1 Purpose of filing the form' section, with robust element search."""
        try:
            self.logger.log("Scrolling to '1 Purpose of filing the form' section...")
            # Try several possible XPaths for robustness
            xpaths = [
                "//*[contains(text(), '1 Purpose of filing the form')]",
                "//*[contains(text(), 'Purpose of filing the form')]",
                "//*[contains(text(), 'Purpose of Filing the Form')]"
            ]
            section_elem = None
            for xpath in xpaths:
                try:
                    section_elem = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    if section_elem:
                        break
                except Exception:
                    continue

            # If not found, try inside iframes
            if not section_elem:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for idx, iframe in enumerate(iframes):
                    self.driver.switch_to.frame(iframe)
                    for xpath in xpaths:
                        try:
                            section_elem = self.wait.until(
                                EC.presence_of_element_located((By.XPATH, xpath))
                            )
                            if section_elem:
                                break
                        except Exception:
                            continue
                    self.driver.switch_to.default_content()
                    if section_elem:
                        break

            if not section_elem:
                self.logger.log("Could not find the 'Purpose of filing the form' section.", "error")
                return False

            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", section_elem)
            self.logger.log("Scrolled to '1 Purpose of filing the form' section.")
            return True
        except Exception as e:
            self.logger.log(f"Could not scroll to form section: {str(e)}", "error")
            return False

    def select_name_approved_yes(self):
        """Select 'Yes' for 'Whether name is already approved by Registrar of Companies'"""
        try:
            # Try to find the radio button by label text or value
            yes_radio = self.driver.find_element(
                By.XPATH,
                "//label[contains(., 'Whether name is already approved')]/following::input[@type='radio'][1]"
            )
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", yes_radio)
            yes_radio.click()
            self.logger.log("Selected 'Yes' for 'Whether name is already approved by Registrar of Companies'.")
            return True
        except Exception as e:
            self.logger.log(f"Could not select 'Yes' radio button: {str(e)}", "error")
            return False

    def fill_srn_of_run_llp(self, srn_value):
        """Fill the Service Request Number (SRN) of RUN-LLP field with the provided value."""
        try:
            srn_input = self.driver.find_element(
                By.XPATH,
                "//label[contains(., 'Service Request Number (SRN)')]/following::input[@type='text'][1]"
            )
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", srn_input)
            srn_input.clear()
            srn_input.send_keys(srn_value)
            self.logger.log(f"Filled SRN of RUN-LLP with value: {srn_value}")
            return True
        except Exception as e:
            self.logger.log(f"Could not fill SRN of RUN-LLP: {str(e)}", "error")
            return False

    def select_type_of_incorporation_new(self):
        """Select 'New Incorporation' for '(c) *Type of incorporation'"""
        try:
            new_incorp_radio = self.driver.find_element(
                By.XPATH,
                "//label[contains(., 'Type of incorporation')]/following::input[@type='radio'][1]"
            )
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", new_incorp_radio)
            new_incorp_radio.click()
            self.logger.log("Selected 'New Incorporation' for '(c) *Type of incorporation'.")
            return True
        except Exception as e:
            self.logger.log(f"Could not select 'New Incorporation' radio button: {str(e)}", "error")
            return False

    def scroll_to_proposed_name_field(self):
        """Scroll to the '(a) Proposed or approved name' field automatically."""
        try:
            self.logger.log("Scrolling to '(a) Proposed or approved name' field...")
            # Try several possible XPaths for robustness
            xpaths = [
                "//*[contains(text(), '(a) *Proposed or approved name')]",
                "//*[contains(text(), 'Proposed or approved name')]",
                "//*[contains(text(), 'proposed or approved name')]"
            ]
            field_elem = None
            for xpath in xpaths:
                try:
                    field_elem = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    if field_elem:
                        break
                except Exception:
                    continue

            # If not found, try inside iframes
            if not field_elem:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for idx, iframe in enumerate(iframes):
                    self.driver.switch_to.frame(iframe)
                    for xpath in xpaths:
                        try:
                            field_elem = self.wait.until(
                                EC.presence_of_element_located((By.XPATH, xpath))
                            )
                            if field_elem:
                                break
                        except Exception:
                            continue
                    self.driver.switch_to.default_content()
                    if field_elem:
                        break

            if not field_elem:
                self.logger.log("Could not find the '(a) Proposed or approved name' field.", "error")
                return False

            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", field_elem)
            self.logger.log("Scrolled to '(a) Proposed or approved name' field.")
            return True
        except Exception as e:
            self.logger.log(f"Could not scroll to '(a) Proposed or approved name' field: {str(e)}", "error")
            return False

    def fill_registered_office_address(self):
        """
        Fill the registered office address details in the form.
        This function fills multiple fields in the "3(a) Address of registered office of LLP" section.
        
        Fields to be filled:
        1. Address Line I: "Plot No.31"
        2. Address Line II: "near Passport Office"
        3. Pin code/ Zip Code: "122015"
        4. Area/ Locality: "Palam"
        5. City: "Gurugram" 
        6. District: "Gurugram"
        7. State/ UT: "Haryana"
        8. Longitude: "77.0809° E"
        9. Latitude: "28.5045° N"
        10. Jurisdiction of Police Station: "Gurugram"
        11. Country: "India" (just verify, already pre-selected)
        
        Returns:
            bool: True if all fields were filled successfully, False otherwise
        """
        try:
            self.logger.log("Filling registered office address details...")
            
            # Install global protection against field clearing
            self.driver.execute_script("""
                // Create a global tracking object for filled fields
                window._filledFields = {};
                
                // Add protection against field clearing
                document.addEventListener('reset', function(e) {
                    // Prevent form resets
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }, true);
                
                // Monitor and intercept attempts to clear fields
                const originalClear = HTMLInputElement.prototype.clear;
                HTMLInputElement.prototype.clear = function() {
                    if (this.getAttribute('data-filled') === 'true') {
                        console.log('Prevented clearing of filled field');
                        return;
                    }
                    return originalClear.apply(this, arguments);
                };
                
                // Prevent programmatic value clearing
                const fieldsToProtect = document.querySelectorAll('input, select, textarea');
                fieldsToProtect.forEach(function(field) {
                    const originalValueDescriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
                    
                    // Store original value
                    field.originalValueBeforeProtection = field.value;
                    
                    // Override the value property for inputs
                    Object.defineProperty(field, 'value', {
                        get: function() {
                            return originalValueDescriptor.get.call(this);
                        },
                        set: function(val) {
                            // Allow non-empty values or if field hasn't been filled yet
                            if (val && val.length > 0 || !this.getAttribute('data-filled')) {
                                originalValueDescriptor.set.call(this, val);
                            } else if (this.getAttribute('data-filled') === 'true') {
                                // Restore the original value if attempting to clear
                                originalValueDescriptor.set.call(this, this.originalValueBeforeProtection || '');
                            }
                        }
                    });
                });
            """)
            
            # Scroll to the address section
            address_section_xpaths = [
                "//*[contains(text(), '3(a) Address of registered office of LLP')]",
                "//*[contains(text(), 'Address of registered office')]",
                "//*[contains(text(), 'registered office of LLP')]"
            ]
            
            section_found = False
            for xpath in address_section_xpaths:
                try:
                    section_elem = self.driver.find_element(By.XPATH, xpath)
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", section_elem)
                    section_found = True
                    self.logger.log("Found and scrolled to address section")
                    break
                except Exception:
                    continue
                    
            if not section_found:
                self.logger.log("Could not find the address section. Attempting to proceed anyway.", "warning")
            
            # Define the fields to be filled - including whether they're dropdowns
            address_fields = [
                {"label": "Address Line I", "value": "Plot No.31", "type": "input"},
                {"label": "Address Line II", "value": "near Passport Office", "type": "input"},
                {"label": "Pin code/ Zip Code", "value": "122015", "type": "input", "data_type": "str", 
                 "alt_labels": ["Pin code", "Pincode", "ZIP", "Zip Code", "Postal Code"]},
                {"label": "Area/ Locality", "value": "Palam", "type": "dropdown", "select_any": True,
                 "alt_labels": ["Area", "Locality", "Area/Locality", "Location"], "force_dropdown": True},
                {"label": "City", "value": "Gurugram", "type": "input", "priority": "high", 
                 "alt_labels": ["Town", "City Name", "Municipal"]},
                {"label": "District", "value": "Gurugram", "type": "input", "priority": "high", 
                 "alt_labels": ["District Name", "County"]},
                {"label": "State/ UT", "value": "Haryana", "type": "dropdown", "priority": "high", "select_any": True,
                 "alt_labels": ["State", "UT", "State Name", "Province"]},
                {"label": "Longitude", "value": 77.0809, "type": "input", "data_type": "float", "display_format": "%.4f° E"},
                {"label": "Latitude", "value": 28.5045, "type": "input", "data_type": "float", "display_format": "%.4f° N"},
                {"label": "Jurisdiction of Police Station", "value": "Gurugram", "type": "input"},
                {"label": "Country", "value": "India", "type": "dropdown", "verify_only": True}  # Just verify, already pre-selected
            ]
            
            # Try to fill each field
            fields_filled = 0
            required_fields_count = len(address_fields)
            
            for field_info in address_fields:
                field_label = field_info["label"]
                field_value = field_info["value"]
                field_type = field_info["type"]
                verify_only = field_info.get("verify_only", False)
                data_type = field_info.get("data_type", "str")
                display_format = field_info.get("display_format", None)
                alt_labels = field_info.get("alt_labels", [])
                select_any = field_info.get("select_any", False)
                priority = field_info.get("priority", "low")
                force_dropdown = field_info.get("force_dropdown", False)
                
                # Convert field value to appropriate string format for display in logs
                display_value = field_value
                if data_type == "int" and isinstance(field_value, int):
                    display_value = str(field_value)
                elif data_type == "float" and isinstance(field_value, (float, int)):
                    if display_format:
                        display_value = display_format % field_value
                    else:
                        display_value = str(field_value)
                
                # Flag for special handling
                is_high_priority = priority.lower() == "high"
                is_pin_code = "pin code" in field_label.lower() or any("pin code" in alt_label.lower() for alt_label in alt_labels)
                is_area_locality = "area" in field_label.lower() or "locality" in field_label.lower() or any("area" in alt_label.lower() for alt_label in alt_labels)
                
                # Special handling for Area/Locality dropdown
                if is_area_locality and force_dropdown:
                    self.logger.log(f"Using specialized handling for {field_label}")
                    
                    # Enhanced automatic handling - actively ensures dropdown is clicked and option selected
                    self.logger.log(f"Auto-selecting '{field_value}' from Area/Locality dropdown")
                    
                    # First force a full search for the dropdown element with multiple approaches
                    dropdown_found = False
                    dropdown_element = None
                    
                    # Specialized selector for Area/Locality dropdown - prioritize direct visible selectors
                    area_locality_selectors = [
                        "//div[contains(@class, 'dropdown')]//span[text()='Select here']",
                        "//div[contains(@class, 'select')]//span[text()='Select here']",
                        "//*[contains(text(), 'Area/ Locality')]/following::*[contains(text(), 'Select here')][1]",
                        "//*[contains(text(), 'Area/ Locality')]/following::div[contains(@class, 'dropdown')][1]",
                        "//*[contains(text(), 'Area/ Locality')]/following::div[contains(@class, 'select')][1]",
                        "//select[contains(@id, 'area') or contains(@name, 'area')]",
                        # Additional direct DOM selectors that might find dropdown
                        "//div[contains(@class, 'dropdown') and contains(@class, 'form-control')]",
                        "//div[contains(@class, 'select') and contains(@class, 'form-control')]"
                    ]
                    
                    # Try each selector to find the dropdown
                    for selector in area_locality_selectors:
                        try:
                            dropdown_element = self.driver.find_element(By.XPATH, selector)
                            if dropdown_element.is_displayed():
                                self.logger.log(f"Found Area/Locality dropdown")
                                dropdown_found = True
                                break
                        except Exception:
                            continue
                    
                    # If direct selectors fail, try finding it through parent elements
                    if not dropdown_found:
                        try:
                            area_label = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Area/ Locality')]")
                            if area_label:
                                parent_div = area_label
                                for _ in range(3):  # Go up to 3 levels up in DOM
                                    try:
                                        parent_div = parent_div.find_element(By.XPATH, "..")
                                        dropdown_candidates = parent_div.find_elements(By.CSS_SELECTOR, 
                                            "div.dropdown, div.select, select, div[role='combobox'], div.form-control")
                                        
                                        for candidate in dropdown_candidates:
                                            if candidate.is_displayed():
                                                dropdown_element = candidate
                                                dropdown_found = True
                                                self.logger.log("Found Area/Locality dropdown through parent element search")
                                                break
                                        
                                        if dropdown_found:
                                            break
                                    except:
                                        break
                        except Exception:
                            pass
                    
                    # Last resort - try to find by relative position to the pin code field
                    if not dropdown_found:
                        try:
                            # Find the pin code field first
                            pin_field = None
                            pin_selectors = [
                                "//input[contains(@id, 'pin') or contains(@name, 'pin')]",
                                "//*[contains(text(), 'Pin code')]/following::input[1]"
                            ]
                            
                            for selector in pin_selectors:
                                try:
                                    pin_field = self.driver.find_element(By.XPATH, selector)
                                    if pin_field.is_displayed():
                                        break
                                except:
                                    continue
                            
                            if pin_field:
                                # Look for any dropdown element to the right or below the pin code field
                                area_candidates = self.driver.find_elements(By.CSS_SELECTOR, 
                                    "div.dropdown, div.select, select, [role='combobox']")
                                
                                for candidate in area_candidates:
                                    if candidate.is_displayed():
                                        pin_rect = pin_field.rect
                                        candidate_rect = candidate.rect
                                        
                                        # Check if candidate is positioned after pin code field
                                        if ((candidate_rect['x'] > pin_rect['x'] + pin_rect['width']) or 
                                            (candidate_rect['y'] > pin_rect['y'] + pin_rect['height'])):
                                            dropdown_element = candidate
                                            dropdown_found = True
                                            self.logger.log("Found Area/Locality dropdown by position relative to pin code field")
                                            break
                        except Exception:
                            pass
                    
                    # If found, try aggressive approach to open and select from dropdown
                    if dropdown_found and dropdown_element:
                        self.logger.log("Dropdown found - preparing to open and select option")
                        
                        try:
                            # Make sure element is visible and scrolled into view
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", dropdown_element)
                            time.sleep(0.3)
                            
                            # Always try multiple times with different methods to ensure dropdown opens
                            dropdown_opened = False
                            
                            # 1. First try standard click methods
                            click_methods = [
                                lambda: dropdown_element.click(),
                                lambda: self.driver.execute_script("arguments[0].click();", dropdown_element),
                                lambda: self.driver.execute_script("""
                                    var element = arguments[0];
                                    var rect = element.getBoundingClientRect();
                                    var centerX = rect.left + rect.width / 2;
                                    var centerY = rect.top + rect.height / 2;
                                    element.dispatchEvent(new MouseEvent('click', {
                                        'view': window,
                                        'bubbles': true,
                                        'cancelable': true,
                                        'clientX': centerX,
                                        'clientY': centerY
                                    }));
                                """, dropdown_element)
                            ]
                            
                            self.logger.log("Attempting to open dropdown")
                            for i, click_method in enumerate(click_methods):
                                try:
                                    click_method()
                                    time.sleep(0.8)  # Wait for dropdown to open
                                    
                                    # Look for visible dropdown items
                                    dropdown_items = self.driver.find_elements(By.CSS_SELECTOR, 
                                        "li, .dropdown-item, .select-option, .dropdown-menu div, .select-menu div, option, ul.dropdown-menu li")
                                    
                                    visible_items = [item for item in dropdown_items if item.is_displayed() and item.text.strip()]
                                    
                                    if visible_items:
                                        self.logger.log(f"Dropdown opened successfully with {len(visible_items)} options")
                                        dropdown_opened = True
                                        break
                                except Exception:
                                    continue
                            
                            # 2. If regular clicks failed, try more aggressive approach to force open
                            if not dropdown_opened:
                                self.logger.log("Standard clicks failed - using advanced techniques to open dropdown")
                                
                                # Try to activate any hidden dropdown menus with JavaScript
                                self.driver.execute_script("""
                                    // Show any dropdown menu that might be hidden
                                    var dropdowns = document.querySelectorAll('.dropdown-menu, .select-menu, ul.options, div[role="listbox"]');
                                    dropdowns.forEach(function(dropdown) {
                                        dropdown.style.display = 'block';
                                        dropdown.style.visibility = 'visible';
                                        dropdown.style.opacity = '1';
                                        dropdown.style.zIndex = '9999';
                                    });
                                    
                                    // Also try to trigger any click handlers
                                    var element = arguments[0];
                                    if(element) {
                                        // Try different event types that might open the dropdown
                                        ['click', 'mousedown', 'mouseup', 'focus', 'pointerdown'].forEach(function(eventType) {
                                            var event = new Event(eventType, { bubbles: true });
                                            element.dispatchEvent(event);
                                        });
                                        
                                        // If element has a specific attribute indicating it controls a dropdown
                                        if(element.hasAttribute('aria-controls')) {
                                            var controlsId = element.getAttribute('aria-controls');
                                            var controlledElement = document.getElementById(controlsId);
                                            if(controlledElement) {
                                                controlledElement.style.display = 'block';
                                                controlledElement.style.visibility = 'visible';
                                            }
                                        }
                                    }
                                """, dropdown_element)
                                
                                time.sleep(0.5)
                            
                            # Find all visible dropdown items after all attempts
                            dropdown_items = self.driver.find_elements(By.CSS_SELECTOR, 
                                "li, .dropdown-item, .select-option, .dropdown-menu div, .select-menu div, option, ul.dropdown-menu li")
                            
                            visible_items = [item for item in dropdown_items if item.is_displayed() and item.text.strip()]
                            self.logger.log(f"Found {len(visible_items)} dropdown options")
                            
                            if visible_items:
                                # First look for exact match of field_value (Palam)
                                exact_match = None
                                partial_matches = []
                                
                                for item in visible_items:
                                    item_text = item.text.strip()
                                    if item_text.lower() == field_value.lower():
                                        exact_match = item
                                        break
                                    elif field_value.lower() in item_text.lower():
                                        partial_matches.append(item)
                                
                                # Use exact match if found, otherwise try partial match
                                if exact_match:
                                    self.logger.log(f"Found exact match: '{exact_match.text}'")
                                    try:
                                        exact_match.click()
                                    except:
                                        self.driver.execute_script("arguments[0].click();", exact_match)
                                    
                                    self.logger.log(f"Selected exact matching option: '{exact_match.text}'")
                                    fields_filled += 1
                                elif partial_matches:
                                    best_match = partial_matches[0]  # Take first partial match
                                    self.logger.log(f"Found partial match: '{best_match.text}'")
                                    try:
                                        best_match.click()
                                    except:
                                        self.driver.execute_script("arguments[0].click();", best_match)
                                    
                                    self.logger.log(f"Selected partial matching option: '{best_match.text}'")
                                    fields_filled += 1
                                else:
                                    # If no matches found and select_any is true, pick first non-empty option
                                    if select_any:
                                        for item in visible_items:
                                            item_text = item.text.strip()
                                            if item_text and item_text.lower() not in ['select', 'select here', 'choose', '--select--']:
                                                try:
                                                    item.click()
                                                except:
                                                    self.driver.execute_script("arguments[0].click();", item)
                                                
                                                self.logger.log(f"Selected first available option: '{item_text}'")
                                                fields_filled += 1
                                                break
                            else:
                                # No visible items - try direct JavaScript injection
                                self.logger.log("No visible dropdown items - using direct JavaScript to set value")
                                
                                self.driver.execute_script("""
                                    var element = arguments[0];
                                    var newValue = arguments[1];
                                    
                                    // Handle different types of dropdowns
                                    if (element.tagName === 'SELECT') {
                                        // For standard select elements
                                        var optionFound = false;
                                        
                                        // First try to find matching option
                                        for (var i = 0; i < element.options.length; i++) {
                                            if (element.options[i].text.toLowerCase().indexOf(newValue.toLowerCase()) >= 0) {
                                                element.selectedIndex = i;
                                                optionFound = true;
                                                console.log("Found and selected matching option: " + element.options[i].text);
                                                break;
                                            }
                                        }
                                        
                                        // If no matching option, select first non-empty
                                        if (!optionFound) {
                                            for (var i = 0; i < element.options.length; i++) {
                                                if (element.options[i].text !== 'Select here' && 
                                                    element.options[i].text !== 'Select' &&
                                                    element.options[i].text.trim() !== '') {
                                                    element.selectedIndex = i;
                                                    optionFound = true;
                                                    console.log("Selected first valid option: " + element.options[i].text);
                                                    break;
                                                }
                                            }
                                        }
                                        
                                        // If still no option, create one
                                        if (!optionFound) {
                                            var option = document.createElement('OPTION');
                                            option.innerText = newValue;
                                            option.value = newValue;
                                            element.appendChild(option);
                                            option.selected = true;
                                            console.log("Created and selected new option: " + newValue);
                                        }
                                        
                                        // Trigger change event
                                        element.dispatchEvent(new Event('change', { bubbles: true }));
                                    } else {
                                        // For div/custom dropdowns
                                        if (element.innerText) {
                                            element.innerText = newValue;
                                        }
                                        
                                        element.setAttribute('data-value', newValue);
                                        element.value = newValue;
                                        
                                        // Set value in any child elements
                                        var spans = element.querySelectorAll('span');
                                        if (spans.length > 0) {
                                            spans[0].innerText = newValue;
                                        }
                                        
                                        var inputs = element.querySelectorAll('input');
                                        if (inputs.length > 0) {
                                            inputs[0].value = newValue;
                                        }
                                        
                                        // Trigger all relevant events
                                        ['input', 'change', 'blur'].forEach(function(eventType) {
                                            element.dispatchEvent(new Event(eventType, { bubbles: true }));
                                        });
                                        
                                        console.log("Set custom dropdown value to: " + newValue);
                                    }
                                """, dropdown_element, field_value)
                                
                                fields_filled += 1
                                self.logger.log(f"Set Area/Locality to '{field_value}' using JavaScript")
                        except Exception as e:
                            self.logger.log(f"Error automating Area/Locality selection: {str(e)}", "warning")
                    else:
                        self.logger.log("Could not find Area/Locality dropdown after multiple attempts", "warning")
                    
                    # Skip standard field handling
                    continue
                
                # For regular fields (not area/locality dropdown)
                try:
                    # Find the element using labels
                    field_found = False
                    input_field = None
                    
                    # Create XPath patterns for the main label and all alternative labels
                    all_labels = [field_label] + alt_labels
                    xpath_patterns = []
                    
                    # Build appropriate XPath patterns based on field type
                    if field_type == "input":
                        for label in all_labels:
                            xpath_patterns.extend([
                                f"//label[contains(text(), '{label}')]/following::input[1]",
                                f"//*[contains(text(), '{label}')]/following::input[1]",
                                f"//input[@placeholder='{label}']"
                            ])
                    elif field_type == "dropdown":
                        for label in all_labels:
                            xpath_patterns.extend([
                                f"//label[contains(text(), '{label}')]/following::select[1]",
                                f"//*[contains(text(), '{label}')]/following::select[1]",
                                f"//*[contains(text(), '{label}')]/following::div[contains(@class, 'dropdown')][1]"
                            ])
                    
                    # Add high priority patterns for important fields
                    if is_high_priority:
                        xpath_patterns.extend([
                            f"//input[contains(@id, '{field_label.lower().replace(' ', '')}')]",
                            f"//input[contains(@name, '{field_label.lower().replace(' ', '')}')]",
                            f"//*[contains(text(), '{field_label}')]/ancestor::div[1]//input"
                        ])
                    
                    # Try each XPath pattern
                    for xpath in xpath_patterns:
                        try:
                            input_field = self.driver.find_element(By.XPATH, xpath)
                            if input_field.is_displayed():
                                field_found = True
                                break
                        except Exception:
                            continue
                    
                    # If field found, fill it
                    if field_found and input_field:
                        # Scroll to the field
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", input_field)
                        time.sleep(0.3)  # Reduced from 0.5 to 0.3 seconds
                        
                        tag_name = input_field.tag_name.lower()
                        
                        # Handle dropdown select
                        if tag_name == "select":
                            from selenium.webdriver.support.ui import Select
                            select = Select(input_field)
                            
                            # Just verify existing value
                            if verify_only:
                                try:
                                    selected_option = select.first_selected_option.text
                                    if selected_option == display_value or display_value.lower() in selected_option.lower():
                                        self.logger.log(f"Verified '{field_label}' is correctly set")
                                        fields_filled += 1
                                    else:
                                        self.logger.log(f"Warning: '{field_label}' is set to '{selected_option}', not '{display_value}'", "warning")
                                except Exception:
                                    pass
                                continue
                                
                            # Try to select by visible text
                            try:
                                select.select_by_visible_text(display_value)
                                fields_filled += 1
                            except Exception:
                                # Get all options and try to select best match
                                options = [option.text for option in select.options]
                                
                                # If select_any is true, select any non-empty option
                                if select_any and options:
                                    for option in options:
                                        if option and option.strip() and option.lower() not in ['select', 'choose', '--select--']:
                                            select.select_by_visible_text(option)
                                            fields_filled += 1
                                            break
                                    continue
                                
                                # Try partial matches or first valid option
                                for option in options:
                                    if display_value.lower() in option.lower() or option.lower() in display_value.lower():
                                        select.select_by_visible_text(option)
                                        fields_filled += 1
                                        break
                                else:
                                    # If no match found, use first valid option
                                    for option in options:
                                        if option and option.strip() and option.lower() not in ['select', 'choose', '--select--']:
                                            select.select_by_visible_text(option)
                                            fields_filled += 1
                                            break
                        
                        # Handle custom dropdown div
                        elif tag_name == "div" and ("select" in input_field.get_attribute("class") or "dropdown" in input_field.get_attribute("class")):
                            try:
                                # For verify_only, just check text
                                if verify_only:
                                    current_text = input_field.text.strip()
                                    if current_text == display_value or display_value.lower() in current_text.lower():
                                        self.logger.log(f"Verified '{field_label}' is correctly set")
                                        fields_filled += 1
                                    continue
                                
                                # Click to open dropdown
                                input_field.click()
                                time.sleep(0.3)  # Reduced from 0.5 to 0.3 seconds
                                
                                # Find and click best option
                                options = self.driver.find_elements(By.CSS_SELECTOR, "li, option, div.option, div.item")
                                visible_options = [opt for opt in options if opt.is_displayed()]
                                
                                for option in visible_options:
                                    if option.text.strip() and (display_value.lower() in option.text.lower() or 
                                        select_any and option.text.lower() not in ['select', 'choose', '--select--']):
                                        option.click()
                                        fields_filled += 1
                                        break
                            except Exception:
                                pass
                                
                        # Regular input field
                        else:
                            try:
                                # For verify_only, just check value
                                if verify_only:
                                    current_value = input_field.get_attribute("value")
                                    if current_value == str(display_value) or str(display_value).lower() in current_value.lower():
                                        self.logger.log(f"Verified '{field_label}' is correctly set")
                                        fields_filled += 1
                                    continue
                                
                                # Clear the field
                                try:
                                    input_field.clear()
                                except:
                                    self.driver.execute_script("arguments[0].value = '';", input_field)
                                
                                # Format value appropriately
                                input_value = str(field_value)
                                
                                # Special handling for pin code and high priority fields
                                if is_pin_code or is_high_priority:
                                    # Try multiple fill methods for important fields
                                    fill_methods = [
                                        lambda: input_field.send_keys(input_value),
                                        lambda: self.driver.execute_script(f"arguments[0].value = '{input_value}';", input_field),
                                        lambda: self.driver.execute_script(f"""
                                            arguments[0].value = '{input_value}';
                                            arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                                            arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                                        """, input_field)
                                    ]
                                    
                                    # Try each method
                                    for method in fill_methods:
                                        try:
                                            method()
                                            time.sleep(0.3)  # Reduced from 0.5 to 0.3 seconds
                                            actual_value = input_field.get_attribute("value")
                                            if actual_value == input_value:
                                                break
                                        except Exception:
                                            continue
                                else:
                                    # Standard input
                                    input_field.send_keys(input_value)
                                
                                # Mark field as filled to prevent clearing
                                self.driver.execute_script("""
                                    arguments[0].setAttribute('data-filled', 'true');
                                    if (!window._filledFields) window._filledFields = {};
                                    window._filledFields[arguments[0].name || arguments[0].id || ''] = true;
                                """, input_field)
                                
                                fields_filled += 1
                            except Exception as e:
                                self.logger.log(f"Error filling {field_label}: {str(e)}", "warning")
                    else:
                        self.logger.log(f"Could not find input field for '{field_label}'", "warning")
                        
                except Exception as e:
                    self.logger.log(f"Error processing '{field_label}': {str(e)}", "warning")
            
            # Check if all fields were filled
            if fields_filled == required_fields_count:
                self.logger.log("Successfully filled all address fields")
                return True
            else:
                self.logger.log(f"Filled {fields_filled}/{required_fields_count} address fields", "warning")
                return fields_filled > 0  # Return True if at least some fields were filled
                
        except Exception as e:
            self.logger.log(f"Error filling registered office address: {str(e)}", "error")
            return False

    def fill_contact_details(self):
        """
        Fill the contact details section in the form.
        This function fills fields in the "(b) Contact Details" section that appears after the office address.
        
        Fields to be filled:
        1. Phone (with STD/ISD code): "011-45678901"
        2. Mobile No: "9354886960"
        3. Fax: "45678901" (numeric only)
        4. Email ID: "ashishmehra@registerkaro.com"
        
        Returns:
            bool: True if all fields were filled successfully, False otherwise
        """
        try:
            self.logger.log("Filling contact details section...")
            
            # First scroll to the Contact Details section
            contact_section_xpaths = [
                "//*[contains(text(), '(b) Contact Details')]",
                "//*[contains(text(), 'Contact Details')]",
                "//*[text()='Phone' or text()='Phone (with STD/ISD code)']/ancestor::div[contains(@class, 'section')]",
                "//*[contains(text(), 'Email') or contains(text(), 'Email ID')]/ancestor::div[2]"
            ]
            
            section_found = False
            for xpath in contact_section_xpaths:
                try:
                    section_elem = self.driver.find_element(By.XPATH, xpath)
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", section_elem)
                    section_found = True
                    self.logger.log("Found and scrolled to contact details section")
                    time.sleep(0.5)
                    break
                except Exception:
                    continue
                    
            if not section_found:
                self.logger.log("Could not find contact details section. Will try to find fields directly.", "warning")
            
            # Define the contact fields to fill with corrected formats
            contact_fields = [
                {"label": "Phone", "value": "01145678901", "type": "input", 
                 "alt_labels": ["Phone (with STD/ISD code)", "Phone Number", "STD/ISD code"]},
                {"label": "Mobile", "value": "9354886960", "type": "input", 
                 "alt_labels": ["Mobile No", "Mobile Number", "Cell"]},
                {"label": "Fax", "value": "45678901", "type": "input", "required": False,
                 "alt_labels": ["Fax Number", "Facsimile"]},
                {"label": "Email", "value": "ashishmehra@registerkaro.com", "type": "input", 
                 "alt_labels": ["Email ID", "E-mail", "Email Address"]}
            ]
            
            # Try to fill each field
            fields_filled = 0
            required_fields = sum(1 for field in contact_fields if field.get("required", True))
            
            for field_info in contact_fields:
                field_label = field_info["label"]
                field_value = field_info["value"]
                field_type = field_info["type"]
                is_required = field_info.get("required", True)
                alt_labels = field_info.get("alt_labels", [])
                
                self.logger.log(f"Looking for {field_label} field to fill with '{field_value}'")
                
                # Create XPath patterns for the field
                all_labels = [field_label] + alt_labels
                xpath_patterns = []
                
                # Build XPath patterns to find the input field
                for label in all_labels:
                    xpath_patterns.extend([
                        f"//label[contains(text(), '{label}')]/following::input[1]",
                        f"//*[contains(text(), '{label}')]/following::input[1]",
                        f"//input[@placeholder='{label}']",
                        f"//input[contains(@id, '{label.lower().replace(' ', '')}')]",
                        f"//input[contains(@name, '{label.lower().replace(' ', '')}')]"
                    ])
                
                # Try each XPath to find the field
                field_found = False
                input_field = None
                
                for xpath in xpath_patterns:
                    try:
                        input_field = self.driver.find_element(By.XPATH, xpath)
                        if input_field.is_displayed():
                            field_found = True
                            self.logger.log(f"Found {field_label} field")
                            break
                    except Exception:
                        continue
                
                # If no field found with XPath, try looking by surrounding text
                if not field_found:
                    try:
                        # Look for any text element containing the field label
                        label_elements = []
                        for label in all_labels:
                            label_elements.extend(self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{label}')]"))
                        
                        # For each label element found, look for an input nearby
                        for label_elem in label_elements:
                            if label_elem.is_displayed():
                                # Try to find an input in the same container
                                parent_div = label_elem
                                for _ in range(3):  # Try a few levels up
                                    try:
                                        parent_div = parent_div.find_element(By.XPATH, "..")
                                        inputs = parent_div.find_elements(By.TAG_NAME, "input")
                                        for inp in inputs:
                                            if inp.is_displayed():
                                                input_field = inp
                                                field_found = True
                                                self.logger.log(f"Found {field_label} field via parent container")
                                                break
                                        if field_found:
                                            break
                                    except:
                                        break
                            if field_found:
                                break
                    except Exception as e:
                        self.logger.log(f"Error searching for {field_label} by container: {str(e)}", "debug")
                
                # If field found, fill it
                if field_found and input_field:
                    # Scroll to the field
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", input_field)
                    time.sleep(0.3)
                    
                    try:
                        # Clear the field
                        try:
                            input_field.clear()
                        except:
                            self.driver.execute_script("arguments[0].value = '';", input_field)
                        
                        # Special handling for phone field to ensure proper format
                        if field_label.lower() == "phone":
                            # Make sure it's just numbers without any separators
                            cleaned_value = ''.join(filter(str.isdigit, field_value))
                            input_field.send_keys(cleaned_value)
                            self.logger.log(f"Filled {field_label} with cleaned value: '{cleaned_value}'")
                        # Special handling for fax field to ensure it's only numbers
                        elif field_label.lower() == "fax":
                            # Make sure it's just numbers without any separators or non-numeric characters
                            cleaned_value = ''.join(filter(str.isdigit, field_value))
                            input_field.send_keys(cleaned_value)
                            self.logger.log(f"Filled {field_label} with numeric-only value: '{cleaned_value}'")
                        else:
                            # Standard input for other fields
                            input_field.send_keys(field_value)
                        
                        # Mark field as filled to prevent clearing
                        self.driver.execute_script("""
                            arguments[0].setAttribute('data-filled', 'true');
                            if (!window._filledFields) window._filledFields = {};
                            window._filledFields[arguments[0].name || arguments[0].id || ''] = true;
                        """, input_field)
                        
                        # For email and mobile fields, try to trigger change/blur events
                        if field_label.lower() in ["email", "mobile", "phone", "fax"]:
                            self.driver.execute_script("""
                                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                                arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            """, input_field)
                        
                        fields_filled += 1
                        self.logger.log(f"Successfully filled {field_label} with '{field_value}'")
                    except Exception as e:
                        if is_required:
                            self.logger.log(f"Error filling {field_label}: {str(e)}", "warning")
                        else:
                            self.logger.log(f"Could not fill optional field {field_label}, continuing", "info")
                else:
                    if is_required:
                        self.logger.log(f"Could not find {field_label} field", "warning")
                    else:
                        self.logger.log(f"Could not find optional field {field_label}, continuing", "info")
            
            # Check if required fields were filled
            if fields_filled >= required_fields:
                self.logger.log(f"Successfully filled contact details section ({fields_filled}/{len(contact_fields)} fields)")
                return True
            else:
                self.logger.log(f"Only filled {fields_filled}/{required_fields} required contact detail fields", "warning")
                return fields_filled > 0  # Return True if at least some fields were filled
                
        except Exception as e:
            self.logger.log(f"Error filling contact details: {str(e)}", "error")
            return False

    def click_blue_button(self, button_name, custom_prompt=None, max_attempts=3):
        """
        Automatically locate and click a blue button using vision-based detection.
        
        Args:
            button_name (str): Name of the button to identify it in logs and screenshots
            custom_prompt (str, optional): Custom prompt for the vision AI to find the button
            max_attempts (int, optional): Number of retry attempts if clicking fails
            
        Returns:
            bool: True if button was successfully clicked, False otherwise
        """
        self.logger.log(f"Attempting to click blue button: {button_name}")
        
        # Default prompt for blue button detection
        if not custom_prompt:
            custom_prompt = f"Locate the blue '{button_name}' button in the image. Return only its exact screen coordinates in the format: x=..., y=.... If the button is not visible or not found, return NOT_FOUND."
        
        # Scroll to ensure the page is fully loaded
        self.driver.execute_script("window.scrollTo(0, 0);")  # First scroll to top
        time.sleep(0.3)  # Reduced from 0.5 to 0.3 seconds
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")  # Then partial scroll down
        time.sleep(0.3)  # Reduced from 0.5 to 0.3 seconds
        
        # Try multiple attempts to click the button
        for attempt in range(max_attempts):
            self.logger.log(f"Click attempt {attempt+1}/{max_attempts} for {button_name} button")
            
            # Take fresh screenshot for each attempt
            success = click_button_with_vision(
                driver=self.driver,
                prompt=custom_prompt,
                button_name=button_name,
                wait_for_scroll=True
            )
            
            if success:
                self.logger.log(f"Successfully clicked {button_name} button on attempt {attempt+1}")
                return True
            
            # If unsuccessful, wait and try a different approach for next attempt
            time.sleep(1)
            
            # Try scrolling a bit more on subsequent attempts
            scroll_amount = 100 * (attempt + 1)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(1)
        
        self.logger.log(f"Failed to click {button_name} button after {max_attempts} attempts", "error")
        return False
        
    def click_button_with_coordinates(self, button_name, coordinates=None, custom_prompt=None, max_attempts=3):
        """
        Automatically locate and click a button using either provided coordinates or vision detection.
        
        Args:
            button_name (str): Name of the button to identify it in logs and screenshots
            coordinates (tuple, optional): X, Y coordinates as tuple (x, y) if already known
            custom_prompt (str, optional): Custom prompt for the vision AI to find the button
            max_attempts (int, optional): Number of retry attempts if clicking fails
            
        Returns:
            bool: True if button was successfully clicked, False otherwise
            tuple: The coordinates used for clicking, or None if unsuccessful
        """
        self.logger.log(f"Attempting to click button: {button_name}")
        
        # If coordinates are provided, use them directly
        if coordinates:
            x, y = coordinates
            self.logger.log(f"Using provided coordinates for {button_name}: x={x}, y={y}")
            
            try:
                # Try using ActionChains for clicking at exact coordinates
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_by_offset(x, y).click().perform()
                ActionChains(self.driver).move_by_offset(-x, -y).perform()  # Reset position
                self.logger.log(f"Successfully clicked at provided coordinates: x={x}, y={y}")
                return True, (x, y)
            except Exception as e:
                self.logger.log(f"Failed to click at provided coordinates: {str(e)}", "error")
                # Fall back to vision detection if direct coordinate click fails
        
        # Default prompt for button detection
        if not custom_prompt:
            custom_prompt = f"Locate the '{button_name}' button in the image. The button might be blue or another color. Return only its exact screen coordinates in the format: x=..., y=.... If the button is not visible or not found, return NOT_FOUND."
        
        # Try multiple attempts to find and click the button
        for attempt in range(max_attempts):
            self.logger.log(f"Vision click attempt {attempt+1}/{max_attempts} for {button_name} button")
            
            # First make sure buttons might be visible
            viewport_height = self.driver.execute_script("return window.innerHeight;")
            doc_height = self.driver.execute_script("return document.body.scrollHeight;")
            
            # Use a more controlled scrolling approach - only scroll in small increments
            # Use a limited set of scroll positions instead of scrolling to the bottom
            scroll_positions = []
            
            # Start from current position (don't reset scroll position)
            current_scroll = self.driver.execute_script("return window.pageYOffset;")
            
            # Only add scroll positions that would be within the document height
            if attempt == 0:
                # On first attempt, stay at current position or go to top if we're already near the bottom
                if current_scroll > (doc_height * 0.7):  # If we're more than 70% down the page
                    scroll_positions.append(0)  # Go to top
                else:
                    scroll_positions.append(current_scroll)  # Stay at current position
            elif attempt == 1:
                # On second attempt, try a bit further down from current position (but not too far)
                next_position = current_scroll + 300
                if next_position < doc_height:
                    scroll_positions.append(next_position)
            elif attempt == 2:
                # On third attempt, try another position but still avoid bottom
                next_position = min(current_scroll + 600, doc_height * 0.7)  # Never go beyond 70% of page height
                scroll_positions.append(next_position)
            
            for position in scroll_positions:
                self.logger.log(f"Scrolling to position: {position}px")
                self.driver.execute_script(f"window.scrollTo(0, {position});")
                time.sleep(0.8)  # Wait for scroll to complete
                
                # Try clicking with vision detection
                success = click_button_with_vision(
                    driver=self.driver,
                    prompt=custom_prompt,
                    button_name=f"{button_name}_attempt{attempt}",
                    wait_for_scroll=True
                )
                
                if success:
                    # Try to extract the coordinates from the log
                    import re
                    log_file_path = "log.txt"  # Adjust path if needed
                    try:
                        with open(log_file_path, "r") as log_file:
                            log_content = log_file.read()
                            coord_match = re.search(r"FINAL CLICK COORDINATES: x=(\d+), y=(\d+)", log_content)
                            if coord_match:
                                x, y = int(coord_match.group(1)), int(coord_match.group(2))
                                self.logger.log(f"Extracted coordinates from successful click: x={x}, y={y}")
                                return True, (x, y)
                    except Exception as e:
                        self.logger.log(f"Could not extract coordinates from log: {str(e)}", "warning")
                    
                    return True, None  # Return True even if we couldn't extract coordinates
            
            # If current scroll positions failed, try a different scroll approach but avoid going to bottom
            if attempt < max_attempts - 1:  # Only for non-final attempts
                add_scroll = min(150 * (attempt + 1), 300)  # Cap the additional scroll
                current_scroll = self.driver.execute_script("return window.pageYOffset;")
                new_scroll = current_scroll + add_scroll
                
                # Make sure we don't scroll past 70% of document height
                new_scroll = min(new_scroll, doc_height * 0.7)
                
                self.logger.log(f"Trying additional scroll to position: {new_scroll}px")
                self.driver.execute_script(f"window.scrollTo(0, {new_scroll});")
                time.sleep(1)
        
        self.logger.log(f"Failed to click {button_name} button after {max_attempts} attempts", "error")
        return False, None

    def click_blue_button_with_cache(self, button_name, custom_prompt=None, max_attempts=3, force_detection=False):
        """
        Click a blue button using cached coordinates if available, or find and cache new coordinates.
        
        Args:
            button_name (str): Name of the button to identify it in logs and cache
            custom_prompt (str, optional): Custom prompt for the vision AI to find the button
            max_attempts (int, optional): Number of retry attempts if clicking fails
            force_detection (bool, optional): If True, bypass the cache and detect button coordinates again
            
        Returns:
            bool: True if button was successfully clicked, False otherwise
        """
        self.logger.log(f"Attempting to click blue button with cache: {button_name}")
        
        # Check if we have cached coordinates and not forcing detection
        if not force_detection and button_name in self.button_coordinates_cache:
            cached_coords = self.button_coordinates_cache[button_name]
            self.logger.log(f"Found cached coordinates for {button_name}: {cached_coords}")
            
            # Try clicking with cached coordinates first
            success, _ = self.click_button_with_coordinates(
                button_name=button_name,
                coordinates=cached_coords,
                max_attempts=1  # Only try once with cached coordinates
            )
            
            if success:
                self.logger.log(f"Successfully clicked {button_name} using cached coordinates")
                return True
            
            self.logger.log(f"Cached coordinates for {button_name} failed, will detect again")
        
        # If no cached coordinates or they failed, detect and cache new ones
        if not custom_prompt:
            custom_prompt = f"Locate the blue '{button_name}' button in the image. The button should be visible and clickable. Return only its exact screen coordinates in the format: x=..., y=.... Do not include any explanation or extra text. If the button is not visible or not found, return NOT_FOUND."
        
        # Use the coordinates function to get both success status and coordinates
        success, coords = self.click_button_with_coordinates(
            button_name=button_name,
            coordinates=None,  # Force new detection
            custom_prompt=custom_prompt,
            max_attempts=max_attempts
        )
        
        # If successful and we got coordinates, cache them for future use
        if success and coords:
            self.logger.log(f"Caching coordinates for {button_name}: {coords}")
            self.button_coordinates_cache[button_name] = coords
        
        return success
        
    def auto_click_all_blue_buttons(self, button_names, max_attempts=3):
        """
        Automatically click a sequence of blue buttons using cached coordinates when possible.
        
        Args:
            button_names (list): List of button names to click in sequence
            max_attempts (int, optional): Maximum attempts per button
            
        Returns:
            bool: True if all buttons were successfully clicked, False if any failed
        """
        all_successful = True
        
        for button_name in button_names:
            self.logger.log(f"Processing button: {button_name}")
            
            # Try clicking the button
            success = self.click_blue_button_with_cache(
                button_name=button_name,
                max_attempts=max_attempts
            )
            
            if not success:
                self.logger.log(f"Failed to click button: {button_name}", "error")
                all_successful = False
                break
            
            # Wait a bit between button clicks
            time.sleep(1.0)  # Reduced from 1.5 to 1.0 seconds
        
        return all_successful

    def fill_designated_partner_details(self):
        """
        Fill the designated partner details section in the form.
        This function fills fields in the "6 Particulars of individual designated partners" section.
        
        Fields to be filled:
        1. Designated partner identification number (DIN/DPIN) - Any random number
        2. Name - "Ashish"
        3. Whether resident of India - "Yes" (radio button)
        4. Number of shares held - Any number
        5. Paid up value of shares held (in INR) - Any amount
        6. Form of contribution - "Cash" (dropdown)
        7. Monetary value of contribution (in INR) - "10000"
        8. Monetary value of contribution (in words) - "Ten Thousand"
        9. Number of LLP(s) in which he/she is a partner - "1"
        10. Number of company(s) in which he/she is a director - "2"
        
        Returns:
            bool: True if all fields were filled successfully, False otherwise
        """
        try:
            self.logger.log("Starting to fill designated partner details...")
            
            # First, scroll to the designated partner section
            self.logger.log("Scrolling to designated partner section...")
            
            # Scroll down to the section after completing the industrial activities description
            section_xpaths = [
                "//*[contains(text(), '6 Particulars of individual designated partners')]",
                "//*[contains(text(), 'individual designated partners')]",
                "//*[contains(text(), 'Basic details of Designated partner')]",
                "//*[contains(text(), '(i) Basic details of Designated partner')]"
            ]
            
            section_found = False
            for xpath in section_xpaths:
                try:
                    section_elem = self.driver.find_element(By.XPATH, xpath)
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", section_elem)
                    section_found = True
                    self.logger.log("Found and scrolled to designated partner section")
                    time.sleep(1)  # Wait for scroll to complete
                    break
                except Exception:
                    continue
                    
            if not section_found:
                # If the main section isn't found, try to scroll to the DIN field directly
                din_field_xpaths = [
                    "//*[contains(text(), 'Designated partner identification number')]",
                    "//*[contains(text(), 'DIN/DPIN')]"
                ]
                
                for xpath in din_field_xpaths:
                    try:
                        din_field = self.driver.find_element(By.XPATH, xpath)
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", din_field)
                        section_found = True
                        self.logger.log("Found and scrolled to DIN field")
                        time.sleep(1)
                        break
                    except Exception:
                        continue
            
            if not section_found:
                self.logger.log("Could not find designated partner section. Will try to fill fields directly.", "warning")
            
            # Define the partner detail fields to fill
            partner_fields = [
                {"label": "Designated partner identification number", "value": "123456789", "type": "input",
                 "alt_labels": ["DIN", "DPIN", "DIN/DPIN"]},
                {"label": "Name", "value": "Ashish", "type": "input",
                 "alt_labels": ["Partner name", "Full name"]},
                {"label": "Number of shares held", "value": "100", "type": "input",
                 "alt_labels": ["Shares held", "Share count"]},
                {"label": "Paid up value of shares held", "value": "10000", "type": "input",
                 "alt_labels": ["Paid up value", "Share value"]},
                {"label": "Monetary value of contribution", "value": "10000", "type": "input",
                 "alt_labels": ["Contribution value", "Value of contribution"]},
                {"label": "Monetary value of contribution (in words)", "value": "Ten Thousand", "type": "input",
                 "alt_labels": ["Value in words", "Contribution in words"]},
                {"label": "Number of LLP", "value": "1", "type": "input",
                 "alt_labels": ["Number of LLP(s)", "LLP count"]},
                {"label": "Number of company", "value": "2", "type": "input",
                 "alt_labels": ["Number of company(s)", "Company count", "Companies"]}
            ]
            
            # Try to fill each field
            fields_filled = 0
            required_fields = len(partner_fields)
            
            for field_info in partner_fields:
                field_label = field_info["label"]
                field_value = field_info["value"]
                field_type = field_info["type"]
                alt_labels = field_info.get("alt_labels", [])
                
                self.logger.log(f"Looking for {field_label} field to fill with '{field_value}'")
                
                # Create XPath patterns for the field
                all_labels = [field_label] + alt_labels
                xpath_patterns = []
                
                # Build XPath patterns to find the input field
                for label in all_labels:
                    xpath_patterns.extend([
                        f"//label[contains(text(), '{label}')]/following::input[1]",
                        f"//*[contains(text(), '{label}')]/following::input[1]",
                        f"//input[@placeholder='{label}']",
                        f"//input[contains(@id, '{label.lower().replace(' ', '')}')]",
                        f"//input[contains(@name, '{label.lower().replace(' ', '')}')]"
                    ])
                
                # Try each XPath to find the field
                field_found = False
                input_field = None
                
                for xpath in xpath_patterns:
                    try:
                        input_field = self.driver.find_element(By.XPATH, xpath)
                        if input_field.is_displayed():
                            field_found = True
                            self.logger.log(f"Found {field_label} field")
                            break
                    except Exception:
                        continue
                
                # If no field found with XPath, try looking by surrounding text
                if not field_found:
                    try:
                        # Look for any text element containing the field label
                        label_elements = []
                        for label in all_labels:
                            label_elements.extend(self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{label}')]"))
                        
                        # For each label element found, look for an input nearby
                        for label_elem in label_elements:
                            if label_elem.is_displayed():
                                # Try to find an input in the same container
                                parent_div = label_elem
                                for _ in range(3):  # Try a few levels up
                                    try:
                                        parent_div = parent_div.find_element(By.XPATH, "..")
                                        inputs = parent_div.find_elements(By.TAG_NAME, "input")
                                        for inp in inputs:
                                            if inp.is_displayed():
                                                input_field = inp
                                                field_found = True
                                                self.logger.log(f"Found {field_label} field via parent container")
                                                break
                                        if field_found:
                                            break
                                    except:
                                        break
                            if field_found:
                                break
                    except Exception as e:
                        self.logger.log(f"Error searching for {field_label} by container: {str(e)}", "debug")
                
                # If field found, fill it
                if field_found and input_field:
                    # Scroll to the field
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", input_field)
                    time.sleep(0.3)
                    
                    try:
                        # Clear the field
                        try:
                            input_field.clear()
                        except:
                            self.driver.execute_script("arguments[0].value = '';", input_field)
                        
                        # Fill the field
                        input_field.send_keys(field_value)
                        
                        # Trigger events to ensure value is registered
                        self.driver.execute_script("""
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                        """, input_field)
                        
                        fields_filled += 1
                        self.logger.log(f"Successfully filled {field_label} with '{field_value}'")
                    except Exception as e:
                        self.logger.log(f"Error filling {field_label}: {str(e)}", "warning")
                else:
                    self.logger.log(f"Could not find {field_label} field", "warning")
            
            # Handle special fields
            
            # 1. Select "Yes" for whether resident of India
            self.logger.log("Selecting 'Yes' for 'Whether resident of India'")
            resident_xpaths = [
                "//label[contains(text(), 'resident of India')]/following::input[@type='radio'][1]",
                "//*[contains(text(), 'resident of India')]/following::input[@type='radio'][1]",
                "//input[@type='radio' and @value='Yes']"
            ]
            
            resident_clicked = False
            for xpath in resident_xpaths:
                try:
                    yes_radio = self.driver.find_element(By.XPATH, xpath)
                    if yes_radio.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", yes_radio)
                        time.sleep(0.3)
                        yes_radio.click()
                        resident_clicked = True
                        self.logger.log("Successfully selected 'Yes' for resident of India")
                        break
                except Exception as e:
                    continue
            
            if not resident_clicked:
                self.logger.log("Could not select 'Yes' for resident of India", "warning")
            
            # 2. Select "Cash" for Form of contribution dropdown
            self.logger.log("Selecting 'Cash' from the 'Form of contribution' dropdown")
            
            # First find the dropdown
            contribution_form_xpaths = [
                "//label[contains(text(), 'Form of contribution')]/following::select[1]",
                "//*[contains(text(), 'Form of contribution')]/following::select[1]",
                "//*[contains(text(), 'Form of contribution')]/following::div[contains(@class, 'dropdown')][1]",
                "//select[contains(@id, 'contribution') or contains(@name, 'contribution')]"
            ]
            
            dropdown_found = False
            for xpath in contribution_form_xpaths:
                try:
                    dropdown = self.driver.find_element(By.XPATH, xpath)
                    if dropdown.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", dropdown)
                        time.sleep(0.3)
                        
                        # Check if it's a standard SELECT element
                        if dropdown.tag_name.lower() == "select":
                            from selenium.webdriver.support.ui import Select
                            select = Select(dropdown)
                            
                            try:
                                select.select_by_visible_text("Cash")
                                dropdown_found = True
                                self.logger.log("Selected 'Cash' from form of contribution dropdown")
                            except:
                                # If exact match fails, try to find option containing "Cash"
                                for option in select.options:
                                    if "cash" in option.text.lower():
                                        select.select_by_visible_text(option.text)
                                        dropdown_found = True
                                        self.logger.log(f"Selected '{option.text}' from form of contribution dropdown")
                                        break
                        else:
                            # For custom dropdowns
                            dropdown.click()
                            time.sleep(0.5)  # Wait for dropdown to open
                            
                            # Try to find and click an option containing "Cash"
                            cash_options = self.driver.find_elements(By.XPATH, "//li[contains(text(), 'Cash')] | //div[contains(text(), 'Cash')] | //option[contains(text(), 'Cash')]")
                            for option in cash_options:
                                if option.is_displayed():
                                    option.click()
                                    dropdown_found = True
                                    self.logger.log("Selected 'Cash' option from custom dropdown")
                                    break
                        
                        if dropdown_found:
                            break
                except Exception as e:
                    continue
            
            if not dropdown_found:
                self.logger.log("Could not select 'Cash' from form of contribution dropdown", "warning")
                
                # Try JavaScript approach as fallback
                try:
                    self.driver.execute_script("""
                        // Try to find any dropdown or select element related to contribution
                        var dropdowns = document.querySelectorAll('select, [role="listbox"], .dropdown');
                        for (var i = 0; i < dropdowns.length; i++) {
                            var dropdown = dropdowns[i];
                            
                            // Look for contribution in nearby labels or text
                            var nearby = dropdown.parentElement.textContent.toLowerCase();
                            if (nearby.includes('contribution') || nearby.includes('form of')) {
                                if (dropdown.tagName === 'SELECT') {
                                    // For standard SELECT elements
                                    for (var j = 0; j < dropdown.options.length; j++) {
                                        if (dropdown.options[j].text.toLowerCase().includes('cash')) {
                                            dropdown.selectedIndex = j;
                                            dropdown.dispatchEvent(new Event('change', { bubbles: true }));
                                            console.log('Selected cash option via JS');
                                            return true;
                                        }
                                    }
                                } else {
                                    // For custom dropdowns, try to set a value
                                    dropdown.click();
                                    setTimeout(function() {
                                        var cashOptions = document.querySelectorAll('li, .option, .dropdown-item');
                                        for (var k = 0; k < cashOptions.length; k++) {
                                            if (cashOptions[k].textContent.toLowerCase().includes('cash')) {
                                                cashOptions[k].click();
                                                console.log('Selected cash from custom dropdown via JS');
                                                return true;
                                            }
                                        }
                                    }, 500);
                                }
                            }
                        }
                        return false;
                    """)
                    self.logger.log("Attempted to select 'Cash' using JavaScript approach")
                except Exception as e:
                    self.logger.log(f"JavaScript fallback for dropdown selection failed: {str(e)}", "warning")
            
            # Check how many fields were successfully filled
            success_rate = fields_filled / required_fields
            resident_success = 1 if resident_clicked else 0
            dropdown_success = 1 if dropdown_found else 0
            
            total_success = fields_filled + resident_success + dropdown_success
            total_fields = required_fields + 2  # +2 for the radio button and dropdown
            
            self.logger.log(f"Filled {total_success}/{total_fields} partner detail fields")
            
            return success_rate >= 0.7  # Return True if at least 70% of fields were filled
            
        except Exception as e:
            self.logger.log(f"Error filling designated partner details: {str(e)}", "error")
            return False
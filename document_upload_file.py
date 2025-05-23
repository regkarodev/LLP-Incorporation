from selenium.webdriver.common.by import By
import time
import os
import json

def handle_file_uploads(driver, config_data):
    """
    Handle file uploads in the attachments page
    """
    print("Handling file uploads...")
    
    # File paths from config
    file1_path = os.path.abspath(config_data["form_data"]["file_paths"]["third_file"])
    file2_path = os.path.abspath(config_data["form_data"]["file_paths"]["fourth_file"])
    
    # Check if the files exist
    if not os.path.exists(file1_path):
        print(f"Warning: File {file1_path} does not exist!")
        raise Exception(f"First file not found: {file1_path}")
    if not os.path.exists(file2_path):
        print(f"Warning: File {file2_path} does not exist!")
        raise Exception(f"Second file not found: {file2_path}")
    
    print(f"Using files:\n{file1_path}\n{file2_path}")
    
    # Get all the Choose File buttons
    choose_file_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'guide-fu-attach-button')]")
    print(f"Found {len(choose_file_buttons)} Choose File buttons")
    
    # FIRST FILE UPLOAD - Direct approach with file inputs
    # upload_first_file(driver, file1_path, choose_file_buttons)
    
    # SECOND FILE UPLOAD - Use the exact XPath provided
    upload_identity_file(driver, file1_path)
    # Upload first file
    upload_file(driver, file2_path)



def upload_identity_file(driver, file_path):

    """
    Upload the second file
    """
    print("\n--- SECOND FILE UPLOAD ---")
    try:
        # Use the exact XPath provided for the second Choose File button
        exact_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[2]/div/div/div[2]/div[1]/button"
        print(f"Using exact XPath for second Choose File button: {exact_xpath}")
        
        # Find the button using the exact XPath
        try:
            upload_button = driver.find_element(By.XPATH, exact_xpath)
            print("Found upload button using exact XPath")
            
            
            # Find the associated file input
            # First, get the parent container that contains both button and input
            parent_container = upload_button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'guideFieldWidget afFileUpload fileUpload')]")
            print("Found parent container")
            
            # Now find the input element within this container
            file_input = parent_container.find_element(By.XPATH, ".//input[@type='file']")
            print("Found file input element")
            
            # Make the file input visible and enabled
            print("Making file input visible and enabled...")
            driver.execute_script("""
                arguments[0].style.display = 'block';
                arguments[0].style.visibility = 'visible';
                arguments[0].style.opacity = '1';
                arguments[0].disabled = false;
                arguments[0].setAttribute('class', 'visible');
            """, file_input)
            time.sleep(2)  # Give more time for the element to become interactive
            
            # Send the file path
            print(f"Sending file path: {file_path}")
            file_input.send_keys(file_path)
            print("File path sent to input element")
            time.sleep(3)
            
            # Verify upload by checking for filename in UI
            try:
                # Extract just the filename from the path for verification
                filename = os.path.basename(file_path)
                
                # Look for the filename text
                filename_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{filename}')]")
                print("SUCCESS: Second file appears to have uploaded successfully")
            except:
                print("WARNING: Second file may not have uploaded - no confirmation in UI")
                
                # Try a more direct approach
                print("Trying alternative approach...")
                
                # Try to directly get all file inputs and use the second one
                file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                print(f"Found {len(file_inputs)} file input elements")
                
                if len(file_inputs) >= 2:
                    # Try with the second file input
                    second_input = file_inputs[1]
                    
                    # Make it visible and enabled
                    driver.execute_script("""
                        arguments[0].style.display = 'block';
                        arguments[0].style.visibility = 'visible';
                        arguments[0].style.opacity = '1';
                        arguments[0].disabled = false;
                        arguments[0].setAttribute('class', 'visible');
                    """, second_input)
                    time.sleep(2)
                    
                    # Send file path
                    second_input.send_keys(file_path)
                    print("File path sent using alternative approach")
                    time.sleep(3)
                    
                    # Check if it worked
                    try:
                        filename_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{filename}')]")
                        print("SUCCESS: Second file uploaded with alternative approach")
                    except:
                        print("WARNING: Alternative approach also failed")
                        print("Please manually upload the second file")
                        input("Press Enter after manually uploading the second file...")
                else:
                    print("Not enough file input elements found")
                    print("Please manually upload the second file")
                    input("Press Enter after manually uploading the second file...")
        except Exception as e:
            print(f"Error with XPath approach: {e}")
            
            # Try a completely different approach - JavaScript execution
            print("Trying JavaScript approach...")
            try:
                # Use JavaScript to find and interact with the file input
                script = """
                // Find all file inputs
                var fileInputs = document.querySelectorAll('input[type="file"]');
                
                // Make sure we have at least 2 file inputs
                if (fileInputs.length >= 2) {
                    // Get the second file input
                    var secondInput = fileInputs[1];
                    
                    // Make it visible and enabled
                    secondInput.style.display = 'block';
                    secondInput.style.visibility = 'visible';
                    secondInput.style.opacity = '1';
                    secondInput.disabled = false;
                    
                    // Return the element so we can use it
                    return secondInput;
                }
                return null;
                """
                
                # Execute the script
                file_input = driver.execute_script(script)
                
                if file_input:
                    print("Found file input using JavaScript")
                    
                    # Send the file path
                    file_input.send_keys(file_path)
                    print("File path sent using JavaScript approach")
                    time.sleep(3)
                else:
                    print("JavaScript approach failed to find file input")
                    print("Please manually upload the second file")
                    input("Press Enter after manually uploading the second file...")
            except Exception as js_error:
                print(f"JavaScript approach failed: {js_error}")
                print("Please manually upload the second file")
                input("Press Enter after manually uploading the second file...")
    except Exception as e:
        print(f"Error with second file upload: {e}")
        print("Please manually upload the second file")
        input("Press Enter after manually uploading the second file...") 



def upload_file(driver, file_path):
    """
    Upload file with enhanced input element detection
    """
    print("\n--- FILE UPLOAD ---")
    try:
        # Use the exact XPath provided for the Choose File button
        exact_xpath = "/html/body/div[2]/div/div/div/div/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[6]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/div[19]/div/div/div/div[1]/div/div[3]/div/div/div/div[1]/div/div[4]/div/div/div/div[1]/div/div[15]/div/div/div/div[1]/div/div[3]/div/div/div[2]/div[1]/button"
        print(f"Using exact XPath for Choose File button: {exact_xpath}")
        
        # Find the button using the exact XPath
        try:
            upload_button = driver.find_element(By.XPATH, exact_xpath)
            print("Found upload button using exact XPath")
            
            # Find the associated file input
            # First, get the parent container that contains both button and input
            parent_container = upload_button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'guideFieldWidget afFileUpload fileUpload')]")
            print("Found parent container")
            
            # Now find the input element within this container
            file_input = parent_container.find_element(By.XPATH, ".//input[@type='file']")
            print("Found file input element")
            
            # Get the input element's ID
            input_id = file_input.get_attribute('id')
            print(f"Found input element ID: {input_id}")
            
            # Make the file input visible and enabled
            print("Making file input visible and enabled...")
            driver.execute_script("""
                arguments[0].style.display = 'block';
                arguments[0].style.visibility = 'visible';
                arguments[0].style.opacity = '1';
                arguments[0].disabled = false;
                arguments[0].setAttribute('class', 'visible');
            """, file_input)
            time.sleep(2)  # Give more time for the element to become interactive
            
            # Send the file path
            print(f"Sending file path: {file_path}")
            file_input.send_keys(file_path)
            print("File path sent to input element")
            time.sleep(3)
            
            # Verify upload by checking for filename in UI
            try:
                # Extract just the filename from the path for verification
                filename = os.path.basename(file_path)
                
                # Look for the filename text
                filename_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{filename}')]")
                print("SUCCESS: File appears to have uploaded successfully")
            except:
                print("WARNING: File may not have uploaded - no confirmation in UI")
                
                # Try a more direct approach using the ID we found
                print("Trying alternative approach with ID...")
                try:
                    # Try to find the input using its ID
                    input_by_id = driver.find_element(By.ID, input_id)
                    print(f"Found input element by ID: {input_id}")
                    
                    # Make it visible and enabled
                    driver.execute_script("""
                        arguments[0].style.display = 'block';
                        arguments[0].style.visibility = 'visible';
                        arguments[0].style.opacity = '1';
                        arguments[0].disabled = false;
                        arguments[0].setAttribute('class', 'visible');
                    """, input_by_id)
                    time.sleep(2)
                    
                    # Send file path
                    input_by_id.send_keys(file_path)
                    print("File path sent using ID-based approach")
                    time.sleep(3)
                    
                    # Check if it worked
                    try:
                        filename_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{filename}')]")
                        print("SUCCESS: File uploaded with ID-based approach")
                    except:
                        print("WARNING: ID-based approach also failed")
                        print("Please manually upload the file")
                        input("Press Enter after manually uploading the file...")
                except Exception as id_error:
                    print(f"Error with ID-based approach: {id_error}")
                    print("Please manually upload the file")
                    input("Press Enter after manually uploading the file...")
        except Exception as e:
            print(f"Error with XPath approach: {e}")
            
            # Try a completely different approach - JavaScript execution
            print("Trying JavaScript approach...")
            try:
                # Use JavaScript to find and interact with the file input
                script = """
                // Find all file inputs
                var fileInputs = document.querySelectorAll('input[type="file"]');
                
                // Make sure we have at least one file input
                if (fileInputs.length >= 1) {
                    // Get the first file input
                    var input = fileInputs[0];
                    
                    // Make it visible and enabled
                    input.style.display = 'block';
                    input.style.visibility = 'visible';
                    input.style.opacity = '1';
                    input.disabled = false;
                    
                    // Return the element so we can use it
                    return input;
                }
                return null;
                """
                
                # Execute the script
                file_input = driver.execute_script(script)
                
                if file_input:
                    print("Found file input using JavaScript")
                    
                    # Send the file path
                    file_input.send_keys(file_path)
                    print("File path sent using JavaScript approach")
                    time.sleep(3)
                else:
                    print("JavaScript approach failed to find file input")
                    print("Please manually upload the file")
                    input("Press Enter after manually uploading the file...")
            except Exception as js_error:
                print(f"JavaScript approach failed: {js_error}")
                print("Please manually upload the file")
                input("Press Enter after manually uploading the file...")
    except Exception as e:
        print(f"Error with file upload: {e}")
        print("Please manually upload the file")
        input("Press Enter after manually uploading the file...") 
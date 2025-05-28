from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Initialize your driver
driver = webdriver.Firefox()  # or Chrome()

# Navigate to your form (after logging in and reaching the partner details section)
# Make sure to replace "YOUR_FORM_URL" with the actual URL
# For example: driver.get("https://example.com/your_form_page")
# For demonstration, I'll use a dummy page. You should use your actual URL.
driver.get("data:text/html,<html><body><h1>Form Page</h1> \
           <input aria-label='First Name' value=''><input aria-label='Surname' value=''> \
           <input aria-label='First Name' value=''><input aria-label='Surname' value=''> \
           <input aria-label='Contribution amount' value=''> \
           <select aria-label='Gender'><option>Male</option></select> \
           <input type='text' aria-label='DIN Number'> \
           <input type='checkbox' aria-label='Whether resident of India'> \
           </body></html>")


# Wait for page to load
time.sleep(2) # Reduced for dummy page, adjust as needed for your actual page

# Find all elements with aria-label
elements_with_aria = driver.find_elements(By.CSS_SELECTOR, "[aria-label]")

print(f"Found {len(elements_with_aria)} elements with aria-label\n")

# Group by aria-label value
aria_labels = {}
for element in elements_with_aria:
    label = element.get_attribute('aria-label')
    tag = element.tag_name
    element_type = element.get_attribute('type') or '' # Get type, default to empty string if not present
    
    # Construct a descriptive string for the element
    element_desc = f"{tag}"
    if element_type:
        element_desc += f"[type={element_type}]"

    if label not in aria_labels:
        aria_labels[label] = []
    
    # Add unique descriptions only
    if element_desc not in aria_labels[label]:
        aria_labels[label].append(element_desc)

# Print unique aria-labels
print("Unique aria-labels found:")
print("-" * 50)
for label, elements_descs in sorted(aria_labels.items()):
    print(f"\nLabel: '{label}'")
    print(f"Element types found: {', '.join(elements_descs)}") # elements_descs is now a list of unique tag[type] strings
    print(f"CSS Selector Example: [aria-label='{label}']")
    # It's better to suggest XPath for elements that might not be input, or to be more general
    # The tag can vary, so *[@aria-label='...'] is more general for XPath
    print(f"General XPath Example: //*[@aria-label='{label}']")


# Find partner-specific fields
print("\n\nPartner-specific fields (based on keywords):")
print("-" * 50)
partner_keywords = ['DIN', 'DPIN', 'contribution', 'LLP', 'company', 'resident', 'First Name', 'Surname', 'Gender'] # Added more for testing
for label in aria_labels:
    if any(keyword.lower() in label.lower() for keyword in partner_keywords): # Case-insensitive check
        # Use general XPath to count, as tag might vary (e.g., input, select, textarea)
        count = len(driver.find_elements(By.XPATH, f"//*[@aria-label='{label}']"))
        print(f"\n'{label}' - Found {count} instances")
        
        # Show XPath selectors for multiple instances
        if count > 0: # Changed from > 1 to show for single instances too
            print(f"  XPath selectors for each instance (example assuming input, adjust tag if needed):")
            for i in range(1, count + 1):
                # Suggest a more general XPath, but also specific if tag is known
                # For this example, we don't know the exact tag for each aria-label universally here
                # So, //* is safer for a general suggestion.
                print(f"    Instance {i}: (//*[@aria-label='{label}'])[{i}]")

# Test XPath selectors
print("\n\nTesting XPath selectors for specific partner fields:")
print("-" * 50)

# CORRECTED: test_fields should be a list of strings (the aria-labels you want to test)
test_fields = [
    "First Name",
    "Middle Name", # This might not exist on the dummy page, good for testing "not found"
    "Surname",
    "Father Name",
    "Father Middle Name",
    "Father Surname",
    "Gender",
    "Date of Birth",
    "Nationality",
    "Whether resident of India",
    "Income-tax PAN/Passport number", # This exact label might not exist
    "Income-tax PAN/Passport number details",
    "Place of Birth (State)",
    "Place of Birth (District)",
    "Occupation type",
    "Area of Occupation",
    "Educational qualification",
    "Mobile No",
    "Email ID", # This exact label might not exist
    "Address Line I",
    "Address Line II",
    "Country",
    "Pin code / Zip Code",
    "Area/ Locality",
    "Jurisdiction of Police Station",
    "Phone (with STD/ISD code)",
    "present_permanent_same", # This is likely not an aria-label, but a conceptual field name
    "Identity Proof",
    "Residential Proof",
    "Identity Proof No.",
    "Residential Proof No.",
    "Form of contribution",
    "Contribution amount", # Added from dummy page
    "Monetary value of contribution (in INR.) (in figures)",
    "Number of LLP(s) in which he/ she is a partner",
    "Number of company(s) in which he/ she is a director",
    "DIN Number" # Added from dummy page
]

for field_label in test_fields:
    try:
        # Find all instances using a general XPath (any tag)
        # This allows testing for labels on <input>, <select>, <textarea>, etc.
        elements = driver.find_elements(By.XPATH, f"//*[@aria-label='{field_label}']")
        if elements:
            print(f"\n'{field_label}':")
            print(f"  Found {len(elements)} elements with this aria-label")
            # Test accessing each one
            for i in range(1, len(elements) + 1): # Iterate up to the actual number of elements found
                try:
                    # Use the general XPath for finding the i-th element
                    element = driver.find_element(By.XPATH, f"(//*[@aria-label='{field_label}'])[{i}]")
                    print(f"  ✓ XPath position [{i}] - Tag: {element.tag_name}, Visible: {element.is_displayed()}, Enabled: {element.is_enabled()}")
                except Exception as e_inner:
                    print(f"  ✗ Error accessing XPath position [{i}] for '{field_label}': {str(e_inner)}")
        else:
            print(f"\n'{field_label}': Not found on page.")
            
    except Exception as e:
        print(f"\nError testing '{field_label}': {str(e)}")

input("\nPress Enter to close browser...")
driver.quit()
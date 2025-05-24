from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Initialize your driver
driver = webdriver.Firefox()  # or Chrome()

# Navigate to your form (after logging in and reaching the partner details section)
# driver.get("YOUR_FORM_URL")

# Wait for page to load
time.sleep(5)

# Find all elements with aria-label
elements_with_aria = driver.find_elements(By.CSS_SELECTOR, "[aria-label]")

print(f"Found {len(elements_with_aria)} elements with aria-label\n")

# Group by aria-label value
aria_labels = {}
for element in elements_with_aria:
    label = element.get_attribute('aria-label')
    tag = element.tag_name
    element_type = element.get_attribute('type') or ''
    
    if label not in aria_labels:
        aria_labels[label] = []
    aria_labels[label].append(f"{tag}[type={element_type}]")

# Print unique aria-labels
print("Unique aria-labels found:")
print("-" * 50)
for label, elements in sorted(aria_labels.items()):
    print(f"\nLabel: '{label}'")
    print(f"Elements: {', '.join(set(elements))}")
    print(f"CSS Selector: [aria-label='{label}']")

# Find partner-specific fields
print("\n\nPartner-specific fields:")
print("-" * 50)
partner_keywords = ['DIN', 'DPIN', 'contribution', 'LLP', 'company', 'resident']
for label in aria_labels:
    if any(keyword in label for keyword in partner_keywords):
        count = len(driver.find_elements(By.CSS_SELECTOR, f"[aria-label='{label}']"))
        print(f"\n'{label}' - Found {count} instances")
        
        # Show XPath selectors for multiple instances
        if count > 1:
            print(f"  XPath selectors for each instance:")
            for i in range(1, count + 1):
                print(f"    Partner {i}: (//input[@aria-label='{label}'])[{i}]")

# Test XPath selectors
print("\n\nTesting XPath selectors for partner fields:")
print("-" * 50)

test_fields = [
    "Designated partner identification number (DIN/DPIN)",
    "Form of contribution",
    "Monetary value of contribution (in INR) (in figures)",
    "Number of LLP(s) in which he/ she is a partner",
    "Number of company(s) in which he/ she is a director"
]

for field in test_fields:
    try:
        # Find all instances using XPath
        elements = driver.find_elements(By.XPATH, f"//input[@aria-label='{field}']")
        if elements:
            print(f"\n'{field}':")
            print(f"  Found {len(elements)} elements")
            # Test accessing each one
            for i in range(1, min(len(elements) + 1, 6)):  # Test up to 5
                try:
                    element = driver.find_element(By.XPATH, f"(//input[@aria-label='{field}'])[{i}]")
                    print(f"  ✓ XPath position [{i}] - Found: {element.tag_name}, visible: {element.is_displayed()}")
                except:
                    print(f"  ✗ XPath position [{i}] - Not found")
    except Exception as e:
        print(f"\nError testing '{field}': {str(e)}")

input("\nPress Enter to close browser...") 
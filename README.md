# LLP Incorporation Form Automation

This project automates the filling of the LLP (Limited Liability Partnership) incorporation form, specifically handling partners without DIN/DPIN.

## Features

### 1. Partner Information Handling
- Processes up to 8 partners without DIN/DPIN
- Minimum iteration based on "Individuals Not having valid DIN/DPIN" value
- Tracks success and failure counts for each partner
- Maintains running totals for all fields filled and failed

### 2. Personal Information Section
- First Name, Middle Name, Surname
- Father's Name (First, Middle, Surname)
- Gender selection
- Date of Birth
- Nationality
- Whether resident of India (radio button)
- Income-tax PAN/Passport number selection
- PAN/Passport number details with verification
- Place of Birth (State and District)
- Whether citizen of India
- Occupation type and details
- Educational qualification
- Contact Information (Mobile and Email)

### 3. Permanent Address Section
- Address Line I
- Address Line II (using specific XPath)
- Country
- Pin code / Zip Code
- Area/ Locality
- Auto-populated fields:
  - City
  - District
  - State / UT
- Jurisdiction of Police Station
- Phone (with STD/ISD code) (using specific XPath)

### 4. Present Address Section
- Whether present residential address same as permanent residential address (radio button)
- If different:
  - Address Line I
  - Address Line II (using specific XPath)
  - Country
  - Pin code / Zip Code
  - Area/ Locality
  - City
  - District
  - State / UT
  - Jurisdiction of Police Station
  - Phone (with STD/ISD code) (using specific XPath)
  - Duration of stay (Years and Months)

### 5. Identity and Residential Proof Section
- Identity Proof selection (using specific XPath)
- Residential Proof selection
- Identity Proof No.
- Residential Proof No.

## Technical Implementation

### XPath Usage
The script uses specific XPaths for critical fields:
- Whether resident of India: `//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_406391466-guidecheckbox_copy_c_1044176976___guide-item"]`
- Present Address Line II: `//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy___guide-item"]`
- Phone (with STD/ISD code): `//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1161909677-guidetextbox_copy_165380706___guide-item"]`
- Identity Proof: `//*[@id="guideContainer-rootPanel-panel-panel_1815470267-panel_1379931518_cop-panel-panel_1228427250-panel-panel-panel_1688891306-guidedropdownlist___guide-item"]`

### Error Handling
- Comprehensive error handling for each field
- Detailed logging of success and failures
- Fallback mechanisms for field interactions
- Verification of field values after setting

### Field Interaction Methods
1. Direct Selenium interactions
2. JavaScript execution for:
   - Removing readonly/disabled attributes
   - Setting field values
   - Triggering necessary events
   - Ensuring visibility
3. Multiple fallback methods for clicking and value setting

### Data Structure
The script expects data in the following format:
```json
{
    "form_data": {
        "fields": {
            "Individuals Not having valid DIN/DPIN": "number"
        }
    },
    "partners_without_din": [
        {
            "options": {
                "Same address": {
                    "Yes": true,
                    "No": false
                },
                "Whether resident of India": {
                    "Yes": true,
                    "No": false
                }
            },
            "First Name": "value",
            "Middle Name": "value",
            "Surname": "value",
            // ... other partner fields
        }
    ]
}
```

## Usage

1. Ensure all dependencies are installed
2. Prepare the configuration data in the required JSON format
3. Run the script with the appropriate driver and configuration

## Dependencies
- Selenium WebDriver
- Python 3.x
- Required Python packages:
  - selenium
  - json
  - time

## Notes
- The script includes appropriate waits and delays for dynamic content
- All field interactions include visibility and interactability checks
- Comprehensive logging for debugging and monitoring
- Handles both mandatory and optional fields appropriately

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Specify your license here]

## Support

For support, please [specify contact information or support channels] 
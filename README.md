# MCA Automation Project

This project automates various tasks related to the Ministry of Corporate Affairs (MCA) portal, including document uploads, form submissions, and other administrative tasks.

## Features

- Automated login to MCA portal
- Document upload automation
- Form filling automation
- Captcha solving integration
- Firefox profile management
- Screenshot capture for verification
- Configurable settings via JSON

## Prerequisites

- Python 3.x
- Firefox browser
- TrueCaptcha account (for captcha solving)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mca_automation
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your TrueCaptcha credentials:
```
TRUECAPTCHA_USER=your_username_here
TRUECAPTCHA_KEY=your_api_key_here
```

4. Configure Firefox profile path in `config.json`:
```json
{
    "firefox_profile_path": "path/to/your/firefox/profile",
    "fillip_url": "https://www.mca.gov.in/content/mca/global/en/mca/llp-e-filling/Fillip.html"
}
```

## Project Structure

- `main.py` - Main entry point and core functionality
- `automate1.py` - Automation utilities and helper functions
- `function1.py` - Additional utility functions
- `config.json` - Configuration settings
- `config_data.json` - Additional configuration data
- `document_upload_file.py` - Document upload functionality
- `attachment_upload.py` - Attachment handling
- `last_upload.py` - Last upload tracking
- `screenshots/` - Directory for captured screenshots
- `firefox_profile/` - Firefox profile directory
- `extra code/` - Additional code snippets and utilities

## Usage

1. Ensure your Firefox profile is properly configured in `config.json`

2. Run the main script:
```bash
python main.py
```

3. The script will:
   - Initialize the Firefox browser
   - Log in to the MCA portal
   - Handle captcha solving
   - Perform the configured automation tasks

## Configuration

### Firefox Profile
The project uses a Firefox profile for persistent sessions. Configure the path in `config.json`:
```json
{
    "firefox_profile_path": "path/to/your/firefox/profile"
}
```

### TrueCaptcha Integration
For captcha solving, create a `.env` file with your TrueCaptcha credentials:
```
TRUECAPTCHA_USER=your_username_here
TRUECAPTCHA_KEY=your_api_key_here
```

## Error Handling

The project includes comprehensive error handling for:
- Login failures
- Captcha solving issues
- Network connectivity problems
- Browser automation errors

## Screenshots

The project automatically captures screenshots in the `screenshots/` directory for:
- Captcha images
- Error states
- Important form submissions

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
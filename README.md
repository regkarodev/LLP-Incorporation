# MCA Automation

This is a modular automation script for the MCA (Ministry of Corporate Affairs) website.

## Project Structure

```
mca_automation/
├── src/
│   ├── __init__.py
│   ├── logger.py
│   ├── browser_manager.py
│   ├── navigation_manager.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Make sure you have Firefox installed
2. Update the Firefox profile path in `main.py` if needed
3. Run the script:
```bash
python src/main.py
```

## Features

- Modular code structure for better maintainability
- Comprehensive logging to both console and file
- Persistent Firefox profile for session management
- Automatic popup handling
- Manual login support with session preservation

## Logging

Logs are written to both:
- Console output
- `mca_automation.log` file

## Notes

- The script uses a persistent Firefox profile to maintain sessions
- Manual login is required for security reasons
- The browser will stay open for manual interaction after automation steps 
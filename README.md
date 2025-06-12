# LLP Incorporation API

This API provides endpoints for handling LLP incorporation form data and file uploads. It wraps the existing Selenium-based automation in a user-friendly REST API interface.

## Features

- Process bodies corporate data and fill the LLP incorporation form
- Upload nominee resolution proofs
- Swagger/OpenAPI documentation
- Error handling and validation

## Prerequisites

- Python 3.7+
- Chrome browser installed
- ChromeDriver compatible with your Chrome version

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the API server:
```bash
python api.py
```

2. Access the Swagger documentation:
```
http://localhost:5000/api/docs
```

## API Endpoints

### 1. Process Bodies Corporate Data

**Endpoint:** `POST /api/bodies-corporate`

Processes the provided bodies corporate data and fills the LLP incorporation form.

**Request Body:**
```json
{
  "form_data": {
    "fields": {
      "Body corporates and their nominees Having valid DIN/DPIN": 1
    }
  },
  "bodies_corporate_with_din": [
    {
      "Type of body corporate": "Company",
      "CIN/FCRN": "L12345KA2020PTC123456",
      "PAN": "ABCDE1234F",
      "Name of the body corporate": "Example Corp",
      "Address Line I": "123 Main St",
      "Address Line II": "Suite 100",
      "Country": "India",
      "Pin code": "560001",
      "Area/ Locality": "Bangalore",
      "Jurisdiction of Police Station": "Central",
      "Phone (with STD/ISD code)": "+91-80-12345678",
      "Mobile No": "9876543210",
      "Fax": "+91-80-12345679",
      "Email ID": "contact@example.com",
      "Form of contribution": "Cash",
      "Monetary value of contribution (in INR) (in figures)": "100000",
      "Number of LLP(s) in which entity is a partner": "0",
      "Number of company(s) in which entity is a director": "0",
      "DIN/DPIN": "1234567890",
      "Name": "John Doe",
      "Whether resident of India": {
        "Yes": true
      },
      "Designation and Authority in body corporate": "Director",
      "Copy of resolution": "/path/to/resolution.pdf"
    }
  ]
}
```

### 2. Upload Nominee Resolution Proofs

**Endpoint:** `POST /api/upload-nominee-resolution`

Uploads nominee resolution proofs for bodies corporate.

**Request Body:**
```json
{
  "bodies_corporate_with_din": [
    {
      "Copy of resolution": "/path/to/resolution.pdf"
    }
  ]
}
```

## Response Format

All endpoints return responses in the following format:

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Successfully processed bodies corporate data"
}
```

**Error Response (400/500):**
```json
{
  "status": "error",
  "message": "Error message here"
}
```

## Error Handling

The API includes comprehensive error handling for:
- Invalid input data
- Missing required fields
- File not found errors
- Selenium automation errors
- Server errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
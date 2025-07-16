# LLP Incorporation Automation

This project automates the process of LLP (Limited Liability Partnership) incorporation by handling form filling, document uploads, and data processing through browser automation. The system now supports advanced document handling with blob-based file uploads for improved reliability and performance.

## Features

- **Automated Form Filling**: Complete automation of LLP incorporation forms
- **Advanced Document Upload**: Blob-based document handling for all file types
- **Multi-Partner Support**: Handle multiple designated partners with and without DIN
- **Corporate Body Processing**: Support for body corporates and their nominees
- **Browser Automation**: Firefox-based automation with profile management
- **API Server**: RESTful API for handling automation requests
- **Real-time Status Updates**: Progress tracking and status monitoring
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Error Recovery**: Robust error handling and recovery mechanisms

## Enhanced Document Handling

The system now supports advanced document upload capabilities:

### Blob-Based File Processing
- All documents are converted to blobs for secure transmission
- Support for multiple file formats (PDF, DOC, DOCX, JPG, PNG, etc.)
- File metadata preservation (name, type, size)
- Efficient memory management for large files

### Document Categories
- **Main Attachments**: Proof of office, utility bills, optional attachments, subscriber sheets
- **Partner Documents**: Identity proofs and residential proofs for partners without DIN
- **Corporate Documents**: Resolution copies for body corporates with DIN
- **Nominee Documents**: Identity proofs, residential proofs, and resolutions for corporate nominees

### File Upload Structure
```javascript
uploads: {
    // Main attachments
    proofOfOffice: { name, type, size, blob },
    utilityBill: { name, type, size, blob },
    optionalAttachments: { name, type, size, blob },
    subscribersSheet: { name, type, size, blob },
    
    // Partner documents (array)
    partnersWithoutDinDocuments: [
        {
            proofIdentity: { name, type, size, blob },
            residentialProof: { name, type, size, blob }
        }
    ],
    
    // Corporate documents (array)
    bodiesCorporateWithDinDocuments: [
        {
            resolution: { name, type, size, blob }
        }
    ],
    
    // Nominee documents (array)
    bodiesCorporateNomineeNoDinDocuments: [
        {
            nomineeProofIdentity: { name, type, size, blob },
            nomineeResidentialProof: { name, type, size, blob },
            resolution: { name, type, size, blob }
        }
    ]
}
```

## Project Structure

```
├── api_main.py                    # Main API server implementation
├── automation_worker.py           # Core automation logic
├── automate1.py                  # Form filling automation
├── function1.py                  # Utility functions
├── main.py                       # Main execution script
├── index.html                    # Web interface with blob handling
├── area_code.json               # Area code mappings
├── bodies_corporate_with_din.py  # Corporate body processing
├── bodies_corporate_without_din.py # Corporate nominee processing
├── partners_without_din.py       # Partner processing
├── document_upload_file.py       # Document upload utilities
├── attachment_upload.py          # Attachment handling
├── logger.py                     # Logging configuration
├── firefox_profile/              # Firefox profile directory
├── screenshots/                  # Automation screenshots
├── static/                       # Static assets
├── extra code/                   # Additional utilities and notebooks
├── requirements.txt              # Project dependencies
└── README.md                     # This file
```

## Prerequisites

- Python 3.8 or higher
- Firefox browser (latest version recommended)
- GeckoDriver (automatically installed by webdriver-manager)
- Modern web browser for the web interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd LLP_incorporation
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure Firefox is installed on your system

## Configuration

### Web Interface Configuration
The web interface (`index.html`) provides a user-friendly way to:
- Fill all form fields
- Upload documents with drag-and-drop support
- Preview uploaded files
- Validate form data before submission

### API Configuration
Update the API endpoint in `index.html` if needed:
```javascript
const response = await fetch('http://65.0.202.146:8009/api/automate', {
    method: 'POST',
    headers: {
        'Accept': 'application/json'
    },
    body: formData  // FormData with blobs
});
```

## Usage

### Web Interface
1. Open `index.html` in a modern web browser
2. Fill in all required form fields
3. Upload necessary documents
4. Click "Submit" to start automation

### API Server
```bash
python api_main.py
```
The API server will start and listen for automation requests on `http://65.0.202.146:8009`.

### Direct Automation
```bash
python main.py
```
This will execute the automation process directly without the web interface.

## API Endpoints

### POST /api/automate
Handles automation requests with blob-based document uploads.

**Request Format:**
- Content-Type: `multipart/form-data`
- Body: FormData containing JSON config and file blobs

**Response:**
```json
{
    "status": "success",
    "task_id": "unique_task_identifier",
    "message": "Automation started successfully"
}
```

## Components

### Web Interface (index.html)
- Modern, responsive UI built with Tailwind CSS
- Real-time form validation
- Document upload with preview
- Blob-based file handling
- Progress tracking

### API Server (api_main.py)
- RESTful API implementation
- Multipart form data handling
- Blob processing and storage
- Task management and status tracking
- Error handling and recovery

### Automation Worker (automation_worker.py)
- Core automation logic
- Browser session management
- Profile handling
- Document upload automation
- Error recovery mechanisms

### Form Automation (automate1.py)
- Form filling sequence
- Document upload handling
- Partner data processing
- Corporate body handling
- Validation and error checking

### Document Processing
- **document_upload_file.py**: File upload utilities
- **attachment_upload.py**: Attachment handling
- **bodies_corporate_with_din.py**: Corporate body processing
- **bodies_corporate_without_din.py**: Corporate nominee processing
- **partners_without_din.py**: Partner processing

## Error Handling

The system implements comprehensive error handling:
- **Browser Session Recovery**: Automatic session restoration on failures
- **Form Submission Retries**: Intelligent retry mechanisms
- **Document Upload Validation**: File type and size validation
- **API Request Validation**: Input validation and sanitization
- **Blob Processing Errors**: Graceful handling of file conversion errors

## Logging

The system uses Python's logging module for:
- Automation progress tracking
- Error reporting and debugging
- Document upload status
- API request/response logging
- Session management information

## Performance Optimizations

- **Blob Processing**: Efficient file handling without temporary storage
- **Memory Management**: Optimized memory usage for large files
- **Parallel Processing**: Concurrent document processing where possible
- **Caching**: Intelligent caching of frequently used data

## Security Features

- **File Validation**: Type and size validation for all uploads
- **Input Sanitization**: Protection against malicious input
- **Secure Transmission**: Blob-based secure file transmission
- **Error Masking**: Sensitive information protection in logs

## Troubleshooting

### Common Issues
1. **Firefox Profile Issues**: Clear the `firefox_profile` directory
2. **Document Upload Failures**: Check file size and format restrictions
3. **API Connection Errors**: Verify server is running on correct port
4. **Blob Processing Errors**: Ensure browser supports FileReader API

### Debug Mode
Enable debug logging by setting the log level in `logger.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Specify your license here]

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the logging output for error details

## Changelog

### Version 2.0.0
- Added blob-based document handling
- Implemented web interface with modern UI
- Enhanced error handling and recovery
- Added comprehensive logging
- Improved performance and security

### Version 1.0.0
- Initial release with basic automation
- Form filling capabilities
- Document upload support
- API server implementation 
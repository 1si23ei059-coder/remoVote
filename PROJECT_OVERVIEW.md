# WebAPI-Python Project Overview

## Project Description
A Flask-based web application that interfaces with SecuGen fingerprint scanning hardware via WebAPI. The application provides a web interface for capturing fingerprints, displaying scan results, and comparing fingerprint templates.

## Project Structure

```
WebAPI-Python/
├── app.py                          # Main Flask application
├── web.config                      # IIS configuration for deployment
├── Deployment_Directions.txt       # Server deployment instructions
├── templates/                      # HTML templates
│   ├── home.html                  # Landing page with navigation
│   ├── SimpleScan.html            # Simple fingerprint capture interface
│   ├── AdvancedScan.html          # Advanced capture with configurable parameters
│   ├── display_image.html         # Display captured fingerprint image and metadata
│   ├── scan1.html                 # First scan for comparison workflow
│   ├── scan2.html                 # Second scan for comparison workflow
│   ├── compare.html               # Compare two fingerprint templates
│   ├── match_score.html           # Display matching score results
│   └── error.html                 # Error display page
└── Logs/
    └── app.log                    # Application logs
```

## Technology Stack
- **Backend**: Python 3.12.3, Flask
- **Frontend**: HTML, JavaScript (vanilla)
- **Deployment**: IIS with wfastcgi
- **External API**: SecuGen WebAPI (localhost:8443)

## Application Routes

### Main Routes
1. **`/`** - Home page with navigation links
2. **`/SimpleScan`** - Simple fingerprint capture with predefined settings
3. **`/AdvancedScan`** - Advanced capture with user-configurable parameters
4. **`/Display_Image`** - Displays captured fingerprint image and metadata
5. **`/scan1`** - First scan in comparison workflow
6. **`/scan2`** - Second scan in comparison workflow
7. **`/compare`** - Compare two fingerprint templates
8. **`/matchscore`** - Display matching score results

## Key Features

### 1. Fingerprint Capture
- **Simple Scan**: Pre-configured capture with default parameters
- **Advanced Scan**: Configurable parameters including:
  - Timeout (ms)
  - Quality threshold (0-100)
  - Fake finger detection levels (0-9)
  - Template format (ISO-19794, ANSI)
  - Image WSQ compression rate (0.75 or 2.25)

### 2. Image Display
- Displays captured fingerprint as BMP image (base64 encoded)
- Shows metadata:
  - Device information (Manufacturer, Model, Serial Number)
  - Image properties (Width, Height, DPI)
  - Quality metrics (Image Quality, NFIQ score)
  - Template data (Base64 encoded)
  - WSQ compressed image data

### 3. Fingerprint Comparison
- Two-step capture process (scan1 → scan2)
- Template matching with configurable quality threshold
- Match score calculation and display

### 4. Error Handling
- Comprehensive error code translation
- User-friendly error messages
- Error codes mapped from SecuGen library (SgFplib.h)

## External API Integration

### SecuGen WebAPI Endpoints
- **`https://localhost:8443/SGIFPCapture`** - Capture fingerprint
- **`https://localhost:8443/SGIMatchScore`** - Match fingerprint templates

### API Parameters
- `timeout`: Capture timeout in milliseconds
- `quality`: Quality threshold (0-100)
- `licstr`: License string (currently empty)
- `templateformat`: Template format (ISO, ISO-19794, ANSI)
- `imagewsqrate`: WSQ compression rate (0.75 or 2.25)
- `fakeDetection`: Fake finger detection level (0-9)

## Data Flow

### Simple/Advanced Scan Flow
1. User clicks submit button
2. JavaScript sends POST request to SecuGen WebAPI
3. WebAPI returns JSON response with fingerprint data
4. JavaScript creates hidden form and submits to Flask backend
5. Flask renders `display_image.html` with captured data

### Comparison Flow
1. User captures first fingerprint (`/scan1`)
2. First template stored in `response_data_1`
3. User captures second fingerprint (`/scan2`)
4. Second template stored in `response_data_2`
5. User initiates comparison (`/compare`)
6. JavaScript sends templates to WebAPI matching endpoint
7. Match score displayed on `/matchscore` page

## Configuration

### Application Settings
- **Secret Key**: Hardcoded in `app.py` (should be changed for production)
- **License String**: Currently empty (`LIC_STR = ''`)
- **Default Parameters**:
  - Timeout: 10000ms
  - Quality: 50
  - Template Format: ISO
  - Image WSQ Rate: 0.75 (SimpleScan) or 2.25 (AdvancedScan)

### IIS Configuration (web.config)
- Python path: `C:\WebAPIPython-18` (needs update for current location)
- WSGI handler: `app.app`
- Log path: `C:\WebAPIPython-18\Logs\app.log` (needs update)
- FastCGI script processor: `C:\Python312\python.exe|C:\Python312\lib\site-packages\wfastcgi.py`

## Error Codes

The application handles various SecuGen error codes:
- **3**: Failure to reach SecuGen Fingerprint Scanner
- **51-63**: Device initialization, capture, and driver errors
- **1000-9999**: SGIBioSrv errors
- **10000-99999**: License errors

## Dependencies

### Required Python Packages
- Flask
- wfastcgi (for IIS deployment)

### System Requirements
- Windows 10/11 (x64)
- Python 3.12.3
- IIS with FastCGI support
- SecuGen fingerprint device drivers
- SecuGen WebAPI client installed
- Modern web browser (Chrome, Edge, Opera, etc.)

## Security Notes
⚠️ **Important Security Considerations**:
- Secret key is hardcoded (should use environment variable)
- License string is empty (may need configuration)
- HTTPS endpoint hardcoded to localhost:8443
- No authentication/authorization implemented
- File permissions need to be set for IIS_IUSRS

## Deployment Notes
- Python should NOT be installed in directories with spaces (e.g., `C:\Program Files\`)
- IIS_IUSRS needs file permissions for the website directory
- Path environment variable must include Python312 directory
- Handler mappings must be configured in IIS

## Current Status
- Application appears to be functional
- Configuration paths in `web.config` may need updating for current deployment location
- Missing `requirements.txt` file (should be created)
- Logging directory exists but may need proper permissions


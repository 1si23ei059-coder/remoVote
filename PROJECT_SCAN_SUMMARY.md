# Project Scan Summary - Biometric Voting System

**Date:** 2025-01-27  
**Project Path:** `J:\voting project\WebAPI-Python`

---

## 📋 Project Overview

A Flask-based **Biometric Voting System** that uses SecuGen fingerprint scanners for secure voter authentication. The system ensures one vote per voter per day and stores all data in CSV files.

---

## 🗂️ Project Structure

```
WebAPI-Python/
├── app.py                          # Main Flask application (529 lines)
├── requirements.txt                # Python dependencies
├── web.config                      # IIS deployment configuration
├── README.md                       # Main documentation
├── PROJECT_OVERVIEW.md            # Project overview document
├── TROUBLESHOOTING.md             # Troubleshooting guide
├── Deployment_Directions.txt      # Server deployment instructions
│
├── CSV Data Files/
│   ├── voters.csv                 # Registered voters (biometric data)
│   ├── votes.csv                  # All votes cast (8 records)
│   ├── daily_votes.csv            # Daily voting tracking (8 records)
│   └── candidates.csv             # Candidate data (8,443 candidates)
│
├── templates/                      # HTML templates (17 files)
│   ├── home.html                  # Landing page with service status
│   ├── register.html              # Voter registration page
│   ├── register_form.html         # Registration form
│   ├── registration_success.html  # Success confirmation
│   ├── login.html                 # Voter login page
│   ├── login_scan2.html          # Second login scan
│   ├── login_compare.html         # Biometric comparison
│   ├── voting_system.html         # Main voting interface
│   ├── admin_login.html           # Admin authentication
│   ├── admin_panel.html           # Admin dashboard
│   ├── error.html                 # Error display page
│   ├── SimpleScan.html            # Simple fingerprint capture
│   ├── AdvancedScan.html          # Advanced capture with config
│   ├── scan1.html                 # First scan for comparison
│   ├── scan2.html                 # Second scan for comparison
│   ├── compare.html               # Compare templates
│   ├── display_image.html         # Display captured image
│   └── match_score.html           # Display matching score
│
└── Logs/
    └── app.log                    # Application logs
```

---

## 🔧 Technology Stack

### Backend
- **Framework:** Flask 2.0.0+
- **Python:** 3.12.3
- **Deployment:** IIS with wfastcgi
- **Data Storage:** CSV files (no database)

### Frontend
- **HTML5** with vanilla JavaScript
- **CSS3** with modern styling
- **Responsive design** with mobile support

### External Integration
- **SecuGen WebAPI** (localhost:8443)
- **SecuGen Fingerprint Scanner** (USB device)

---

## 🛣️ Application Routes (16 endpoints)

### Public Routes
1. **`GET /`** - Home page with service status check
2. **`GET /register`** - Voter registration page
3. **`POST /register_scan`** - Process biometric capture for registration
4. **`POST /save_registration`** - Save voter registration data
5. **`GET /login`** - Voter login page
6. **`POST /login_scan1`** - First login fingerprint scan
7. **`POST /login_scan2`** - Second login fingerprint scan
8. **`POST /login_verify`** - Verify biometric and proceed to voting
9. **`GET /voting`** - Voting system interface
10. **`POST /cast_vote`** - Record vote
11. **`GET /get_candidates_json`** - Get candidates data (JSON API)
12. **`GET /get_voters_json`** - Get voters data for biometric matching (JSON API)

### Admin Routes
13. **`GET /admin`** - Admin login page
14. **`POST /admin`** - Process admin login (password: `mini2025`)
15. **`GET /admin_panel`** - Admin dashboard
16. **`POST /admin/upload_candidates`** - Upload candidates CSV file
17. **`POST /admin/logout`** - Admin logout

---

## 📊 Data Models

### Voters CSV (`voters.csv`)
**Structure:**
```
voter_id, name, template_base64, bmp_base64, registration_date
```
- Stores biometric templates (Base64 encoded)
- Stores fingerprint images (BMP, Base64 encoded)
- Prevents duplicate voter IDs
- Prevents duplicate biometrics

### Votes CSV (`votes.csv`)
**Structure:**
```
date, voter_id, name, state, constituency, candidate_name, party, timestamp
```
- Records all votes cast
- Links voter to candidate and constituency
- Includes timestamp for audit trail

### Daily Votes CSV (`daily_votes.csv`)
**Structure:**
```
date, voter_id, voted
```
- Tracks daily voting to prevent duplicate votes
- Simple flag system (yes/no)

### Candidates CSV (`candidates.csv`)
**Structure:**
```
_id, State, Constituency, Party, Candidate Name
```
- 8,443 candidate records
- Uploaded by admin
- Used for voting interface

---

## 🔐 Security Features

1. **Biometric Authentication**
   - Two-step verification (self-verify + database match)
   - Minimum matching score: 20 (configurable)
   - Prevents identity fraud

2. **Vote Protection**
   - One vote per voter per day enforcement
   - Duplicate biometric detection
   - Duplicate voter ID prevention

3. **Session Management**
   - Flask sessions for voter authentication
   - Admin session protection
   - Automatic session clearing after vote

4. **Admin Protection**
   - Password-protected admin panel
   - Current password: `mini2025` (should be changed)

---

## 🔄 Workflows

### Voter Registration Flow
1. User navigates to `/register`
2. Scans fingerprint using SecuGen device
3. System captures template and BMP image
4. User enters Voter ID and Name
5. System checks for duplicates:
   - Voter ID already exists?
   - Biometric template already registered?
6. If valid, saves to `voters.csv`
7. Shows success confirmation

### Voter Login & Voting Flow
1. User navigates to `/login`
2. **First Scan:** Captures fingerprint template1
3. **Second Scan:** Captures fingerprint template2
4. **Self-Verification:** Compares template1 vs template2
5. **Database Matching:** Compares template2 against all registered voters
6. System finds best match (score ≥ 20)
7. Checks if voter already voted today
8. If valid, creates session and redirects to `/voting`
9. User selects State → Constituency → Candidate
10. Vote is recorded in `votes.csv` and `daily_votes.csv`
11. Session is cleared

### Admin Workflow
1. Admin logs in at `/admin` (password: `mini2025`)
2. Admin panel shows:
   - Registered voters list
   - Election results by constituency
   - Detailed vote log
3. Can upload candidates CSV file
4. Can logout

---

## 🔌 External API Integration

### SecuGen WebAPI Endpoints

**Base URL:** `https://localhost:8443`

1. **`POST /SGIFPCapture`**
   - Captures fingerprint
   - Parameters:
     - `timeout`: 10000ms
     - `quality`: 50
     - `licstr`: (empty)
     - `templateformat`: ISO
     - `imagewsqrate`: 0.75
   - Returns: JSON with TemplateBase64, BMPBase64, metadata

2. **`POST /SGIMatchScore`**
   - Compares two fingerprint templates
   - Parameters:
     - `template1`: Base64 template
     - `template2`: Base64 template
     - `templateformat`: ISO
     - `licstr`: (empty)
   - Returns: JSON with MatchingScore, ErrorCode

---

## ⚙️ Configuration

### Application Settings (`app.py`)
- **Secret Key:** `'your_secret_key_change_in_production'` (hardcoded)
- **License String:** `LIC_STR = ''` (empty)
- **Matching Threshold:** 20 (minimum score)
- **CSV Field Size Limit:** Increased to handle large Base64 strings

### IIS Configuration (`web.config`)
- **Python Path:** `C:\WebAPIPython-18` (needs update)
- **WSGI Handler:** `app.app`
- **Log Path:** `C:\WebAPIPython-18\Logs\app.log` (needs update)
- **FastCGI:** `C:\Python312\python.exe|C:\Python312\lib\site-packages\wfastcgi.py`

### Dependencies (`requirements.txt`)
```
Flask>=2.0.0
wfastcgi>=3.0.0
```

---

## 🐛 Error Handling

### SecuGen Error Codes
The system translates SecuGen error codes:
- **3:** Failure to reach SecuGen Fingerprint Scanner
- **51:** System file load failure
- **52:** Sensor chip initialization failed
- **53:** Device not found
- **54:** Fingerprint image capture timeout
- **55:** No device available
- **56:** Driver load failed
- **57:** Wrong Image
- **58:** Lack of bandwidth
- **59:** Device Busy
- **60:** Cannot get serial number
- **61:** Unsupported device
- **63:** SgiBioSrv didn't start

### Custom Error Codes
- **400:** Missing required information
- **401:** Biometric verification failed
- **403:** Already voted today
- **409:** Duplicate registration

---

## 📈 Current Data Status

### Voters
- File: `voters.csv` (9 lines total, including header)
- Contains registered voters with biometric data
- Large Base64 strings for templates and images

### Votes
- File: `votes.csv` (9 lines total, including header)
- 7 votes recorded
- Dates: All from 2025-12-01
- States: Karnataka, Himachal Pradesh, Chhattisgarh
- Constituencies: Tumkur, KANGRA, SURGUJA, Gulbarga

### Daily Votes
- File: `daily_votes.csv` (9 lines total, including header)
- 7 daily vote records
- All from 2025-12-01

### Candidates
- File: `candidates.csv` (8,443 lines)
- Covers multiple states and constituencies
- Various political parties

---

## 🔍 Key Functions

### Data Management
- `init_csv_files()` - Initialize CSV files with headers
- `save_voter()` - Save voter to CSV
- `get_all_voters()` - Load all voters from CSV
- `voter_id_exists()` - Check if voter ID exists
- `biometric_exists()` - Check if biometric template exists
- `save_vote()` - Save vote to CSV
- `get_votes()` - Get votes grouped by constituency
- `get_vote_log()` - Get all votes as list
- `get_voter_by_id()` - Get voter by ID
- `has_voted_today()` - Check if voter voted today
- `mark_voted_today()` - Mark voter as voted

### Biometric Functions
- `TranslateErrorNumber()` - Translate SecuGen error codes
- `get_int_form_value()` - Safely parse form integers

---

## 🎨 Frontend Features

### Home Page
- Service status indicator (checks SecuGen WebAPI)
- Auto-refresh every 30 seconds
- Modern, responsive design
- Navigation to registration, login, admin

### Voting System
- Multi-step form (State → Constituency → Candidate)
- Real-time candidate loading
- Voter ID confirmation
- Success/error messaging

### Admin Panel
- Voter list display
- Results by constituency
- Vote log with timestamps
- CSV upload interface

---

## ⚠️ Security Concerns

1. **Hardcoded Secrets**
   - Secret key in code (should use environment variable)
   - Admin password in code (should use hashing + database)

2. **CSV Storage**
   - Sensitive biometric data in plain CSV
   - No encryption
   - No backup mechanism

3. **Session Security**
   - Simple Flask sessions
   - No HTTPS enforcement (in code)

4. **Input Validation**
   - Basic validation present
   - Could be more robust

---

## 🚀 Deployment Notes

### Requirements
- Windows 10/11 (x64)
- Python 3.12.3 (NOT in directory with spaces)
- IIS with FastCGI support
- SecuGen drivers installed
- SecuGen WebAPI client running on localhost:8443

### IIS Setup
1. Install Python 3.12.3 (avoid spaces in path)
2. Install Flask and wfastcgi via pip
3. Create IIS website
4. Configure `web.config` with correct paths
5. Set handler mappings for FastCGI
6. Grant IIS_IUSRS file permissions
7. Update PYTHONPATH in web.config

### Service Dependencies
- SecuGen WebAPI must be running
- Fingerprint device must be connected
- SSL certificate must be accepted in browser

---

## 📝 Code Quality Notes

### Strengths
- Well-organized route structure
- Comprehensive error handling
- Good separation of concerns
- Detailed logging and debugging
- User-friendly error messages

### Areas for Improvement
- Move secrets to environment variables
- Add database instead of CSV
- Implement proper password hashing
- Add input sanitization
- Add unit tests
- Add API rate limiting
- Implement proper logging system
- Add data backup mechanism

---

## 🔗 Related Files

- **README.md** - Main user documentation
- **PROJECT_OVERVIEW.md** - Technical overview
- **TROUBLESHOOTING.md** - Common issues and solutions
- **Deployment_Directions.txt** - Server setup instructions
- **web.config** - IIS configuration

---

## 📊 Statistics

- **Total Routes:** 16
- **Templates:** 17 HTML files
- **CSV Files:** 4
- **Python Functions:** ~20
- **Lines of Code (app.py):** 529
- **Registered Voters:** ~7 (from CSV)
- **Votes Cast:** 7
- **Candidates:** 8,443

---

## 🎯 System Status

✅ **Functional Components:**
- Voter registration
- Biometric authentication
- Voting system
- Admin panel
- CSV data management

⚠️ **Configuration Needed:**
- Update `web.config` paths
- Change admin password
- Change secret key
- Configure proper logging

🔧 **Dependencies:**
- SecuGen WebAPI service must be running
- Fingerprint device must be connected
- Browser must accept SSL certificate

---

**End of Project Scan Summary**


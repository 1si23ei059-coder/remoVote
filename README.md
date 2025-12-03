# Biometric Voting System

A Flask-based web application for secure voting using SecuGen fingerprint biometric authentication. The system ensures one vote per voter per day and stores all data in CSV files.

## Features

### Voter Registration
- Biometric capture using SecuGen fingerprint scanner
- Voter ID and name registration
- Prevents duplicate voter ID registration
- Prevents duplicate biometric registration
- Stores biometric data (template and image) in CSV

### Voter Login & Verification
- Two-step biometric verification:
  1. Self-verification (compares two scans to ensure quality)
  2. Database matching (compares with all registered voters)
- Prevents voting if already voted today
- Secure session management

### Voting System
- State selection
- Constituency selection
- Voter ID confirmation
- Candidate selection and voting
- Automatic vote recording

### Admin Panel
- Upload candidate CSV files
- View registered voters
- View election results by constituency
- View detailed vote log
- Password-protected access

## System Requirements

1. **Hardware:**
   - SecuGen fingerprint device (USB connected)
   - Windows 10/11 (x64)

2. **Software:**
   - Python 3.12.3
   - SecuGen fingerprint driver
   - SecuGen WebAPI client (running on localhost:8443)
   - Flask web framework

3. **Browser:**
   - Modern browser (Chrome, Edge, Opera, etc.)

## Installation

1. Install Python 3.12.3 (avoid directories with spaces)
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure SecuGen WebAPI client is running on `https://localhost:8443`
4. Run the application:
   ```bash
   python app.py
   ```
5. Access the application at `http://localhost:5000`

## CSV File Structure

### voters.csv
Stores registered voter information:
```
voter_id,name,template_base64,bmp_base64,registration_date
```

### votes.csv
Stores all votes cast:
```
date,voter_id,name,state,constituency,candidate_name,party,timestamp
```

### daily_votes.csv
Tracks daily voting to prevent duplicate votes:
```
date,voter_id,voted
```

### candidates.csv
Stores candidate data (uploaded by admin):
```
S.No,State,Constituency,Party,Candidate Name
```

## Usage Flow

### For Voters:

1. **Registration:**
   - Go to home page → "Register as Voter"
   - Scan fingerprint
   - Enter Voter ID and Name
   - Complete registration

2. **Voting:**
   - Go to home page → "Voter Login"
   - Scan fingerprint twice for verification
   - System verifies identity and checks if already voted today
   - Select State → Constituency → Confirm Voter ID
   - Select candidate and vote
   - Receive confirmation

### For Administrators:

1. **Login:**
   - Go to home page → "Admin Login"
   - Enter password: `mini2025`

2. **Upload Candidates:**
   - Upload CSV file with candidate data
   - Format: S.No, State, Constituency, Party, Candidate Name

3. **View Results:**
   - View election results by constituency
   - View detailed vote log
   - View registered voters list

## Security Features

- Biometric authentication prevents identity fraud
- One vote per voter per day enforcement
- Duplicate biometric detection during registration
- Duplicate voter ID prevention
- Session-based authentication
- Admin password protection

## API Endpoints

- `GET /` - Home page
- `GET /register` - Registration page
- `POST /register_scan` - Process biometric capture
- `POST /save_registration` - Save voter registration
- `GET /login` - Login page
- `POST /login_scan1` - First login scan
- `POST /login_scan2` - Second login scan
- `POST /login_verify` - Verify biometric and proceed to voting
- `GET /voting` - Voting system interface
- `POST /cast_vote` - Record vote
- `GET /get_candidates_json` - Get candidates data (JSON)
- `GET /get_voters_json` - Get voters data (JSON)
- `GET /admin` - Admin login page
- `GET /admin_panel` - Admin dashboard
- `POST /admin/upload_candidates` - Upload candidates CSV

## Biometric Comparison Logic

The system uses SecuGen WebAPI for biometric comparison:

1. **Self-Verification:** Compares two scans to ensure quality
2. **Database Matching:** Compares second scan with all registered voter templates
3. **Threshold:** Minimum matching score of 50 required
4. **Best Match:** Selects voter with highest matching score above threshold

## Error Handling

The system handles various SecuGen error codes:
- Device connection errors
- Capture timeout errors
- Driver errors
- Image quality errors
- Custom errors for duplicate registration, already voted, etc.

## Notes

- All biometric data is stored as Base64-encoded strings in CSV files
- The system uses in-memory session storage for active workflows
- CSV files are created automatically on first run
- Admin password should be changed in production
- Secret key should be changed in production

## Troubleshooting

1. **"Check if SGIBIOSRV is running" error:**
   - Ensure SecuGen WebAPI client is running
   - Check if device is connected and drivers are installed

2. **"No candidate data available":**
   - Admin must upload candidates CSV file first

3. **"Already voted today":**
   - Each voter can only vote once per day
   - System automatically prevents duplicate voting

4. **"Biometric not found":**
   - Voter must register first before logging in

## License

This project is for educational/demonstration purposes.


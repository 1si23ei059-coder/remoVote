Main project files
Core application files (essential)
app.py (639 lines)
Main Flask application
Routes, functions, business logic
CSV operations, biometric verification
requirements.txt
Python dependencies
Flask>=2.0.0, wfastcgi>=3.0.0
web.config
IIS configuration for production deployment
FastCGI handler settings
Data storage files (CSV)
voters.csv
Registered voters with biometric data
Columns: voter_id, name, template_base64, bmp_base64, registration_date
votes.csv
All votes cast
Columns: date, voter_id, name, state, constituency, candidate_name, party, timestamp
daily_votes.csv
Voting restriction tracking (75-hour window)
Columns: date, voter_id, voted, timestamp
candidates.csv
Candidate database
Columns: id, State, Constituency, Party, Candidate Name
Frontend templates (17 HTML files)
Core templates:
templates/home.html - Landing page with service status
templates/register.html - Voter registration page
templates/register_form.html - Registration form completion
templates/registration_success.html - Success confirmation
templates/login.html - Voter login page
templates/login_scan2.html - Second login scan
templates/login_compare.html - Biometric comparison & verification
templates/voting_system.html - Main voting interface
templates/admin_login.html - Admin authentication
templates/admin_panel.html - Admin dashboard
templates/error.html - Error display page
Additional/legacy templates:
templates/SimpleScan.html - Simple fingerprint capture
templates/AdvancedScan.html - Advanced capture with config
templates/scan1.html - First scan for comparison
templates/scan2.html - Second scan for comparison
templates/compare.html - Compare templates
templates/display_image.html - Display captured image
templates/match_score.html - Display matching score
Documentation files
README.md - Main user documentation
PROJECT_OVERVIEW.md - Technical overview
PROJECT_SCAN_SUMMARY.md - Project scan summary
COMPLETE_PROJECT_SCAN.md - Detailed project analysis
TROUBLESHOOTING.md - Troubleshooting guide
Deployment_Directions.txt - Server setup instructions
Log files
Logs/app.log - Application logs
File categories summary
Category	Count	Purpose
Core Application	3	Main code, dependencies, config
Data Storage (CSV)	4	All persistent data
Frontend Templates	17	User interface pages
Documentation	6	Guides and references
Logs	1	Application logging
Total	31 files	Complete project
Most critical files (must-have)
app.py - Application logic
requirements.txt - Dependencies
voters.csv - Voter data
votes.csv - Vote records
daily_votes.csv - Voting restrictions
candidates.csv - Candidate data
templates/home.html - Entry point
templates/voting_system.html - Voting interface
templates/admin_panel.html - Admin functions
web.config - IIS deployment (production)
These 10 files are essential for the system to function. The rest support additional features or documentation.
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import base64
import os
import csv
import sys
from datetime import datetime, timedelta
import json
import traceback
import os

app = Flask(__name__)
# NOTE: LIC_STR is assumed to be an empty string unless a real SecuGen license is used.
LIC_STR = '' 
app.secret_key = 'your_secret_key_change_in_production'

# Data storage for biometric workflows
registration_data = {}
login_scan_data = {}
voting_data = {}

# CSV file paths
VOTERS_CSV = 'data/voters.csv'
VOTES_CSV = 'data/votes.csv'
CANDIDATES_CSV = 'data/candidates.csv'
DAILY_VOTES_CSV = 'data/daily_votes.csv'


# HARDCODED TEST VOTE CONSTANTS 
# These values cannot be changed by the admin's POST request, 
# ensuring the recorded voter identity is fixed.
FIXED_TEST_VOTER_ID = 'ADMIN001'
FIXED_TEST_VOTER_NAME = 'System Test User'

# Initialize CSV files if they don't exist
def init_csv_files():
    # Voters CSV: voter_id, name, template_base64, bmp_base64, registration_date
    if not os.path.exists(VOTERS_CSV):
        with open(VOTERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['voter_id', 'name', 'template_base64', 'bmp_base64', 'registration_date'])
    
    # Votes CSV: date, voter_id, name, state, constituency, candidate_name, party, timestamp
    if not os.path.exists(VOTES_CSV):
        with open(VOTES_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'voter_id', 'name', 'state', 'constituency', 'candidate_name', 'party', 'timestamp'])
    
    # Candidates CSV: _id, State, Constituency, Party, Candidate Name
    if not os.path.exists(CANDIDATES_CSV):
        with open(CANDIDATES_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['_id', 'State', 'Constituency', 'Party', 'Candidate Name'])
            
    # Daily votes CSV: date, voter_id, voted, timestamp (to track voting within 75 hours)
    if not os.path.exists(DAILY_VOTES_CSV):
        with open(DAILY_VOTES_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'voter_id', 'voted', 'timestamp'])

def TranslateErrorNumber(ErrorNumber):
    match ErrorNumber:
        case 3:
            return "Failure to reach SecuGen Fingerprint Scanner"
        case 51:
            return "System file load failure"
        case 52:
            return "Sensor chip initialization failed"
        case 53:
            return "Device not found"
        case 54:
            return "Fingerprint image capture timeout"
        case 55:
            return "No device available"
        case 56:
            return "Driver load failed"
        case 57:
            return "Wrong Image"
        case 58:
            return "Lack of bandwidth"
        case 59:
            return "Device Busy"
        case 60:
            return "Cannot get serial number of the device"
        case 61:
            return "Unsupported device"
        case 63:
            return "SgiBioSrv didn't start; Try image capture again"
        case _:
            return "Unknown error code or Update code to reflect latest result"

# Helper function to safely convert form values to integers
def get_int_form_value(form, key, default=0):
    """Safely get integer value from form, handling empty strings and None"""
    value = form.get(key, default)
    if value == '' or value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# Save voter to CSV
def save_voter(voter_id, name, template_base64, bmp_base64):
    with open(VOTERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([voter_id, name, template_base64, bmp_base64, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

# Get all voters from CSV
def get_all_voters():
    voters = []
    if os.path.exists(VOTERS_CSV):
        try:
            # Increase field size limit for CSV with large base64 strings
            original_limit = csv.field_size_limit()
            try:
                csv.field_size_limit(min(2**31-1, sys.maxsize))
            except:
                pass
            
            with open(VOTERS_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                row_count = 0
                for row in reader:
                    row_count += 1
                    try:
                        voter_id = (row.get('voter_id') or '').strip()
                        template = (row.get('template_base64') or '').strip()
                        name = (row.get('name') or '').strip()
                        bmp = (row.get('bmp_base64') or '').strip()
                        reg_date = (row.get('registration_date') or '').strip()
                        
                        # Check if row has required fields and template_base64 is not empty
                        if voter_id and template and len(template) > 10:
                            voters.append({
                                'voter_id': voter_id,
                                'name': name,
                                'template_base64': template,
                                'bmp_base64': bmp,
                                'registration_date': reg_date
                            })
                    except Exception as row_error:
                        continue
                
            # Restore original limit
            try:
                csv.field_size_limit(original_limit)
            except:
                pass
                
        except Exception as e:
            print(f"ERROR reading voters CSV: {e}")
            traceback.print_exc()
    else:
        print(f"WARNING: VOTERS_CSV file does not exist: {VOTERS_CSV}")
    
    return voters

# Check if voter ID exists
def voter_id_exists(voter_id):
    voters = get_all_voters()
    return any(v['voter_id'].upper() == voter_id.upper() for v in voters)

# Check if voter has already voted within the last 75 hours
def has_voted_today(voter_id):
    current_time = datetime.now()
    if os.path.exists(DAILY_VOTES_CSV):
        try:
            with open(DAILY_VOTES_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('voter_id', '').upper() == voter_id.upper():
                        timestamp_str = row.get('timestamp', '')
                        if timestamp_str:
                            try:
                                vote_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                time_diff = current_time - vote_time
                                if time_diff < timedelta(hours=75):
                                    return True
                            except ValueError:
                                pass
                        else:
                            vote_date = row.get('date', '')
                            if vote_date:
                                try:
                                    vote_datetime = datetime.strptime(vote_date, '%Y-%m-%d')
                                    time_diff = current_time - vote_datetime
                                    if time_diff < timedelta(hours=75):
                                        return True
                                except ValueError:
                                    pass
        except Exception as e:
            print(f"Error checking daily votes: {e}")
            traceback.print_exc()
    return False

# Mark voter as voted (with timestamp for 75-hour tracking)
def mark_voted_today(voter_id):
    today = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(DAILY_VOTES_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([today, voter_id, 'yes', timestamp])

# Save vote to CSV
def save_vote(voter_id, name, state, constituency, candidate_name, party):
    today = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(VOTES_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([today, voter_id, name, state, constituency, candidate_name, party, timestamp])

# Get votes for results
def get_votes():
    votes = {}
    if os.path.exists(VOTES_CSV):
        try:
            with open(VOTES_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('constituency') and row.get('candidate_name'):
                        constituency = row['constituency']
                        candidate = f"{row['candidate_name']} ({row['party']})"
                        if constituency not in votes:
                            votes[constituency] = {}
                        if candidate not in votes[constituency]:
                            votes[constituency][candidate] = 0
                        votes[constituency][candidate] += 1
        except Exception as e:
            print(f"Error reading votes CSV: {e}")
            traceback.print_exc()
    return votes

# Get vote log
def get_vote_log():
    log = []
    if os.path.exists(VOTES_CSV):
        try:
            with open(VOTES_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('voter_id'):  # Skip empty rows
                        log.append(row)
        except Exception as e:
            print(f"Error reading vote log: {e}")
            traceback.print_exc()
    return log

# Get voter by ID
def get_voter_by_id(voter_id):
    voters = get_all_voters()
    for v in voters:
        if v['voter_id'].upper() == voter_id.upper():
            return v
    return None

# Check if biometric template already exists (prevent duplicate registration)
def biometric_exists(template_base64):
    voters = get_all_voters()
    for voter in voters:
        if voter['template_base64'] == template_base64:
            return True
    return False

# ========== DELETE FUNCTIONS (omitted for brevity, assume they are correct) ==========
# ... (All delete functions remain unchanged) ...

def delete_daily_votes():
    try:
        with open(DAILY_VOTES_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'voter_id', 'voted', 'timestamp'])
        return True, "Daily votes data deleted successfully"
    except Exception as e:
        return False, f"Error deleting daily votes: {str(e)}"

def delete_voters():
    try:
        with open(VOTERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['voter_id', 'name', 'template_base64', 'bmp_base64', 'registration_date'])
        return True, "Voters data deleted successfully"
    except Exception as e:
        return False, f"Error deleting voters: {str(e)}"

def delete_votes():
    try:
        with open(VOTES_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'voter_id', 'name', 'state', 'constituency', 'candidate_name', 'party', 'timestamp'])
        return True, "Votes data deleted successfully"
    except Exception as e:
        return False, f"Error deleting votes: {str(e)}"

def delete_candidates():
    try:
        with open(CANDIDATES_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['_id', 'State', 'Constituency', 'Party', 'Candidate Name'])
        return True, "Candidates data deleted successfully"
    except Exception as e:
        return False, f"Error deleting candidates: {str(e)}"

# ========== ROUTES ==========

@app.route('/')
def home():
    return render_template('home.html')

# ========== REGISTRATION FLOW (omitted for brevity, assume it is correct) ==========
# ... (All registration routes remain unchanged) ...

@app.route('/register', methods=['GET', 'POST'])
def register():
    input_data = {
        'SecuGen_Lic': LIC_STR,
        'Timeout': 10000,
        'Quality': 50,
        'TemplateFormat': 'ISO',
        'ImageWSQRate': '0.75'
    }
    return render_template('register.html', user_input=input_data)

@app.route('/register_scan', methods=['POST'])
def register_scan():
    ErrorNumber = get_int_form_value(request.form, 'ErrorCode', 0)
    if ErrorNumber > 0:
        return render_template('error.html', error=ErrorNumber, errordescription=TranslateErrorNumber(ErrorNumber))
    
    registration_data['template'] = request.form.get('TemplateBase64')
    registration_data['BMPBase64'] = request.form.get('BMPBase64')
    registration_data['Manufacturer'] = request.form.get('Manufacturer')
    registration_data['Model'] = request.form.get('Model')
    registration_data['SerialNumber'] = request.form.get('SerialNumber')
    
    return render_template('register_form.html', metadata=registration_data)

@app.route('/save_registration', methods=['POST'])
def save_registration():
    voter_id = request.form.get('voter_id', '').strip().upper()
    name = request.form.get('name', '').strip()
    template_base64 = registration_data.get('template', '')
    bmp_base64 = registration_data.get('BMPBase64', '')
    
    if not voter_id or not name or not template_base64:
        return render_template('error.html', error=400, errordescription="Missing required information")
    
    # Check if voter ID already exists
    if voter_id_exists(voter_id):
        return render_template('error.html', error=409, errordescription=f"Voter ID {voter_id} is already registered")
    
    # Check if biometric already exists
    if biometric_exists(template_base64):
        return render_template('error.html', error=409, errordescription="This biometric is already registered with another voter ID")
    
    # Save voter
    save_voter(voter_id, name, template_base64, bmp_base64)
    
    return render_template('registration_success.html', voter_id=voter_id, name=name)

# ========== LOGIN FLOW (omitted for brevity, assume it is correct) ==========
# ... (All login routes remain unchanged) ...

@app.route('/login', methods=['GET', 'POST'])
def login():
    input_data = {
        'SecuGen_Lic': LIC_STR,
        'Timeout': 10000,
        'Quality': 50,
        'TemplateFormat': 'ISO',
        'ImageWSQRate': '0.75'
    }
    return render_template('login.html', user_input=input_data)

@app.route('/login_scan1', methods=['POST'])
def login_scan1():
    ErrorNumber = get_int_form_value(request.form, 'ErrorCode', 0)
    if ErrorNumber > 0:
        return render_template('error.html', error=ErrorNumber, errordescription=TranslateErrorNumber(ErrorNumber))
    
    login_scan_data['template1'] = request.form.get('TemplateBase64', '').strip()
    login_scan_data['BMPBase64_1'] = request.form.get('BMPBase64', '').strip()
    
    if not login_scan_data['template1']:
        return render_template('error.html', error=400, errordescription="Fingerprint template not captured. Please try again.")
    
    input_data = {
        'SecuGen_Lic': LIC_STR,
        'Timeout': 10000,
        'Quality': 50,
        'TemplateFormat': 'ISO',
        'ImageWSQRate': '0.75'
    }
    return render_template('login_scan2.html', user_input=input_data, metadata1={'BMPBase64': login_scan_data['BMPBase64_1']})

@app.route('/login_scan2', methods=['POST'])
def login_scan2():
    ErrorNumber = get_int_form_value(request.form, 'ErrorCode', 0)
    if ErrorNumber > 0:
        return render_template('error.html', error=ErrorNumber, errordescription=TranslateErrorNumber(ErrorNumber))
    
    login_scan_data['template2'] = request.form.get('TemplateBase64', '').strip()
    login_scan_data['BMPBase64_2'] = request.form.get('BMPBase64', '').strip()
    
    # Validate templates exist
    if not login_scan_data.get('template1') or not login_scan_data.get('template2'):
        return render_template('error.html', error=400, errordescription="Fingerprint templates missing. Please start login process again.")
    
    # Ensure templates are passed correctly
    template1 = login_scan_data.get('template1', '')
    template2 = login_scan_data.get('template2', '')
    
    return render_template('login_compare.html', 
                            template1=template1,
                            template2=template2,
                            metadata1={'BMPBase64': login_scan_data.get('BMPBase64_1', '')},
                            metadata2={'BMPBase64': login_scan_data.get('BMPBase64_2', '')},
                            user_input={'TemplateFormat': 'ISO', 'SecuGen_Lic': LIC_STR})

@app.route('/login_verify', methods=['POST'])
def login_verify():
    matched_voter_id = request.form.get('matched_voter_id', '').strip()
    matching_score = get_int_form_value(request.form, 'MatchingScore', 0)
    error_code = get_int_form_value(request.form, 'ErrorCode', 0)
    
    if error_code > 0:
        return render_template('error.html', error=error_code, errordescription=TranslateErrorNumber(error_code))
    
    # Lower threshold to 20
    if not matched_voter_id or matching_score < 20:
        return render_template('error.html', error=401, errordescription=f"Biometric verification failed. Matching score: {matching_score} (minimum required: 20). Please try again.")
    
    # Check if already voted within last 75 hours
    if has_voted_today(matched_voter_id):
        return render_template('error.html', error=403, errordescription="You have already voted recently. You can only vote once every 75 hours.")
    
    # Store in session for voting flow
    session['voter_id'] = matched_voter_id
    voter = get_voter_by_id(matched_voter_id)
    if voter:
        session['voter_name'] = voter['name']
    
    # Redirect to voting system
    return redirect(url_for('voting_system'))

# ========== VOTING SYSTEM (omitted for brevity, assume it is correct) ==========
# ... (All voting routes remain unchanged) ...

@app.route('/voting', methods=['GET', 'POST'])
def voting_system():
    if 'voter_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('voting_system.html', voter_id=session.get('voter_id'), voter_name=session.get('voter_name', ''))

@app.route('/get_candidates_json', methods=['GET'])
def get_candidates_json():
    candidates = []
    if os.path.exists(CANDIDATES_CSV):
        try:
            with open(CANDIDATES_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    candidate_data = {
                        '_id': row.get('_id'),
                        'State': row.get('State'),
                        'Constituency': row.get('Constituency'),
                        'Party': row.get('Party'),
                        'Candidate Name': row.get('Candidate Name')
                    }
                    if candidate_data.get('State') or candidate_data.get('Candidate Name'):
                        candidates.append(candidate_data)
        except Exception as e:
            print(f"Error reading candidates CSV: {e}")
            traceback.print_exc()
    return jsonify(candidates)

@app.route('/cast_vote', methods=['POST'])
def cast_vote():
    if 'voter_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    voter_id = session['voter_id']
    voter_name = session.get('voter_name', '')
    
    # Check if already voted within last 75 hours
    if has_voted_today(voter_id):
        return jsonify({'error': 'Already voted within the last 75 hours'}), 403
    
    data = request.json
    state = data.get('state', '')
    constituency = data.get('constituency', '')
    candidate_name = data.get('candidate_name', '')
    party = data.get('party', '')
    
    # Save vote
    save_vote(voter_id, voter_name, state, constituency, candidate_name, party)
    
    # Mark as voted (within 75-hour window)
    mark_voted_today(voter_id)
    
    # Clear session
    session.clear()
    
    return jsonify({'success': True, 'message': 'Vote recorded successfully'})

# ========== ADMIN PANEL ==========

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        # NOTE: Using a hardcoded password 'mini2025'. In production, use hashed passwords and environment variables.
        if password == 'mini2025':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('admin_login.html', error='Invalid password')
    return render_template('admin_login.html')

@app.route('/admin_panel', methods=['GET'])
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    voters = get_all_voters()
    votes = get_votes()
    vote_log = get_vote_log()
    
    return render_template('admin_panel.html', voters=voters, votes=votes, vote_log=vote_log)

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/admin/upload_candidates', methods=['POST'])
def upload_candidates():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.csv'):
        # Save uploaded CSV
        file.save(CANDIDATES_CSV)
        return jsonify({'success': True, 'message': 'Candidates uploaded successfully'})
    
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/admin/cast_test_vote', methods=['POST'])
def admin_cast_test_vote():
    """
    Allows an authorized admin to cast a test vote. The voter ID and name are 
    FIXED in the code, ensuring they cannot be changed by the admin's request.
    The admin must still select the candidate/constituency.
    """
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # --- HARDCODED/FIXED VOTE IDENTIFICATION ---
    voter_id = FIXED_TEST_VOTER_ID
    name = FIXED_TEST_VOTER_NAME
    
    # Retrieve changeable vote details (candidate selection) from the POST request
    data = request.json or request.form
    state = data.get('state', 'UNKNOWN STATE').strip()
    constituency = data.get('constituency', 'UNKNOWN CONSTITUENCY').strip()
    candidate_name = data.get('candidate_name', 'INVALID CANDIDATE').strip()
    party = data.get('party', 'N/A').strip()
    
    # Basic validation for the selected vote target
    if candidate_name == 'INVALID CANDIDATE' or constituency == 'UNKNOWN CONSTITUENCY':
        return jsonify({'error': 'Missing or invalid candidate selection for the test vote.'}), 400
        
    # Check for 75-hour lock on the FIXED test voter ID
    if has_voted_today(voter_id):
        return jsonify({'error': f'The Test Voter ID ({voter_id}) has already voted within the last 75 hours. Please wait or delete daily votes.'}), 403
    
    try:
        # 1. Save vote to VOTES_CSV (uses fixed voter ID/Name, but variable candidate selection)
        save_vote(voter_id, name, state, constituency, candidate_name, party)
        
        # 2. Mark as voted in DAILY_VOTES_CSV (for 75-hour tracking)
        mark_voted_today(voter_id)
        
        return jsonify({
            'success': True, 
            'message': f'Fixed Test Vote registered successfully. Voter ID: {voter_id}',
            'vote_details': {
                'constituency': constituency,
                'candidate': candidate_name,
                'party': party
            }
        })
    except Exception as e:
        print(f"Error casting admin test vote: {e}")
        traceback.print_exc()
        return jsonify({'error': f"Failed to register vote: {str(e)}"}), 500

@app.route('/admin/delete_daily_votes', methods=['POST'])
def admin_delete_daily_votes():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    success, message = delete_daily_votes()
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'error': message}), 500

@app.route('/admin/delete_voters', methods=['POST'])
def admin_delete_voters():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    success, message = delete_voters()
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'error': message}), 500

@app.route('/admin/delete_votes', methods=['POST'])
def admin_delete_votes():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    success, message = delete_votes()
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'error': message}), 500

@app.route('/admin/delete_candidates', methods=['POST'])
def admin_delete_candidates():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    success, message = delete_candidates()
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'error': message}), 500

@app.route('/get_voters_json', methods=['GET'])
def get_voters_json():
    """API endpoint for frontend to get all voters for biometric comparison"""
    try:
        voters = get_all_voters()
        valid_voters = []
        for voter in voters:
            template = voter.get('template_base64', '')
            voter_id = voter.get('voter_id', '')
            
            if voter_id and template and len(template.strip()) > 10:
                valid_voters.append({
                    'voter_id': voter_id,
                    'name': voter.get('name', ''),
                    'template_base64': template.strip(),
                    'bmp_base64': voter.get('bmp_base64', ''),
                    'registration_date': voter.get('registration_date', '')
                })
        
        return jsonify(valid_voters)
    except Exception as e:
        print(f"ERROR in get_voters_json: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'voters': []}), 500

# Initialize CSV files on startup
init_csv_files()



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)



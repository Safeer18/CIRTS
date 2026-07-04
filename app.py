import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from backend import models
from backend.otp_manager import OTPManager
from io import BytesIO
from datetime import datetime
import json   # add at top of app.py if not already present

# load environment
load_dotenv()

app = Flask(__name__, template_folder="frontend/templates")
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['UPLOAD_FOLDER'] = "uploaded_evidence"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

otp_manager = OTPManager()
temp_complaints = {}

FERNET_KEY = os.getenv('FERNET_KEY', 'CHANGE_THIS')
cipher_suite = Fernet(FERNET_KEY.encode() if isinstance(FERNET_KEY, str) else FERNET_KEY)
# Auto-create admin if not exists

try:
    existing_admin = models.get_user_by_username("admin")
    if not existing_admin:
        models.create_user("admin", "admin123", "admin", "admin@example.com", None)
        print("Default admin user created: admin / admin123")
except Exception as e:
    print("Admin creation error:", e)
# Put this after `app = Flask(...)` and after the inject_now() context processor if present.
@app.context_processor
def inject_helpers():
    # WARNING: exposing models to templates is fine for a demo/project.
    # For production, prefer passing only needed data to templates instead.
    return {
        'models': models,
        'now': datetime.utcnow
    }


def encrypt_file(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    return cipher_suite.encrypt(data)

def decrypt_file(encrypted_data):
    return cipher_suite.decrypt(encrypted_data)

def get_client_ip():
    # Server-side fallback (may be private if running locally)
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = request.remote_addr or '0.0.0.0'
    return ip

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return dt.strftime(format)
        except:
            return value
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

@app.route('/')
def home():
    return redirect(url_for('login'))

# --------------------------
# Auth / User routes
# --------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form.get('role', 'citizen')
        section_id = request.form.get('section_id')
        section_id = int(section_id) if section_id else None

        if not username or not email or not password or not confirm_password:
            flash("All fields are required", "warning")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Passwords do not match", "warning")
            return redirect(url_for('register'))

        if models.get_user_by_username(username):
            flash("Username already exists", "warning")
            return redirect(url_for('register'))

        models.create_user(username, password, role, email, section_id)
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    police_sections = models.get_police_sections() if hasattr(models, "get_police_sections") else []
    return render_template('register.html', police_sections=police_sections)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']

        # Debug logging (temporary)
        print(f"DEBUG: login attempt for username={uname}")

        ok = False
        try:
            ok = models.authenticate_user(uname, pwd)
        except Exception as e:
            print("DEBUG: authenticate_user raised:", e)
            ok = False

        print("DEBUG: authenticate_user returned:", ok)

        if ok:
            user = models.get_user_by_username(uname)
            if not user:
                print("DEBUG: user not found after authenticate (unexpected).")
                flash('Login error, contact admin', 'danger')
                return render_template('login.html')

            # Set session robustly and normalize role to lowercase string
            session['user_id'] = user.get('user_id')
            session['username'] = user.get('username')
            role_val = user.get('role') or 'citizen'
            if isinstance(role_val, str):
                role_val = role_val.strip()
            session['role'] = role_val
            session['section_id'] = user.get('section_id')

            print("DEBUG: session set:", {
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'role': session.get('role'),
                'section_id': session.get('section_id')
            })

            # Redirect based on role (use lowercase check to be robust)
            r = (session.get('role') or '').lower()
            if r == 'investigator':
                return redirect(url_for('police_dashboard'))
            elif r == 'admin':
                return redirect(url_for('admin_users'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --------------------------
# Dashboards & Views
# --------------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'citizen':
        return redirect(url_for('login'))
    complaints = models.get_complaints_by_user(session['user_id'])
    for c in complaints:
        c['evidence'] = models.get_evidence_by_complaint(c['complaint_id'])
    return render_template('dashboard.html', username=session['username'], complaints=complaints)

@app.route('/police_dashboard')
def police_dashboard():
    if 'user_id' not in session or session.get('role') != 'investigator':
        return redirect(url_for('login'))
    section_id = session.get('section_id')
    complaints = models.get_complaints_by_section(section_id) or []

    # server-side filtering by status and search query (q)
    status = request.args.get('status','').strip()
    q = request.args.get('q','').strip().lower()

    def matches(c):
        if status and ( (c.get('status') or '').lower() != status.lower() ):
            return False
        if q:
            # check complaint_id, title, or reporter username
            if q.isdigit() and str(c.get('complaint_id')) == q:
                return True
            title = (c.get('title') or '').lower()
            reporter = (c.get('username') or c.get('reporter_username') or '').lower()
            if q in title or q in reporter:
                return True
            return False
        return True

    filtered = [c for c in complaints if matches(c)]
    return render_template('police_dashboard.html', complaints=filtered)


@app.route('/bulk_assign', methods=['POST'])
def bulk_assign():
    # Assign selected complaints to current investigator's section
    if 'user_id' not in session or session.get('role') != 'investigator':
        flash('Unauthorized', 'danger')
        return redirect(url_for('login'))
    section_id = session.get('section_id')
    data = request.form.get('selected_ids')
    if not data:
        flash('No complaints selected', 'warning')
        return redirect(url_for('police_dashboard'))
    try:
        ids = json.loads(data)
    except Exception:
        flash('Invalid selection data', 'danger')
        return redirect(url_for('police_dashboard'))
    updated = 0
    for cid in ids:
        try:
            models.update_complaint_section(int(cid), section_id)
            # audit
            try:
                models.add_audit_log(session.get('user_id'), f'Bulk assigned complaint {cid} to section {section_id}')
            except Exception:
                pass
            # notify owner (best-effort)
            try:
                comp = models.get_complaint_by_id(int(cid))
                if comp and comp.get('user_id'):
                    owner = models.get_user_by_id(comp.get('user_id')) if hasattr(models, 'get_user_by_id') else None
                    if owner and owner.get('email'):
                        otp_manager.send_email(owner.get('email'), f'Your complaint #{cid} was assigned to section {section_id}.')
            except Exception:
                pass
            updated += 1
        except Exception:
            pass
    flash(f'Assigned {updated} complaints to your section', 'success')
    return redirect(url_for('police_dashboard'))


# --------------------------
# File complaint (with demo location override)
# --------------------------
@app.route('/add_complaint', methods=['GET', 'POST'])
def add_complaint():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        classification = request.form.get('classification')
        if not title or not description or not classification:
            flash("Title, description, and classification are required", "warning")
            return redirect(url_for('add_complaint'))

        user_id = session['user_id']
        user = models.get_user_by_username(session['username'])
        otp = otp_manager.generate_otp(user_id)
        otp_manager.send_email(user['email'], otp)

        temp_file_paths = []
        if 'evidence_files' in request.files:
            files = request.files.getlist('evidence_files')
            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{user_id}_{filename}")
                    file.save(temp_filepath)
                    temp_file_paths.append({'original_name': filename, 'temp_path': temp_filepath})

        # --- DEMO: Always show Dehradun, Uttarakhand, India ---
        ip_address = request.form.get('public_ip') or get_client_ip()
        city = "Dehradun"
        country = "Uttarakhand, India"
        print(f"[DEMO MODE] Overriding location for {ip_address} -> {city}, {country}")

        temp_complaints[user_id] = {
            'title': title,
            'description': description,
            'classification': classification,
            'file_paths': temp_file_paths,
            'ip_address': ip_address,
            'ip_city': city,
            'ip_country': country
        }
        flash("An OTP has been sent to your email. Please verify.", "info")
        return redirect(url_for('verify_otp'))

    return render_template('add_complaint.html')

# --------------------------
# OTP verification and complaint finalize
# --------------------------
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    if request.method == 'POST':
        input_otp = request.form['otp']
        if otp_manager.validate_otp(user_id, input_otp):
            data = temp_complaints.get(user_id)
            if not data:
                flash("No complaint data found", "danger")
                return redirect(url_for('add_complaint'))

            role = session.get('role')
            if role == 'investigator':
                section_id = session.get('section_id')
            else:
                section_id = 1  # Default police section id for citizens

            # Add complaint to DB
            models.add_complaint(
                user_id,
                data['title'], data['description'],
                section_id,
                data.get('classification'),
                data.get('ip_address'),
                data.get('ip_country'),
                data.get('ip_city')
            )
            # Refresh user's complaints and find newly added complaint id
            complaints = models.get_complaints_by_user(user_id)
            new_comp = max(complaints, key=lambda c: c['complaint_id'])

            # Audit: log complaint submission
            try:
                models.add_audit_log(session.get('user_id'), f"Submitted complaint {new_comp['complaint_id']}")
            except Exception:
                pass

            # Update complaint section (assignment)
            try:
                models.update_complaint_section(new_comp['complaint_id'], section_id)
            except Exception:
                pass

            # Encrypt & store evidence, then remove temp files
            for file_info in data['file_paths']:
                try:
                    encrypted = encrypt_file(file_info['temp_path'])
                    models.add_evidence(new_comp['complaint_id'], file_info['original_name'], encrypted)
                except Exception as e:
                    print("Error adding evidence:", e)
                try:
                    os.remove(file_info['temp_path'])
                except Exception:
                    pass

            # cleanup
            if user_id in temp_complaints:
                del temp_complaints[user_id]

            flash("Complaint submitted successfully!", "success")
            return redirect(url_for('view_complaints'))
        else:
            flash("Invalid OTP. Try again.", "danger")

    return render_template('verify_otp.html')

# --------------------------
# View complaints & status
# --------------------------
@app.route('/view_complaints')
def view_complaints():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    complaints = models.get_complaints_by_user(session['user_id'])
    for c in complaints:
        c['evidence'] = models.get_evidence_by_complaint(c['complaint_id'])
    return render_template('view_complaints.html', complaints=complaints)


@app.route('/complaint_status/<int:complaint_id>')
def complaint_status(complaint_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    complaint = None
    try:
        complaint = models.get_complaint_by_id(complaint_id)
    except Exception as e:
        print("complaint_status: DB error:", e)
        flash("Could not load complaint (server error).", "danger")
        return redirect(url_for('dashboard'))

    if not complaint:
        flash("Complaint not found", "danger")
        return redirect(url_for('dashboard'))

    statuses = models.get_case_status_updates(complaint_id)
    return render_template('complaint_status.html', complaint=complaint, statuses=statuses)


# --------------------------
# Investigator: update status (with audit + notification)
# --------------------------
@app.route('/update_complaint_status/<int:complaint_id>', methods=['GET', 'POST'])
def update_complaint_status(complaint_id):
    if 'user_id' not in session or session.get('role') != 'investigator':
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))

    complaints = models.get_complaints_by_section(session.get('section_id'))
    complaint = next((c for c in complaints if c['complaint_id'] == complaint_id), None)

    if not complaint:
        flash("Complaint not found or unauthorized.", "danger")
        return redirect(url_for('police_dashboard'))

    if request.method == 'POST':
        new_status = request.form.get('status_update', '').strip()
        if new_status:
            models.add_case_status_update(complaint_id, new_status)
            models.update_complaint_status(complaint_id, new_status)

            # Audit log for status update
            try:
                models.add_audit_log(session.get('user_id'), f"Updated complaint {complaint_id} status to: {new_status}")
            except Exception:
                pass

            # Notification email (best-effort) to complaint owner
            try:
                comp = models.get_complaint_by_id(complaint_id)
                if comp and comp.get('user_id'):
                    owner = models.get_user_by_id(comp.get('user_id')) if hasattr(models, 'get_user_by_id') else None
                    if owner and owner.get('email'):
                        otp_manager.send_email(owner.get('email'), f"Your complaint #{complaint_id} status updated to: {new_status}")
            except Exception as e:
                print('Notification send error:', e)

            flash("Complaint status updated successfully", "success")
            return redirect(url_for('police_dashboard'))
        else:
            flash("Status update cannot be empty", "warning")

    status_updates = models.get_case_status_updates(complaint_id)
    return render_template('update_complaint_status.html',
                           complaint=complaint,
                           status_updates=status_updates)

# --------------------------
# Evidence download (decrypt & send)
# --------------------------
@app.route('/download_evidence/<int:complaint_id>/<filename>')
def download_evidence(complaint_id, filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_complaints = models.get_complaints_by_user(session['user_id'])
    complaint_ids = [c['complaint_id'] for c in user_complaints]
    if complaint_id not in complaint_ids and session.get('role') != 'investigator':
        flash("Unauthorized access", "danger")
        return redirect(url_for('view_complaints'))
    evidence_list = models.get_evidence_by_complaint(complaint_id)
    evidence = next((e for e in evidence_list if (e.get('file_name') == filename) or (e.get('file_path') == filename)), None)
    if not evidence:
        flash("Evidence not found", "danger")
        return redirect(url_for('view_complaints'))
    decrypted_data = decrypt_file(evidence['encrypted_blob'])
    return send_file(BytesIO(decrypted_data), download_name=filename, as_attachment=True)

# --------------------------
# Admin & profile routes
# --------------------------
@app.route('/admin/users')
def admin_users():
    # robust admin check (case-insensitive)
    role = (session.get('role') or '').lower()
    if 'user_id' not in session or role != 'admin':
        print(f"DEBUG: admin_users access denied. session role={session.get('role')}, user_id={session.get('user_id')}")
        flash('Unauthorized access', 'danger')
        return redirect(url_for('login'))

    users = []
    try:
        if hasattr(models, 'get_all_users'):
            users = models.get_all_users() or []
        else:
            flash('Admin function unavailable: get_all_users not found.', 'warning')
    except Exception as e:
        print("Error fetching users for admin:", e)
        flash('Could not load user list (server error). Check logs.', 'danger')
        users = []

    return render_template('admin_users.html', users=users)



@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = models.get_user_by_username(session['username'])
    return render_template('profile.html', user=user)
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    # reload current user info
    user = None
    try:
        user = models.get_user_by_username(session.get('username'))
    except Exception as e:
        print("edit_profile: error getting user:", e)
        flash("Could not load your profile (server error).", "danger")
        return redirect(url_for('profile'))

    if request.method == 'POST':
        # collect posted values (only allow username/email changes here)
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip()

        if not new_username or not new_email:
            flash("Username and email cannot be empty.", "warning")
            return redirect(url_for('edit_profile'))

        try:
            models.update_user_profile(user_id, username=new_username, email=new_email)
            # update session username if changed
            session['username'] = new_username
            # audit
            try:
                models.add_audit_log(session.get('user_id'), f"Updated profile (username/email)")
            except Exception:
                pass
            flash("Profile updated successfully.", "success")
            return redirect(url_for('profile'))
        except Exception as e:
            print("edit_profile: update error:", e)
            flash("Could not update profile (server error).", "danger")
            return redirect(url_for('edit_profile'))

    # GET: render edit form
    return render_template('edit_profile.html', user=user)

@app.route('/evidence_viewer/<int:complaint_id>')
def evidence_viewer(complaint_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    evidence = models.get_evidence_by_complaint(complaint_id)
    evidence_list = [{'file_name': e.get('file_name') or e.get('file_path') or ''} for e in evidence]
    return render_template('evidence_viewer.html', evidence=evidence_list, complaint_id=complaint_id)

# --------------------------
# Run server
# --------------------------
if __name__ == '__main__':
    app.run(debug=True)

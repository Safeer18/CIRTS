from backend.db import Database
import hashlib
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
FERNET_KEY = os.getenv('FERNET_KEY')
cipher_suite = Fernet(FERNET_KEY.encode())

db = Database()
db.connect()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# User functions
def create_user(username, password, role, email, section_id=None):
    password_hash = hash_password(password)
    query = """
    INSERT INTO Users (username, password_hash, role, email, section_id) 
    VALUES (%s, %s, %s, %s, %s)
    """
    return db.execute(query, (username, password_hash, role, email, section_id))

def get_user_by_username(username):
    query = "SELECT * FROM Users WHERE username = %s"
    return db.fetch_one(query, (username,))

def authenticate_user(username, password):
    user = get_user_by_username(username)
    if not user:
        return False
    return user['password_hash'] == hash_password(password)

# Police Sections functions
def get_police_sections():
    query = "SELECT * FROM PoliceSections"
    return db.fetch_all(query)

def get_police_section_by_id(section_id):
    query = "SELECT * FROM PoliceSections WHERE section_id = %s"
    return db.fetch_one(query, (section_id,))

# Complaint functions
def add_complaint(user_id, title, description, section_id=None):
    query = """
    INSERT INTO Complaints (user_id, title, description, section_id)
    VALUES (%s, %s, %s, %s)
    """
    return db.execute(query, (user_id, title, description, section_id))

def get_complaints_by_user(user_id):
    query = "SELECT * FROM Complaints WHERE user_id = %s"
    return db.fetch_all(query, (user_id,))

def get_complaints_by_section(section_id):
    query = "SELECT * FROM Complaints WHERE section_id = %s"
    return db.fetch_all(query, (section_id,))

def update_complaint_section(complaint_id, section_id):
    query = "UPDATE Complaints SET section_id = %s WHERE complaint_id = %s"
    return db.execute(query, (section_id, complaint_id))

def update_complaint_status(complaint_id, status):
    query = "UPDATE Complaints SET status = %s WHERE complaint_id = %s"
    return db.execute(query, (status, complaint_id))

# Evidence functions
def add_evidence(complaint_id, filename, encrypted_blob):
    query = """
    INSERT INTO Evidence (complaint_id, file_path, encrypted_blob)
    VALUES (%s, %s, %s)
    """
    return db.execute(query, (complaint_id, filename, encrypted_blob))

def get_evidence_by_complaint(complaint_id):
    query = "SELECT * FROM Evidence WHERE complaint_id = %s"
    return db.fetch_all(query, (complaint_id,))

# Case Status functions
def add_case_status_update(complaint_id, status_update):
    query = """
    INSERT INTO CaseStatus (complaint_id, status_update)
    VALUES (%s, %s)
    """
    return db.execute(query, (complaint_id, status_update))

def get_case_status_updates(complaint_id):
    query = "SELECT * FROM CaseStatus WHERE complaint_id = %s ORDER BY updated_at DESC"
    return db.fetch_all(query, (complaint_id,))
def assign_unassigned_complaints_to_section(section_id):
    query = """
    UPDATE Complaints
    SET section_id = %s
    WHERE section_id IS NULL
    """
    return db.execute(query, (section_id,))
def add_case_status_update(complaint_id, status_update):
    query = "INSERT INTO CaseStatus (complaint_id, status_update) VALUES (%s, %s)"
    return db.execute(query, (complaint_id, status_update))

def get_case_status_updates(complaint_id):
    query = "SELECT * FROM CaseStatus WHERE complaint_id = %s ORDER BY updated_at DESC"
    return db.fetch_all(query, (complaint_id,))

def update_complaint_status(complaint_id, status):
    query = "UPDATE Complaints SET status = %s WHERE complaint_id = %s"
    return db.execute(query, (status, complaint_id))
def add_complaint(user_id, title, description, section_id=None, classification=None,
                  ip_address=None, ip_country=None, ip_city=None):
    query = """
    INSERT INTO Complaints (user_id, title, description, section_id, classification,
                            ip_address, ip_country, ip_city)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    return db.execute(query, (user_id, title, description, section_id, classification,
                             ip_address, ip_country, ip_city))
def get_complaint_by_id(complaint_id):
    query = "SELECT * FROM Complaints WHERE complaint_id = %s"
    complaints = db.fetch_all(query, (complaint_id,))
    return complaints[0] if complaints else None
def add_audit_log(user_id, action, details=None):
    """Insert an audit log entry."""
    try:
        query = """INSERT INTO AuditLogs (user_id, action, details) VALUES (%s, %s, %s)"""
        return db.execute(query, (user_id, action, details))
    except Exception as e:
        print('add_audit_log error:', e)
        return None

def get_audit_logs(limit=100):
    query = "SELECT * FROM AuditLogs ORDER BY action_time DESC LIMIT %s"
    return db.fetch_all(query, (limit,))

def get_all_users():
    query = "SELECT user_id, username, email, role, section_id, created_at FROM Users ORDER BY created_at DESC"
    return db.fetch_all(query)

def get_user_by_id(user_id):
    query = "SELECT user_id, username, email, role, section_id, created_at FROM Users WHERE user_id = %s"
    return db.fetch_one(query, (user_id,))
# -------------------------
# User update helper
# -------------------------
def update_user_profile(user_id, username=None, email=None):
    """
    Update user profile fields. Returns True on success.
    """
    try:
        fields = []
        params = []
        if username is not None:
            fields.append("username = %s")
            params.append(username)
        if email is not None:
            fields.append("email = %s")
            params.append(email)
        if not fields:
            return False
        params.append(user_id)
        query = "UPDATE Users SET " + ", ".join(fields) + " WHERE user_id = %s"
        return db.execute(query, tuple(params))
    except Exception as e:
        print("update_user_profile error:", e)
        raise


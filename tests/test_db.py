import pytest
from backend import models

def test_user_creation_and_auth():
    # Create test user
    username = "testuser"
    password = "testpass"
    email = "testuser@example.com"
    role = "citizen"
    models.create_user(username, password, role, email)

    user = models.get_user_by_username(username)
    assert user is not None
    assert user['username'] == username

    auth_success = models.authenticate_user(username, password)
    assert auth_success

def test_add_and_fetch_complaint():
    user = models.get_user_by_username("alice")
    assert user is not None

    # Add complaint
    res = models.add_complaint(user['user_id'], "Test Complaint", "Description Test")
    assert res

    complaints = models.get_complaints_by_user(user['user_id'])
    assert any(c['title'] == "Test Complaint" for c in complaints)

def test_case_status_updates():
    complaints = models.get_complaints_by_user(1)
    complaint_id = complaints[0]['complaint_id']

    res = models.add_case_status_update(complaint_id, "Test status update")
    assert res

    statuses = models.get_case_status_updates(complaint_id)
    assert any(s['status_update'] == "Test status update" for s in statuses)

USE cirts;

INSERT INTO Users (username, password_hash, role, email) VALUES
('alice', SHA2('alice123', 256), 'citizen', 'alice@example.com'),
('bob', SHA2('bob123', 256), 'investigator', 'bob@example.com'),
('admin', SHA2('admin123', 256), 'admin', 'admin@example.com');

INSERT INTO Complaints (user_id, title, description, status) VALUES
(1, 'Phishing Email Incident', 'Received multiple phishing emails with suspicious links.', 'pending'),
(1, 'Unauthorized Bank Transaction', 'Unauthorized transaction noticed in bank statement.', 'under investigation');

INSERT INTO CaseStatus (complaint_id, status_update) VALUES
(1, 'Complaint received and logged'),
(1, 'Initial investigation in progress'),
(2, 'Complaint received and logged');

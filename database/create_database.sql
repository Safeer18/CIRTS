DROP DATABASE IF EXISTS cirts;
CREATE DATABASE cirts;
USE cirts;

CREATE TABLE Users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('citizen', 'investigator', 'admin') NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Complaints (
  complaint_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Evidence (
  evidence_id INT AUTO_INCREMENT PRIMARY KEY,
  complaint_id INT NOT NULL,
  file_path VARCHAR(255) NOT NULL,
  encrypted_blob LONGBLOB,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (complaint_id) REFERENCES Complaints(complaint_id)
);

CREATE TABLE CaseStatus (
  status_id INT AUTO_INCREMENT PRIMARY KEY,
  complaint_id INT NOT NULL,
  status_update TEXT NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (complaint_id) REFERENCES Complaints(complaint_id)
);

CREATE TABLE AuditLogs (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  action VARCHAR(255) NOT NULL,
  action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  details TEXT,
  FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
CREATE TABLE IF NOT EXISTS AuditLogs (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  action VARCHAR(255) NOT NULL,
  action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  details TEXT,
  FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


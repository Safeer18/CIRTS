CREATE TABLE IF NOT EXISTS PoliceSections (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

ALTER TABLE Users ADD COLUMN section_id INT NULL;
ALTER TABLE Users
  ADD CONSTRAINT fk_users_section
  FOREIGN KEY (section_id) REFERENCES PoliceSections(section_id);

ALTER TABLE Complaints ADD COLUMN section_id INT NULL;
ALTER TABLE Complaints
  ADD CONSTRAINT fk_complaints_section
  FOREIGN KEY (section_id) REFERENCES PoliceSections(section_id);

INSERT IGNORE INTO PoliceSections (name) VALUES
('Cyber Crime Cell'),
('Cyber Security Department'),
('Investigation Division');

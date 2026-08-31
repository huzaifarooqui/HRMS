from database import get_db

TABLES=[
"""CREATE TABLE IF NOT EXISTS admins(id INT AUTO_INCREMENT PRIMARY KEY,username VARCHAR(50) UNIQUE NOT NULL,password VARCHAR(255) NOT NULL,full_name VARCHAR(100),must_change_password TINYINT(1) DEFAULT 1,role VARCHAR(30) DEFAULT 'Super Admin',is_active TINYINT(1) DEFAULT 1,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,last_login DATETIME NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS departments(id INT AUTO_INCREMENT PRIMARY KEY,department_name VARCHAR(100) UNIQUE NOT NULL,description VARCHAR(255),head_employee_id INT NULL,status ENUM('Active','Inactive') DEFAULT 'Active',created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS employees(id INT AUTO_INCREMENT PRIMARY KEY,employee_id VARCHAR(20) UNIQUE,login_id VARCHAR(20) UNIQUE NOT NULL,first_name VARCHAR(50) NOT NULL,last_name VARCHAR(50),father_name VARCHAR(100),mother_name VARCHAR(100),father_phone VARCHAR(15),mother_phone VARCHAR(15),dob DATE,gender ENUM('Male','Female','Other'),email VARCHAR(100) UNIQUE,address TEXT,city VARCHAR(80),district VARCHAR(80),state VARCHAR(80),pincode VARCHAR(10),phone VARCHAR(15),alternate_phone VARCHAR(15),emergency_contact_name VARCHAR(100),emergency_contact_phone VARCHAR(15),blood_group VARCHAR(10),aadhar VARCHAR(12) UNIQUE,pan VARCHAR(10) UNIQUE,department_id INT NULL,department VARCHAR(100),designation VARCHAR(100),joining_date DATE,salary DECIMAL(12,2),target DECIMAL(12,2),password VARCHAR(255),photo VARCHAR(255),status ENUM('Active','Inactive') DEFAULT 'Active',created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,CONSTRAINT fk_emp_dept FOREIGN KEY(department_id) REFERENCES departments(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS company_settings(id INT PRIMARY KEY,company_name VARCHAR(200),company_logo VARCHAR(255),company_address TEXT,company_phone VARCHAR(20),company_email VARCHAR(150),office_latitude DECIMAL(10,8),office_longitude DECIMAL(11,8),office_start TIME,last_reporting TIME,half_day_after TIME DEFAULT '10:30:00',office_end TIME,working_hours INT DEFAULT 9,grace_minutes INT DEFAULT 15,gps_radius INT DEFAULT 3,weekend_days VARCHAR(30) DEFAULT 'Sunday',created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS attendance(id INT AUTO_INCREMENT PRIMARY KEY,employee_id INT NOT NULL,attendance_date DATE NOT NULL,check_in DATETIME,check_out DATETIME,check_in_lat DECIMAL(10,8),check_in_lng DECIMAL(11,8),check_out_lat DECIMAL(10,8),check_out_lng DECIMAL(11,8),working_minutes INT DEFAULT 0,late_minutes INT DEFAULT 0,overtime_minutes INT DEFAULT 0,early_exit_minutes INT DEFAULT 0,status ENUM('Present','Late','Half Day','Absent','Leave','Holiday') DEFAULT 'Present',remarks VARCHAR(255),late_reason VARCHAR(500),created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,UNIQUE KEY uq_att(employee_id,attendance_date),CONSTRAINT fk_att_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS attendance_audit(id INT AUTO_INCREMENT PRIMARY KEY,attendance_id INT NULL,employee_id INT NOT NULL,admin_id INT NULL,action_type VARCHAR(20) NOT NULL,reason VARCHAR(500) NOT NULL,old_data TEXT NULL,new_data TEXT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,INDEX idx_audit_attendance(attendance_id),CONSTRAINT fk_audit_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,CONSTRAINT fk_audit_admin FOREIGN KEY(admin_id) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS leave_types(id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(80) UNIQUE NOT NULL,code VARCHAR(20) UNIQUE NOT NULL,annual_limit DECIMAL(5,2) DEFAULT 0,is_paid TINYINT(1) DEFAULT 1,allow_half_day TINYINT(1) DEFAULT 1,status ENUM('Active','Inactive') DEFAULT 'Active',created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS leave_requests(id INT AUTO_INCREMENT PRIMARY KEY,employee_id INT NOT NULL,leave_type_id INT NOT NULL,start_date DATE NOT NULL,end_date DATE NOT NULL,day_type ENUM('Full Day','First Half','Second Half') DEFAULT 'Full Day',total_days DECIMAL(5,2) NOT NULL,reason VARCHAR(500) NOT NULL,contact_during_leave VARCHAR(20),status ENUM('Pending','Approved','Rejected','Cancelled') DEFAULT 'Pending',admin_remark VARCHAR(500),reviewed_by INT NULL,reviewed_at DATETIME NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,CONSTRAINT fk_lr_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,CONSTRAINT fk_lr_type FOREIGN KEY(leave_type_id) REFERENCES leave_types(id),CONSTRAINT fk_lr_admin FOREIGN KEY(reviewed_by) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS employee_documents(id INT AUTO_INCREMENT PRIMARY KEY,employee_id INT NOT NULL,title VARCHAR(150) NOT NULL,document_type VARCHAR(80) DEFAULT 'Other',file_name VARCHAR(255) NOT NULL,original_name VARCHAR(255),verification_status VARCHAR(30) DEFAULT 'Uploaded',verification_source VARCHAR(50) DEFAULT 'Manual Upload',external_document_id VARCHAR(255),verified_at DATETIME NULL,uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,CONSTRAINT fk_doc_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS allocation_snapshots(
id BIGINT AUTO_INCREMENT PRIMARY KEY,
employee_id INT NOT NULL,
source_folder VARCHAR(160) NOT NULL,
source_file VARCHAR(255) NOT NULL,
source_modified DATETIME NULL,
source_signature VARCHAR(160) NOT NULL,
headers_json LONGTEXT NOT NULL,
rows_json LONGTEXT NOT NULL,
imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
UNIQUE KEY uq_allocation_signature(employee_id,source_signature),
INDEX idx_allocation_employee_time(employee_id,imported_at),
CONSTRAINT fk_allocation_employee FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS admin_allocation_snapshots(
id BIGINT AUTO_INCREMENT PRIMARY KEY,
source_file VARCHAR(255) NOT NULL,
source_modified DATETIME NULL,
source_signature VARCHAR(160) NOT NULL UNIQUE,
tables_json LONGTEXT NOT NULL,
imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
INDEX idx_admin_allocation_time(imported_at)
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS digilocker_oauth_sessions(
id BIGINT AUTO_INCREMENT PRIMARY KEY,
state VARCHAR(160) NOT NULL UNIQUE,
employee_id INT NOT NULL,
admin_id INT NOT NULL,
code_verifier VARCHAR(160) NOT NULL,
access_token_enc LONGTEXT NULL,
refresh_token_enc LONGTEXT NULL,
issued_docs_json LONGTEXT NULL,
expires_at DATETIME NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
INDEX idx_dl_employee(employee_id),
INDEX idx_dl_expiry(expires_at),
CONSTRAINT fk_dl_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,
CONSTRAINT fk_dl_admin FOREIGN KEY(admin_id) REFERENCES admins(id) ON DELETE CASCADE
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS employee_feedback(
id BIGINT AUTO_INCREMENT PRIMARY KEY,
employee_id INT NOT NULL,
message TEXT NOT NULL,
status ENUM('New','Reviewed','Resolved') DEFAULT 'New',
admin_reply TEXT NULL,
reviewed_by INT NULL,
reviewed_at DATETIME NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
INDEX idx_feedback_status(status),
INDEX idx_feedback_employee(employee_id),
CONSTRAINT fk_feedback_employee FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,
CONSTRAINT fk_feedback_admin FOREIGN KEY(reviewed_by) REFERENCES admins(id) ON DELETE SET NULL
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS hr_document_drafts(
id BIGINT AUTO_INCREMENT PRIMARY KEY,
employee_id INT NOT NULL,
document_type VARCHAR(100) NOT NULL,
document_date DATE NOT NULL,
reference_no VARCHAR(80) NULL,
notes TEXT NULL,
fields_json LONGTEXT NULL,
status ENUM('Awaiting Template','Ready','Generated') DEFAULT 'Awaiting Template',
generated_file VARCHAR(255) NULL,
created_by INT NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
INDEX idx_hrdoc_employee(employee_id),
CONSTRAINT fk_hrdoc_employee FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,
CONSTRAINT fk_hrdoc_admin FOREIGN KEY(created_by) REFERENCES admins(id) ON DELETE RESTRICT
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS holidays(id INT AUTO_INCREMENT PRIMARY KEY,holiday_date DATE UNIQUE NOT NULL,holiday_name VARCHAR(150) NOT NULL,holiday_type ENUM('National','Festival','Company','Restricted','Weekly Off') DEFAULT 'Company',description VARCHAR(255),status ENUM('Active','Inactive') DEFAULT 'Active',created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS approval_requests(
id BIGINT AUTO_INCREMENT PRIMARY KEY,
request_type VARCHAR(60) NOT NULL,
entity_type VARCHAR(60) NOT NULL,
entity_id VARCHAR(80) NOT NULL,
title VARCHAR(180) NOT NULL,
payload_json LONGTEXT NULL,
status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
current_stage ENUM('HR','Manager','Owner','Completed') DEFAULT 'HR',
submitted_by INT NOT NULL,
hr_by INT NULL, hr_at DATETIME NULL, hr_note VARCHAR(500) NULL,
manager_by INT NULL, manager_at DATETIME NULL, manager_note VARCHAR(500) NULL,
owner_by INT NULL, owner_at DATETIME NULL, owner_note VARCHAR(500) NULL,
rejected_by INT NULL, rejected_at DATETIME NULL, rejection_note VARCHAR(500) NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
INDEX idx_approval_status_stage(status,current_stage),
INDEX idx_approval_entity(entity_type,entity_id),
CONSTRAINT fk_approval_submitter FOREIGN KEY(submitted_by) REFERENCES admins(id) ON DELETE RESTRICT,
CONSTRAINT fk_approval_hr FOREIGN KEY(hr_by) REFERENCES admins(id) ON DELETE SET NULL,
CONSTRAINT fk_approval_manager FOREIGN KEY(manager_by) REFERENCES admins(id) ON DELETE SET NULL,
CONSTRAINT fk_approval_owner FOREIGN KEY(owner_by) REFERENCES admins(id) ON DELETE SET NULL,
CONSTRAINT fk_approval_rejected FOREIGN KEY(rejected_by) REFERENCES admins(id) ON DELETE SET NULL
) ENGINE=InnoDB"""
]


TABLES.extend([
"""CREATE TABLE IF NOT EXISTS system_audit_log(
id BIGINT AUTO_INCREMENT PRIMARY KEY,
admin_id INT NULL,
employee_id INT NULL,
action VARCHAR(100) NOT NULL,
entity_type VARCHAR(80) NOT NULL,
entity_id VARCHAR(80) NULL,
details TEXT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
INDEX idx_audit_action(action),
INDEX idx_audit_created(created_at),
CONSTRAINT fk_sysaudit_admin FOREIGN KEY(admin_id) REFERENCES admins(id) ON DELETE SET NULL,
CONSTRAINT fk_sysaudit_employee FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE SET NULL
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS employee_notifications(
id BIGINT AUTO_INCREMENT PRIMARY KEY,
employee_id INT NOT NULL,
title VARCHAR(160) NOT NULL,
message VARCHAR(500) NOT NULL,
notification_type VARCHAR(50) DEFAULT 'General',
is_read TINYINT(1) DEFAULT 0,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
read_at DATETIME NULL,
INDEX idx_notify_employee(employee_id,is_read),
CONSTRAINT fk_notify_employee FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS attendance_month_locks(
month_key CHAR(7) PRIMARY KEY,
is_locked TINYINT(1) DEFAULT 1,
locked_by INT NULL,
locked_at DATETIME NULL,
reopened_by INT NULL,
reopened_at DATETIME NULL,
note VARCHAR(500) NULL,
CONSTRAINT fk_attlock_admin FOREIGN KEY(locked_by) REFERENCES admins(id) ON DELETE SET NULL,
CONSTRAINT fk_attreopen_admin FOREIGN KEY(reopened_by) REFERENCES admins(id) ON DELETE SET NULL
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS payroll_locks(
month_key CHAR(7) PRIMARY KEY,
is_finalized TINYINT(1) DEFAULT 1,
finalized_by INT NULL,
finalized_at DATETIME NULL,
snapshot_json LONGTEXT NULL,
reopened_by INT NULL,
reopened_at DATETIME NULL,
CONSTRAINT fk_payroll_lock_admin FOREIGN KEY(finalized_by) REFERENCES admins(id) ON DELETE SET NULL,
CONSTRAINT fk_payroll_reopen_admin FOREIGN KEY(reopened_by) REFERENCES admins(id) ON DELETE SET NULL
) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS employee_exit_checklist(
id BIGINT AUTO_INCREMENT PRIMARY KEY,
employee_id INT NOT NULL,
asset_returned TINYINT(1) DEFAULT 0,
handover_completed TINYINT(1) DEFAULT 0,
documents_completed TINYINT(1) DEFAULT 0,
attendance_closed TINYINT(1) DEFAULT 0,
fnf_status VARCHAR(50) DEFAULT 'Pending',
remarks VARCHAR(500) NULL,
updated_by INT NULL,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
UNIQUE KEY uq_exit_employee(employee_id),
CONSTRAINT fk_exit_employee FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,
CONSTRAINT fk_exit_admin FOREIGN KEY(updated_by) REFERENCES admins(id) ON DELETE SET NULL
) ENGINE=InnoDB"""
])

TABLES.extend([
"""CREATE TABLE IF NOT EXISTS attendance_regularization(id BIGINT AUTO_INCREMENT PRIMARY KEY,employee_id INT NOT NULL,attendance_date DATE NOT NULL,request_type VARCHAR(50) NOT NULL,requested_check_in TIME NULL,requested_check_out TIME NULL,requested_status VARCHAR(30) NULL,reason VARCHAR(500) NOT NULL,evidence_file VARCHAR(255) NULL,status VARCHAR(30) DEFAULT 'Pending',approval_request_id BIGINT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,INDEX idx_reg_emp(employee_id),CONSTRAINT fk_reg_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS employee_assets(id BIGINT AUTO_INCREMENT PRIMARY KEY,employee_id INT NOT NULL,asset_type VARCHAR(80) NOT NULL,asset_name VARCHAR(150) NOT NULL,asset_code VARCHAR(80) NULL,serial_no VARCHAR(120) NULL,issue_date DATE NULL,return_date DATE NULL,issue_condition VARCHAR(120) NULL,return_condition VARCHAR(120) NULL,status VARCHAR(30) DEFAULT 'Issued',remarks VARCHAR(500) NULL,created_by INT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,INDEX idx_asset_emp(employee_id),CONSTRAINT fk_asset_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,CONSTRAINT fk_asset_admin FOREIGN KEY(created_by) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS company_announcements(id BIGINT AUTO_INCREMENT PRIMARY KEY,title VARCHAR(180) NOT NULL,message TEXT NOT NULL,announcement_type VARCHAR(50) DEFAULT 'Notice',priority VARCHAR(20) DEFAULT 'Normal',publish_from DATETIME NOT NULL,publish_until DATETIME NULL,requires_ack TINYINT(1) DEFAULT 0,status VARCHAR(20) DEFAULT 'Active',created_by INT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,CONSTRAINT fk_announce_admin FOREIGN KEY(created_by) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS announcement_acknowledgements(id BIGINT AUTO_INCREMENT PRIMARY KEY,announcement_id BIGINT NOT NULL,employee_id INT NOT NULL,acknowledged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,UNIQUE KEY uq_announce_ack(announcement_id,employee_id),CONSTRAINT fk_ack_ann FOREIGN KEY(announcement_id) REFERENCES company_announcements(id) ON DELETE CASCADE,CONSTRAINT fk_ack_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS employee_lifecycle(id BIGINT AUTO_INCREMENT PRIMARY KEY,employee_id INT NOT NULL,event_type VARCHAR(60) NOT NULL,title VARCHAR(180) NOT NULL,details TEXT NULL,effective_date DATE NOT NULL,created_by INT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,INDEX idx_lifecycle_emp(employee_id,effective_date),CONSTRAINT fk_lifecycle_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,CONSTRAINT fk_lifecycle_admin FOREIGN KEY(created_by) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS hr_cases(id BIGINT AUTO_INCREMENT PRIMARY KEY,case_no VARCHAR(40) UNIQUE NOT NULL,employee_id INT NOT NULL,case_type VARCHAR(60) NOT NULL,title VARCHAR(180) NOT NULL,description TEXT NOT NULL,severity VARCHAR(20) DEFAULT 'Normal',status VARCHAR(30) DEFAULT 'Open',resolution TEXT NULL,opened_by INT NULL,closed_by INT NULL,closed_at DATETIME NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,INDEX idx_case_emp(employee_id),CONSTRAINT fk_case_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,CONSTRAINT fk_case_open FOREIGN KEY(opened_by) REFERENCES admins(id) ON DELETE SET NULL,CONSTRAINT fk_case_close FOREIGN KEY(closed_by) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS onboarding_checklist(id BIGINT AUTO_INCREMENT PRIMARY KEY,employee_id INT NOT NULL,documents_verified TINYINT(1) DEFAULT 0,id_card_issued TINYINT(1) DEFAULT 0,policy_acknowledged TINYINT(1) DEFAULT 0,assets_issued TINYINT(1) DEFAULT 0,orientation_completed TINYINT(1) DEFAULT 0,remarks VARCHAR(500) NULL,updated_by INT NULL,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,UNIQUE KEY uq_onboard_emp(employee_id),CONSTRAINT fk_onboard_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,CONSTRAINT fk_onboard_admin FOREIGN KEY(updated_by) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS admin_notifications(id BIGINT AUTO_INCREMENT PRIMARY KEY,admin_role VARCHAR(30) NOT NULL,title VARCHAR(180) NOT NULL,message VARCHAR(500) NOT NULL,notification_type VARCHAR(50) DEFAULT 'Workflow',entity_type VARCHAR(60) NULL,entity_id VARCHAR(80) NULL,is_read TINYINT(1) DEFAULT 0,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,INDEX idx_admin_notify(admin_role,is_read)) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS admin_login_history(id BIGINT AUTO_INCREMENT PRIMARY KEY,admin_id INT NOT NULL,login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,ip_address VARCHAR(64) NULL,user_agent VARCHAR(500) NULL,CONSTRAINT fk_login_admin FOREIGN KEY(admin_id) REFERENCES admins(id) ON DELETE CASCADE) ENGINE=InnoDB"""
])



ADVANCED_TABLES=[
"""CREATE TABLE IF NOT EXISTS automation_rules(id BIGINT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(160) NOT NULL,trigger_type VARCHAR(60) NOT NULL,threshold_value INT DEFAULT 0,action_type VARCHAR(60) NOT NULL,action_message VARCHAR(500) NULL,is_active TINYINT(1) DEFAULT 1,created_by INT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,INDEX idx_auto_active(is_active),CONSTRAINT fk_auto_admin FOREIGN KEY(created_by) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS scheduled_reports(id BIGINT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(160) NOT NULL,report_type VARCHAR(60) NOT NULL,frequency VARCHAR(30) NOT NULL,day_of_month INT NULL,day_of_week INT NULL,recipient_role VARCHAR(30) DEFAULT 'HR',is_active TINYINT(1) DEFAULT 1,last_run_at DATETIME NULL,next_run_at DATETIME NULL,created_by INT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,INDEX idx_schedule_active(is_active),CONSTRAINT fk_schedule_admin FOREIGN KEY(created_by) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS payroll_records(id BIGINT AUTO_INCREMENT PRIMARY KEY,employee_id INT NOT NULL,salary_month CHAR(7) NOT NULL,total_days INT DEFAULT 0,present_days DECIMAL(6,2) DEFAULT 0,late_days INT DEFAULT 0,half_days DECIMAL(6,2) DEFAULT 0,absent_days DECIMAL(6,2) DEFAULT 0,final_days DECIMAL(6,2) DEFAULT 0,gross_salary DECIMAL(12,2) DEFAULT 0,incentive DECIMAL(12,2) DEFAULT 0,other_deductions DECIMAL(12,2) DEFAULT 0,net_salary DECIMAL(12,2) DEFAULT 0,status VARCHAR(30) DEFAULT 'Draft',generated_by INT NULL,generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,UNIQUE KEY uq_payroll_emp_month(employee_id,salary_month),CONSTRAINT fk_payroll_emp FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,CONSTRAINT fk_payroll_records_generated_by_admin FOREIGN KEY(generated_by) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
"""CREATE TABLE IF NOT EXISTS security_events(id BIGINT AUTO_INCREMENT PRIMARY KEY,event_type VARCHAR(80) NOT NULL,admin_id INT NULL,ip_address VARCHAR(64) NULL,user_agent VARCHAR(500) NULL,details VARCHAR(500) NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,INDEX idx_sec_created(created_at),CONSTRAINT fk_sec_admin FOREIGN KEY(admin_id) REFERENCES admins(id) ON DELETE SET NULL) ENGINE=InnoDB""",
]

COLUMNS={
'admins':[('role',"VARCHAR(30) DEFAULT 'Super Admin'"),('is_active','TINYINT(1) DEFAULT 1'),('dob','DATE NULL')],
'approval_requests':[('stage_entered_at','DATETIME NULL'),('sla_hours','INT DEFAULT 24'),('escalation_count','INT DEFAULT 0'),('last_reminder_at','DATETIME NULL'),('reference_no','VARCHAR(50) NULL')],
'employee_feedback':[('response_locked','TINYINT(1) DEFAULT 0'),('locked_at','DATETIME NULL')],
'employees':[('employment_stage',"VARCHAR(30) DEFAULT 'Active'"),('archived_at','DATETIME NULL'),('archived_by','INT NULL'),('emergency_contact_name','VARCHAR(100) NULL'),('emergency_contact_phone','VARCHAR(15) NULL'),('blood_group','VARCHAR(10) NULL'),('father_phone','VARCHAR(15) NULL'),('mother_phone','VARCHAR(15) NULL'),('district','VARCHAR(80) NULL'),('target','DECIMAL(12,2) NULL'),('inactive_from','DATE NULL')],
'attendance':[('check_in_lat','DECIMAL(10,8) NULL'),('check_in_lng','DECIMAL(11,8) NULL'),('check_out_lat','DECIMAL(10,8) NULL'),('check_out_lng','DECIMAL(11,8) NULL'),('early_exit_minutes','INT DEFAULT 0'),('late_reason','VARCHAR(500) NULL')],
'company_settings':[('weekend_days',"VARCHAR(30) DEFAULT 'Sunday'"),('company_website','VARCHAR(180) NULL'),('company_about','TEXT NULL'),('owner_name','VARCHAR(120) NULL'),('owner_title','VARCHAR(100) NULL'),('manager_name','VARCHAR(120) NULL'),('manager_title','VARCHAR(100) NULL'),('hr_name','VARCHAR(120) NULL'),('hr_title','VARCHAR(100) NULL'),('management_contact','VARCHAR(30) NULL'),('half_day_after',"TIME DEFAULT '10:30:00'")],
'departments':[('head_employee_id','INT NULL')],
'hr_document_drafts':[('document_number','VARCHAR(100) NULL'),('version_no','INT DEFAULT 1'),('issued_at','DATETIME NULL')],
'employee_documents':[('document_number','VARCHAR(100) NULL'),('version_no','INT DEFAULT 1'),('issue_date','DATE NULL'),('expiry_date','DATE NULL'),('document_status',"VARCHAR(30) DEFAULT 'Active'"),('remarks','VARCHAR(500) NULL'),('uploaded_by','INT NULL'),('deleted_at','DATETIME NULL'),('deleted_by','INT NULL'),('acknowledged_at','DATETIME NULL'),('title',"VARCHAR(150) NULL"),('document_type',"VARCHAR(80) DEFAULT 'Other'"),('file_name',"VARCHAR(255) NULL"),('original_name',"VARCHAR(255) NULL"),('verification_status',"VARCHAR(30) DEFAULT 'Uploaded'"),('verification_source',"VARCHAR(50) DEFAULT 'Manual Upload'"),('external_document_id','VARCHAR(255) NULL'),('verified_at','DATETIME NULL'),('uploaded_at',"TIMESTAMP DEFAULT CURRENT_TIMESTAMP")]
}

def setup_database():
    cnx=get_db();cur=cnx.cursor(dictionary=True)
    try:
        for sql in TABLES:cur.execute(sql)
        for sql in ADVANCED_TABLES:cur.execute(sql)
        cur.execute("SELECT DATABASE() db");db=cur.fetchone()['db']
        for table,cols in COLUMNS.items():
            for name,definition in cols:
                cur.execute("SELECT COUNT(*) c FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s",(db,table,name))
                if cur.fetchone()['c']==0:cur.execute(f"ALTER TABLE `{table}` ADD COLUMN `{name}` {definition}")
        cur.execute("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='employee_documents'",(db,));doc_cols={row['COLUMN_NAME'] for row in cur.fetchall()}
        if 'document_name' in doc_cols:cur.execute("UPDATE employee_documents SET title=COALESCE(NULLIF(title,''),document_name) WHERE title IS NULL OR title=''")
        if 'document_path' in doc_cols:cur.execute("UPDATE employee_documents SET file_name=COALESCE(NULLIF(file_name,''),document_path) WHERE file_name IS NULL OR file_name=''")
        if 'file_path' in doc_cols:cur.execute("UPDATE employee_documents SET file_name=COALESCE(NULLIF(file_name,''),file_path) WHERE file_name IS NULL OR file_name=''")
        if 'original_filename' in doc_cols:cur.execute("UPDATE employee_documents SET original_name=COALESCE(NULLIF(original_name,''),original_filename) WHERE original_name IS NULL OR original_name=''")
        cur.execute("UPDATE employee_documents SET title=COALESCE(NULLIF(title,''),NULLIF(original_name,''),NULLIF(file_name,''),'Document'),document_type=COALESCE(NULLIF(document_type,''),'Other'),verification_status=COALESCE(NULLIF(verification_status,''),'Uploaded'),verification_source=COALESCE(NULLIF(verification_source,''),'Manual Upload')")
        cur.execute("UPDATE admins SET role=COALESCE(NULLIF(role,''),'Super Admin'),is_active=COALESCE(is_active,1)")
        cur.execute("INSERT IGNORE INTO company_settings(id,company_name,office_start,last_reporting,half_day_after,office_end,working_hours,grace_minutes,gps_radius) VALUES(1,'Guru Ram Singh Ji Associates','09:30:00','09:45:00','10:30:00','18:30:00',9,15,3)")
        cur.execute("INSERT IGNORE INTO admins(username,password,full_name,must_change_password,role,is_active) VALUES('admin','Admin@123','System Administrator',1,'Super Admin',1)")
        cur.execute("INSERT IGNORE INTO leave_types(name,code,annual_limit,is_paid,allow_half_day) VALUES('Casual Leave','CL',12,1,1),('Sick Leave','SL',10,1,1),('Earned Leave','EL',15,1,0),('Leave Without Pay','LWP',0,0,1),('Emergency Leave','EML',5,1,1),('Work From Home','WFH',12,1,0),('Comp Off','CO',10,1,1),('Maternity Leave','ML',180,1,0),('Paternity Leave','PL',15,1,0),('Marriage Leave','MRL',7,1,0),('Other / Custom','OTHER',0,0,1)")
        cnx.commit()
    finally:cur.close();cnx.close()

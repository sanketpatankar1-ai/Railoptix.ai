# Supabase Migration Guide for RailOptix

This guide explains how to migrate the RailOptix local PostgreSQL database to a managed Supabase PostgreSQL instance, without making any code changes. 

## 1. Create the Supabase Project
1. Go to [Supabase](https://supabase.com/) and sign in.
2. Click **New Project**, select your organization, and choose a project name (e.g., `RailOptix`).
3. Generate a strong Database Password and securely save it.
4. Select a region close to your users and click **Create new project**.

## 2. Find Database Credentials
Once the project is created:
1. Go to **Project Settings -> Database**.
2. Scroll down to **Connection string**.
3. Select **URI**.
4. The string will look like this:
   `postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:5432/postgres`

*(Note: Use port `5432` for direct/session connection, as SQLAlchemy manages its own connection pool natively via `psycopg2-binary`.)*

## 3. Configure `.env`
Update your `~/Downloads/RailOptix-main/.env` file. Replace the `DATABASE_URL` value with your Supabase URI.

**Old `.env`**:
```env
DATABASE_URL=postgresql://postgres@localhost:5432/railopt
```

**New `.env`**:
```env
DATABASE_URL=postgresql://postgres.[project-ref]:SUPABASE_DB_PASSWORD@aws-0-[region].pooler.supabase.com:5432/postgres
```

## 4. Run the Schema Migration Script (SQL Editor)
Go to the **Supabase Dashboard -> SQL Editor -> New Query**. Paste the following script and click **Run**. This will create the required Enums, Tables, and Indexes in the exact topological order required by the RailOptix SQLAlchemy models.

```sql
-- ENUM Definitions
CREATE TYPE line_type_enum AS ENUM ('single', 'double', 'triple', 'quadruple');
CREATE TYPE traffic_density_enum AS ENUM ('high', 'medium', 'low');
CREATE TYPE window_type_enum AS ENUM ('night', 'day', 'mixed', 'morning', 'midday', 'evening');
CREATE TYPE train_type_enum AS ENUM ('passenger', 'goods', 'express', 'mail', 'special');
CREATE TYPE frequency_enum AS ENUM ('daily', 'biweekly', 'weekly');

-- Table: corridor_blocks
CREATE TABLE corridor_blocks (
	section_id VARCHAR(50) NOT NULL, 
	section_name VARCHAR(200) NOT NULL, 
	from_station VARCHAR(100) NOT NULL, 
	to_station VARCHAR(100) NOT NULL, 
	line_type line_type_enum NOT NULL, 
	traffic_density traffic_density_enum NOT NULL, 
	zone VARCHAR(100) NOT NULL, 
	zone_code VARCHAR(20) NOT NULL, 
	division VARCHAR(100) NOT NULL, 
	total_km FLOAT NOT NULL, 
	electrified BOOLEAN NOT NULL, 
	lat_from FLOAT, 
	lon_from FLOAT, 
	lat_to FLOAT, 
	lon_to FLOAT, 
	PRIMARY KEY (section_id)
);
CREATE INDEX ix_corridor_blocks_zone_code ON corridor_blocks (zone_code);

-- Table: users
CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	email VARCHAR(200) NOT NULL, 
	password VARCHAR(255) NOT NULL, 
	role VARCHAR(18) NOT NULL, 
	department VARCHAR(100), 
	zonal_railway VARCHAR(100) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_users_email ON users (email);

-- Table: audit_logs
CREATE TABLE audit_logs (
	id SERIAL NOT NULL, 
	action VARCHAR(100) NOT NULL, 
	user_id VARCHAR(36), 
	user_name VARCHAR(100) NOT NULL, 
	target_id VARCHAR(100), 
	target_type VARCHAR(50), 
	details TEXT NOT NULL, 
	ip_address VARCHAR(50), 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_audit_logs_action ON audit_logs (action);
CREATE INDEX ix_audit_logs_created_at ON audit_logs (created_at);

-- Table: block_schedules
CREATE TABLE block_schedules (
	id VARCHAR(36) NOT NULL, 
	schedule_id VARCHAR(80) NOT NULL, 
	section_id VARCHAR(50) NOT NULL, 
	section_name VARCHAR(200) NOT NULL, 
	zone_code VARCHAR(20), 
	window_start TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	window_end TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	total_duration_min INTEGER NOT NULL, 
	departments JSON NOT NULL, 
	task_ids JSON NOT NULL, 
	task_id_strings JSON NOT NULL, 
	is_multi_department BOOLEAN NOT NULL, 
	plan_type VARCHAR(7) NOT NULL, 
	week_number INTEGER, 
	month_year VARCHAR(10), 
	horizon_label VARCHAR(20), 
	optimizer_score FLOAT NOT NULL, 
	ai_reasoning TEXT NOT NULL, 
	original_window JSON, 
	original_score FLOAT, 
	availability_score FLOAT, 
	ttt_conflicts JSON, 
	status VARCHAR(9) NOT NULL, 
	approved_by VARCHAR(36), 
	approval_date TIMESTAMP WITHOUT TIME ZONE, 
	rejection_reason TEXT NOT NULL, 
	is_overridden BOOLEAN NOT NULL, 
	override_reason TEXT NOT NULL, 
	carry_forward_from VARCHAR(80), 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (schedule_id), 
	FOREIGN KEY(approved_by) REFERENCES users (id)
);
CREATE INDEX ix_schedules_plan_type_status ON block_schedules (plan_type, status);
CREATE INDEX ix_schedules_section_start ON block_schedules (section_id, window_start);
CREATE INDEX ix_block_schedules_zone_code ON block_schedules (zone_code);
CREATE INDEX ix_block_schedules_status ON block_schedules (status);
CREATE INDEX ix_block_schedules_section_id ON block_schedules (section_id);
CREATE INDEX ix_schedules_week ON block_schedules (week_number);

-- Table: block_windows
CREATE TABLE block_windows (
	id SERIAL NOT NULL, 
	section_id VARCHAR(50) NOT NULL, 
	day_of_week INTEGER NOT NULL, 
	start_time TIME WITHOUT TIME ZONE NOT NULL, 
	end_time TIME WITHOUT TIME ZONE NOT NULL, 
	window_type window_type_enum NOT NULL, 
	max_duration_minutes INTEGER NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(section_id) REFERENCES corridor_blocks (section_id) ON DELETE CASCADE
);
CREATE INDEX ix_block_windows_section_day ON block_windows (section_id, day_of_week);

-- Table: maintenance_tasks
CREATE TABLE maintenance_tasks (
	id VARCHAR(36) NOT NULL, 
	task_id VARCHAR(60) NOT NULL, 
	source_system VARCHAR(4) NOT NULL, 
	department VARCHAR(21) NOT NULL, 
	section_id VARCHAR(50) NOT NULL, 
	section_name VARCHAR(200) NOT NULL, 
	zone_code VARCHAR(20), 
	defect_type VARCHAR(200) NOT NULL, 
	defect_description TEXT NOT NULL, 
	criticality VARCHAR(8) NOT NULL, 
	reported_date DATE NOT NULL, 
	due_date DATE NOT NULL, 
	estimated_duration INTEGER NOT NULL, 
	location_km FLOAT, 
	status VARCHAR(11) NOT NULL, 
	criticality_score FLOAT, 
	urgency_tier VARCHAR(20), 
	score_breakdown JSON, 
	ai_reasoning TEXT, 
	ml_score FLOAT, 
	rule_score FLOAT, 
	recurrence_count INTEGER NOT NULL, 
	last_occurrence DATE, 
	inspection_gap_days INTEGER NOT NULL, 
	import_source VARCHAR(11) NOT NULL, 
	import_batch_id VARCHAR(60), 
	assigned_to VARCHAR(36), 
	notes TEXT NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(section_id) REFERENCES corridor_blocks (section_id), 
	FOREIGN KEY(assigned_to) REFERENCES users (id)
);
CREATE INDEX ix_maintenance_tasks_status ON maintenance_tasks (status);
CREATE INDEX ix_tasks_criticality ON maintenance_tasks (criticality);
CREATE INDEX ix_maintenance_tasks_due_date ON maintenance_tasks (due_date);
CREATE UNIQUE INDEX ix_maintenance_tasks_task_id ON maintenance_tasks (task_id);
CREATE INDEX ix_maintenance_tasks_zone_code ON maintenance_tasks (zone_code);
CREATE INDEX ix_tasks_dept_status ON maintenance_tasks (department, status);
CREATE INDEX ix_tasks_section ON maintenance_tasks (section_id);

-- Table: traffic_data
CREATE TABLE traffic_data (
	id SERIAL NOT NULL, 
	section_id VARCHAR(50) NOT NULL, 
	date DATE NOT NULL, 
	hour INTEGER NOT NULL, 
	passenger_trains INTEGER NOT NULL, 
	goods_trains INTEGER NOT NULL, 
	total_trains INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(section_id) REFERENCES corridor_blocks (section_id) ON DELETE CASCADE
);
CREATE INDEX ix_traffic_data_section_date_hour ON traffic_data (section_id, date, hour);

-- Table: train_timetable
CREATE TABLE train_timetable (
	id SERIAL NOT NULL, 
	train_no VARCHAR(10) NOT NULL, 
	train_name VARCHAR(200), 
	section_id VARCHAR(50) NOT NULL, 
	day_of_week INTEGER NOT NULL, 
	departure_time TIME WITHOUT TIME ZONE NOT NULL, 
	arrival_time TIME WITHOUT TIME ZONE NOT NULL, 
	train_type train_type_enum NOT NULL, 
	frequency frequency_enum NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	ttt_source VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(section_id) REFERENCES corridor_blocks (section_id) ON DELETE CASCADE
);
CREATE INDEX ix_timetable_section_day ON train_timetable (section_id, day_of_week);

-- Table: alert_logs
CREATE TABLE alert_logs (
	id SERIAL NOT NULL, 
	alert_type VARCHAR(50) NOT NULL, 
	task_id VARCHAR(36), 
	schedule_id VARCHAR(80), 
	section_id VARCHAR(50), 
	message TEXT NOT NULL, 
	severity VARCHAR(20) NOT NULL, 
	is_read BOOLEAN NOT NULL, 
	resolved_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(task_id) REFERENCES maintenance_tasks (id) ON DELETE CASCADE
);
CREATE INDEX ix_alert_logs_is_read ON alert_logs (is_read);
CREATE INDEX ix_alert_logs_alert_type ON alert_logs (alert_type);
CREATE INDEX ix_alert_logs_created_at ON alert_logs (created_at);
```

## 5. Testing the Connection
You can test if the database is configured properly by hitting the health check endpoint using `curl`:
```bash
curl -s http://localhost:8000/api/health
```
If the connection is valid, you'll see a response containing `"database": "ok"`. *(If the database tables are empty, `backend/main.py` will automatically seed demo data into Supabase the first time it starts).*

## 6. Running the Project

**Start Backend (Terminal 1)**
```bash
cd ~/Downloads/RailOptix-main
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend (Terminal 2)**
```bash
cd ~/Downloads/RailOptix-main/client
npm run dev
```

## 7. Verifying Supabase Usage
1. Open the application at `http://localhost:3000`.
2. Login and navigate through the dashboard.
3. Open the **Supabase Dashboard -> Table Editor**, and verify that records are actively being created in tables like `audit_logs` or `maintenance_tasks`.

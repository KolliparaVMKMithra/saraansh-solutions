"""
Database Module
Handles all database operations for applicant data
"""
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import sqlite3

try:
    import pymssql
    PYMSSQL_AVAILABLE = True
except ImportError:
    PYMSSQL_AVAILABLE = False


class Database:
    def __init__(self):
        self.conn = None
        self.use_sqlite = False

        db_server = os.getenv('DB_SERVER')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_name = os.getenv('DB_NAME')

        if PYMSSQL_AVAILABLE and db_server and db_password:
            self._connect_azure(db_server, db_user, db_password, db_name)
        else:
            print("[DB] Missing Azure SQL config, using SQLite", flush=True)
            self.use_sqlite = True
            self._connect_sqlite()

        # Create tables after connection
        self.create_tables()

    def _connect_azure(self, server, user, password, database):
        try:
            self.conn = pymssql.connect(
                server=server,
                user=user,
                password=password,
                database=database,
                login_timeout=30,
                tds_version='7.4'
            )
            self.use_sqlite = False
            print("[DB] Connected to Azure SQL successfully", flush=True)
        except Exception as e:
            print(f"[DB] Azure SQL connection failed: {e}", flush=True)
            self.use_sqlite = True
            self._connect_sqlite()

    def _connect_sqlite(self):
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(backend_dir, 'applicants.db')
        print(f"[DB] Connecting to SQLite: {db_path}", flush=True)
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            print("[DB] SQLite connected successfully", flush=True)
        except Exception as e:
            print(f"[DB] SQLite error: {e}, using in-memory", flush=True)
            self.conn = sqlite3.connect(':memory:', check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

    def _ensure_column(self, cursor, table_name: str, column_definition: str):
        if self.use_sqlite:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row['name'] for row in cursor.fetchall()]
            col_name = column_definition.split()[0]
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")
        else:
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}")
            except Exception:
                pass

    def create_tables(self):
        if not self.conn:
            return

        cursor = self.conn.cursor()

        if self.use_sqlite:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS Applicants (
                applicationId TEXT PRIMARY KEY,
                applicantName TEXT NOT NULL,
                emailAddress TEXT,
                mobileNumber TEXT,
                city TEXT,
                state TEXT,
                applicantStatus TEXT DEFAULT 'Active',
                jobTitle TEXT,
                ownership TEXT,
                workAuthorization TEXT,
                source TEXT,
                createdBy TEXT,
                createdOn TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modifiedOn TIMESTAMP,
                techSkills TEXT,
                resumeText TEXT,
                blobUrl TEXT
            )
            """
            try:
                cursor.execute(create_table_sql)
                self.conn.commit()
                self._ensure_column(cursor, 'Applicants', 'techSkills TEXT')
                self._ensure_column(cursor, 'Applicants', 'resumeText TEXT')
                self._ensure_column(cursor, 'Applicants', 'blobUrl TEXT')
                self.conn.commit()
            except Exception as e:
                print(f"Warning: Could not create tables: {e}", flush=True)
        else:
            create_table_sql = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Applicants' AND xtype='U')
            CREATE TABLE Applicants (
                applicationId NVARCHAR(255) PRIMARY KEY,
                applicantName NVARCHAR(255) NOT NULL,
                emailAddress NVARCHAR(255),
                mobileNumber NVARCHAR(50),
                city NVARCHAR(100),
                state NVARCHAR(100),
                applicantStatus NVARCHAR(50) DEFAULT 'Active',
                jobTitle NVARCHAR(255),
                ownership NVARCHAR(100),
                workAuthorization NVARCHAR(100),
                source NVARCHAR(100),
                createdBy NVARCHAR(255),
                createdOn DATETIME DEFAULT GETDATE(),
                modifiedOn DATETIME,
                techSkills NVARCHAR(MAX),
                resumeText NVARCHAR(MAX),
                blobUrl NVARCHAR(MAX)
            )
            """
            try:
                cursor.execute(create_table_sql)
                self.conn.commit()
            except Exception as e:
                print(f"Warning: Could not create tables: {e}", flush=True)

        print("Database tables ready", flush=True)

    def _placeholder(self):
        return "%s" if not self.use_sqlite else "?"

    def insert_applicant(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()
        applicant_id = data.get('applicantId', '')
        p = self._placeholder()

        insert_sql = f"""
        INSERT INTO Applicants (
            applicationId, applicantName, emailAddress, mobileNumber,
            city, state, applicantStatus, jobTitle, ownership,
            workAuthorization, source, createdBy,
            techSkills, resumeText, blobUrl
        ) VALUES ({p},{p},{p},{p},{p},{p},{p},{p},{p},{p},{p},{p},{p},{p},{p})
        """

        values = (
            applicant_id,
            data.get('applicantName', ''),
            data.get('emailAddress', ''),
            data.get('mobileNumber', ''),
            data.get('city', ''),
            data.get('state', ''),
            data.get('applicantStatus', 'Active'),
            data.get('jobTitle', ''),
            data.get('ownership', 'Internal'),
            data.get('workAuthorization', ''),
            data.get('source', 'Resume Upload'),
            data.get('createdBy', 'System'),
            data.get('techSkills', 'Not Specified'),
            data.get('resumeText', ''),
            data.get('blobUrl', '')
        )

        try:
            cursor.execute(insert_sql, values)
            self.conn.commit()
            return {
                'applicantId': applicant_id,
                'applicantName': data.get('applicantName', ''),
                'message': 'Applicant added successfully'
            }
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error inserting applicant: {str(e)}")

    def search_applicants(self, filters: Dict[str, str]) -> List[Dict[str, Any]]:
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()
        p = self._placeholder()

        query = "SELECT DISTINCT * FROM Applicants WHERE 1=1"
        params = []

        if filters.get('createdBy'):
            created_by = filters['createdBy'].strip()
            if created_by:
                query += f" AND createdBy = {p}"
                params.append(created_by)

        if filters.get('keywords'):
            keywords = filters['keywords'].strip()
            if keywords:
                keyword_list = keywords.split()
                search_conditions = []
                for keyword in keyword_list:
                    keyword_pattern = f"%{keyword.lower()}%"
                    search_conditions.append(
                        f"(LOWER(applicantName) LIKE {p} OR LOWER(emailAddress) LIKE {p} OR LOWER(jobTitle) LIKE {p} OR LOWER(techSkills) LIKE {p} OR LOWER(resumeText) LIKE {p})"
                    )
                    params.extend([keyword_pattern] * 5)
                if search_conditions:
                    query += " AND (" + " OR ".join(search_conditions) + ")"

        if filters.get('jobTitle'):
            jobTitle = filters['jobTitle'].strip()
            if jobTitle:
                query += f" AND LOWER(jobTitle) LIKE {p}"
                params.append(f"%{jobTitle.lower()}%")

        if filters.get('city'):
            city = filters['city'].strip()
            if city:
                query += f" AND LOWER(city) LIKE {p}"
                params.append(f"%{city.lower()}%")

        if filters.get('state') and filters['state'] != 'United States':
            state = filters['state'].strip()
            if state:
                query += f" AND state = {p}"
                params.append(state)

        if self.use_sqlite:
            query += " ORDER BY createdOn DESC LIMIT 1000"
        else:
            query = query.replace("SELECT DISTINCT *", "SELECT DISTINCT TOP 1000 *")
            query += " ORDER BY createdOn DESC"

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in rows:
                if self.use_sqlite:
                    results.append(dict(row))
                else:
                    results.append(dict(zip(columns, row)))
            return results
        except Exception as e:
            raise Exception(f"Error searching applicants: {str(e)}")

    def get_all_applicants(self, skip: int = 0, limit: int = 100, created_by: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()
        p = self._placeholder()

        if self.use_sqlite:
            if created_by:
                query = f"SELECT DISTINCT * FROM Applicants WHERE createdBy = {p} ORDER BY createdOn DESC LIMIT {p} OFFSET {p}"
                params = (created_by, limit, skip)
            else:
                query = f"SELECT DISTINCT * FROM Applicants ORDER BY createdOn DESC LIMIT {p} OFFSET {p}"
                params = (limit, skip)
        else:
            if created_by:
                query = f"SELECT DISTINCT * FROM Applicants WHERE createdBy = {p} ORDER BY createdOn DESC OFFSET {p} ROWS FETCH NEXT {p} ROWS ONLY"
                params = (created_by, skip, limit)
            else:
                query = f"SELECT DISTINCT * FROM Applicants ORDER BY createdOn DESC OFFSET {p} ROWS FETCH NEXT {p} ROWS ONLY"
                params = (skip, limit)

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in rows:
                if self.use_sqlite:
                    results.append(dict(row))
                else:
                    results.append(dict(zip(columns, row)))
            return results
        except Exception as e:
            raise Exception(f"Error fetching applicants: {str(e)}")

    def get_applicant(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()
        p = self._placeholder()
        query = f"SELECT * FROM Applicants WHERE applicationId = {p}"

        try:
            cursor.execute(query, (applicant_id,))
            row = cursor.fetchone()
            if not row:
                return None
            columns = [desc[0] for desc in cursor.description]
            if self.use_sqlite:
                return dict(row)
            return dict(zip(columns, row))
        except Exception as e:
            raise Exception(f"Error fetching applicant: {str(e)}")

    def update_applicant(self, applicant_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()
        p = self._placeholder()

        check_query = f"SELECT * FROM Applicants WHERE applicationId = {p}"
        cursor.execute(check_query, (applicant_id,))
        if not cursor.fetchone():
            return None

        update_fields = []
        params = []

        for key, value in data.items():
            if key not in ['applicationId', 'createdOn', 'createdBy']:
                update_fields.append(f"{key} = {p}")
                params.append(value)

        if not update_fields:
            return self.get_applicant(applicant_id)

        update_fields.append(f"modifiedOn = {p}")
        params.append(datetime.now().isoformat())
        params.append(applicant_id)

        update_query = f"UPDATE Applicants SET {', '.join(update_fields)} WHERE applicationId = {p}"

        try:
            cursor.execute(update_query, params)
            self.conn.commit()
            return self.get_applicant(applicant_id)
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error updating applicant: {str(e)}")

    def delete_applicant(self, applicant_id: str) -> bool:
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()
        p = self._placeholder()

        check_query = f"SELECT * FROM Applicants WHERE applicationId = {p}"
        cursor.execute(check_query, (applicant_id,))
        if not cursor.fetchone():
            return False

        delete_query = f"DELETE FROM Applicants WHERE applicationId = {p}"

        try:
            cursor.execute(delete_query, (applicant_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error deleting applicant: {str(e)}")

    def delete_all_applicants(self) -> int:
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM Applicants")
            count = cursor.fetchone()[0]
            cursor.execute("DELETE FROM Applicants")
            self.conn.commit()
            return count
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error deleting all applicants: {str(e)}")

    def close(self):
        if self.conn:
            self.conn.close()
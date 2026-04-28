"""
Database Module
Handles all database operations for applicant data
"""
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

try:
    import pyodbc
except ImportError:
    pyodbc = None


class Database:
    """
    Database handler for applicant data
    Supports Azure SQL Database and local SQLite for testing
    """
    
    def __init__(self):
        """Initialize database connection"""
        # Try to use Azure SQL, fallback to SQLite
        self.connection_string = os.getenv(
            'DB_CONNECTION_STRING',
            'sqlite:///applicants.db'
        )
        
        self.use_sqlite = self.connection_string.startswith('sqlite')
        
        if self.use_sqlite:
            import sqlite3
            self.sqlite3 = sqlite3
            self.conn = None
            self._connect_sqlite()
        else:
            self.conn = None
            if pyodbc:
                self._connect_azure()

    def _connect_sqlite(self):
        """Connect to SQLite database"""
        db_path = self.connection_string.replace('sqlite:///', '')
        self.conn = self.sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = self.sqlite3.Row

    def _connect_azure(self):
        """Connect to Azure SQL Database"""
        try:
            self.conn = pyodbc.connect(self.connection_string)
        except Exception as e:
            print(f"Warning: Could not connect to Azure SQL: {e}")
            print("Falling back to SQLite...")
            self._connect_sqlite()

    def _ensure_column(self, cursor, table_name: str, column_definition: str):
        """Ensure a specific column exists in the table"""
        if self.use_sqlite:
            # SQLite has limited ALTER TABLE support, so only add if missing
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
        """Create database schema"""
        if not self.conn:
            return

        cursor = self.conn.cursor()

        # Create Applicants table based on provided column names
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
            print("Database tables created successfully")
        except Exception as e:
            print(f"Warning: Could not create tables: {e}")
            # Tables might already exist
            pass

        # Ensure any new columns are present for previously created databases
        self._ensure_column(cursor, 'Applicants', 'techSkills TEXT')
        self._ensure_column(cursor, 'Applicants', 'resumeText TEXT')
        self._ensure_column(cursor, 'Applicants', 'blobUrl TEXT')
        self.conn.commit()

    def insert_applicant(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert new applicant record"""
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()

        # Map incoming data to database columns
        applicant_id = data.get('applicantId', '')
        
        insert_sql = """
        INSERT INTO Applicants (
            applicationId, applicantName, emailAddress, mobileNumber,
            city, state, applicantStatus, jobTitle, ownership, 
            workAuthorization, source, createdBy, createdOn,
            techSkills, resumeText, blobUrl
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            datetime.now().isoformat(),
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
        """
        Search applicants based on filters
        Returns all resumes containing ANY of the keywords in ANY field (no duplicates)
        Filters by createdBy (current user) if provided
        """
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()
        
        # Start with base query using DISTINCT to avoid duplicates
        query = "SELECT DISTINCT * FROM Applicants WHERE 1=1"
        params = []

        # Filter by createdBy (current user) if provided
        if filters.get('createdBy'):
            created_by = filters['createdBy'].strip()
            if created_by:
                query += " AND createdBy = ?"
                params.append(created_by)

        # Keywords search - matches if ANY keyword is found in ANY field
        if filters.get('keywords'):
            keywords = filters['keywords'].strip()
            if keywords:
                # Split by spaces to get individual keywords
                keyword_list = keywords.split()
                
                # Build search condition: each keyword can match any field
                search_conditions = []
                for keyword in keyword_list:
                    keyword_pattern = f"%{keyword.lower()}%"
                    search_conditions.append(
                        f"(LOWER(applicantName) LIKE ? OR LOWER(emailAddress) LIKE ? OR LOWER(jobTitle) LIKE ? OR LOWER(techSkills) LIKE ? OR LOWER(resumeText) LIKE ?)"
                    )
                    # Add the same pattern 5 times (once per field)
                    params.extend([keyword_pattern] * 5)
                
                # Join all keyword searches with OR (find ANY keyword)
                if search_conditions:
                    query += " AND (" + " OR ".join(search_conditions) + ")"

        # Job Title filter
        if filters.get('jobTitle'):
            jobTitle = filters['jobTitle'].strip()
            if jobTitle:
                query += " AND LOWER(jobTitle) LIKE ?"
                params.append(f"%{jobTitle.lower()}%")

        # City filter
        if filters.get('city'):
            city = filters['city'].strip()
            if city:
                query += " AND LOWER(city) LIKE ?"
                params.append(f"%{city.lower()}%")

        # State filter
        if filters.get('state') and filters['state'] != 'United States':
            state = filters['state'].strip()
            if state:
                query += " AND state = ?"
                params.append(state)

        query += " ORDER BY createdOn DESC LIMIT 1000"

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            if self.use_sqlite:
                for row in rows:
                    results.append(dict(row))
            else:
                # For pyodbc
                columns = [desc[0] for desc in cursor.description]
                for row in rows:
                    results.append(dict(zip(columns, row)))
            
            return results
        except Exception as e:
            raise Exception(f"Error searching applicants: {str(e)}")

    def get_all_applicants(self, skip: int = 0, limit: int = 100, created_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all applicants with pagination (no duplicates)
        Optionally filter by createdBy (current user)
        """
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()

        if created_by:
            query = f"""
            SELECT DISTINCT * FROM Applicants
            WHERE createdBy = ?
            ORDER BY createdOn DESC
            LIMIT ? OFFSET ?
            """
            params = (created_by, limit, skip)
        else:
            query = f"""
            SELECT DISTINCT * FROM Applicants
            ORDER BY createdOn DESC
            LIMIT ? OFFSET ?
            """
            params = (limit, skip)

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            if self.use_sqlite:
                for row in rows:
                    results.append(dict(row))
            else:
                columns = [desc[0] for desc in cursor.description]
                for row in rows:
                    results.append(dict(zip(columns, row)))
            
            return results
        except Exception as e:
            raise Exception(f"Error fetching applicants: {str(e)}")

    def get_applicant(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """Get specific applicant by ID"""
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()

        query = "SELECT * FROM Applicants WHERE applicationId = ?"

        try:
            cursor.execute(query, (applicant_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            if self.use_sqlite:
                return dict(row)
            else:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
        except Exception as e:
            raise Exception(f"Error fetching applicant: {str(e)}")

    def update_applicant(self, applicant_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update applicant record"""
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()

        # Check if applicant exists
        check_query = "SELECT * FROM Applicants WHERE applicationId = ?"
        cursor.execute(check_query, (applicant_id,))
        if not cursor.fetchone():
            return None

        # Build update query
        update_fields = []
        params = []

        for key, value in data.items():
            if key not in ['applicationId', 'createdOn', 'createdBy']:
                update_fields.append(f"{key} = ?")
                params.append(value)

        if not update_fields:
            return self.get_applicant(applicant_id)

        update_fields.append("modifiedOn = ?")
        params.append(datetime.now().isoformat())
        params.append(applicant_id)

        update_query = f"UPDATE Applicants SET {', '.join(update_fields)} WHERE applicationId = ?"

        try:
            cursor.execute(update_query, params)
            self.conn.commit()
            return self.get_applicant(applicant_id)
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error updating applicant: {str(e)}")

    def delete_applicant(self, applicant_id: str) -> bool:
        """Delete applicant record"""
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()

        # Check if applicant exists
        check_query = "SELECT * FROM Applicants WHERE applicationId = ?"
        cursor.execute(check_query, (applicant_id,))
        if not cursor.fetchone():
            return False

        delete_query = "DELETE FROM Applicants WHERE applicationId = ?"

        try:
            cursor.execute(delete_query, (applicant_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error deleting applicant: {str(e)}")

    def delete_all_applicants(self) -> int:
        """Delete all applicant records from database
        Returns the number of records deleted
        """
        if not self.conn:
            raise Exception("Database not connected")

        cursor = self.conn.cursor()
        
        try:
            # Get count of records before deletion
            cursor.execute("SELECT COUNT(*) FROM Applicants")
            if self.use_sqlite:
                count = cursor.fetchone()[0]
            else:
                count = cursor.fetchone()[0]
            
            # Delete all records
            cursor.execute("DELETE FROM Applicants")
            self.conn.commit()
            return count
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error deleting all applicants: {str(e)}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

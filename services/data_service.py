"""
Data service for managing database operations.
"""
# Korrigierte Importe für services/data_service.py
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import sqlite3
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
import threading
import queue
import logging
from dataclasses import asdict

from models.project import Project
from models.position import Position
from models.aufmass_item import AufmassItem
from models.profile import Profile, STANDARD_PROFILES
from models.position_template import PositionTemplate, STANDARD_TEMPLATES
from utils.logger import get_logger

logger = get_logger(__name__)


class DataService:
    """Service for handling database operations and data processing."""
    
    def __init__(self, db_path: str = "aufmass.db"):
        """Initialize the data service with database connection."""
        self.db_path = db_path
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        self._profile_cache = {}  # Memory cache for profiles
        self._template_cache = {}  # Memory cache for position templates
        self._create_tables()
        self._init_standard_profiles()
        self._init_standard_templates()
        logger.info(f"DataService initialized with database: {db_path}")
    
    def _worker(self) -> None:
        """Background worker thread for processing database operations."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        while True:
            try:
                task, args, kwargs, result_id = self.task_queue.get()
                if task == "shutdown":
                    break
                    
                result = task(conn, *args, **kwargs)
                self.result_queue.put((result_id, result))
                self.task_queue.task_done()
            except Exception as e:
                logger.error(f"Database operation error: {e}")
                self.result_queue.put((result_id, None))
                self.task_queue.task_done()
        
        conn.close()
    
    def _execute_task(self, task, *args, **kwargs):
        """Execute a task on the worker thread and wait for result."""
        result_id = id(task)
        self.task_queue.put((task, args, kwargs, result_id))
        
        # Wait for the result
        while True:
            task_result_id, result = self.result_queue.get()
            if task_result_id == result_id:
                self.result_queue.task_done()
                return result
            self.result_queue.put((task_result_id, result))
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        def _task(conn):
            cursor = conn.cursor()
            
            # Create projects table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                city TEXT,
                postal_code TEXT,
                status TEXT DEFAULT 'Ausstehend',
                profile_system TEXT,
                contact_person TEXT,
                installation_date TEXT,
                measurement_date TEXT,
                field_service_employee TEXT,
                color TEXT,
                icon TEXT,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            ''')
            
            # Create positions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                project_id INTEGER,
                template_code TEXT,
                name TEXT NOT NULL,
                floor TEXT,
                existing_window_type TEXT,
                roller_shutter_type TEXT,
                notes TEXT,
                product TEXT,
                product_id INTEGER,
                product_type TEXT DEFAULT '',
                product_ids TEXT DEFAULT '[]',
                is_main_position INTEGER DEFAULT 1,
                parent_id TEXT,
                color TEXT,
                status TEXT DEFAULT 'Ausstehend',
                accessories TEXT,
                has_measurement_data INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
            ''')
            
            # Create measurements table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id TEXT,
                project_id INTEGER,
                inner_width INTEGER DEFAULT 0,
                inner_height INTEGER DEFAULT 0,
                outer_width INTEGER DEFAULT 0,
                outer_height INTEGER DEFAULT 0,
                diagonal INTEGER DEFAULT 0,
                special_notes TEXT,
                photos TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (position_id) REFERENCES positions (id),
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
            ''')
            
            # Create profiles table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id TEXT PRIMARY KEY,
                system_code TEXT NOT NULL,
                profile_type_code TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                depth_mm REAL NOT NULL,
                view_width_mm REAL NOT NULL,
                rebate_height_mm REAL NOT NULL,
                wall_thickness_mm REAL NOT NULL,
                chamber_count INTEGER NOT NULL,
                glazing_thickness_max REAL NOT NULL,
                uf_value REAL NOT NULL,
                psi_value REAL,
                test_standard TEXT,
                svg_path TEXT,
                section_drawing_path TEXT,
                reinforcement_possible INTEGER DEFAULT 1,
                standard_colors TEXT,
                surface_textures TEXT,
                max_sash_weight_kg REAL,
                max_element_height_mm REAL,
                max_element_width_mm REAL,
                seal_count INTEGER DEFAULT 2,
                seal_type TEXT DEFAULT 'EPDM',
                is_active INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            ''')
            
            # Create position templates table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS position_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                w_mm INTEGER DEFAULT 0,
                h_mm INTEGER DEFAULT 0,
                default_product_type TEXT,
                is_active INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
            ''')
            
            # Add migration for existing databases with safer column checking
            def _column_exists(table, column):
                cursor.execute(f"PRAGMA table_info({table});")
                return any(row[1] == column for row in cursor.fetchall())
            
            # Add product_type column if it doesn't exist
            if not _column_exists("positions", "product_type"):
                try:
                    cursor.execute("ALTER TABLE positions ADD COLUMN product_type TEXT DEFAULT ''")
                    logger.info("Added product_type column to existing positions table")
                except sqlite3.OperationalError as e:
                    logger.warning(f"Failed to add product_type column: {e}")
            
            # Add product_ids column if it doesn't exist
            if not _column_exists("positions", "product_ids"):
                try:
                    cursor.execute("ALTER TABLE positions ADD COLUMN product_ids TEXT DEFAULT '[]'")
                    logger.info("Added product_ids column to existing positions table")
                except sqlite3.OperationalError as e:
                    logger.warning(f"Failed to add product_ids column: {e}")
            
            # Add template_code column if it doesn't exist
            if not _column_exists("positions", "template_code"):
                try:
                    cursor.execute("ALTER TABLE positions ADD COLUMN template_code TEXT DEFAULT ''")
                    logger.info("Added template_code column to existing positions table")
                except sqlite3.OperationalError as e:
                    logger.warning(f"Failed to add template_code column: {e}")
            
            # Add product_id column if it doesn't exist
            if not _column_exists("positions", "product_id"):
                try:
                    cursor.execute("ALTER TABLE positions ADD COLUMN product_id INTEGER")
                    logger.info("Added product_id column to existing positions table")
                except sqlite3.OperationalError as e:
                    logger.warning(f"Failed to add product_id column: {e}")
            
            # Add extended measurement fields to measurements table
            extended_measurement_fields = [
                ("sill_height", "REAL DEFAULT 0"),
                ("frame_depth", "REAL DEFAULT 70"),
                ("mullion_offset", "REAL DEFAULT 50"),
                ("transom_offset", "REAL DEFAULT 50"),
                ("glazing_thickness", "REAL DEFAULT 24"),
                ("reveal_left", "REAL DEFAULT 0"),
                ("reveal_right", "REAL DEFAULT 0"),
                ("reveal_top", "REAL DEFAULT 0"),
                ("reveal_bottom", "REAL DEFAULT 0"),
                ("area", "REAL DEFAULT 0"),
                ("perimeter", "REAL DEFAULT 0")
            ]
            
            for field_name, field_type in extended_measurement_fields:
                if not _column_exists("measurements", field_name):
                    try:
                        cursor.execute(f"ALTER TABLE measurements ADD COLUMN {field_name} {field_type}")
                        logger.info(f"Added {field_name} column to measurements table")
                    except sqlite3.OperationalError as e:
                        logger.warning(f"Failed to add {field_name} column: {e}")
            
            # Remove deprecated columns
            try:
                # Create new table without w_mm and h_mm
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions_new (
                    id TEXT PRIMARY KEY,
                    project_id INTEGER,
                    template_code TEXT,
                    name TEXT NOT NULL,
                    floor TEXT,
                    existing_window_type TEXT,
                    roller_shutter_type TEXT,
                    notes TEXT,
                    product TEXT,
                    product_id INTEGER,
                    product_type TEXT DEFAULT '',
                    product_ids TEXT DEFAULT '[]',
                    is_main_position INTEGER DEFAULT 1,
                    parent_id TEXT,
                    color TEXT,
                    status TEXT DEFAULT 'Ausstehend',
                    accessories TEXT,
                    has_measurement_data INTEGER DEFAULT 0,
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
                ''')
                
                # Copy data excluding w_mm and h_mm
                cursor.execute('''
                INSERT OR IGNORE INTO positions_new 
                SELECT id, project_id, template_code, name, floor, existing_window_type,
                       roller_shutter_type, notes, product, product_id, 
                       COALESCE(product_type, '') as product_type,
                       COALESCE(product_ids, '[]') as product_ids,
                       is_main_position, parent_id, color, status, accessories,
                       has_measurement_data, created_at, updated_at
                FROM positions
                ''')
                
                # Replace old table
                cursor.execute("DROP TABLE positions")
                cursor.execute("ALTER TABLE positions_new RENAME TO positions")
                logger.info("Migrated positions table to remove w_mm/h_mm columns")
            except sqlite3.Error as e:
                logger.warning(f"Failed to migrate positions table: {e}")
                pass
            
            conn.commit()
            return True
        
        self._execute_task(_task)
        logger.info("Database tables created or confirmed to exist")
    
    # Project operations
    def save_project(self, project: Project) -> int:
        """Save a project to the database."""
        def _task(conn, project):
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            if project.id == 0:  # New project
                cursor.execute('''
                INSERT INTO projects (
                    name, address, city, postal_code, status, profile_system,
                    contact_person, installation_date, measurement_date,
                    field_service_employee, color, icon, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    project.name, project.address, project.city, project.postal_code,
                    project.status, project.profile_system, project.contact_person, 
                    project.installation_date.isoformat() if project.installation_date else None,
                    project.measurement_date.isoformat() if project.measurement_date else None,
                    project.field_service_employee, project.color, project.icon,
                    project.notes, now, now
                ))
                project_id = cursor.lastrowid
            else:  # Update existing project
                cursor.execute('''
                UPDATE projects SET
                    name = ?, address = ?, city = ?, postal_code = ?, status = ?,
                    profile_system = ?, contact_person = ?, installation_date = ?,
                    measurement_date = ?, field_service_employee = ?, color = ?, 
                    icon = ?, notes = ?, updated_at = ?
                WHERE id = ?
                ''', (
                    project.name, project.address, project.city, project.postal_code,
                    project.status, project.profile_system, project.contact_person,
                    project.installation_date.isoformat() if project.installation_date else None,
                    project.measurement_date.isoformat() if project.measurement_date else None,
                    project.field_service_employee, project.color, project.icon,
                    project.notes, now, project.id
                ))
                project_id = project.id
            
            conn.commit()
            return project_id
        
        project_id = self._execute_task(_task, project)
        logger.info(f"Saved project with ID: {project_id}")
        return project_id
    
    
    def get_projects(self) -> List[Project]:
        """Get all projects from the database."""
        def _task(conn):
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM projects ORDER BY updated_at DESC')
            rows = cursor.fetchall()
            
            projects = []
            for row in rows:
                project = Project(
                    id=row['id'],
                    name=row['name'],
                    address=row['address'],
                    city=row['city'],
                    postal_code=row['postal_code'],
                    status=row['status'],
                    profile_system=row['profile_system'],
                    contact_person=row['contact_person'],
                    installation_date=datetime.fromisoformat(row['installation_date']) if row['installation_date'] else None,
                    measurement_date=datetime.fromisoformat(row['measurement_date']) if row['measurement_date'] else None,
                    field_service_employee=row['field_service_employee'],
                    color=row['color'],
                    icon=row['icon'],
                    notes=row['notes'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                )
                projects.append(project)
                
            return projects
        
        projects = self._execute_task(_task)
        logger.info(f"Retrieved {len(projects)} projects")
        return projects
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a single project by ID."""
        def _task(conn, project_id):
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
            row = cursor.fetchone()
            
            if row:
                return Project(
                    id=row['id'],
                    name=row['name'],
                    address=row['address'],
                    city=row['city'],
                    postal_code=row['postal_code'],
                    status=row['status'],
                    profile_system=row['profile_system'],
                    contact_person=row['contact_person'],
                    installation_date=datetime.fromisoformat(row['installation_date']) if row['installation_date'] else None,
                    measurement_date=datetime.fromisoformat(row['measurement_date']) if row['measurement_date'] else None,
                    field_service_employee=row['field_service_employee'],
                    color=row['color'],
                    icon=row['icon'],
                    notes=row['notes'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                )
            return None
        
        project = self._execute_task(_task, project_id)
        if project:
            logger.info(f"Retrieved project with ID: {project_id}")
        else:
            logger.warning(f"Project with ID {project_id} not found")
        return project
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all related positions and measurements."""
        def _task(conn, project_id):
            cursor = conn.cursor()
            
            # Get all positions for this project
            cursor.execute('SELECT id FROM positions WHERE project_id = ?', (project_id,))
            position_ids = [row['id'] for row in cursor.fetchall()]
            
            # Delete measurements for all positions
            for position_id in position_ids:
                cursor.execute('DELETE FROM measurements WHERE position_id = ?', (position_id,))
            
            # Delete positions
            cursor.execute('DELETE FROM positions WHERE project_id = ?', (project_id,))
            
            # Delete project
            cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        
        success = self._execute_task(_task, project_id)
        if success:
            logger.info(f"Deleted project with ID: {project_id}")
        else:
            logger.warning(f"Failed to delete project with ID: {project_id}")
        return success
    
    # Position operations
    def save_position(self, position: Position) -> str:
        """Save a position to the database."""
        def _task(conn, position):
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            # Convert accessories list to JSON string
            accessories_json = json.dumps(position.accessories)
            
            # Check if position already exists
            cursor.execute('SELECT id FROM positions WHERE id = ?', (position.id,))
            exists = cursor.fetchone() is not None
            
            if not exists:  # New position
                cursor.execute('''
                INSERT INTO positions (
                    id, project_id, template_code, name, floor, existing_window_type, 
                    roller_shutter_type, notes, product, product_id, product_type, 
                    product_ids, is_main_position, parent_id, color, status, accessories, 
                    has_measurement_data, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    position.id, position.project_id, position.template_code, 
                    position.name, position.floor, position.existing_window_type, 
                    position.roller_shutter_type, position.notes, position.product,
                    position.product_id, position.product_type, json.dumps(position.product_ids),
                    1 if position.is_main_position else 0,
                    position.parent_id, position.color, position.status,
                    accessories_json, 1 if position.has_measurement_data else 0,
                    now, now
                ))
            else:  # Update existing position
                cursor.execute('''
                UPDATE positions SET
                    project_id = ?, template_code = ?, name = ?, floor = ?, 
                    existing_window_type = ?, roller_shutter_type = ?, notes = ?, 
                    product = ?, product_id = ?, product_type = ?, product_ids = ?,
                    is_main_position = ?, parent_id = ?, color = ?, status = ?,
                    accessories = ?, has_measurement_data = ?, updated_at = ?
                WHERE id = ?
                ''', (
                    position.project_id, position.template_code, position.name, 
                    position.floor, position.existing_window_type, 
                    position.roller_shutter_type, position.notes, position.product,
                    position.product_id, position.product_type, json.dumps(position.product_ids),
                    1 if position.is_main_position else 0,
                    position.parent_id, position.color, position.status,
                    accessories_json, 1 if position.has_measurement_data else 0,
                    now, position.id
                ))
            
            conn.commit()
            return position.id
        
        position_id = self._execute_task(_task, position)
        logger.info(f"Saved position with ID: {position_id}")
        return position_id
    
    def get_positions(self, project_id: int) -> List[Position]:
        """Get all positions for a specific project."""
        def _task(conn, project_id):
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM positions WHERE project_id = ? ORDER BY id', (project_id,))
            rows = cursor.fetchall()
            
            positions = []
            for row in rows:
                # Parse accessories from JSON
                accessories = json.loads(row['accessories']) if row['accessories'] else []
                
                # Parse product_ids from JSON
                product_ids_str = row['product_ids'] if 'product_ids' in row.keys() else '[]'
                try:
                    product_ids = json.loads(product_ids_str) if product_ids_str else []
                except json.JSONDecodeError:
                    product_ids = []
                
                position = Position(
                    id=row['id'],
                    project_id=row['project_id'],
                    template_code=row['template_code'] if 'template_code' in row.keys() else '',
                    name=row['name'],
                    floor=row['floor'],
                    existing_window_type=row['existing_window_type'],
                    roller_shutter_type=row['roller_shutter_type'],
                    notes=row['notes'],
                    product=row['product'],
                    product_id=row['product_id'] if 'product_id' in row.keys() else None,
                    product_type=row['product_type'] if 'product_type' in row.keys() else '',
                    product_ids=product_ids,
                    is_main_position=bool(row['is_main_position']),
                    parent_id=row['parent_id'],
                    color=row['color'],
                    status=row['status'],
                    accessories=accessories,
                    has_measurement_data=bool(row['has_measurement_data']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                positions.append(position)
            
            return positions
        
        positions = self._execute_task(_task, project_id)
        logger.info(f"Retrieved {len(positions)} positions for project {project_id}")
        return positions
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """Get a specific position by ID."""
        def _task(conn, position_id):
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM positions WHERE id = ?', (position_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Parse accessories from JSON
            accessories = json.loads(row['accessories']) if row['accessories'] else []
            
            # Parse product_ids from JSON
            product_ids_str = row['product_ids'] if 'product_ids' in row.keys() else '[]'
            try:
                product_ids = json.loads(product_ids_str) if product_ids_str else []
            except json.JSONDecodeError:
                product_ids = []
            
            position = Position(
                id=row['id'],
                project_id=row['project_id'],
                template_code=row['template_code'] if 'template_code' in row.keys() else '',
                name=row['name'],
                floor=row['floor'],
                existing_window_type=row['existing_window_type'],
                roller_shutter_type=row['roller_shutter_type'],
                notes=row['notes'],
                product=row['product'],
                product_id=row['product_id'] if 'product_id' in row.keys() else None,
                product_type=row['product_type'] if 'product_type' in row.keys() else '',
                product_ids=product_ids,
                is_main_position=bool(row['is_main_position']),
                parent_id=row['parent_id'],
                color=row['color'],
                status=row['status'],
                accessories=accessories,
                has_measurement_data=bool(row['has_measurement_data']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
            
            return position
        
        position = self._execute_task(_task, position_id)
        if position:
            logger.info(f"Retrieved position with ID: {position_id}")
        else:
            logger.warning(f"Position with ID {position_id} not found")
        return position
    
    def delete_position(self, position_id: str) -> bool:
        """Delete a position and its measurements."""
        def _task(conn, position_id):
            cursor = conn.cursor()
            
            # Check if it's a main position with sub-positions
            cursor.execute('SELECT is_main_position FROM positions WHERE id = ?', (position_id,))
            row = cursor.fetchone()
            
            if row and row['is_main_position']:
                # Delete sub-positions and their measurements
                cursor.execute('SELECT id FROM positions WHERE parent_id = ?', (position_id,))
                sub_position_ids = [row['id'] for row in cursor.fetchall()]
                
                for sub_id in sub_position_ids:
                    cursor.execute('DELETE FROM measurements WHERE position_id = ?', (sub_id,))
                    cursor.execute('DELETE FROM positions WHERE id = ?', (sub_id,))
            
            # Delete measurements for this position
            cursor.execute('DELETE FROM measurements WHERE position_id = ?', (position_id,))
            
            # Delete the position
            cursor.execute('DELETE FROM positions WHERE id = ?', (position_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        
        success = self._execute_task(_task, position_id)
        if success:
            logger.info(f"Deleted position with ID: {position_id}")
        else:
            logger.warning(f"Failed to delete position with ID: {position_id}")
        return success
    
    # Measurement operations
    def save_measurement(self, measurement: AufmassItem) -> int:
        """Save measurement data for a position."""
        def _task(conn, measurement):
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            # Convert photos list to JSON
            photos_json = json.dumps(measurement.photos)
            
            if measurement.id == 0:  # New measurement
                cursor.execute('''
                INSERT INTO measurements (
                    position_id, project_id, inner_width, inner_height, 
                    outer_width, outer_height, diagonal, special_notes,
                    photos, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    measurement.position_id, measurement.project_id,
                    measurement.inner_width, measurement.inner_height,
                    measurement.outer_width, measurement.outer_height,
                    measurement.diagonal, measurement.special_notes,
                    photos_json, now, now
                ))
                measurement_id = cursor.lastrowid
                
                # Update position to indicate it has measurement data
                cursor.execute('''
                UPDATE positions SET has_measurement_data = 1 WHERE id = ?
                ''', (measurement.position_id,))
            else:  # Update existing measurement
                cursor.execute('''
                UPDATE measurements SET
                    inner_width = ?, inner_height = ?, outer_width = ?,
                    outer_height = ?, diagonal = ?, special_notes = ?,
                    photos = ?, updated_at = ?
                WHERE id = ?
                ''', (
                    measurement.inner_width, measurement.inner_height,
                    measurement.outer_width, measurement.outer_height,
                    measurement.diagonal, measurement.special_notes,
                    photos_json, now, measurement.id
                ))
                measurement_id = measurement.id
            
            conn.commit()
            return measurement_id
        
        measurement_id = self._execute_task(_task, measurement)
        logger.info(f"Saved measurement with ID: {measurement_id}")
        return measurement_id
    
    def get_measurement(self, position_id: str) -> Optional[AufmassItem]:
        """Get measurement data for a specific position."""
        def _task(conn, position_id):
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM measurements WHERE position_id = ?', (position_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Parse photos from JSON
            photos = json.loads(row['photos']) if row['photos'] else []
            
            data_dict = {
                'id': row['id'],
                'position_id': row['position_id'],
                'project_id': row['project_id'],
                'inner_width': row['inner_width'],
                'inner_height': row['inner_height'],
                'outer_width': row['outer_width'],
                'outer_height': row['outer_height'],
                'diagonal': row['diagonal'],
                'special_notes': row['special_notes'],
                'photos': photos,
                'created_at': datetime.fromisoformat(row['created_at']),
                'updated_at': datetime.fromisoformat(row['updated_at'])
            }

            measurement = AufmassItem.from_dict(data_dict)
            
            return measurement
        
        measurement = self._execute_task(_task, position_id)
        if measurement:
            logger.info(f"Retrieved measurement for position: {position_id}")
        else:
            logger.info(f"No measurement found for position: {position_id}")
        return measurement
    
    # Profile operations
    def _init_standard_profiles(self) -> None:
        """Initialize standard VEKA profiles in database."""
        existing_profiles = self.get_profiles()
        existing_ids = {p.id for p in existing_profiles}
        
        for profile in STANDARD_PROFILES:
            if profile.id not in existing_ids:
                self.save_profile(profile)
        
        logger.info(f"Initialized {len(STANDARD_PROFILES)} standard profiles")
    
    def save_profile(self, profile: Profile) -> str:
        """Save a profile to the database."""
        def _task(conn, profile):
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            profile_data = profile.to_dict()
            profile_data['created_at'] = now
            profile_data['updated_at'] = now
            
            # Check if profile exists
            cursor.execute('SELECT id FROM profiles WHERE id = ?', (profile.id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing profile
                update_fields = ', '.join([f'{k} = ?' for k in profile_data.keys() if k != 'id'])
                values = [v for k, v in profile_data.items() if k != 'id'] + [profile.id]
                cursor.execute(f'UPDATE profiles SET {update_fields} WHERE id = ?', values)
            else:
                # Insert new profile
                placeholders = ', '.join(['?' for _ in profile_data])
                fields = ', '.join(profile_data.keys())
                cursor.execute(f'INSERT INTO profiles ({fields}) VALUES ({placeholders})', 
                             list(profile_data.values()))
            
            conn.commit()
            return profile.id
        
        profile_id = self._execute_task(_task, profile)
        # Update cache
        self._profile_cache[profile.id] = profile
        logger.info(f"Saved profile: {profile.id}")
        return profile_id
    
    def get_profile(self, profile_id: str) -> Optional[Profile]:
        """Get a profile by ID with caching."""
        # Check cache first
        if profile_id in self._profile_cache:
            return self._profile_cache[profile_id]
        
        def _task(conn, profile_id):
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM profiles WHERE id = ? AND is_active = 1', (profile_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return Profile.from_dict(dict(row))
        
        profile = self._execute_task(_task, profile_id)
        if profile:
            # Cache the result
            self._profile_cache[profile.id] = profile
            logger.info(f"Retrieved profile: {profile_id}")
        else:
            logger.warning(f"Profile not found: {profile_id}")
        return profile
    
    def get_profiles(self, system_code: Optional[str] = None, 
                    profile_type_code: Optional[str] = None,
                    active_only: bool = True) -> List[Profile]:
        """Get profiles with optional filtering."""
        def _task(conn, system_code, profile_type_code, active_only):
            cursor = conn.cursor()
            
            query = 'SELECT * FROM profiles WHERE 1=1'
            params = []
            
            if active_only:
                query += ' AND is_active = 1'
            if system_code:
                query += ' AND system_code = ?'
                params.append(system_code)
            if profile_type_code:
                query += ' AND profile_type_code = ?'
                params.append(profile_type_code)
            
            query += ' ORDER BY sort_order, name'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            profiles = []
            for row in rows:
                profile = Profile.from_dict(dict(row))
                profiles.append(profile)
                # Update cache
                self._profile_cache[profile.id] = profile
            
            return profiles
        
        profiles = self._execute_task(_task, system_code, profile_type_code, active_only)
        logger.info(f"Retrieved {len(profiles)} profiles")
        return profiles
    
    def list_profile_names(self, system_code: Optional[str] = None) -> List[str]:
        """Get list of profile display names for UI dropdowns."""
        profiles = self.get_profiles(system_code=system_code)
        return [profile.display_name for profile in profiles]
    
    def get_profiles_by_system(self, system_code: str) -> List[Profile]:
        """Get all profiles for a specific VEKA system."""
        return self.get_profiles(system_code=system_code)
    
    def clear_profile_cache(self) -> None:
        """Clear the profile memory cache."""
        self._profile_cache.clear()
        logger.info("Profile cache cleared")
    
    # Position Template operations
    def _init_standard_templates(self) -> None:
        """Initialize standard position templates in database."""
        existing_templates = self.get_position_templates()
        existing_codes = {t.code for t in existing_templates}
        
        for template in STANDARD_TEMPLATES:
            if template.code not in existing_codes:
                self.save_position_template(template)
        
        logger.info(f"Initialized {len(STANDARD_TEMPLATES)} standard position templates")
    
    def save_position_template(self, template: PositionTemplate) -> int:
        """Save a position template to the database."""
        def _task(conn, template):
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            template_data = template.to_dict()
            template_data['created_at'] = now
            template_data['updated_at'] = now
            
            # Check if template exists
            cursor.execute('SELECT id FROM position_templates WHERE code = ?', (template.code,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing template
                template_id = exists[0]
                update_fields = ', '.join([f'{k} = ?' for k in template_data.keys() if k != 'id'])
                values = [v for k, v in template_data.items() if k != 'id'] + [template_id]
                cursor.execute(f'UPDATE position_templates SET {update_fields} WHERE id = ?', values)
            else:
                # Insert new template
                placeholders = ', '.join(['?' for _ in template_data if _ != 'id'])
                fields = ', '.join(k for k in template_data.keys() if k != 'id')
                values = [v for k, v in template_data.items() if k != 'id']
                cursor.execute(f'INSERT INTO position_templates ({fields}) VALUES ({placeholders})', values)
                template_id = cursor.lastrowid
            
            conn.commit()
            return template_id
        
        template_id = self._execute_task(_task, template)
        # Update cache
        template.id = template_id
        self._template_cache[template.code] = template
        logger.info(f"Saved position template: {template.code}")
        return template_id
    
    def get_position_template(self, code: str) -> Optional[PositionTemplate]:
        """Get a position template by code with caching."""
        # Check cache first
        if code in self._template_cache:
            return self._template_cache[code]
        
        def _task(conn, code):
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM position_templates WHERE code = ? AND is_active = 1', (code,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return PositionTemplate.from_dict(dict(row))
        
        template = self._execute_task(_task, code)
        if template:
            # Cache the result
            self._template_cache[template.code] = template
            logger.info(f"Retrieved position template: {code}")
        else:
            logger.warning(f"Position template not found: {code}")
        return template
    
    def get_position_templates(self, category: Optional[str] = None, 
                              active_only: bool = True) -> List[PositionTemplate]:
        """Get position templates with optional filtering."""
        def _task(conn, category, active_only):
            cursor = conn.cursor()
            
            query = 'SELECT * FROM position_templates WHERE 1=1'
            params = []
            
            if active_only:
                query += ' AND is_active = 1'
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            query += ' ORDER BY sort_order, name'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            templates = []
            for row in rows:
                template = PositionTemplate.from_dict(dict(row))
                templates.append(template)
                # Update cache
                self._template_cache[template.code] = template
            
            return templates
        
        templates = self._execute_task(_task, category, active_only)
        logger.info(f"Retrieved {len(templates)} position templates")
        return templates
    
    def get_template_categories(self) -> List[str]:
        """Get list of template categories."""
        def _task(conn):
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT category FROM position_templates WHERE is_active = 1 ORDER BY category')
            rows = cursor.fetchall()
            return [row[0] for row in rows if row[0]]
        
        categories = self._execute_task(_task)
        logger.info(f"Retrieved {len(categories)} template categories")
        return categories
    
    def clear_template_cache(self) -> None:
        """Clear the position template memory cache."""
        self._template_cache.clear()
        logger.info("Position template cache cleared")
    
    def shutdown(self) -> None:
        """Shutdown the service and worker thread."""
        self.task_queue.put(("shutdown", [], {}, None))
        self.worker_thread.join()
        logger.info("DataService shut down")

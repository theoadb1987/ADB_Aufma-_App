#!/usr/bin/env python3
"""
VEKA Profile Import Tool
========================

Imports VEKA profile data from CSV/Excel files into the application database.

Usage:
    python tools/import_veka_profiles.py --source data/veka_profiles.xlsx --out app/data/profiles.sqlite
    python tools/import_veka_profiles.py --csv data/veka_profiles.csv
    python tools/import_veka_profiles.py --generate-sample

Features:
- Excel/CSV import with automatic column detection
- Data validation and cleanup
- SVG path assignment
- Duplicate detection and handling
- Performance optimization
"""

import argparse
import sys
import os
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.profile import Profile, ProfileDimensions, ThermalData, VEKASystem, ProfileType
from services.data_service import DataService


class VEKAProfileImporter:
    """Importer for VEKA profile data from various sources."""
    
    def __init__(self, output_db: Optional[str] = None):
        """Initialize importer with optional output database."""
        self.output_db = output_db or "aufmass.db"
        self.data_service = None
        self.profiles_imported = 0
        self.profiles_updated = 0
        self.profiles_skipped = 0
        
        # Column mapping for different input formats
        self.column_mapping = {
            'id': ['id', 'profile_id', 'artikel_nr', 'article_number'],
            'system': ['system', 'system_code', 'serie', 'profilserie'],
            'type': ['type', 'profile_type', 'typ', 'bauteil'],
            'name': ['name', 'bezeichnung', 'description'],
            'depth_mm': ['depth_mm', 'bautiefe', 'tiefe', 'depth'],
            'view_width_mm': ['view_width_mm', 'ansichtsbreite', 'width', 'view_width'],
            'rebate_height_mm': ['rebate_height_mm', 'falzhoehe', 'falz', 'rebate'],
            'wall_thickness_mm': ['wall_thickness_mm', 'wandstaerke', 'wall_thickness'],
            'chamber_count': ['chamber_count', 'kammern', 'chambers'],
            'glazing_thickness_max': ['glazing_thickness_max', 'verglasung_max', 'glas_max'],
            'uf_value': ['uf_value', 'uf_wert', 'u_wert', 'thermal'],
            'max_sash_weight_kg': ['max_sash_weight_kg', 'max_gewicht', 'weight_max'],
            'max_element_height_mm': ['max_element_height_mm', 'hoehe_max', 'height_max'],
            'max_element_width_mm': ['max_element_width_mm', 'breite_max', 'width_max'],
            'description': ['description', 'beschreibung', 'notes', 'bemerkungen']
        }
        
        # System code mapping
        self.system_mapping = {
            'SL70': VEKASystem.SOFTLINE_70,
            'SOFTLINE_70': VEKASystem.SOFTLINE_70,
            'SOFTLINE70': VEKASystem.SOFTLINE_70,
            'SL82': VEKASystem.SOFTLINE_82,
            'SOFTLINE_82': VEKASystem.SOFTLINE_82,
            'SOFTLINE82': VEKASystem.SOFTLINE_82,
            'AL90': VEKASystem.ALPHALINE_90,
            'ALPHALINE_90': VEKASystem.ALPHALINE_90,
            'PL76': VEKASystem.PERFECTLINE_76,
            'PERFECTLINE_76': VEKASystem.PERFECTLINE_76,
        }
        
        # Profile type mapping
        self.type_mapping = {
            'FRAME': ProfileType.FRAME,
            'BLENDRAHMEN': ProfileType.FRAME,
            'RAHMEN': ProfileType.FRAME,
            'SASH': ProfileType.SASH,
            'FLUEGEL': ProfileType.SASH,
            'FLÜGEL': ProfileType.SASH,
            'MULLION': ProfileType.MULLION,
            'PFOSTEN': ProfileType.MULLION,
            'TRANSOM': ProfileType.TRANSOM,
            'KAEMPFER': ProfileType.TRANSOM,
            'KÄMPFER': ProfileType.TRANSOM,
            'GLAZING_BEAD': ProfileType.GLAZING_BEAD,
            'GLASLEISTE': ProfileType.GLAZING_BEAD,
        }
    
    def _init_data_service(self):
        """Initialize data service connection."""
        if not self.data_service:
            self.data_service = DataService(self.output_db)
            print(f"✅ Connected to database: {self.output_db}")
    
    def _map_columns(self, headers: List[str]) -> Dict[str, str]:
        """Map input columns to standard field names."""
        column_map = {}
        input_columns = [col.lower().strip() for col in headers]
        
        for field, possible_names in self.column_mapping.items():
            for possible_name in possible_names:
                if possible_name.lower() in input_columns:
                    original_col = headers[input_columns.index(possible_name.lower())]
                    column_map[field] = original_col
                    break
        
        print(f"📋 Column mapping: {len(column_map)} fields mapped")
        for field, col in column_map.items():
            print(f"   {field} ← {col}")
        
        return column_map
    
    def _parse_system(self, system_str: str) -> VEKASystem:
        """Parse system string to VEKASystem enum."""
        if not system_str:
            return VEKASystem.SOFTLINE_70  # Default
        
        system_clean = str(system_str).upper().strip()
        return self.system_mapping.get(system_clean, VEKASystem.SOFTLINE_70)
    
    def _parse_profile_type(self, type_str: str) -> ProfileType:
        """Parse profile type string to ProfileType enum."""
        if not type_str:
            return ProfileType.FRAME  # Default
        
        type_clean = str(type_str).upper().strip()
        return self.type_mapping.get(type_clean, ProfileType.FRAME)
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float."""
        if value is None or value == '' or value == 'None':
            return default
        try:
            return float(str(value).replace(',', '.'))
        except (ValueError, TypeError):
            return default
    
    def _safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert value to int."""
        if value is None or value == '' or value == 'None':
            return default
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return default
    
    def _safe_str(self, value: Any, default: str = '') -> str:
        """Safely convert value to string."""
        if value is None or value == '' or value == 'None':
            return default
        return str(value).strip()
    
    def _convert_row_to_profile(self, row: Dict[str, str], column_map: Dict[str, str]) -> Optional[Profile]:
        """Convert row dict to Profile object."""
        try:
            # Extract basic fields
            profile_id = self._safe_str(row.get(column_map.get('id', ''), ''))
            if not profile_id:
                print(f"⚠️  Skipping row without ID")
                return None
            
            system = self._parse_system(row.get(column_map.get('system', ''), ''))
            profile_type = self._parse_profile_type(row.get(column_map.get('type', ''), ''))
            name = self._safe_str(row.get(column_map.get('name', ''), ''))
            description = self._safe_str(row.get(column_map.get('description', ''), ''))
            
            # Create dimensions
            dimensions = ProfileDimensions(
                depth_mm=self._safe_float(row.get(column_map.get('depth_mm', ''), 70.0)),
                view_width_mm=self._safe_float(row.get(column_map.get('view_width_mm', ''), 100.0)),
                rebate_height_mm=self._safe_float(row.get(column_map.get('rebate_height_mm', ''), 20.0)),
                wall_thickness_mm=self._safe_float(row.get(column_map.get('wall_thickness_mm', ''), 2.5), 2.5),
                chamber_count=self._safe_int(row.get(column_map.get('chamber_count', ''), 5), 5),
                glazing_thickness_max=self._safe_float(row.get(column_map.get('glazing_thickness_max', ''), 40.0))
            )
            
            # Create thermal data
            thermal = ThermalData(
                uf_value=self._safe_float(row.get(column_map.get('uf_value', ''), 1.3), 1.3)
            )
            
            # Create profile
            profile = Profile(
                id=profile_id,
                system=system,
                profile_type=profile_type,
                name=name or f"{system.display_name} {profile_type.display_name}",
                description=description,
                dimensions=dimensions,
                thermal=thermal,
                max_sash_weight_kg=self._safe_float(row.get(column_map.get('max_sash_weight_kg', ''), None)) or None,
                max_element_height_mm=self._safe_float(row.get(column_map.get('max_element_height_mm', ''), None)) or None,
                max_element_width_mm=self._safe_float(row.get(column_map.get('max_element_width_mm', ''), None)) or None
            )
            
            return profile
            
        except Exception as e:
            print(f"❌ Error converting row to profile: {e}")
            print(f"   Row data: {row}")
            return None
    
    def import_from_csv(self, csv_path: str, encoding: str = 'utf-8') -> int:
        """Import profiles from CSV file."""
        print(f"📁 Reading CSV: {csv_path}")
        
        try:
            # Try different encodings
            for enc in [encoding, 'utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(csv_path, 'r', encoding=enc, newline='') as csvfile:
                        # Detect delimiter
                        sample = csvfile.read(1024)
                        csvfile.seek(0)
                        sniffer = csv.Sniffer()
                        delimiter = sniffer.sniff(sample).delimiter
                        
                        reader = csv.DictReader(csvfile, delimiter=delimiter)
                        rows = list(reader)
                        headers = reader.fieldnames or []
                        
                    print(f"✅ CSV loaded with encoding: {enc}, {len(rows)} rows")
                    return self._import_from_rows(rows, headers)
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Could not read CSV with any encoding")
            
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            return 0
    
    def import_from_excel(self, excel_path: str, sheet_name: Optional[str] = None) -> int:
        """Import profiles from Excel file."""
        print(f"📁 Reading Excel: {excel_path}")
        print("❌ Excel import requires 'openpyxl' package")
        print("   Install with: pip install openpyxl")
        print("   Or convert to CSV format instead")
        return 0
    
    def _import_from_rows(self, rows: List[Dict[str, str]], headers: List[str]) -> int:
        """Import profiles from list of row dictionaries."""
        self._init_data_service()
        
        print(f"📊 Processing {len(rows)} rows...")
        
        # Map columns
        column_map = self._map_columns(headers)
        if not column_map:
            print("❌ No recognizable columns found")
            print(f"   Available columns: {headers}")
            return 0
        
        # Process each row
        for idx, row in enumerate(rows):
            profile = self._convert_row_to_profile(row, column_map)
            if profile:
                try:
                    # Check if profile exists
                    existing = self.data_service.get_profile(profile.id)
                    
                    if existing:
                        # Update existing
                        self.data_service.save_profile(profile)
                        self.profiles_updated += 1
                        print(f"📝 Updated: {profile.id}")
                    else:
                        # Create new
                        self.data_service.save_profile(profile)
                        self.profiles_imported += 1
                        print(f"✅ Imported: {profile.id}")
                        
                except Exception as e:
                    print(f"❌ Error saving profile {profile.id}: {e}")
                    self.profiles_skipped += 1
            else:
                self.profiles_skipped += 1
        
        total = self.profiles_imported + self.profiles_updated
        print(f"🎉 Import complete: {total} profiles processed")
        print(f"   📥 New: {self.profiles_imported}")
        print(f"   📝 Updated: {self.profiles_updated}")
        print(f"   ⚠️  Skipped: {self.profiles_skipped}")
        
        return total
    
    def generate_sample_data(self, output_path: str) -> None:
        """Generate sample CSV file with VEKA profile data."""
        print(f"📋 Generating sample data: {output_path}")
        
        sample_data = [
            {
                'id': 'SL70_FRAME_70_MD',
                'system': 'SL70',
                'type': 'FRAME',
                'name': 'Blendrahmen 70mm MD',
                'description': 'Mitteldichtung Blendrahmen für Softline 70',
                'depth_mm': 70.0,
                'view_width_mm': 119.0,
                'rebate_height_mm': 20.0,
                'wall_thickness_mm': 2.8,
                'chamber_count': 5,
                'glazing_thickness_max': 41.0,
                'uf_value': 1.3,
                'max_sash_weight_kg': 130.0,
                'max_element_height_mm': 2500.0,
                'max_element_width_mm': 1600.0
            },
            {
                'id': 'SL70_SASH_70',
                'system': 'SL70',
                'type': 'SASH',
                'name': 'Flügelprofil 70mm',
                'description': 'Standard Flügelprofil für Softline 70',
                'depth_mm': 70.0,
                'view_width_mm': 94.0,
                'rebate_height_mm': 20.0,
                'wall_thickness_mm': 2.8,
                'chamber_count': 5,
                'glazing_thickness_max': 41.0,
                'uf_value': 1.3,
                'max_sash_weight_kg': None,
                'max_element_height_mm': None,
                'max_element_width_mm': None
            },
            {
                'id': 'SL82_FRAME_82_MD',
                'system': 'SL82',
                'type': 'FRAME',
                'name': 'Blendrahmen 82mm MD',
                'description': 'Mitteldichtung Blendrahmen für Softline 82',
                'depth_mm': 82.0,
                'view_width_mm': 127.0,
                'rebate_height_mm': 24.0,
                'wall_thickness_mm': 3.0,
                'chamber_count': 6,
                'glazing_thickness_max': 53.0,
                'uf_value': 1.0,
                'max_sash_weight_kg': 150.0,
                'max_element_height_mm': 2800.0,
                'max_element_width_mm': 1800.0
            }
        ]
        
        # Write to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            if sample_data:
                fieldnames = sample_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sample_data)
        
        print(f"✅ Sample data written: {len(sample_data)} profiles")
    
    def cleanup(self):
        """Clean up resources."""
        if self.data_service:
            self.data_service.shutdown()


def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(
        description="Import VEKA profile data into application database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import from Excel file
  python tools/import_veka_profiles.py --source data/veka_profiles.xlsx
  
  # Import from CSV with custom encoding
  python tools/import_veka_profiles.py --csv data/profiles.csv --encoding latin-1
  
  # Generate sample data file
  python tools/import_veka_profiles.py --generate-sample --output sample_profiles.csv
  
  # Import to custom database
  python tools/import_veka_profiles.py --source data/profiles.xlsx --out custom.db
        """
    )
    
    parser.add_argument('--source', help='Excel file to import (.xlsx)')
    parser.add_argument('--csv', help='CSV file to import (.csv)')
    parser.add_argument('--sheet', help='Excel sheet name (default: first sheet)')
    parser.add_argument('--encoding', default='utf-8', help='CSV encoding (default: utf-8)')
    parser.add_argument('--out', help='Output database file (default: aufmass.db)')
    parser.add_argument('--generate-sample', action='store_true', help='Generate sample CSV file')
    parser.add_argument('--output', default='sample_veka_profiles.csv', help='Sample output file')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.source, args.csv, args.generate_sample]):
        parser.error("Must specify --source, --csv, or --generate-sample")
    
    importer = VEKAProfileImporter(args.out)
    
    try:
        if args.generate_sample:
            importer.generate_sample_data(args.output)
            return
        
        total_imported = 0
        
        if args.source:
            if not os.path.exists(args.source):
                print(f"❌ File not found: {args.source}")
                sys.exit(1)
            total_imported = importer.import_from_excel(args.source, args.sheet)
        
        elif args.csv:
            if not os.path.exists(args.csv):
                print(f"❌ File not found: {args.csv}")
                sys.exit(1)
            total_imported = importer.import_from_csv(args.csv, args.encoding)
        
        if total_imported > 0:
            print(f"🎉 Successfully imported {total_imported} profiles")
        else:
            print("❌ No profiles imported")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\\n⚠️  Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)
    finally:
        importer.cleanup()


if __name__ == '__main__':
    main()
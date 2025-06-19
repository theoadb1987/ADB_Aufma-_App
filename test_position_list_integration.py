#!/usr/bin/env python3
"""
Test für Position-Liste Integration.
Prüft, ob Positionen korrekt erstellt und in der Liste angezeigt werden.
"""
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.product import ProductType
from services.data_service import DataService
from services.position_service import PositionService
from ui.position_ui import PositionListUI

def test_position_list_integration():
    """Test der Position-Liste Integration."""
    print("🧪 Testing Position-Liste Integration...")
    
    # Setup
    data_service = DataService("test_position_list.db")
    position_service = PositionService(data_service)
    
    print("\n📋 Test 1: Position über PositionService erstellen")
    
    # Position-Daten wie sie von der UI kommen würden
    position_data = {
        'project_id': 1,
        'template_code': 'WZ_WIN',
        'title': 'Wohnzimmer Fenster Test',
        'description': 'Test Position für Wohnzimmer',
        'product_name': 'Kunststofffenster Standard',
        'product_type': ProductType.WINDOW,
        'w_mm': 1200,
        'h_mm': 1400,
        'quantity': 1.0,
        'unit': 'Stück',
        'price': 299.99
    }
    
    # Position erstellen
    position_id = position_service.create_position(position_data)
    
    if position_id:
        print(f"   ✅ Position erstellt mit ID: {position_id}")
    else:
        print("   ❌ Position konnte nicht erstellt werden")
        return False
    
    print("\n🔍 Test 2: Position aus Service abrufen")
    
    # Position über Service abrufen
    retrieved_position = position_service.get_position(position_id)
    
    if retrieved_position:
        print(f"   ✅ Position abgerufen: {retrieved_position['title']}")
        print(f"   - Product Type: {retrieved_position.get('product_type', 'None')}")
        print(f"   - Dimensions: {retrieved_position.get('w_mm', 0)}×{retrieved_position.get('h_mm', 0)}mm")
    else:
        print("   ❌ Position konnte nicht abgerufen werden")
        return False
    
    print("\n📊 Test 3: Alle Positionen für Projekt abrufen")
    
    # Weitere Position erstellen
    position_data2 = {
        'project_id': 1,
        'template_code': 'ROL_STD',
        'title': 'Rollladen Test',
        'description': 'Test Rollladen',
        'product_name': 'Rollladen Standard',
        'product_type': ProductType.ROLLER_SHUTTER,
        'w_mm': 1000,
        'h_mm': 1200,
        'quantity': 1.0,
        'unit': 'Stück',
        'price': 199.99
    }
    
    position_id2 = position_service.create_position(position_data2)
    print(f"   ✅ Zweite Position erstellt mit ID: {position_id2}")
    
    # Alle Positionen abrufen
    all_positions = position_service.get_positions_by_project(1)
    print(f"   ✅ {len(all_positions)} Positionen für Projekt 1 gefunden")
    
    for pos in all_positions:
        print(f"     - {pos['number']}: {pos['title']} ({pos.get('product_type', 'Kein Typ')})")
    
    print("\n🎨 Test 4: PositionListUI Integration (ohne GUI)")
    
    # Prüfen, ob die Datenstruktur für die UI korrekt ist
    if all_positions:
        first_position = all_positions[0]
        required_fields = ['id', 'number', 'title', 'quantity', 'price', 'product_type']
        
        missing_fields = []
        for field in required_fields:
            if field not in first_position:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   ❌ Fehlende Felder für UI: {missing_fields}")
            return False
        else:
            print("   ✅ Alle erforderlichen Felder für UI vorhanden")
    
    print("\n✅ Position-Liste Integration test erfolgreich abgeschlossen!")
    return True

def cleanup():
    """Test-Dateien aufräumen."""
    try:
        os.remove("test_position_list.db")
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    try:
        success = test_position_list_integration()
        if success:
            print("\n🎉 Alle Tests bestanden!")
        else:
            print("\n💥 Einige Tests fehlgeschlagen!")
            sys.exit(1)
    finally:
        cleanup()
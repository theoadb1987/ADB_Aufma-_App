#!/usr/bin/env python3
"""
Test script for position templates functionality.
"""
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.data_service import DataService
from models.position_template import PositionTemplate, STANDARD_TEMPLATES
from models.product import ProductType
from models.position import Position
from viewmodels.position_viewmodel import PositionViewModel

def test_position_templates():
    """Test position templates functionality."""
    print("🧪 Testing Position Templates...")
    
    # Initialize data service
    data_service = DataService("test_templates.db")
    
    # Test 1: Verify standard templates are loaded
    print("\n📋 Test 1: Loading standard templates")
    templates = data_service.get_position_templates()
    print(f"   ✓ Loaded {len(templates)} templates")
    
    for template in templates[:3]:  # Show first 3
        print(f"     - {template.name} ({template.code}): {template.dimensions_text}")
    
    # Test 2: Create position with template
    print("\n🏗️  Test 2: Creating position with template")
    template = templates[0] if templates else None
    
    if template:
        position_vm = PositionViewModel(data_service)
        
        # Create position with template
        position_id = position_vm.create_position_with_template(
            project_id=1,
            template_code=template.code,
            name=f"Test Position ({template.name})",
            floor="Erdgeschoss", 
            existing_window_type="Holz",
            roller_shutter_type="Nicht vorhanden",
            notes=f"Erstellt mit Vorlage: {template.name}",
            selected_products=["Kunststofffenster Standard"],
            w_mm=template.w_mm,
            h_mm=template.h_mm,
            product_id=None
        )
        
        if position_id:
            print(f"   ✓ Position created with ID: {position_id}")
            print(f"     Template: {template.name}")
            print(f"     Dimensions: {template.w_mm}×{template.h_mm}mm")
        else:
            print("   ❌ Failed to create position")
    
    # Test 3: Verify template data integrity
    print("\n🔍 Test 3: Template data integrity")
    categories = data_service.get_template_categories()
    print(f"   ✓ Found {len(categories)} template categories:")
    for category in categories:
        count = len(data_service.get_position_templates(category=category))
        print(f"     - {category}: {count} templates")
    
    # Test 4: Product type integration
    print("\n🎨 Test 4: Product type integration")
    for product_type in ProductType:
        print(f"   - {product_type.display_name}: {product_type.icon_path}")
        if product_type.icon_exists():
            print(f"     ✓ Icon exists")
        else:
            print(f"     ⚠️ Icon missing")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_position_templates()
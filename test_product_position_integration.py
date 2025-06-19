#!/usr/bin/env python3
"""
End-to-end test for Product → Position integration.
This test verifies the complete workflow from product selection to position creation.
"""
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.product import ProductType
from models.position import Position
from services.data_service import DataService
from viewmodels.position_viewmodel import PositionViewModel
from ui.position_ui import PositionDetailUI

def test_product_position_integration():
    """Test complete Product → Position integration workflow."""
    print("🧪 Testing Product → Position Integration...")
    
    # Setup
    data_service = DataService("test_integration.db")
    position_vm = PositionViewModel(data_service)
    
    print("\n📋 Test 1: Creating position with product type")
    
    # Simulate product selection
    selected_product_type = ProductType.ROLLER_SHUTTER
    print(f"   Selected product type: {selected_product_type.display_name}")
    
    # Create position with product type
    position_id = position_vm.create_position_with_template(
        project_id=1,
        template_code="ROL_STD",  # Rollladen template
        name=f"Test Position mit {selected_product_type.display_name}",
        floor="Erdgeschoss",
        existing_window_type="Kunststoff", 
        roller_shutter_type="Vorbaurollladen",
        notes=f"Position mit {selected_product_type.display_name} erstellt",
        selected_products=[f"{selected_product_type.display_name} Standard"],
        w_mm=1200,
        h_mm=1400,
        product_id=None,
        product_type=selected_product_type.display_name
    )
    
    if position_id:
        print(f"   ✅ Position created with ID: {position_id}")
    else:
        print("   ❌ Failed to create position")
        return False
    
    print("\n🔍 Test 2: Verifying position data")
    
    # Retrieve and verify position
    position = data_service.get_position(position_id)
    if position:
        print(f"   ✅ Position retrieved successfully")
        print(f"   - Name: {position.name}")
        print(f"   - Product Type: {position.product_type}")
        print(f"   - Template Code: {position.template_code}")
        print(f"   - Dimensions: {position.w_mm}×{position.h_mm}mm")
        
        # Verify data integrity
        assert position.product_type == selected_product_type.display_name
        assert position.template_code == "ROL_STD"
        assert position.w_mm == 1200
        assert position.h_mm == 1400
        print("   ✅ All data verified correctly")
    else:
        print("   ❌ Failed to retrieve position")
        return False
    
    print("\n🎨 Test 3: Testing all product types")
    
    test_product_types = [
        (ProductType.WINDOW, "Fenster"),
        (ProductType.FLY_SCREEN, "Fliegengitter"), 
        (ProductType.PLEATED_BLIND, "Plissee"),
        (ProductType.AWNING, "Markise")
    ]
    
    for i, (product_type, expected_name) in enumerate(test_product_types, 2):
        position_id = position_vm.create_position_with_template(
            project_id=1,
            template_code="",
            name=f"Test {expected_name}",
            floor="Erdgeschoss",
            existing_window_type="Holz",
            roller_shutter_type="Nicht vorhanden", 
            notes=f"Test für {expected_name}",
            selected_products=[f"{expected_name} Standard"],
            w_mm=1000,
            h_mm=1200,
            product_id=None,
            product_type=expected_name
        )
        
        if position_id:
            position = data_service.get_position(position_id)
            if position and position.product_type == expected_name:
                print(f"   ✅ {expected_name}: Position created and verified")
            else:
                print(f"   ❌ {expected_name}: Verification failed")
                return False
        else:
            print(f"   ❌ {expected_name}: Creation failed")
            return False
    
    print("\n📊 Test 4: Database integrity check")
    
    # Get all positions for project
    all_positions = data_service.get_positions(1)
    print(f"   Total positions created: {len(all_positions)}")
    
    # Verify all have product types
    positions_with_product_type = [p for p in all_positions if p.product_type]
    print(f"   Positions with product type: {len(positions_with_product_type)}")
    
    if len(positions_with_product_type) == len(all_positions):
        print("   ✅ All positions have product types")
    else:
        print("   ⚠️  Some positions missing product types")
    
    # Show summary
    print("\n📈 Summary:")
    for position in all_positions:
        print(f"   - {position.name}: {position.product_type or 'No type'}")
    
    print("\n✅ Product → Position integration test completed successfully!")
    return True

def cleanup():
    """Clean up test files."""
    try:
        os.remove("test_integration.db")
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    try:
        success = test_product_position_integration()
        if success:
            print("\n🎉 All tests passed!")
        else:
            print("\n💥 Some tests failed!")
            sys.exit(1)
    finally:
        cleanup()
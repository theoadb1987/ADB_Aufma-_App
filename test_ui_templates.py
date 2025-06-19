#!/usr/bin/env python3
"""
UI test for position templates functionality.
"""
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer

from ui.position_ui import PositionDetailUI
from services.data_service import DataService

class TestWindow(QMainWindow):
    """Test window for position templates UI."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Position Templates UI Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize data service
        self.data_service = DataService("test_ui.db")
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create position detail UI
        self.position_ui = PositionDetailUI()
        layout.addWidget(self.position_ui)
        
        # Load templates
        self._load_templates()
        
        # Test button
        test_button = QPushButton("Test Template Selection")
        test_button.clicked.connect(self._test_template_selection)
        layout.addWidget(test_button)
        
        print("✅ UI Test Window initialized")
        print("📋 Select a template from the dropdown to see it populate the form")
    
    def _load_templates(self):
        """Load templates into the UI."""
        templates = self.data_service.get_position_templates()
        self.position_ui.set_templates(templates)
        print(f"📋 Loaded {len(templates)} templates into UI")
    
    def _test_template_selection(self):
        """Test template selection functionality."""
        template = self.position_ui.get_selected_template()
        data = self.position_ui.get_data()
        
        if template:
            print(f"✅ Selected template: {template.name}")
            print(f"   Code: {template.code}")
            print(f"   Dimensions: {template.w_mm}×{template.h_mm}mm")
            print(f"   Form data: {data['template_code']}, {data['w_mm']}×{data['h_mm']}mm")
        else:
            print("❌ No template selected")

def main():
    """Run the UI test."""
    app = QApplication(sys.argv)
    
    # Create and show test window
    window = TestWindow()
    window.show()
    
    # Auto-close after 30 seconds for automated testing
    QTimer.singleShot(30000, app.quit)
    
    print("🚀 Starting UI test...")
    print("   Window will auto-close in 30 seconds")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
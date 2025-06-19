"""
Project UI module providing UI components for project views.
"""
# Standard libraries
import sys
import os
from typing import Optional, Callable, List, Tuple, Dict, Any
from datetime import datetime

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party libraries
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QTextEdit, QComboBox, 
                            QFrame, QScrollArea, QTabWidget, QDateEdit,
                            QSplitter, QLayout, QMessageBox)
from PyQt6.QtCore import Qt, QDate

# Local imports
from models.project import Project
from ui.base_ui import BaseUI
from utils.logger import get_logger

logger = get_logger(__name__)


class ProjectListUI(BaseUI):
    """UI class for project list view."""
    
    def __init__(self):
        """Initialize the ProjectListUI."""
        super().__init__()
        self.projects_layout = None
        self.projects_content = None
        self.search_input = None
        self.add_button = None
        logger.debug("ProjectListUI initialized")

    def setup_ui(self, container: QWidget) -> None:
        """Set up the project list UI elements in the given container."""
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Create header with access to the add button
        header = self.create_panel_header("Projekte", "+")
        container_layout.addWidget(header)
        
        # Get access to the add button for connecting callbacks later
        buttons = header.findChildren(QPushButton)
        if buttons:
            self.add_button = buttons[0]
        
        # Create search field
        search_container = self.create_search_field("Projekte durchsuchen...")
        
        # Get the search input widget for future reference
        self.search_input = search_container.findChild(QLineEdit)
        
        # Create content area
        self.projects_content = QWidget()
        self.projects_layout = QVBoxLayout(self.projects_content)
        self.projects_layout.setContentsMargins(0, 0, 0, 0)
        self.projects_layout.setSpacing(0)
        
        # Create scroll area
        scroll_area = self.create_scroll_area(self.projects_content)
        
        # Create tab widget for organizing content
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #2A2A2A;
            }
            QTabBar {
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #999999;
                min-width: 100px;
                height: 40px;
                font-size: 14px;
                padding: 0px 15px;
                margin-right: 4px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:hover {
                background-color: #333333;
                color: #bbbbbb;
            }
            QTabBar::tab:selected {
                background-color: #333333;
                color: #ffffff;
                border-bottom: 2px solid #0070f5;
            }
        """)
        
        # Create tab content
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.setContentsMargins(10, 10, 10, 10)
        tab1_layout.setSpacing(10)
        
        tab1_layout.addWidget(search_container)
        tab1_layout.addWidget(scroll_area, 1)
        
        # Add legend for project status
        legend = self._create_legend()
        tab1_layout.addWidget(legend)
        
        # Create secondary tab (empty for now)
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QLabel("Inhalt für zweiten Reiter"))
        
        # Add tabs
        tab_widget.addTab(tab1, "Projekte")
        tab_widget.addTab(tab2, "Kategorien")
        
        container_layout.addWidget(tab_widget)
        logger.debug("ProjectListUI setup completed")

    def _create_legend(self) -> QWidget:
        """Create a status legend widget."""
        legend = QWidget()
        legend.setStyleSheet("""
            background-color: #333333;
            border-radius: 8px;
            padding: 5px;
        """)
        
        legend_layout = QVBoxLayout(legend)
        legend_layout.setContentsMargins(10, 10, 10, 10)
        legend_layout.setSpacing(8)
        
        # Legend title
        title = QLabel("Legende:")
        title.setStyleSheet("color: #BBBBBB; font-size: 13px;")
        legend_layout.addWidget(title)
        
        # Status types
        status_types = [
            {"label": "Aufmaß erfolgt", "color": "#30d158"},
            {"label": "Aufmaß ausstehend", "color": "#ff9f0a"},
            {"label": "Klärung erforderlich", "color": "#bf5af2"},
            {"label": "Auftragsanpassung", "color": "#64d2ff"}
        ]
        
        # Create status items
        for status in status_types:
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(0, 2, 0, 2)
            item_layout.setSpacing(8)
            
            # Color dot
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {status['color']}; font-size: 16px;")
            
            # Status text
            label = QLabel(status["label"])
            label.setStyleSheet("color: #BBBBBB; font-size: 12px;")
            
            item_layout.addWidget(dot)
            item_layout.addWidget(label, 1)
            
            legend_layout.addWidget(item)
        
        return legend

    def create_project_item(self, project: Project) -> QWidget:
        """Create a project item widget for the list."""
        item = QWidget()
        item.setFixedHeight(70)
        
        # Background color based on selection
        bg_color = "#333333" if project.is_selected else "#2A2A2A"
        item.setStyleSheet(f"background-color: {bg_color};")
        
        # Layout
        layout = QHBoxLayout(item)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Info container (name and address)
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        # Project name
        name = QLabel(project.name)
        name.setStyleSheet(f"""
            color: {'white' if project.is_selected else '#CCCCCC'};
            font-size: 15px;
            font-weight: bold;
        """)
        
        # Project address
        address = QLabel(project.full_address)
        address.setStyleSheet("""
            color: #999999;
            font-size: 12px;
        """)
        
        info_layout.addWidget(name)
        info_layout.addWidget(address)
        
        # Status indicator as a colored dot
        status_dot = QLabel("●")
        status_dot.setFixedSize(24, 24)
        status_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_dot.setStyleSheet(f"""
            color: {project.color};
            font-size: 18px;
            padding: 0px;
            margin: 0px;
        """)
        
        # Add to row layout
        layout.addWidget(info_container, 1)
        layout.addWidget(status_dot)
        
        return item

    def update_project_list(self, projects: List[Project], on_select_project_callback: Optional[Callable] = None) -> None:
        """Update the project list with the provided projects."""
        # Clear current content
        self.clear_layout(self.projects_layout)
        
        if not projects:
            # Show empty state
            empty_label = QLabel("Keine Projekte vorhanden")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                color: #999999;
                font-size: 14px;
                padding: 20px;
            """)
            self.projects_layout.addWidget(empty_label)
            self.projects_layout.addStretch()
            return
            
        for i, project in enumerate(projects):
            # Create project item
            project_item = self.create_project_item(project)
            
            # Connect click event to select project if callback provided
            if on_select_project_callback:
                project_item.mousePressEvent = lambda event, p=project: on_select_project_callback(p)
                
            self.projects_layout.addWidget(project_item)
            
            # Add divider if not the last item
            if i < len(projects) - 1:
                divider = self.create_divider()
                self.projects_layout.addWidget(divider)
        
        # Add stretch to push items to the top
        self.projects_layout.addStretch()
        logger.debug(f"Updated project list with {len(projects)} projects")

    def set_add_button_callback(self, callback: Callable) -> None:
        """Set the callback for the add button."""
        if self.add_button:
            self.add_button.clicked.connect(callback)
            logger.debug("Set add button callback")

    def clear_layout(self, layout: QLayout) -> None:
        """Clear all widgets from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class ProjectDetailUI(BaseUI):
    """UI class for project detail view."""
    
    def __init__(self):
        """Initialize the ProjectDetailUI."""
        super().__init__()
        self.detail_header = None
        self.project_name = None
        self.project_address = None
        self.profile_system = None
        self.contact_person = None
        self.installation_date = None
        self.measurement_date = None
        self.field_service_employee = None
        self.project_status = None
        self.toggle_view_button = None
        self.save_button = None
        self.tab_widget = None
        self.delete_button = None
        logger.debug("ProjectDetailUI initialized")
    
    def setup_ui(self, container: QWidget) -> None:
        """Set up the project detail UI elements."""
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Create header
        self.detail_header = self.create_panel_header("Projektdetails", "✎", with_delete=True)
        container_layout.addWidget(self.detail_header)
        
        # Get access to the delete button for connecting callbacks later
        buttons = self.detail_header.findChildren(QPushButton)
        if len(buttons) > 1:  # First is edit button, second is delete button
            self.delete_button = buttons[1]
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #242424;
            }
            QTabBar {
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #999999;
                min-width: 100px;
                height: 32px;
                font-size: 12px;
                padding: 0px 12px;
                margin-right: 4px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:hover {
                background-color: #333333;
                color: #bbbbbb;
            }
            QTabBar::tab:selected {
                background-color: #333333;
                color: #ffffff;
                border-bottom: 2px solid #0070f5;
            }
        """)
        
        # Create tabs
        overview_tab = self._create_overview_tab()
        document_tab = QWidget()
        schedule_tab = QWidget()
        team_tab = QWidget()
        
        # Add tabs
        self.tab_widget.addTab(overview_tab, "Übersicht")
        self.tab_widget.addTab(document_tab, "Dokumente")
        self.tab_widget.addTab(schedule_tab, "Zeitplan")
        self.tab_widget.addTab(team_tab, "Team")
        
        container_layout.addWidget(self.tab_widget)
        logger.debug("ProjectDetailUI setup completed")
    
    def _create_overview_tab(self) -> QWidget:
        """Create the project overview tab with form fields."""
        # Main container
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scrollable content
        scroll_container = QScrollArea()
        scroll_container.setWidgetResizable(True)
        scroll_container.setFrameShape(QFrame.Shape.NoFrame)
        scroll_container.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_container.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #333333;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Form widget
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(20)
        
        # Title
        main_title = QLabel("Projektdetails")
        main_title.setStyleSheet("""
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            padding-bottom: 10px;
        """)
        form_layout.addWidget(main_title)
        
        # Form fields
        self.project_name = QLineEdit()
        self.project_address = QTextEdit()
        self.project_address.setMaximumHeight(60)
        
        self.profile_system = QComboBox()
        self.profile_system.addItems(["Kunststoff", "Aluminium", "Holz", "Holz-Aluminium"])
        
        self.contact_person = QLineEdit()
        
        self.installation_date = QDateEdit()
        self.installation_date.setDisplayFormat("dd.MM.yyyy")
        self.installation_date.setCalendarPopup(True)
        self.installation_date.setDate(QDate.currentDate().addMonths(1))
        
        self.measurement_date = QDateEdit()
        self.measurement_date.setDisplayFormat("dd.MM.yyyy")
        self.measurement_date.setCalendarPopup(True)
        self.measurement_date.setDate(QDate.currentDate())
        
        self.field_service_employee = QLineEdit()
        
        self.project_status = QComboBox()
        self.project_status.addItems(["Ausstehend", "Aufmaß", "Klärung", "Anpassung"])
        
        form_fields = [
            {"label": "Projektname", "widget": self.project_name},
            {"label": "Adresse", "widget": self.project_address, "multiline": True},
            {"label": "Profilsystem", "widget": self.profile_system, "dropdown": True},
            {"label": "Ansprechpartner", "widget": self.contact_person},
            {"label": "Gewünschter Montagetermin", "widget": self.installation_date, "date": True},
            {"label": "Aufmaß-Datum", "widget": self.measurement_date, "date": True},
            {"label": "Außendienstmitarbeiter", "widget": self.field_service_employee},
            {"label": "Status", "widget": self.project_status, "dropdown": True}
        ]
        
        # Add form fields
        self._add_form_fields(form_fields, form_layout)
        
        # Add spacing at the bottom
        form_layout.addStretch(1)
        
        # Set form widget as scrollable content
        scroll_container.setWidget(form_widget)
        main_layout.addWidget(scroll_container, 1)
        
        # Button container
        buttons_container = QWidget()
        buttons_container.setStyleSheet("background-color: #242424;")
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(20, 15, 20, 15)
        
        # Measurement area button
        self.toggle_view_button = QPushButton("📏 Zum Aufmaßbereich")
        self.toggle_view_button.setFixedSize(220, 40)
        self.toggle_view_button.setStyleSheet("""
            QPushButton {
                background-color: #0070f5;
                color: #ffffff;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0060d5;
            }
        """)
        
        # Save button
        self.save_button = QPushButton("✓ Projekt speichern")
        self.save_button.setFixedSize(220, 40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #30d158;
                color: #ffffff;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #25b048;
            }
        """)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.toggle_view_button)
        buttons_layout.addSpacing(15)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addStretch()
        
        main_layout.addWidget(buttons_container)
        
        return tab
    
    def _add_form_fields(self, fields, layout):
        """Helper to add form fields with consistent styling."""
        # Styling
        label_style = """
            color: #a0a0a0;
            font-size: 12px;
            margin-bottom: 4px;
        """
        
        field_style = """
            background-color: #383838;
            color: #e0e0e0;
            border-radius: 5px;
            padding: 8px;
            font-size: 14px;
            min-height: 18px;
        """
        
        # Add each field
        for field in fields:
            container = QWidget()
            field_layout = QVBoxLayout(container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(4)
            
            # Label
            label = QLabel(field["label"])
            label.setStyleSheet(label_style)
            field_layout.addWidget(label)
            
            # Input widget
            widget = field["widget"]
            
            if not field.get("button"):
                widget.setStyleSheet(field_style)
            
            if isinstance(widget, QTextEdit):
                widget.setMinimumHeight(60)
            elif isinstance(widget, QDateEdit):
                widget.setMinimumHeight(38)
            elif not field.get("button"):
                widget.setMinimumHeight(38)
            
            field_layout.addWidget(widget)
            layout.addWidget(container)
    
    def set_project_data(self, project: Project) -> None:
        """Set form data from a Project object."""
        if not project:
            return
        
        # Update header title
        header_label = self.detail_header.findChild(QLabel)
        if header_label:
            header_label.setText(project.name)
        
        # Update form fields
        self.project_name.setText(project.name)
        address_text = f"{project.address}\n{project.postal_code} {project.city}"
        self.project_address.setText(address_text)
        self.profile_system.setCurrentText(project.profile_system or "Kunststoff")
        self.contact_person.setText(project.contact_person)
        
        # Set dates
        if project.installation_date:
            self.installation_date.setDate(QDate(project.installation_date.year, 
                                          project.installation_date.month, 
                                          project.installation_date.day))
        
        if project.measurement_date:
            self.measurement_date.setDate(QDate(project.measurement_date.year, 
                                          project.measurement_date.month, 
                                          project.measurement_date.day))
        
        self.field_service_employee.setText(project.field_service_employee)
        self.project_status.setCurrentText(project.status)
        logger.debug(f"Set project data: {project.name}")
    
    def get_project_data(self, original_project: Project = None) -> Dict[str, Any]:
        """Get form data as a dictionary suitable for creating/updating a Project."""
        data = {}
        
        # Basic project fields
        data['name'] = self.project_name.text()
        
        # Parse address from text edit
        address_lines = self.project_address.toPlainText().strip().split('\n')
        if len(address_lines) >= 1:
            data['address'] = address_lines[0]
        else:
            data['address'] = ""
        
        # Parse city and postal code from second line
        if len(address_lines) >= 2:
            city_line = address_lines[1].strip()
            postal_parts = city_line.split(' ', 1)
            if len(postal_parts) >= 2:
                data['postal_code'] = postal_parts[0]
                data['city'] = postal_parts[1]
            else:
                data['city'] = city_line
                data['postal_code'] = ""
        else:
            data['city'] = ""
            data['postal_code'] = ""
        
        data['profile_system'] = self.profile_system.currentText()
        data['contact_person'] = self.contact_person.text()
        
        # Parse dates
        data['installation_date'] = datetime(
            self.installation_date.date().year(),
            self.installation_date.date().month(),
            self.installation_date.date().day()
        )
        
        data['measurement_date'] = datetime(
            self.measurement_date.date().year(),
            self.measurement_date.date().month(),
            self.measurement_date.date().day()
        )
        
        data['field_service_employee'] = self.field_service_employee.text()
        data['status'] = self.project_status.currentText()
        
        # Copy original project data if provided, then update with form data
        if original_project:
            data['id'] = original_project.id
            data['created_at'] = original_project.created_at
            data['updated_at'] = datetime.now()
        
        logger.debug(f"Retrieved project data: {data['name']}")
        return data
    
    def setup_for_new_project(self) -> None:
        """Prepare UI for creating a new project."""
        # Reset form fields
        self.project_name.setText("")
        self.project_address.setText("")
        self.profile_system.setCurrentIndex(0)
        self.contact_person.setText("")
        self.installation_date.setDate(QDate.currentDate().addMonths(1))
        self.measurement_date.setDate(QDate.currentDate())
        self.field_service_employee.setText("")
        self.project_status.setCurrentText("Ausstehend")
        
        # Update header title
        header_label = self.detail_header.findChild(QLabel)
        if header_label:
            header_label.setText("Neues Projekt")
        logger.debug("Setup for new project")
    
    def set_toggle_view_callback(self, callback: Callable) -> None:
        """Set the callback for the toggle view button."""
        if self.toggle_view_button:
            self.toggle_view_button.clicked.connect(callback)
            logger.debug("Set toggle view callback")
    
    def set_save_callback(self, callback: Callable) -> None:
        """Set the callback for the save button."""
        if self.save_button:
            self.save_button.clicked.connect(callback)
            logger.debug("Set save callback")
    
    def set_delete_callback(self, callback: Callable) -> None:
        """Set the callback for the delete button."""
        if self.delete_button:
            self.delete_button.clicked.connect(callback)
            logger.debug("Set delete callback")

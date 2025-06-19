# Standard libraries
import sys
import os
from typing import List, Dict, Any, Optional, Tuple, Callable, Union

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party libraries
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QLineEdit, QTextEdit, QComboBox, 
                           QFrame, QScrollArea, QTabWidget, QSplitter,
                           QDateEdit, QCheckBox, QRadioButton)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

# Local imports
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseUI:
    """Base UI class providing common UI components for views."""
    
    @staticmethod
    def create_panel_header(title_text: str, button_text: str, 
                           button_callback: Optional[Callable] = None,
                           with_delete: bool = False,
                           delete_callback: Optional[Callable] = None) -> QWidget:
        """
        Create a standardized header for panels.
        
        Args:
            title_text: Text to display as the panel title
            button_text: Text to display on the action button
            button_callback: Optional callback function for button click
            with_delete: Whether to include a delete button
            delete_callback: Optional callback function for delete button
            
        Returns:
            QWidget containing the header
        """
        header = QWidget()
        header.setFixedHeight(42)
        header.setStyleSheet("""
            background-color: #0070f5;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 0, 15, 0)
        
        # Title label
        title = QLabel(title_text)
        title.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: bold;
        """)
        
        # Action button
        action_button = QPushButton(button_text)
        action_button.setFixedSize(30, 30)
        action_button.setStyleSheet("""
            background-color: #0070f5;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border: 2px solid white;
            border-radius: 15px;
        """)
        
        if button_callback:
            action_button.clicked.connect(button_callback)
        
        # Add buttons for right panel
        if with_delete:
            delete_button = QPushButton("-")
            delete_button.setFixedSize(30, 30)
            delete_button.setStyleSheet("""
                background-color: #0070f5; 
                color: #ffffff; 
                border: 2px solid #ffffff; 
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            """)
            
            if delete_callback:
                delete_button.clicked.connect(delete_callback)
            
            menu_button = QPushButton("⋮")
            menu_button.setFixedSize(30, 30)
            menu_button.setStyleSheet("""
                background-color: #0070f5; 
                color: #ffffff; 
                border: 2px solid #ffffff; 
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            """)
            
            layout.addWidget(title)
            layout.addStretch()
            layout.addWidget(action_button)
            layout.addWidget(delete_button)
            layout.addWidget(menu_button)
        else:
            layout.addWidget(title)
            layout.addStretch()
            layout.addWidget(action_button)
        
        logger.debug(f"Created panel header with title: {title_text}")
        return header
    
    @staticmethod
    def create_search_field(placeholder_text: str, 
                           search_callback: Optional[Callable] = None) -> QWidget:
        """
        Create a standardized search field.
        
        Args:
            placeholder_text: Placeholder text for the search input
            search_callback: Optional callback function when text changes
            
        Returns:
            QWidget containing the search field
        """
        search_container = QWidget()
        search_container.setFixedHeight(40)
        
        layout = QHBoxLayout(search_container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText(placeholder_text)
        search_input.setStyleSheet("""
            background-color: #333333;
            color: #e0e0e0;
            border: none;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
        """)
        
        if search_callback:
            search_input.textChanged.connect(search_callback)
        
        # Search icon
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("""
            color: #888888;
            padding-right: 10px;
        """)
        search_icon.setFixedWidth(30)
        
        layout.addWidget(search_input, 1)
        layout.addWidget(search_icon)
        
        logger.debug(f"Created search field with placeholder: {placeholder_text}")
        return search_container
    
    @staticmethod
    def create_form_field(label_text: str, widget: QWidget) -> QWidget:
        """
        Create a standardized form field with label and input widget.
        
        Args:
            label_text: Text for the field label
            widget: Input widget (QLineEdit, QComboBox, etc.)
            
        Returns:
            QWidget containing the form field
        """
        container = QWidget()
        field_layout = QVBoxLayout(container)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(4)
        
        # Label
        label = QLabel(label_text)
        label.setStyleSheet("""
            color: #a0a0a0;
            font-size: 12px;
            margin-bottom: 4px;
        """)
        field_layout.addWidget(label)
        
        # Input widget styling based on widget type
        base_style = """
            background-color: #383838;
            color: #e0e0e0;
            border-radius: 5px;
            padding: 8px;
            font-size: 14px;
        """
        
        if isinstance(widget, QTextEdit):
            widget.setStyleSheet(base_style)
            widget.setMinimumHeight(60)
        elif isinstance(widget, QDateEdit):
            widget.setStyleSheet(base_style)
            widget.setMinimumHeight(38)
        elif isinstance(widget, QPushButton):
            # Don't override button styling
            pass
        else:
            widget.setStyleSheet(base_style)
            widget.setMinimumHeight(38)
        
        field_layout.addWidget(widget)
        
        return container
    
    @staticmethod
    def create_form_row(fields: List[Tuple[str, QWidget, Optional[int]]]) -> QWidget:
        """
        Create a row of form fields (horizontal layout).
        
        Args:
            fields: List of tuples (label_text, widget, stretch_factor)
                   stretch_factor is optional, defaults to 0
            
        Returns:
            QWidget containing the form row
        """
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(15)
        
        for field in fields:
            label_text = field[0]
            widget = field[1]
            stretch = field[2] if len(field) > 2 and field[2] is not None else 0
            
            field_container = BaseUI.create_form_field(label_text, widget)
            row_layout.addWidget(field_container, stretch)
        
        return row
    
    @staticmethod
    def create_divider(is_sub: bool = False) -> QWidget:
        """
        Create a standardized divider line.
        
        Args:
            is_sub: Whether this is a sub-divider (affects styling)
            
        Returns:
            QWidget containing the divider
        """
        divider_container = QWidget()
        divider_container.setFixedHeight(2)
        
        container_layout = QHBoxLayout(divider_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(2)
        
        if is_sub:
            # Thinner, darker divider for sub-items with indentation
            divider.setStyleSheet("background-color: #444444;")
            container_layout.setContentsMargins(40, 0, 0, 0)
        else:
            divider.setStyleSheet("background-color: #555555;")
        
        # Add spacing for centered divider
        container_layout.addSpacing(40)
        container_layout.addWidget(divider)
        container_layout.addSpacing(40)
        
        return divider_container
    
    @staticmethod
    def create_scroll_area(content_widget: QWidget) -> QScrollArea:
        """
        Create a standardized scroll area.
        
        Args:
            content_widget: Widget to be placed inside the scroll area
            
        Returns:
            QScrollArea containing the content widget
        """
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
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
        
        scroll_area.setWidget(content_widget)
        
        return scroll_area
    
    @staticmethod
    def create_tab_widget(tabs: List[Tuple[str, QWidget]]) -> QTabWidget:
        """
        Create a standardized tab widget.
        
        Args:
            tabs: List of tuples containing (tab_title, tab_widget)
            
        Returns:
            QTabWidget containing the tabs
        """
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
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
        
        for title, widget in tabs:
            tab_widget.addTab(widget, title)
        
        return tab_widget
    
    @staticmethod
    def create_standard_button(text: str, button_type: str = "primary", 
                             callback: Optional[Callable] = None,
                             fixed_size: Optional[Tuple[int, int]] = None) -> QPushButton:
        """
        Create a standardized button with different styles.
        
        Args:
            text: Button text
            button_type: Type of button ("primary", "secondary", "success", "danger")
            callback: Optional callback function for button click
            fixed_size: Optional tuple for fixed button size (width, height)
            
        Returns:
            QPushButton with applied styling
        """
        button = QPushButton(text)
        
        # Apply fixed size if specified
        if fixed_size:
            button.setFixedSize(fixed_size[0], fixed_size[1])
        
        # Style based on button type
        if button_type == "primary":
            button.setStyleSheet("""
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
        elif button_type == "secondary":
            button.setStyleSheet("""
                QPushButton {
                    background-color: #444444;
                    color: #ffffff;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
        elif button_type == "success":
            button.setStyleSheet("""
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
        elif button_type == "danger":
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ff3b30;
                    color: #ffffff;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e0352b;
                }
            """)
        
        # Connect callback if provided
        if callback:
            button.clicked.connect(callback)
        
        logger.debug(f"Created standard button: {text} ({button_type})")
        return button
    
    @staticmethod
    def create_button_container(buttons: List[QPushButton], 
                               alignment: str = "center") -> QWidget:
        """
        Create a container for buttons with proper layout.
        
        Args:
            buttons: List of QPushButton widgets
            alignment: Alignment of buttons ("left", "center", "right", "spread")
            
        Returns:
            QWidget containing the buttons
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        if alignment == "center":
            layout.addStretch(1)
            for button in buttons:
                layout.addWidget(button)
            layout.addStretch(1)
        elif alignment == "left":
            for button in buttons:
                layout.addWidget(button)
            layout.addStretch(1)
        elif alignment == "right":
            layout.addStretch(1)
            for button in buttons:
                layout.addWidget(button)
        elif alignment == "spread":
            layout.addStretch(1)
            for i, button in enumerate(buttons):
                layout.addWidget(button)
                if i < len(buttons) - 1:
                    layout.addStretch(1)
            layout.addStretch(1)
        
        return container

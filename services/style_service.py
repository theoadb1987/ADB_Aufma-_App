"""
Style service for managing UI themes and styles.
"""
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from typing import Dict, Any, Optional, Callable
from utils.logger import get_logger

logger = get_logger(__name__)

class StyleService:
    """Service for managing application styling and themes."""
    
    DARK_THEME = "dark"
    LIGHT_THEME = "light"
    
    def __init__(self, config_service=None):
        """Initialize the style service with optional config service."""
        self.config_service = config_service
        self.theme = self.DARK_THEME
        self.theme_changed_callbacks = []
        
        # Load theme from config if available
        if self.config_service:
            self.theme = self.config_service.get("theme", self.DARK_THEME)
        
        logger.info(f"StyleService initialized with theme: {self.theme}")
    
    def set_theme(self, theme: str) -> None:
        """Set the application theme (dark or light)."""
        if theme not in [self.DARK_THEME, self.LIGHT_THEME]:
            logger.error(f"Invalid theme: {theme}")
            return
        
        self.theme = theme
        
        # Apply the theme to the application
        self._apply_theme()
        
        # Save to config if available
        if self.config_service:
            self.config_service.set("theme", theme)
        
        # Notify callbacks
        for callback in self.theme_changed_callbacks:
            callback(theme)
        
        logger.info(f"Theme set to: {theme}")
    
    def _apply_theme(self) -> None:
        """Apply the current theme to the application."""
        if self.theme == self.DARK_THEME:
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
    
    def _apply_dark_theme(self) -> None:
        """Apply dark theme to the application."""
        app = QApplication.instance()
        if not app:
            logger.error("QApplication instance not found")
            return
        
        # Define palette colors
        background_color = QColor("#1e1e1e")
        dark_gray = QColor("#282828")
        button_color = QColor("#333333")
        text_color = QColor("#e0e0e0")
        highlight_color = QColor("#0070f5")
        
        # Create palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, background_color)
        dark_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        dark_palette.setColor(QPalette.ColorRole.Base, dark_gray)
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, background_color)
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, dark_gray)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
        dark_palette.setColor(QPalette.ColorRole.Text, text_color)
        dark_palette.setColor(QPalette.ColorRole.Button, button_color)
        dark_palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Highlight, highlight_color)
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        # Apply palette
        app.setPalette(dark_palette)
        
        # Set stylesheet
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'SF Pro Display', 'Arial', sans-serif;
            }
            
            QPushButton {
                background-color: #333333;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                color: #e0e0e0;
            }
            
            QPushButton:hover {
                background-color: #444444;
            }
            
            QPushButton:pressed {
                background-color: #0070f5;
            }
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #333333;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 4px;
                color: #e0e0e0;
            }
            
            QTabWidget::pane {
                border: none;
                background-color: #242424;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #999999;
                padding: 8px 12px;
                margin-right: 4px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #333333;
                color: #ffffff;
                border-bottom: 2px solid #0070f5;
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
            
            QTableView, QListView, QTreeView {
                background-color: #282828;
                alternate-background-color: #2a2a2a;
                border: none;
                gridline-color: #333333;
                color: #e0e0e0;
            }
            
            QHeaderView::section {
                background-color: #383838;
                color: #e0e0e0;
                padding: 4px;
                border: none;
                border-right: 1px solid #444444;
                border-bottom: 1px solid #444444;
            }
        """)
        
        logger.info("Applied dark theme")
    
    def _apply_light_theme(self) -> None:
        """Apply light theme to the application."""
        app = QApplication.instance()
        if not app:
            logger.error("QApplication instance not found")
            return
        
        # Define palette colors
        background_color = QColor("#f5f5f5")
        base_color = QColor("#ffffff")
        button_color = QColor("#e0e0e0")
        text_color = QColor("#202020")
        highlight_color = QColor("#0070f5")
        
        # Create palette
        light_palette = QPalette()
        light_palette.setColor(QPalette.ColorRole.Window, background_color)
        light_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        light_palette.setColor(QPalette.ColorRole.Base, base_color)
        light_palette.setColor(QPalette.ColorRole.AlternateBase, background_color)
        light_palette.setColor(QPalette.ColorRole.ToolTipBase, base_color)
        light_palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
        light_palette.setColor(QPalette.ColorRole.Text, text_color)
        light_palette.setColor(QPalette.ColorRole.Button, button_color)
        light_palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        light_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.black)
        light_palette.setColor(QPalette.ColorRole.Highlight, highlight_color)
        light_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        # Apply palette
        app.setPalette(light_palette)
        
        # Set stylesheet
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f5f5;
                color: #202020;
                font-family: 'SF Pro Display', 'Arial', sans-serif;
            }
            
            QPushButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                color: #202020;
            }
            
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            
            QPushButton:pressed {
                background-color: #0070f5;
                color: white;
            }
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
                color: #202020;
            }
            
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
            
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #606060;
                padding: 8px 12px;
                margin-right: 4px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #202020;
                border-bottom: 2px solid #0070f5;
            }
            
            QScrollBar:vertical {
                background: #e0e0e0;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background: #b0b0b0;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QTableView, QListView, QTreeView {
                background-color: #ffffff;
                alternate-background-color: #f8f8f8;
                border: none;
                gridline-color: #e0e0e0;
                color: #202020;
            }
            
            QHeaderView::section {
                background-color: #e8e8e8;
                color: #404040;
                padding: 4px;
                border: none;
                border-right: 1px solid #d0d0d0;
                border-bottom: 1px solid #d0d0d0;
            }
        """)
        
        logger.info("Applied light theme")
    
    def toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        new_theme = self.LIGHT_THEME if self.theme == self.DARK_THEME else self.DARK_THEME
        self.set_theme(new_theme)
        logger.info(f"Theme toggled to: {new_theme}")
    
    def get_current_theme(self) -> str:
        """Get the current theme name."""
        return self.theme
    
    def is_dark_theme(self) -> bool:
        """Check if the current theme is dark."""
        return self.theme == self.DARK_THEME
    
    def register_theme_changed_callback(self, callback: Callable[[str], None]) -> None:
        """Register a callback to be notified when the theme changes."""
        self.theme_changed_callbacks.append(callback)
    
    def get_style_for_status(self, status: str) -> Dict[str, str]:
        """Get colors and styles for a specific status."""
        # Colors for dark theme
        if self.is_dark_theme():
            status_styles = {
                "Aufmaß": {
                    "color": "#30d158",
                    "background": "#1a3f29",
                    "icon": "✓"
                },
                "Ausstehend": {
                    "color": "#ff9f0a",
                    "background": "#3d3524",
                    "icon": "⏱"
                },
                "Klärung": {
                    "color": "#bf5af2",
                    "background": "#372a3f",
                    "icon": "?"
                },
                "Anpassung": {
                    "color": "#64d2ff",
                    "background": "#243540",
                    "icon": "🔧"
                }
            }
        else:
            # Colors for light theme
            status_styles = {
                "Aufmaß": {
                    "color": "#248a3d",
                    "background": "#e3f2e3",
                    "icon": "✓"
                },
                "Ausstehend": {
                    "color": "#b86000",
                    "background": "#fff3e3",
                    "icon": "⏱"
                },
                "Klärung": {
                    "color": "#8e3bbc",
                    "background": "#f5ebfa",
                    "icon": "?"
                },
                "Anpassung": {
                    "color": "#1e88c9",
                    "background": "#e6f3ff",
                    "icon": "🔧"
                }
            }
        
        return status_styles.get(status, {
            "color": "#777777",
            "background": "#333333" if self.is_dark_theme() else "#e0e0e0",
            "icon": "•"
        })
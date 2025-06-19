"""
Element Designer View for window type selection and schnitt preview.
"""
import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                            QScrollArea, QFrame, QTextEdit, QSplitter, QGridLayout, QSlider, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from models.window_element import WindowElement, ProfileType, WindowType
from models.profile import Profile, VEKASystem
from services.service_container import container
from services.data_service import DataService


class ElementDesignerView(QWidget):
    """ElementDesigner Widget nach Spezifikation V1 VariantA"""
    
    # Signals
    window_type_selected = pyqtSignal(WindowType)
    svg_export_requested = pyqtSignal(str)  # Export path
    profile_changed = pyqtSignal(str)  # Profile ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.glossary_data = {}
        self.schnitt_mapping = {}
        self.current_window_type = None
        self.current_profile = None
        
        # Parameters for customization
        self.mullion_offset = 50  # Pfosten-Versatz in %
        self.transom_offset = 50  # Kämpfer-Versatz in %
        
        # Get DataService (with fallback)
        try:
            self.data_service = container.get(DataService)
        except Exception:
            # Fallback für Tests oder standalone Verwendung
            self.data_service = DataService()
        
        self._load_data_files()
        self._setup_ui()
        
    def _load_data_files(self):
        """Lädt Glossar und Schnitt-Mapping"""
        try:
            # Glossar laden
            glossar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'glossar.json')
            if os.path.exists(glossar_path):
                with open(glossar_path, 'r', encoding='utf-8') as f:
                    self.glossary_data = json.load(f)
                    
            # Schnitt-Mapping laden
            mapping_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'schnitt_map.json')
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    self.schnitt_mapping = json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Datendateien: {e}")
            
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Titel
        title = QLabel("<h2>ElementDesigner v1.0</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff; margin: 10px;")
        layout.addWidget(title)
        
        # Profile selection section
        profile_section = self._create_profile_section()
        layout.addWidget(profile_section)
        
        # Splitter für Hauptbereiche
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Linke Seite: Fenstertyp-Auswahl
        left_widget = self._create_window_type_panel()
        splitter.addWidget(left_widget)
        
        # Rechte Seite: Schnitt-Vorschau und Glossar
        right_widget = self._create_preview_panel()
        splitter.addWidget(right_widget)
        
        # Verhältnis setzen
        splitter.setSizes([300, 400])
        
        # Parameters Panel
        params_panel = self._create_parameters_panel()
        layout.addWidget(params_panel)
        
        # Export Buttons
        export_layout = QHBoxLayout()
        
        svg_export_btn = QPushButton("📄 SVG Exportieren")
        svg_export_btn.setStyleSheet("""
            QPushButton {
                background-color: #0070f5;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0060d5;
            }
        """)
        svg_export_btn.clicked.connect(self._export_svg)
        
        png_export_btn = QPushButton("🖼️ PNG Screenshot")
        png_export_btn.setStyleSheet("""
            QPushButton {
                background-color: #30d158;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #25b048;
            }
        """)
        png_export_btn.clicked.connect(self._export_png)
        
        export_layout.addStretch()
        export_layout.addWidget(svg_export_btn)
        export_layout.addWidget(png_export_btn)
        export_layout.addStretch()
        
        layout.addLayout(export_layout)
    
    def _create_profile_section(self):
        """Erstellt die Profilsystem-Auswahl"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border-radius: 8px;
                margin: 5px;
                max-height: 80px;
            }
        """)
        layout = QHBoxLayout()
        widget.setLayout(layout)
        
        # Profile system label
        profile_label = QLabel("<b>Profilsystem:</b>")
        profile_label.setStyleSheet("color: #CCCCCC; margin: 10px;")
        layout.addWidget(profile_label)
        
        # Profile system dropdown
        self.profile_combo = QComboBox()
        self.profile_combo.setStyleSheet("""
            QComboBox {
                background-color: #383838;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #777777;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAYAAAA71pVKAAAAjklEQVQoU2NkwANiY2P/AwlcYiTbfAYGBsaYmJj/QJVAMpBsF7jACVRTOAODaBcDg8gKBoZ/fxgYWP4yMEz8y8Dw9y8DA8M/BgZGfIpJNh9oONBpqOaAfGAVAyM+xSSZDzQYZCmQHwK0l4GBgZWBge0vA8PWvwwMa4AWdwCtZmZgYGDEp5gk84GGg/wPtJw0+wEIRi0PvdG8jQAAAABJRU5ErkJggg==);
                width: 12px;
                height: 12px;
            }
        """)
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        layout.addWidget(self.profile_combo)
        
        # Load profile systems
        self._load_profile_systems()
        
        layout.addStretch()
        
        return widget
    
    def _load_profile_systems(self):
        """Lädt verfügbare Profilsysteme"""
        try:
            # Get all profile systems
            systems = {}
            profiles = self.data_service.get_profiles()
            
            for profile in profiles:
                system_name = profile.system.display_name
                if system_name not in systems:
                    systems[system_name] = profile.system.code
            
            # Add to dropdown
            self.profile_combo.clear()
            for display_name, code in sorted(systems.items()):
                self.profile_combo.addItem(display_name, code)
            
            # Set default
            if self.profile_combo.count() > 0:
                self.profile_combo.setCurrentIndex(0)
                self._on_profile_changed(self.profile_combo.currentText())
                
        except Exception as e:
            print(f"Fehler beim Laden der Profilsysteme: {e}")
    
    def _on_profile_changed(self, system_name: str):
        """Behandelt Änderung des Profilsystems"""
        system_code = self.profile_combo.currentData()
        if system_code:
            # Load frame profile for this system
            frame_profiles = self.data_service.get_profiles(
                system_code=system_code, 
                profile_type_code='frame'
            )
            
            if frame_profiles:
                self.current_profile = frame_profiles[0]
                self.profile_changed.emit(self.current_profile.id)
                self._update_preview_with_profile()
                print(f"Profilsystem gewechselt zu: {system_name} ({self.current_profile.id})")
    
    def _update_preview_with_profile(self):
        """Aktualisiert Vorschau mit Profilinformationen"""
        if self.current_profile and hasattr(self, 'preview_area'):
            current_text = self.preview_area.text()
            
            # Add profile info if not already present
            if "Profilsystem:" not in current_text:
                profile_info = f"<br><br><b style='color: #FFFFFF;'>Profilsystem:</b><br>"
                profile_info += f"<span style='color: #0070f5;'>{self.current_profile.display_name}</span><br>"
                profile_info += f"<span style='color: #CCCCCC;'>Bautiefe: {self.current_profile.dimensions.depth_mm}mm</span><br>"
                profile_info += f"<span style='color: #CCCCCC;'>Uf-Wert: {self.current_profile.thermal.uf_value} W/(m²K)</span>"
                
                # Insert profile info before window type info
                if self.current_window_type:
                    updated_text = current_text + profile_info
                else:
                    updated_text = f"<b style='color: #FFFFFF;'>Profilauswahl aktiv</b>{profile_info}"
                
                self.preview_area.setText(updated_text)
        
    def _create_window_type_panel(self):
        """Erstellt das Fenstertyp-Auswahl Panel"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Titel
        title_label = QLabel("<b>Fenstertypen (14 Stk.)</b>")
        title_label.setStyleSheet("color: #CCCCCC; margin: 10px;")
        layout.addWidget(title_label)
        
        # Scroll-Bereich für Icon-Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(400)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Grid für Icons
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        grid_widget.setLayout(grid_layout)
        
        # Window Type Buttons erstellen
        row, col = 0, 0
        for window_type in WindowType:
            btn = QPushButton()
            btn.setText(f"{window_type.code}\n{window_type.display_name}")
            btn.setMinimumSize(120, 80)
            btn.setMaximumSize(120, 80)
            btn.setStyleSheet("""
                QPushButton {
                    border: 2px solid #555555;
                    border-radius: 8px;
                    background-color: #383838;
                    color: #CCCCCC;
                    font-size: 9px;
                }
                QPushButton:hover {
                    background-color: #484848;
                    border-color: #777777;
                    color: #FFFFFF;
                }
                QPushButton:pressed {
                    background-color: #0070f5;
                    border-color: #0070f5;
                }
            """)
            
            # Tooltip mit Beschreibung
            if 'fenstertypen' in self.glossary_data and window_type.code in self.glossary_data.get('fenstertypen', {}):
                tooltip_data = self.glossary_data['fenstertypen'][window_type.code]
                tooltip = f"<b>{tooltip_data['name']}</b><br>{tooltip_data['beschreibung']}<br><i>{tooltip_data['anwendung']}</i>"
                btn.setToolTip(tooltip)
            else:
                btn.setToolTip(f"{window_type.display_name}\n{window_type.description}")
                
            # Klick-Handler
            btn.clicked.connect(lambda checked, wt=window_type: self._on_window_type_selected(wt))
            
            grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= 2:  # 2 Spalten
                col = 0
                row += 1
                
        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)
        
        return widget
        
    def _create_preview_panel(self):
        """Erstellt das Vorschau- und Glossar-Panel"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Schnitt-Vorschau Bereich
        preview_title = QLabel("<b>Schnitt-Vorschau</b>")
        preview_title.setStyleSheet("color: #CCCCCC; margin: 10px;")
        layout.addWidget(preview_title)
        
        self.preview_area = QLabel()
        self.preview_area.setMinimumHeight(200)
        self.preview_area.setStyleSheet("""
            QLabel {
                border: 1px solid #555555;
                background-color: #383838;
                color: #CCCCCC;
                margin: 5px;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_area.setText("Fenstertyp auswählen für Vorschau")
        self.preview_area.setWordWrap(True)
        layout.addWidget(self.preview_area)
        
        # Glossar-Bereich
        glossar_title = QLabel("<b>Glossar</b>")
        glossar_title.setStyleSheet("color: #CCCCCC; margin: 10px;")
        layout.addWidget(glossar_title)
        
        self.glossar_text = QTextEdit()
        self.glossar_text.setMaximumHeight(150)
        self.glossar_text.setReadOnly(True)
        self.glossar_text.setStyleSheet("""
            QTextEdit {
                background-color: #383838;
                color: #CCCCCC;
                border: 1px solid #555555;
                border-radius: 4px;
                margin: 5px;
                padding: 8px;
            }
        """)
        self._update_glossar_display()
        layout.addWidget(self.glossar_text)
        
        return widget
        
    def _update_glossar_display(self):
        """Aktualisiert die Glossar-Anzeige"""
        if 'begriffe' in self.glossary_data:
            glossar_html = "<h4 style='color: #FFFFFF;'>Begriffe:</h4><ul style='color: #CCCCCC;'>"
            for begriff, definition in self.glossary_data['begriffe'].items():
                glossar_html += f"<li><b style='color: #FFFFFF;'>{begriff}:</b> {definition}</li>"
            glossar_html += "</ul>"
            self.glossar_text.setHtml(glossar_html)
        else:
            self.glossar_text.setText("Glossar-Daten nicht verfügbar")
            
    def _on_window_type_selected(self, window_type: WindowType):
        """Behandelt Fenstertyp-Auswahl"""
        self.current_window_type = window_type
        
        # Schnitt-Templates für diesen Typ finden
        templates = []
        if 'schnitt_templates' in self.schnitt_mapping:
            for template_id, template_data in self.schnitt_mapping['schnitt_templates'].items():
                if window_type.code in template_data.get('window_types', []):
                    templates.append(f"• {template_data['description']} ({template_data['file']})")
                
        # Preview aktualisieren
        if templates:
            preview_text = f"<b style='color: #FFFFFF;'>{window_type.display_name}</b><br><br>"
            preview_text += f"<i style='color: #CCCCCC;'>{window_type.description}</i><br><br>"
            preview_text += "<b style='color: #FFFFFF;'>Verfügbare Schnitt-Templates:</b><br>"
            preview_text += "<br>".join(templates)
        else:
            preview_text = f"<b style='color: #FFFFFF;'>{window_type.display_name}</b><br><br>"
            preview_text += f"<i style='color: #CCCCCC;'>{window_type.description}</i><br><br>"
            preview_text += "<span style='color: #FF6B6B;'>Keine Schnitt-Templates gefunden</span>"
            
        self.preview_area.setText(preview_text)
        
        # Signal emittieren
        self.window_type_selected.emit(window_type)
        
    def _export_svg(self):
        """Exportiert aktuellen Entwurf als SVG"""
        if not self.current_window_type:
            self.preview_area.setText("Bitte erst einen Fenstertyp auswählen!")
            return
            
        export_path = f"export_{self.current_window_type.code}.svg"
        # TODO: Implementiere echten SVG Export
        print(f"SVG Export: {export_path}")
        self.svg_export_requested.emit(export_path)
        
    def _export_png(self):
        """Erstellt PNG Screenshot"""
        if not self.current_window_type:
            self.preview_area.setText("Bitte erst einen Fenstertyp auswählen!")
            return
            
        # TODO: Implementiere PNG Screenshot
        print(f"PNG Screenshot: {self.current_window_type.code}")
        
    def _create_parameters_panel(self):
        """Erstellt das Parameter-Panel mit Slidern."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: #2A2A2A;
                border-radius: 8px;
                margin: 5px;
                max-height: 120px;
            }
        """)
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Titel
        title_label = QLabel("<b>Parameter</b>")
        title_label.setStyleSheet("color: #CCCCCC; margin: 5px;")
        layout.addWidget(title_label)
        
        # Pfosten (Mullion) Slider
        mullion_layout = QHBoxLayout()
        mullion_label = QLabel("Pfosten-Versatz:")
        mullion_label.setStyleSheet("color: #CCCCCC; min-width: 100px;")
        
        self.mullion_slider = QSlider(Qt.Orientation.Horizontal)
        self.mullion_slider.setMinimum(20)
        self.mullion_slider.setMaximum(80)
        self.mullion_slider.setValue(self.mullion_offset)
        self.mullion_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #555555;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0070f5;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #0060d5;
            }
        """)
        self.mullion_slider.valueChanged.connect(self._on_mullion_changed)
        
        self.mullion_value_label = QLabel(f"{self.mullion_offset}%")
        self.mullion_value_label.setStyleSheet("color: #CCCCCC; min-width: 40px;")
        
        mullion_layout.addWidget(mullion_label)
        mullion_layout.addWidget(self.mullion_slider)
        mullion_layout.addWidget(self.mullion_value_label)
        layout.addLayout(mullion_layout)
        
        # Kämpfer (Transom) Slider
        transom_layout = QHBoxLayout()
        transom_label = QLabel("Kämpfer-Versatz:")
        transom_label.setStyleSheet("color: #CCCCCC; min-width: 100px;")
        
        self.transom_slider = QSlider(Qt.Orientation.Horizontal)
        self.transom_slider.setMinimum(30)
        self.transom_slider.setMaximum(70)
        self.transom_slider.setValue(self.transom_offset)
        self.transom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #555555;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #30d158;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #25b048;
            }
        """)
        self.transom_slider.valueChanged.connect(self._on_transom_changed)
        
        self.transom_value_label = QLabel(f"{self.transom_offset}%")
        self.transom_value_label.setStyleSheet("color: #CCCCCC; min-width: 40px;")
        
        transom_layout.addWidget(transom_label)
        transom_layout.addWidget(self.transom_slider)
        transom_layout.addWidget(self.transom_value_label)
        layout.addLayout(transom_layout)
        
        return widget
    
    def _on_mullion_changed(self, value):
        """Behandelt Änderung des Pfosten-Versatzes."""
        self.mullion_offset = value
        self.mullion_value_label.setText(f"{value}%")
        self._update_preview_with_parameters()
        
    def _on_transom_changed(self, value):
        """Behandelt Änderung des Kämpfer-Versatzes."""
        self.transom_offset = value
        self.transom_value_label.setText(f"{value}%")
        self._update_preview_with_parameters()
        
    def _update_preview_with_parameters(self):
        """Aktualisiert Vorschau mit aktuellen Parametern."""
        if self.current_window_type:
            # Trigger preview update with current parameters
            current_text = self.preview_area.text()
            if "Pfosten:" not in current_text and (
                self.current_window_type in [WindowType.FT_DD, WindowType.FT_DKD, WindowType.FT_HS]
            ):
                # Add parameter info for multi-panel windows
                current_text += f"<br><br><b style='color: #FFFFFF;'>Parameter:</b><br>"
                current_text += f"<span style='color: #0070f5;'>Pfosten: {self.mullion_offset}%</span><br>"
                current_text += f"<span style='color: #30d158;'>Kämpfer: {self.transom_offset}%</span>"
                self.preview_area.setText(current_text)
    
    def get_current_window_type(self):
        """Gibt aktuell ausgewählten Fenstertyp zurück"""
        return self.current_window_type
        
    def get_current_parameters(self):
        """Gibt aktuelle Parameter zurück"""
        return {
            'mullion_offset': self.mullion_offset,
            'transom_offset': self.transom_offset
        }
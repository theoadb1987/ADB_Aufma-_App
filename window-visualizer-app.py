# Projektstruktur:
# window_visualizer/
# ├── main.py
# ├── models/
# │   ├── __init__.py
# │   ├── window_element.py
# │   └── profile_data.py
# ├── views/
# │   ├── __init__.py
# │   ├── main_window.py
# │   ├── graphics_view.py
# │   └── window_item.py
# ├── viewmodels/
# │   ├── __init__.py
# │   └── window_viewmodel.py
# ├── controllers/
# │   ├── __init__.py
# │   └── view_controller.py
# └── utils/
#     ├── __init__.py
#     └── colors.py

# === models/window_element.py ===
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum
import uuid

class ProfileType(Enum):
    """VEKA Profiltypen"""
    BLEND_070 = "070"
    BLEND_076_MD = "076 MD"
    BLEND_082_MD = "082 MD"
    FLUEGEL_103_229 = "103.229"
    FLUEGEL_103_232 = "103.232"
    FLUEGEL_103_380 = "103.380"
    FLUEGEL_103_381 = "103.381"

class WindowType(Enum):
    """Fenstertypen nach ElementDesigner Spezifikation"""
    FT_F = ("FT_F", "Festverglasung", "unverriegelt")
    FT_D = ("FT_D", "Dreh-Fenster", "DIN L / R")
    FT_K = ("FT_K", "Kipp-Fenster", "oberes Kipp")
    FT_DK = ("FT_DK", "Dreh-Kipp", "Standard")
    FT_DD = ("FT_DD", "2-flg. Dreh/Dreh", "Mittelpfosten")
    FT_DKD = ("FT_DKD", "2-flg. Dreh-Kipp", "links + rechts")
    FT_HS = ("FT_HS", "Hebe-Schiebe", "Parallel-Ebene")
    FT_PSK = ("FT_PSK", "Parallel-Schiebe-Kipp", "PSK")
    FT_SVG = ("FT_SVG", "Schwing-Fenster", "mittig gelagert")
    FT_VS = ("FT_VS", "Vertikal-Schiebe", "Double-hung")
    FT_HS2 = ("FT_HS2", "Horizontal-Schiebe", "2 Schiebeflügel")
    FT_FALT = ("FT_FALT", "Falt-Fenster/Tür", "mehrteilig")
    FT_RB = ("FT_RB", "Rundbogen-Fenster", "fest")
    FT_SCHR = ("FT_SCHR", "Schrägelement", "fest / DK")
    
    def __init__(self, code, name, description):
        self.code = code
        self.name = name
        self.description = description

@dataclass
class WindowElement:
    """Datenmodell für ein Fensterelement"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    x: float = 0.0
    y: float = 0.0
    width: float = 1000.0
    height: float = 1200.0
    profile_type: ProfileType = ProfileType.BLEND_070
    window_type: WindowType = WindowType.FT_DK
    comment: str = ""
    rotation: float = 0.0
    is_selected: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Berechnete Profilmaße
    profile_width_a: float = 0.0
    profile_width_b: float = 0.0
    profile_width_c: float = 0.0
    profile_width_d: float = 0.0
    
    @property
    def center_x(self) -> float:
        return self.x + self.width / 2
    
    @property
    def center_y(self) -> float:
        return self.y + self.height / 2
    
    def get_bounds(self) -> tuple[float, float, float, float]:
        """Gibt (x, y, x+width, y+height) zurück"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

# === models/profile_data.py ===
from typing import Dict, Tuple

# VEKA Profilmaße aus der Tabelle
PROFILE_DIMENSIONS = {
    ProfileType.BLEND_070: {
        58: {"A": 58, "B": 70, "C": 14, "D": 0},
        67: {"A": 67, "B": 70, "C": 38, "D": 18},
        80: {"A": 80, "B": 70, "C": 51, "D": 31},
        100: {"A": 100, "B": 70, "C": 71, "D": 51},
    },
    ProfileType.BLEND_076_MD: {
        71: {"A": 71, "B": 76, "C": 38, "D": 18},
        81: {"A": 81, "B": 76, "C": 48, "D": 28},
        104: {"A": 104, "B": 76, "C": 71, "D": 51},
    },
    ProfileType.BLEND_082_MD: {
        73: {"A": 73, "B": 85, "C": 40, "D": 20},
        83: {"A": 83, "B": 82, "C": 50, "D": 30},
        106: {"A": 106, "B": 82, "C": 73, "D": 53},
    }
}

# === utils/colors.py ===
from PyQt6.QtGui import QColor
from models.window_element import ProfileType

# Farbschema für Profile
PROFILE_COLORS = {
    ProfileType.BLEND_070: QColor(70, 130, 180),      # Steel Blue
    ProfileType.BLEND_076_MD: QColor(60, 179, 113),   # Medium Sea Green
    ProfileType.BLEND_082_MD: QColor(220, 20, 60),    # Crimson
    ProfileType.FLUEGEL_103_229: QColor(255, 140, 0), # Dark Orange
    ProfileType.FLUEGEL_103_232: QColor(147, 112, 219), # Medium Purple
    ProfileType.FLUEGEL_103_380: QColor(32, 178, 170),  # Light Sea Green
    ProfileType.FLUEGEL_103_381: QColor(255, 20, 147),  # Deep Pink
}

SELECTION_COLOR = QColor(255, 200, 0, 128)  # Gelb mit Transparenz
GRID_COLOR = QColor(200, 200, 200, 50)
SNAP_POINT_COLOR = QColor(255, 0, 0)

# === views/window_item.py ===
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QFont, QPainter, QFontMetrics
from models.window_element import WindowElement
from utils.colors import PROFILE_COLORS, SELECTION_COLOR

class WindowItem(QGraphicsRectItem):
    """Grafische Repräsentation eines Fensterelements"""
    
    def __init__(self, element: WindowElement):
        super().__init__()
        self.element = element
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        
        # Visuelle Komponenten
        self._dimension_texts = []
        self._profile_label = None
        self._show_dimensions = True
        self._show_labels = True
        
        self.update_geometry()
        self.update_appearance()
        
    def update_geometry(self):
        """Aktualisiert Position und Größe"""
        self.setRect(0, 0, self.element.width, self.element.height)
        self.setPos(self.element.x, self.element.y)
        
        if self.element.rotation != 0:
            self.setRotation(self.element.rotation)
            
        self._update_dimensions()
        self._update_label()
    
    def update_appearance(self):
        """Aktualisiert Farben und Stil"""
        color = PROFILE_COLORS.get(self.element.profile_type, Qt.GlobalColor.gray)
        
        # Hauptrahmen
        pen = QPen(color, 3)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.setPen(pen)
        
        # Füllung (leicht transparent)
        fill_color = QColor(color)
        fill_color.setAlpha(30)
        self.setBrush(QBrush(fill_color))
        
        # Selektion
        if self.element.is_selected:
            self._add_selection_overlay()
    
    def _add_selection_overlay(self):
        """Fügt Selektions-Highlighting hinzu"""
        pen = self.pen()
        pen.setColor(SELECTION_COLOR)
        pen.setWidth(5)
        pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)
    
    def _update_dimensions(self):
        """Aktualisiert Bemaßungstexte"""
        # Alte Texte entfernen
        for text in self._dimension_texts:
            if text.scene():
                text.scene().removeItem(text)
        self._dimension_texts.clear()
        
        if not self._show_dimensions:
            return
            
        # Breite oben
        width_text = QGraphicsTextItem(f"{self.element.width:.0f}")
        width_text.setParentItem(self)
        width_text.setPos(self.element.width/2 - 30, -30)
        self._dimension_texts.append(width_text)
        
        # Höhe rechts
        height_text = QGraphicsTextItem(f"{self.element.height:.0f}")
        height_text.setParentItem(self)
        height_text.setPos(self.element.width + 10, self.element.height/2 - 10)
        self._dimension_texts.append(height_text)
    
    def _update_label(self):
        """Aktualisiert Profiltyp-Label"""
        if self._profile_label:
            if self._profile_label.scene():
                self._profile_label.scene().removeItem(self._profile_label)
                
        if not self._show_labels:
            return
            
        label = f"{self.element.profile_type.value}\n{self.element.comment}"
        self._profile_label = QGraphicsTextItem(label)
        self._profile_label.setParentItem(self)
        
        # Zentriert im Element
        font = QFont("Arial", 10)
        self._profile_label.setFont(font)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(self.element.profile_type.value)
        self._profile_label.setPos(
            (self.element.width - text_width) / 2,
            self.element.height / 2 - 20
        )
    
    def set_selected(self, selected: bool):
        """Setzt den Selektionsstatus"""
        self.element.is_selected = selected
        self.setSelected(selected)
        self.update_appearance()
    
    def itemChange(self, change, value):
        """Behandelt Änderungen am Item"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Position im Datenmodell aktualisieren
            pos = value.toPointF() if hasattr(value, 'toPointF') else value
            self.element.x = pos.x()
            self.element.y = pos.y()
            
        return super().itemChange(change, value)
    
    def paint(self, painter: QPainter, option, widget=None):
        """Erweiterte Zeichenfunktion"""
        super().paint(painter, option, widget)
        
        # Zusätzliche Details zeichnen (z.B. Profilquerschnitt)
        if self.element.is_selected:
            self._draw_profile_details(painter)
    
    def _draw_profile_details(self, painter: QPainter):
        """Zeichnet Profildetails bei Selektion"""
        # Vereinfachte Profildarstellung an den Ecken
        pen = QPen(Qt.GlobalColor.darkGray, 1)
        painter.setPen(pen)
        
        # Eckdetails (vereinfacht)
        corner_size = 20
        corners = [
            (0, 0),  # Oben links
            (self.element.width - corner_size, 0),  # Oben rechts
            (0, self.element.height - corner_size),  # Unten links
            (self.element.width - corner_size, self.element.height - corner_size)  # Unten rechts
        ]
        
        for x, y in corners:
            painter.drawRect(x, y, corner_size, corner_size)

# === views/graphics_view.py ===
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QWheelEvent, QMouseEvent
from utils.colors import GRID_COLOR, SNAP_POINT_COLOR

class GraphicsView(QGraphicsView):
    """Erweiterte QGraphicsView mit Zoom, Pan und Grid"""
    
    # Signals
    mouse_position_changed = pyqtSignal(QPointF)
    zoom_changed = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        
        # Einstellungen
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Grid-Einstellungen
        self.grid_size = 50
        self.grid_visible = True
        self.snap_to_grid = True
        
        # Zoom-Einstellungen
        self.zoom_factor = 1.15
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.current_zoom = 1.0
        
        # Scene erstellen
        scene = QGraphicsScene()
        scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.setScene(scene)
        
        # Hintergrund
        self.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
    
    def drawBackground(self, painter: QPainter, rect: QRectF):
        """Zeichnet Grid im Hintergrund"""
        super().drawBackground(painter, rect)
        
        if not self.grid_visible:
            return
            
        # Grid zeichnen
        pen = QPen(GRID_COLOR, 0.5)
        painter.setPen(pen)
        
        # Sichtbaren Bereich bestimmen
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        
        # Vertikale Linien
        x = left
        while x <= rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += self.grid_size
            
        # Horizontale Linien
        y = top
        while y <= rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += self.grid_size
            
        # Ursprung markieren
        origin_pen = QPen(Qt.GlobalColor.red, 2)
        painter.setPen(origin_pen)
        painter.drawLine(-20, 0, 20, 0)
        painter.drawLine(0, -20, 0, 20)
    
    def wheelEvent(self, event: QWheelEvent):
        """Zoom mit Mausrad"""
        # Zoom-Richtung
        if event.angleDelta().y() > 0:
            zoom_in = True
        else:
            zoom_in = False
            
        # Zoom-Faktor berechnen
        if zoom_in:
            factor = self.zoom_factor
        else:
            factor = 1.0 / self.zoom_factor
            
        # Neue Zoom-Stufe prüfen
        new_zoom = self.current_zoom * factor
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
            
        # Zoom anwenden
        self.scale(factor, factor)
        self.current_zoom = new_zoom
        self.zoom_changed.emit(self.current_zoom)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Mausposition tracking"""
        super().mouseMoveEvent(event)
        
        # Szenen-Koordinaten
        scene_pos = self.mapToScene(event.pos())
        
        # Snap to Grid
        if self.snap_to_grid:
            scene_pos = self.snap_point(scene_pos)
            
        self.mouse_position_changed.emit(scene_pos)
    
    def snap_point(self, point: QPointF) -> QPointF:
        """Rastet Punkt am Grid ein"""
        x = round(point.x() / self.grid_size) * self.grid_size
        y = round(point.y() / self.grid_size) * self.grid_size
        return QPointF(x, y)
    
    def fit_in_view_with_margin(self, rect: QRectF, margin: int = 50):
        """Passt Ansicht mit Rand an"""
        adjusted_rect = rect.adjusted(-margin, -margin, margin, margin)
        self.fitInView(adjusted_rect, Qt.AspectRatioMode.KeepAspectRatio)
        
        # Zoom-Level aktualisieren
        transform = self.transform()
        self.current_zoom = transform.m11()  # Horizontaler Skalierungsfaktor
        self.zoom_changed.emit(self.current_zoom)

# === controllers/view_controller.py ===
from PyQt6.QtCore import QObject, QPointF
from PyQt6.QtWidgets import QGraphicsScene
from typing import List, Optional
from models.window_element import WindowElement
from views.window_item import WindowItem
from views.graphics_view import GraphicsView

class ViewController(QObject):
    """Controller für View-Interaktionen"""
    
    def __init__(self, view: GraphicsView):
        super().__init__()
        self.view = view
        self.scene = view.scene()
        self.window_items: List[WindowItem] = []
        self.selected_items: List[WindowItem] = []
        
        # Verbindungen
        self.scene.selectionChanged.connect(self._on_selection_changed)
    
    def add_window(self, element: WindowElement) -> WindowItem:
        """Fügt neues Fenster hinzu"""
        item = WindowItem(element)
        self.scene.addItem(item)
        self.window_items.append(item)
        return item
    
    def remove_window(self, item: WindowItem):
        """Entfernt Fenster"""
        if item in self.window_items:
            self.window_items.remove(item)
            self.scene.removeItem(item)
            
    def clear_all(self):
        """Entfernt alle Fenster"""
        for item in self.window_items:
            self.scene.removeItem(item)
        self.window_items.clear()
        self.selected_items.clear()
    
    def _on_selection_changed(self):
        """Behandelt Selektionsänderungen"""
        self.selected_items.clear()
        
        for item in self.scene.selectedItems():
            if isinstance(item, WindowItem):
                item.set_selected(True)
                self.selected_items.append(item)
                
        # Nicht-selektierte Items
        for item in self.window_items:
            if item not in self.selected_items:
                item.set_selected(False)
    
    def zoom_to_fit(self):
        """Zoomt auf alle Elemente"""
        if not self.window_items:
            return
            
        # Bounding Box aller Items
        min_x = min(item.element.x for item in self.window_items)
        min_y = min(item.element.y for item in self.window_items)
        max_x = max(item.element.x + item.element.width for item in self.window_items)
        max_y = max(item.element.y + item.element.height for item in self.window_items)
        
        rect = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
        self.view.fit_in_view_with_margin(rect)
    
    def align_selected_horizontal(self):
        """Richtet selektierte Elemente horizontal aus"""
        if len(self.selected_items) < 2:
            return
            
        # Referenz-Y (erstes Element)
        ref_y = self.selected_items[0].element.y
        
        for item in self.selected_items[1:]:
            item.element.y = ref_y
            item.update_geometry()
    
    def distribute_selected_horizontal(self):
        """Verteilt selektierte Elemente gleichmäßig horizontal"""
        if len(self.selected_items) < 3:
            return
            
        # Sortieren nach X
        sorted_items = sorted(self.selected_items, key=lambda i: i.element.x)
        
        # Abstände berechnen
        first = sorted_items[0]
        last = sorted_items[-1]
        total_width = sum(item.element.width for item in sorted_items[1:-1])
        available_space = (last.element.x - first.element.x - first.element.width) - total_width
        gap = available_space / (len(sorted_items) - 1)
        
        # Neu positionieren
        current_x = first.element.x + first.element.width + gap
        for item in sorted_items[1:-1]:
            item.element.x = current_x
            item.update_geometry()
            current_x += item.element.width + gap

# === viewmodels/window_viewmodel.py ===
from PyQt6.QtCore import QObject, pyqtSignal
from typing import List, Optional
import csv
import json
from models.window_element import WindowElement, ProfileType

class WindowViewModel(QObject):
    """ViewModel für Fensterverwaltung"""
    
    # Signals
    elements_changed = pyqtSignal()
    element_added = pyqtSignal(WindowElement)
    element_removed = pyqtSignal(str)  # ID
    element_updated = pyqtSignal(WindowElement)
    
    def __init__(self):
        super().__init__()
        self.elements: List[WindowElement] = []
    
    def add_element(self, element: WindowElement):
        """Fügt neues Element hinzu"""
        self.elements.append(element)
        self.element_added.emit(element)
        self.elements_changed.emit()
    
    def remove_element(self, element_id: str):
        """Entfernt Element"""
        element = self.get_element_by_id(element_id)
        if element:
            self.elements.remove(element)
            self.element_removed.emit(element_id)
            self.elements_changed.emit()
    
    def get_element_by_id(self, element_id: str) -> Optional[WindowElement]:
        """Findet Element nach ID"""
        for element in self.elements:
            if element.id == element_id:
                return element
        return None
    
    def update_element(self, element: WindowElement):
        """Aktualisiert Element"""
        self.element_updated.emit(element)
        self.elements_changed.emit()
    
    def load_from_csv(self, filename: str):
        """Lädt Elemente aus CSV"""
        self.elements.clear()
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Window Type aus CSV lesen, Fallback auf FT_DK
                window_type_code = row.get('Fenstertyp', 'FT_DK')
                window_type = WindowType.FT_DK  # Default
                for wt in WindowType:
                    if wt.code == window_type_code:
                        window_type = wt
                        break
                        
                element = WindowElement(
                    id=row.get('ID', ''),
                    x=float(row.get('X', 0)),
                    y=float(row.get('Y', 0)),
                    width=float(row.get('Breite', 1000)),
                    height=float(row.get('Höhe', 1200)),
                    profile_type=ProfileType(row.get('Profil', '070')),
                    window_type=window_type,
                    comment=row.get('Kommentar', '')
                )
                self.add_element(element)
    
    def save_to_csv(self, filename: str):
        """Speichert Elemente in CSV"""
        with open(filename, 'w', encoding='utf-8', newline='') as file:
            fieldnames = ['ID', 'X', 'Y', 'Breite', 'Höhe', 'Profil', 'Fenstertyp', 'Kommentar']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for element in self.elements:
                writer.writerow({
                    'ID': element.id,
                    'X': element.x,
                    'Y': element.y,
                    'Breite': element.width,
                    'Höhe': element.height,
                    'Profil': element.profile_type.value,
                    'Fenstertyp': element.window_type.code,
                    'Kommentar': element.comment
                })
    
    def export_to_json(self, filename: str):
        """Exportiert als JSON mit allen Details"""
        data = []
        for element in self.elements:
            data.append({
                'id': element.id,
                'geometry': {
                    'x': element.x,
                    'y': element.y,
                    'width': element.width,
                    'height': element.height,
                    'rotation': element.rotation
                },
                'profile': {
                    'type': element.profile_type.value,
                    'dimensions': {
                        'A': element.profile_width_a,
                        'B': element.profile_width_b,
                        'C': element.profile_width_c,
                        'D': element.profile_width_d
                    }
                },
                'window_type': {
                    'code': element.window_type.code,
                    'name': element.window_type.name,
                    'description': element.window_type.description
                },
                'metadata': element.metadata,
                'comment': element.comment
            })
            
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

# === views/main_window.py ===
from PyQt6.QtWidgets import (QMainWindow, QToolBar, QStatusBar, QDockWidget,
                            QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                            QSpinBox, QComboBox, QTableWidget, QTableWidgetItem,
                            QWidget, QFileDialog, QMessageBox, QGridLayout,
                            QScrollArea, QFrame, QTextEdit, QSplitter)
import json
import os
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QAction, QIcon
from views.graphics_view import GraphicsView
from controllers.view_controller import ViewController
from viewmodels.window_viewmodel import WindowViewModel
from models.window_element import WindowElement, ProfileType

class ElementDesignerWidget(QWidget):
    """ElementDesigner Widget nach Spezifikation V1 VariantA"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.glossary_data = {}
        self.schnitt_mapping = {}
        self._load_data_files()
        self._setup_ui()
        
    def _load_data_files(self):
        """Lädt Glossar und Schnitt-Mapping"""
        try:
            # Glossar laden
            glossar_path = os.path.join(os.path.dirname(__file__), 'assets', 'glossar.json')
            if os.path.exists(glossar_path):
                with open(glossar_path, 'r', encoding='utf-8') as f:
                    self.glossary_data = json.load(f)
                    
            # Schnitt-Mapping laden
            mapping_path = os.path.join(os.path.dirname(__file__), 'config', 'schnitt_map.json')
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
        layout.addWidget(title)
        
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
        
    def _create_window_type_panel(self):
        """Erstellt das Fenstertyp-Auswahl Panel"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Titel
        layout.addWidget(QLabel("<b>Fenstertypen (14 Stk.)</b>"))
        
        # Scroll-Bereich für Icon-Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(400)
        
        # Grid für Icons
        grid_widget = QWidget()
        grid_layout = QGridLayout()
        grid_widget.setLayout(grid_layout)
        
        # Window Type Buttons erstellen
        row, col = 0, 0
        for window_type in WindowType:
            btn = QPushButton()
            btn.setText(f"{window_type.code}\n{window_type.name}")
            btn.setMinimumSize(120, 80)
            btn.setMaximumSize(120, 80)
            btn.setStyleSheet("""
                QPushButton {
                    border: 2px solid #ccc;
                    border-radius: 8px;
                    background-color: #f9f9f9;
                    font-size: 9px;
                }
                QPushButton:hover {
                    background-color: #e9e9e9;
                    border-color: #999;
                }
                QPushButton:pressed {
                    background-color: #d9d9d9;
                }
            """)
            
            # Tooltip mit Beschreibung
            if hasattr(self.glossary_data, 'fenstertypen') and window_type.code in self.glossary_data.get('fenstertypen', {}):
                tooltip_data = self.glossary_data['fenstertypen'][window_type.code]
                tooltip = f"<b>{tooltip_data['name']}</b><br>{tooltip_data['beschreibung']}<br><i>{tooltip_data['anwendung']}</i>"
                btn.setToolTip(tooltip)
            else:
                btn.setToolTip(f"{window_type.name}\n{window_type.description}")
                
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
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Schnitt-Vorschau Bereich
        layout.addWidget(QLabel("<b>Schnitt-Vorschau</b>"))
        
        self.preview_area = QLabel()
        self.preview_area.setMinimumHeight(200)
        self.preview_area.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                background-color: white;
                margin: 5px;
            }
        """)
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_area.setText("Fenstertyp auswählen für Vorschau")
        layout.addWidget(self.preview_area)
        
        # Glossar-Bereich
        layout.addWidget(QLabel("<b>Glossar</b>"))
        
        self.glossar_text = QTextEdit()
        self.glossar_text.setMaximumHeight(150)
        self.glossar_text.setReadOnly(True)
        self._update_glossar_display()
        layout.addWidget(self.glossar_text)
        
        return widget
        
    def _update_glossar_display(self):
        """Aktualisiert die Glossar-Anzeige"""
        if 'begriffe' in self.glossary_data:
            glossar_html = "<h4>Begriffe:</h4><ul>"
            for begriff, definition in self.glossary_data['begriffe'].items():
                glossar_html += f"<li><b>{begriff}:</b> {definition}</li>"
            glossar_html += "</ul>"
            self.glossar_text.setHtml(glossar_html)
        else:
            self.glossar_text.setText("Glossar-Daten nicht verfügbar")
            
    def _on_window_type_selected(self, window_type: WindowType):
        """Behandelt Fenstertyp-Auswahl"""
        # Schnitt-Templates für diesen Typ finden
        templates = []
        for template_id, template_data in self.schnitt_mapping.get('schnitt_templates', {}).items():
            if window_type.code in template_data.get('window_types', []):
                templates.append(f"• {template_data['description']} ({template_data['file']})")
                
        # Preview aktualisieren
        if templates:
            preview_text = f"<b>{window_type.name}</b><br><br>"
            preview_text += f"<i>{window_type.description}</i><br><br>"
            preview_text += "<b>Verfügbare Schnitt-Templates:</b><br>"
            preview_text += "<br>".join(templates)
        else:
            preview_text = f"<b>{window_type.name}</b><br><br>"
            preview_text += f"<i>{window_type.description}</i><br><br>"
            preview_text += "Keine Schnitt-Templates gefunden"
            
        self.preview_area.setText(preview_text)
        self.preview_area.setWordWrap(True)

class MainWindow(QMainWindow):
    """Hauptfenster der Anwendung"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VEKA Bauelement-Visualisierer")
        self.setGeometry(100, 100, 1400, 900)
        
        # ViewModels und Controller
        self.view_model = WindowViewModel()
        self.graphics_view = GraphicsView()
        self.view_controller = ViewController(self.graphics_view)
        
        self._setup_ui()
        self._setup_connections()
        self._load_sample_data()
    
    def _setup_ui(self):
        """Erstellt UI-Komponenten"""
        # Zentrale View
        self.setCentralWidget(self.graphics_view)
        
        # Toolbar
        self._create_toolbar()
        
        # Statusbar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.mouse_pos_label = QLabel("X: 0, Y: 0")
        self.zoom_label = QLabel("Zoom: 100%")
        self.status_bar.addPermanentWidget(self.mouse_pos_label)
        self.status_bar.addPermanentWidget(self.zoom_label)
        
        # Eigenschaften-Dock
        self._create_properties_dock()
        
        # Element-Liste Dock
        self._create_element_list_dock()
        
        # ElementDesigner Dock
        self._create_element_designer_dock()
    
    def _create_toolbar(self):
        """Erstellt Haupttoolbar"""
        toolbar = QToolBar("Hauptwerkzeuge")
        self.addToolBar(toolbar)
        
        # Datei-Aktionen
        new_action = QAction("Neu", self)
        new_action.triggered.connect(self._on_new_element)
        toolbar.addAction(new_action)
        
        open_action = QAction("Öffnen", self)
        open_action.triggered.connect(self._on_open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("Speichern", self)
        save_action.triggered.connect(self._on_save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # View-Aktionen
        zoom_fit_action = QAction("Alles anzeigen", self)
        zoom_fit_action.triggered.connect(self.view_controller.zoom_to_fit)
        toolbar.addAction(zoom_fit_action)
        
        grid_action = QAction("Raster", self)
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.toggled.connect(self._toggle_grid)
        toolbar.addAction(grid_action)
        
        snap_action = QAction("Einrasten", self)
        snap_action.setCheckable(True)
        snap_action.setChecked(True)
        snap_action.toggled.connect(self._toggle_snap)
        toolbar.addAction(snap_action)
        
        toolbar.addSeparator()
        
        # Ausrichtung
        align_h_action = QAction("Horizontal ausrichten", self)
        align_h_action.triggered.connect(self.view_controller.align_selected_horizontal)
        toolbar.addAction(align_h_action)
        
        distribute_h_action = QAction("Horizontal verteilen", self)
        distribute_h_action.triggered.connect(self.view_controller.distribute_selected_horizontal)
        toolbar.addAction(distribute_h_action)
    
    def _create_properties_dock(self):
        """Erstellt Eigenschaften-Panel"""
        dock = QDockWidget("Eigenschaften", self)
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Neue Element-Eingaben
        layout.addWidget(QLabel("<b>Neues Element:</b>"))
        
        # Position
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X:"))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(-9999, 9999)
        self.x_spin.setValue(100)
        pos_layout.addWidget(self.x_spin)
        
        pos_layout.addWidget(QLabel("Y:"))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(-9999, 9999)
        self.y_spin.setValue(100)
        pos_layout.addWidget(self.y_spin)
        layout.addLayout(pos_layout)
        
        # Größe
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Breite:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 5000)
        self.width_spin.setValue(1000)
        self.width_spin.setSingleStep(50)
        size_layout.addWidget(self.width_spin)
        
        size_layout.addWidget(QLabel("Höhe:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 5000)
        self.height_spin.setValue(1200)
        self.height_spin.setSingleStep(50)
        size_layout.addWidget(self.height_spin)
        layout.addLayout(size_layout)
        
        # Profil
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Profil:"))
        self.profile_combo = QComboBox()
        for profile in ProfileType:
            self.profile_combo.addItem(profile.value, profile)
        profile_layout.addWidget(self.profile_combo)
        layout.addLayout(profile_layout)
        
        # Fenstertyp
        window_type_layout = QHBoxLayout()
        window_type_layout.addWidget(QLabel("Fenstertyp:"))
        self.window_type_combo = QComboBox()
        for window_type in WindowType:
            self.window_type_combo.addItem(f"{window_type.code} - {window_type.name}", window_type)
        window_type_layout.addWidget(self.window_type_combo)
        layout.addLayout(window_type_layout)
        
        # Hinzufügen-Button
        add_button = QPushButton("Element hinzufügen")
        add_button.clicked.connect(self._on_new_element)
        layout.addWidget(add_button)
        
        layout.addStretch()
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    
    def _create_element_list_dock(self):
        """Erstellt Element-Listen Panel"""
        dock = QDockWidget("Elemente", self)
        
        self.element_table = QTableWidget()
        self.element_table.setColumnCount(8)
        self.element_table.setHorizontalHeaderLabels(
            ["ID", "X", "Y", "Breite", "Höhe", "Profil", "Fenstertyp", "Kommentar"]
        )
        
        dock.setWidget(self.element_table)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        
    def _create_element_designer_dock(self):
        """Erstellt ElementDesigner Dock-Widget"""
        dock = QDockWidget("ElementDesigner", self)
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                         QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        
        # ElementDesigner Widget erstellen
        self.element_designer = ElementDesignerWidget()
        dock.setWidget(self.element_designer)
        
        # Als floating window starten (wie in Spezifikation gewünscht)
        dock.setFloating(True)
        dock.resize(800, 600)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    
    def _setup_connections(self):
        """Verbindet Signals und Slots"""
        # View Model
        self.view_model.element_added.connect(self._on_element_added)
        self.view_model.element_removed.connect(self._on_element_removed)
        self.view_model.elements_changed.connect(self._update_element_table)
        
        # Graphics View
        self.graphics_view.mouse_position_changed.connect(self._update_mouse_position)
        self.graphics_view.zoom_changed.connect(self._update_zoom_level)
    
    def _on_new_element(self):
        """Erstellt neues Element"""
        element = WindowElement(
            x=self.x_spin.value(),
            y=self.y_spin.value(),
            width=self.width_spin.value(),
            height=self.height_spin.value(),
            profile_type=self.profile_combo.currentData(),
            window_type=self.window_type_combo.currentData()
        )
        self.view_model.add_element(element)
    
    def _on_element_added(self, element: WindowElement):
        """Behandelt neues Element"""
        self.view_controller.add_window(element)
        self._update_element_table()
    
    def _on_element_removed(self, element_id: str):
        """Behandelt entferntes Element"""
        # Item in View finden und entfernen
        for item in self.view_controller.window_items:
            if item.element.id == element_id:
                self.view_controller.remove_window(item)
                break
    
    def _update_element_table(self):
        """Aktualisiert Element-Tabelle"""
        self.element_table.setRowCount(len(self.view_model.elements))
        
        for row, element in enumerate(self.view_model.elements):
            self.element_table.setItem(row, 0, QTableWidgetItem(element.id[:8]))
            self.element_table.setItem(row, 1, QTableWidgetItem(f"{element.x:.0f}"))
            self.element_table.setItem(row, 2, QTableWidgetItem(f"{element.y:.0f}"))
            self.element_table.setItem(row, 3, QTableWidgetItem(f"{element.width:.0f}"))
            self.element_table.setItem(row, 4, QTableWidgetItem(f"{element.height:.0f}"))
            self.element_table.setItem(row, 5, QTableWidgetItem(element.profile_type.value))
            self.element_table.setItem(row, 6, QTableWidgetItem(f"{element.window_type.code}"))
            self.element_table.setItem(row, 7, QTableWidgetItem(element.comment))
    
    def _update_mouse_position(self, pos: QPointF):
        """Aktualisiert Mausposition in Statusbar"""
        self.mouse_pos_label.setText(f"X: {pos.x():.0f}, Y: {pos.y():.0f}")
    
    def _update_zoom_level(self, zoom: float):
        """Aktualisiert Zoom-Level in Statusbar"""
        self.zoom_label.setText(f"Zoom: {zoom*100:.0f}%")
    
    def _toggle_grid(self, checked: bool):
        """Schaltet Raster ein/aus"""
        self.graphics_view.grid_visible = checked
        self.graphics_view.viewport().update()
    
    def _toggle_snap(self, checked: bool):
        """Schaltet Einrasten ein/aus"""
        self.graphics_view.snap_to_grid = checked
    
    def _on_open_file(self):
        """Öffnet CSV-Datei"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Datei öffnen", "", "CSV-Dateien (*.csv)"
        )
        if filename:
            try:
                self.view_controller.clear_all()
                self.view_model.load_from_csv(filename)
                self.view_controller.zoom_to_fit()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Laden: {str(e)}")
    
    def _on_save_file(self):
        """Speichert in CSV-Datei"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Datei speichern", "", "CSV-Dateien (*.csv)"
        )
        if filename:
            try:
                self.view_model.save_to_csv(filename)
                self.status_bar.showMessage("Datei gespeichert", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def _load_sample_data(self):
        """Lädt Beispieldaten"""
        sample_data = [
            {"x": 120, "y": 50, "width": 1000, "height": 1200, 
             "profile": ProfileType.BLEND_070, "window_type": WindowType.FT_DK, "comment": "Erdgeschoss West"},
            {"x": 1250, "y": 50, "width": 900, "height": 1200, 
             "profile": ProfileType.BLEND_076_MD, "window_type": WindowType.FT_DKD, "comment": "Erdgeschoss Ost"},
            {"x": 2280, "y": 50, "width": 800, "height": 1200, 
             "profile": ProfileType.BLEND_082_MD, "window_type": WindowType.FT_K, "comment": "Obergeschoss"},
            {"x": 120, "y": 1350, "width": 1200, "height": 800, 
             "profile": ProfileType.BLEND_070, "window_type": WindowType.FT_F, "comment": "Festfeld"},
            {"x": 1450, "y": 1350, "width": 600, "height": 800, 
             "profile": ProfileType.BLEND_076_MD, "window_type": WindowType.FT_HS, "comment": "WC-Fenster"},
        ]
        
        for data in sample_data:
            element = WindowElement(
                x=data["x"],
                y=data["y"],
                width=data["width"],
                height=data["height"],
                profile_type=data["profile"],
                window_type=data["window_type"],
                comment=data["comment"]
            )
            self.view_model.add_element(element)
        
        # Ansicht anpassen
        self.view_controller.zoom_to_fit()

# === main.py ===
import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VEKA Bauelement-Visualisierer")
    app.setOrganizationName("YourCompany")
    
    # Stil anpassen
    app.setStyle("Fusion")
    
    # Hauptfenster
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# === Performance-Optimierungen ===
"""
1. Level-of-Detail (LOD):
   - Vereinfachte Darstellung bei kleinem Zoom
   - Details nur bei Selektion/großem Zoom
   
2. Culling:
   - Nur sichtbare Elemente zeichnen
   - QGraphicsScene macht das automatisch
   
3. Batch-Updates:
   - Mehrere Änderungen sammeln
   - Einmal update() aufrufen
   
4. Caching:
   - Vorberechnete Profilgeometrien
   - QPainterPath für komplexe Formen

5. Threading:
   - Laden/Speichern in separatem Thread
   - QThread für lange Operationen
"""

# === 3D-Erweiterung (Ausblick) ===
"""
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import numpy as np

class Window3DView(QOpenGLWidget):
    '''3D-Ansicht mit PyOpenGL'''
    
    def initializeGL(self):
        glClearColor(0.9, 0.9, 0.9, 1.0)
        glEnable(GL_DEPTH_TEST)
        
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # 3D-Rendering hier
        
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        # Projektionsmatrix anpassen
"""

# === Tests (pytest) ===
"""
def test_window_element_creation():
    element = WindowElement(x=100, y=200, width=1000, height=1200)
    assert element.x == 100
    assert element.center_x == 600
    
def test_profile_colors():
    assert ProfileType.BLEND_070 in PROFILE_COLORS
    color = PROFILE_COLORS[ProfileType.BLEND_070]
    assert color.isValid()
"""